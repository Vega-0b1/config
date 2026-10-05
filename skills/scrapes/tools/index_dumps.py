#!/usr/bin/env python3
"""
Add a line-numbered CONTENTS index to the flat-text dumps in this directory.

The index is inserted after the file's title line and lists every page with the
line range it occupies, so a lookup is a seek instead of a scan of 400k lines:

  CONTENTS — 1303 pages · scraped 2026-06-05 · index added 2026-08-14
  Line numbers include this index. Pull one page with:
      sed -n 'START,ENDp' nixos_wiki.txt
  ------------------------------------------------------------
      1314     1433  1Password
    153309   154063  WireGuard
  ------------------------------------------------------------

Line numbers are absolute: they account for the index's own length.

Two page formats are recognized, auto-detected per file:

  wiki  a '# <Title>' line fenced above and below by 60 '=' characters
        (arch_wiki.txt, nixos_wiki.txt, stm32f4_hal.txt, openocd_manual.txt)
  doc   a '## <Title>' line followed within 2 lines by '(source: <URL>)'
        (hypr_waybar_docs.txt, nvim_plugins_docs.txt)

Running this on an already-indexed file is safe: the existing index is detected
and rebuilt, never stacked. No third-party deps required.
"""

import argparse
import datetime
import os
import random
import re
import sys

SEPARATOR = "=" * 60
RULE = "-" * 60
HEADING = "CONTENTS — "
HERE = os.path.dirname(os.path.abspath(__file__))

# Entries are '<start> <end>  <title>'. Never let one begin with '# ': that would
# forge a page banner and corrupt detection on the next run.
ENTRY = "{:>8} {:>8}  {}"


def pages_wiki(lines):
    """Fenced '# Title' banners. Anchor at the opening fence, not the title."""
    out = []
    for i, line in enumerate(lines):
        if line.startswith("# ") and i > 0 and lines[i - 1] == SEPARATOR:
            out.append((i - 1, line[2:].strip()))
    return out


def pages_doc(lines):
    """'## Title' followed by a '(source: URL)' line."""
    out = []
    for i, line in enumerate(lines):
        if line.startswith("## ") and any(
            "(source:" in lines[j] for j in range(i + 1, min(i + 3, len(lines)))
        ):
            out.append((i, line[3:].strip()))
    return out


def detect(lines):
    """Pick the page format by which detector actually finds pages."""
    wiki, doc = pages_wiki(lines), pages_doc(lines)
    if not wiki and not doc:
        return None, []
    return ("wiki", wiki) if len(wiki) >= len(doc) else ("doc", doc)


def index_bounds(lines):
    """Line span (start, end) of an existing CONTENTS block, or None."""
    for i, line in enumerate(lines[:8]):
        if line.startswith(HEADING):
            rules = [j for j, l in enumerate(lines[i:], i) if l == RULE]
            if len(rules) >= 2:
                return i - 1, rules[1] + 1  # include the blank line before/after
    return None


def strip_index(lines):
    span = index_bounds(lines)
    if not span:
        return lines, False
    start, end = span
    return lines[:start] + lines[end + 1:], True


def scraped_date(lines, path):
    """The dump's scrape date, carried in the CONTENTS header across re-indexes.

    It cannot be recovered from mtime: indexing rewrites the file, so mtime marks
    the last index run, not the scrape. Once recorded here it survives.
    """
    for line in lines[:8]:
        if line.startswith(HEADING):
            m = re.search(r"scraped (\d{4}-\d{2}-\d{2})", line)
            if m:
                return m.group(1)
    return None


def build_index(path, lines, pages, date, scraped):
    stamp = f"scraped {scraped} · " if scraped else ""
    head = [
        "",
        f"{HEADING}{len(pages)} pages · {stamp}index added {date}",
        "Line numbers include this index. Pull one page with:",
        f"    sed -n 'START,ENDp' {os.path.basename(path)}",
        RULE,
    ]
    foot = [RULE, ""]
    # The insertion's line count is fixed once the page count is known, so the
    # offset can be applied to every entry in a single pass.
    offset = len(head) + len(pages) + len(foot)
    ends = [pages[k + 1][0] - 1 for k in range(len(pages) - 1)] + [len(lines) - 1]
    body = [
        ENTRY.format(s + 1 + offset, e + 1 + offset, title)
        for (s, title), e in zip(pages, ends)
    ]
    return head + body + foot


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().split("\n")


