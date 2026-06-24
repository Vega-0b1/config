---
name: addclass
description: Scaffold a new class directory under /home/jcvega/edu/ with the standard structure (extracted, source, code) and a README. Sorts any existing files into the right subdirectory.
---

Set up a new class directory with the standard structure used across this edu repo.

## Directory Philosophy

```
extracted/   — the "stack": always read this first. Pre-processed markdown notes only.
               Can have subdirs (e.g. extracted/instructions/).
source/      — the "heap": raw files — books, slides, exams, lab PDFs, weekly folders.
               Only open these when extracted/ doesn't have what you need.
code/        — code written during the course.
```

## Instructions

### 1. Resolve the target path

- If an argument is given (e.g. `calculus`), target is `/home/jcvega/edu/calculus/`. Create it if it doesn't exist.
- If no argument is given, scaffold inside the current directory in place. First verify cwd is a class directory (parent is `~/edu` or `~/edu/zOld`) — if not, stop and tell the user to provide a name or navigate to the right place.

### 2. Infer course metadata from existing files

Do not ask the user anything — scanning filenames gives enough context, and asking creates unnecessary friction for a simple scaffolding task. Scan the target root for clues:

- **Textbook:** Read filenames of any EPUBs/PDFs — the filename usually contains the title, author, and edition.
- **Course number & name:** Infer from the folder name and any filenames that include a course code. If nothing is findable, use the folder name as the course name.

### 3. Create the directory structure

```
{target}/extracted/
{target}/source/
{target}/code/
```

### 4. Sort existing files and directories

Scan the target root for any files and directories. Use judgment to place each:

- **`source/`** — anything raw: textbooks (EPUB/PDF), lecture slides, weekly folders (`wk1/`, `wk2/`), exam PDFs, lab PDFs, handouts. Default for anything ambiguous — source/ is the safe bucket for unknowns since it's the "raw files" home and nothing gets lost there.
- **`code/`** — source code files or directories containing code.
- **`extracted/`** — only if already a pre-processed markdown notes file.

If something genuinely fits nowhere, leave it in place and note it in the summary — do not force a wrong placement.

### 5. Write README.md

```markdown
# <Course Name>

- **Course:** <Course Number — Course Name, or just Course Name>
- **Textbook:** <Title, Author, Edition, or omit if none found>

## Directories

\`\`\`
extracted/   — pre-processed notes (read this first)
source/      — raw files: books, slides, exams, labs (open only when needed)
code/        — code written during the course
\`\`\`

Always read `extracted/` first. Only open `source/` if the extracted notes don't cover what you need.
```

### 6. Confirm

Print: full path created, files moved and where they landed, anything left in place.

## Usage

```
/addclass calculus
/addclass machine_learning
```
