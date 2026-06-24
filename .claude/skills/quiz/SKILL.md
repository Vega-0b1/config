---
name: quiz
description: Quiz the user on course material using extracted notes from the extracted/ directory in the current working directory.
---

Quiz the user on the specified week or topic using extracted notes.

## Instructions

### 1. Load the notes

Map the argument to a file: `wk8` → `extracted/wk8_notes.md`, `midterm1` → `extracted/midterm1_notes.md`, etc.

If no argument is given, list the files available in `extracted/` and ask the user which to quiz on.

If the file doesn't exist, stop and tell the user — do not hallucinate questions from memory.

### 2. Quiz rules

- Ask **one question at a time** — wait for the answer before proceeding. Multiple questions at once make it hard to give focused answers and make it impossible to pinpoint exactly what the user knows vs. doesn't know.
- Clarifying question mid-quiz → answer it fully, then re-display the current question at the bottom so the user doesn't have to scroll up to remember what they were answering.
- After each answer: confirm correct/incorrect with a brief explanation so the user knows exactly what they got right or wrong, then move to the next question.
- Track score (correct/total). Display summary at the end.

### 3. Question guidelines

- Ask as many questions as needed to cover the full breadth of the material, then show the summary. Don't cut off early — stopping short gives the user false confidence about material that wasn't covered. Don't pad with repetition either.
- Vary question types — don't repeat exact values from the notes. Rephrase to test understanding, not memorization.
- When a question involves an algorithm, protocol, or process: show the relevant pseudocode or steps before asking — algorithm questions without that context are unfair since the user is being tested on behavior, not on memorizing code.
- When showing math: follow with a Legend block defining each symbol — a formula without a legend is meaningless to someone seeing it for the first time.

## Usage

```
/quiz wk8
/quiz midterm1
```
