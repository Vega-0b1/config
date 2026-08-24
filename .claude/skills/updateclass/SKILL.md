---
name: updateclass
description: Bring an already-scaffolded class directory up to date with material added since it was created. Detects new files and asks, per file, whether it is teaching material (y), textbook (t), course scope (c), or misc class material (m). Extracts documents via /extract, places them in the correct subdirectory (extracted/class/week<N>/, extracted/textbook/, extracted/, or extracted/class/misc/), and records teaching files against the WEEK they were taught. The week is what makes the file reachable: /generate_questions week<N> generates questions from the material registered to that week, and /learn week<N> drills them. Run this whenever slides, handouts, labs, exams, textbooks, or a syllabus land in a class folder.
---

Update an existing class directory with newly added material.

`/addclass` scaffolds a class once. `/updateclass` is its ongoing counterpart: run it whenever new material arrives. Its job is to get those files classified, extracted, and placed in the right directory — and for teaching material, to record which week it belongs to.

Every file that lands in a class directory is one of four things:

- **Teaching material (`y`)** — slides, handouts, labs the professor gave. Goes to `extracted/class/week<N>/`. Registered under `### Teaching` so `/generate_questions week<N>` can reach it.
- **Textbook (`t`)** — the course textbook or reference book. Goes to `extracted/textbook/`. Not registered — `/generate_questions chapter<N>` finds it via `## Source Profile`.
- **Course scope (`c`)** — syllabus, schedule. Goes to `extracted/`. Registered under `### Course Scope` so `/learn` can tell you which chapters are out of scope.
- **Misc (`m`)** — setup docs, install guides, VM manuals, tool instructions. Goes to `extracted/class/misc/`. Extracted and searchable but never fed to `/generate_questions`.

## Rules

// Target resolution
R1.  Target = cwd.
R2.  IF cwd contains no `CLAUDE.md` THEN stop and tell the user to run `/addclass` first. Do NOT scaffold.
     // Commentary: the registry and the Contents inventory both live in `CLAUDE.md`. Without it there is nowhere to record the answers this skill collects.
R3.  IF cwd's basename is `source`, `extracted`, `code`, or `images` THEN stop and tell the user to run from the class root.

// New-file detection
R4.  Enumerate candidate files: every loose file and directory in the class root, plus every file directly inside `source/`, `code/`, and `extracted/`. Do NOT recurse into `extracted/textbook/` or `extracted/class/` — those are managed by the skill chain, not by the user dropping files in.
R5.  A candidate is NEW IF its basename does not appear in the `## Contents` section of `CLAUDE.md`.
     // Commentary: `/addclass` R18a, `/extract` R21, and `/generate_questions` R24a all maintain Contents as a living inventory. Reusing it as the seen-set means this skill needs no state file of its own.
R6.  IF `## Contents` reads `Nothing here yet` (the `/addclass` R18c placeholder) THEN treat the inventory as empty and every candidate as NEW.
R7.  Exclude from candidates: `CLAUDE.md`, `README.md`, dotfiles, lock files, the `extracted/images/` directory, the `extracted/textbook/` directory, the `extracted/class/` directory, and the skill chain's own output — `questions_*.md`, `practice_*.md`, `gaps_*.md`, and `flagged_questions_*.md`.
     // Commentary: those are written by /generate_questions and /learn. Without this exclusion the first /updateclass run in any class that has used the chain asks about its own artifacts.
R8.  IF no candidate is NEW THEN report that the class is already up to date and stop. Do not prompt.
R9.  Treat a NEW directory (e.g. `wk4/`) as one candidate, not as one candidate per file inside it.
     // Commentary: weekly folders are a single act of course delivery. Prompting per file inside one would ask the same question a dozen times.
R9a. IF two NEW candidates share a basename and differ only as a legacy/modern pair (`.ppt`/`.pptx`, `.doc`/`.docx`, `.xls`/`.xlsx`) THEN treat them as ONE candidate, listed under the modern name. Both files are handled together throughout.
     // Commentary: /extract R8a–R8f converts a legacy binary and keeps both files, so one lecture can appear twice in the R4 scan.
