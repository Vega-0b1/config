---
name: learn
description: Teach the user course material concept by concept, then check understanding with questions. Delivers the core questions by default — what the professor actually taught. Append + to the topic (chapter1+) for full textbook coverage including material the course skipped. Pass no_context for a blind review mode that hides the teaching content and just scores answers. Say "flag" on a question to log it with a reason for later processing. Say "en" on a question to see its English translation when the material is not in English. Requires a pre-generated questions file from /generate_questions. Reads from extracted/ in the current directory.
---

Deliver course material question by question using a pre-generated questions file. `/learn` is a delivery engine — it does not generate content or questions. Those come from `/generate_questions`.

Two modes: **teach** (default) shows each question's Teach field before asking — first contact with material. **review** (`no_context` flag) hides all Teach fields and asks blind — retrieval practice for material already learned. The modes differ only in Teach field visibility: in both, a graded answer (right or wrong) shows the answer and moves on. Say "flag" on any question to log it with a reason to a flagged-questions file for later processing. Say "en" on any question to see its English translation, when the questions file carries one.

One filter, independent of the mode, and it is **on by default**. A bare `/learn chapter1` delivers only the questions tagged `Priority: core` — the concepts the professor's own material covers, or failing that the ones serving the chapter's stated Objectives and Key Points. Append `+` to the topic (`/learn chapter1+`) to get everything, including the textbook material the course skipped.

The default is the common case: you are studying for a class you are currently taking. The `+` run is the deliberate one — a chapter the professor passed over, or the whole book after the semester ends. Nothing is ever deleted by the filter; `+` always reaches it.

IF a file has no core tier — because the class has no anchor to rank against — then a bare run delivers everything and says so. It never refuses.

## Rules

// Mode selection & loading
R1.  IF the arguments contain `no_context` or `--no_context` THEN mode = review; remove that token from the arguments.
R1a. IF more than one argument remains after removing the mode flag (R1) and the deprecated core token (R1b) THEN stop and ask the user which one is the topic. STOP until user responds.
R1b. IF the arguments contain `core` or `--core` THEN remove that token and print one line: "`core` is the default now — delivering core questions. Use `<topic>+` for everything." Do NOT treat it as a filter and do NOT stop.
     // Commentary: the token named an opt-in that is now the default, so it is redundant rather than wrong. Erroring on muscle memory would punish the user for a change they did not make; ignoring it silently would leave them believing a flag is doing work.

// Filter resolution — R1c–R1d run on the arguments; R1e resolves against the loaded file
R1c. IF the topic argument ends in `+` THEN requested filter = all. Strip the `+` before the R3 file lookup.
     // Example: `/learn chapter1+` loads `extracted/questions_chapter1.md` and delivers every entry.
R1d. IF the topic argument does not end in `+` THEN requested filter = core-only.
     // Commentary: the common case is studying for the class you are currently in, and that is the case that should need no flag. Full textbook coverage is the deliberate act — after the course ends, or for a chapter the professor skipped — so it is what carries the marker.
R1e. After loading the file per R3–R4: IF requested filter = core-only AND the file contains zero entries whose `Priority` field begins with `core` THEN set filter = all and print one line naming the cause per R1e1–R1e3. Do NOT stop.
     // Commentary: this replaces three refusal rules that were correct when `core` was an explicit opt-in — the user had asked for something the file could not give. As a default it must never refuse, or every untiered class on the system becomes unrunnable without a flag the user has no reason to know about.
