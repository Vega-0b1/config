---
name: updateclass
description: Update an existing class directory after new material arrives. Lecture slide decks (.ppt/.pptx) go to one lectures folder without prompts; other files are classified as lecture, textbook, or auto sort. Auto sort reads the content, files syllabi as course scope, and groups same-type material into collections. No week bookkeeping.
---

Update an existing class directory with newly added material.

`/addclass` scaffolds a class once. `/updateclass` imports later material. A `.ppt` or `.pptx`
file is a lecture deck: it is extracted into `extracted/class/lectures/` without a prompt. Every
other file receives a `l/t/a` prompt: lecture, textbook, or auto sort. Nothing is filed by week.

Textbook chapters and registered lecture material create questions. Each registered deck is a
source for `/generate-questions <deck>`; auto-sorted material (handouts, specs, labs, code) is
organized into collections but never generates questions. `/updateclass` never asks the user to map material to a textbook chapter.

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
R23. Ask `what is this? (l/t/a)` for each LOOSE CANDIDATE.
R24. Print this legend with every R23 prompt:
     `l = lecture material from the professor`
     `t = textbook`
     `a = auto sort: read the content and organize it`
R25. Accept exactly one case-insensitive `l`, `t`, or `a`. IF the reply is any other token THEN re-ask about the same candidate.
R30. Do NOT ask for a week.
R31. Do NOT infer a LOOSE CANDIDATE's `l/t/a` answer from its filename, extension, location, lecture number, or modification time.
     // Commentary: R31 governs the prompt only. Auto sort (R36–R36i) reads content after the user answers `a`.

// Lecture and textbook processing
R32. IF a loose document is lecture material THEN invoke `/extract <candidate>` with output to `extracted/class/lectures/` AND move its raw file to `source/lectures/`.
R33. IF a loose code or image file is lecture material THEN copy it to `extracted/class/lectures/` AND move its original to `source/lectures/`.
R34. IF a loose document is a textbook THEN invoke `/extract <candidate>` with output to `extracted/textbook/`.
R34a. IF a loose code or image file is a textbook candidate THEN stop, name the file, and ask the user how to handle it.
R35. Invoke `/extract` once per document and name that document explicitly.
R35a. IF `/extract` stops for a loose document THEN leave that document unregistered, continue with the remaining candidates, and report the stop.

// Auto sort
R36. IF a LOOSE CANDIDATE is answered `a` THEN read its content and name its DOCUMENT TYPE as one plural lowercase noun describing what the document is.
     // Example: a homework assignment → `homework`; a lab handout → `labs`; a past exam → `exams`; a grading rubric → `rubrics`; a Python demo → `code`.
R36a. IF the content is a syllabus, course schedule, or course calendar THEN its DOCUMENT TYPE is COURSE SCOPE; invoke `/extract <candidate>` with output to `extracted/` AND move its raw file to `source/`.
R36b. A COLLECTION is a directory `extracted/class/<DOCUMENT TYPE>/` paired with `source/<DOCUMENT TYPE>/`. `lectures`, `misc`, and `other` are never COLLECTION names.
R36c. IF a COLLECTION for the candidate's DOCUMENT TYPE exists THEN file the candidate into it.
R36d. IF no COLLECTION for the DOCUMENT TYPE exists AND `extracted/class/misc/` or `extracted/class/other/` holds a file of the same DOCUMENT TYPE THEN create the COLLECTION, move each such file and its raw source file into it, and file the candidate into it.
R36e. IF neither R36c nor R36d applies THEN file the candidate into `extracted/class/misc/`, with its raw file in `source/misc/`.
R36f. Filing a document = invoke `/extract <candidate>` with output to the target `extracted/` directory AND move its raw file to the paired `source/` directory. Filing a code or image file = copy it to the target `extracted/` directory AND move its original to the paired `source/` directory.
R36g. Process auto-sort candidates one at a time in list order, so a candidate filed under R36e is visible to R36d for the next candidate.
R36h. IF R36d moves a file THEN rewrite every `## Contents` and `## Instructor Material` entry for its old path to the new path.
R36i. IF a candidate's content fits none of the document types already present AND cannot be named as one plural noun THEN file it under R36e.
R37. IF `/extract` stops for an auto-sort document THEN leave it unregistered, continue with the remaining candidates, and report the stop.
R43. IF a loose candidate is neither a document, code file, nor image file THEN move it to `source/` after its classification.
R43a. IF moving files out of a NEW directory leaves it empty THEN remove that empty directory.

