---
name: quiz
description: Quiz the user on algorithms course material using extracted notes from the extracted/ directory. Supports wk1-wk8 and midterm1.
---

Quiz the user on the specified week or topic using the extracted notes in `extracted/`.

## Instructions

1. **Read the relevant notes file** from `extracted/` (e.g., `extracted/wk8_notes.md`)
2. **Follow quiz mode rules strictly:**
   - Ask **one question at a time** — wait for the answer before proceeding
   - If the user asks a clarifying question mid-quiz: answer it, then re-display the current quiz question at the bottom
   - After each answer: confirm correct/incorrect with a brief explanation, then show the next question
   - Track score (correct/total) and display a summary at the end
3. **Generate varied questions** — don't repeat exact exam values. Use the variation rules in the notes file if present.
4. **For Part I style questions:** always display the algorithm pseudocode before asking Q1
5. **For T/F table questions:** always state constraints (e.g., k ≥ 1, e > 0, c > 1) before showing the table

## Usage

```
/quiz wk8
/quiz midterm1
```
