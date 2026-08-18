#!/usr/bin/env python3
"""
Analyze the flat-text dumps in this directory.

Every subcommand here exists because it caught something real:

  pages     True page counts. A raw `grep -c '^# '` overcounts badly — both
            scrapers emit '# ' banners for stray body lines and shell comments
            ('# With Zplug:'), so arch_wiki reports 11,019 against 4,359 real.
  compare   Title and token overlap between two dumps, including dropped-code
            detection. This is what proved nix_manual_wiki.txt was a worse copy
            of nixos_wiki.txt -- it had replaced 250 code blocks with bare
            'lang=nix' stubs -- which is why it was retired 2026-08-14.
  options   The NixOS options reference appended to both NixOS dumps. Placeholder
            names must be normalized or degraded renderings ('settings..disks'
            against 'settings.<drive-bay-name>.disks') read as unique options.
  stale     Scrape age per file, plus the known Hyprland version skew.
  coverage  Neovim plugins configured in a .nix file against those documented in
            nvim_plugins_docs.txt, in both directions.

No third-party deps required.
"""

import argparse
import datetime
import os
import re
import sys
from collections import Counter

SEPARATOR = "=" * 60
HERE = os.path.dirname(os.path.abspath(__file__))

# An option entry in the NixOS options reference: indented 7 spaces, dotted path.
OPTION = re.compile(r"^ {7}([a-z][a-zA-Z0-9_]*\.[^\s]+)\s*$")
TOKEN = re.compile(r"[A-Za-z0-9_.\-/]{2,}")
TRANSLATION = re.compile(
    r"/(zh|zh-hans|zh-hant|ja|de|fr|ru|es|pt|it|ko|tr|pl|nl|uk|vi|id|fa|ar)$"
)


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().split("\n")


def body(lines):
    """Drop a CONTENTS index if present, so counts reflect real content."""
    for i, line in enumerate(lines[:8]):
        if line.startswith("CONTENTS — "):
            rules = [j for j, l in enumerate(lines[i:], i) if l == "-" * 60]
            if len(rules) >= 2:
                return lines[:i - 1] + lines[rules[1] + 2:]
    return lines


def real_pages(lines):
    """Fenced banners only — the discriminator against misparsed body lines."""
    return [
        (i - 1, l[2:].strip())
        for i, l in enumerate(lines)
        if l.startswith("# ") and i > 0 and lines[i - 1] == SEPARATOR
    ]


def doc_pages(lines):
    return [
        (i, l[3:].strip())
        for i, l in enumerate(lines)
        if l.startswith("## ")
        and any("(source:" in lines[j] for j in range(i + 1, min(i + 3, len(lines))))
    ]


def sections(lines):
    """{title: text} for fenced pages, first occurrence wins."""
    out, cur, buf = {}, None, []
    for line in lines:
        if line.startswith("# "):
            if cur is not None:
                out.setdefault(cur, "\n".join(buf))
            cur, buf = line[2:].strip().replace("`", ""), []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out.setdefault(cur, "\n".join(buf))
    return out


def dumps(paths):
    return paths or sorted(
        os.path.join(HERE, f) for f in os.listdir(HERE) if f.endswith(".txt")
    )


def cmd_pages(args):
    print(f"{'FILE':24} {'REAL':>6} {'RAW #':>7} {'MISPARSED':>10}  KIND")
    for path in dumps(args.files):
        lines = body(read(path))
        wiki, doc = real_pages(lines), doc_pages(lines)
        raw = sum(1 for l in lines if l.startswith("# "))
        if len(wiki) >= len(doc):
            real, kind = len(wiki), "wiki"
        else:
            real, kind = len(doc), "doc"
        print(
            f"{os.path.basename(path):24} {real:6} {raw:7} "
            f"{raw - real if kind == 'wiki' else 0:10}  {kind}"
        )
        if args.translations and kind == "wiki":
            trans = [t for _, t in wiki if TRANSLATION.search(t)]
            loc = Counter()
            for _, t in wiki:
                m = re.search(r"\(([^)]+)\)$", t)
                if m and not m.group(1)[0].islower():
                    loc[m.group(1)] += 1
            langs = {k: v for k, v in loc.items() if v >= 20}
            if trans:
                print(f"    {len(trans)} translation pages (/xx suffix)")
            if langs:
                total = sum(langs.values())
                top = ", ".join(
                    f"{k} {v}" for k, v in sorted(langs.items(), key=lambda x: -x[1])
                )
                print(f"    {total} localized pages: {top}")
    return 0