R1e1. IF every entry reads `Priority: untiered` THEN the line is: "<class> has no anchor to tier against — delivering all N questions."
R1e2. IF the entries carry no `Priority` field at all THEN the line is: "This questions file predates priority tagging — delivering all N. Re-run /generate_questions <arg> to tier it."
R1e3. IF the entries are tiered but none is `core` THEN the line is: "No core questions in this file — delivering all N."
R1e4. R1e1 and R1e2 override R1e3. A file with no `Priority` field also has zero `core` entries, so all three conditions can hold at once; the most specific cause is the one to name.
R1f. IF filter = core-only THEN deliver only entries whose `Priority` field begins with `core`. Skip all other entries without displaying them and without counting them in the total.
R1g. IF filter = all THEN deliver every entry regardless of its `Priority` field.
R1h. `untiered` is not `supporting`. An `untiered` file is delivered in full, exactly as a tiered file is under `+`.
R2.  IF the arguments do not contain a no_context flag THEN mode = teach.
R2a. The mode flag (R1) and the `+` suffix (R1c) are independent. Both may be given, in either order.
     // Example: `/learn chapter1+ no_context` = review mode, every question.
R3.  IF <arg> is given THEN look for `extracted/questions_<arg>.md`.
R4.  IF the file exists THEN load it and proceed to R7.
R4a. IF the loaded file contains zero units or zero questions THEN stop and tell the user: "Questions file is empty — re-run /generate_questions <arg>."
R5.  IF the file does not exist THEN stop and tell the user: "Run /generate_questions <arg> first."
R6.  IF no <arg> is given THEN list all `extracted/questions_*.md` files and ask the user to pick one. STOP until user responds.

// Unit and question delivery
// Course scope notice
R6a. After loading the file per R3–R4 and before the first question: IF the class `CLAUDE.md` holds a `### Course Scope` entry listing the loaded chapter as not covered THEN print one line saying the course does not cover it. Then proceed normally.
     // Example: `Note: CS4470 does not cover chapter 7 — this is textbook material beyond the course.`
R6b. R6a is a notice, not a gate. Do NOT refuse, do NOT ask for confirmation, and do NOT change the filter.
     // Commentary: studying a chapter the course skipped is a deliberate act — after the final, or out of interest. The notice sets the expectation that none of it will be on the exam; blocking it would remove the reason the questions were generated at all.
R6c. IF the loaded chapter is in scope, or the class has no `### Course Scope` entry, THEN print no notice.
R6d. IF a `### Course Scope` entry exists but carries no derivable chapter list — its `covers` field reads `NOT DETERMINED`, is empty, or names no chapter — THEN treat the class as having no scope entry and print no notice. Do NOT stop under R29.
     // Commentary: mirrors /generate_questions R0j3. /updateclass R26d writes such an entry when a syllabus defers its schedule elsewhere. The chapter is then neither in scope nor out of it, which matched no branch of R6a–R6c and sent a plain `/learn chapter3` to the catch-all.

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
R11. Do NOT display `Concept`, `Priority`, `Tests`, or `Audit` fields at any point.
     // Commentary: Priority is read by R1f to filter and is never shown. Displaying it mid-session invites treating `supporting` questions as skippable. `Concept` is the merge key /generate_questions R13f writes; it names the answer, so showing it before the user answers gives the question away.
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
R23. IF the user gives the flag reason THEN append an entry to `extracted/flagged_questions_<arg>.md` containing: unit number and title, question number, the full question entry (Teach, Question, Answer key, Elaboration), the user's reason verbatim, today's date, and a `**Status:**` field per R23b.
R23a. IF `extracted/flagged_questions_<arg>.md` does not exist THEN create it first with frontmatter: `name: flagged_questions_<arg>`, `source: questions_<arg>.md`.
R23b. The `**Status:**` field of a newly written flag is `OPEN`. Do NOT write any other value at flag time, and do NOT judge the flag's merit.
     // Commentary: /generate_questions R5k3 reads this field to tell a question the user deliberately removed from one that is merely flagged. Without it every flag this skill writes is invisible to that rule, and a merge re-adds the rejected question. The value is `OPEN` because at flag time nothing has been decided — the user has said only that something is wrong with the question.
R23c. Label the question number field `**Question no.:**` and the question text field `**Question:**`. Do NOT use `**Question:**` for both.
     // Commentary: `~/edu/network/extracted/flagged_questions_chapter1.md` carries two `**Question:**` lines in one entry, which makes the entry unparseable by field name.
