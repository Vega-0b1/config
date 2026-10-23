---
name: generate-questions
description: "Build and audit questions for /learn, with optional verified diagram attachments. A BOOK run (chapter1, ch1) analyzes the whole textbook chapter and generates at most 25 core-concept conceptual questions, with no cap override. A PROBLEMS run (chapter1 problems, lec13 problems) writes every computational exercise in the chapter's section exercise sets, or every computational problem a lecture deck prints, one checked entry per part, solving any part whose answer the source does not print. A LECTURE run (lec13, lec13_dijkstra) generates at most 25 conceptual questions from one registered lecture slide deck, capN overrides the limit. Existing files offer regenerate or cancel."
---

Build questions from a textbook chapter or from one lecture slide deck.

Three paths, selected by the argument (R0l, R0k4, R0k5):

- **Book run** — `chapter1` — GENERATES at most 25 audited conceptual questions on the chapter's
  core concepts, selected after analyzing the whole chapter.
- **Problems run** — `chapter1 problems` or `lec13 problems` — writes every computational exercise
  in the chapter's section exercise sets (not Examples, review, or problem-solving sets) or every
  computational problem the lecture deck prints, one checked entry per part, to `problems_chapter1.md` or
  `problems_<DECK ID>.md`. No cap. A part the source leaves unanswered is solved twice and kept
  when both solutions agree.
- **Lecture run** — `lec13` — GENERATES at most 25 audited conceptual questions from one registered
  lecture slide deck, written next to the deck's extracted notes. The deck is the only source.

## Rule files

This file holds the SHARED core: run-type dispatch, existing-file handling, output paths,
verification, and the report contract. The path-specific rules live beside it:

- `book.md` — Source Profile, chapter loading, visual repair, unit segmentation, concept inventory,
  curated adoption, question generation, computational problems, answer keys, translation, audit,
  constructive exercises.
- `problems.md` — problem inventory, answer source (printed or solved), problem entry fields,
  problem audit, for chapters and decks alike. It borrows loading, figure, Teach-formatting, and
  grounding rules from `book.md`, and deck resolution from `lecture.md`.
- `lecture.md` — deck resolution, slide inventory, cap, lecture frontmatter. It borrows Teach,
  inventory, generation, and audit rules from `book.md`.

Helpers sit alongside them: `verify_quotes.py` (quote verification), `verify_diagrams.py`
(optional diagram attachments), `verify_problems.py` (problem `Check:` arithmetic), and `splice_chapter.py` (R4b5 — writes a visually repaired
chapter slice back into the full textbook notes file).

R0k2 requires the matching file to be read before anything else happens. Rule IDs are global and
unique across all rule files; a rule cited by number lives in whichever file its block sits in.

## Rules — shared core

// Run type — selects which rule file loads; resolve before anything else touches a file
R0k. IF the argument normalizes to a week — `week<N>` or `wk<N>`, case-insensitively — THEN stop and tell the user: "Week runs were removed; run /generate-questions <deck> for each lecture deck." List the registered DECK IDs (lecture.md L2a).
R0l. IF the argument normalizes to a chapter under book.md R2a AND R0k4 does not apply THEN this is a BOOK run.
R0k5. IF the argument does not normalize to a week or a chapter AND carries no `problems` token THEN this is a LECTURE run. lecture.md L3 resolves the deck.
R0k5a. IF no argument is given THEN this is a BOOK run; book.md R4a lists the chapters.
R0k4. IF the argument carries a `problems` token, case-insensitively, AND the remaining argument normalizes to a chapter THEN strip the token; this is a CHAPTER PROBLEMS run.
R0k4c. IF the argument carries a `problems` token AND the remaining argument is non-empty AND does not normalize to a week or a chapter THEN strip the token; this is a DECK PROBLEMS run. lecture.md L3 resolves the deck.
     // Example: `lec13 problems` → DECK PROBLEMS run on `lec13_dijkstra`.