R9b. Before prompting, check each NEW document candidate's format. Note on its R11 line when it is a legacy binary that `/extract` will convert.

// Classification prompt
R10. IF exactly one candidate is NEW THEN print its name and ask: `what is this? (y/t/c/m)`. STOP until the user responds.
R11. IF more than one candidate is NEW THEN print the full numbered list once for context, then ask about the FIRST candidate alone. STOP until the user responds.
R11a. Print the legend with every prompt:
     `y = teaching material from the professor (slides, handout, lab)`
     `t = textbook`
     `c = course scope (syllabus, schedule)`
     `m = misc class material (setup docs, install guides)`
R11b. Ask about exactly one candidate per turn, in list order. Do NOT present the next candidate until the current one has been answered.
     // Commentary: batching the whole list into one reply forces the user to hold every filename in their head at once, and a miscounted reply invalidates the entire batch.
R11c. IF a candidate has been answered THEN ask about the next one immediately. Do NOT ask whether to continue.
R12. Accept a single `y`, `t`, `c`, or `m` case-insensitively, and nothing else. IF the reply is any other token THEN re-ask about the same candidate. STOP until the user responds. Do NOT guess.
R13. `y` = teaching material. `t` = textbook. `c` = course scope. `m` = misc class material.
R13a. `y` and `c` are different kinds of instructor material and are NOT interchangeable. A `y` candidate says what is worth knowing; a `c` candidate says which chapters are on the menu.
     // Commentary: a syllabus names the topic of an entire week without teaching any of it. Registering it as `y` would make it a question SOURCE under /generate_questions R0m, and every question generated from it would fail admissibility for want of a sentence explaining anything.

// Week prompt — asked per `y` candidate, immediately after its classification
R13b. IF a candidate was answered `y` THEN ask which week of the course it is from, before moving to the next candidate. STOP until the user responds.
R13b1. Accept a positive integer, or `n` meaning the week does not matter. IF the reply is anything else THEN re-ask the same candidate. Do NOT guess.
R13b2. The week prompt carries no hint. Ask it plainly: `Which week is this from? — number, or n`.
     // Commentary: chapter mapping is R22–R26, which runs after every candidate has been classified. The week cannot be inferred at this point.
R13b3. IF the answer is `n` THEN the file goes to `extracted/class/unassigned/` and gets no `week:` value in the registry. An entry with no week is reachable by NO `/generate_questions` run — the class path selects by week and the book path never reads class material. Report it under R35 as unreachable.
R13b4. Do NOT ask the week for candidates answered `t`, `c`, or `m`.
R13b5. Do NOT infer the week from a filename, a lecture number, or a file's mtime. R13b1's answer is the only source.
     // Commentary: lecture numbering and week numbering diverge as soon as a class meets more than once a week. mtime records when the file was downloaded, not when it was taught. A wrong week silently mis-scopes exam preparation.

R14. Do NOT infer classification from a filename, extension, or location. R13's answer is the only source.
     // Commentary: a PDF the user downloaded and a PDF the professor handed out are byte-identical in every respect this skill can observe.

// Sorting
R15. IF a NEW candidate is a document (`.pdf`, `.docx`, `.pptx`, `.epub`) THEN do NOT move it. Leave it in place for R17.
     // Commentary: `/extract` R17–R18 move their own inputs into `source/` after a successful write. Pre-moving would leave the extract call with nothing to find.
R16. IF a NEW candidate is not a document THEN sort it: code to `code/` (creating it if needed), raw material and anything ambiguous to `source/`, and leave dotfiles, lock files, unknown archives, and context-free media in place.

// Extraction
R17. IF a NEW candidate is a document AND was answered `y` THEN invoke `/extract <candidate>` with output to `extracted/class/week<N>/`, where `<N>` is the week from R13b. IF the week was `n` THEN output to `extracted/class/unassigned/`.
R17a. IF a NEW candidate is a document AND was answered `t` THEN invoke `/extract <candidate>` with output to `extracted/textbook/`.
R17b. IF a NEW candidate is a document AND was answered `c` THEN invoke `/extract <candidate>` with output to `extracted/`.
R17c. IF a NEW candidate is a document AND was answered `m` THEN invoke `/extract <candidate>` with output to `extracted/class/misc/`.
     // Commentary: each classification has exactly one output directory. `/extract` is a dumb tool — it takes a file and an output path.
