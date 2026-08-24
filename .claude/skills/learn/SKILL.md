---
name: learn
description: Teach the user course material concept by concept, then check understanding with questions. `/learn week1` drills what the professor actually taught that week; `/learn chapter1` drills the textbook chapter. Both deliver every question in their file — there is no filter. Pass no_context for a blind review mode that hides the teaching content and just scores answers. Say "flag" on a question to log it with a reason for later processing. Say "en" on a question to see its English translation when the material is not in English. `/learn save` writes progress to disk mid-session; `/learn resume` picks up where you left off in a new chat. Requires a pre-generated questions file from /generate_questions. Week files live in extracted/class/week<N>/, chapter files in extracted/textbook/chapters/chapter<N>/.
---

Deliver course material question by question using a pre-generated questions file. `/learn` is a delivery engine — it does not generate content or questions. Those come from `/generate_questions`.

Two topics, two files, both delivered in full:

- `/learn week1` — the class material the professor delivered in week 1. This is the study list for a course you are currently taking.
- `/learn chapter1` — the textbook chapter. This is the reference bank: everything the book explains, whether the course reached it or not.

Which file to run is the only scoping decision, and it is made by the topic argument. There is no priority tier, no core subset, and no `+` suffix — `/generate_questions` writes no `Priority` field for anything to filter on.

Two modes: **teach** (default) shows each question's Teach field before asking — first contact with material. **review** (`no_context` flag) hides all Teach fields and asks blind — retrieval practice for material already learned. The modes differ only in Teach field visibility: in both, a graded answer (right or wrong) shows the answer and moves on. Say "flag" on any question to log it with a reason to a flagged-questions file for later processing. Say "en" on any question to see its English translation, when the questions file carries one.

## Rules

// Mode selection & loading
R1.  IF the arguments contain `no_context` or `--no_context` THEN mode = review; remove that token from the arguments.
R1a. IF more than one argument remains after removing the mode flag (R1) THEN stop and ask the user which one is the topic. STOP until user responds.
R1b. IF the arguments contain `core`, `--core`, or a topic ending in `+` THEN remove that token or suffix and print one line: "Tiering is gone — `/learn <topic>` delivers the whole file. Use `/learn week<N>` for what the professor taught." Then proceed. Do NOT stop and do NOT treat it as a filter.
     // Commentary: both named a filter that no longer exists. Erroring on muscle memory would punish the user for a change they did not make; accepting the token silently would leave them believing it still scopes the session. `chapter1+` must still find `extracted/questions_chapter1.md`, so the suffix is stripped before the R3 lookup.

// Delivery scope
R1c. Deliver EVERY entry in the loaded file. There is no filter, no subset, and no rule that skips an entry on the basis of any field it carries.
R1d. IF an entry carries a `Priority:` field THEN ignore it. It is legacy data written by an older `/generate_questions`; it scopes nothing.
     // Commentary: eight questions files on this system predate the split and still carry `Priority: core | supporting`. /generate_questions R5e1 deliberately leaves those fields in place rather than churning files the user has been studying. Reading them here would resurrect the tier this change removed.
R2.  IF the arguments do not contain a no_context flag THEN mode = teach.
R2a. The mode flag (R1) and the topic argument are independent and may be given in either order.
     // Example: `/learn week1 no_context` = review mode over week 1's class material.
// File lookup
R3.  IF <arg> normalizes to a week — `week<N>` or `wk<N>` — THEN look for `extracted/class/week<N>/questions_week<N>.md`.
R3a. IF <arg> normalizes to a chapter — `chapter<N>` or `capitulo<N>` — THEN look for `extracted/textbook/chapters/chapter<N>/questions_chapter<N>.md` (or `capitulo<N>/questions_capitulo<N>.md` for Spanish-language classes).
R3b. IF <arg> does not match either pattern THEN look for `extracted/questions_<arg>.md` as a fallback.
     // Commentary: the fallback keeps any questions file not yet migrated to the new layout reachable.
