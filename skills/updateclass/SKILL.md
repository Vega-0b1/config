---
name: updateclass
description: Update an existing class directory after new material arrives. Week-named folders are imported as teaching material without prompts; loose files are classified as teaching material, textbook, course scope, or misc material.
---

Update an existing class directory with newly added material.

`/addclass` scaffolds a class once. `/updateclass` imports later material. A new folder named
`wk<N>` or `week<N>` is a teaching-material batch for that week. The folder name supplies the
week, so no file in that folder needs a classification or chapter prompt. Loose files are the
exception path and receive a classification prompt.

Only textbook material creates questions. Week material tells `/generate-questions week<N>` what
the professor covered; that skill reads the week's extracted material and automatically matches its
topics to the existing textbook question pool. `/updateclass` never asks the user to map material
to a textbook chapter.

## Rules

// Target resolution
R1.  Target = cwd.
R2.  IF cwd contains no `CLAUDE.md` THEN stop and tell the user to run `/addclass` first.
R3.  IF cwd's basename is `source`, `extracted`, `code`, or `images` THEN stop and tell the user to run from the class root.

// New-file detection
R4. Enumerate loose files and directories directly in the class root, plus files directly inside `source/`, `code/`, and `extracted/`.
R5. Exclude `CLAUDE.md`, `README.md`, dotfiles, lock files, `source/`, `code/`, `extracted/`, `questions_*.md`, and `practice_*.md` from candidates.
R6. Exclude every path under `extracted/textbook/`, `extracted/class/`, and `extracted/images/` from candidates.
R7. A candidate is NEW IF neither its literal path relative to the class root nor its basename appears in the `## Contents` section of `CLAUDE.md`.
R8. IF `## Contents` contains `Nothing here yet` THEN treat every candidate as NEW.
R9. IF no candidate is NEW THEN report that the class is already up to date and stop.
R10. Treat a NEW directory as one candidate.
R11. A WEEK FOLDER is a NEW directory whose basename matches `wk<N>` or `week<N>`, case-insensitively, where `<N>` is a positive integer.
R12. IF a candidate is a WEEK FOLDER THEN normalize it to `week<N>`, preserving only its integer N.
R13. A NEW candidate that is not a WEEK FOLDER is a LOOSE CANDIDATE.

// Week-folder intake
R14. IF a candidate is a WEEK FOLDER THEN classify the entire folder as teaching material for its normalized week.
R15. IF a candidate is a WEEK FOLDER THEN do NOT ask the user for its classification, week, or textbook chapter.
R16. IF a WEEK FOLDER contains extractable documents THEN invoke `/extract <folder>` once with output to `extracted/class/week<N>/`.
R17. IF `/extract` stops for a WEEK FOLDER THEN leave every affected file unregistered, continue with the remaining candidates, and report the stop.
R18. IF a WEEK FOLDER contains code or image files THEN copy those files to `extracted/class/week<N>/`, preserving their paths relative to the WEEK FOLDER. Do NOT extract them.
R19. IF R16 succeeds OR the WEEK FOLDER contains no extractable document THEN move every residual raw code or image file from the WEEK FOLDER to `source/<folder>/`, preserving its path relative to the WEEK FOLDER.
R20. IF R19 leaves the original WEEK FOLDER empty THEN remove that empty directory.
R21. IF a WEEK FOLDER contains no extractable documents, code, or images THEN stop, name the folder, and ask the user how to handle it.

// Loose-candidate classification
R22. IF a LOOSE CANDIDATE exists THEN print the full numbered list of LOOSE CANDIDATES once, then prompt for exactly one candidate at a time in list order.
R23. Ask `what is this? (y/t/c/m)` for each LOOSE CANDIDATE.
R24. Print this legend with every R23 prompt:
     `y = teaching material from the professor`
     `t = textbook`
     `c = course scope, such as a syllabus or schedule`
     `m = misc class material`
R25. Accept exactly one case-insensitive `y`, `t`, `c`, or `m`. IF the reply is any other token THEN re-ask about the same candidate.
R26. IF a LOOSE CANDIDATE is answered `y` THEN ask `Which week is this from? — positive number, or n` before processing another candidate.
R27. Accept a positive integer or `n` for R26. IF the reply is anything else THEN re-ask.
R28. IF the R26 reply is a positive integer THEN classify the candidate as teaching material for `week<N>`.
R29. IF the R26 reply is `n` THEN classify the candidate as unassigned teaching material.
R30. IF a LOOSE CANDIDATE is answered `t`, `c`, or `m` THEN do NOT ask for a week.
R31. Do NOT infer a LOOSE CANDIDATE's classification or week from its filename, extension, location, lecture number, or modification time.

