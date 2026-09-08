#!/usr/bin/env python3
"""Replace one repaired chapter slice in its full notes file.

Usage: splice_chapter.py [--dry-run] <slice.md> <notes.md>
"""
import re
import shutil
import sys

MARKER_RE = re.compile(r"^<!--\s*visual-repair:\s*done\s*-->\s*$")
# Supports Chapter, Capitulo, and numbered headings with or without titles.
CHAPTER_RE = re.compile(
    r"^#{1,6}\s+(?:(?:chapter|capitulo)\s+)?(\d+)(?:\s*:\s*.*|\s+[^.].*)?$",
    re.IGNORECASE,
)


def load(path):
    with open(path, encoding="utf-8") as f:
        return f.read().split("\n")


def heading(line):
    match = CHAPTER_RE.match(line)
    return int(match.group(1)) if match else None


def slice_heading(lines):
    for line in lines:
        if not line.strip() or MARKER_RE.match(line):
            continue
        return line, heading(line)
    return None, None


def chapter_positions(lines):
    return [(index, number) for index, line in enumerate(lines)
            if (number := heading(line)) is not None]


def main():
    args = sys.argv[1:]
    dry_run = False
    if args and args[0] == "--dry-run":
        dry_run, args = True, args[1:]
    if len(args) != 2:
        sys.exit(__doc__)
    slice_path, notes_path = args
    slice_lines, notes_lines = load(slice_path), load(notes_path)
    first, number = slice_heading(slice_lines)
    if number is None:
        sys.exit(f"error: {slice_path} does not begin with a supported chapter heading\n"
                 f"       first content line was: {first!r}")
    positions = chapter_positions(notes_lines)
    matches = [index for index, candidate in positions if candidate == number]
    if len(matches) != 1:
        detail = "not found" if not matches else f"appears {len(matches)} times"
        sys.exit(f"error: chapter {number} {detail} in {notes_path}; target is ambiguous")
    start = matches[0]
    end = next((index for index, _ in positions if index > start), len(notes_lines))
    body = [line for line in slice_lines if not MARKER_RE.match(line)]
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    replacement = body + [""]
    old = notes_lines[start:end]
    new_lines = notes_lines[:start] + replacement + notes_lines[end:]
    if len(chapter_positions(notes_lines)) != len(chapter_positions(new_lines)):
        sys.exit("error: splice would change the chapter count; refusing")
    changed = sum(a != b for a, b in zip(old, replacement)) + abs(len(old) - len(replacement))
    print(f"chapter        : {number}")
    print(f"notes range    : lines {start + 1}-{end}")
    print(f"lines differing: {changed}")
    if dry_run:
        print("dry run - nothing written")
        return
    shutil.copyfile(notes_path, notes_path + ".bak")
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))


if __name__ == "__main__":
    main()