R4.  IF the file exists THEN load it and proceed to R7.
R4a. IF the loaded file contains zero units or zero questions THEN stop and tell the user: "Questions file is empty — re-run /generate_questions <arg>."
R5.  IF the file does not exist THEN stop and tell the user: "Run /generate_questions <arg> first."
R6.  IF no <arg> is given THEN list all `questions_*.md` files under `extracted/textbook/chapters/` and `extracted/class/` and ask the user to pick one. STOP until user responds.

// Unit and question delivery
// Course scope notice
R6a. After loading the file per R3–R4 and before the first question: IF the topic is a chapter AND the class `CLAUDE.md` holds a `### Course Scope` entry listing that chapter as not covered THEN print one line saying the course does not cover it. Then proceed normally.
     // Example: `Note: CS4470 does not cover chapter 7 — this is textbook material beyond the course.`
R6a1. IF the topic is a week — `week<N>` or `wk<N>` — THEN print no scope notice, whatever the `### Course Scope` entry says. Material the professor delivered is in scope by definition.
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
R11. Do NOT display `Concept`, `Source quote`, `Tests`, `Audit`, or a legacy `Priority` field at any point.
     // Commentary: `Concept` is the merge key /generate_questions R13f writes; it names the answer, so showing it before the user answers gives the question away. A legacy `Priority` field is inert under R1d, and displaying it would invite treating `supporting` entries as skippable when nothing skips them.
R11c. `Source quote` is barred in BOTH modes, and most strictly in review. It is the raw source sentence /generate_questions R13g records for its R18b audit, and it states the answer outright.
     // Commentary: R9 hides the Teach field in review mode precisely so retrieval is unaided. `Source quote` is a denser giveaway than the Teach field it was used to check — displaying it would defeat both modes at once.
R11d. R11 is a denylist and R8 is the allowlist. IF an entry carries a field R8 does not name THEN do NOT display it, whether or not R11 lists it.
     // Commentary: R11 named four fields and a fifth was added to the format later. A denylist that has to be amended every time /generate_questions gains a field will eventually leak one; R11d makes silence the default.
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
R23. IF the user gives the flag reason THEN append an entry to `flagged_questions_<arg>.md` in the same directory as the loaded questions file, containing: unit number and title, question number, the full question entry (Teach, Question, Answer key, Elaboration), the user's reason verbatim, today's date, and a `**Status:**` field per R23b.
     // Commentary: the flagged file lives next to the questions file it references — `extracted/textbook/chapters/chapter1/flagged_questions_chapter1.md` or `extracted/class/week1/flagged_questions_week1.md`.
R23a. IF the flagged-questions file does not exist THEN create it first with frontmatter: `name: flagged_questions_<arg>`, `source: questions_<arg>.md`.
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
R28a. The R28 score line names the topic and the file's full size, with no filter annotation. Every question in the file was delivered, so the total IS the file.
     // Example: `**Final score: 24 / 33** (week1 — all 33 questions in this file.)`
R28b. IF every delivered question was flagged THEN display no score. Say instead: "All N questions were flagged — no score. Flagged questions are in `extracted/flagged_questions_<arg>.md`." R28b overrides R28.
     // Commentary: R24 excludes flagged questions from the total, so an all-flagged run makes the R28 score line read "0 / 0".
R28c. IF the topic was a chapter AND `extracted/class/` contains any `week<N>/questions_week<N>.md` files THEN, after the R28 score, print one line saying this was textbook coverage and naming the week files as the record of what was actually taught.
     // Example: `This was the textbook chapter. What the professor covered is in class/week1/questions_week1.md and class/week2/questions_week2.md.`
     // Commentary: the two files are independent and neither is a subset of the other. A strong score on a chapter says nothing about exam readiness, and this is the one moment the user is thinking about coverage.

