"""Offline reference archives and installed Linux man-pages for scrapes.py."""

from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
import gzip
import hashlib
import os
import re
import subprocess
import tarfile
import time
import urllib.request


SEPARATOR = '=' * 60
Spec = Mapping[str, object]


def setting(spec: Spec, key: str, default: str = '') -> str:
    value = spec.get(key, default)
    if not isinstance(value, str):
        raise ValueError(f'{key} must be a string')
    return value


def strings(spec: Spec, key: str) -> list[str]:
    value = spec.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f'{key} must be a list of strings')
    return [str(item) for item in value]


class ReferenceHTML(HTMLParser):
    """Keep code whitespace and table cell boundaries; discard UI and scripts."""

    def __init__(self, content_id: str = '', content_tag: str = '') -> None:
        super().__init__(convert_charrefs=True)
        self.content_id = content_id
        self.content_tag = content_tag
        self.active = not (content_id or content_tag)
        self.found = self.active
        self.stack: list[tuple[str, bool, bool]] = []
        self.suppressed = False
        self.pre = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        previous = (tag, self.active, self.suppressed)
        if (self.content_id and attributes.get('id') == self.content_id) or (self.content_tag and tag == self.content_tag):
            self.active = True
            self.found = True
        self.suppressed = self.suppressed or tag in {'script', 'style', 'nav', 'footer', 'head'}
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append(previous)
        if not self.active or self.suppressed:
            return
        if tag == 'pre':
            self.pre += 1
            self.parts.append('\n```\n')
        elif tag in {'p', 'div', 'tr', 'li', 'dt', 'dd', 'br', 'section', 'table'}:
            self.parts.append('\n')
        elif tag in {'td', 'th'}:
            self.parts.append(' | ')
        elif tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            self.parts.append('\n\n### ')
        elif tag == 'img' and attributes.get('alt'):
            self.parts.append(attributes['alt'] or '')

    def handle_endtag(self, tag: str) -> None:
        if self.active and not self.suppressed:
            if tag == 'pre' and self.pre:
                self.pre -= 1
                self.parts.append('\n```\n')
            elif tag in {'p', 'div', 'tr', 'li', 'dt', 'dd', 'section', 'table', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
                self.parts.append('\n')
        for index in range(len(self.stack) - 1, -1, -1):
            opened, active, suppressed = self.stack[index]
            if opened == tag:
                self.active, self.suppressed = active, suppressed
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if self.active and not self.suppressed:
            data = data.replace('\u00a0', ' ')
            self.parts.append(data if self.pre else re.sub(r'\s+', ' ', data))

    def result(self) -> str:
        if not self.found:
            raise ValueError(f'HTML content root {self.content_id or self.content_tag!r} not found')
        return re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', ''.join(self.parts)).strip()


def archive_path(url: str) -> Path:
    cache = Path.home() / 'edu/zStore/scrapes/.cache/references'
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / (hashlib.sha256(url.encode()).hexdigest()[:16] + '-' + url.rsplit('/', 1)[-1])
    if not path.exists() or time.time() - path.stat().st_mtime > 86400:
        print(f'  downloading {url}', flush=True)
        request = urllib.request.Request(url, headers={'User-Agent': 'scrapes.py/1.0 (personal doc mirror)'})
        temporary = path.with_suffix(path.suffix + '.part')
        with urllib.request.urlopen(request, timeout=120) as response, temporary.open('wb') as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        with tarfile.open(temporary, 'r:*') as archive:
            if not archive.getmembers():
                raise ValueError('Empty documentation archive')
        temporary.replace(path)
    return path


def build_archive(name: str, spec: Spec) -> list[str]:
    lines = [setting(spec, 'title', name), SEPARATOR, '']
    prefixes = strings(spec, 'prefixes')
    excluded = strings(spec, 'exclude_prefixes')
    excluded_suffixes = strings(spec, 'exclude_suffixes')
    suffix = setting(spec, 'suffix', '.html')
    strip_root = setting(spec, 'strip_root')
    count = 0
    for url in strings(spec, 'urls'):
        with tarfile.open(archive_path(url), 'r:*') as archive:
            # Preserve archive order: sorting compressed tar members causes
            # repeated backward decompression and quadratic extraction time.
            members = (member for member in archive
                       if member.isfile() and member.name.endswith(suffix)
                       and any(member.name.startswith(prefix) for prefix in prefixes)
                       and not any(member.name.startswith(prefix) for prefix in excluded)
                       and not any(member.name.endswith(ending) for ending in excluded_suffixes))
            for member in members:
                source = archive.extractfile(member)
                if source is None:
                    raise ValueError(f'Missing archive member {member.name}')
                with source:
                    body = source.read().decode('utf-8')
                relative = member.name.removeprefix(strip_root)
                if suffix == '.html':
                    if spec.get('skip_redirects') is True and 'http-equiv="refresh"' in body.lower():
                        continue
                    parser = ReferenceHTML(setting(spec, 'content_id'), setting(spec, 'content_tag'))
                    parser.feed(body)
                    parser.close()
                    body = parser.result()
                if not body.strip():
                    raise ValueError(f'Empty page: {member.name}')
                title = relative.removesuffix(suffix)
                source_url = setting(spec, 'source_base') + relative.removesuffix(setting(spec, 'source_remove_suffix'))
                if suffix == '.txt':
                    source_url = source_url.removesuffix('.txt') + '.html'
                lines.extend([SEPARATOR, f'# {title}', SEPARATOR,
                              f'(source: {source_url})', f'(archive: {url})', '', *body.splitlines(), ''])
                count += 1
                if count % 1000 == 0:
                    print(f'  {count} pages extracted', flush=True)
    print(f'  {count} archive pages', flush=True)
    return lines


def render_man(path: str) -> tuple[str, str]:
    with gzip.open(path, 'rt', encoding='utf-8') as source:
        roff = source.read()
    # Alias pages refer to a real page already present in this dump.
    if re.fullmatch(r'\s*\.so\s+\S+\s*', roff):
        return path, ''
    environment = dict(os.environ, MANWIDTH='100', GROFF_NO_SGR='1', LC_ALL='C.UTF-8')
    environment.pop('MAN_KEEP_FORMATTING', None)
    result = subprocess.run(['man', '-P', 'cat', '-l', path], env=environment,
                            capture_output=True, text=True, check=True, timeout=30)
    text = re.sub(r'.\x08', '', result.stdout)
    text = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', text)
    # Join roff's wrapped words without joining paragraphs or code lines.
    text = text.replace('\u2010\n', '').replace('\u00ad\n', '')
    if not text.strip():
        raise ValueError(f'Empty rendered man page: {path}')
    return path, text


def build_local_man(name: str, spec: Spec) -> list[str]:
    result = subprocess.run(['dpkg-query', '-L', *strings(spec, 'packages')],
                            capture_output=True, text=True, check=True)
    sections = strings(spec, 'sections')
    paths = sorted({path for path in result.stdout.splitlines()
                    if path.endswith('.gz') and any(f'/man{section}/' in path for section in sections)})
    versions = subprocess.run(['dpkg-query', '-W', '-f=${binary:Package} ${Version}\n', *strings(spec, 'packages')],
                              capture_output=True, text=True, check=True).stdout.strip()
    lines = [setting(spec, 'title', name), SEPARATOR, '', versions, '']
    count = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        for path, body in executor.map(render_man, paths):
            if not body:
                continue
            title = Path(path).name.removesuffix('.gz')
            section = title.rsplit('.', 1)[-1][0]
            lines.extend([SEPARATOR, f'# {title}', SEPARATOR,
                          f'(source: https://man7.org/linux/man-pages/man{section}/{title}.html)',
                          f'(local: {path})', '', *body.splitlines(), ''])
            count += 1
            if count % 250 == 0:
                print(f'  {count} man pages rendered', flush=True)
    print(f'  {count} installed man pages', flush=True)
    return lines
