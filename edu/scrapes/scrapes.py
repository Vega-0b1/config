#!/usr/bin/env python3
"""
Produce and refresh the dumps in this directory from sources.toml.

    scrapes.py list                  manifest entries, scrape dates, ages
    scrapes.py scrape NAME...        fetch -> index -> audit -> promote on pass
    scrapes.py update [--stale 60]   re-scrape everything past the age threshold
    scrapes.py audit [NAME...]       run the gate against the live dumps

Promotion is atomic and gated. A candidate is written to <name>.txt.new, indexed,
and audited; it replaces the live dump only if the gate passes. A scrape takes
minutes, these files are not in git, and a truncated run must never be able to
destroy a good dump -- so a failing candidate is kept as .new for inspection and
the live file is left untouched. --force overrides, --dry-run never promotes.

Source kinds:

  nix-options  build a flake attr and render its options.json. No network; the
               output matches the version actually installed rather than a
               website's current state.
  markdown     fetch raw markdown URLs (GitHub, codeberg, gitlab -- the manifest
               carries full URLs because the plugin set spans all three), and
               optionally walk a repo tree via the GitHub API.
  mediawiki    absorbed from the old scrape_arch_wiki.py: enumerate a wiki's
               pages through the API, fetch wikitext, strip markup.
  texinfo      render a package's shipped .info manual, parsed directly.
  doxygen      extract @brief blocks and signatures from C sources.
  pdf          fetch (or read) a PDF and extract text with pdftotext -layout,
               one dump page per PDF page. The PDF itself is not kept.

No third-party deps required.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
import tomllib
import urllib.parse
import urllib.request

import index_dumps

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "sources.toml")
SEPARATOR = "=" * 60
RULE = "─" * 40
UA = "scrapes.py/1.0 (personal doc mirror)"


def load_manifest():
    with open(MANIFEST, "rb") as f:
        return tomllib.load(f)


def fetch_url(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_json(url, timeout=30):
    return json.loads(fetch_url(url, timeout))


def fetch_bytes(url, timeout=120):
    """Binary sibling of fetch_url. PDFs must not be decoded as text."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ----------------------------------------------------------------------- pdf ---

def pdf_to_pages(data, label):
    """PDF bytes -> [(page_number, text)] via pdftotext -layout.

    -layout preserves column alignment, which is the difference between a
    readable register table and a scrambled one. pdftotext emits form feeds at
    page boundaries, so PDF pages map one-to-one onto dump pages and a citation
    like "page 24 of the datasheet" stays meaningful.
    """
    if not data.startswith(b"%PDF"):
        # Vendors serve HTML error pages from .pdf URLs; without this check that
        # becomes a dump full of markup instead of an obvious failure.
        head = data[:80].decode("utf-8", errors="replace").replace("\n", " ")
        raise RuntimeError(f"{label}: not a PDF (starts with {head!r})")
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(data)
        path = tmp.name
    try:
        out = subprocess.run(["pdftotext", "-layout", path, "-"],
                             capture_output=True, text=True, timeout=600)
        if out.returncode != 0:
            raise RuntimeError(f"{label}: pdftotext failed: {out.stderr.strip()[:200]}")
        text = out.stdout
    finally:
        os.unlink(path)          # the PDF itself is not kept; the manifest has the URL
    pages = [p for p in text.split("\f")]
    return [(i, p) for i, p in enumerate(pages, 1) if p.strip()]


