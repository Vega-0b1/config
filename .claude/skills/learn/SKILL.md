---
name: learn
description: Teach the user course material concept by concept, then check understanding with questions. Pass no_context for a blind review mode that hides the teaching content and just scores answers. Say "flag" on a question to log it with a reason for later processing. Requires a pre-generated questions file from /generate_questions. Reads from extracted/ in the current directory.
---

Deliver course material question by question using a pre-generated questions file. `/learn` is a delivery engine — it does not generate content or questions. Those come from `/generate_questions`.

Two modes: **teach** (default) shows each question's Teach field before asking — first contact with material. **review** (`no_context` flag) hides all Teach fields and asks blind — retrieval practice for material already learned. The modes differ only in Teach field visibility: in both, a graded answer (right or wrong) shows the answer and moves on. Say "flag" on any question to log it with a reason to a flagged-questions file for later processing.

## Rules

// Mode selection & loading
R1.  IF the arguments contain `no_context` or `--no_context` THEN mode = review; treat the remaining argument as <arg>.
R1a. IF more than one argument remains after removing the mode flag THEN stop and ask the user which one is the topic. STOP until user responds.
R2.  IF the arguments do not contain a no_context flag THEN mode = teach.
R3.  IF <arg> is given THEN look for `extracted/questions_<arg>.md`.
R4.  IF the file exists THEN load it and proceed to R7.
R4a. IF the loaded file contains zero units or zero questions THEN stop and tell the user: "Questions file is empty — re-run /generate_questions <arg>."
R5.  IF the file does not exist THEN stop and tell the user: "Run /generate_questions <arg> first."
R6.  IF no <arg> is given THEN list all `extracted/questions_*.md` files and ask the user to pick one. STOP until user responds.

// Unit and question delivery
R7.  IF starting a new unit THEN display "Unit X of Y — <title>" as a level-2 markdown heading: `## Unit X of Y — <title>`.
R8.  IF mode = teach AND about to display a question THEN first display that question's `Teach:` field verbatim as a markdown blockquote — prefix every line of the Teach content, including blank lines between sub-concepts, with `> `.
     // Commentary: the blockquote renders as a distinct callout in the desktop app; the `> ` on blank lines keeps a multi-paragraph Teach field inside one quote block.
R8a. The `> ` blockquote prefix in R8 is display framing, not content. R10 does not prohibit it.
R8b. IF mode = teach THEN after the Teach blockquote and before the Question, output a blank line, a `---` horizontal rule, and a blank line.
     // Commentary: the blank lines keep `---` from being parsed as a setext underline of the blockquote; the rule chunks "reference" from "what to answer".
R9.  IF mode = review THEN do NOT display Teach fields at any point.
     // Commentary: review mode is retrieval practice — showing the material before the question makes it an open-book test of text on screen.
R10. Do NOT rewrite, summarize, or add to the Teach field.
R11. Do NOT display `Tests` or `Audit` fields at any point.
R12. Ask one question at a time. Display only the `Question` field, rendered as a level-3 markdown heading with a `❓` anchor: `### ❓ <question text>`. Do NOT display the next question until the user answers the current one.

// Grading (both modes)
R13. IF the user's answer contains the key idea(s) from the `Answer key` THEN mark correct.
     Correct answers need not match the phrasing in the Answer key.
     // Example: Answer key = "TCP throttles the sender when the network is congested."
     //          User says  = "TCP slows you down if the network is busy." → CORRECT (R13).
R13a. IF a question's Teach field contains a formula AND the user's answer correctly explains the underlying mechanism conceptually (without citing formula terms or variable names) THEN mark correct.
R13b. R13a overrides R14: a missing formula citation alone is not sufficient to mark an answer wrong if the conceptual mechanism is correctly explained.
R14. IF the user's answer is missing the key idea(s) from the `Answer key` THEN mark wrong.
R15. IF the user's answer contains a factually incorrect claim THEN mark wrong.
R16. R15 overrides R13: IF the answer contains the key idea AND a factually incorrect claim THEN mark wrong.
     // Example: User says "TCP throttles the sender by dropping packets." → WRONG (R16): mechanism claim is wrong.

// Result display (both modes)
R16a. IF marking an answer correct THEN begin the result with `✅ **Correct**`.
R16b. IF marking an answer wrong — including a skip under R17 — THEN begin the result with `❌ **Wrong**`.
R16c. R16a–R16b set the result prefix only. They do not change what R13–R18 require the result to contain.

// Skip (both modes)
R17. IF the user's message declines to answer rather than attempts an answer (e.g. "skip", "pass", "next", "move on", "I don't know") THEN acknowledge it, display the correct answer from the `Answer key`, mark the question wrong as skipped, and move to the next question. In teach mode, display the Teach field before the Question field of the next question.

// Wrong answer flow (both modes)
R18. IF the answer is marked wrong THEN state wrong, display the correct answer from the `Answer key`, give a one-sentence explanation of the key idea missed, and move to the next question immediately. Do NOT re-teach, do NOT re-ask. In teach mode, display the Teach field before the Question field of the next question.
R19. Advance to the next question after every graded answer regardless of correctness. In teach mode, display the Teach field before the Question field of the next question.

// Pacing
R20. IF the user sends a clarifying or follow-up question THEN answer it fully, then re-display the current unanswered question. Do not ask "Ready to continue?"
R21. Move through units in order. There is no correctness gate on advancing to the next question or unit.

// Flagging (both modes)
R22. IF the user's message on a pending question is "flag" (or otherwise clearly requests flagging the question) THEN ask "Why are you flagging this question?" STOP until user responds.
R23. IF the user gives the flag reason THEN append an entry to `extracted/flagged_questions_<arg>.md` containing: unit number and title, question number, the full question entry (Teach, Question, Answer key), the user's reason verbatim, and today's date.
R23a. IF `extracted/flagged_questions_<arg>.md` does not exist THEN create it first with frontmatter: `name: flagged_questions_<arg>`, `source: questions_<arg>.md`.
R24. IF the flag entry is saved THEN confirm in one line, mark the question flagged — not graded, excluded from both the correct count and the total — and move to the next question. In teach mode, display the Teach field before the Question field of the next question.
R25. R22–R24 override R13–R18: "flag" is neither an answer nor a skip. Do not grade it, do not mark it wrong, do not display the Answer key in the session.

// English reference
R26. IF the source material is in a non-English language OR uses discipline-specific scientific terminology AND the user's answer is marked correct THEN append: `**English reference:** <standard English name>`.
R27. Do NOT append the English reference after wrong answers.

// Wrap up (both modes)
R28. IF the last question of the last unit has been graded, skipped, or flagged THEN display the final score as (correct / total) — skips count as wrong; flagged questions are excluded from the total — list the questions marked wrong or skipped with their unit titles, list any flagged questions, and output a one-paragraph summary of the weak areas.

// Catch-all
R29. IF any condition not covered by R1–R28 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Usage

```
/generate_questions chapter2      ← run this first
/learn chapter2                   ← first pass: teach then ask
/learn chapter2 no_context        ← review pass: blind questions, score at the end
```