// Loose-candidate processing
R32. IF a loose document is teaching material for `week<N>` THEN invoke `/extract <candidate>` with output to `extracted/class/week<N>/`.
R33. IF a loose document is unassigned teaching material THEN invoke `/extract <candidate>` with output to `extracted/class/unassigned/`.
R34. IF a loose document is a textbook THEN invoke `/extract <candidate>` with output to `extracted/textbook/`.
R35. IF a loose document is course scope THEN invoke `/extract <candidate>` with output to `extracted/`.
R36. IF a loose document is misc material THEN invoke `/extract <candidate>` with output to `extracted/class/misc/`.
R37. Invoke `/extract` once per loose document and name that document explicitly.
R38. IF `/extract` stops for a loose document THEN leave that document unregistered, continue with the remaining candidates, and report the stop.
R39. IF a loose code or image file is teaching material for `week<N>` THEN copy it to `extracted/class/week<N>/` and move its original to `source/`.
R40. IF a loose code or image file is unassigned teaching material THEN copy it to `extracted/class/unassigned/` and move its original to `source/`.
R41. IF a loose code or image file is misc material THEN copy it to `extracted/class/misc/` and move its original to `source/`.
R42. IF a loose code or image file is a textbook or course-scope candidate THEN stop, name the file, and ask the user how to handle it.
R43. IF a loose candidate is neither a document, code file, nor image file THEN move it to `source/` after its classification.

// Registry
R44. IF at least one teaching or course-scope file was successfully processed THEN ensure `CLAUDE.md` contains an `## Instructor Material` section immediately after `## Contents`, or append it at end of file when `## Contents` is absent.
R45. IF a teaching file was successfully processed for `week<N>` THEN write it under `### Teaching` as ``- `<path>` — week <N> — <kind and extent>``.
R46. IF an unassigned teaching file was successfully processed THEN write it under `### Teaching` as ``- `<path>` — unassigned — <kind and extent>``.
R47. IF a course-scope file was successfully processed THEN write it under `### Course Scope` as ``- `<path>` — <kind and extent>``.
R48. IF a registry entry for the same path already exists THEN replace that entry.
R49. Do NOT add a textbook or misc-material registry entry.
R50. Do NOT record a chapter number or inferred chapter mapping in `## Instructor Material`.

// Contents and textbook state
R51. Add a one-line entry for every successfully processed NEW candidate under its `**<dir>/**` group in `## Contents`.
R52. Every R51 entry MUST begin with the candidate's literal name in backticks.
R53. IF `/extract` already added a Contents entry for an output or moved source file THEN do NOT add a duplicate.
R54. IF a textbook was successfully extracted AND `## Source Profile` has no `Notes file:` field THEN set `Notes file:` to its full extracted-notes path.
R55. IF a textbook was successfully extracted AND `Notes file:` names a different file THEN report the conflict and ask the user how to proceed. STOP until the user responds.
R56. Do NOT modify `CLAUDE.md` outside `## Contents`, `## Instructor Material`, and `## Source Profile`'s `Notes file:` field.

// Study-list state
R57. IF a week gained at least one teaching entry AND `extracted/class/week<N>/questions_week<N>.md` exists THEN mark that questions file STALE.
R58. IF a questions file is STALE THEN report its path and say `/generate-questions week<N>` with `reselect` rebuilds it from the new week material.
R59. Do NOT invoke `/generate-questions` automatically.
R60. IF a week gained its first teaching entry and its questions file does not exist THEN report that `/generate-questions week<N>` creates its study list.
R61. IF R58 or R60 names a week AND no chapter questions file exists under `extracted/textbook/chapters/` THEN report that the textbook pool is empty and `/generate-questions chapter<N>` must run first.

// Report
R62. Report the NEW candidates, each detected WEEK FOLDER and normalized week, each loose-file classification, files extracted or copied and their destinations, files moved to `source/`, every unassigned teaching file, every extraction stop, registry and Contents changes, Notes-file conflicts, and stale or newly available study lists.
R63. IF a WEEK FOLDER was imported THEN state that `/generate-questions week<N>` will infer coverage from the week's contents and the textbook question pool without a chapter-mapping prompt.

// Catch-all
R64. IF any condition not covered by R1–R63 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Instructor Material Format

```markdown
## Instructor Material

### Teaching

- `extracted/class/week1/wk1_notes.md` — week 1 — pdf, 42 pages
- `extracted/class/week1/demo.py` — week 1 — code, read directly
- `extracted/class/unassigned/guest_lecture_notes.md` — unassigned — pdf, 8 pages

### Course Scope

- `extracted/syllabus_notes.md` — pdf, 5 pages
```

Teaching lines contain a backtick-quoted path relative to the class root, the normalized week or
`unassigned`, and the source kind with its extent. Course-scope lines contain the path and source
kind only. `/generate-questions` reads only Teaching lines with a numbered week.

## Usage

```
/updateclass          ← run from the class root after dropping in new material
```

Drop weekly material in `wk1/`, `week2/`, or another recognized week folder, then run
`/updateclass`. It extracts documents into the corresponding `extracted/class/week<N>/` directory,
records that week, and asks no classification or chapter question. A loose textbook, syllabus, or
other file receives the `y/t/c/m` prompt.

Run `/generate-questions chapter<N>` on textbook chapters before running a week. Then
`/generate-questions week<N>` reads the week's material, infers what it covers, and selects only
the matching textbook questions.

Loose-file classifications and destinations:

```
y  teaching material  → extracted/class/week<N>/      → SELECTS what goes in questions_week<N>.md
t  textbook           → extracted/textbook/           → BECOMES questions_chapter<N>.md
c  course scope       → extracted/                    → becomes a notice, never a question
m  misc class material→ extracted/class/misc/         → searchable, never a question
```

Only `t` ever becomes a question. Week folders and loose `y` material decide which textbook
questions each week gets.
