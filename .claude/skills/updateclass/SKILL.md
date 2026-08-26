---
name: updateclass
description: Bring an already-scaffolded class directory up to date with material added since it was created. Detects new files and asks, per file, whether it is teaching material (y), textbook (t), course scope (c), or misc class material (m). Extracts documents via /extract, places them in the correct subdirectory (extracted/class/week<N>/, extracted/textbook/, extracted/, or extracted/class/misc/), and records teaching files against the WEEK they were taught. The week is what makes the file reachable: /generate_questions week<N> reads the material registered to that week to see which topics it covered, then selects the matching questions out of the textbook chapter files, and /learn week<N> drills them. Run this whenever slides, handouts, labs, exams, textbooks, or a syllabus land in a class folder.
---

Update an existing class directory with newly added material.

`/addclass` scaffolds a class once. `/updateclass` is its ongoing counterpart: run it whenever new material arrives. Its job is to get those files classified, extracted, and placed in the right directory — and for teaching material, to record which week it belongs to.

Every file that lands in a class directory is one of four things:

- **Teaching material (`y`)** — slides, handouts, labs the professor gave. Goes to `extracted/class/week<N>/`. Registered under `### Teaching` so `/generate_questions week<N>` can read it for coverage. It is never a question source — it decides which textbook questions that week gets.
- **Textbook (`t`)** — the course textbook or reference book. Goes to `extracted/textbook/`. Not registered — `/generate_questions chapter<N>` finds it via `## Source Profile`. This is the only thing questions are ever made from.
- **Course scope (`c`)** — syllabus, schedule. Goes to `extracted/`. Registered under `### Course Scope` so `/learn` can tell you which chapters are out of scope.
- **Misc (`m`)** — setup docs, install guides, VM manuals, tool instructions. Goes to `extracted/class/misc/`. Extracted and searchable but never fed to `/generate_questions`.

## Rules

// Target resolution
R1.  Target = cwd.
R2.  IF cwd contains no `CLAUDE.md` THEN stop and tell the user to run `/addclass` first.
R3.  IF cwd's basename is `source`, `extracted`, `code`, or `images` THEN stop and tell the user to run from the class root.

// New-file detection
R4.  Enumerate candidate files: every loose file and directory in the class root, plus every file directly inside `source/`, `code/`, and `extracted/`. Do NOT recurse into `extracted/textbook/` or `extracted/class/`.
R5.  A candidate is NEW IF its basename does not appear in the `## Contents` section of `CLAUDE.md`.
R6.  IF `## Contents` reads `Nothing here yet` (the `/addclass` R18c placeholder) THEN treat the inventory as empty and every candidate as NEW.
R7.  Exclude from candidates: `CLAUDE.md`, `README.md`, dotfiles, lock files, `extracted/images/`, `extracted/textbook/`, `extracted/class/`, and the skill chain's own output — `questions_*.md` and `practice_*.md`.
R8.  IF no candidate is NEW THEN report that the class is already up to date and stop.
R9.  Treat a NEW directory (e.g. `wk4/`) as one candidate, not as one candidate per file inside it.
R9a. IF two NEW candidates share a basename and differ only as a legacy/modern pair (`.ppt`/`.pptx`, `.doc`/`.docx`, `.xls`/`.xlsx`) THEN treat them as ONE candidate.
R9b. Before prompting, check each NEW document candidate's format. Note on its R11 line when it is a legacy binary that `/extract` will convert.

// Classification prompt
R10. IF exactly one candidate is NEW THEN print its name and ask: `what is this? (y/t/c/m)`. STOP until the user responds.
R11. IF more than one candidate is NEW THEN print the full numbered list once for context, then ask about the FIRST candidate alone. STOP until the user responds.
R11a. Print the legend with every prompt:
     `y = teaching material from the professor (slides, handout, lab)`
     `t = textbook`
     `c = course scope (syllabus, schedule)`
     `m = misc class material (setup docs, install guides)`
R11b. Ask about exactly one candidate per turn, in list order.
R11c. IF a candidate has been answered THEN ask about the next one immediately. Do NOT ask whether to continue.
R12. Accept a single `y`, `t`, `c`, or `m` case-insensitively, and nothing else. IF the reply is any other token THEN re-ask about the same candidate.
R13. `y` = teaching material. `t` = textbook. `c` = course scope. `m` = misc class material.
R13a. `y` and `c` are different kinds of instructor material and are NOT interchangeable. A syllabus names the topic of an entire TERM without teaching any of it. Registering it as `y` would feed it to /generate_questions R0m as coverage, and R0n2 admits a topic on the strength of it being NAMED — so a single syllabus registered to week 1 would claim the whole course as week 1's coverage and pull the entire question pool into one study list.

