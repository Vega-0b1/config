#!/usr/bin/env python3
"""Verify that every `Source quote:` in a questions file really appears in its source.

Mechanical check only. Answers one question per quote: is this string actually in
the source file? It cannot tell you whether the Teach field is faithful to the
quote — that is R18b, and it needs a reader.

Usage:
    verify_quotes.py [--legacy] <questions_file> [source_file ...]

With no source files given, the sources are read from the questions file's
`source:` frontmatter and resolved relative to the questions file's directory.
A class run lists several comma-separated sources (R24h1); all are searched and a
quote need only match one.

Strict mode requires every entry to carry a valid Source quote. `--legacy` permits
missing Source quote fields but still reports them; malformed or empty fields
remain errors, and both modes fail when zero quotes were checked.

Exit status: 0 = every checked quote found, 1 = verification/schema failure,
2 = usage or source-file error.
"""

import re
import sys
import unicodedata
from pathlib import Path


VALID_QUESTION_HEADER_RE = re.compile(r"^#### Q\d+[ \t]*$", re.M)
QUESTION_LIKE_HEADER_RE = re.compile(r"^#{1,6}[ \t]+Q\d+\b.*$", re.M)
SOURCE_QUOTE_RE = re.compile(
    r"^Source quote:[ \t]*(.*?)(?=^(?:Concept|Origin generated|Origin|Teach|Teach_EN|"
    r"Question|Question_EN|Tests|Answer key|Elaboration|Audit):|\Z)",
    flags=re.M | re.S,
)
SOURCE_QUOTE_LIKE_RE = re.compile(
    r"^Source[ \t]+quote[ \t]*:", flags=re.M | re.I
)


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


def malformed_question_headers(questions_text):
    return [
        (questions_text.count("\n", 0, match.start()) + 1, match.group())
        for match in QUESTION_LIKE_HEADER_RE.finditer(questions_text)
        if not VALID_QUESTION_HEADER_RE.fullmatch(match.group())
    ]


def parse_entries(questions_text):
    """Yield (unit, qid, body) for each correctly headed question entry."""
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
            yield unit, pending, chunk
            pending = None


def extract_quotes(body):
    """Return (state, fragments) for one entry's Source quote field.

    R12e2 joins fragments of one interrupted sentence with ` [...] `; R13g1
    separates independent sentences with a blank line. Both become separate
    strings, because each must be independently findable in the source.
    """
    m = SOURCE_QUOTE_RE.search(body)
    if not m:
        if SOURCE_QUOTE_LIKE_RE.search(body):
            return "malformed", []
        return "missing", []
    block = m.group(1)
    fragments = []
    for piece in re.split(r"\n\s*\n", block):
        for frag in piece.split("[...]"):
            frag = frag.strip().strip('"').strip()
            if normalize(frag):
                fragments.append(frag)
    if not fragments:
        return "empty", []
    return "ok", fragments


def parse_args(argv):
    args = argv[1:]
    if args.count("--legacy") > 1:
        return None, None, "--legacy may be given only once"
    legacy = "--legacy" in args
    args = [arg for arg in args if arg != "--legacy"]
    unknown = [arg for arg in args if arg.startswith("--")]
    if unknown:
        return None, None, f"unknown option: {unknown[0]}"
    if not args:
        return None, None, "missing questions file"
    return legacy, args, None


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
    legacy, args, arg_error = parse_args(argv)
    if arg_error:
        print(f"error: {arg_error}", file=sys.stderr)
        print(__doc__.strip(), file=sys.stderr)
        return 2

    qpath = Path(args[0])
    if not qpath.is_file():
        print(f"error: no such questions file: {qpath}", file=sys.stderr)
        return 2

    sources = resolve_sources(qpath, args[1:])
    missing_sources = [s for s in sources if not s.is_file()]
    sources = [s for s in sources if s.is_file()]
    if not sources:
        print(f"error: no readable source file for {qpath}", file=sys.stderr)
        for s in missing_sources:
            print(f"       tried: {s}", file=sys.stderr)
        return 2

    questions_text = qpath.read_text(encoding="utf-8")
    haystacks = [(s, normalize(s.read_text(encoding="utf-8"))) for s in sources]

    checked = failures = entries = no_quote = 0
    problems = []
    schema_problems = []

    for line_number, header in malformed_question_headers(questions_text):
        schema_problems.append(
            f"line {line_number}: malformed question heading: {header}"
        )

    for unit, qid, body in parse_entries(questions_text):
        entries += 1
        quote_state, quotes = extract_quotes(body)
        if quote_state == "missing" and legacy:
            no_quote += 1
            continue
        if quote_state != "ok":
            descriptions = {
                "missing": "missing Source quote field",
                "malformed": "malformed Source quote field; use exact `Source quote:`",
                "empty": "empty Source quote field",
            }
            schema_problems.append(f"[{unit}] {qid}: {descriptions[quote_state]}")
            continue
        for quote in quotes:
            checked += 1
            nq = normalize(quote)
            if not any(nq in hay for _, hay in haystacks):
                failures += 1
                problems.append((unit, qid, quote))

    if entries == 0:
        schema_problems.append("no valid question entries were parsed")
    if checked == 0:
        schema_problems.append("zero Source quote fragments were checked")

    print(f"questions file : {qpath}")
    for s in sources:
        print(f"source         : {s}")
    print(f"mode           : {'legacy' if legacy else 'strict'}")
    print(f"entries        : {entries}")
    print(f"quotes checked : {checked}")
    print(f"NOT FOUND      : {failures}")
    print(f"schema errors  : {len(schema_problems)}")
    if no_quote:
        print(f"legacy skipped : {no_quote} missing Source quote field(s)")

    if schema_problems:
        print("\nschema/verification errors:")
        for problem in schema_problems:
            print(f"  {problem}")

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

    if schema_problems or problems:
        return 1

    print("\nAll quotes verified against the source.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
