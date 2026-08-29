#!/usr/bin/env python3
"""Verify that textbook chapter slices match their notes-file headings.

Exit status: 0 = at least one slice verified and none failed, or every class
legitimately skipped; 1 = verification failed; 2 = usage error.
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

PROFILE_RE = re.compile(r"^-\s*\*\*Chapter heading:\*\*\s*(.+)$", re.M)
NOTES_RE = re.compile(r"^-\s*\*\*Notes file:\*\*\s*`([^`]+)`", re.M)
SLICE_RE = re.compile(r"^(chapter|capitulo)(\d+)$")
REPAIR_MARKER = "<!-- visual-repair: done -->"


@dataclass
class Result:
    status: str
    checked: int = 0
    failures: list[str] = field(default_factory=list)
    reason: str = ""


def chapter_pattern(text: str):
    """Return (pattern, reason), where reason is ``none`` or an error."""
    match = PROFILE_RE.search(text)
    if not match:
        return None, "no chapter heading pattern declared"
    declaration = match.group(1).strip()
    if declaration.lower().startswith("none"):
        return None, "declared none"
    codes = re.findall(r"`([^`]+)`", declaration)
    if not codes:
        return None, "chapter heading pattern has no backtick-quoted regex"
    pattern = codes[0].replace("<N>", r"(\d+)")
    if "(\\d+)" not in pattern:
        pattern = re.sub(r"(?<![\\\w])N(?![\w>])", r"(\\d+)", pattern)
    pattern = pattern.replace("<Title>", "").rstrip()
    try:
        compiled = re.compile(pattern)
    except re.error as error:
        return None, f"unusable chapter pattern {pattern!r}: {error}"
    if compiled.groups < 1:
        return None, "chapter heading pattern does not capture a chapter number"
    return compiled, ""


def slice_files(class_dir: Path, notes: Path | None = None):
    """Return canonical chapter/capitulo slices keyed by (word, number)."""
    roots = [notes.parent / "chapters"] if notes else class_dir.rglob("chapters")
    found = {}
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.glob("*/*.md"):
            match = SLICE_RE.fullmatch(path.parent.name)
            if match and path.name == f"{match.group(1)}{match.group(2)}.md":
                found[(match.group(1), int(match.group(2)))] = path
    return found


def layout_error(slice_path: Path, heading: str):
    lines = slice_path.read_text(encoding="utf-8").split("\n")
    if not lines:
        return "slice is empty"
    if lines[0] == REPAIR_MARKER:
        if len(lines) < 2 or lines[1] != heading:
            return "repair marker is not followed immediately by the chapter heading"
        return None
    if lines[0] == heading:
        return None
    return f"first line is {lines[0]!r}, not the chapter heading"


def check_class(class_dir: Path, explicit: bool) -> Result:
    claude_md = class_dir / "CLAUDE.md"
    if not claude_md.is_file():
        return Result("failed", failures=["no CLAUDE.md"])
    text = claude_md.read_text(encoding="utf-8")
    pattern, pattern_reason = chapter_pattern(text)
    existing = slice_files(class_dir)
    if pattern_reason == "declared none":
        if existing:
            return Result("failed", failures=["profile declares no chapters but slice files exist"])
        return Result("skipped", reason="profile declares no chapters")
    if pattern is None:
        return Result("failed", failures=[pattern_reason])

    notes_match = NOTES_RE.search(text)
    if not notes_match:
        return Result("failed", failures=["no notes file declared"])
    notes = class_dir / notes_match.group(1)
    if not notes.is_file():
        return Result("failed", failures=[f"notes file missing: {notes}"])

    existing = slice_files(class_dir, notes)
    headings = {}
    for line in notes.read_text(encoding="utf-8").split("\n"):
        match = pattern.match(line)
        if match:
            try:
                headings.setdefault(int(match.group(1)), line)
            except (IndexError, ValueError):
                return Result("failed", failures=["chapter heading pattern captured a non-numeric number"])

    if not headings:
        if existing:
            return Result("failed", failures=["slice files exist but the notes file contains no chapter headings"])
        if explicit:
            return Result("failed", failures=["notes file contains no chapter headings to verify"])
        return Result("skipped", reason="notes file contains no chapter headings")

    failures, consumed, checked = [], set(), 0
    for number, heading in sorted(headings.items()):
        candidates = [(key, path) for key, path in existing.items() if key[1] == number]
        if not candidates:
            failures.append(f"chapter{number}: expected slice is missing")
            continue
        key, path = sorted(candidates)[0]
        consumed.add(key)
        checked += 1
        error = layout_error(path, heading)
        if error:
            failures.append(f"{path.relative_to(class_dir)}: {error}")

    for key, path in sorted(existing.items()):
        if key not in consumed:
            failures.append(f"{path.relative_to(class_dir)}: extra slice has no matching notes heading")

    if failures:
        return Result("failed", checked=checked, failures=failures)
    return Result("verified", checked=checked)


def main(argv):
    explicit = len(argv) > 1
    if explicit:
        dirs = [Path(argument) for argument in argv[1:]]
    else:
        edu = Path.home() / "edu"
        if not edu.is_dir():
            print("usage: verify_slices.py <class_dir> ...", file=sys.stderr)
            return 2
        dirs = sorted(path for path in edu.iterdir() if (path / "CLAUDE.md").is_file())

    verified = skipped = failed = total_checked = 0
    for directory in dirs:
        result = check_class(directory, explicit)
        total_checked += result.checked
        if result.status == "verified":
            verified += 1
            print(f"{directory.name:24} {result.checked:3} slices checked   VERIFIED")
        elif result.status == "skipped":
            skipped += 1
            print(f"{directory.name:24} skipped — {result.reason}")
        else:
            failed += 1
            print(f"{directory.name:24} FAILED")
            for failure in result.failures:
                print(f"    ! {failure}")

    print(f"\nslices checked : {total_checked}")
    print(f"classes verified: {verified}")
    print(f"classes skipped : {skipped}")
    print(f"classes failed  : {failed}")
    if failed:
        return 1
    if not total_checked:
        print("\nNo slices were verified.")
        return 0
    print("\nEvery verified slice starts at its own chapter heading.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