// Week prompt — asked per `y` candidate, immediately after its classification
R13b. IF a candidate was answered `y` THEN ask which week of the course it is from, before moving to the next candidate. STOP until the user responds.
R13b1. Accept a positive integer, or `n` meaning the week does not matter. IF the reply is anything else THEN re-ask.
R13b2. The week prompt carries no hint. Ask it plainly: `Which week is this from? — number, or n`.
R13b3. IF the answer is `n` THEN the file goes to `extracted/class/unassigned/` and gets no `week:` value in the registry. An entry with no week is reachable by NO `/generate_questions` run. Report it as unreachable.
R13b4. Do NOT ask the week for candidates answered `t`, `c`, or `m`.
R13b5. Do NOT infer the week from a filename, a lecture number, or a file's mtime.

R14. Do NOT infer classification from a filename, extension, or location.

// Sorting
R15. IF a NEW candidate is a document THEN do NOT move it. Leave it in place for R17.
     // Commentary: `/extract` R17–R18 move their own inputs into `source/` after a successful write.
R16. IF a NEW candidate is not a document THEN sort it: code to `code/`, raw material to `source/`.

// Extraction
R17. IF a NEW candidate is a document AND was answered `y` THEN invoke `/extract <candidate>` with output to `extracted/class/week<N>/`, where `<N>` is the week from R13b. IF the week was `n` THEN output to `extracted/class/unassigned/`.
R17a. IF answered `t` THEN invoke `/extract <candidate>` with output to `extracted/textbook/`.
R17b. IF answered `c` THEN invoke `/extract <candidate>` with output to `extracted/`.
R17c. IF answered `m` THEN invoke `/extract <candidate>` with output to `extracted/class/misc/`.
R18. Invoke `/extract` once per candidate, naming that candidate explicitly. Do NOT invoke it with no argument.
R19. This skill contains no extraction logic. All format handling belongs to `/extract`.
R20. IF `/extract` stops for any reason THEN leave that candidate unregistered, continue with the remaining candidates, and report the stop.
R21. IF a NEW candidate is code or an image AND the answer was `y` THEN copy it to `extracted/class/week<N>/` (or `extracted/class/unassigned/` if week was `n`) and register it by its destination path. Do NOT extract it.
R21a. IF a NEW candidate is code or an image AND the answer was `m` THEN copy it to `extracted/class/misc/`. Do NOT extract it.

// Chapter mapping
R22. IF a candidate was answered `y` THEN determine which chapter it covers, per R23–R25. IF answered `c` THEN determine the course's chapter scope, per R26a–R26d.
R22a. IF answered `t` or `m` THEN skip chapter mapping entirely.
R23. Read the primary notes file named by the `Notes file:` field of the `## Source Profile` in `CLAUDE.md`, and collect its chapter headings.
R24. Compare the candidate's extracted content against those chapter headings. Propose the best-matching chapter for each `y` candidate, display every proposal, and ask the user to confirm or correct. STOP until the user responds.
R25. IF `CLAUDE.md` has no `## Source Profile`, or its `Notes file` does not exist, THEN ask the user which chapter each `y` candidate covers. STOP until the user responds.
R26. A mapping value may name something other than a chapter (`wk10`, `midterm`, `lab3`). Record whatever the user confirms, verbatim.
R26a. IF answered `c` THEN locate the section listing topics against weeks or dates — `Topics`, `Schedule`, `Course Outline`, `Calendar`, or `Tentative Schedule`.
R26b. Map each listed topic to the chapters collected in R23. Produce two sets: chapters IN scope and chapters NOT in scope.
R26c. Display both sets and ask the user to confirm or correct them. STOP until the user responds.
R26d. IF no schedule section can be located THEN do NOT guess a scope. Say so and ask the user which chapters the course covers. STOP until they respond.
R26e. Do NOT derive scope from a `y` candidate.

// Registry write
R27. IF at least one candidate was answered `y` or `c` THEN write its confirmed mapping to the `## Instructor Material` section of `CLAUDE.md`. IF the section does not exist THEN create it immediately after `## Contents`, or at end of file.
R27a. Write `y` entries under a `### Teaching` subheading and `c` entries under a `### Course Scope` subheading.
R27b. IF a week was given under R13b THEN record it on the entry as `week <N>`. IF the answer was `n` THEN omit the field entirely.
R28. IF an entry for the same path already exists THEN replace that line.
R29. Do NOT write a registry entry for candidates answered `t` or `m`.