// Save & resume
R30.  IF the argument is `save` THEN this is a save request, not a topic. R30 applies only when a `/learn` session is active (a questions file is loaded and at least one question has been displayed).
R30a. IF `save` is invoked with no active session THEN say "Nothing to save — no /learn session is running." Do NOT stop under R35.
R30b. IF `save` is invoked THEN write a progress file to the same directory as the loaded questions file, named `progress_<arg>.md` (e.g. `progress_chapter3.md`, `progress_week1.md`).
R30c. The progress file contains exactly these fields:
       - `topic:` — the normalized topic argument (e.g. `chapter3`, `week1`)
       - `mode:` — `teach` or `review`
       - `questions_file:` — absolute path to the loaded questions file
       - `current_unit:` — unit number the session is on
       - `current_question:` — question number within the unit (1-indexed) of the NEXT question to deliver
       - `correct:` — count of questions marked correct so far
       - `wrong:` — count of questions marked wrong or skipped so far
       - `flagged:` — count of questions flagged so far
       - `wrong_list:` — list of (unit number, question number, question text) for each wrong/skipped question
       - `flagged_list:` — list of (unit number, question number, question text) for each flagged question
       - `saved_at:` — ISO 8601 timestamp
R30d. IF the progress file already exists THEN overwrite it.
      // Commentary: only one save point per topic. The user wants to resume from one place, not manage save slots.
R30e. After writing the file, confirm in one line: "Progress saved — question N of M. `/learn resume` in a new chat to continue."
R30f. R30 overrides R13–R18: `save` is neither an answer nor a skip. Do not grade it, do not mark it wrong.
      // Commentary: mirrors the R25 protection for `flag` and R12f for `en`.

R31.  IF the argument is `resume` THEN this is a resume request, not a topic.
R31a. Scan all `progress_*.md` files under `extracted/class/` and `extracted/textbook/chapters/` in the current class directory.
R31b. IF exactly one progress file exists THEN load it and proceed to R31e.
R31c. IF multiple progress files exist THEN list them with their topic, saved-at timestamp, and score so far. Ask the user to pick one. STOP until user responds.
R31d. IF no progress file exists THEN say "No saved sessions found." Do NOT stop under R35.
R31e. Load the questions file from the `questions_file:` path in the progress file. IF the file does not exist THEN say "Questions file missing — cannot resume." Do NOT stop under R35.
R31f. Restore mode from the progress file's `mode:` field.
R31g. Restore the correct, wrong, and flagged counts and their lists from the progress file.
R31h. Skip to the unit and question recorded in `current_unit:` and `current_question:`. Deliver that question per the normal flow (R7–R12) as if the session had just reached it.
      // Commentary: questions before this point were already graded in the prior session. Their scores are carried in the progress file.
R31i. After the resumed session ends normally (R28), delete the progress file.
      // Commentary: a completed session has no resume point. Leaving the file would let `/learn resume` reload a finished run.
R31j. IF the user saves again during a resumed session (R30) THEN overwrite the same progress file with the updated state.

// Catch-all
R35. IF any condition not covered by R1–R31 (including all lettered sub-rules) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Usage

```
/generate_questions week1         ← run this first
/learn week1                      ← first pass over week 1's class material: teach then ask
/learn week1 no_context           ← review pass over the same: blind questions

/generate_questions chapter2      ← the textbook path
/learn chapter2                   ← first pass over the whole chapter
/learn chapter2 no_context        ← review pass over the whole chapter

/learn save                       ← save progress to disk mid-session, then close the chat
/learn resume                     ← pick up where you left off in a new chat
```

Every run delivers the entire file. To study less, pick a narrower topic — that is what `week<N>` is.

In-session keywords, typed in reply to a pending question:

```
en        ← show this question's English translation, then re-ask (R12b)
flag      ← log the question with a reason, skip grading it (R22)
skip      ← give up on the question, see the answer, count it wrong (R17)
save      ← write progress to disk so you can resume in a new chat (R30)
```
