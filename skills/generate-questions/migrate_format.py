#!/usr/bin/env python3
"""Migrate a /generate-questions file from format 1 to format 2.

Format 2 differs from format 1 in exactly three ways:
  1. Frontmatter carries `format: 2`.
  2. `#### Q<n>` uses the ABSOLUTE position in the file, not a per-unit label.
  3. Continuation lines of multi-line fields are indented two spaces.
     Blank lines stay blank -- they are semantic inside Source quote (R13g1).

Nothing else is touched. No field VALUE is altered; indentation is presentation
and is stripped on read.
"""
import re, sys, pathlib

KEYS = ["Concept", "Origin generated", "Origin fingerprint", "Origin",
        "Source quote", "Teach_EN", "Teach", "Legend", "Question_EN", "Question",
        "Tests", "Answer key", "Elaboration", "Audit"]
KEY_RE = re.compile(r"^(%s):" % "|".join(KEYS))
QHEAD_RE = re.compile(r"^#### Q\d+\s*$")


def migrate(text):
    lines = text.split("\n")
    out = []
    i = 0
    # Frontmatter: stamp format: 2 before the closing fence.
    if lines and lines[0] == "---":
        out.append(lines[0]); i = 1
        while i < len(lines) and lines[i] != "---":
            if not lines[i].startswith("format:"):
                out.append(lines[i])
            i += 1
        out.append("format: 2")
        out.append("---")
        i += 1
    pos = 0
    field = None
    for line in lines[i:]:
        if QHEAD_RE.match(line):
            pos += 1
            out.append("#### Q%d" % pos)
            field = None
        elif line.startswith("## Unit "):
            out.append(line)
            field = None
        elif KEY_RE.match(line):
            out.append(line)
            field = KEY_RE.match(line).group(1)
        elif field is not None and line.strip():
            out.append("  " + line)
        else:
            out.append(line)
    return "\n".join(out), pos


if __name__ == "__main__":
    for p in sys.argv[1:]:
        src = pathlib.Path(p)
        new, n = migrate(src.read_text(encoding="utf-8"))
        sys.stdout.write("%-70s %d entries\n" % (src.name, n))
        print(new, end="")