R23d. Do NOT rewrite the `**Status:**` field of an existing entry. Resolving a flag is a deliberate act taken outside a `/learn` session.
R24. IF the flag entry is saved THEN confirm in one line, mark the question flagged — not graded, excluded from both the correct count and the total — and advance per R19.
R25. R22–R24 override R13–R18: "flag" is neither an answer nor a skip. Do not grade it, do not mark it wrong, do not display the Answer key or Elaboration in the session.

// English reference
R26. IF the user's answer is marked correct AND (the source material is in a non-English language OR the source material uses discipline-specific scientific terminology) THEN append: `**English reference:** <standard English name>`.
     // Commentary: the correctness test is the outer condition. Without the parentheses the rule reads as though a non-English source triggers the append regardless of grade, which contradicts R27.
R27. Do NOT append the English reference after wrong answers, skips, or flags.

// Wrap up (both modes)
R28. IF the last delivered question of the last unit has been graded, skipped, or flagged THEN display the final score as (correct / total) — skips count as wrong; flagged questions are excluded from the total — list the questions marked wrong or skipped with their unit titles, list any flagged questions, and output a one-paragraph summary of the weak areas.
R28a. IF filter = core-only THEN the R28 score line MUST name the filter and the file's full size.
     // Example: `**Final score: 12 / 16** (core only — 16 of 33 questions in this file. Run `/learn chapter2+` for all 33.)`
     // Commentary: without this the user cannot tell a 16-question core pass from a 16-question file.
R28a1. IF filter was set to all by R1e THEN the R28 score line MUST say the file had no core tier, naming the R1e1–R1e3 cause.
     // Example: `**Final score: 24 / 33** (all 33 — this file is untiered, so there was no core subset to deliver.)`
     // Commentary: R1e prints its line before the session starts, an hour of questions earlier. Without the reminder at the score, a full run reads as though core-only silently delivered everything.
R28a2. IF filter = all because the topic ended in `+` THEN the R28 score line MUST say the run was the full file.
     // Example: `**Final score: 24 / 33** (all 33 questions — full coverage.)`
R28b. IF every delivered question was flagged THEN display no score. Say instead: "All N questions were flagged — no score. Flagged questions are in `extracted/flagged_questions_<arg>.md`." R28b overrides R28.
     // Commentary: R24 excludes flagged questions from the total, so an all-flagged run makes the R28 score line read "0 / 0".
R28c. IF `extracted/gaps_<arg>.md` exists THEN, after the R28 score, print one line naming how many topics it lists and pointing at the file.
     // Example: `⚠ 3 topics were taught but are not in the textbook — see extracted/gaps_chapter1.md. No questions exist for them.`
     // Commentary: these are topics the professor covered that the notes cannot answer, so no question in this session tested them and a good score says nothing about them. Surfacing the count at the score is the only moment the user is thinking about their coverage.
R28d. Do NOT list the gap topics individually and do NOT attempt to teach them. Name the count and the file.
     // Commentary: /generate_questions R24m deliberately records no answers for these — everything known about them is that they were taught and are absent. Improvising an explanation here would invent exactly the unaudited content that rule exists to prevent.

// Catch-all
R29. IF any condition not covered by R1–R28 (including all lettered sub-rules) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Usage

```
/generate_questions chapter2      ← run this first
/learn chapter2                   ← first pass: teach then ask, core only (the default)
/learn chapter2+                  ← first pass, everything the textbook covers
/learn chapter2 no_context        ← review pass: blind questions, core only
/learn chapter2+ no_context       ← review pass, everything
```

In-session keywords, typed in reply to a pending question:

```
en        ← show this question's English translation, then re-ask (R12b)
flag      ← log the question with a reason, skip grading it (R22)
skip      ← give up on the question, see the answer, count it wrong (R17)
```