def build_pdf(name, spec):
    sources = [("url", u) for u in spec.get("urls", [])]
    sources += [("file", os.path.expanduser(f)) for f in spec.get("files", [])]
    if not sources:
        raise RuntimeError("manifest entry has neither 'urls' nor 'files'")
    title = spec.get("title", name.replace("_", " ").title())
    lines = [title, SEPARATOR, ""]
    total, thin = 0, 0
    for kind, src in sources:
        label = os.path.basename(src.rstrip("/"))
        print(f"  {kind}: {label}", flush=True)
        data = fetch_bytes(src) if kind == "url" else open(src, "rb").read()
        pages = pdf_to_pages(data, label)
        doc = spec.get("doc_title", label.rsplit(".", 1)[0])
        for n, text in pages:
            body = text.rstrip("\n").split("\n")
            # An image-only scan extracts to near-nothing. Counted so the caller
            # can surface it rather than promoting a dump of blank pages.
            if len(" ".join(body).split()) < 5:
                thin += 1
            lines += [SEPARATOR, f"# {doc} — page {n}", SEPARATOR, "",
                      f"(source: {src})", ""] + body + [""]
        total += len(pages)
        print(f"    {len(pages)} pages", flush=True)
    # An image-only scan yields ZERO extractable pages, not thin ones -- a purely
    # ratio-based check short-circuits on total==0 and lets it through to fail
    # later as a confusing min_pages violation. Name it here instead.
    if total == 0:
        raise RuntimeError(
            "no extractable text — the PDF has no text layer (image-only scan). "
            "pdftotext cannot read it; OCR would be required.")
    if thin / total > 0.5:
        raise RuntimeError(
            f"{thin}/{total} pages extracted almost no text — likely a partial "
            f"image-only scan; pdftotext cannot read it")
    print(f"  {total} pages total", flush=True)
    return lines


# --------------------------------------------------------------- nix-options ---

def render_options(data):
    """options.json -> the 7-space-indented layout audit_dumps.OPTION parses."""
    out = []
    for name in sorted(data):
        o = data[name]
        out.append(f"       {name}")
        desc = (o.get("description") or "").strip()
        for line in desc.split("\n"):
            line = line.strip()
            if line:
                out.append(f"           {line}")
        out.append("")
        t = o.get("type")
        if t:
            out.append(f"           Type: {t}")
            out.append("")
        if "default" in o:
            d = o["default"]
            d = d.get("text", d) if isinstance(d, dict) else d
            out.append(f"           Default: {json.dumps(d) if not isinstance(d, str) else d}"[:400])
            out.append("")
        decl = o.get("declarations") or []
        if decl:
            d0 = decl[0]
            d0 = d0.get("url", d0.get("name", "")) if isinstance(d0, dict) else d0
            out.append(f"           Declared by: {d0}")
            out.append("")
    return out


def build_nix_options(name, spec):
    """Build an options.json and render it.

    Prefer `expr` over `attr`: a bare flake ref like
    'github:nix-community/home-manager/release-26.05' resolves to that branch's
    HEAD, not to the rev in /etc/nixos/flake.lock, so it would silently document
    a version this system does not have. Going through builtins.getFlake uses the
    lock, which is the whole reason these are generated rather than scraped.
    """
    jpath = spec["json_path"]
    if "expr" in spec:
        source = "flake.lock (" + spec["expr"].split("inputs.")[-1].split(".")[0] + ")"
        cmd = ["nix", "build", "--no-link", "--print-out-paths",
               "--impure", "--expr", spec["expr"]]
    else:
        source = spec["attr"]
        cmd = ["nix", "build", "--no-link", "--print-out-paths", source]
    print(f"  building {source}", flush=True)
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if out.returncode != 0:
        raise RuntimeError(f"nix build failed: {out.stderr.strip().splitlines()[-1:]}")
    store = out.stdout.strip().splitlines()[-1]
    with open(os.path.join(store, jpath)) as f:
        data = json.load(f)
    print(f"  {len(data)} options", flush=True)
    title = ("NixOS Options Reference" if "nixos" in name
             else "Home Manager Options Reference")
    lines = [title, SEPARATOR, "", SEPARATOR, f"# {title}", SEPARATOR, "",
             f"Generated from {source}", f"{len(data)} options.", ""]
    return lines + render_options(data)


# ------------------------------------------------------------------ markdown ---

def github_tree(repo, branch, prefix, ext):
    """List files under a prefix via the GitHub trees API."""
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    tree = fetch_json(url).get("tree", [])
    paths = [t["path"] for t in tree
             if t["type"] == "blob" and t["path"].startswith(prefix)
             and t["path"].endswith(ext)]
    return [f"https://raw.githubusercontent.com/{repo}/{branch}/"
            + urllib.parse.quote(p) for p in sorted(paths)]


def title_for(url):
    path = urllib.parse.unquote(urllib.parse.urlparse(url).path)
    parts = [p for p in path.split("/") if p]
    if parts and parts[-1].lower() in ("readme.md", "home.md"):
        for p in reversed(parts[:-1]):
            if p not in ("main", "master", "raw", "branch", "wiki", "-"):
                return p
    stem = parts[-1].rsplit(".", 1)[0] if parts else url
    return stem.replace("-", " ").replace("_", " ")


