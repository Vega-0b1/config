---
name: learn
description: Teach the user course material concept by concept, then check understanding with questions. Pass no_context for a blind review mode that hides the teaching content and just scores answers. Pass core to deliver only the questions tagged core, skipping supporting material. Say "flag" on a question to log it with a reason for later processing. Say "en" on a question to see its English translation when the material is not in English. Requires a pre-generated questions file from /generate_questions. Reads from extracted/ in the current directory.
---

Deliver course material question by question using a pre-generated questions file. `/learn` is a delivery engine — it does not generate content or questions. Those come from `/generate_questions`.

Two modes: **teach** (default) shows each question's Teach field before asking — first contact with material. **review** (`no_context` flag) hides all Teach fields and asks blind — retrieval practice for material already learned. The modes differ only in Teach field visibility: in both, a graded answer (right or wrong) shows the answer and moves on. Say "flag" on any question to log it with a reason to a flagged-questions file for later processing. Say "en" on any question to see its English translation, when the questions file carries one.

One filter, independent of the mode: **`core`** delivers only the questions tagged `Priority: core` — the concepts that serve the chapter's own stated Objectives and Key Points — and skips the supporting material. Use it when time is short; use the unfiltered run for full coverage. The two flags compose in either order.

## Rules

// Mode selection & loading
R1.  IF the arguments contain `no_context` or `--no_context` THEN mode = review; remove that token from the arguments.
R1a. IF more than one argument remains after removing the mode flag (R1) and the filter flag (R1b) THEN stop and ask the user which one is the topic. STOP until user responds.
R1b. IF the arguments contain `core` or `--core` THEN filter = core-only; remove that token from the arguments.
R1c. IF filter = core-only THEN deliver only entries whose `Priority` field begins with `core`. Skip all other entries without displaying them and without counting them in the total.
R1d. IF no core flag is given THEN filter = all; deliver every entry regardless of its `Priority` field.
R1e. IF filter = core-only AND the loaded file contains zero entries whose `Priority` field begins with `core` THEN stop and tell the user: "No core questions in this file — run without the core flag, or re-run /generate_questions <arg>."
R1f. IF filter = core-only AND the loaded file's entries have no `Priority` field at all THEN consult the class's `## Source Profile` in `CLAUDE.md`. IF its generation mode is `capped` THEN stop and tell the user: "<class> is untiered by design — its textbook has no objectives or key points to rank against. Run without the core flag." ELSE stop and tell the user: "This questions file predates priority tagging — re-run /generate_questions <arg>, or run without the core flag."
R1g. IF filter = core-only AND every entry reads `Priority: untiered` THEN stop and give the same untiered-by-design message as R1f.
     // Commentary: two different causes need two different messages. Telling someone to regenerate a file that has no anchor to tier against sends them to do work that cannot succeed.
R1h. `untiered` is not `supporting`. An `untiered` file is delivered in full by an unfiltered run exactly as a tiered file is.
     // Commentary: silently delivering everything when the user asked for core-only would misrepresent the session length they signed up for. Refusing with the right reason is the point of R1f–R1g.
R1i. R1f and R1g override R1e. IF the file has no `Priority` field at all THEN R1f is the message. IF every entry reads `Priority: untiered` THEN R1g is the message. R1e fires only on a tiered file whose entries are all `supporting`.
     // Commentary: R1f's and R1g's conditions are both subsets of R1e's — a file with no Priority field also has zero core entries. Without this rule the generic "re-run /generate_questions" message wins by position, which is the exact wrong advice R1f exists to avoid.
R2.  IF the arguments do not contain a no_context flag THEN mode = teach.
R2a. R1 and R1b are independent. Both flags may be given together in either order.
     // Example: `/learn chapter1 core no_context` = review mode, core questions only.
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
R8c. R8b overrides the global CLAUDE.md response-style ban on `---` horizontal rules, for the Teach/Question separator only.
     // Commentary: that ban is scoped to terminal output, where `---` renders as three literal dashes. /learn's output is markdown-rendered, so the rule is the correct separator here. Naming the override keeps the two from being read as a conflict.
R9.  IF mode = review THEN do NOT display Teach fields at any point.
     // Commentary: review mode is retrieval practice — showing the material before the question makes it an open-book test of text on screen.
