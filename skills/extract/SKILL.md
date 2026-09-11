---
name: extract
description: Extract all content from PDFs/DOCX/EPUB/PPTX files into a markdown notes file. Accepts an optional output directory (defaults to extracted/). PDFs gain a `## Page N` heading per page and PPTX decks a `## Slide N` heading per slide, so extracted content can be cited and grepped by location. Scanned and oversized PDFs go through `pdftotext -layout` + `pdf_layout.py`, which strips repeated running heads and rebuilds chapter/section/subsection headings from the book's own numbering, tolerating OCR damage and rejecting table-of-contents lines. When extracting a textbook to extracted/textbook/, also splits it into per-chapter slices using the chapter heading pattern from the Source Profile. After extracting, moves the source files into source/.
---

Scan files and extract all content into a single markdown file. Output directory is caller-specified or defaults to `extracted/`.

## Rules

// Target and output resolution
R0.  IF the caller provides an output directory (e.g. `/updateclass` passing `extracted/class/week1/`) THEN OUTDIR = that directory. OTHERWISE OUTDIR = `extracted/`.
R1.  IF the argument names a subfolder (e.g. `wk9`) THEN target = all files inside that subfolder; output = `OUTDIR/<subfolder>_notes.md`.
R2.  IF the argument names a single file (e.g. `textbook.epub`) THEN target = that file; output = `OUTDIR/<sanitized>_notes.md`, sanitized per the Sanitization block below.
R3.  IF no argument is given THEN target = all loose files in the current directory; output = `OUTDIR/<current-folder-name>_notes.md`.
R4.  IF cwd's basename is `source`, `extracted`, `code`, or `images` THEN warn the user that cwd is not a class root and ask whether to proceed. STOP until user responds.
R4a. IF cwd contains no `CLAUDE.md` AND no `extracted/` directory THEN apply R4's warning as well.
R5.  IF OUTDIR does not exist THEN create it (including intermediate directories).
R6.  IF the output file already exists THEN stop and warn the user before overwriting. STOP until user responds.
R7.  IF no extractable content files are found THEN stop and tell the user.

// Reading
R8.  Supported formats: PDF, DOCX, PPTX, EPUB, and the legacy binaries PPT and DOC via the conversion in R8a–R8f.

// Legacy binary formats
R8a. IF a target file's extension is `.ppt` or `.doc` THEN convert it to the modern equivalent before extracting.
R8b. Confirm the file is OLE2 by reading its first 8 bytes (`d0 cf 11 e0 a1 b1 1a e1`). IF they do not match THEN skip the conversion and extract as the modern counterpart.
R8c. Convert with `soffice --headless --convert-to <target> <file>`. Target = `pptx` for `.ppt` and `docx` for `.doc`.
R8d. IF `soffice` is not on PATH THEN stop and tell the user the file needs LibreOffice to convert.
R8e. IF the conversion produces no output file THEN stop and report it.
R8f. Extract from the CONVERTED file. Keep the original. R17a or R18a moves both after successful incorporation.
R8g. IF an extraction run begins THEN initialize EXTRACTED_SOURCES as an empty ordered set of absolute paths.
R8h. IF a target file's content is incorporated into the output without conversion THEN add that target file's absolute path to EXTRACTED_SOURCES.
R8i. IF a converted file's content is incorporated into the output THEN add the original and converted files' absolute paths to EXTRACTED_SOURCES.
R8j. IF a target file is skipped OR its extraction fails THEN do NOT add that target or its converted file to EXTRACTED_SOURCES.