R0k4d. CHAPTER PROBLEMS runs and DECK PROBLEMS runs are both PROBLEMS runs. A rule that names a PROBLEMS run applies to both.
R0k4a. IF the argument carries a `problems` token AND nothing remains after stripping it THEN stop and tell the user: "Name a chapter or a deck: /generate-questions chapter<N> problems or /generate-questions <deck> problems."
R0k4b. IF a `cap<N>` token appears on a PROBLEMS run THEN ignore it; a PROBLEMS run has no cap.
R0k1a. IF the argument carries a `cap<N>` token — `cap40`, case-insensitively — THEN strip it before normalizing the run type and pass N to lecture.md L7 as the CAP. IF no `cap<N>` token is present THEN CAP stays at its L7 default.
R0k1b. IF a `cap<N>` token appears on a BOOK run THEN ignore it; the chapter limit remains fixed at 25 questions.
R0k1c. IF a LECTURE run's `cap<N>` carries a non-positive or non-integer N THEN stop and ask the user for a valid cap.
R0k2. IF the run type is resolved under R0l, R0k4, R0k4c, or R0k5 THEN Read the matching rule file from this skill's directory BEFORE applying any rule below: book run → `book.md`, chapter problems run → `book.md` AND `problems.md`, deck problems run → `book.md`, `lecture.md`, AND `problems.md`, lecture run → `book.md` AND `lecture.md`.
R0k2a. IF the matching rule file has not been read THEN no source may be loaded, no question may be generated, and no file may be saved. This file alone is not sufficient to run the skill.

// Existing-file handling
R5.  IF the output path (R24) already has a questions file THEN read its frontmatter and apply R5b.
R5b. IF R5 finds an existing questions file THEN prompt for `regenerate` or `cancel`.
R5b1. IF the reply contains exactly one operation token AND that operation is allowed by R5b THEN apply it: `regenerate` proceeds as a first generation — under R6–R7 on a BOOK or CHAPTER PROBLEMS run, under lecture.md L6 on a LECTURE run, under problems.md P2 on a DECK PROBLEMS run; `cancel` stops execution.
R5b2. IF the reply contains zero or multiple operation tokens OR names an operation disallowed for this run THEN make no file changes, repeat the run-specific prompt, and wait; R5b2 overrides R5b1.
R5c. IF the output path has no existing questions file THEN proceed as a first run — R6 on a book or chapter problems run, lecture.md L6 on a lecture run, problems.md P2 on a deck problems run. Do NOT prompt.

// Recorded state
R5d. Read `kind:` from the existing file's frontmatter. It records which path wrote the file.
R5e. IF the requested run type (R0l/R0k4/R0k4c/R0k5) differs from the file's recorded `kind:` THEN stop, name both, and ask the user how to proceed.

// Concept merging — shared definition
R12g. IF two inventory concepts would produce questions with the same Answer key idea THEN merge them into one concept.

// Output
R24. Save the questions file next to its source:
     - Book run: `extracted/textbook/chapters/chapter<N>/questions_chapter<N>.md`
     - Book run (non-English convention): `extracted/textbook/chapters/capitulo<N>/questions_capitulo<N>.md`
     - Chapter problems run: `extracted/textbook/chapters/chapter<N>/problems_chapter<N>.md`
     - Chapter problems run (non-English convention): `extracted/textbook/chapters/capitulo<N>/problems_capitulo<N>.md`
     - Lecture run: `<directory of the deck's registered file>/questions_<DECK ID>.md`
     - Deck problems run: `<directory of the deck's registered file>/problems_<DECK ID>.md`
     IF the output directory does not exist THEN create it (including intermediate directories).
     Use the exact structure in the Output Format block of the loaded path file.
