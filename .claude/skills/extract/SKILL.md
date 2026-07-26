---
name: extract
description: Extract all content from PDFs/DOCX/EPUB/PPTX files in the current directory (or a specified subfolder/file) into a single markdown notes file saved to extracted/. For EPUBs, also extracts embedded images to extracted/images/ and links them inline so /generate_questions can read figures. After extracting, moves the source files into source/.
---

Scan files and extract all content into a single markdown file saved to `extracted/`.

## Rules

// Target and output resolution
R1.  IF the argument names a subfolder (e.g. `wk9`) THEN target = all files inside that subfolder; output = `extracted/<subfolder>_notes.md`.
R2.  IF the argument names a single file (e.g. `textbook.epub`) THEN target = that file; output = `extracted/<sanitized>_notes.md`, sanitized per the Sanitization block below.
R3.  IF no argument is given THEN target = all loose files in the current directory; output = `extracted/<current-folder-name>_notes.md`.
R4.  IF cwd looks like `source/` or a subfolder rather than a class root THEN warn the user before proceeding.
R5.  IF `extracted/` does not exist THEN create it.
R6.  IF the output file already exists THEN stop and warn the user before overwriting. STOP until user responds.
     // Commentary: a previous extraction may have been intentional; the user may have added manual notes to it.
R7.  IF no extractable content files are found THEN stop and tell the user.

// Reading
R8.  Supported formats: PDF, DOCX, PPTX, EPUB.
R9.  IF a file is unrelated (`.gitignore`, lock files, code files, existing markdown in `extracted/`) THEN skip it.
R10. IF multiple files are targeted THEN read them in parallel.
     // Commentary: matters especially for large courses with many weekly slide decks.
R11. IF the file is a PDF THEN read it directly with the Read tool.
R11a. IF the file is a PDF THEN do NOT extract its embedded images; note in the R25 report that PDF figures were not extracted.
     // Commentary: PDF image streams carry no markup tying a figure to its surrounding section, so position-accurate inline linking is not reliable. Image extraction is EPUB-only (R13a–R13e).
R12. IF the file is a DOCX THEN extract with Python `zipfile` + `xml.etree.ElementTree`: unzip, parse `word/document.xml`, collect all `<w:t>` text nodes per paragraph.
R13. IF the file is an EPUB THEN extract with Python `zipfile` + `xml.etree.ElementTree`: unzip, find `.xhtml`/`.html` files in spine order (via `META-INF/container.xml` → `content.opf`), strip tags (except `<img>`, per R13c), concatenate. Skip nav/TOC files.

// Image handling (EPUB only)
R13a. IF the file is an EPUB THEN copy every embedded image (`.jpg`, `.jpeg`, `.png`, `.gif`, `.svg`) out of the EPUB into `extracted/images/`, preserving each image's original basename.
R13b. IF the EPUB contains at least one image AND `extracted/images/` does not exist THEN create it.
R13c. IF an `<img>` tag appears in the EPUB spine content THEN, instead of stripping it, write a markdown link `![](images/<basename>)` at that same position in the output, where `<basename>` is the file name taken from the tag's `src` attribute.
     // Commentary: the inline link at the figure's reading-flow position (next to its caption) is what lets /generate_questions R9b open the figure and transcribe formulas, tables, and data. R13c overrides the "strip tags" clause of R13 for `<img>`.
R13d. Emit an inline link per R13c for every `<img>`, including images that look decorative (covers, chapter-opener photos, logos). Do NOT judge relevance at extract time.
     // Commentary: /generate_questions decides per question whether a figure is worth opening; the extract step's job is only to make every figure reachable.
R13e. IF an image basename to be copied already exists in `extracted/images/` from a different source file THEN prefix both the copied file and its inline links with the sanitized source name + `_`.