def cmd_compare(args):
    a_lines, b_lines = body(read(args.a)), body(read(args.b))
    a, b = sections(a_lines), sections(b_lines)
    na, nb = os.path.basename(args.a), os.path.basename(args.b)
    shared = sorted(set(a) & set(b))
    print(f"{na}: {len(a)} titles    {nb}: {len(b)} titles")
    print(f"shared {len(shared)}   only {na}: {len(set(a)-set(b))}   "
          f"only {nb}: {len(set(b)-set(a))}")

    norm = lambda s: re.sub(r"\s+", " ", s.replace("`", "")).strip()
    same = sum(1 for t in shared if norm(a[t]) == norm(b[t]))
    print(f"of the shared, {same} identical after normalization, "
          f"{len(shared)-same} differ")

    # Whole-file token coverage: what does A say that B never says anywhere?
    ta = Counter(TOKEN.findall("\n".join(a_lines).replace("`", "")))
    tb = Counter(TOKEN.findall("\n".join(b_lines).replace("`", "")))
    absent = {w: n for w, n in ta.items() if w not in tb}
    print(f"tokens in {na} absent from {nb} entirely: {len(absent)} distinct, "
          f"{sum(absent.values())} occurrences "
          f"({100*sum(absent.values())/max(sum(ta.values()),1):.3f}%)")

    # Code-block loss. The weaker scraper drops fenced blocks and leaves a stub.
    stub = re.compile(r"^\s*(\|?name=[^|]*\|)?lang=[a-z]*$")
    code = re.compile(r"^\s+[a-zA-Z_][a-zA-Z0-9_.\"-]* = ")
    for name, lines in ((na, a_lines), (nb, b_lines)):
        print(f"  {name:24} {sum(1 for l in lines if stub.match(l)):4} dropped-code "
              f"stubs, {sum(1 for l in lines if code.match(l)):6} code-like lines")
    return 0


def norm_option(name):
    """Collapse placeholder spellings so the two dumps' options compare.

    The weaker scraper drops '<drive-bay-name>' entirely, leaving a doubled dot;
    removing the placeholder and then collapsing runs of dots maps both forms to
    the same key. Doing it in one regex pass does not: the dot preceding '<' is
    scanned before the placeholder is gone, so its lookahead fails.
    """
    return re.sub(r"\.{2,}", ".", re.sub(r"<[^>]*>", "", name))


OPTIONS_BANNER = re.compile(r"options reference|NixOS Manual", re.IGNORECASE)


def options_start(lines):
    """First line of the appended options reference, or None.

    Prefer the page banner introducing the block: a wiki dump that appends an
    options reference labels it '# NixOS options reference' or '# NixOS Manual'.
    Only fall back to shape-matching, which anchors too early — wiki pages that
    document options carry the same indented-path-then-'Type:' shape.
    """
    for i, title in real_pages(lines):
        if OPTIONS_BANNER.search(title):
            return i
    for i, line in enumerate(lines):
        if OPTION.match(line) and any(
            "Type:" in lines[j] for j in range(i + 1, min(i + 15, len(lines)))
        ):
            return i
    return None


def options_names(lines):
    start = options_start(lines)
    if start is None:
        return set()
    return {m.group(1) for m in (OPTION.match(l) for l in lines[start:]) if m}