def build_markdown(name, spec):
    urls = list(spec.get("urls", []))
    for t in spec.get("tree", []):
        print(f"  listing {t['repo']}/{t['prefix']}", flush=True)
        urls += github_tree(t["repo"], t["branch"], t["prefix"], t["ext"])
    print(f"  {len(urls)} documents to fetch", flush=True)

    header = name.replace("_", " ").title()
    lines = [header, SEPARATOR, ""]
    ok = 0
    for i, url in enumerate(urls, 1):
        try:
            text = fetch_url(url)
        except Exception as e:
            # Recorded in-band so the gate can block on it (audit_dumps looks
            # for '## FETCH-ERROR'), rather than failing silently.
            lines += [RULE, f"## FETCH-ERROR {title_for(url)}", f"(source: {url})",
                      f"{type(e).__name__}: {e}", ""]
            print(f"  [{i}/{len(urls)}] FAILED {url}: {e}", flush=True)
            continue
        lines += [RULE, f"## {title_for(url)}", f"(source: {url})", ""]
        lines += text.split("\n") + [""]
        ok += 1
        if i % 20 == 0:
            print(f"  [{i}/{len(urls)}] fetched", flush=True)
        time.sleep(0.15)
    print(f"  {ok}/{len(urls)} fetched", flush=True)
    return lines


# ----------------------------------------------------------------- mediawiki ---

def split_params(inner):
    """Split a template body on top-level '|', ignoring nested {{ }} and [ ]."""
    parts, buf, depth = [], [], 0
    i = 0
    while i < len(inner):
        c = inner[i]
        if inner.startswith("{{", i) or inner.startswith("[[", i):
            depth += 1
            buf.append(inner[i:i + 2])
            i += 2
            continue
        if inner.startswith("}}", i) or inner.startswith("]]", i):
            depth -= 1
            buf.append(inner[i:i + 2])
            i += 2
            continue
        if c == "|" and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(c)
        i += 1
    parts.append("".join(buf))
    return parts


def expand_templates(text):
    """Replace {{...}} templates, tracking brace depth so nested braces survive.

    This is the fix for the defect visible in both NixOS dumps. The old rule was
    a flat `\\{\\{[^{}]*\\}\\}` substitution, which cannot match across the braces
    inside a nix attrset -- so `{{File|3=...}}` was left half-deleted, littering
    the dump with 238 '|lang=' and 141 '|name=/' fragments. Code templates now
    render as labeled blocks and their content is kept intact.
    """
    out, i = [], 0
    while i < len(text):
        if not text.startswith("{{", i):
            out.append(text[i])
            i += 1
            continue
        depth, j = 0, i
        while j < len(text):
            if text.startswith("{{", j):
                depth += 1
                j += 2
            elif text.startswith("}}", j):
                depth -= 1
                j += 2
                if depth == 0:
                    break
            else:
                j += 1
        if depth != 0:                      # unbalanced; leave it alone
            out.append(text[i])
            i += 1
            continue
        parts = split_params(text[i + 2:j - 2])
        name = parts[0].strip().lower()
        named, pos = {}, []
        for p in parts[1:]:
            if "=" in p and not p.lstrip().startswith(("{", "[")):
                k, _, v = p.partition("=")
                if k.strip().isidentifier() or k.strip().isdigit():
                    named[k.strip()] = v
                    continue
            pos.append(p)
        ex = expand_templates          # content may itself contain templates
        p0 = ex(pos[0]) if pos else ""

        # Magic words that stand in for characters MediaWiki cannot pass through
        # a template parameter. These appear *inside* code blocks, so dropping
        # them silently corrupts the very snippets worth keeping.
        if name == "!":
            out.append("|")
        elif name == "=":
            out.append("=")
        elif name in ("file", "filesystem"):          # NixOS wiki code block
            code = ex(named.get("3", "")) or p0
            label, lang = named.get("name", ""), named.get("lang", "")
            out.append(f"\n```{lang}" + (f"  # {label}" if label else "")
                       + f"\n{code.strip()}\n```\n")
        elif name == "hc":                            # Arch: header + code
            body = ex(named.get("2", "")) or (ex(pos[1]) if len(pos) > 1 else "")
            out.append(f"\n```  # {p0.strip()}\n{body.strip()}\n```\n")
        elif name == "bc":                            # Arch: block code
            body = ex(named.get("1", "")) or p0
            out.append(f"\n```\n{body.strip()}\n```\n")
        elif name in ("ic", "code", "kbd"):
            out.append(f"`{p0.strip()}`")
        elif name in ("pkg", "aur", "grp"):           # package names are content
            out.append(f"{p0.strip()}")
        elif name == "man":
            sec = p0.strip()
            page = ex(pos[1]).strip() if len(pos) > 1 else ""
            out.append(f"{page}({sec})" if page else sec)
        elif name == "app":
            desc = ex(pos[1]).strip() if len(pos) > 1 else ""
            out.append(f"{p0.strip()}" + (f" — {desc}" if desc else ""))
        elif name in ("note", "warning", "tip", "caution", "important"):
            body = ex(named.get("1", "")) or p0
            out.append(f"\n{name.upper()}: {body.strip()}\n")
        elif name == "bug":
            out.append(f"FS#{p0.strip()}")
        # everything else (Related, Merge, navigation chrome) is dropped
        i = j
    return "".join(out)


