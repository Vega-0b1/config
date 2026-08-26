#!/usr/bin/env python3
"""Verify that every `Source quote:` in a questions file really appears in its source.

Mechanical check only. Answers one question per quote: is this string actually in
the source file? It cannot tell you whether the Teach field is faithful to the
quote — that is R18b, and it needs a reader.

Usage:
    verify_quotes.py <questions_file> [source_file ...]

With no source files given, the sources are read from the questions file's
`source:` frontmatter and resolved relative to the questions file's directory.
A class run lists several comma-separated sources (R24h1); all are searched and a
quote need only match one.

Exit status: 0 = every quote found, 1 = at least one missing, 2 = usage error.
"""

import re
import sys
import unicodedata
from pathlib import Path


def normalize(text):
    """Collapse the differences that are formatting, not content.

    Markdown emphasis, smart quotes, dash variants, and the hard line breaks a
    PDF extraction leaves mid-sentence are all noise here. Case is folded so a
    quote that opens a sentence still matches mid-sentence usage.
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("**", "").replace("*", "").replace("`", "")
    text = re.sub(r"[‘’‛]", "'", text)
    text = re.sub(r"[“”]", '"', text)
    text = re.sub(r"[‐-―−]", "-", text)
    text = text.replace("…", "...")
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()


def parse_entries(questions_text):
    """Yield (unit, qid, [quote, ...]) for each entry carrying a Source quote."""
    unit = "(no unit heading)"
    parts = re.split(r"^(## Unit .*|#### Q\d+)\s*$", questions_text, flags=re.M)
    pending = None
    for chunk in parts:
        if chunk is None:
            continue
        header = chunk.strip()
        if header.startswith("## Unit "):
            unit = header[3:]
            pending = None
        elif re.fullmatch(r"#### Q\d+", header):
            pending = header[5:]
        elif pending:
            yield unit, pending, extract_quotes(chunk)
            pending = None


def extract_quotes(body):
    """Pull the Source quote block, split on the ` [...] ` and blank-line joins.

    R12e2 joins fragments of one interrupted sentence with ` [...] `; R13g1
    separates independent sentences with a blank line. Both become separate
    strings, because each must be independently findable in the source.
    """
    m = re.search(
        r"^Source quote:[ \t]*(.*?)(?=^(?:Teach|Teach_EN|Question|Tests|Answer key|Concept|Audit):)",
        body,
        flags=re.M | re.S,
    )
    if not m:
        return []
    block = m.group(1)
    fragments = []
    for piece in re.split(r"\n\s*\n", block):
        for frag in piece.split("[...]"):
            frag = frag.strip().strip('"').strip()
            if len(normalize(frag)) >= 15:
                fragments.append(frag)
    return fragments


def resolve_sources(qpath, argv_sources):
    if argv_sources:
        return [Path(p) for p in argv_sources]
    text = qpath.read_text(encoding="utf-8")
    m = re.search(r"^source:[ \t]*(.+)$", text, flags=re.M)
    if not m:
        return []
    names = [n.strip() for n in m.group(1).split(",") if n.strip()]
    resolved = []
    for name in names:
        cand = qpath.parent / name
        # A class run records paths relative to the class root, not to the file.
        if not cand.exists():
            for up in qpath.parents:
                alt = up / name
                if alt.exists():
                    cand = alt
                    break
        # A select run's source is a chapter slice in a different subtree.
        # Search under extracted/textbook/chapters/ from the class root.
        if not cand.exists():
            for up in qpath.parents:
                chapters_dir = up / "extracted" / "textbook" / "chapters"
                if chapters_dir.is_dir():
                    matches = list(chapters_dir.rglob(name))
                    if matches:
                        cand = matches[0]
                    break
        resolved.append(cand)
    return resolved


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    qpath = Path(argv[1])
    if not qpath.is_file():
        print(f"error: no such questions file: {qpath}", file=sys.stderr)
        return 2

    sources = resolve_sources(qpath, argv[2:])
    missing_sources = [s for s in sources if not s.is_file()]
    sources = [s for s in sources if s.is_file()]
    if not sources:
        print(f"error: no readable source file for {qpath}", file=sys.stderr)
        for s in missing_sources:
            print(f"       tried: {s}", file=sys.stderr)
        return 2

    haystacks = [(s, normalize(s.read_text(encoding="utf-8"))) for s in sources]

    checked = failures = entries = no_quote = 0
    problems = []

    for unit, qid, quotes in parse_entries(qpath.read_text(encoding="utf-8")):
        entries += 1
        if not quotes:
            no_quote += 1
            continue
        for quote in quotes:
            checked += 1
            nq = normalize(quote)
            if not any(nq in hay for _, hay in haystacks):
                failures += 1
                problems.append((unit, qid, quote))

    print(f"questions file : {qpath}")
    for s in sources:
        print(f"source         : {s}")
    print(f"entries        : {entries}")
    print(f"quotes checked : {checked}")
    print(f"NOT FOUND      : {failures}")
    if no_quote:
        print(f"no Source quote: {no_quote}  (legacy entries — skipped per R18b3)")

    if problems:
        print("\nquotes that do not appear in the source:")
        for unit, qid, quote in problems:
            snippet = quote if len(quote) <= 100 else quote[:100] + "..."
            print(f"  [{unit}] {qid}: {snippet}")
        print(
            "\nEach of these is either a fabricated quote, a paraphrase recorded "
            "where a verbatim sentence belongs (R12e1), or an interrupted sentence "
            "stitched together instead of joined with [...] (R12e2)."
        )
        return 1

    if checked == 0:
        print("\nNo Source quote fields found. Nothing was verified.")
        return 0

    print("\nAll quotes verified against the source.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
