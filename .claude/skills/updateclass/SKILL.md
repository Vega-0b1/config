---
name: updateclass
description: Bring an already-scaffolded class directory up to date with material added since it was created. Detects new files and asks, per file, whether it is teaching material from the professor (slides, handouts, labs), a course-scope document (syllabus, schedule), or neither. Extracts documents via /extract — converting legacy .ppt/.doc/.xls first — then maps teaching files to the chapter they cover and reads the syllabus for which chapters the course covers at all. Records both in the class CLAUDE.md so /generate_questions can tier questions against what was actually taught, and /learn can flag chapters the course skips. Run this whenever slides, handouts, labs, exams, or a syllabus land in a class folder.
---

Update an existing class directory with newly added material.

`/addclass` scaffolds a class once. `/updateclass` is its ongoing counterpart: run it whenever new material arrives mid-semester. Its job is to get those files sorted, extracted, and — critically — to record which of them came from the instructor.

That last part is the whole point. `/generate_questions` tiers questions `core` vs `supporting`. Without instructor material it can only rank against the textbook's own Objectives and Key Points, and for books that carry no such apparatus it cannot rank at all. A registry of what the professor actually put in front of the class gives it a real anchor: what was taught is what is testable.

## Rules

// Target resolution
R1.  Target = cwd.
R2.  IF cwd contains no `CLAUDE.md` THEN stop and tell the user to run `/addclass` first. Do NOT scaffold.
     // Commentary: the registry (R23) and the Contents inventory (R26) both live in `CLAUDE.md`. Without it there is nowhere to record the answers this skill collects, and the y/n prompts would be discarded work.
R3.  IF cwd's basename is `source`, `extracted`, `code`, or `images` THEN stop and tell the user to run from the class root.

// New-file detection
R4.  Enumerate candidate files: every loose file and directory in the class root, plus every file directly inside `source/`, `code/`, and `extracted/`.
R5.  A candidate is NEW IF its basename does not appear in the `## Contents` section of `CLAUDE.md`.
     // Commentary: `/addclass` R18a, `/extract` R21, and `/generate_questions` R24a all maintain Contents as a living inventory. Reusing it as the seen-set means this skill needs no state file of its own and stays correct even when files were added by those skills rather than by hand.
R6.  IF `## Contents` reads `Nothing here yet` (the `/addclass` R18c placeholder) THEN treat the inventory as empty and every candidate as NEW.
R7.  Exclude from candidates: `CLAUDE.md`, `README.md`, dotfiles, lock files, the `extracted/images/` directory, and the skill chain's own output — `questions_*.md`, `practice_*.md`, and `flagged_questions_*.md`.
     // Commentary: those three are written by /generate_questions R24/R24e and /learn R23a, and /learn's flagged-questions file is never added to Contents by its author. Without this exclusion the first /updateclass run in any class that has used /learn asks "instructor-provided?" about the chain's own artifacts.
R8.  IF no candidate is NEW THEN report that the class is already up to date and stop. Do not prompt.
R9.  Treat a NEW directory (e.g. `wk4/`) as one candidate, not as one candidate per file inside it.
     // Commentary: weekly folders are a single act of course delivery. Prompting per file inside one would ask the same question a dozen times.
R9a. IF two NEW candidates share a basename and differ only as a legacy/modern pair (`.ppt`/`.pptx`, `.doc`/`.docx`, `.xls`/`.xlsx`) THEN treat them as ONE candidate, listed under the modern name. Both files are handled together throughout.
     // Commentary: /extract R8a–R8f converts a legacy binary and keeps both files, so one lecture can appear twice in the R4 scan. Prompting about `lec1.ppt` and `lec1.pptx` separately asks the same question twice about the same lecture.
R9b. Before prompting, check each NEW document candidate's format. Note on its R11 line when it is a legacy binary that `/extract` will convert.
     // Commentary: the conversion is automatic under /extract R8a, so this is disclosure, not a decision point. Saying it up front keeps a surprise `.pptx` appearing in `source/` from reading as a bug.