// Registry
R44. IF at least one lecture or course-scope file was successfully processed THEN ensure `CLAUDE.md` contains an `## Instructor Material` section immediately after `## Contents`, or append it at end of file when `## Contents` is absent.
R45. IF a lecture deck or lecture-material file was successfully processed THEN write it under `### Teaching` as ``- `<path>` — <kind and extent>``.
R47. IF a course-scope file was successfully processed THEN write it under `### Course Scope` as ``- `<path>` — <kind and extent>``.
R48. IF a registry entry for the same path already exists THEN replace that entry.
R49. Do NOT add a registry entry for textbook or COLLECTION or `misc` files. R36h overrides R49 for an entry that existed before the move.
R50. Do NOT record a chapter number or inferred chapter mapping in `## Instructor Material`.

// Contents and textbook state
R51. Add a one-line entry for every successfully processed NEW candidate under its `**<dir>/**` group in `## Contents`.
R52. IF writing an R51 entry THEN record each processed file's exact class-root-relative path in backticks, including files from a NEW directory; a folder summary does not replace its file inventory.
R53. IF `/extract` already added a Contents entry for an output or moved source file THEN do NOT add a duplicate.
R54. IF a textbook was successfully extracted AND `## Source Profile` has no `Notes file:` field THEN set `Notes file:` to its full extracted-notes path.
R55. IF a textbook was successfully extracted AND `Notes file:` names a different file THEN report the conflict and ask the user how to proceed. STOP until the user responds.
R56. IF updating `CLAUDE.md` THEN limit changes to `## Contents`, `## Instructor Material`, `## Source Profile`'s `Notes file:` field, and the scan/OCR provenance required by extract R11j in `## Source Profile`.

// Lecture-deck state
R57. IF a processed lecture file holds one or more deck headings (generate-questions lecture.md L2) THEN list each DECK ID (L2a) it holds.
R58. IF a listed deck's `questions_<DECK ID>.md` already exists beside its file THEN mark that questions file STALE and report that `/generate-questions <DECK ID>` with `regenerate` rebuilds it.
R59. Do NOT invoke `/generate-questions` automatically.
R60. IF a listed deck has no questions file THEN report that `/generate-questions <DECK ID>` creates its study list.

// Report
R62. Report the NEW candidates, each lecture deck, each loose-file classification, each auto-sort DOCUMENT TYPE and destination, each COLLECTION created and the files moved into it, files extracted or copied and their destinations, files moved to `source/`, every extraction stop, registry and Contents changes, Notes-file conflicts, and the decks listed under R57–R60.

// Catch-all
R64. IF any condition not covered by R1–R62 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Instructor Material Format

```markdown
## Instructor Material

### Teaching

- `extracted/class/lectures/lec13_dijkstra_notes.md` — pptx, 14 slides
- `extracted/class/lectures/week3_handout_notes.md` — pdf, 4 pages

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
`source/lectures/`. Every other file receives the `l/t/a` prompt. Then run
`/generate-questions <deck>` for each new deck the report lists.

```
deck (.ppt/.pptx)     → extracted/class/lectures/     → BECOMES questions_<deck>.md
l  lecture material   → extracted/class/lectures/     → registered under Teaching
t  textbook           → extracted/textbook/           → BECOMES questions_chapter<N>.md
a  auto sort          → syllabus/schedule → extracted/ (Course Scope, a notice)
                      → second file of a type → extracted/class/<type>/ collection
                      → first file of a type  → extracted/class/misc/ until a match arrives
```