R18. Invoke `/extract` once per candidate, naming that candidate explicitly. Do NOT invoke it with no argument.
     // Commentary: a bare `/extract` targets every loose file in the directory and writes them to one combined notes file, which would fuse a slide deck and a handout into a single undifferentiated extraction.
R19. This skill contains no extraction logic. All format handling — page anchors, slide anchors, image extraction, heading reconstruction — belongs to `/extract`.
R20. IF `/extract` stops for any reason (an existing output file per its R6, an unreadable source, a failed write) THEN leave that candidate unregistered, continue with the remaining candidates, and report the stop under R35.
R21. IF a NEW candidate is code or an image AND the answer was `y` THEN copy it to `extracted/class/week<N>/` (or `extracted/class/unassigned/` if week was `n`) and register it by its destination path. Do NOT extract it.
     // Commentary: `/generate_questions` opens code and image paths directly with the Read tool. Converting them to markdown would only lose fidelity.
R21a. IF a NEW candidate is code or an image AND the answer was `m` THEN copy it to `extracted/class/misc/`. Do NOT extract it.

// Chapter mapping
R22. IF a candidate was answered `y` THEN determine which chapter it covers, per R23–R25. IF a candidate was answered `c` THEN determine the course's chapter scope instead, per R26a–R26d.
R22a. IF a candidate was answered `t` or `m` THEN skip chapter mapping entirely.
     // Commentary: the textbook IS the chapter list, and misc material has no chapter affinity.
R23. Read the primary notes file named by the `Notes file:` field of the `## Source Profile` in `CLAUDE.md`, and collect its chapter headings under that profile's chapter heading pattern.
R24. Compare the candidate's extracted content against those chapter headings and their subsection titles. Propose the best-matching chapter for each `y` candidate, display every proposal as a list, and ask the user to confirm or correct it. STOP until the user responds.
     // Example: `ch1_slides.md → Chapter 1 (What Is the Internet?)` — confirm, or reply with the correct chapter.
R25. IF `CLAUDE.md` has no `## Source Profile`, or its `Notes file` does not exist, THEN do NOT propose a mapping. Ask the user which chapter each `y` candidate covers. STOP until the user responds.
     // Commentary: with no chapter list to match against, a proposal would be a guess dressed as an inference.
R26. A mapping value may name something other than a chapter (`wk10`, `midterm`, `lab3`). Record whatever the user confirms, verbatim.
R26a. IF a candidate was answered `c` THEN locate the section of its extracted content that lists topics against weeks, units, or dates — a heading matching `Topics`, `Schedule`, `Course Outline`, `Calendar`, or `Tentative Schedule`, case-insensitively.
R26b. Map each listed topic to the chapters collected in R23, by topic name against chapter title. Produce two sets: chapters IN scope and chapters NOT in scope.
     // Example: "Week 6: Transport layer" → Chapter 3 (Transport Layer). Chapters no topic maps to are out of scope.
R26c. Display both sets and ask the user to confirm or correct them. STOP until the user responds.
R26d. IF no schedule section can be located THEN do NOT guess a scope. Say so, ask the user which chapters the course covers, and STOP until they respond.
R26e. Do NOT derive scope from a `y` candidate, and do NOT derive per-chapter priority from a `c` candidate. The two kinds answer different questions.

// Registry write
R27. IF at least one candidate was answered `y` or `c` THEN write its confirmed mapping to the `## Instructor Material` section of `CLAUDE.md`, in the format given below. IF the section does not exist THEN create it immediately after `## Contents`, or at end of file when there is no Contents section.
R27a. Write `y` entries under a `### Teaching` subheading and `c` entries under a `### Course Scope` subheading. Create whichever subheading is missing.
R27b. IF a week was given under R13b THEN record it on the entry as `week <N>`. IF the answer was `n` THEN omit the field entirely.
     // Commentary: /generate_questions R0m reads only `### Teaching`, and R0m5 explicitly refuses `### Course Scope` as a source. The split is what keeps a syllabus out of the question set.