def cmd_options(args):
    sets = {}
    for path in dumps(args.files):
        lines = body(read(path))
        names = options_names(lines)
        if not names:
            continue
        sets[os.path.basename(path)] = names
        print(f"{os.path.basename(path):24} {len(names):6} options")
    if len(sets) == 2:
        (na, a), (nb, b) = sets.items()
        # Normalize placeholders before diffing, or degraded renderings look unique.
        cn = lambda s: {norm_option(x) for x in s}
        ca, cb = cn(a), cn(b)
        print(f"\nafter placeholder normalization:")
        print(f"  shared {len(ca&cb)}   only {na}: {len(ca-cb)}   only {nb}: {len(cb-ca)}")
        for label, extra in ((na, ca - cb), (nb, cb - ca)):
            if extra and len(extra) <= 12:
                print(f"  only in {label}: {', '.join(sorted(extra)[:12])}")
    return 0


def cmd_stale(args):
    """Age since the SCRAPE, which is not mtime.

    Indexing rewrites every dump, so mtime tracks the last index run and would
    report everything as fresh. The real date is recorded in the CONTENTS header
    by index_dumps.py; fall back to mtime only when it is missing, and say so.
    """
    today = datetime.date.today()
    print(f"{'FILE':24} {'SCRAPED':>12} {'AGE':>8}")
    for path in dumps(args.files):
        src = "header"
        d = None
        for line in read(path)[:8]:
            if line.startswith("CONTENTS — "):
                m = re.search(r"scraped (\d{4}-\d{2}-\d{2})", line)
                if m:
                    d = datetime.date.fromisoformat(m.group(1))
                break
        if d is None:
            d = datetime.date.fromtimestamp(os.path.getmtime(path))
            src = "mtime?"
        age = (today - d).days
        flag = "  STALE" if age > args.days else ""
        print(f"{os.path.basename(path):24} {d.isoformat():>12} {age:5}d  "
              f"{src}{flag}")
    hyp = os.path.join(HERE, "hypr_waybar_docs.txt")
    if os.path.isfile(hyp):
        text = "\n".join(read(hyp)[:400])
        print("\nhypr_waybar_docs.txt documents Hyprland 0.55; verify the running "
              "version with `hyprctl version` before trusting API details.")
    return 0


def plugin_key(name):
    """Collapse the naming variants so nixpkgs attrs and repo names compare.

    blink-cmp / blink.cmp -> blinkcmp     harpoon2 / harpoon -> harpoon
    nvim-notify           -> notify       noice-nvim         -> noice
    """
    k = name.lower()
    for suffix in (".nvim", "-nvim", ".lua", "_nvim"):
        if k.endswith(suffix):
            k = k[: -len(suffix)]
    if k.startswith("nvim-") or k.startswith("nvim."):
        k = k[5:]
    k = re.sub(r"[-._]", "", k)
    return re.sub(r"\d+$", "", k) or name.lower()


def configured_plugins(path):
    """Names inside the `plugins = with pkgs.vimPlugins; [ ... ]` list.

    Two declaration styles appear there: `plugin = <name>;` entries (sometimes
    with a call attached, as in `nvim-treesitter.withPlugins (p: [...])`) and
    bare identifiers on their own line, such as `nvim-dap` or `plenary-nvim`.
    """
    lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
    try:
        start = next(i for i, l in enumerate(lines) if "with pkgs.vimPlugins" in l)
    except StopIteration:
        return set()
    found = set()
    for line in lines[start + 1:]:
        if re.match(r"^\s{0,4}\];", line):
            break
        m = re.search(r"plugin\s*=\s*([a-zA-Z0-9_.-]+)", line)
        if m:
            found.add(m.group(1).split(".")[0] if ".with" in m.group(1) else m.group(1))
            continue
        # Require a '-' or '.': every nixpkgs vimPlugins attr has one, while the
        # Lua keywords that share this indentation ('end', 'return') do not.
        m = re.match(r"^\s{4,10}([a-z][a-zA-Z0-9_]*[-.][a-zA-Z0-9_.-]*)\s*$", line)
        if m:
            found.add(m.group(1))
    return found


