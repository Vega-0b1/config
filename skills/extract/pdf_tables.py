#!/usr/bin/env python3
"""Turn a born-digital PDF's ruled tables into Markdown tables, and flag the ones
a script cannot be trusted with.

`pdftotext -layout` keeps a table as space-aligned columns. `pdfplumber` can
read the same table as rows and cells, which become a Markdown table at no
token cost. It is reliable on plain text and plain numbers, and wrong in two
ways that matter:

  * superscripts and subscripts are flattened into the baseline, so `10^7`
    becomes `107` and `A_O` becomes `AO` — wrong values with no visible error;
  * math (fractions, integrals, stacked limits) comes out scrambled.

So every cell is checked: a character noticeably smaller than the largest one
in its cell is a sub/superscript, and a math glyph is math. A table with any
flagged cell is marked RETYPE, and the agent retypes only that table from the
page image. On the Irwin circuits book 12 of 29 tables passed clean.

Two passes around pdf_layout.py:

    pdf_tables.py mark <in.pdf> <raw.txt> <raw_marked.txt> <tables.json>
        For each table, remove the raw lines whose words all belong to that
        table and put `[[TABLE <page>.<k>]]` where they were. A line holding
        any word from outside the table is kept, so no prose is lost; if no
        line could be matched, the marker goes at the end of the page and the
        aligned text stays.

    pdf_tables.py fill <notes.md> <tables.json> <out.md>
        Replace each marker with its Markdown table. A RETYPE table is preceded
        by `<!-- RETYPE table <page>.<k>: <reasons> -->`.
"""

import json
import re
import statistics
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import NotRequired, TypedDict

import pdfplumber


class TableInfo(TypedDict):
    page: int
    k: int
    markdown: str
    words: list[str]
    retype: list[str]
    placed: NotRequired[str]


MATH = set("∫∑∏√∞∂≈∓∙λΔ") | {"_"}
MIN_FILLED = 0.4
MIN_ROWS = 3
MARKER_RE = re.compile(r"^\s*\[\[TABLE (\d+)\.(\d+)\]\]\s*$")
_CLEAN = str.maketrans({"­": "-", "​": None, " ": " ", "﻿": None})


def clean(text: str | None) -> str:
    return re.sub(r"\s+", " ", (text or "").translate(_CLEAN)).strip()


def words(text: str) -> list[str]:
    return clean(text).split()


def filled_ratio(rows: Sequence[Sequence[str | None]]) -> float:
    cells = [c for r in rows for c in r]
    return sum(1 for c in cells if clean(c)) / max(len(cells), 1)


def is_data_table(rows: Sequence[Sequence[str | None]]) -> bool:
    """Reject ruled boxes that are not tables: chapter banners, one-cell callout
    boxes, figure labels, and graph gridlines. A table has at least 2 columns,
    3 rows, 2 rows with two or more filled cells, and is mostly filled."""
    if len(rows) < MIN_ROWS or max(len(r) for r in rows) < 2:
        return False
    multi = sum(1 for r in rows if sum(1 for c in r if clean(c)) >= 2)
    return multi >= 2 and filled_ratio(rows) >= MIN_FILLED


def cell_flags(chars: Sequence[Mapping[str, object]]) -> list[str]:
    visible = [c for c in chars if str(c["text"]).strip()]
    if not visible:
        return []
    reasons: list[str] = []
    ref = max(float(str(c["size"])) for c in visible)
    if any(float(str(c["size"])) < 0.8 * ref for c in visible):
        reasons.append("sub/superscript")
    if any(str(c["text"]) in MATH for c in visible):
        reasons.append("math symbol")
    return reasons


def to_markdown(rows: Sequence[Sequence[str | None]]) -> str:
    cells = [[clean(c).replace("|", "\\|") for c in r] for r in rows]
    width = max(len(r) for r in cells)
    cells = [r + [""] * (width - len(r)) for r in cells]
    lines = ["| " + " | ".join(cells[0]) + " |", "|" + "---|" * width]
    lines += ["| " + " | ".join(r) + " |" for r in cells[1:]]
    return "\n".join(lines)


