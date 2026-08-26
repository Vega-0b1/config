#!/usr/bin/env python3
"""Turn `pdftotext -layout` output into paged markdown with reconstructed headings.

`pdftotext -layout` preserves the printed page furniture, which is not content:
every verso page repeats `156        CHAPTER 7. RACE CONDITION VULNERABILITY`
and every recto page repeats `7.3. EXPERIMENT SETUP                     159`.
In a 690-page book that is ~480 lines of duplicated noise.

It also gives no headings at all. The book's own numbering is the only signal,
and on a scanned book that signal is damaged: `7 .1` for `7.1`, `4.7. 1` for
`4.7.1`, `24.7. I` for `24.7.1`. A strict `^\\d+\\.\\d+` regex silently drops
those, losing real structure — worse than the noise, because you cannot see it.

The hard part is telling a heading from a table-of-contents entry, since both
read `7.1  The General Race Condition Problem`. Three signals separate them,
and a candidate must clear all three:
  1. TOC entries are right-aligned to a page number  -> trailing `\\s{2,}\\d+$`.
  2. TOC entries carry dot leaders                   -> `. . .` or `....`.
  3. TOC entries appear before their chapter opens   -> chapter-context check.
Running heads are stripped first, so they never reach heading detection at all;
their ALL-CAPS form is a fourth rejection rule kept as a backstop.

Usage:
    pdf_layout.py <raw.txt> <out.md>              # raw.txt from `pdftotext -layout`
    pdf_layout.py --report <raw.txt>              # print stats, write nothing
"""

import re
import sys

# ── OCR-tolerant number patterns ─────────────────────────────────────────────
# `\s*` around every dot absorbs the scanner's inserted spaces (`7 .1`, `4.7. 1`).
# `[0-9IlO]` absorbs the classic glyph confusions in a numeral position.
_D = r"[0-9IlO]"
SECTION_RE = re.compile(rf"^({_D}{{1,2}})\s*\.\s*({_D}{{1,2}})\s+(\S.*)$")
SUBSEC_RE = re.compile(rf"^({_D}{{1,2}})\s*\.\s*({_D}{{1,2}})\s*\.\s*({_D}{{1,2}})\s+(\S.*)$")
CHAPTER_RE = re.compile(r"^Chapter\s+(\d{1,2})\s*$")

# ── Running-head patterns ────────────────────────────────────────────────────
# Verso: page number, wide gutter, then `CHAPTER <n>.` in caps. The book's OCR
# mangles the word itself (`CHA PTER`, `CHAPTER/.`) and splits the folio across
# a space (`11 6` for 116), so match both loosely.
_FOLIO = r"\d{1,3}(?:\s\d{1,2})?"
VERSO_RE = re.compile(rf"^\s*{_FOLIO}\s{{2,}}.*CH\s?A\s?PTER\s*[0-9IVXL/]+\s*[.~]", re.I)
VERSO_TIGHT_RE = re.compile(rf"^\s*{_FOLIO}\s+CH\s?A\s?PTER\s*[0-9IVXL/]+\s*[.~]", re.I)
# Recto: section number, then an ALL-CAPS title, then a right-aligned page number.
RECTO_RE = re.compile(
    rf"^\s*{_D}{{1,2}}\s*\.\s*{_D}{{1,2}}\s*\.?\s+[A-Z][A-Z0-9 ,'’\-&/()~:.]{{4,}}\s{{2,}}\d{{1,3}}\s*$"
)

DOT_LEADER_RE = re.compile(r"\.\s*\.\s*\.")
PAGE_TAIL_RE = re.compile(r"\s{2,}\d{1,3}\s*$")

_NUM_FIX = str.maketrans({"I": "1", "l": "1", "O": "0"})


def _num(tok):
    """Read a numeral that OCR may have rendered with letter glyphs."""
    try:
        return int(tok.translate(_NUM_FIX))
    except ValueError:
        return None


def is_running_head(line, idx_in_page):
    """Running heads sit in the top or bottom band of the page, never mid-text."""
    if idx_in_page > 2:
        return False
    return bool(VERSO_RE.match(line) or VERSO_TIGHT_RE.match(line) or RECTO_RE.match(line))