// Heading reconstruction (EPUB)
R13f. IF the EPUB spine content contains `<h1>`–`<h6>` tags THEN map each to the markdown level of the same depth (`<h1>`→`#`, `<h2>`→`##`, … `<h6>`→`######`).
R13g. IF the EPUB spine content contains no `<h1>`–`<h6>` tags THEN reconstruct the heading hierarchy from the book's own title/numbering scheme per R13h–R13j.
     // Commentary: some EPUBs (e.g. Kurose) mark every paragraph with identical `<p>` styling and carry zero heading tags, so heading level must be inferred from the title text itself. Without this, the output has no `##` blocks and /generate_questions (R7/R8) has nothing to segment into units.
R13h. Under R13g, treat a block-level element (`<p>`/`<div>`) as a heading candidate ONLY when its entire trimmed text is one of:
     - `Chapter <N> <Title>` → chapter heading;
     - `<C>.<S> <Title>` where `<C>` ≤ the number of chapters detected AND `<Title>` begins with a capital letter or `(` → numbered-section heading.
R13i. Reject a R13h candidate that: (a) ends with a trailing page number (` <digits>` at end of line); (b) appears inside an `<a>` link or embedded within a longer sentence; or (c) repeats a chapter/section number already emitted.
     // Commentary: each title appears ~3× — once in the table of contents (trailing page number), once as the body heading (no page number), and again in cross-reference links. Only the body occurrence becomes a heading. Rejecting trailing-page-number lines drops the TOC; the "entire trimmed text" test in R13h drops inline mentions.
R13j. Emit chapter headings as `#` and numbered-section headings as `##`.
     // Commentary: /generate_questions R7/R8 counts `##` blocks as units, so numbered sections must be `##` (not `#` or `###`) to segment correctly.
R14. IF the file is a PPTX THEN extract with Python `zipfile` + `xml.etree.ElementTree`: unzip, find `ppt/slides/slide*.xml`, collect all `<a:t>` text nodes in order.

// Writing
R15. Write all extracted text verbatim to the output file. Preserve structure (headings, lists, tables, code blocks) where possible.
R16. Do NOT summarize, filter, or omit anything.
     // Commentary: notes are the study/exam reference; any omission creates gaps the user won't know exist until they need the missing content.

// Moving sources
R17. IF the output write succeeded AND the argument was a subfolder THEN create `source/` if needed and move the whole subfolder to `source/<subfolder>/`.
R18. IF the output write succeeded AND the target was a single file or loose files THEN create `source/` if needed and move each file individually into `source/`.
R19. IF the output write failed THEN do NOT move any files.
     // Commentary: moving after a failed write would leave the source inaccessible.
R20. Do NOT move `extracted/` (including `extracted/images/`), `source/`, `code/`, `CLAUDE.md`, or `README.md`.

// CLAUDE.md Contents update
R21. IF the output write succeeded AND the class root contains a `CLAUDE.md` with a `## Contents` section THEN add a one-line entry for the new notes file under its `**extracted/**` group and update the `**source/**` group to reflect the moved files. IF a needed group header does not exist THEN create it.
R22. IF the output write succeeded AND the class root contains a `CLAUDE.md` without a `## Contents` section THEN append a `## Contents` section (format: `**<dir>/**` bold group headers, one `- file — description` line per entry) and populate it per R21.
R23. IF the class root contains no `CLAUDE.md` THEN skip R21–R22.
R24. IF updating the Contents section THEN do not modify any other part of `CLAUDE.md`.

// Confirm
R25. Print what was written to `extracted/`, how many images were copied to `extracted/images/` (per R13a) or that PDF figures were not extracted (per R11a), how many chapter/section headings were reconstructed when R13g applied, what was moved to `source/`, and whether `CLAUDE.md` Contents was updated.

// Catch-all
R26. IF any condition not covered by R1–R25 (including lettered sub-rules) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Sanitization (single-file argument)

Strip the extension, drop everything after the first ` - ` or `(`, lowercase, replace spaces/punctuation with underscores, truncate to ~30 chars.
// Example: `"James Kurose, Keith Ross - Computer Networking_ A Top-Down Approach (7th Edition)...epub"` → `extracted/james_kurose_computer_networking_notes.md`.

## Usage

```
/extract wk9
/extract textbook.epub
/extract
```