def documented_plugins(path):
    """Repo names from page-level '(source: URL)' lines only.

    Scanning the whole file instead picks up URLs quoted inside README bodies
    (media.repo, vscodelua) that are not plugins at all.

    Host-agnostic on purpose: the plugin set spans github, codeberg, and gitlab,
    and every one of those puts the repo second in the path (/owner/repo/...).
    """
    repos = set()
    for line in read(path):
        if "(source:" in line:
            m = re.search(r"https?://[^/\s]+/([^/\s)]+)/([^/\s)]+)", line)
            if m:
                owner, repo = m.group(1), m.group(2)
                # raw.githubusercontent.com/wiki/<owner>/<repo>/... shifts by one
                if owner == "wiki":
                    m2 = re.search(r"/wiki/[^/]+/([^/\s)]+)", line)
                    if m2:
                        repo = m2.group(1)
                repos.add(repo)
    return repos


def cmd_coverage(args):
    doc = os.path.join(HERE, "nvim_plugins_docs.txt")
    cfg_names = configured_plugins(args.config)
    doc_names = documented_plugins(doc)
    cfg = {plugin_key(n): n for n in cfg_names}
    dok = {plugin_key(n): n for n in doc_names}
    print(f"configured in {os.path.basename(args.config)}: {len(cfg)}")
    print(f"documented in nvim_plugins_docs.txt: {len(dok)}")
    missing = sorted(cfg[k] for k in cfg.keys() - dok.keys())
    stale = sorted(dok[k] for k in dok.keys() - cfg.keys())
    print(f"\nused but NOT documented ({len(missing)}): {', '.join(missing) or '—'}")
    print(f"documented but NOT used ({len(stale)}): {', '.join(stale) or '—'}")
    return 0


def verify(path, against=None, min_pages=0, min_options=0, sentinels=(),
           tolerance=0.9):
    """Gate a candidate dump. Returns (blockers, warnings).

    Every check here corresponds to a defect found in the existing dumps, so the
    gate is calibrated against real failures rather than imagined ones.
    """
    blockers, warnings = [], []
    lines = read(path)
    content = body(lines)
    kind, pages = ("wiki", real_pages(content))
    if len(doc_pages(content)) > len(pages):
        kind, pages = "doc", doc_pages(content)
    n = len(pages)
    opts = len(options_names(content))

    # -- blockers -------------------------------------------------------------
    if min_pages and n < min_pages:
        blockers.append(f"only {n} pages, manifest requires >= {min_pages}")
    if min_options and opts < min_options:
        blockers.append(f"only {opts} options, manifest requires >= {min_options}")

    # Regression against the dump being replaced. This is what catches a scrape
    # that silently lost a batch of pages, as nixos_wiki.txt did with E-F.
    if against and os.path.isfile(against):
        prev = body(read(against))
        pn = max(len(real_pages(prev)), len(doc_pages(prev)))
        po = len(options_names(prev))
        if pn and n < pn * tolerance:
            blockers.append(
                f"{n} pages vs {pn} in the current dump "
                f"({100*n/pn:.0f}%, floor {100*tolerance:.0f}%)")
        # Growth is suspicious too. A scrape that suddenly doubles has usually
        # changed what it collects rather than found new content -- including
        # redirect stubs turned 4,349 Arch pages into 16,249, and the gate passed
        # because it only looked for shrinkage.
        if pn and n > pn * 1.5:
            blockers.append(
                f"{n} pages vs {pn} currently ({n/pn:.1f}x) — verify this is new "
                f"content, not a change in what the scraper collects")
        if po and opts < po * tolerance:
            blockers.append(f"{opts} options vs {po} currently ({100*opts/po:.0f}%)")

    text = "\n".join(content)
    for s in sentinels:
        if s not in text:
            blockers.append(f"sentinel missing: {s!r}")

    errs = sum(1 for l in lines if l.startswith("## FETCH-ERROR"))
    if errs:
        blockers.append(f"{errs} source(s) failed to fetch")

    # -- warnings -------------------------------------------------------------
    stubs = sum(1 for l in content if re.match(r"^\s*(\|?name=[^|]*\|)?lang=[a-z]*$", l))
    if stubs:
        warnings.append(f"{stubs} dropped code blocks (bare 'lang=' stubs)")

    # Count '# ' lines outside code fences only. A well-parsed dump preserves
    # shell comments inside ``` blocks, which would otherwise inflate this and
    # make a better scrape look worse -- the Arch re-scrape went 60% -> 70% purely
    # because 7,341 more comment lines survived inside code.
    raw, fence = 0, False
    for l in content:
        if l.startswith("```"):
            fence = not fence
        elif l.startswith("# ") and not fence:
            raw += 1
    if kind == "wiki" and raw and n and raw > n * 1.5:
        warnings.append(
            f"{raw - n} misparsed banners ({100*(raw-n)/raw:.0f}% of '# ' lines "
            f"outside code fences)")

    # A large block of reference data filed under a banner that does not describe
    # it -- the failure that made 242k lines of options read as the Zsh page.
    # A block under its own options banner is correctly labeled and fine.
    if pages and kind == "wiki":
        tail = len(content) - pages[-1][0]
        looks_like_reference = opts > 500
        labeled = OPTIONS_BANNER.search(pages[-1][1])
        if tail > max(5000, len(content) * 0.15) and looks_like_reference and not labeled:
            warnings.append(
                f"{tail} lines of reference data filed under {pages[-1][1]!r}")

    return blockers, warnings


