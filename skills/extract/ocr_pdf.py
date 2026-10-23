#!/usr/bin/env python3
"""Re-OCR a scanned PDF into `pdftotext -layout`-shaped text, for pdf_layout.py.

A scanned PDF's own text layer is whatever OCR the scanner ran, and on the Du
textbook it splits words apart (`Ubun t u 12 . 0 4`, `/et c / pas swd`) and
misreads glyphs (`UJD O` for `UID 0`). Re-running a modern OCR model on the
page images fixes most of that, but the result must still look like
`pdftotext -layout` output, or pdf_layout.py cannot find running heads and
headings in it:

  * pages are separated by form feeds (`\f`);
  * each text box is placed at the column its x-position implies, so the wide
    gutter before a running head's folio survives (`7.3. TITLE      159`);
  * a section number fused to its title (`8.6.1Selecting`) gets its space back.

Built to run on the NAS through the `offload` skill (CPU-heavy: a 690-page book
took about an hour on the NAS). Needs `pypdfium2` and `rapidocr_onnxruntime`
plus the English recognition model `en_PP-OCRv3_rec_infer.onnx`; the default
model is Chinese-trained and drops the spaces between English words.

Usage:
    ocr_pdf.py <in.pdf> <out_dir> <rec_model.onnx> [--workers 6] [--dpi 300]

Each worker holds ~0.6-0.9 GB. Size --workers from the NAS's free memory
(offload skill R6c); 14 workers exhausted it and the kernel killed workers.
A re-run skips pages already in `<out_dir>/pages/`, so a crashed run resumes.
A dead worker raises BrokenProcessPool instead of hanging the run forever.

Writes `<out_dir>/pages/<NNNN>.txt` as each page finishes, then
`<out_dir>/raw.txt` (all pages joined by `\f`) once every page is done.
"""

import argparse
import re
import statistics
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pypdfium2
from rapidocr_onnxruntime import RapidOCR

Box = tuple[float, float, float, float, str]  # x0, x1, y_center, height, text

# Digit look-alikes match pdf_layout.py: OCR reads `1.6.` as `I.6.` and fuses it to the title.
FUSED_NUMBER_RE = re.compile(r"^(\s*[0-9IlO]{1,2}(?:\s*\.\s*[0-9IlO]{1,2}){1,2}\.?)(?=[A-Za-z])")

_doc: "pypdfium2.PdfDocument | None" = None
_eng: "RapidOCR | None" = None
_scale = 300 / 72


def _init(pdf_path: str, model: str, dpi: int) -> None:
    global _doc, _eng, _scale
    _doc = pypdfium2.PdfDocument(pdf_path)
    _eng = RapidOCR(rec_model_path=model, intra_op_num_threads=1)
    _scale = dpi / 72


def group_lines(boxes: Sequence[Box]) -> list[list[Box]]:
    lines: list[list[Box]] = []
    for b in sorted(boxes, key=lambda b: b[2]):
        if lines and abs(b[2] - lines[-1][-1][2]) < 0.5 * b[3]:
            lines[-1].append(b)
        else:
            lines.append([b])
    return [sorted(line) for line in lines]


def layout_line(line: Sequence[Box], char_w: float) -> str:
    out = ""
    for x0, _x1, _y, _h, text in line:
        col = round(x0 / char_w)
        if out and col <= len(out):
            out += " "
        else:
            out = out.ljust(col)
        out += text
    return FUSED_NUMBER_RE.sub(r"\1 ", out).rstrip()


def ocr_page(index: int) -> tuple[int, str]:
    if _doc is None or _eng is None:
        raise RuntimeError("worker not initialized")
    image = _doc[index].render(scale=_scale, grayscale=True).to_pil()
    result, _ = _eng(image)
    boxes: list[Box] = []
    widths: list[float] = []
    for pts, text, _score in result or []:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        boxes.append((min(xs), max(xs), sum(ys) / 4, max(ys) - min(ys), text))
        if len(text) >= 4:
            widths.append((max(xs) - min(xs)) / len(text))
    if not boxes:
        return index, ""
    char_w = statistics.median(widths) if widths else 10.0
    return index, "\n".join(layout_line(line, char_w) for line in group_lines(boxes))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("out_dir")
    ap.add_argument("model")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--dpi", type=int, default=300)
    args = ap.parse_args()

    n = len(pypdfium2.PdfDocument(args.pdf))
    pages_dir = Path(args.out_dir) / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    todo = [i for i in range(n) if not (pages_dir / f"{i + 1:04d}.txt").exists()]
    print(f"{n - len(todo)}/{n} pages already done, {len(todo)} to OCR", flush=True)
    start = time.time()
    with ProcessPoolExecutor(args.workers, initializer=_init,
                             initargs=(args.pdf, args.model, args.dpi)) as pool:
        futures = [pool.submit(ocr_page, i) for i in todo]
        for done, fut in enumerate(as_completed(futures), 1):
            index, text = fut.result()
            (pages_dir / f"{index + 1:04d}.txt").write_text(text + "\n")
            if done % 20 == 0 or done == len(todo):
                rate = done / (time.time() - start)
                print(f"{n - len(todo) + done}/{n} pages, ~{(len(todo) - done) / rate / 60:.1f} min left", flush=True)
    raw = "\f".join((pages_dir / f"{i:04d}.txt").read_text() for i in range(1, n + 1))
    (Path(args.out_dir) / "raw.txt").write_text(raw + "\f")
    print("done", flush=True)


if __name__ == "__main__":
    main()
