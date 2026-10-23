#!/usr/bin/env python3
"""Put back the lines a re-OCR dropped, using the scanned PDF's own text layer.

RapidOCR's re-OCR (ocr_pdf.py) is cleaner than a scanner's text layer but not
complete: on the Du textbook it dropped about 1.7% of the text, usually one
whole line on 219 of 690 pages, most likely where the detector boxed two lines
as one. The text layer is damaged but complete, so it can fill the holes.

For each page, every text-layer line of 12+ alphanumeric characters is checked
against the OCR page (exact substring, else >= 75% of its characters in
matching runs of 4+). A line not found is inserted after the OCR line that
matched the previous text-layer line, so it lands where the page printed it.
On the Du textbook this inserted 531 lines and cut the missing text from 1.69%
to 0.26%; the remainder is diagrams, hex dumps and code read in another order.

Usage:
    merge_layer.py <raw_layer.txt> <raw_ocr.txt> <raw_merged.txt>
"""
import difflib
import re
import sys
from collections.abc import Sequence
from pathlib import Path

MIN_CHARS = 12


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def covered(line_norm: str, page_norm: str) -> bool:
    """True if the line's characters appear in the OCR page, allowing OCR noise."""
    if line_norm in page_norm:
        return True
    sm = difflib.SequenceMatcher(None, line_norm, page_norm, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks() if b.size >= 4)
    return matched >= 0.75 * len(line_norm)


def merge_page(layer: str, ocr: str) -> tuple[str, int]:
    ocr_lines = ocr.split("\n")
    ocr_norms = [norm(l) for l in ocr_lines]
    page_norm = "".join(ocr_norms)
    out = list(ocr_lines)
    inserted = 0
    anchor = -1  # index in `out` of the OCR line matching the last covered layer line
    for line in layer.split("\n"):
        n = norm(line)
        if len(n) < MIN_CHARS:
            continue
        if covered(n, page_norm):
            best, best_ratio = anchor, 0.0
            for i in range(max(anchor, 0), len(out)):
                r = difflib.SequenceMatcher(None, n, norm(out[i]), autojunk=False).ratio()
                if r > best_ratio:
                    best, best_ratio = i, r
            if best_ratio >= 0.5:
                anchor = best
        else:
            out.insert(anchor + 1, line)
            anchor += 1
            inserted += 1
    return "\n".join(out), inserted


def main() -> None:
    layer = Path(sys.argv[1]).read_text().split("\f")
    ocr = Path(sys.argv[2]).read_text().split("\f")
    pages: list[str] = []
    total = 0
    for a, b in zip(layer, ocr):
        merged, n = merge_page(a, b)
        pages.append(merged)
        total += n
    Path(sys.argv[3]).write_text("\f".join(pages))
    print(f"inserted {total} text-layer lines missing from the OCR")


if __name__ == "__main__":
    main()
