---
name: updateclass
description: Update an existing class directory after new material arrives. Lecture slide decks (.ppt/.pptx) go to one lectures folder without prompts; other files are classified as teaching material, textbook, course scope, or misc material. No week bookkeeping.
---

Update an existing class directory with newly added material.

`/addclass` scaffolds a class once. `/updateclass` imports later material. A `.ppt` or `.pptx`
file is a lecture deck: it is extracted into `extracted/class/lectures/` without a prompt. Every
other file receives a classification prompt. Nothing is filed by week.

Textbook chapters and registered lecture slide decks create questions. Each registered deck is a
source for `/generate-questions <deck>`; handouts, specs, labs and code are registered but never
generate questions. `/updateclass` never asks the user to map material to a textbook chapter.

## Rules

// Target resolution
R1.  Target = cwd.
R2.  IF cwd contains no `CLAUDE.md` THEN stop and tell the user to run `/addclass` first.
R3.  IF cwd's basename is `source`, `extracted`, `code`, or `images` THEN stop and tell the user to run from the class root.

// New-file detection
R4. Enumerate loose files and directories directly in the class root, plus files directly inside `source/`, `code/`, and `extracted/`.
R5. Exclude `CLAUDE.md`, `README.md`, dotfiles, lock files, `source/`, `code/`, `extracted/`, `questions_*.md`, and `practice_*.md` from candidates.
R6. Exclude every path under `extracted/textbook/`, `extracted/class/`, and `extracted/images/` from candidates.
R7. IF a candidate's exact class-root-relative path is absent from `## Contents` THEN treat it as NEW; resolve a basename-only Contents entry under its directory group before comparison, and never match a basename across different directories.
R8. IF `## Contents` contains `Nothing here yet` THEN treat every candidate as NEW.
R9. IF no candidate is NEW THEN report that the class is already up to date and stop.
R10. IF a NEW directory is found THEN treat each file inside it, at any depth, as its own candidate. Do NOT ask about the directory itself.
R11. A DECK CANDIDATE is a NEW candidate whose extension is `.ppt` or `.pptx`, case-insensitively.
R11a. IF a `.ppt` and a `.pptx` with the same stem are both NEW in the same directory THEN they are ONE deck candidate; extract the `.pptx`.
R12. A NEW candidate that is not a DECK CANDIDATE is a LOOSE CANDIDATE.

// Deck intake
R14. IF a candidate is a DECK CANDIDATE THEN classify it as a lecture deck. Do NOT ask the user for its classification, week, or textbook chapter. R14 overrides R31.
R16. IF a candidate is a lecture deck THEN invoke `/extract <candidate>` with output to `extracted/class/lectures/`.
R17. IF `/extract` stops for a deck THEN leave it unregistered, continue with the remaining candidates, and report the stop.
R19. IF R16 succeeds THEN move the deck's raw file(s) to `source/lectures/`.

// Loose-candidate classification
R22. IF a LOOSE CANDIDATE exists THEN print the full numbered list of LOOSE CANDIDATES once, then prompt for exactly one candidate at a time in list order.
R23. Ask `what is this? (y/t/c/m)` for each LOOSE CANDIDATE.
R24. Print this legend with every R23 prompt:
     `y = teaching material from the professor (not a slide deck)`
     `t = textbook`
     `c = course scope, such as a syllabus or schedule`
     `m = misc class material`
R25. Accept exactly one case-insensitive `y`, `t`, `c`, or `m`. IF the reply is any other token THEN re-ask about the same candidate.
R30. Do NOT ask for a week.
R31. Do NOT infer a LOOSE CANDIDATE's classification from its filename, extension, location, lecture number, or modification time.

// Loose-candidate processing
R32. IF a loose document is teaching material THEN invoke `/extract <candidate>` with output to `extracted/class/other/`.
R34. IF a loose document is a textbook THEN invoke `/extract <candidate>` with output to `extracted/textbook/`.
R35. IF a loose document is course scope THEN invoke `/extract <candidate>` with output to `extracted/`.
R36. IF a loose document is misc material THEN invoke `/extract <candidate>` with output to `extracted/class/misc/`.
R37. Invoke `/extract` once per document and name that document explicitly.
R38. IF `/extract` stops for a loose document THEN leave that document unregistered, continue with the remaining candidates, and report the stop.
R38a. IF a teaching document was extracted THEN move its raw file to `source/other/`.
R39. IF a loose code or image file is teaching material THEN copy it to `extracted/class/other/` and move its original to `source/other/`.
R41. IF a loose code or image file is misc material THEN copy it to `extracted/class/misc/` and move its original to `source/`.
R42. IF a loose code or image file is a textbook or course-scope candidate THEN stop, name the file, and ask the user how to handle it.
R43. IF a loose candidate is neither a document, code file, nor image file THEN move it to `source/` after its classification.
R43a. IF moving files out of a NEW directory leaves it empty THEN remove that empty directory.