R9.  IF a file is unrelated (`.gitignore`, lock files, code files, existing markdown in `extracted/`) THEN skip it.
R10. IF multiple files are targeted THEN read them in parallel.
R11. IF the file is a PDF AND it is under 100 MB AND it is BORN-DIGITAL THEN read it directly with the Read tool.
R11a. IF a source carries figures THEN say so in the report — the format and that its figures were not extracted.
R11a1. IF the file is a PDF AND (it is 100 MB or larger OR it is SCANNED) THEN extract with `pdftotext -layout <file> <raw.txt>`, then build the notes file with `pdf_layout.py <raw.txt> <notes.md>` (next to this skill).
R11a2. IF the Read tool returns a size error on a PDF THEN fall back to R11a1. Do NOT report the extraction as blocked.
R11b. IF the file is a PDF THEN emit `## Page <N>` on its own line immediately before each page's content, where `<N>` is that page's 1-indexed position in the PDF.
R11d. IF a PDF page yields no extractable text THEN emit its `## Page <N>` heading anyway, followed by no content.

// Scanned PDFs — detect at extract time, never later
R11f. IF the file is a PDF THEN classify it as SCANNED or BORN-DIGITAL before extracting, and record which in the report.
R11g. Classify SCANNED IF either holds: (a) the `Producer` or `Creator` names a scanner or an OCR pass — `Paper Capture`, `Image Converter`, `MFP`, `intsig`, `CamScanner`, `ScanSnap`; or (b) `pdftotext` over three sample pages yields under 200 characters per page while `pdfimages -list` shows a full-page image on those pages.
R11h. PDF alone is NOT the risk factor; SCANNED is. A born-digital PDF carries the publisher's own text and extracts cleanly.
R11i. IF a PDF is SCANNED THEN run `rejoin_ocr.py` (next to this skill) over the finished notes file, and report the merge count.
R11j. IF a PDF is SCANNED THEN say so in the class `CLAUDE.md` Source Profile, naming the residual damage as character-level and stating that re-extraction will NOT repair it.
R11k. Residual substitutions — `nonnal` for `normal`, `tum` for `turn` — are repaired only by reading the page image: `pdftoppm -f <p> -l <p> -r 170 -png`. Do this per chapter, on demand, not across a whole book.
R11k1. Visual repair is TRANSCRIPTION from the image, never inference from context. IF a token cannot be read clearly THEN leave it as-is and flag it.
R11k2. Repairing text invalidates every `Source quote:` generated against the old text. Repair a chapter BEFORE generating its questions.
R11l. Do NOT use a word-fragment rate as a quality gate on its own. The measure is English-prose-specific and over-reports on non-English text and math-heavy content.

// Pipeline order
R11m. IF a PDF is extracted under R11a1 THEN run the stages in this order: `pdftotext -layout` → `pdf_layout.py` → `rejoin_ocr.py` → chapter split (R16a–R16b4). Do NOT reorder them.
R11m1. Run `rejoin_ocr.py` AFTER headings exist, so its heading-preservation check counts them.
R11m2. Keep the `pdftotext` output. IF a later stage needs re-running THEN re-run it from that file, not from the PDF.

// PDF running heads — layout furniture, not content
R11n. A running head is the line a print layout repeats at the top of every page: verso `<folio>   CHAPTER <N>. <TITLE>`, recto `<N>.<M>. <TITLE>   <folio>`. IF a line falls within the first three non-blank lines of a page AND matches a running-head form THEN remove it.
R11n1. R11n is the only exception to R16. A running head is duplicated furniture, so removing it deletes no content.
R11n2. Do NOT remove a running-head candidate that sits below the third non-blank line of its page.
     // Commentary: body text can legitimately open with a numeral. Position is what makes the signal safe to act on.
R11n3. IF OCR splits the folio across a space (`11 6` for 116) THEN still match it.
R11n4. Report the count of running heads removed.

// Heading reconstruction (PDF)
R11o. IF the file is a PDF THEN reconstruct chapter, section, and subsection headings from the book's own numbering.
R11o1. `Chapter <N>` alone on a line → `# Chapter <N>: <Title>`, where `<Title>` is the one-to-three short Title-Case lines printed under it. Stop collecting at the first line over 60 characters or ending in a period.
R11o2. `<C>.<S> <Title>` → `## <C>.<S> <Title>`.
R11o3. `<C>.<S>.<U> <Title>` → `### <C>.<S>.<U> <Title>`. Test the three-level form BEFORE the two-level form.
     // Commentary: `7.4.1` also matches the two-level shape, so testing two-level first silently demotes every subsection to a section.