def strip_wikitext(text):
    """Wikitext -> plain text, preserving code blocks."""
    import re
    text = expand_templates(text)
    text = re.sub(r"\[\[(?:File|Image):[^\]]*\]\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[https?://\S+\s+([^\]]+)\]", r"\1", text)
    text = re.sub(r"\[https?://\S+\]", "", text)
    text = re.sub(r"'{2,3}", "", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&nbsp;", " "),
                 ("&#91;", "["), ("&#93;", "]")):
        text = text.replace(a, b)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def mw_fetch(api, params, ua):
    params["format"] = "json"
    url = api + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def build_mediawiki(name, spec):
    api, ua = spec["api"], spec.get("user_agent", UA)
    # Skip redirects by default. They are one-line '#REDIRECT [[X]]' stubs that
    # carry no content: including them on the Arch wiki turned 4,349 real pages
    # into 16,249, of which 73% were under 8 lines. They bloat the CONTENTS index
    # and dilute every grep.
    params = {"action": "query", "list": "allpages",
              "apnamespace": str(spec.get("namespace", 0)), "aplimit": "500",
              "apfilterredir": spec.get("filterredir", "nonredirects")}
    titles = []
    while True:
        data = mw_fetch(api, dict(params), ua)
        titles += [p["title"] for p in data["query"]["allpages"]]
        cont = data.get("continue", {}).get("apcontinue")
        if not cont:
            break
        params["apcontinue"] = cont
        time.sleep(0.1)
    print(f"  {len(titles)} pages to fetch", flush=True)

    lines = [name.replace("_", " ").title(), SEPARATOR, ""]
    done = 0
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        try:
            data = mw_fetch(api, {"action": "query", "prop": "revisions",
                                  "rvprop": "content", "rvslots": "main",
                                  "titles": "|".join(batch)}, ua)
            pages = {p["title"]: p["revisions"][0]["slots"]["main"]["*"]
                     for p in data["query"]["pages"].values() if p.get("revisions")}
        except Exception as e:
            print(f"  [warn] batch {i} failed: {e}", flush=True)
            time.sleep(2)
            continue
        for title in batch:
            plain = strip_wikitext(pages.get(title, ""))
            if not plain:
                continue
            lines += [SEPARATOR, f"# {title}", SEPARATOR, ""] + plain.split("\n") + [""]
        done += len(batch)
        if done % 500 < 50:
            print(f"  {done}/{len(titles)}", flush=True)
        time.sleep(0.2)
    return lines


# ------------------------------------------------------------------ texinfo ---

def nix_store_path(spec):
    """Realise a package from the flake and return its store path."""
    cmd = ["nix", "build", "--no-link", "--print-out-paths"]
    cmd += (["--impure", "--expr", spec["expr"]] if "expr" in spec else [spec["attr"]])
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if out.returncode != 0:
        raise RuntimeError(f"nix build failed: {out.stderr.strip().splitlines()[-1:]}")
    return out.stdout.strip().splitlines()[-1]


