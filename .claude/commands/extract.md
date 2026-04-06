# Extract Week Notes

Scan all files in the specified weekly folder (e.g., `wk5/`) and extract all quiz-relevant content into a single markdown file saved to `extracted/`.

## Instructions

1. **Glob the target week folder** to list all files
2. **Skip low-value files:** weekly overviews, reading assignments, and any clearly unrelated files (e.g., Oregon Trail brochure)
3. **Read and extract from all remaining files** — PDFs, DOCX, PPTX
4. **Write a single markdown file** to `extracted/<week>_notes.md` with the following sections (include only what's present in the source material):
   - Algorithm pseudocode (exact, verbatim)
   - Definitions and key concepts
   - Running time analysis with recurrences and proofs
   - Loop invariants (all 3 parts: initialization, maintenance, termination)
   - Theorems and lemmas with proofs
   - Example traces
   - All group activity / group project exercises with full solutions
   - All quiz questions with correct answers
   - Summary table and common mistakes

5. **Goal:** After extraction, future quiz sessions should require reading only the markdown file — no PDFs.

## Usage

```
/extract wk9
```