R28. IF an entry for the same path already exists THEN replace that line. Do NOT duplicate it.
R29. Do NOT write a registry entry for candidates answered `t` or `m`.
     // Commentary: textbooks are found via `## Source Profile`, not the registry. Misc material is not a question source and not a scope source.

// Contents update
R30. Add a one-line entry (`- file — description`) for every NEW candidate that was sorted or extracted, under its `**<dir>/**` group header in `## Contents`. IF a needed group header does not exist THEN create it. Every entry MUST lead with the file's literal name in backticks, per `/addclass` R18a1.
R30a. IF an existing `## Contents` entry names a file in prose rather than in backticks AND this run identified that file, THEN rewrite that entry to lead with the literal filename, preserving its description.
R31. IF `/extract` already added an entry for a file under R21 of that skill THEN do not add a second one.
R32. Do NOT modify any part of `CLAUDE.md` outside `## Contents` and `## Instructor Material`, except as R33 requires.

// Source Profile — textbook handling
R32a. IF a candidate was answered `t` AND `CLAUDE.md` has no `Notes file:` in its `## Source Profile` THEN update the `Notes file:` field to point at the extracted textbook path.
R32b. IF a candidate was answered `t` AND `CLAUDE.md` already has a `Notes file:` pointing at a different file THEN report the conflict under R35 and ask the user whether to replace it. STOP until the user responds.
     // Commentary: a class has one primary textbook. A second one is unusual enough to warrant confirmation rather than silent replacement.
R32c. Do NOT write `Anchor source`, `Generation mode`, or any other profile field. Those are obsolete.

// Stale questions detection
R33a. IF a WEEK gained a `### Teaching` entry in this run AND `extracted/class/week<N>/questions_week<N>.md` already exists THEN mark that questions file STALE.
     // Commentary: keyed to the week, not the chapter. A new deck changes what `/generate_questions week<N>` would produce; it changes nothing about the textbook chapter, which is generated from the book alone.
R33b. IF a questions file is marked STALE THEN name it in the R35 report and say that `/generate_questions week<N>` will merge the new material in without regenerating.
R33c. Do NOT invoke `/generate_questions` automatically. Report the staleness and let the user choose when to spend the run.
     // Commentary: the user may be adding four decks in one sitting. Firing a merge per registry write would run it three times for nothing.
R33d. IF a week gained its FIRST `### Teaching` entry AND no `extracted/class/week<N>/questions_week<N>.md` exists THEN say so in the R35 report and name `/generate_questions week<N>` as the run that would create it.

// Confirm
R35. Report: candidates found and which were NEW, the y/t/c/m answer per candidate, the week recorded per `y` candidate or that it was declined, any legacy file converted by `/extract` R8a, what was extracted and to where, what was sorted and to where, the confirmed chapter mapping per `### Teaching` entry, any entry left with no week and therefore unreachable (R13b3), the confirmed in-scope and out-of-scope chapter sets per `### Course Scope` entry, any `/extract` stop from R20, any Contents entry repaired under R30a, any questions file marked STALE under R33a, whether `## Instructor Material` and `## Contents` were updated, any Notes file conflict from R32b, and anything left in place under R16.
R35a. IF a `### Course Scope` entry was written THEN name the out-of-scope chapters explicitly in the report.
     // Commentary: "your course skips chapters 7 and 9" is the single most useful thing this skill can tell someone.

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
`/generate_questions week1` can generate questions from the slides and `/learn week1` can drill
them. The syllabus is read for its schedule, producing the course's chapter scope. The textbook
is extracted and the `Notes file:` field is set in `## Source Profile`.

The four classifications and their destinations:

```
y  teaching material  → extracted/class/week<N>/     → becomes questions_week<N>.md
t  textbook           → extracted/textbook/           → becomes questions_chapter<N>.md
c  course scope       → extracted/                    → becomes a notice, never a question
m  misc class material→ extracted/class/misc/         → searchable, never a question
```