R11o4. Match numerals OCR-tolerantly: allow whitespace around each dot (`7 .1`, `4.7. 1`) and accept `I`, `l`, or `O` in a numeral position.
     // Commentary: a strict `^\d+\.\d+` regex dropped 14 real sections and all 414 subsections of the Du textbook, and the loss was invisible in the output.
R11o5. Accept a section or subsection candidate ONLY IF its chapter number equals the chapter currently open.
R11o6. Reject a candidate that carries dot leaders (`. . .`), OR ends in two-or-more spaces followed by a page number, OR whose title is entirely uppercase.
     // Commentary: those three are the table-of-contents and running-head signatures. A textbook prints every section number three times — book TOC, chapter TOC, body heading — and only the third is a heading.
R11o7. Report counts of chapters, sections, and subsections emitted, and of candidates rejected under R11o6.
R11o8. After writing, verify for each heading level that the total count equals the unique count. IF they differ THEN table-of-contents lines leaked through — stop and report before splitting chapters.
     // Example: 500 `## N.N` lines against 188 unique numbers means each section was emitted from the book TOC, the chapter TOC, and the body. Only the body one is a heading.
R11o9. IF a heading level's unique count is far below the count of that level's entries in the book's table of contents THEN the numeral pattern is too strict — widen it under R11o4 and re-run.

R12. IF the file is a DOCX THEN extract with Python `zipfile` + `xml.etree.ElementTree`: unzip, parse `word/document.xml`, collect all `<w:t>` text nodes per paragraph.
R13. IF the file is an EPUB THEN extract with Python `zipfile` + `xml.etree.ElementTree`: unzip, find `.xhtml`/`.html` files in spine order (via `META-INF/container.xml` → `content.opf`), strip tags, concatenate. Skip EPUB navigation/TOC documents. This exclusion overrides R16 and R16g because those documents are duplicated structural furniture; it does not exclude a body-spine page merely titled Contents or any caption/body text.

// Figures — no format extracts them
R13a. Do NOT extract embedded images from ANY source format, and do NOT create an `images/` directory. `<img>` tags are stripped like every other tag under R13.
R13b. IF a figure's caption is text in the spine content THEN it survives extraction as ordinary prose. Do NOT strip captions.
R13c. Do NOT write a placeholder — no `![](…)`, no `[FIGURE]` — where an `<img>` was stripped.

// Heading reconstruction (EPUB)
R13f. IF the EPUB spine content contains `<h1>`–`<h6>` tags THEN map each to the markdown level of the same depth (`<h1>`→`#`, `<h2>`→`##`, … `<h6>`→`######`).
R13g. IF the EPUB spine content contains no `<h1>`–`<h6>` tags THEN reconstruct the heading hierarchy from the book's own title/numbering scheme per R13h–R13j.
R13h. Under R13g, treat a block-level element (`<p>`/`<div>`) as a heading candidate ONLY when its entire trimmed text is one of:
     - `Chapter <N> <Title>` → chapter heading;
     - `<C>.<S> <Title>` where `<C>` ≤ the number of chapters detected AND `<Title>` begins with a capital letter or `(` → numbered-section heading.
R13i. Reject a R13h candidate that: (a) ends with a trailing page number; (b) appears inside an `<a>` link or embedded within a longer sentence; or (c) repeats a chapter/section number already emitted.
R13j. Emit chapter headings as `#` and numbered-section headings as `##`.