// Contents update
R30. Add a one-line entry for every NEW candidate that was sorted or extracted, under its `**<dir>/**` group header in `## Contents`. Every entry MUST lead with the file's literal name in backticks.
R30a. IF an existing `## Contents` entry names a file in prose rather than in backticks AND this run identified that file THEN rewrite that entry to lead with the literal filename.
R31. IF `/extract` already added an entry for a file THEN do not add a second one.
R32. Do NOT modify any part of `CLAUDE.md` outside `## Contents` and `## Instructor Material`, except as R33a–R33e require.

// Source Profile — textbook handling
R32a. IF answered `t` AND `CLAUDE.md` has no `Notes file:` in its `## Source Profile` THEN update the `Notes file:` field.
R32b. IF answered `t` AND `CLAUDE.md` already has a `Notes file:` pointing at a different file THEN report the conflict and ask. STOP until the user responds.
// Stale questions detection
R33a. IF a WEEK gained a `### Teaching` entry in this run AND `extracted/class/week<N>/questions_week<N>.md` already exists THEN mark that questions file STALE.
R33b. IF a questions file is marked STALE THEN name it in the report and say `/generate_questions week<N>` with `reselect` will fix it.
R33c. Do NOT invoke `/generate_questions` automatically. Report the staleness and let the user choose when to run it.
R33d. IF a week gained its FIRST `### Teaching` entry AND no questions file exists for it THEN say so in the report and name `/generate_questions week<N>` as the command.
R33e. IF a week is named under R33b or R33d AND the class has NO chapter questions file under `extracted/textbook/chapters/` THEN additionally say the pool is empty and `/generate_questions chapter<N>` must run first.

// Confirm
R35. Report: candidates found and which were NEW, the y/t/c/m answer per candidate, the week recorded per `y` candidate or that it was declined, any legacy file converted by `/extract`, what was extracted and to where, what was sorted and to where, the confirmed chapter mapping per `### Teaching` entry, any entry left with no week and therefore unreachable, the confirmed in-scope and out-of-scope chapter sets per `### Course Scope` entry, any `/extract` stop, any Contents entry repaired under R30a, any questions file marked STALE, whether `## Instructor Material` and `## Contents` were updated, any Notes file conflict.
R35a. IF a `### Course Scope` entry was written THEN name the out-of-scope chapters explicitly in the report.

// Catch-all
R36. IF any condition not covered by R1–R35a (including lettered sub-rules) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Instructor Material Format

```markdown
## Instructor Material

### Teaching

- `extracted/class/week1/ch1_slides.md` — chapter 1 — week 1 — pptx, 42 slides
- `extracted/class/week6/lab2.md` — chapter 3 — week 6 — pdf, 8 pages
- `extracted/class/week4/udp_demo.py` — chapter 2 — week 4 — code, read directly
- `extracted/class/unassigned/topology_handout.png` — chapter 1 — image, read directly

### Course Scope

- `extracted/syllabus_notes.md` — covers 1, 2, 3, 4, 5, 6, 8 — not covered: 7, 9 — pdf, 5 pages
```

**Teaching** lines are: backtick-quoted path relative to the class root (always under `extracted/class/week<N>/` when a week was given, or `extracted/class/unassigned/` when it was not), an em dash, the confirmed mapping from R26, an em dash, `week <N>` from R13b when one was given, an em dash, and the source kind with its extent (slide count, page count, or `read directly` for unextracted code and images). The last example above shows an entry whose week was answered `n` — the file lands in `unassigned/` and the week field is absent.

**Course Scope** lines replace the single mapping with two chapter sets from R26c: `covers <list>` then `not covered: <list>`. These entries are never read as a question source.

## Usage

```
/updateclass          ← run from the class root after dropping in new material
```

Typical session: drop `lec1_intro.ppt`, `syllabus.pdf`, and `textbook.epub` into `~/edu/network/`,
run `/updateclass`. Answer `y` for the lecture deck (→ `extracted/class/week1/`), `c` for the
syllabus (→ `extracted/`), and `t` for the textbook (→ `extracted/textbook/`). The deck is
converted to `.pptx`, extracted with per-slide anchors, and recorded against week 1 — so
`/generate_questions week1` can read it for coverage and select the matching textbook questions,
and `/learn week1` can drill them. The syllabus is read for its schedule, producing the course's
chapter scope. The textbook is extracted and the `Notes file:` field is set in `## Source Profile`.

Order matters after this: run `/generate_questions chapter<N>` on the textbook chapters before
running any week. The week selects from those files and stops if none exist.

The four classifications and their destinations:

```
y  teaching material  → extracted/class/week<N>/      → SELECTS what goes in questions_week<N>.md
t  textbook           → extracted/textbook/           → BECOMES questions_chapter<N>.md
c  course scope       → extracted/                    → becomes a notice, never a question
m  misc class material→ extracted/class/misc/         → searchable, never a question
```

Only `t` ever becomes a question. `y` decides which of those questions each week gets.
