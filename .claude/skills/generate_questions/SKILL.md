---
name: generate_questions
description: Build and audit quiz questions for use by /learn. The textbook is the only question source. A BOOK run (chapter1, ch1) reads the chapter slice at extracted/textbook/chapters/chapter<N>/chapter<N>.md, generates audited questions, and writes them next to it — this is the question POOL. A SELECT run (week1, wk1) generates nothing: it reads the week's ### Teaching material only to learn which topics the professor covered, then copies the matching questions out of the pool into extracted/class/week<N>/questions_week<N>.md. Re-running a BOOK file warns before overwriting. Re-running a SELECT file offers resync (refresh copies from their origin) or reselect (rebuild the selection).
---

Build a question pool from the textbook; select this week's practice set out of it.

Two paths, selected by the argument (R0k–R0l):

- **Book run** — `chapter1` — GENERATES audited questions from the textbook chapter. Everything the
  book explains. This file is a reference bank, not a study list.
- **Select run** — `week1` — GENERATES NOTHING. It reads the week's registered class material to
  determine what the professor covered, then copies the questions that match out of the book pool.
  This file is the study list.

The textbook is the only thing that ever produces a question. Class material only ever answers one
question: *which of the book's questions are on the table this week?*

## Rule files

This file holds the SHARED core: run-type dispatch, existing-file handling, output paths,
verification, and the report contract. The path-specific rules live beside it:

- `book.md` — Source Profile, chapter loading, visual repair, unit segmentation, concept inventory,
  curated adoption, question generation, answer keys, translation, audit, constructive exercises.
- `select.md` — week material loading, coverage profile, pool, matching, copying, resync, reselect.

Two helpers sit alongside them: `verify_quotes.py` (R23 quote verification) and `splice_chapter.py`
(R4b5 — writes a visually repaired chapter slice back into the full textbook notes file).

R0k2 requires the matching file to be read before anything else happens. Rule IDs are global and
unique across all three files; a rule cited by number lives in whichever file its block sits in.

## Rules — shared core

// Run type — selects which rule file loads; resolve before anything else touches a file
R0k. IF the argument normalizes to a week — `week<N>` or `wk<N>`, case-insensitively — THEN this is a SELECT run. Apply R0m–R0t3 and SKIP R1–R4b6.
R0l. IF the argument does not normalize to a week THEN this is a BOOK run. Apply R1–R4b6.
R0k1. `week<N>` and `wk<N>` are reserved forms.
R0k2. IF the run type is resolved under R0k or R0l THEN Read the matching rule file from this skill's directory BEFORE applying any rule below: book run → `book.md`, select run → `select.md`.
R0k2a. IF the matching rule file has not been read THEN no source may be loaded, no question may be generated or copied, and no file may be saved. This file alone is not sufficient to run the skill.
R0k3. IF this is a SELECT run THEN R9a–R23a do NOT run. Do NOT build a concept inventory, do NOT classify exercises, do NOT adopt curated questions, do NOT generate a candidate, and do NOT audit anything.

// Existing-file handling
R5.  IF the output path (R24) already has a questions file THEN read its frontmatter and apply R5a or R5a1.
R5b. IF the user chooses `regenerate` THEN discard the existing file and proceed to R7 as a first generation. IF `resync` THEN proceed under R0s–R0s7. IF `reselect` THEN proceed under R0t–R0t3. IF `cancel` THEN stop execution.
R5c. IF the output path has no existing questions file THEN proceed as a first run — R7 on a book run, R0n on a select run. Do NOT prompt.

// Recorded state
R5d. Read `kind:` from the existing file's frontmatter. It records which path wrote the file.
R5e. IF the requested run type (R0k/R0l) differs from the file's recorded `kind:` THEN stop, name both, and ask the user how to proceed.

// Concept matching — shared definitions
R5k. Match an entry to a concept by its `Concept:` field. IF an entry has no `Concept:` field THEN match on its `Tests:` field instead.
R5k1. IF R5k's field match fails THEN fall back to R12g's same-idea test against the entry's `Answer key`. IF the Answer key carries the idea THEN treat it as a match.
R5k2. R5k1 governs whether a concept MATCHES, not whether an entry is correct. Do NOT rewrite an entry on the strength of an R5k1 match alone.
R12g. IF two inventory concepts would produce questions with the same Answer key idea THEN merge them into one concept.
     // Commentary: R12g sits in the core because a select run needs its same-idea test for R0q1 matching, and R5k1 needs it for fallback matching. Its cross-unit extension R12g1 is book-only.

// Output
R24. Save the questions file next to its source:
     - Book run: `extracted/textbook/chapters/chapter<N>/questions_chapter<N>.md`
     - Book run (non-English convention): `extracted/textbook/chapters/capitulo<N>/questions_capitulo<N>.md`
     - Select run: `extracted/class/week<N>/questions_week<N>.md`
     IF the output directory does not exist THEN create it (including intermediate directories).
     Use the exact structure in the Output Format block of the loaded path file.