R14. IF the file is a PPTX THEN extract with Python `zipfile` + `xml.etree.ElementTree`: unzip, find `ppt/slides/slide*.xml`, and process each slide separately in numeric slide order.
R14a. Order slides by the integer in the `slideN.xml` filename, not by the archive's listing order.
R14b. IF processing a slide THEN emit `## Slide <N> — <title>` on its own line, then that slide's `<a:t>` text nodes in document order.
R14c. `<title>` under R14b = the text of the shape whose `<p:ph>` placeholder type is `title` or `ctrTitle`. IF the slide has no such placeholder THEN `<title>` = the slide's first `<a:t>` text node. IF the slide has no text at all THEN emit the heading as `## Slide <N>` with no title.
R14c1. When assembling text from `<a:t>` runs, join runs WITHIN one `<a:p>` paragraph with NO separator, and join paragraphs with a single space. Do NOT insert a separator between runs.
R14d. IF a slide's `<a:t>` nodes were consumed by R14c to supply the title THEN still emit them in the slide's body content. Do NOT drop a text node because it was read for the heading.
R14e. Emit `# <deck name>` once at the top of the output, where `<deck name>` is the sanitized source filename per the Sanitization block.

// Locator headings
R14f. `## Page <N>` (R11b) and `## Slide <N> — <title>` (R14b) are locator headings: they record where content sits in its source document. They do NOT assert structural sections. /generate-questions excludes them when segmenting.

// Writing
R15. Write all extracted text verbatim to the output file. Preserve structure (headings, lists, tables, code blocks) where possible.
R15a. R11b, R14b, and R14e emit headings that do not appear in the source. R15's verbatim requirement governs the extracted text only.
R15b. R11o may join a detected chapter-number line with its verbatim title line(s) and insert Markdown heading punctuation. Aside from that reconstruction, the source words survive unchanged; only leading whitespace and alignment padding may be dropped.
R16. Do NOT summarize, filter, or omit anything.
R16g. R11n overrides R16: running heads are removed. No other rule may omit source text.
R16h. Verify the `pdf_layout.py` output against the `pdftotext` text: every non-heading line in the output must appear in the raw text. IF a line was invented THEN stop and report.
R16h1. Run R16h BEFORE `rejoin_ocr.py`, never after. `rejoin_ocr.py` rewrites lines by design, so the comparison is only meaningful on the pre-rejoin artifact.
     // Commentary: R16h catches a heading-reconstruction bug that rewrites text instead of re-tagging it. Run after the rejoin and it reports thousands of false differences.

// Chapter splitting (textbook only)
R16a. IF OUTDIR is `extracted/textbook/` AND the class root contains a `CLAUDE.md` with a `## Source Profile` section that declares a chapter heading pattern THEN split the output into per-chapter slices.
R16a1. BEFORE writing any slice, scan the existing slices for a `<!-- visual-repair: done -->` marker on their first line.
R16a2. IF any existing slice carries that marker THEN stop, list every marked chapter by number, state that re-splitting discards their visual repair, and ask whether to `overwrite` or `cancel`. STOP until user responds.
     // Commentary: `/generate-questions` R4b repairs a chapter by reading its page images one at a time. That work is expensive, lives only in the slice, and a re-extraction overwrites it with no error. The loss is silent — the new slice looks correct.
R16a3. IF the user answers `cancel` THEN write the full notes file but do NOT split. Report which chapters were preserved.
R16a4. IF the user answers `overwrite` THEN split normally and report how many repaired chapters were discarded and that they need re-repair on their next `/generate-questions` run.
R16a5. R16a1's scan is a precondition of R16a, not of R16b. Run it once before the first slice is written, never per slice.
R16b. IF R16a applies THEN for each chapter found by the heading pattern: create `OUTDIR/chapters/chapter<N>/` and write that chapter's content (from its heading to the line before the next chapter heading) to `OUTDIR/chapters/chapter<N>/chapter<N>.md`.
R16b1. IF a slice has no `<!-- visual-repair: done -->` marker THEN its chapter heading line IS its first line.
R16b1a. IF a slice has `<!-- visual-repair: done -->` as its first line THEN its chapter heading line IS its second line.
R16b1b. IF any line other than the visual-repair marker precedes the chapter heading line THEN the slice is wrong.
R16b2. The boundary is anchored on the CHAPTER heading only. Do NOT anchor it on a section heading, a page locator, or any other pattern.
R16b3. Cutting late loses the chapter opener, which is content, not front matter.
R16b4. After writing the slices, verify R16b1–R16b1b for every one. Report the count checked and any that failed.
R16c. IF the class uses a non-English chapter convention (e.g. `capitulo`) THEN use that convention for directory and file names: `OUTDIR/chapters/capitulo<N>/capitulo<N>.md`.
R16d. IF the textbook has content before the first chapter heading (front matter, preface) THEN do NOT create a slice for it. It lives only in the full book file.
R16e. The full book file written by R15 is NOT affected by the split. Both the full file and the per-chapter slices exist side by side.
R16f. IF R16a does not apply THEN skip the split entirely.

