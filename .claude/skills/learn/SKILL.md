---
name: learn
description: Teach the user algorithms course material concept by concept, then check understanding with a question. Good for going in with zero prior knowledge. Supports wk1-wk10 and midterm1.
---

Teach the user the specified week or topic using the extracted notes in `extracted/`, one concept at a time.

## Instructions

1. **Read the relevant notes file** from `/home/jcvega/edu/algorithms/class_material/extracted/` (e.g., `extracted/wk10_notes.md`)
2. **Break the material into concepts** — each major section or idea is one "lesson unit"
3. **For each unit, follow this loop:**
   - **Teach:** Present the concept clearly — definition, key points, pseudocode if relevant, a concrete example
   - **Check:** Ask one focused question to confirm the user understood it
   - **Respond:** Confirm correct/incorrect with a brief explanation
   - **Continue:** Move to the next unit
4. **Pacing rules:**
   - Never dump multiple units at once — one at a time
   - If the user gets the check question wrong, re-explain the concept more simply before moving on
   - If the user asks a follow-up question mid-lesson: answer it fully, then immediately resume with the current unit — do NOT ask "Ready to continue?"
5. **Show pseudocode** whenever introducing an algorithm — exact pseudocode from the notes
6. **Show math formulas** with a Legend block defining each symbol:
   > **Legend:** α = load factor | m = number of slots | n = number of elements
7. **Track progress** — show "Unit X of Y" at the start of each new concept
8. At the end, give a brief summary of everything covered and offer to quiz the user with `/quiz`

## Usage

```
/learn wk10
/learn wk7
```