// Classification prompt
R10. IF exactly one candidate is NEW THEN print its name and ask: `instructor-provided? (y/n/s/c)`. STOP until the user responds.
R11. IF more than one candidate is NEW THEN print the full numbered list once for context, then ask about the FIRST candidate alone. STOP until the user responds.
R11b. Ask about exactly one candidate per turn, in list order. Do NOT present the next candidate until the current one has been answered.
     // Commentary: batching the whole list into one space-separated reply looks efficient and is not. It forces the user to hold every filename in their head at once, and a miscounted reply invalidates the entire batch under R12 rather than one item.
R11c. IF a candidate has been answered THEN ask about the next one immediately. Do NOT ask whether to continue.
R11a. Print the legend with every prompt:
     `y = teaching material from the professor (slides, handout, lab)`
     `c = course scope (syllabus, schedule) — defines what the course covers`
     `n = not from the professor`
     `s = already processed, just inventory it`
R12. Accept a single `y`, `n`, `s`, or `c` case-insensitively, and nothing else. IF the reply is any other token THEN re-ask about the same candidate. STOP until the user responds. Do NOT guess.
R13. `y` = teaching material. `c` = course scope. `n` = not instructor-provided. `s` = already processed by an earlier run or by hand.
R13b. `y` and `c` are different kinds of instructor material and are NOT interchangeable. A `y` candidate says what is worth knowing; a `c` candidate says which chapters are on the menu.
     // Commentary: a syllabus names the topic of an entire week — "Week 6: Transport layer". Every concept in that chapter matches it, so treating it as teaching material would promote a whole chapter to `core` and the tier would stop meaning anything. This is the same failure /generate_questions R0e1 rejects narrative chapter summaries for.
R13a. IF the answer is `s` THEN skip R15–R29 for that candidate. Apply R30 and R30a only, so the file gains a Contents entry naming it literally.
     // Commentary: R5 matches Contents by basename, but /addclass R18a lets an entry be written as prose — `~/edu/network` inventories its textbook as "Kurose & Ross textbook EPUB", which no basename match can find. Without `s`, that EPUB reads as NEW on every run and R17 re-extracts a 349-image book into a duplicate notes file. One `s` writes the literal filename into Contents and the candidate never resurfaces.
R14. Do NOT infer instructor provenance from a filename, extension, or location. R13's answer is the only source.
     // Commentary: a PDF the user downloaded and a PDF the professor handed out are byte-identical in every respect this skill can observe. Guessing here mistags a whole chapter's core tier, and the user would not find out until the quiz.
R14a. Do NOT infer `s` either. A candidate is already-processed only when the user says so.
     // Commentary: the tempting heuristic — "an extraction with a matching name exists" — fails on this very repo, where the Kurose EPUB extracted to `networking_notes.md` rather than to the sanitized name /extract R2 would derive. The user knows what they have already run; the filesystem does not record it.

// Sorting
R15. IF a NEW candidate is a document (`.pdf`, `.docx`, `.pptx`, `.epub`) THEN do NOT move it. Leave it in place for R17.
     // Commentary: `/extract` R17–R18 move their own inputs into `source/` after a successful write. Pre-moving would leave the extract call with nothing to find, and moving after would double-handle the file.
R16. IF a NEW candidate is not a document THEN sort it per `/addclass` R11–R16: code to `code/` (creating it if needed), pre-processed markdown to `extracted/`, raw material and anything ambiguous to `source/`, and leave dotfiles, lock files, unknown archives, and context-free media in place.

// Extraction
R17. IF a NEW candidate is a document THEN invoke `/extract <candidate>`.
R18. Invoke `/extract` once per candidate, naming that candidate explicitly. Do NOT invoke it with no argument.
     // Commentary: a bare `/extract` targets every loose file in the directory and writes them to one combined notes file, which would fuse a slide deck and a handout into a single undifferentiated extraction.
R19. This skill contains no extraction logic. All format handling — page anchors, slide anchors, image extraction, heading reconstruction — belongs to `/extract`.
R20. IF `/extract` stops for any reason (an existing output file per its R6, an unreadable source, a failed write) THEN leave that candidate unregistered, continue with the remaining candidates, and report the stop under R35.
R21. IF a NEW candidate is code or an image AND the answer was `y` THEN register it by its own path. Do NOT extract it.
     // Commentary: `/generate_questions` opens code and image paths directly with the Read tool, the same way its R9b already opens figures. Converting them to markdown would only lose fidelity.

