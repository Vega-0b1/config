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

Each major section or idea = one lesson unit. Count them so you can track "Unit X of Y". Showing "Unit X of Y" gives the user a sense of progress and how much is left.

### 3. For each unit, follow this loop

- **Teach:** definition, key points, example. Show pseudocode or step sequences when the subject calls for it (exact text from the notes).
- **Check:** After teaching a unit, ask questions one at a time until all key concepts from that unit have been tested. Each question must target ONE specific idea — asking about multiple things at once makes it hard to pinpoint what the user doesn't know. Questions MUST be answerable from what was just taught — never ask about details that weren't explicitly covered, as that would be unfair and break trust. **If a term used in the teach content is defined in a later unit, do not quiz on it now — either omit it from the teach content or note "we'll cover this in a later unit" and skip quizzing on it.**
- **Respond:** Accept the answer as correct if it captures the right concept, even if the wording differs from the notes. Only mark it wrong if the core concept is missing or factually incorrect. **Do not penalize the user for omitting details that were introduced in the teach content but not yet fully explained — if the user's answer captures the main idea, it's correct.** Confirm correct/incorrect with a brief explanation so the user knows exactly what they got right or wrong, then ask the next question if concepts remain uncovered.
- **Continue:** Move to the next unit only after all key concepts from the current unit have been checked. Moving on too early leaves gaps.

### 4. Pacing rules

- One unit at a time — never dump multiple at once. The user needs time to absorb one idea before moving to the next.
- Wrong answer → re-explain more simply, then ask the same check question again before moving on. The user hasn't learned it until they can answer correctly.
- Follow-up question mid-lesson → answer it fully, then resume the current unit without asking "Ready to continue?" — asking "ready?" is unnecessary friction that breaks flow.
- **Repost the full teach content every 3 questions.** After every 3rd question within a unit, repost the full original teach content for that unit before asking the next question. This keeps the reference material visible so the user doesn't have to scroll up — in a long quiz session the teach content scrolls off screen and becomes inaccessible.

### 5. Math formulas

Always follow a formula with a Legend block defining every variable. Without a legend, formulas are meaningless to someone seeing them for the first time:
> **Legend:** α = load factor | m = number of slots | n = number of elements

### 6. Wrap up

Show "Unit X of Y" at the start of each new concept. At the end, give a brief summary of everything covered so the user leaves with a consolidated view of the whole chapter.

## Usage

```
/learn wk10
/learn midterm1
```
