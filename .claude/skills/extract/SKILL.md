---
name: extract
description: Extract all content from PDFs/DOCX/EPUB/PPTX files in the current directory (or a specified subfolder/file) into a single markdown notes file saved to extracted/. PDFs gain a `## Page N` heading per page and PPTX decks a `## Slide N` heading per slide, so extracted content can be cited and grepped by location. For EPUBs, also extracts embedded images to extracted/images/ and links them inline so /generate_questions can read figures. After extracting, moves the source files into source/.
---

Scan files and extract all content into a single markdown file saved to `extracted/`.

## Rules

// Target and output resolution
R1.  IF the argument names a subfolder (e.g. `wk9`) THEN target = all files inside that subfolder; output = `extracted/<subfolder>_notes.md`.
R2.  IF the argument names a single file (e.g. `textbook.epub`) THEN target = that file; output = `extracted/<sanitized>_notes.md`, sanitized per the Sanitization block below.
R3.  IF no argument is given THEN target = all loose files in the current directory; output = `extracted/<current-folder-name>_notes.md`.
R4.  IF cwd's basename is `source`, `extracted`, `code`, or `images` THEN warn the user that cwd is not a class root and ask whether to proceed. STOP until user responds.
R4a. IF cwd contains no `CLAUDE.md` AND no `extracted/` directory THEN apply R4's warning as well.
     // Commentary: R4 and R4a are the two decidable tests for "not a class root". A class root either has been scaffolded by /addclass (CLAUDE.md) or has been extracted into before (extracted/).
R5.  IF `extracted/` does not exist THEN create it.
R6.  IF the output file already exists THEN stop and warn the user before overwriting. STOP until user responds.
     // Commentary: a previous extraction may have been intentional; the user may have added manual notes to it.
R7.  IF no extractable content files are found THEN stop and tell the user.

// Reading
R8.  Supported formats: PDF, DOCX, PPTX, EPUB, and the legacy binaries PPT, DOC, XLS via the conversion in R8a–R8f.

// Legacy binary formats
R8a. IF a target file's extension is `.ppt`, `.doc`, or `.xls` THEN convert it to the modern equivalent before extracting, per R8b–R8f. Do NOT attempt to parse the binary directly.
     // Commentary: these are OLE2 compound documents, not zip containers. R12's and R14's `zipfile` calls raise BadZipFile on them, which is how a legacy deck reaches the user as an error instead of as notes.
R8b. Confirm the file is OLE2 by reading its first 8 bytes and comparing them to `d0 cf 11 e0 a1 b1 1a e1`. IF they do not match THEN skip the conversion, extract the file as its modern counterpart, and note the mismatch in the R25 report.
     // Commentary: a file named `.ppt` whose magic is `PK` is a mislabeled PPTX. Converting it would be pointless work, and rewriting it could lose content the direct path reads fine.
R8c. Convert with `soffice --headless --convert-to <target> <file>`, writing the output beside the original. Target = `pptx` for `.ppt`, `docx` for `.doc`, `xlsx` for `.xls`.
R8d. IF `soffice` is not on PATH THEN stop and tell the user the file needs LibreOffice to convert. Do NOT attempt to parse the binary and do NOT silently skip the file.
R8e. IF the conversion produces no output file THEN stop and report it. Do NOT fall back to parsing the original.
R8f. Extract from the CONVERTED file. Keep the original. R17–R18 move both to `source/`.
     // Commentary: the original is the file the professor actually sent. Deleting it after a lossy format conversion would leave no way to redo the extraction if the converter mangled something.
R9.  IF a file is unrelated (`.gitignore`, lock files, code files, existing markdown in `extracted/`) THEN skip it.
R10. IF multiple files are targeted THEN read them in parallel.
     // Commentary: matters especially for large courses with many weekly slide decks.
R11. IF the file is a PDF THEN read it directly with the Read tool.
R11a. IF the file is a PDF, DOCX, or PPTX THEN do NOT extract its embedded images; note in the R25 report which of those formats were processed and that their figures were not extracted.
     // Commentary: only the EPUB path (R13a–R13e) resolves an image to its position in the reading flow. PDF image streams carry no markup tying a figure to its section; DOCX and PPTX store images as relationship IDs this skill does not resolve. Naming all three keeps a figure-bearing slide deck from silently losing its figures with no report line.
