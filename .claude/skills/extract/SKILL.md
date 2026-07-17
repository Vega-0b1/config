---
name: extract
description: Extract all content from PDFs/DOCX/EPUB/PPTX files in the current directory (or a specified subfolder/file) into a single markdown notes file saved to extracted/. After extracting, moves the source files into source/.
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
R12. IF the file is a DOCX THEN extract with Python `zipfile` + `xml.etree.ElementTree`: unzip, parse `word/document.xml`, collect all `<w:t>` text nodes per paragraph.
R13. IF the file is an EPUB THEN extract with Python `zipfile` + `xml.etree.ElementTree`: unzip, find `.xhtml`/`.html` files in spine order (via `META-INF/container.xml` → `content.opf`), strip tags, concatenate. Skip nav/TOC files.
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
R20. Do NOT move `extracted/`, `source/`, `code/`, `CLAUDE.md`, or `README.md`.

// CLAUDE.md Contents update
R21. IF the output write succeeded AND the class root contains a `CLAUDE.md` with a `## Contents` section THEN add a one-line entry for the new notes file under its `**extracted/**` group and update the `**source/**` group to reflect the moved files. IF a needed group header does not exist THEN create it.
R22. IF the output write succeeded AND the class root contains a `CLAUDE.md` without a `## Contents` section THEN append a `## Contents` section (format: `**<dir>/**` bold group headers, one `- file — description` line per entry) and populate it per R21.
R23. IF the class root contains no `CLAUDE.md` THEN skip R21–R22.
R24. IF updating the Contents section THEN do not modify any other part of `CLAUDE.md`.

// Confirm
R25. Print what was written to `extracted/`, what was moved to `source/`, and whether `CLAUDE.md` Contents was updated.

// Catch-all
R26. IF any condition not covered by R1–R25 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Sanitization (single-file argument)

Strip the extension, drop everything after the first ` - ` or `(`, lowercase, replace spaces/punctuation with underscores, truncate to ~30 chars.
// Example: `"James Kurose, Keith Ross - Computer Networking_ A Top-Down Approach (7th Edition)...epub"` → `extracted/james_kurose_computer_networking_notes.md`.

## Usage

```
/extract wk9
/extract textbook.epub
/extract
```