def cmd_verify(args):
    blockers, warnings = verify(
        args.file, against=args.against, min_pages=args.min_pages,
        min_options=args.min_options, sentinels=args.sentinel or (),
        tolerance=args.tolerance)
    name = os.path.basename(args.file)
    for w in warnings:
        print(f"  warn   {name}: {w}", flush=True)
    for b in blockers:
        print(f"  BLOCK  {name}: {b}", flush=True)
    if not blockers:
        print(f"  PASS   {name}"
              f"{' (with %d warning(s))' % len(warnings) if warnings else ''}",
              flush=True)
    return 1 if blockers else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("verify", help="gate a candidate dump; exit 1 if it fails")
    p.add_argument("file")
    p.add_argument("--against", help="current dump to compare against")
    p.add_argument("--min-pages", type=int, default=0)
    p.add_argument("--min-options", type=int, default=0)
    p.add_argument("--sentinel", action="append", help="string that must survive")
    p.add_argument("--tolerance", type=float, default=0.9,
                   help="fraction of the current dump's pages required (default 0.9)")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("pages", help="true page counts vs raw banner counts")
    p.add_argument("files", nargs="*")
    p.add_argument("--translations", action="store_true",
                   help="also break down non-English pages")
    p.set_defaults(func=cmd_pages)

    p = sub.add_parser("compare", help="title/token overlap between two dumps")
    p.add_argument("a")
    p.add_argument("b")
    p.set_defaults(func=cmd_compare)

    p = sub.add_parser("options", help="NixOS options reference stats and diff")
    p.add_argument("files", nargs="*")
    p.set_defaults(func=cmd_options)

    p = sub.add_parser("stale", help="scrape age per dump")
    p.add_argument("files", nargs="*")
    p.add_argument("--days", type=int, default=90, help="stale threshold (default 90)")
    p.set_defaults(func=cmd_stale)

    p = sub.add_parser("coverage", help="Neovim plugin docs vs configured plugins")
    p.add_argument("--config", default="/etc/nixos/nix-config/neovim.nix")
    p.set_defaults(func=cmd_coverage)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
