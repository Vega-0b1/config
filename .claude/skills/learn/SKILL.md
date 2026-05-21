---
name: learn
description: Teach the user course material concept by concept, then check understanding with a question. Good for going in with zero prior knowledge. Reads from extracted/ in the current directory.
---

Teach the user the specified week or topic using extracted notes, one concept at a time.

## Instructions

### 1. Load the notes

Map the argument to a file: `wk10` → `extracted/wk10_notes.md`, `midterm1` → `extracted/midterm1_notes.md`, etc.

If no argument is given, list the files available in `extracted/` and ask the user which to study.

If the file doesn't exist, stop and tell the user — do not guess or hallucinate content.

### 2. Break material into concepts

Each major section or idea = one lesson unit. Count them so you can track "Unit X of Y".

### 3. For each unit, follow this loop

- **Teach:** definition, key points, example. Show pseudocode or step sequences when the subject calls for it (exact text from the notes).
- **Check:** After teaching a unit, ask questions one at a time until all key concepts from that unit have been tested. Each question must target ONE specific idea. Questions MUST be answerable from what was just taught — never ask about details that weren't explicitly covered.
- **Respond:** Accept the answer as correct if it captures the right concept, even if the wording differs from the notes. Only mark it wrong if the core concept is missing or factually incorrect. Confirm correct/incorrect with a brief explanation, then ask the next question if concepts remain uncovered.
- **Continue:** Move to the next unit only after all key concepts from the current unit have been checked.

### 4. Pacing rules

- One unit at a time — never dump multiple at once.
- Wrong answer → re-explain more simply, then ask the same check question again before moving on.
- Follow-up question mid-lesson → answer it fully, then resume the current unit without asking "Ready to continue?"
- **Repost the full teach content every 3 questions.** After every 3rd question within a unit, repost the full original teach content for that unit before asking the next question, so the reference material stays visible.

### 5. Math formulas

Always follow a formula with a Legend block:
> **Legend:** α = load factor | m = number of slots | n = number of elements

### 6. Wrap up

Show "Unit X of Y" at the start of each new concept. At the end, give a brief summary of everything covered.

## Usage

```
/learn wk10
/learn midterm1
```
