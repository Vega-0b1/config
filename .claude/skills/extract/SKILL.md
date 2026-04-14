---
name: extract
description: Extract quiz-relevant content from a weekly folder of PDFs/DOCX files into a single markdown notes file saved to extracted/. Avoids re-reading PDFs every quiz session.
---

Scan all files in the specified weekly folder (e.g., `wk9/`) and extract all quiz-relevant content into a single markdown file saved to `extracted/`.

## Instructions

1. **Glob the target week folder** to list all files
2. **Read all files** — PDFs, DOCX, PPTX — in parallel where possible. Weekly overviews and reading assignments may contain quiz focus clues (key topics, guiding questions), so include them. Skip only files that are clearly unrelated (e.g., syllabus, administrative forms).
3. **Write a single markdown file** to `extracted/<week>_notes.md` with the following sections (include only what's present):
   - Algorithm pseudocode (exact, verbatim)
   - Definitions and key concepts
   - Running time analysis with recurrences and proofs
   - Loop invariants (all 3 parts: initialization, maintenance, termination)
   - Theorems and lemmas with proofs
   - Example traces
   - All group activity / group project exercises with full solutions
   - All quiz questions with correct answers
   - Summary table and common mistakes

4. **Goal:** After extraction, future quiz sessions only need the markdown file — no PDFs.

## Usage

```
/extract wk9
```