// Chapter mapping
R22. IF a candidate was answered `y` THEN determine which chapter it covers, per R23–R25. IF a candidate was answered `c` THEN determine the course's chapter scope instead, per R26a–R26d.
R23. Read the primary notes file named by the `Notes file:` field of the `## Source Profile` in `CLAUDE.md`, and collect its chapter headings under that profile's chapter heading pattern.
R24. Compare the candidate's extracted content against those chapter headings and their subsection titles. Propose the best-matching chapter for each `y` candidate, display every proposal as a list, and ask the user to confirm or correct it. STOP until the user responds.
     // Example: `ch1_slides_notes.md → Chapter 1 (What Is the Internet?)` — confirm, or reply with the correct chapter.
R25. IF `CLAUDE.md` has no `## Source Profile`, or its `Notes file` does not exist, THEN do NOT propose a mapping. Ask the user which chapter each `y` candidate covers. STOP until the user responds.
     // Commentary: with no chapter list to match against, a proposal would be a guess dressed as an inference. Asking is honest and costs one reply.
R26. A mapping value may name something other than a chapter (`wk10`, `midterm`, `lab3`). Record whatever the user confirms, verbatim.
R26a. IF a candidate was answered `c` THEN locate the section of its extracted content that lists topics against weeks, units, or dates — a heading matching `Topics`, `Schedule`, `Course Outline`, `Calendar`, or `Tentative Schedule`, case-insensitively.
R26b. Map each listed topic to the chapters collected in R23, by topic name against chapter title. Produce two sets: chapters IN scope and chapters NOT in scope.
     // Example: "Week 6: Transport layer" → Chapter 3 (Transport Layer). Chapters no topic maps to are out of scope.
R26c. Display both sets and ask the user to confirm or correct them. STOP until the user responds.
     // Example: `In scope: 1, 2, 3, 4, 5, 6, 8 · Not covered: 7 (Wireless and Mobile Networks), 9 (Multimedia Networking)` — confirm, or correct.
R26d. IF no schedule section can be located THEN do NOT guess a scope. Say so, ask the user which chapters the course covers, and STOP until they respond.
     // Commentary: a syllabus without a schedule still records provenance worth keeping, but an invented scope would mark real chapters out of scope and /learn would tell the user not to study them.
R26e. Do NOT derive scope from a `y` candidate, and do NOT derive per-chapter priority from a `c` candidate. The two kinds answer different questions.

// Registry write
R27. IF at least one candidate was answered `y` or `c` THEN write its confirmed mapping to the `## Instructor Material` section of `CLAUDE.md`, in the format given below. IF the section does not exist THEN create it immediately after `## Contents`, or at end of file when there is no Contents section.
R27a. Write `y` entries under a `### Teaching` subheading and `c` entries under a `### Course Scope` subheading. Create whichever subheading is missing.
     // Commentary: /generate_questions R12n reads only `### Teaching` when it assigns `core`. The split is what keeps a syllabus from promoting an entire chapter.
R28. IF an entry for the same path already exists THEN replace that line. Do NOT duplicate it.
R29. Do NOT write a registry entry for a candidate answered `n`.

// Contents update
R30. Add a one-line entry (`- file — description`) for every NEW candidate that was sorted or extracted, under its `**<dir>/**` group header in `## Contents`. IF a needed group header does not exist THEN create it. Every entry MUST lead with the file's literal name in backticks, per `/addclass` R18a1.
R30a. IF an existing `## Contents` entry names a file in prose rather than in backticks AND this run identified that file, THEN rewrite that entry to lead with the literal filename, preserving its description.
     // Commentary: this is what stops the `s` answer from becoming a permanent tax. A prose entry is invisible to R5's basename match, so without the repair the same file reads as NEW on every future run and the user re-answers `s` forever.
R31. IF `/extract` already added an entry for a file under R21 of that skill THEN do not add a second one.
R32. Do NOT modify any part of `CLAUDE.md` outside `## Contents` and `## Instructor Material`, except as R33 requires.

