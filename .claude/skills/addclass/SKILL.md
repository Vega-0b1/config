---
name: addclass
description: Scaffold a new class directory under /home/jcvega/edu/ with the standard structure (extracted, source, and code when the class has code) and a CLAUDE.md. Sorts any existing files into the right subdirectory.
---

Set up a new class directory with the standard structure used across this edu repo.

## Directory Philosophy

```
extracted/   — the "stack": always read this first. Pre-processed markdown notes only.
               Can have subdirs (e.g. extracted/instructions/).
source/      — the "heap": raw files — books, slides, exams, lab PDFs, weekly folders.
               Only open these when extracted/ doesn't have what you need.
code/        — code written during the course. Created only when the class has code.
```

## Rules

// Target resolution
R1.  IF an argument is given (e.g. `calculus`) THEN target = `/home/jcvega/edu/<arg>/`. Create it if it doesn't exist.
R2.  IF no argument is given AND cwd's parent is `~/edu` or `~/edu/zOld` THEN target = cwd; scaffold in place.
R3.  IF no argument is given AND cwd's parent is NOT `~/edu` or `~/edu/zOld` THEN stop and tell the user to provide a name or navigate to a class directory.

// Metadata inference
R4.  IF inferring course metadata THEN scan filenames in the target root. Do NOT ask the user questions.
     // Commentary: filenames give enough context; asking creates friction for a simple scaffolding task.
R5.  IF an EPUB/PDF filename contains a title, author, or edition THEN use it as the textbook.
R6.  IF the folder name or any filename contains a course code THEN use it as the course number.
R7.  IF no course name is findable THEN use the folder name as the course name.

// Directory creation
R8.  Create `{target}/extracted/` and `{target}/source/`.
R9.  IF the target root contains code files or directories containing code THEN create `{target}/code/`.
R10. IF the target root contains no code THEN do NOT create `code/`.

// File sorting
R11. IF a file or directory is raw material (textbook EPUB/PDF, lecture slides, weekly folders like `wk1/`, exam PDFs, lab PDFs, handouts) THEN move it to `source/`.
R12. IF a file or directory contains code THEN move it to `code/` (created per R9).
R13. IF a file is already a pre-processed markdown notes file THEN move it to `extracted/`.
R14. IF a file is ambiguous but plausibly raw material THEN move it to `source/`.
     // Commentary: source/ is the safe bucket for unknowns — nothing gets lost there.
R15. IF a file genuinely fits nowhere THEN leave it in place and note it in the summary.
R16. Do NOT move `extracted/`, `source/`, `code/`, or `CLAUDE.md`.

// CLAUDE.md
R17. Write `{target}/CLAUDE.md` using the template below.
R18. IF `code/` was not created (R10) THEN omit the `code/` line from the directories block in CLAUDE.md.
R18a. IF writing the `## Contents` section THEN add a one-line entry (`- file — description`) for every file sorted in R11–R15, grouped under a `**<dir>/**` bold header per directory.
R18b. IF a directory received no files THEN omit its group header from the Contents section.
R18c. IF no files were sorted at all THEN keep the `## Contents` section with the single line: `Nothing here yet — /extract and /generate_questions add entries as they create files.`
     // Commentary: the section must exist so those skills grow it instead of skipping it.

// Confirm
R19. Print: full path created, files moved and where they landed, anything left in place.

// Catch-all
R20. IF any condition not covered by R1–R19 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## CLAUDE.md Template

```markdown
# <Course Name>

- **Course:** <Course Number — Course Name, or just Course Name>
- **Textbook:** <Title, Author, Edition — omit line if none found>

## Directories

\`\`\`
extracted/   — pre-processed notes (read this first)
source/      — raw files: books, slides, exams, labs (open only when needed)
code/        — code written during the course
\`\`\`

Always read `extracted/` first. Only open `source/` if the extracted notes don't cover what you need.

## Contents

**extracted/**
- <file — one-line description>

**source/**
- <file — one-line description>

**code/**
- <file — one-line description>
```

// Commentary: the Contents section is a living inventory — /extract and
// /generate_questions append entries to it as they create files, so every fresh
// session knows what exists without exploring.

## Usage

```
/addclass calculus
/addclass machine_learning
```