// Moving sources
R17. IF the output write succeeded AND the argument was a subfolder THEN create `source/<subfolder>/` if needed.
R17a. IF R17 applies THEN move each path in EXTRACTED_SOURCES into `source/<subfolder>/`, preserving its filename.
R17b. IF R17a leaves the target subfolder empty THEN remove the empty target subfolder.
R18. IF the output write succeeded AND the target was a single file or loose files THEN create `source/` if needed.
R18a. IF R18 applies THEN move each path in EXTRACTED_SOURCES individually into `source/`, preserving its filename.
R18b. IF R17 or R18 applies THEN leave every path not in EXTRACTED_SOURCES at its original location.
R19. IF the output write failed THEN do NOT move any files.
R20. IF a candidate move path is `extracted/`, `source/`, `code/`, `CLAUDE.md`, or `README.md` THEN do NOT move it.
R20a. IF R20 and either R17a or R18a apply THEN R20 overrides R17a and R18a.

// CLAUDE.md Contents update
R21. IF the output write succeeded AND the class root contains a `CLAUDE.md` with a `## Contents` section THEN add a one-line entry for the new notes file under its `**extracted/**` group and update the `**source/**` group to reflect the moved files.
R22. IF the output write succeeded AND the class root contains a `CLAUDE.md` without a `## Contents` section THEN append a `## Contents` section and populate it per R21.
R23. IF the class root contains no `CLAUDE.md` THEN skip R21–R22.
R24. IF updating the Contents section THEN do not modify any other part of `CLAUDE.md`.

// Confirm
R25. Report: what was written and its path, OUTDIR used, any legacy file converted and what it became, any extension/magic mismatch, figures present but not extracted, SCANNED/BORN-DIGITAL classification of every PDF and which test decided it, `rejoin_ocr.py` merge count for scanned sources, `## Page`/`## Slide` anchor counts, empty page counts, slides with no title placeholder, heading reconstruction count when R13g applied, chapter slices written and R16b4 verification result, what was moved to `source/`, whether `CLAUDE.md` Contents was updated.
R25a. IF a PDF was extracted under R11a1 THEN also report: running heads removed (R11n4), chapter/section/subsection counts and R11o6 rejections (R11o7), the R11o8 total-vs-unique check per level, and the R16h no-invented-lines check.
R25b. IF R16a1 found repaired slices THEN report which chapters were discarded or preserved, and that a discarded chapter re-repairs on its next `/generate-questions` run.

// Catch-all
R26. IF any condition not covered by R0–R25 (including lettered sub-rules) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Sanitization (single-file argument)

Strip the extension, drop everything after the first ` - ` or `(`, lowercase, replace spaces/punctuation with underscores, truncate to ~30 chars.
// Example: `"James Kurose, Keith Ross - Computer Networking_ A Top-Down Approach (7th Edition)...epub"` → `OUTDIR/james_kurose_computer_networking_notes.md`.

## Usage

```
/extract wk9                          ← standalone, output to extracted/
/extract textbook.epub                ← standalone, output to extracted/
/extract                              ← standalone, output to extracted/
```

When called by `/updateclass`, the output directory is passed by the caller:

```
/updateclass answers y, week 1  → /extract deck.pptx  → output to extracted/class/week1/
/updateclass answers t          → /extract book.epub   → output to extracted/textbook/
/updateclass answers c          → /extract syllabus.pdf→ output to extracted/
/updateclass answers m          → /extract setup.pdf   → output to extracted/class/misc/
```