def write(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_entries(lines):
    """Yield (start, end, title) from an existing index."""
    span = index_bounds(lines)
    if not span:
        return []
    out = []
    for line in lines[span[0]:span[1] + 1]:
        parts = line.split(None, 2)
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            out.append((int(parts[0]), int(parts[1]), parts[2]))
    return out


def do_check(path, sample):
    """Verify index entries resolve to the pages they name. True if all pass."""
    lines = read(path)
    entries = parse_entries(lines)
    if not entries:
        print(f"{os.path.basename(path):24} NO INDEX", flush=True)
        return False
    picks = random.sample(entries, min(sample, len(entries)))
    bad = []
    for start, end, title in picks:
        if start >= end or start > len(lines):
            bad.append((start, title, "range invalid"))
            continue
        segment = "\n".join(lines[start - 1:min(end, start + 8)])
        if title.split()[0][:20] not in segment:
            bad.append((start, title, "title not in range"))
    status = "OK" if not bad else f"{len(bad)} FAILED"
    print(
        f"{os.path.basename(path):24} {len(entries):5} entries, "
        f"sampled {len(picks):3} -> {status}",
        flush=True,
    )
    for start, title, why in bad[:5]:
        print(f"    line {start}: {title[:40]} ({why})", flush=True)
    return not bad


def do_index(path, date, dry_run, scraped=None):
    lines = read(path)
    scraped = scraped or scraped_date(lines, path)
    body, had = strip_index(lines)
    kind, pages = detect(body)
    if not pages:
        print(f"{os.path.basename(path):24} no pages found, skipped", flush=True)
        return False
    block = build_index(path, body, pages, date, scraped)
    out = body[:2] + block + body[2:]
    verb = "reindexed" if had else "indexed"
    print(
        f"{os.path.basename(path):24} {kind:4} {len(pages):5} pages, "
        f"{verb}, +{len(block)} lines ({len(body)} -> {len(out)})",
        flush=True,
    )
    if not dry_run:
        write(path, out)
    return True


def do_strip(path, dry_run):
    lines = read(path)
    out, had = strip_index(lines)
    if not had:
        print(f"{os.path.basename(path):24} no index present", flush=True)
        return False
    print(
        f"{os.path.basename(path):24} index removed "
        f"({len(lines)} -> {len(out)} lines)",
        flush=True,
    )
    if not dry_run:
        write(path, out)
    return True


def main():
    ap = argparse.ArgumentParser(
        description="Add, remove, or verify CONTENTS indexes on the dumps."
    )
    ap.add_argument("files", nargs="*", help="dump files (default: *.txt here)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--strip", action="store_true", help="remove the index")
    mode.add_argument("--check", action="store_true", help="verify entries resolve")
    ap.add_argument("--dry-run", action="store_true", help="write nothing")
    ap.add_argument("--scraped", metavar="YYYY-MM-DD",
                    help="record/override the dump's scrape date in the header")
    ap.add_argument("--sample", type=int, default=40,
                    help="entries to verify per file with --check (default 40)")
    args = ap.parse_args()

    paths = args.files or sorted(
        os.path.join(HERE, f) for f in os.listdir(HERE) if f.endswith(".txt")
    )
    if not paths:
        print("no dump files found", file=sys.stderr)
        return 1

    date = datetime.date.today().isoformat()
    ok = True
    for path in paths:
        if not os.path.isfile(path):
            print(f"{path}: not found", file=sys.stderr)
            ok = False
            continue
        if args.check:
            ok &= do_check(path, args.sample)
        elif args.strip:
            do_strip(path, args.dry_run)
        else:
            do_index(path, date, args.dry_run, args.scraped)

    if args.dry_run:
        print("\n(dry run — nothing written)", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
