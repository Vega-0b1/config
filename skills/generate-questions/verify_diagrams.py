#!/usr/bin/env python3
"""Check optional diagram attachments without changing text-only quote verification.

Usage: verify_diagrams.py <questions-file>

Paths in question fields and figure registries are relative to the class root.
Mechanical checks cover assets, provenance, stage separation, and quoted visual
descriptions. Status: verified records a prior human/agent visual inspection;
this script cannot establish that an image was transcribed correctly.
"""

from collections.abc import Mapping
import hashlib
from pathlib import Path
import re
import sys
import zipfile

from verify_quotes import normalize, parse_entries

FIELD = re.compile(r'^([A-Z][A-Za-z0-9_ ]*):[ \t]*(.*)$')
IMAGE = re.compile(r'!\[[^\]\n]*\]\(([^()\n]+)\)')
DIAGRAM_FIELDS = ('Diagram', 'Answer diagram', 'Figure source', 'Figure quote')


def fields(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    current: str | None = None
    for line in text.splitlines():
        match = FIELD.fullmatch(line)
        if match is not None:
            current = match.group(1)
            if current in result:
                raise ValueError(f'duplicate field: {current}')
            result[current] = match.group(2)
        elif current is not None and (line.startswith('  ') or not line.strip()):
            result[current] += '\n' + (line[2:] if line.startswith('  ') else '')
        else:
            current = None
    return {key: value.strip() for key, value in result.items()}


def required(values: Mapping[str, str], key: str) -> str:
    value = values.get(key, '')
    if not value:
        raise ValueError(f'missing or empty {key}')
    return value


def class_root(path: Path) -> Path:
    for parent in path.resolve().parents:
        if (parent / 'extracted').is_dir():
            return parent
    raise ValueError(f'no class root with extracted/ found above {path}')


def local_file(root: Path, name: str) -> Path:
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts or '://' in name:
        raise ValueError(f'expected a class-root-relative path: {name}')
    result = (root / relative).resolve()
    if not result.is_relative_to(root.resolve()) or not result.is_file():
        raise ValueError(f'missing or outside-class file: {name}')
    return result


def figure_record(root: Path, reference: str) -> dict[str, str]:
    name, separator, identifier = reference.rpartition('#')
    if not separator or re.fullmatch(r'[a-z0-9_]+', identifier) is None:
        raise ValueError('Figure source must be <registry-path>#<figure-id>')
    registry = local_file(root, name)
    text = registry.read_text(encoding='utf-8')
    pattern = rf'^#### {re.escape(identifier)}[ \t]*\n(.*?)(?=^#### |\Z)'
    records = re.findall(pattern, text, flags=re.M | re.S)
    if len(records) != 1:
        raise ValueError(f'expected one registry entry for {identifier}, found {len(records)}')
    record = fields(records[0])
    if required(record, 'Status') != 'verified':
        raise ValueError(f'figure {identifier} is not verified')
    source = local_file(root, required(record, 'Source'))
    if zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as archive:
            if archive.read('mimetype').strip() != b'application/epub+zip':
                raise ValueError('figure Source archive must be an EPUB')
            if required(record, 'Document') not in archive.namelist():
                raise ValueError('EPUB Document member is missing')
    elif source.suffix.lower() == '.pdf':
        for key in ('Page', 'DPI'):
            if re.fullmatch(r'[1-9][0-9]*', required(record, key)) is None:
                raise ValueError(f'{key} must be a positive integer')
    else:
        raise ValueError('figure Source must be a PDF or EPUB')
    required(record, 'Description')
    return record


def check_image(root: Path, value: str, record: Mapping[str, str], stage: str) -> None:
    match = IMAGE.fullmatch(value)
    if match is None:
        raise ValueError(f'{stage} diagram must contain exactly one Markdown image')
    path = local_file(root, match.group(1))
    expected_path = local_file(root, required(record, f'{stage} image'))
    if path != expected_path:
        raise ValueError(f'{stage} diagram does not match the registry {stage} image')
    raw = path.read_bytes()
    digest = required(record, f'{stage} SHA256')
    if re.fullmatch(r'[0-9a-f]{64}', digest) is None:
        raise ValueError(f'{stage} SHA256 must contain 64 lowercase hexadecimal characters')
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError(f'{stage} image changed since visual verification: {path}')
    source = local_file(root, required(record, 'Source'))
    if zipfile.is_zipfile(source):
        if not (raw.startswith(b'\x89PNG\r\n\x1a\n') or raw.startswith(b'\xff\xd8\xff')):
            raise ValueError(f'{stage} EPUB display image must be PNG or JPEG')
        with zipfile.ZipFile(source) as archive:
            original = archive.read(required(record, f'{stage} member'))
        representation = record.get(f'{stage} representation', 'native')
        if representation == 'native':
            if raw != original:
                raise ValueError(f'{stage} image differs from its original EPUB member')
        elif representation in ('redraw', 'clean'):
            original_path = local_file(root, required(record, f'{stage} original'))
            if original_path.read_bytes() != original:
                raise ValueError(f'{stage} preserved original differs from its EPUB member')
            if hashlib.sha256(original).hexdigest() != required(record, f'{stage} source SHA256'):
                raise ValueError(f'{stage} original EPUB image hash does not match')
        else:
            raise ValueError(f'unsupported {stage} representation: {representation}')
        return
    if not raw.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError(f'{stage} PDF image is not a PNG: {path}')
    crop = required(record, f'{stage} crop').split()
    if len(crop) != 4 or any(re.fullmatch(r'[0-9]+', item) is None for item in crop):
        raise ValueError(f'{stage} crop must be x y width height in nonnegative pixels')
    if int(crop[2]) == 0 or int(crop[3]) == 0:
        raise ValueError(f'{stage} crop width and height must be positive')
    width = int.from_bytes(raw[16:20], 'big')
    height = int.from_bytes(raw[20:24], 'big')
    if (width, height) != (int(crop[2]), int(crop[3])):
        raise ValueError(f'{stage} PNG dimensions disagree with its recorded crop')


def check_entry(root: Path, entry: Mapping[str, str]) -> tuple[int, int]:
    question = entry.get('Diagram')
    answer = entry.get('Answer diagram')
    if not question and not answer:
        raise ValueError('diagram provenance has no Diagram or Answer diagram attachment')
    record = figure_record(root, required(entry, 'Figure source'))
    quote = required(entry, 'Figure quote')
    fragments = [piece.strip() for piece in re.split(r'\n\s*\n|\[\.\.\.\]', quote)]
    if not any(normalize(fragment) for fragment in fragments):
        raise ValueError('Figure quote has no nonempty fragments')
    description = normalize(required(record, 'Description'))
    for fragment in fragments:
        if normalize(fragment) and normalize(fragment) not in description:
            raise ValueError(f'Figure quote not found in verified Description: {fragment}')
    if question:
        check_image(root, question, record, 'Question')
    if answer:
        check_image(root, answer, record, 'Answer')
    return (1 if question else 0, 1 if answer else 0)


def main() -> None:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    qpath = Path(sys.argv[1])
    try:
        text = qpath.read_text(encoding='utf-8')
        questions = 0
        answers = 0
        checked = 0
        root: Path | None = None
        problems: list[str] = []
        for unit, qid, body in parse_entries(text):
            if not any(re.search(rf'^{re.escape(key)}:', body, flags=re.M) for key in DIAGRAM_FIELDS):
                continue
            try:
                if root is None:
                    root = class_root(qpath)
                qcount, acount = check_entry(root, fields(body))
                questions += qcount
                answers += acount
                checked += 1
            except (ValueError, KeyError, zipfile.BadZipFile) as error:
                problems.append(f'[{unit}] {qid}: {error}')
        print(f'diagram entries : {checked}; question images: {questions}; answer images: {answers}')
        if problems:
            for problem in problems:
                print(problem, file=sys.stderr)
            sys.exit(1)
        print('Diagram checks passed.' if checked else 'Text-only file: no diagram fields to check.')
    except (OSError, UnicodeError, ValueError, KeyError, zipfile.BadZipFile) as error:
        print(f'error: {error}', file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