def build_texinfo(name, spec):
    """Render a package's shipped .info manual.

    The .info files are plain text with nodes separated by 0x1f, so this parses
    them directly rather than shelling out to `info` -- which would mean putting
    texinfo on the system just to read a file that is already readable.
    """
    import glob as _glob
    store = nix_store_path(spec)
    files = sorted(_glob.glob(os.path.join(store, spec["info_glob"])))
    if not files:
        raise RuntimeError(f"no .info files under {store}/{spec['info_glob']}")
    print(f"  {len(files)} info file(s) from {os.path.basename(store)}", flush=True)

    title = spec.get("title", name.replace("_", " ").title())
    lines = [title, SEPARATOR, ""]
    seen, pages = set(), 0
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as f:
            blob = f.read()
        for chunk in blob.split("\x1f"):
            chunk = chunk.lstrip("\n")
            if not chunk.startswith("File: "):
                continue
            head, _, body = chunk.partition("\n")
            m = re.search(r"Node: ([^,\n]+)", head)
            if not m:
                continue
            node = m.group(1).strip()
            # The tag table at the end of the first file repeats every node name
            # with no body; skip those or the dump doubles.
            if node in seen or not body.strip():
                continue
            seen.add(node)
            lines += [SEPARATOR, f"# {node}", SEPARATOR, ""] + body.rstrip().split("\n") + [""]
            pages += 1
    print(f"  {pages} nodes", flush=True)
    return lines


# ------------------------------------------------------------------ doxygen ---

DOXY = re.compile(r"/\*\*(.*?)\*/\s*\n([^\n{;]*)", re.DOTALL)


def clean_doxy(block):
    """Strip the leading '  * ' decoration from a doxygen comment body."""
    out = []
    for line in block.split("\n"):
        line = re.sub(r"^\s*\*\s?", "", line).rstrip()
        out.append(line)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def build_doxygen(name, spec):
    """Extract @brief blocks and the signatures they document from C sources.

    Scoped deliberately: `root` points at one driver directory. The STM32Cube
    tree around it is 2.7 GB of Middlewares, Projects and CMSIS, and sweeping
    those in would produce a dump larger than the Arch wiki.
    """
    import glob as _glob
    root = os.path.expanduser(spec["root"])
    if not os.path.isdir(root):
        raise RuntimeError(f"root not found: {root}")
    files = sorted(_glob.glob(os.path.join(root, spec.get("glob", "*.c"))))
    print(f"  {len(files)} source files under {os.path.basename(root)}", flush=True)

    title = spec.get("title", name.replace("_", " ").title())
    lines = [title, SEPARATOR, "", f"Generated from {root}", ""]
    blocks = 0
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as f:
            src = f.read()
        found = []
        for m in DOXY.finditer(src):
            body, sig = clean_doxy(m.group(1)), m.group(2).strip()
            if not any(l.startswith("@brief") for l in body):
                continue                      # file/group headers, not functions
            if not sig or sig.startswith(("*", "/", "#")):
                sig = ""
            found.append((sig, body))
        if not found:
            continue
        page = os.path.basename(path).replace(".c", "").replace("_", " ")
        lines += [SEPARATOR, f"# {page}", SEPARATOR, ""]
        for sig, body in found:
            if sig:
                lines.append(sig)
            lines += ["    " + l if l else "" for l in body] + [""]
            blocks += 1
    print(f"  {blocks} documented functions across "
          f"{sum(1 for l in lines if l.startswith('# '))} modules", flush=True)
    return lines


BUILDERS = {"nix-options": build_nix_options,
            "markdown": build_markdown,
            "mediawiki": build_mediawiki,
            "texinfo": build_texinfo,
            "doxygen": build_doxygen,
            "pdf": build_pdf}


# ------------------------------------------------------------------ pipeline ---

def dump_path(name):
    return os.path.join(HERE, f"{name}.txt")


def gate(candidate, live, spec):
    """Run audit_dumps.verify. Returns (blockers, warnings)."""
    import audit_dumps
    return audit_dumps.verify(
        candidate,
        against=live if live and os.path.isfile(live) else None,
        min_pages=spec.get("min_pages", 0),
        min_options=spec.get("min_options", 0),
        sentinels=spec.get("sentinels", ()),
    )