def looks_like_toc(text, full_line):
    """A heading candidate that is really a contents entry."""
    if DOT_LEADER_RE.search(full_line):
        return True
    if PAGE_TAIL_RE.search(full_line):
        return True
    letters = [c for c in text if c.isalpha()]
    if len(letters) >= 6 and all(c.isupper() for c in letters):
        return True  # backstop: a running head that survived stripping
    return False


def clean_title(text):
    """Collapse the runs of spaces `-layout` uses for alignment."""
    return re.sub(r"\s{2,}", " ", text).strip().rstrip(". ").strip() or text.strip()


def extract_chapter_title(lines, i):
    """Read the display title printed under a `Chapter N` line.

    The title is one or two short Title-Case lines; the abstract paragraph that
    follows is long and reads as prose. Stop at the first line that is prose.
    """
    parts = []
    j = i + 1
    while j < len(lines) and len(parts) < 3:
        s = lines[j].strip()
        if not s:
            if parts:
                break
            j += 1
            continue
        if len(s) > 60 or s.endswith("."):
            break
        if not (s[0].isupper() or s[0] == "("):
            break
        parts.append(s)
        j += 1
    return " ".join(parts).strip(), j


def convert(raw):
    pages = raw.split("\f")
    out = []
    stats = {
        "pages": 0, "empty_pages": 0, "running_heads": 0,
        "chapters": 0, "sections": 0, "subsections": 0, "toc_rejected": 0,
    }
    current_chapter = None

    for pno, page in enumerate(pages, start=1):
        if pno == len(pages) and not page.strip():
            break  # trailing fragment after the final form feed
        stats["pages"] += 1
        out.append(f"## Page {pno}")
        out.append("")

        lines = page.split("\n")
        body = []
        seen = 0
        for line in lines:
            if not line.strip():
                body.append("")
                continue
            if is_running_head(line, seen):
                stats["running_heads"] += 1
                seen += 1
                continue
            seen += 1
            body.append(line)

        while body and not body[-1].strip():
            body.pop()
        while body and not body[0].strip():
            body.pop(0)
        if not body:
            stats["empty_pages"] += 1
            continue

        i = 0
        while i < len(body):
            line = body[i]
            s = line.strip()
            if not s:
                out.append("")
                i += 1
                continue

            m = CHAPTER_RE.match(s)
            if m:
                n = int(m.group(1))
                title, nxt = extract_chapter_title(body, i)
                current_chapter = n
                stats["chapters"] += 1
                out.append(f"# Chapter {n}: {title}" if title else f"# Chapter {n}")
                out.append("")
                i = nxt
                continue

            # Subsection before section: `7.4.1` also matches the section shape.
            m = SUBSEC_RE.match(s)
            if m:
                c, sec, sub = _num(m.group(1)), _num(m.group(2)), _num(m.group(3))
                text = clean_title(m.group(4))
                if (c is not None and c == current_chapter and sec and sub
                        and not looks_like_toc(text, line)):
                    stats["subsections"] += 1
                    out.append(f"### {c}.{sec}.{sub} {text}")
                    i += 1
                    continue
                if c == current_chapter:
                    stats["toc_rejected"] += 1

            m = SECTION_RE.match(s)
            if m:
                c, sec = _num(m.group(1)), _num(m.group(2))
                text = clean_title(m.group(3))
                if (c is not None and c == current_chapter and sec
                        and not looks_like_toc(text, line)):
                    stats["sections"] += 1
                    out.append(f"## {c}.{sec} {text}")
                    i += 1
                    continue
                if c == current_chapter:
                    stats["toc_rejected"] += 1

            out.append(line)
            i += 1

        out.append("")

    text = "\n".join(out)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text, stats


def main():
    args = sys.argv[1:]
    report_only = False
    if args and args[0] == "--report":
        report_only = True
        args = args[1:]
    if not args or (not report_only and len(args) < 2):
        sys.exit(__doc__)

    with open(args[0], "r", errors="replace") as f:
        raw = f.read()

    text, stats = convert(raw)

    for k in ("pages", "empty_pages", "running_heads", "chapters",
              "sections", "subsections", "toc_rejected"):
        print(f"{k:<16}: {stats[k]}")

    if not report_only:
        with open(args[1], "w") as f:
            f.write(text if text.endswith("\n") else text + "\n")
        print(f"\nwrote {args[1]}")


if __name__ == "__main__":
    main()