// Stale questions detection
R32a. IF a chapter gained a `### Teaching` entry in this run AND `extracted/questions_<chapter>.md` already exists THEN mark that questions file STALE.
R32b. IF a questions file is marked STALE THEN name it in the R35 report and say that `/generate_questions <chapter>` will merge the new material in without regenerating.
     // Commentary: the registry write changes which concepts are core, but nothing rewrites the questions file — a user who stops here has a correct registry and a questions file that still reflects last week. Naming it is what closes the loop, since /generate_questions cannot announce staleness for a chapter nobody re-runs.
R32c. Do NOT invoke `/generate_questions` automatically. Report the staleness and let the user choose when to spend the run.
     // Commentary: a merge on a large chapter is real work, and the user may be adding four decks in one sitting. Firing a merge per registry write would run it three times for nothing.

// Source Profile touch-up
R33. IF the registry holds at least one `### Teaching` entry after R27 THEN set the `## Source Profile`'s anchor source to `instructor` and its generation mode to `tiered`.
R33a. A `### Course Scope` entry alone does NOT change the anchor source or the generation mode.
     // Commentary: scope says which chapters are on the menu, not which concepts within them matter. A class holding only a syllabus still has nothing to rank against and must stay `capped`/`untiered`.
R34. IF `CLAUDE.md` has no `## Source Profile` THEN skip R33. Do NOT create one.
     // Commentary: profile detection belongs to `/generate_questions` R0b, which writes the whole profile from the notes' actual shape. A partial profile written here would satisfy its R0a and suppress the real detection.

// Confirm
R35. Report: candidates found and which were NEW, the y/n/s/c answer per candidate, every candidate skipped under R13a, any legacy file converted by `/extract` R8a, what was extracted and to where, what was sorted and to where, the confirmed chapter mapping per `### Teaching` entry, the confirmed in-scope and out-of-scope chapter sets per `### Course Scope` entry, any `/extract` stop from R20, any Contents entry repaired under R30a, any questions file marked STALE under R32a, whether `## Instructor Material` and `## Contents` were updated, whether the Source Profile was touched under R33, and anything left in place under R16.
R35a. IF a `### Course Scope` entry was written THEN name the out-of-scope chapters explicitly in the report.
     // Commentary: "your course skips chapters 7 and 9" is the single most useful thing this skill can tell someone, and it is the answer to what to do with the rest of the book once the semester ends.

// Catch-all
R36. IF any condition not covered by R1–R35 (including lettered sub-rules) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Instructor Material Format

```markdown
## Instructor Material

### Teaching

- `extracted/ch1_slides_notes.md` — chapter 1 — pptx, 42 slides
- `extracted/lab2_notes.md` — chapter 3 — pdf, 8 pages
- `code/udp_demo.py` — chapter 2 — code, read directly
- `extracted/images/topology_handout.png` — chapter 1 — image, read directly

### Course Scope

- `extracted/syllabus_notes.md` — covers 1, 2, 3, 4, 5, 6, 8 — not covered: 7, 9 — pdf, 5 pages
```

**Teaching** lines are: backtick-quoted path relative to the class root, an em dash, the confirmed mapping from R26, an em dash, and the source kind with its extent (slide count, page count, or `read directly` for unextracted code and images).

**Course Scope** lines replace the single mapping with two chapter sets from R26c: `covers <list>` then `not covered: <list>`. These entries never promote a concept to `core`.

// Commentary: one section, hand-editable, in the file `/generate_questions` R0 already
// opens. A wrong chapter inference is corrected once by hand and stays corrected —
// the same affordance Source Profile R0g gives to a wrong profile detection.

## Usage

```
/updateclass          ← run from the class root after dropping in new material
```

Typical session: drop `lec1_intro.ppt` and `syllabus.pdf` into `~/edu/network/`,
run `/updateclass`, answer `y`, then `c` when it asks about the next file. The deck
is converted to `.pptx`, extracted with
per-slide anchors, and mapped to chapter 1 — so `/generate_questions chapter1` can
now mark a concept `core` and cite the slide that taught it. The syllabus is read
for its schedule instead, producing the course's chapter scope, so `/learn` can
tell you that chapters 7 and 9 are never covered.

The two kinds answer different questions and are not interchangeable:

```
y  teaching material  → what is worth knowing   → promotes concepts to core
c  course scope       → what is on the menu     → promotes nothing
```