R24a. IF the questions file is saved AND the class root contains a `CLAUDE.md` with a `## Contents` section THEN add a one-line entry for the questions file under the appropriate group: `**extracted/textbook/**` for book runs, `**extracted/class/**` for select runs. IF the needed group header does not exist THEN create it. IF an entry for the file already exists THEN replace that line instead of duplicating.
R24a1. R24a applies identically to `practice_<arg>.md` (R24e): it gets its own Contents entry.
R24a2. IF a file this skill would have written was NOT created on this run — no constructive exercises (R24g) — THEN write no Contents entry for it.
R24b. IF the questions file is saved AND the class root contains a `CLAUDE.md` without a `## Contents` section THEN append a `## Contents` section and add the entry per R24a.
R24c. IF the class root contains no `CLAUDE.md` THEN skip R24a–R24b.
R24d. IF updating the Contents section THEN do not modify any other part of `CLAUDE.md`.

// Frontmatter and per-entry metadata
R24h. IF saving THEN write `kind: book` or `kind: select` into the frontmatter, from the run type selected by R0k/R0l.
R24i. IF saving an entry THEN write its `Concept:` field per R13f and its `Source quote:` field per R13g.

// Shared audit fact — cited by the book audit (R18b) and by the select verify (R24k4)
R18b3. IF a SELECT entry carries no `Source quote:` field THEN skip R18b for that entry.
R18b3a. IF an entry is skipped under R18b3 THEN report it.
R18b3b. IF an entry is skipped under R18b3 THEN do NOT mark it FAIL.
R18b3c. IF an entry is skipped under R18b3 THEN do NOT backfill the field.

// Mechanical verification — after saving, before reporting
R24k. IF a questions file is saved THEN apply the verifier rule for its run type before reporting the run complete.
R24k0. IF a BOOK questions file is saved THEN run `python3 <skill dir>/verify_quotes.py <output path>` in strict mode.
R24k1. IF verify_quotes.py exits non-zero THEN do NOT report the run as complete.
R24k1a. IF verify_quotes.py exits 1 and names schema or quote problems THEN fix every named problem.
R24k1b. IF every problem named under R24k1a is fixed THEN re-run verify_quotes.py.
R24k1c. IF the R24k1b re-run exits 1 THEN R24k1a applies again.
R24k2. IF a quote is genuinely present but the script cannot find it THEN fix the normalization defect in verify_quotes.py.
R24k2a. IF R24k2 applies THEN do NOT edit the quote to match the script.
R24k3. IF the script exits 2 THEN report the source or usage error exactly as printed.
R24k5. IF the user asks how to check a BOOK questions file THEN give them the strict command.
R24k5a. IF the user asks how to check a SELECT questions file THEN give them the `--legacy` command.
R24k6. IF strict mode finds an entry without an exact non-empty `Source quote:` field THEN exit 1.
R24k7. IF either mode finds a malformed question heading, a malformed or empty `Source quote:` field, zero valid entries, OR zero checked quote fragments THEN exit 1.
R24k8. IF a quote fragment has non-empty normalized text THEN verify it regardless of its character count.

// Report
R25. After saving, report errors, warnings, and a summary. Report only what the user needs to act on or verify — do not enumerate everything that went right.

R25a. ALWAYS report: (a) output file path, (b) questions saved (total and per unit), (c) verify_quotes.py result, (d) whether `CLAUDE.md` Contents was updated.

R25b. Report IF applicable — errors and warnings:
     - candidates dropped and their fail reasons
     - inventory gaps found under R12r and whether each was fixable
     - curated questions skipped with reason
     - entries skipped by R18b3 for carrying no `Source quote:`
     - any unit where an R15d–R15e question-type quota was waived under R15f
     - every RESTATEMENT UNIT identified under R13d1
     - every concept excluded under R12g1 as already covered by an earlier unit
     - on a regenerate, which select files now need a resync per R5a2
     - on a SELECT run: every UNCOVERED TOPIC under R0q2, with the locator that raised it and whether R0q3 identified a missing chapter questions file
     - on a SELECT run: any registered file that could not be opened (R0m4), any entry with no week (R0m3), any topic excluded under R0n5
     - on a resync: entries REFRESHED, entries byte-identical, entries ORPHANED — with counts and names
     - on a book run: whether visual repair ran under R4b, how many pages were repaired, and any tokens left unfixed under R4b2
     - on a book run where repair ran: the R4b5 splice back into the notes file — chapter, line range replaced, lines changed

R25c. IF a SELECT run wrote nothing under R0s7 THEN report only the output path, the pool dates, and that the file was already current.

// Catch-all
R26. IF any condition not covered by R0–R25 (including lettered sub-rules, in any of the three rule files) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Field semantics

// Note: Concept, Source quote, Tests and Audit are internal metadata — /learn never displays them. Source quote is the raw source sentence, kept so R18b can check the Teach field against it. /learn displays only Teach and Question, grades on Answer key alone, and delivers every entry in the file. Elaboration is shown only alongside Answer key after a wrong answer or a skip. Teach_EN and Question_EN are printed only when the user types `en`. Origin and Origin generated are also internal.

## Usage

```
/generate_questions chapter2     ← book run: reads extracted/textbook/chapters/chapter2/chapter2.md
                                   GENERATES audited questions, writes them next to the slice
/generate_questions week1        ← select run: reads ### Teaching entries for week 1 for coverage,
                                   COPIES matching questions out of the chapter files
                                   writes extracted/class/week1/questions_week1.md
/generate_questions wk1          ← same as week1
```

The textbook is the only thing that ever produces a question.

Order matters: run the chapters first. A select run with an empty pool stops and tells you so — it
will not fall back to generating from the slides.