R10. Do NOT rewrite, summarize, or add to the Teach field.
R11. Do NOT display `Priority`, `Tests`, or `Audit` fields at any point.
     // Commentary: Priority is read by R1c to filter and is never shown. Displaying it mid-session invites treating `supporting` questions as skippable.
R11a. Do NOT display the `Elaboration` field before the user answers, in either mode. It is post-grade material, released only under R17 and R18.
R12. Ask one question at a time. Display only the `Question` field, rendered as a level-3 markdown heading with a `❓` anchor: `### ❓ <question text>`. Do NOT display the next question until the user answers the current one.

// Translation on demand (both modes)
R12a. Do NOT display `Teach_EN` or `Question_EN` when delivering a question. They are released only on request, per R12b.
R12b. IF the user's message on a pending question is `en` (or otherwise clearly requests the English translation) THEN display the translation per R12c, then re-display the current unanswered question per R20. Do NOT advance.
R12c. Displaying the translation = output the heading `**English translation**`, then `Teach_EN` verbatim IF mode = teach, then `Question_EN` verbatim.
     // Commentary: Teach before Question mirrors the delivery order set by R8 and R12, so the translation reads in the same sequence as the Spanish it mirrors.
R12c1. The R12c heading is `**English translation**`, NOT `**English reference:**`. The latter belongs to R26 and means something else.
     // Commentary: R26 appends the standard English name of a single term after a correct answer. R12c prints a whole entry on request. Two different outputs must not carry one label.
R12d. IF mode = review THEN do NOT display `Teach_EN`. Only `Question_EN` is shown.
     // Commentary: review mode hides the Teach field (R9). Showing its translation would turn retrieval practice back into an open-book read.
R12e. IF the entry has no `Teach_EN` and no `Question_EN` field THEN say in one line that this questions file carries no translations, then re-display the question per R20. Do NOT stop under R29.
R12f. R12a–R12e override R13–R18: `en` is neither an answer nor a skip. Do not grade it, do not mark it wrong, do not display `Answer key` or `Elaboration`.
     // Commentary: mirrors R25, which gives `flag` the same protection. Without this, `en` reads as a wrong answer and burns the question.
R12g. A question the user asked `en` on remains pending: it is graded normally when answered, and counts in both the correct count and the total.
     // Commentary: unlike `flag` (R24), `en` is not a terminal action on the question — it changes nothing about scoring.
R12h. IF the user sends `en` again on the same question THEN re-display the same translation. No state changes.

// Grading (both modes)
R13. IF the user's answer contains the idea in the `Answer key` THEN mark correct.
     Correct answers need not match the phrasing in the Answer key.
     // Example: Answer key = "TCP throttles the sender when the network is congested."
     //          User says  = "TCP slows you down if the network is busy." → CORRECT (R13).
R13a. IF a question's Teach field contains a formula AND the user's answer correctly explains the underlying mechanism conceptually (without citing formula terms or variable names) THEN mark correct.
R13b. R13a overrides R14: a missing formula citation alone is not sufficient to mark an answer wrong if the conceptual mechanism is correctly explained.
R13c. Grade against the `Answer key` field ONLY. Nothing in the `Elaboration` field is required for a correct grade.
     // Commentary: Answer key states the minimum sufficient answer (generate_questions R16a); Elaboration is the mechanism, example, or consequence beyond it. Reading Elaboration as a grading requirement is what made brief-but-correct answers fail.
R13d. IF an entry has no `Elaboration` field AND its `Answer key` runs longer than one sentence THEN grade against its first sentence alone.
     // Commentary: backward compatibility for questions files generated before the two-field format. Without this, a stale file keeps grading as a conjunction of every clause.
R14. IF the user's answer is missing the idea in the `Answer key` THEN mark wrong.
R15. IF the user's answer contains a factually incorrect claim THEN mark wrong.
R16. R15 overrides R13: IF the answer contains the key idea AND a factually incorrect claim THEN mark wrong.
     // Example: User says "TCP throttles the sender by dropping packets." → WRONG (R16): mechanism claim is wrong.

// Result display (both modes)
R16a. IF marking an answer correct THEN begin the result with `✅ **Correct**`.
R16b. IF marking an answer wrong — including a skip under R17 — THEN begin the result with `❌ **Wrong**`.
R16c. R16a–R16b set the result prefix only. They do not change what R13–R18 require the result to contain.

