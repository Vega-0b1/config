---
name: quiz
description: Quiz the user on course material using extracted notes from the extracted/ directory in the current working directory.
---

Quiz the user on the specified week or topic using extracted notes.

## Instructions

### 1. Load the notes

Map the argument to a file: `wk8` → `extracted/wk8_notes.md`, `midterm1` → `extracted/midterm1_notes.md`, etc.

If no argument is given, list the files available in `extracted/` and ask the user which to quiz on.

If the file doesn't exist, stop and tell the user — do not hallucinate questions.

### 2. Quiz rules

- Ask **one question at a time** — wait for the answer before proceeding.
- Clarifying question mid-quiz → answer it, then re-display the current question at the bottom.
- After each answer: confirm correct/incorrect with a brief explanation, then next question.
- Track score (correct/total). Display summary at the end.

### 3. Question guidelines

- Ask as many questions as needed to cover the full breadth of the material, then show the summary. Don't cut off early and don't pad with repetition.
- Vary question types — don't repeat exact values from the notes.
- When a question involves an algorithm, protocol, or process: show the relevant pseudocode or steps before asking.
- When showing math: follow with a Legend block defining each symbol.

## Usage

```
/quiz wk8
/quiz midterm1
```