def do_scrape(name, spec, args):
    live = dump_path(name)
    cand = live + ".new"
    print(f"\n== {name} ({spec['kind']})", flush=True)
    started = datetime.date.today().isoformat()
    try:
        lines = BUILDERS[spec["kind"]](name, spec)
    except Exception as e:
        print(f"  FAILED to build: {type(e).__name__}: {e}", flush=True)
        return False
    index_dumps.write(cand, lines)
    index_dumps.do_index(cand, datetime.date.today().isoformat(), False, scraped=started)

    blockers, warnings = gate(cand, live, spec)
    for w in warnings:
        print(f"  warn   {w}", flush=True)
    for b in blockers:
        print(f"  BLOCK  {b}", flush=True)

    if args.dry_run:
        print(f"  dry run — candidate left at {os.path.basename(cand)}", flush=True)
        return not blockers
    if blockers and not args.force:
        print(f"  NOT PROMOTED. {os.path.basename(live)} untouched; "
              f"candidate kept at {os.path.basename(cand)}", flush=True)
        return False
    os.replace(cand, live)
    # Re-index under the final name: the index carries a `sed -n ... <file>` hint
    # built from the candidate's basename, which would otherwise point everyone at
    # a .new file that no longer exists. do_index is idempotent and preserves the
    # scrape date, so this only rewrites the header.
    index_dumps.do_index(live, datetime.date.today().isoformat(), False)
    print(f"  promoted -> {os.path.basename(live)}"
          f"{' (forced past blockers)' if blockers else ''}", flush=True)
    return True


def age_days(path):
    if not os.path.isfile(path):
        return None
    for line in index_dumps.read(path)[:8]:
        if line.startswith(index_dumps.HEADING):
            import re
            m = re.search(r"scraped (\d{4}-\d{2}-\d{2})", line)
            if m:
                d = datetime.date.fromisoformat(m.group(1))
                return (datetime.date.today() - d).days
    return None


def cmd_list(args):
    man = load_manifest()
    print(f"{'NAME':24} {'KIND':13} {'PAGES':>7} {'AGE':>6}")
    for name, spec in man.items():
        p = dump_path(name)
        if os.path.isfile(p):
            lines = index_dumps.read(p)
            k, pages = index_dumps.detect(lines)
            a = age_days(p)
            print(f"{name:24} {spec['kind']:13} {len(pages):7} "
                  f"{(str(a) + 'd') if a is not None else '?':>6}")
        else:
            print(f"{name:24} {spec['kind']:13} {'—':>7} {'absent':>6}")
    return 0


def cmd_scrape(args):
    man = load_manifest()
    names = args.names or list(man)
    bad = [n for n in names if n not in man]
    if bad:
        print(f"not in sources.toml: {', '.join(bad)}", file=sys.stderr)
        return 1
    results = [do_scrape(n, man[n], args) for n in names]
    return 0 if all(results) else 1


def cmd_update(args):
    man = load_manifest()
    due = []
    for name, spec in man.items():
        a = age_days(dump_path(name))
        if a is None or a >= args.stale:
            due.append(name)
            print(f"  due: {name} ({a if a is not None else 'no date'}d)", flush=True)
    if not due:
        print(f"nothing older than {args.stale}d", flush=True)
        return 0
    args.names = due
    return cmd_scrape(args)


def cmd_audit(args):
    man = load_manifest()
    names = args.names or [n for n in man if os.path.isfile(dump_path(n))]
    failed = 0
    for name in names:
        spec = man.get(name, {})
        p = dump_path(name)
        if not os.path.isfile(p):
            print(f"  MISSING {name}", flush=True)
            failed += 1
            continue
        blockers, warnings = gate(p, None, spec)
        for w in warnings:
            print(f"  warn   {name}: {w}", flush=True)
        for b in blockers:
            print(f"  BLOCK  {name}: {b}", flush=True)
        if not blockers:
            print(f"  PASS   {name}", flush=True)
        else:
            failed += 1
    return 1 if failed else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="manifest entries and ages")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("scrape", help="fetch, audit, promote on pass")
    p.add_argument("names", nargs="*")
    p.add_argument("--force", action="store_true", help="promote despite blockers")
    p.add_argument("--dry-run", action="store_true", help="never promote")
    p.set_defaults(func=cmd_scrape)

    p = sub.add_parser("update", help="re-scrape anything past the age threshold")
    p.add_argument("--stale", type=int, default=60, help="days (default 60)")
    p.add_argument("--force", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("audit", help="gate the live dumps")
    p.add_argument("names", nargs="*")
    p.set_defaults(func=cmd_audit)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
