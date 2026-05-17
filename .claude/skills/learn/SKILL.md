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
- **Check:** ask one focused question to confirm understanding. The question MUST be answerable from what was just taught in the Teach step — never ask about details that weren't explicitly covered.
- **Respond:** confirm correct/incorrect with a brief explanation.
- **Continue:** next unit.

### 4. Pacing rules

- One unit at a time — never dump multiple at once.
- Wrong answer → re-explain more simply before moving on.
- Follow-up question mid-lesson → answer it fully, then resume the current unit without asking "Ready to continue?"

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