// Skip (both modes)
R17. IF the user's message declines to answer rather than attempts an answer (e.g. "skip", "pass", "next", "move on", "I don't know") THEN acknowledge it, display the correct answer per R18a, mark the question wrong as skipped, and advance per R19.

// Wrong answer flow (both modes)
R18. IF the answer is marked wrong THEN state wrong, display the correct answer per R18a, give a one-sentence explanation of the key idea missed, and advance per R19. Do NOT re-teach, do NOT re-ask.
R18a. Displaying the correct answer = display the `Answer key`, followed by the `Elaboration` field when the entry has one.
     // Commentary: the grading threshold narrowed under R13c, but the explanation the user gets after a miss did not. R18a is the single definition of that display, so R17 and R18 stay in step.
R19. IF a question has been graded, skipped, or flagged THEN advance to the next question regardless of the outcome. IF mode = teach THEN display the next question's Teach field before its Question field, per R8 and R8b.
     // Commentary: R19 is the single definition of advancing. R17, R18, and R24 delegate to it rather than restating it, so the teach-mode display requirement has one place to change.

// Pacing
R20. IF the user sends a clarifying or follow-up question THEN answer it fully, then re-display the current unanswered question. Do not ask "Ready to continue?"
R21. Move through units in order. There is no correctness gate on advancing to the next question or unit.

// Flagging (both modes)
R22. IF the user's message on a pending question is "flag" (or otherwise clearly requests flagging the question) THEN ask "Why are you flagging this question?" STOP until user responds.
R23. IF the user gives the flag reason THEN append an entry to `extracted/flagged_questions_<arg>.md` containing: unit number and title, question number, the full question entry (Teach, Question, Answer key, Elaboration), the user's reason verbatim, and today's date.
R23a. IF `extracted/flagged_questions_<arg>.md` does not exist THEN create it first with frontmatter: `name: flagged_questions_<arg>`, `source: questions_<arg>.md`.
R24. IF the flag entry is saved THEN confirm in one line, mark the question flagged — not graded, excluded from both the correct count and the total — and advance per R19.
R25. R22–R24 override R13–R18: "flag" is neither an answer nor a skip. Do not grade it, do not mark it wrong, do not display the Answer key or Elaboration in the session.

// English reference
R26. IF the user's answer is marked correct AND (the source material is in a non-English language OR the source material uses discipline-specific scientific terminology) THEN append: `**English reference:** <standard English name>`.
     // Commentary: the correctness test is the outer condition. Without the parentheses the rule reads as though a non-English source triggers the append regardless of grade, which contradicts R27.
R27. Do NOT append the English reference after wrong answers, skips, or flags.

// Wrap up (both modes)
R28. IF the last delivered question of the last unit has been graded, skipped, or flagged THEN display the final score as (correct / total) — skips count as wrong; flagged questions are excluded from the total — list the questions marked wrong or skipped with their unit titles, list any flagged questions, and output a one-paragraph summary of the weak areas.
R28a. IF filter = core-only THEN the R28 score line MUST name the filter and the file's full size.
     // Example: `**Final score: 12 / 16** (core only — 16 of 33 questions in this file)`
     // Commentary: without this the user cannot tell a 16-question core pass from a 16-question file.
R28b. IF every delivered question was flagged THEN display no score. Say instead: "All N questions were flagged — no score. Flagged questions are in `extracted/flagged_questions_<arg>.md`." R28b overrides R28.
     // Commentary: R24 excludes flagged questions from the total, so an all-flagged run makes the R28 score line read "0 / 0".

// Catch-all
R29. IF any condition not covered by R1–R28 (including all lettered sub-rules) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Usage

```
/generate_questions chapter2      ← run this first
/learn chapter2                   ← first pass: teach then ask, everything
/learn chapter2 core              ← first pass, core concepts only
/learn chapter2 no_context        ← review pass: blind questions, score at the end
/learn chapter2 core no_context   ← review pass, core concepts only
```

In-session keywords, typed in reply to a pending question:

```
en        ← show this question's English translation, then re-ask (R12b)
flag      ← log the question with a reason, skip grading it (R22)
skip      ← give up on the question, see the answer, count it wrong (R17)
```