// Registry
R44. IF at least one teaching or course-scope file was successfully processed THEN ensure `CLAUDE.md` contains an `## Instructor Material` section immediately after `## Contents`, or append it at end of file when `## Contents` is absent.
R45. IF a lecture deck or teaching file was successfully processed THEN write it under `### Teaching` as ``- `<path>` — <kind and extent>``.
R47. IF a course-scope file was successfully processed THEN write it under `### Course Scope` as ``- `<path>` — <kind and extent>``.
R48. IF a registry entry for the same path already exists THEN replace that entry.
R49. Do NOT add a textbook or misc-material registry entry.
R50. Do NOT record a chapter number or inferred chapter mapping in `## Instructor Material`.

// Contents and textbook state
R51. Add a one-line entry for every successfully processed NEW candidate under its `**<dir>/**` group in `## Contents`.
R52. IF writing an R51 entry THEN record each processed file's exact class-root-relative path in backticks, including files from a NEW directory; a folder summary does not replace its file inventory.
R53. IF `/extract` already added a Contents entry for an output or moved source file THEN do NOT add a duplicate.
R54. IF a textbook was successfully extracted AND `## Source Profile` has no `Notes file:` field THEN set `Notes file:` to its full extracted-notes path.
R55. IF a textbook was successfully extracted AND `Notes file:` names a different file THEN report the conflict and ask the user how to proceed. STOP until the user responds.
R56. IF updating `CLAUDE.md` THEN limit changes to `## Contents`, `## Instructor Material`, `## Source Profile`'s `Notes file:` field, and the scan/OCR provenance required by extract R11j in `## Source Profile`.

// Lecture-deck state
R57. IF a processed teaching file holds one or more deck headings (generate-questions lecture.md L2) THEN list each DECK ID (L2a) it holds.
R58. IF a listed deck's `questions_<DECK ID>.md` already exists beside its file THEN mark that questions file STALE and report that `/generate-questions <DECK ID>` with `regenerate` rebuilds it.
R59. Do NOT invoke `/generate-questions` automatically.
R60. IF a listed deck has no questions file THEN report that `/generate-questions <DECK ID>` creates its study list.

// Report
R62. Report the NEW candidates, each lecture deck, each loose-file classification, files extracted or copied and their destinations, files moved to `source/`, every extraction stop, registry and Contents changes, Notes-file conflicts, and the decks listed under R57–R60.

// Catch-all
R64. IF any condition not covered by R1–R62 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Instructor Material Format

```markdown
## Instructor Material

### Teaching

- `extracted/class/lectures/lec13_dijkstra_notes.md` — pptx, 14 slides
- `extracted/class/other/hw_1_1_notes.md` — pdf, 1 page
- `extracted/class/other/demo.py` — code, read directly

### Course Scope

- `extracted/syllabus_notes.md` — pdf, 5 pages
```

Teaching lines contain a backtick-quoted path relative to the class root and the source kind with
its extent. Course-scope lines have the same shape. `/generate-questions <deck>` searches every
Teaching line for slide decks.

## Usage

```
/updateclass          ← run from the class root after dropping in new material
```

Drop new files (or a folder of them) in the class root and run `/updateclass`. Every `.ppt`/`.pptx`
is extracted into `extracted/class/lectures/` with no question asked, and its raw file goes to
`source/lectures/`. Every other file receives the `y/t/c/m` prompt. Then run
`/generate-questions <deck>` for each new deck the report lists.

```
deck (.ppt/.pptx)     → extracted/class/lectures/     → BECOMES questions_<deck>.md
y  teaching material  → extracted/class/other/        → registered, never a question
t  textbook           → extracted/textbook/           → BECOMES questions_chapter<N>.md
c  course scope       → extracted/                    → becomes a notice, never a question
m  misc class material→ extracted/class/misc/         → searchable, never a question
```