R11b. IF the file is a PDF THEN emit `## Page <N>` on its own line immediately before each page's content, where `<N>` is that page's 1-indexed position in the PDF.
R11c. R11b applies to every PDF extraction. There is no flag, no format exemption, and no size threshold.
     // Commentary: the Read tool already returns a PDF page by page, so this records a boundary that exists rather than inferring one. The anchor is what turns "find the definition of congestion window" into a citable location instead of a scan through an undifferentiated dump.
R11d. IF a PDF page yields no extractable text THEN emit its `## Page <N>` heading anyway, followed by no content.
     // Commentary: skipping an empty page's heading shifts every later page number off by one against the real document, which destroys the exact mapping the heading exists to preserve.
R11e. PDFs extracted before R11b existed carry no page headings. Do NOT retrofit them during an unrelated run. A file gains anchors only when it is re-extracted deliberately.
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
R14. IF the file is a PPTX THEN extract with Python `zipfile` + `xml.etree.ElementTree`: unzip, find `ppt/slides/slide*.xml`, and process each slide separately in numeric slide order.
R14a. Order slides by the integer in the `slideN.xml` filename, not by the archive's listing order.
     // Commentary: `zipfile.namelist()` returns `slide10.xml` before `slide2.xml` under a lexical sort, which silently reorders a deck past nine slides.
R14b. IF processing a slide THEN emit `## Slide <N> — <title>` on its own line, then that slide's `<a:t>` text nodes in document order.
R14c. `<title>` under R14b = the text of the shape whose `<p:ph>` placeholder type is `title` or `ctrTitle`. IF the slide has no such placeholder THEN `<title>` = the slide's first `<a:t>` text node. IF the slide has no text at all THEN emit the heading as `## Slide <N>` with no title and no em dash.
R14c1. When assembling text from `<a:t>` runs, join runs WITHIN one `<a:p>` paragraph with NO separator, and join paragraphs with a single space. Do NOT insert a separator between runs.
     // Commentary: PowerPoint splits a single visual word across several runs whenever formatting changes mid-word, and one smart quote is enough to trigger it. Joining runs with a space produces `What ’ s the Internet: “ nuts and bolts ” view` instead of `What’s the Internet: “nuts and bolts” view` — and that mangled string is what R12o writes into the questions file as the locator citation.
R14d. IF a slide's `<a:t>` nodes were consumed by R14c to supply the title THEN still emit them in the slide's body content. Do NOT drop a text node because it was read for the heading.
     // Commentary: the title placeholder is content as well as a label; removing it from the body would lose the slide's own statement of its topic.
R14e. Emit `# <deck name>` once at the top of the output, where `<deck name>` is the sanitized source filename per the Sanitization block.
     // Commentary: gives the file one `#` above its `##` slide anchors, so it profiles as a single document rather than as a headless run of sibling sections.

// Locator headings
R14f. `## Page <N>` (R11b) and `## Slide <N> — <title>` (R14b) are locator headings: they record where content sits in its source document. They do NOT assert that the content beneath them is a structural section of the work.
     // Commentary: /generate_questions excludes locator headings when it segments a file into chapters and units. Without that exclusion a 400-page PDF profiles as 400 one-page units. This rule states the contract; that skill enforces it.

// Writing
R15. Write all extracted text verbatim to the output file. Preserve structure (headings, lists, tables, code blocks) where possible.
R15a. R11b, R14b, and R14e emit headings that do not appear in the source. R15's verbatim requirement governs the extracted text only. Emitting those headings is not a violation of R15 or R16.
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
R25. Print any legacy file converted under R8a–R8f and what it became, any extension/magic mismatch found under R8b, what was written to `extracted/`, how many images were copied to `extracted/images/` (per R13a), which non-EPUB formats had their figures skipped (per R11a), how many chapter/section headings were reconstructed when R13g applied, how many `## Page` anchors were emitted per PDF (per R11b) and how many of those pages were empty (per R11d), how many `## Slide` anchors were emitted per PPTX (per R14b) and how many slides had no title placeholder (per R14c), what was moved to `source/`, and whether `CLAUDE.md` Contents was updated.

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
