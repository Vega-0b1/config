#!/usr/bin/env python3
"""Write a repaired chapter slice back into the full textbook notes file.

Visual repair (book.md R4b) fixes OCR damage in a chapter slice by reading the
page images. Without this script that repair lives only in the slice, and the
notes file it was cut from keeps the damaged text forever. Two files then
disagree about what the book says, and the stale one is the fallback source
book.md R2 reaches for when a slice is missing — so the drift is not merely
untidy, it is a path back to text you already paid to fix.

This replaces the chapter's line range in the notes file with the slice's
content. The range is found the same way `/extract` R16b cut it: from the
chapter heading to the line before the next chapter heading.

Refuses to run when the splice would not be a clean swap:
  - slice's first content line is not a chapter heading   -> wrong file
  - that chapter heading is absent from the notes file    -> wrong pairing
  - the heading appears more than once in the notes file  -> ambiguous target
  - the resulting file would lose or gain a chapter       -> range miscut

Usage:
    splice_chapter.py <slice.md> <notes.md>
    splice_chapter.py --dry-run <slice.md> <notes.md>
"""

import re
import shutil
import sys

CHAPTER_RE = re.compile(r"^# Chapter (\d+):")
MARKER_RE = re.compile(r"^<!--\s*visual-repair:\s*done\s*-->\s*$")


def load(path):
    with open(path, "r") as f:
        return f.read().split("\n")


def slice_heading(slice_lines):
    """First non-marker, non-blank line must be the chapter heading."""
    for line in slice_lines:
        if not line.strip() or MARKER_RE.match(line):
            continue
        m = CHAPTER_RE.match(line)
        return (line, int(m.group(1))) if m else (line, None)
    return (None, None)


def chapter_positions(notes_lines):
    return [(i, int(m.group(1)))
            for i, l in enumerate(notes_lines)
            if (m := CHAPTER_RE.match(l))]


def main():
    args = sys.argv[1:]
    dry = False
    if args and args[0] == "--dry-run":
        dry, args = True, args[1:]
    if len(args) != 2:
        sys.exit(__doc__)
    slice_path, notes_path = args

    slice_lines = load(slice_path)
    notes_lines = load(notes_path)

    heading, ch_num = slice_heading(slice_lines)
    if ch_num is None:
        sys.exit(f"error: {slice_path} does not begin with a '# Chapter <N>:' heading\n"
                 f"       first content line was: {heading!r}")

    positions = chapter_positions(notes_lines)
    matches = [(i, n) for i, n in positions if n == ch_num]
    if not matches:
        sys.exit(f"error: chapter {ch_num} not found in {notes_path}")
    if len(matches) > 1:
        sys.exit(f"error: chapter {ch_num} appears {len(matches)} times in {notes_path}; "
                 f"target is ambiguous")

    start = matches[0][0]
    later = [i for i, _ in positions if i > start]
    end = later[0] if later else len(notes_lines)

    # The marker is slice bookkeeping; the notes file should not carry it.
    body = [l for l in slice_lines if not MARKER_RE.match(l)]
    while body and not body[-1].strip():
        body.pop()
    while body and not body[0].strip():
        body.pop(0)

    old = notes_lines[start:end]
    replacement = body + [""]  # restore the blank the cut consumed
    new_lines = notes_lines[:start] + replacement + notes_lines[end:]

    before = len(chapter_positions(notes_lines))
    after = len(chapter_positions(new_lines))
    if before != after:
        sys.exit(f"error: splice would change the chapter count {before} -> {after}; refusing")

    # Compare against what actually lands, so an unchanged slice reports zero.
    changed = (sum(1 for a, b in zip(old, replacement) if a != b)
               + abs(len(old) - len(replacement)))

    print(f"chapter        : {ch_num}")
    print(f"notes range    : lines {start + 1}-{end}")
    print(f"old / new lines: {len(old)} -> {len(replacement)}")
    print(f"lines differing: {changed}")
    print(f"chapters intact: {after}")

    if dry:
        print("\ndry run - nothing written")
        return

    shutil.copyfile(notes_path, notes_path + ".bak")
    with open(notes_path, "w") as f:
        f.write("\n".join(new_lines))
    print(f"\nwrote {notes_path}  (backup at {notes_path}.bak)")


if __name__ == "__main__":
    main()
