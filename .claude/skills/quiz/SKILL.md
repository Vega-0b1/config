---
name: quiz
description: Quiz the user on course material using extracted notes from the extracted/ directory in the current working directory.
---

Quiz the user on the specified week or topic.

## Rules

// Mode selection
R1.  IF `extracted/questions_<arg>.md` exists THEN use Mode A (R5–R14).
R2.  IF `extracted/questions_<arg>.md` does not exist AND a raw notes file for the argument exists THEN use Mode B (R15–R24).
     Notify the user: "No pre-audited questions found. Falling back to on-the-fly generation. Run /generate_questions <arg> for better results."
R3.  IF neither file exists THEN stop and tell the user. Do not generate questions.
R4.  R1 overrides R2: IF both files exist THEN always use Mode A.

// Mode A — Pre-generated questions
R5.  IF about to display a question (Mode A) THEN first display that question's `Teach:` field verbatim, framed by a Unicode line before and after:
     ────────────────────────────────────────────────────────────────
     <Teach field content>
     ────────────────────────────────────────────────────────────────
R6.  Do NOT display `Tests` or `Audit` fields.
R7.  Ask each question one at a time, in the order they appear in the file.
R8.  Display only the `Question` field.
R9.  IF the user's answer contains the key idea(s) from the `Answer key` THEN mark correct.
R10. IF the user's answer is missing the key idea(s) OR contains a factually incorrect claim THEN mark wrong.
R11. R10 overrides R9: IF the answer contains the key idea AND a factually incorrect claim THEN mark wrong.
R12. IF the answer is marked wrong THEN re-display the relevant teach content and explain it more concretely, then ask the same question again.
R13. Track score as (correct / total questions asked). Display final score summary after the last question.
R14. Do not ask "Ready to continue?" — proceed immediately.

// Mode B — On-the-fly generation
R15. Before generating a question, verify that every concept required to answer it is explicitly stated in the notes. IF any concept is absent THEN drop the question.
R16. Each question MUST require the user to explain a mechanism, describe a scenario, or contrast two ideas.
     A question answerable by pattern-matching a single phrase is prohibited.
R17. IF the notes state a fact without explaining the reason AND the candidate question asks "why" about that fact AND adding the reason as context before the question would make it answerable THEN include the reason as question context.
R18. IF the notes state a fact without explaining the reason AND the candidate question asks "why" about that fact AND the reason cannot be derived from the notes THEN drop the question.
     // R17 fires first; R18 fires only if R17 is not possible.
R19. IF a question involves an algorithm, protocol, or multi-step process THEN display the relevant steps before asking.
R20. IF a question involves a math formula THEN display the formula with a Legend block before asking.
R21. Ask one question at a time. Wait for the user's answer before proceeding.
R22. IF the user sends a clarifying question THEN answer it fully, then re-display the current unanswered question at the bottom.
R23. IF the user's answer is marked wrong THEN re-explain the concept more concretely, then ask the same question again before moving on.
R24. Cover at least one question per `##` section heading in the notes. Do not stop before all sections are covered.

// Catch-all
R25. IF any condition not covered by R1–R24 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Usage

```
/quiz chapter2
/quiz wk8
```