R24a. IF the questions file is saved AND the class root contains a `CLAUDE.md` with a `## Contents` section THEN add a one-line entry for the questions file under the appropriate group: `**extracted/textbook/**` for book and chapter problems runs, `**extracted/class/**` for lecture and deck problems runs. IF the needed group header does not exist THEN create it. IF an entry for the file already exists THEN replace that line instead of duplicating.
R24a1. R24a applies identically to `practice_<arg>.md` (R24e): it gets its own Contents entry.
R24a2. IF a file this skill would have written was NOT created on this run — no constructive exercises (R24g) — THEN write no Contents entry for it.
R24b. IF the questions file is saved AND the class root contains a `CLAUDE.md` without a `## Contents` section THEN append a `## Contents` section and add the entry per R24a.
R24c. IF the class root contains no `CLAUDE.md` THEN skip R24a–R24b.
R24d. IF updating the Contents section THEN do not modify any other part of `CLAUDE.md`.

// Frontmatter and per-entry metadata
R24h. IF saving THEN write `kind: book`, `kind: problems`, or `kind: lecture` into the frontmatter, from the run type selected by R0l, R0k4, R0k4c, or R0k5. Both kinds of PROBLEMS run write `kind: problems`.
R24h4. IF saving THEN write `model: <model ID>` and `effort: <reasoning effort level>` into the frontmatter, recording the model and effort level used to generate the questions.
R24i. IF saving an entry THEN write its `Concept:` field per R13f and its `Source quote:` field per R13g.
R24v. IF an entry carries diagram fields THEN treat `Figure source` and `Figure quote` as internal provenance; `Diagram` is visible with the question and `Answer diagram` only with its released answer.

// Mechanical verification — after saving, before reporting
R24k. IF a questions file is saved THEN apply the verifier rule for its run type before reporting the run complete.
R24k0. IF a BOOK, PROBLEMS, or LECTURE file is saved THEN run `python3 <skill dir>/verify_quotes.py <output path>` in strict mode.
R24k1. IF verify_quotes.py exits non-zero THEN do NOT report the run as complete.
R24k1a. IF verify_quotes.py exits 1 and names schema or quote problems THEN fix every named problem.
R24k1b. IF every problem named under R24k1a is fixed THEN re-run verify_quotes.py.
R24k1c. IF the R24k1b re-run exits 1 THEN R24k1a applies again.
R24k2. IF a quote is genuinely present but the script cannot find it THEN fix the normalization defect in verify_quotes.py.
R24k2a. IF R24k2 applies THEN do NOT edit the quote to match the script.
R24k3. IF the script exits 2 THEN report the source or usage error exactly as printed.
R24k5. IF the user asks how to check a questions file THEN give them the strict command.
R24k6. IF strict mode finds an entry without an exact non-empty `Source quote:` field THEN exit 1.
R24k7. IF either mode finds a malformed question heading, a malformed or empty `Source quote:` field, zero valid entries, OR zero checked quote fragments THEN exit 1.
R24k8. IF a quote fragment has non-empty normalized text THEN verify it regardless of its character count.
R24k9. IF a saved BOOK file carries `Diagram`, `Answer diagram`, `Figure source`, or `Figure quote` THEN run `python3 <skill dir>/verify_diagrams.py <output path>` in addition to its existing quote verifier.
R24k10. IF the diagram verifier fails THEN fix the reported attachment or provenance error and rerun it before reporting completion; do not remove required diagrams to make a dependent question pass.
R24k11. IF R24k9 applies THEN report the diagram verifier result and the number of question and answer images attached.
R24k12. IF a saved BOOK or PROBLEMS file carries any `Type: problem` entry THEN run `python3 <skill dir>/verify_problems.py <output path>` in addition to its quote verifier.
R24k13. IF verify_problems.py exits 1 on a PROBLEMS file THEN re-solve each named entry under R18c and correct whichever of `Answer key`, `Elaboration`, or `Check` the re-solve shows is wrong, then re-run it.
R24k13a. Do NOT change a `Check:` or `Answer key:` value only to make the two agree. IF the R18c re-solve cannot confirm a value THEN drop the entry under P4b.
R24k13b. IF verify_problems.py reports that a curated problem's value is not the printed answer THEN R18c2 applies to that entry.
R24k15. IF verify_problems.py exits 2 THEN report the error exactly as printed.
R24k16. IF verify_problems.py exits non-zero after R24k13 THEN do NOT report the run as complete.