def read_tables(pdf_path: str) -> list[TableInfo]:
    found: list[TableInfo] = []
    with pdfplumber.open(pdf_path) as pdf:
        for pno, page in enumerate(pdf.pages, start=1):
            k = 0
            for table in page.find_tables():
                rows = table.extract()
                if not rows or not rows[0] or not is_data_table(rows):
                    continue
                k += 1
                reasons: set[str] = set()
                for row in table.rows:
                    for bbox in row.cells:
                        if bbox is None:
                            continue
                        x0, top, x1, bottom = bbox
                        chars = [c for c in page.chars
                                 if x0 <= (c["x0"] + c["x1"]) / 2 <= x1
                                 and top <= (c["top"] + c["bottom"]) / 2 <= bottom]
                        reasons.update(cell_flags(chars))
                found.append({
                    "page": pno, "k": k,
                    "markdown": to_markdown(rows),
                    "words": [w for r in rows for c in r for w in words(c or "")],
                    "retype": sorted(reasons),
                })
    return found


def mark(pdf_path: str, raw_path: str, out_raw: str, out_json: str) -> None:
    tables = read_tables(pdf_path)
    pages = Path(raw_path).read_text().split("\f")
    by_page: dict[int, list[TableInfo]] = {}
    for t in tables:
        by_page.setdefault(t["page"], []).append(t)
    replaced = appended = 0
    for pno, page_tables in by_page.items():
        lines = pages[pno - 1].split("\n")
        for t in page_tables:
            pool = Counter(t["words"])
            hits = [i for i, line in enumerate(lines)
                    if words(line) and not (Counter(words(line)) - pool)]
            marker = f"[[TABLE {t['page']}.{t['k']}]]"
            if hits:
                first = hits[0]
                lines = [marker if i == first else line
                         for i, line in enumerate(lines) if i == first or i not in hits]
                t["placed"] = "replaced"
                replaced += 1
            else:
                # Keep the page's trailing newline after the marker, or the marker
                # fuses with whatever follows the page break.
                at = len(lines) - 1 if lines and lines[-1] == "" else len(lines)
                lines.insert(at, marker)
                t["placed"] = "appended"
                appended += 1
        pages[pno - 1] = "\n".join(lines)
    Path(out_raw).write_text("\f".join(pages))
    Path(out_json).write_text(json.dumps(tables, ensure_ascii=False, indent=1))
    retype = sum(1 for t in tables if t["retype"])
    print(f"tables: {len(tables)} ({replaced} replaced aligned text, {appended} appended), "
          f"auto-ok: {len(tables) - retype}, RETYPE: {retype}")


def fill(notes_path: str, json_path: str, out_path: str) -> None:
    loaded: list[TableInfo] = json.loads(Path(json_path).read_text())
    tables = {(t["page"], t["k"]): t for t in loaded}
    out: list[str] = []
    filled = 0
    for line in Path(notes_path).read_text().split("\n"):
        m = MARKER_RE.match(line)
        if not m:
            out.append(line)
            continue
        t = tables[(int(m.group(1)), int(m.group(2)))]
        if t["retype"]:
            out.append(f"<!-- RETYPE table {m.group(1)}.{m.group(2)}: {', '.join(t['retype'])} -->")
        out.append(t["markdown"])
        filled += 1
    Path(out_path).write_text("\n".join(out))
    print(f"filled {filled} of {len(tables)} table markers")


def main() -> None:
    if len(sys.argv) == 6 and sys.argv[1] == "mark":
        mark(*sys.argv[2:6])
    elif len(sys.argv) == 5 and sys.argv[1] == "fill":
        fill(*sys.argv[2:5])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
