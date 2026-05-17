---
name: extract
description: Extract all content from PDFs/DOCX/EPUB/PPTX files in the current directory (or a specified subfolder/file) into a single markdown notes file saved to extracted/. After extracting, moves the source files into source/.
---

Scan files and extract all content into a single markdown file saved to `extracted/`.

## Instructions

### 1. Resolve the target and output filename

| Argument | Target | Output file |
|---|---|---|
| `wk9` | all files inside `wk9/` subfolder | `extracted/wk9_notes.md` |
| `textbook.epub` | just that file | `extracted/<sanitized>_notes.md` |
| *(none)* | all loose files in the current directory | `extracted/<current-folder-name>_notes.md` |

**Output filename sanitization (single file arg):** Strip the extension, drop everything after the first ` - ` or `(`, lowercase, replace spaces/punctuation with underscores, truncate to ~30 chars. Example: `"James Kurose, Keith Ross - Computer Networking_ A Top-Down Approach (7th Edition)...epub"` → `extracted/james_kurose_computer_networking_notes.md`.

- Run from the class root (e.g. `~/edu/cybersecurity/`). If cwd looks like `source/` or a subfolder, warn the user.
- Create `extracted/` if it doesn't exist.
- If the output file already exists, stop and warn the user before overwriting.
- If no extractable content files are found, stop and tell the user.

### 2. Read all files in parallel

Supported formats: PDF, DOCX, PPTX, EPUB. Skip unrelated files (`.gitignore`, lock files, code files, existing markdown in `extracted/`).

- **PDF:** read directly with the Read tool.
- **DOCX:** extract with Python's `zipfile` + `xml.etree.ElementTree` — unzip, parse `word/document.xml`, collect all `<w:t>` text nodes per paragraph.
- **EPUB:** extract with Python's `zipfile` + `xml.etree.ElementTree` — unzip, find `.xhtml`/`.html` files in spine order (via `META-INF/container.xml` → `content.opf`), strip tags, concatenate. Skip nav/TOC files.
- **PPTX:** extract with Python's `zipfile` + `xml.etree.ElementTree` — unzip, find `ppt/slides/slide*.xml`, collect all `<a:t>` text nodes in order.

### 3. Write the output file

Write to `extracted/<name>_notes.md` with all text verbatim. Preserve structure (headings, lists, tables, code blocks) where possible. Do not summarize, filter, or omit anything.

### 4. Move source files into source/

After a successful write:
- Create `source/` if it doesn't exist.
- Subfolder arg → move the whole subfolder: `source/wk9/`
- Single file or loose files → move each file individually into `source/`
- Do not move `extracted/`, `source/`, `code/`, or the README.

### 5. Confirm

Print what was written to `extracted/` and what was moved to `source/`.

## Usage

```
/extract wk9
/extract textbook.epub
/extract
```