// Report
R25. After saving, report errors, warnings, and a summary. Report only what the user needs to act on or verify — do not enumerate everything that went right.

R25a. ALWAYS report: (a) output file path, (b) questions saved (total and per unit), (c) verify_quotes.py result, (d) whether `CLAUDE.md` Contents was updated, (e) on a PROBLEMS run, entries saved, split into curated and solved, (f) verify_problems.py result when R24k12 applies, including how many entries carry `Check: none`.

R25b. Report IF applicable — errors and warnings:
     - candidates dropped and their fail reasons
     - inventory gaps found under R12r and whether each was fixable
     - curated questions skipped with reason
     - any unit where an R15d–R15e question-type quota was waived under R15f
     - every RESTATEMENT UNIT identified under R13d1
     - every concept excluded under R12g1 as already covered by an earlier unit
     - on a LECTURE run: everything lecture.md L11 names
     - on a DECK PROBLEMS run: the deck resolved and its file, the slide count, and every slide excluded as chrome under L5c (as a slide-number list)
     - on a book or chapter problems run: whether the R6a figure pass ran, how many figures it verified, and the R9o1 figures it left unchecked
     - on a problems run: every part skipped under P2b–P2c, with its locator and reason
     - on a problems run: every entry dropped under P3d, P3e, or P4b, with its locator and fail reason
     - on a book or chapter problems run: whether visual repair ran under R4b, how many pages were repaired, and any tokens left unfixed under R4b2
     - on a book or chapter problems run where repair ran: the R4b5 splice back into the notes file — chapter, line range replaced, lines changed

R25d. IF reporting a BOOK or LECTURE run THEN do not list concepts or topics omitted from its question set; this overrides topic-omission reporting in R25b, R9h, R12g1, R12s, and R13d1, but not verification errors or source-repair warnings.

// Catch-all
R26. IF any condition not covered by R0–R25 (including lettered sub-rules, in any rule file) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Field semantics

// Note: Type and Check are internal metadata as well: Type marks a problem entry, and Check is read only by verify_problems.py. A problem's Legend holds its given values, which /learn shows as a 📋 Given block.
// Note: Concept, Source quote, Tests, Audit, Teach_EN, Question_EN, and Origin are internal metadata — /learn never displays them. Source quote is the raw source sentence, kept so R18b can check Teach against it. /learn displays Teach and Question, never grades responses, and releases Answer key plus optional Elaboration together after an answer request or attempted answer. Translation fields remain internal unless /learn later adds an explicit translation mode.

## Usage

```
/generate-questions chapter2     ← book run: reads extracted/textbook/chapters/chapter2/chapter2.md
                                   first runs /extract diagrams-only chapter2 if any figure is
                                   unchecked (R6), then GENERATES up to 25 conceptual questions
                                   next to the slice
/generate-questions chapter2 problems ← problems run: every computational exercise in chapter 2's
                                   section exercise sets, one checked entry per part, written to problems_chapter2.md
/generate-questions lec13        ← lecture run: resolves the registered deck lec13_dijkstra,
                                   GENERATES up to 25 conceptual questions from its slides, writes
                                   questions_lec13_dijkstra.md next to the deck's notes
/generate-questions lec13 cap10  ← lecture run capped at 10 questions
/generate-questions lec13 problems ← problems run on a deck: every computational exercise and
                                   worked example on its slides, one checked entry per part,
                                   written to problems_lec13_dijkstra.md next to the deck's notes
```

Register a deck with `/updateclass` before its lecture or problems run; a deck in `source/` or `Downloads/` is
not in the registry.
