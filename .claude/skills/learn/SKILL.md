---
name: learn
description: Teach the user course material concept by concept, then check understanding with questions. Requires a pre-generated questions file from /generate_questions. Reads from extracted/ in the current directory.
---

Deliver course material question by question using a pre-generated questions file. `/learn` is a delivery engine — it does not generate content or questions. Those come from `/generate_questions`.

## Rules

// Loading
R1.  IF argument is given THEN look for `extracted/questions_<arg>.md`.
R2.  IF the file exists THEN load it and proceed to R5.
R3.  IF the file does not exist THEN stop and tell the user: "Run /generate_questions <arg> first."
R4.  IF no argument is given THEN list all `extracted/questions_*.md` files and ask the user to pick one. STOP until user responds.

// Unit and question delivery
R5.  IF starting a new unit THEN display "Unit X of Y — <title>".
R6.  IF about to display a question THEN first display that question's `Teach:` field verbatim, framed by labeled Unicode lines with two blank lines inside each edge:
     ──────────────────────── start ────────────────────────


     <Teach field content>


     ──────────────────────── end ────────────────────────
R7.  Do NOT rewrite, summarize, or add to the Teach field.
R8.  Do NOT display `Tests` or `Audit` fields at any point.
R9.  After displaying the Teach field, ask the question.
R10. Ask one question at a time. Do NOT display the next question until the user answers the current one.
R11. Display only the `Question` field — not `Tests`, `Answer key`, or `Audit`.

// Grading
R12. IF the user's answer contains the key idea(s) from the `Answer key` THEN mark correct.
     Correct answers need not match the phrasing in the Answer key.
     // Example: Answer key = "TCP throttles the sender when the network is congested."
     //          User says  = "TCP slows you down if the network is busy." → CORRECT (R12).
R12a. IF a question's Teach field contains a formula AND the user's answer correctly explains the underlying mechanism conceptually (without citing formula terms or variable names) THEN mark correct.
R12b. R12a overrides R13: a missing formula citation alone is not sufficient to mark an answer wrong if the conceptual mechanism is correctly explained.
R13. IF the user's answer is missing the key idea(s) from the `Answer key` THEN mark wrong.
R14. IF the user's answer contains a factually incorrect claim THEN mark wrong.
R15. R14 overrides R12: IF the answer contains the key idea AND a factually incorrect claim THEN mark wrong.
     // Example: User says "TCP throttles the sender by dropping packets." → WRONG (R15): mechanism claim is wrong.

// Skip
R16s. IF the user says "skip" (or a clear equivalent: "pass", "next", "move on") THEN acknowledge it, display the correct answer from the `Answer key`, and move to the next question. Count the skipped question as wrong in the final score.
R16t. R16s overrides R18: a skipped question does not require a correct answer before advancing.

// Wrong answer flow
R16. IF the answer is marked wrong THEN re-display that question's `Teach:` field (framed by Unicode lines per R6), then explain the concept using simpler language or a more concrete example.
R17. After R16, ask the same question again.
R18. Do NOT move to the next question until the current question is marked correct.

// Pacing
R19. IF the user sends a clarifying or follow-up question THEN answer it fully, then re-display the current unanswered question. Do not ask "Ready to continue?"
R20. Move to the next unit only after all questions in the current unit are marked correct.

// English reference
R21. IF the source material is in a non-English language OR uses discipline-specific scientific terminology AND the user's answer is marked correct THEN append: `**English reference:** <standard English name>`.
R22. Do NOT append the English reference after wrong answers.

// Wrap up
R23. After the last question of the last unit is marked correct, output a one-paragraph summary covering all units.

// Catch-all
R24. IF any condition not covered by R1–R23 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Usage

```
/generate_questions chapter2   ← run this first
/learn chapter2
```
