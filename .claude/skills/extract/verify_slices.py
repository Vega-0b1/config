#!/usr/bin/env python3
"""Verify that every chapter slice starts at its own chapter heading.

Mechanical check only, and it answers exactly one question per slice: is this
file's first line the chapter heading it was supposed to be cut at? That is
/extract R16b1, and it is the single property that separated every correct
slice on this system from every broken one.

The failure it catches is invisible by inspection. A slice cut one chapter-opener
too late has the right filename, plausible content, and no error anywhere in it —
it is simply missing its own opening paragraphs and carrying the next chapter's.
Two classes shipped that way for months.

Usage:
    verify_slices.py <class_dir> [<class_dir> ...]
    verify_slices.py            # checks every class under ~/edu

The chapter heading pattern is read from the class's CLAUDE.md `## Source
Profile` section (`- **Chapter heading:** ...`). Backtick-quoted regexes are
used as written; the `<N>` placeholder becomes a capture group.

Exit status: 0 = every slice correct, 1 = at least one wrong, 2 = usage error.
"""

import re
import sys
from pathlib import Path

PROFILE_RE = re.compile(r"^-\s*\*\*Chapter heading:\*\*\s*(.+)$", re.M)
NOTES_RE = re.compile(r"^-\s*\*\*Notes file:\*\*\s*`([^`]+)`", re.M)


def chapter_pattern(claude_md_text):
    """Pull the chapter heading regex out of a Source Profile line.

    Returns None when the profile declares `none`, which is a legitimate state
    (R0c0a) and not a failure — such a class simply has no slices to check.
    """
    m = PROFILE_RE.search(claude_md_text)
    if not m:
        return None
    decl = m.group(1).strip()
    if decl.lower().startswith("none"):
        return None
    codes = re.findall(r"`([^`]+)`", decl)
    if not codes:
        return None
    pat = codes[0]
    # `<N>` is how the profiles write the chapter number; make it a group.
    pat = pat.replace("<N>", r"(\d+)")
    # Profiles also write bare `N` inside a pattern (e.g. `^# Chapter N`).
    if "(\\d+)" not in pat:
        pat = re.sub(r"(?<![\\\w])N(?![\w>])", r"(\\d+)", pat)
    # A trailing `<Title>` placeholder is prose, not regex.
    pat = pat.replace("<Title>", "").rstrip()
    try:
        return re.compile(pat)
    except re.error as e:
        print(f"  ! unusable chapter pattern {pat!r}: {e}", file=sys.stderr)
        return None


def check_class(class_dir):
    """Returns (checked, failures, skipped_reason)."""
    cm = class_dir / "CLAUDE.md"
    if not cm.is_file():
        return 0, [], "no CLAUDE.md"
    text = cm.read_text(encoding="utf-8")
    pat = chapter_pattern(text)
    if pat is None:
        return 0, [], "no chapter heading pattern declared"
    nm = NOTES_RE.search(text)
    if not nm:
        return 0, [], "no notes file declared"
    notes = class_dir / nm.group(1)
    if not notes.is_file():
        return 0, [], f"notes file missing: {notes}"

    full = notes.read_text(encoding="utf-8").split("\n")
    headings = {}
    for i, line in enumerate(full, 1):
        m = pat.match(line)
        if m and m.groups():
            n = int(m.group(1))
            headings.setdefault(n, (i, line))

    chapters_dir = class_dir / notes.parent.relative_to(class_dir) / "chapters"
    checked, failures = 0, []
    for n, (lineno, heading) in sorted(headings.items()):
        slice_path = None
        for word in ("chapter", "capitulo"):
            p = chapters_dir / f"{word}{n}" / f"{word}{n}.md"
            if p.is_file():
                slice_path = p
                break
        if slice_path is None:
            failures.append((n, None, heading, "no slice on disk"))
            continue
        checked += 1
        body = slice_path.read_text(encoding="utf-8").split("\n")
        first = next((l for l in body if l.strip()), "")
        if first.strip() != heading.strip():
            failures.append((n, slice_path, heading, first))
    return checked, failures, None


def main(argv):
    if len(argv) > 1:
        dirs = [Path(a) for a in argv[1:]]
    else:
        edu = Path.home() / "edu"
        if not edu.is_dir():
            print("usage: verify_slices.py <class_dir> ...", file=sys.stderr)
            return 2
        dirs = sorted(d for d in edu.iterdir() if (d / "CLAUDE.md").is_file())

    total_checked = total_failed = 0
    for d in dirs:
        checked, failures, skip = check_class(d)
        if skip:
            print(f"{d.name:24} skipped — {skip}")
            continue
        hard = [f for f in failures]
        total_checked += checked
        total_failed += len(hard)
        status = "OK" if not hard else f"{len(hard)} WRONG"
        print(f"{d.name:24} {checked:3} slices checked   {status}")
        for n, path, heading, first in hard:
            print(f"    chapter{n}: expected first line {heading.strip()!r}")
            print(f"              got               {str(first).strip()[:70]!r}")

    print(f"\nslices checked : {total_checked}")
    print(f"slices wrong   : {total_failed}")
    if total_failed:
        print(
            "\nA wrong first line means the slice was cut somewhere other than its "
            "chapter heading — almost always at the first section heading, which "
            "drops the chapter's opening and pulls in the next chapter's (R16b2)."
        )
        return 1
    print("\nEvery slice starts at its own chapter heading.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
