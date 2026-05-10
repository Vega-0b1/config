---
name: extract
description: Extract quiz-relevant content from a weekly folder of PDFs/DOCX/EPUB files into a single markdown notes file saved to extracted/. Avoids re-reading source files every quiz session.
---

Scan all files in the specified weekly folder (e.g., `wk9/`) and extract all quiz-relevant content into a single markdown file saved to `extracted/`.

## Instructions

1. **Glob the target week folder** to list all files
2. **Read all files** — PDFs, DOCX, PPTX, EPUB — in parallel where possible. Weekly overviews and reading assignments may contain quiz focus clues (key topics, guiding questions), so include them. Skip only files that are clearly unrelated (e.g., syllabus, administrative forms).
   - **For DOCX files:** extract text using Python's zipfile + xml.etree.ElementTree (unzip the docx, parse `word/document.xml`, collect all `<w:t>` text nodes per paragraph). This gives exact verbatim text.
   - **For EPUB files:** extract text using Python's zipfile + xml.etree.ElementTree (EPUBs are ZIPs containing XHTML files). Unzip the epub, find all `.xhtml`/`.html` files inside (check `META-INF/container.xml` → `content.opf` for the spine order if needed), parse each with ElementTree stripping all tags, and concatenate the text in spine order. Strip navigation/TOC files (e.g., `toc.xhtml`, `nav.xhtml`). This gives full verbatim text in reading order.
3. **Write a single markdown file** to `extracted/<week>_notes.md` with all text extracted verbatim from the source files. Preserve structure (headings, lists, tables, code blocks) where possible. Do not summarize, filter, or omit anything — include everything.

4. **Goal:** After extraction, future quiz sessions only need the markdown file — no PDFs.

## Usage

```
/extract wk9
```
