---
name: learn
model: haiku
effort: low
description: Deliver course material concept by concept — teach, ask, then serve the stored answers on request. `/learn week1` drills the textbook questions covering what the professor taught that week — the study list; `/learn chapter1` drills the whole textbook chapter — the reference bank. Both deliver every question in their file, there is no filter, and every question in both comes from the textbook. Questions arrive one at a time; nothing is graded and no score is kept: type "next" to see the stored answer and move on. Pass batch<N> for several questions per turn. Pass no_context for a blind review mode that hides the teaching content. Your place autosaves every 10 questions; `/learn save` forces a save now and `/learn resume` picks it up in a new chat. Requires a pre-generated questions file from /generate_questions. Week files live in extracted/class/week<N>/, chapter files in extracted/textbook/chapters/chapter<N>/.
---

Deliver course material question by question using a pre-generated questions file. `/learn` is a delivery engine — it does not generate content or questions, and it does not grade. Content comes from `/generate_questions`; the verdict comes from you.

Two topics, two files, both delivered in full:

- `/learn week1` — the textbook questions covering what the professor taught in week 1. This is the study list for a course you are currently taking.
- `/learn chapter1` — the whole textbook chapter. This is the reference bank: everything the book explains, whether the course reached it or not.

Every question in both files was generated from the textbook. The difference is scope, not source:
`/generate_questions chapter<N>` writes the pool, and `/generate_questions week<N>` copies the subset
of that pool matching what the professor covered. A week file is therefore a strict subset of the
chapter files it draws from, and each of its entries records where it came from.

Which file to run is the only scoping decision, and it is made by the topic argument.

**The loop:** teach material, ask the question, wait. You answer however you like — out loud, on paper, in your head. Type `next` and the stored answer appears. Compare it yourself, then the next question follows. Nothing you type is judged, and no score is kept.

Two modes: **teach** (default) shows each question's Teach field before asking — first contact with material. **review** (`no_context` flag) hides all Teach fields and asks blind — retrieval practice for material already learned. The modes differ only in Teach field visibility; the loop is identical in both.

## Rules

// Mode selection & loading
R1.  IF the arguments contain `no_context` or `--no_context` THEN mode = review; remove that token from the arguments.
R1a. IF more than one argument remains after removing the mode flag (R1) THEN stop and ask the user which one is the topic. STOP until user responds.
// Delivery scope
R1c. Deliver EVERY entry in the loaded file. There is no filter, no subset, and no rule that skips an entry on the basis of any field it carries.
R2.  IF the arguments do not contain a no_context flag THEN mode = teach.
R2a. The mode flag (R1) and the topic argument are independent and may be given in either order.

// File lookup
R3.  IF <arg> normalizes to a week — `week<N>` or `wk<N>` — THEN look for `extracted/class/week<N>/questions_week<N>.md`.
R3a. IF <arg> normalizes to a chapter — `chapter<N>` or `capitulo<N>` — THEN look for `extracted/textbook/chapters/chapter<N>/questions_chapter<N>.md` (or `capitulo<N>/questions_capitulo<N>.md` for Spanish-language classes).
R3b. IF <arg> does not match either pattern THEN look for `extracted/questions_<arg>.md` as a fallback.
R4.  IF the file exists THEN load it per R4b–R4d and proceed to R7.
R4a. IF `--count` reports zero questions THEN stop and tell the user: "Questions file is empty — re-run /generate_questions <arg>."

// Windowed loading — never read the whole questions file
R4b. WINDOW = 10. This is the number of questions loaded into context at a time.
R4c. Loading the file = four small reads, never a whole-file read:
       1. The frontmatter — read the first 10 lines.
       2. The question index — `grep -n '^#### Q' <file> | cut -d: -f1 | nl -ba`. This yields one row per question: POSITION, then the line it starts on. It carries no `Q<n>` labels.
       3. The unit index — `grep -n '^## Unit ' <file>`, for unit headings and titles.
       4. The first window — from the line shown at position 1 through the line before the line shown at position WINDOW+1, or end of file when the index has no such position.
R4c1. Address questions by their ABSOLUTE POSITION — the left column of the R4c step-2 index — never by the `Q<n>` label a heading carries.
      // Commentary: `Q<n>` restarts at Q1 in every unit and multiple `Q1`s exist in every multi-unit file. The step-2 command strips labels deliberately.
R4c2. IF the window edge is being determined THEN read it from the step-2 index by POSITION lookup. Do NOT compute it from question labels, from line counts, or by estimating lines-per-question.
R4d. IF the currently loaded window is exhausted AND unloaded questions remain THEN load the next WINDOW questions by the same line-range read. Do NOT re-read the frontmatter or the index.
R4e. IF a question outside the loaded window is needed for any reason THEN load its window first.
R4f. The index from R4c step 2 is internal metadata. Do NOT display it, and do NOT display line numbers or window boundaries to the user.
R4g. Window boundaries are invisible to the user. Do NOT announce loading, do NOT say "loading the next 10", and do NOT pause at a window edge.
R4h. IF the index shows WINDOW or fewer questions in total THEN the first window is the whole file and R4d never fires.
R5.  IF the file does not exist THEN stop and tell the user: "Run /generate_questions <arg> first."
R6.  IF no <arg> is given THEN list all `questions_*.md` files under `extracted/textbook/chapters/` and `extracted/class/` and ask the user to pick one. STOP until user responds.

// Course scope notice
R6a. After loading the file per R3–R4 and before the first question: IF the topic is a chapter AND the class `CLAUDE.md` holds a `### Course Scope` entry listing that chapter as not covered THEN print one line saying the course does not cover it. Then proceed normally.
R6a1. IF the topic is a week THEN print no scope notice. A week file holds only questions the professor's own material selected, so it is in scope by construction.
R6b. R6a is a notice, not a gate. Do NOT refuse, do NOT ask for confirmation.
R6d. IF a `### Course Scope` entry exists but carries no derivable chapter list — `covers` reads `NOT DETERMINED`, is empty, or names no chapter — THEN treat the class as having no scope entry and print no notice. Do NOT stop under R35.

// Unit and question delivery
R7.  IF starting a new unit THEN display "Unit X of Y — <title>" as a level-2 markdown heading: `## Unit X of Y — <title>`.
R8.  IF mode = teach AND about to display a question THEN first display that question's `Teach:` field verbatim as a markdown blockquote — prefix every line with `> `. IF the entry has a `Legend:` field THEN append it inside the same blockquote.
R8a. The `> ` blockquote prefix in R8 is display framing, not content. R10 does not prohibit it.
R8b. IF mode = teach THEN after the Teach blockquote and before the Question, output a blank line, a `---` horizontal rule, and a blank line.
R8c. R8b overrides the global CLAUDE.md response-style ban on `---` horizontal rules, for the Teach/Question separator only.
R9.  IF mode = review THEN do NOT display Teach or Legend fields at any point.
R10. Do NOT rewrite, summarize, or add to the Teach field.
R11. Do NOT display `Concept`, `Source quote`, `Tests`, `Audit`, `Origin`, `Origin generated`, `Teach_EN`, or `Question_EN` at any point.
R11d. R11 is a denylist and R8/R12k are the allowlist. IF an entry carries a field they do not name THEN do NOT display it.
R11a. Do NOT display the `Answer key` or `Elaboration` field when delivering a question, in either mode. They are released only under R13a.
R11a2. IF an entry's `Origin` field records `ORPHANED` THEN still deliver the question normally. Report it once in the R28 wrap-up per R28d.

// Batch delivery
R12. BATCH = 1. Deliver BATCH questions per turn, then STOP and wait for the user.
R12i. IF the user's arguments contain `batch<N>` (e.g. `batch3`, `batch5`) THEN BATCH = N for this session; remove that token from the arguments before R1a counts them.
R12j. IF fewer than BATCH questions remain undelivered THEN the final batch is however many remain.
R12k. Displaying one question = its `Question` field rendered as a level-3 markdown heading with a `❓` anchor and a UNIT-QUALIFIED label: `### ❓ U<u>·Q<n> — <question text>`, where `<u>` is its unit number and `<n>` is the `Q<n>` label its heading carries. IF mode = teach THEN R8 and R8b precede it.
R12k1. IF the file holds exactly one unit THEN drop the `U<u>·` prefix and label the question `Q<n>`.
R12l. Display the batch's questions in ascending position order, one after another in a single turn, each per R12k. Do NOT reveal any answer.
R12m. After the last question of the batch, STOP. Do NOT display the next batch until the current batch's answers have been released under R13a.
R12n. IF a unit boundary falls inside a batch THEN display the R7 unit heading at that point and continue the batch across it.

R13. IF a batch is pending AND the user's message requests the answers — `next`, `n`, `answer`, `show`, `skip`, `pass`, `I don't know`, or any equivalent — THEN display the answers per R13a and advance per R19.
R13a. Displaying the answers = for EVERY question in the pending batch, in ascending position order, output the heading `**Answer — <label>**` using that question's R12k label, then its `Answer key` verbatim, then its `Elaboration` verbatim when it has one.
R13a2. Label every answer with the same label its question carried under R12k.
R13a4. IF BATCH = 1 THEN the `— <label>` suffix is optional; a bare `**Answer**` is sufficient.
R13b. Do NOT rewrite, summarize, shorten, or expand `Answer key` or `Elaboration`. Display them as written.
R13a1. One `next` releases the WHOLE batch. Do NOT release answers one at a time.
R14. IF a batch is pending AND the user's message is an attempted answer rather than a request THEN display the answers per R13a and advance per R19, exactly as if they had typed `next`.
R15. Do NOT grade, score, judge, correct, or comment on anything the user types on a pending batch. Do NOT say correct, wrong, close, or partially right.
R16. There is no correct count, no wrong count, and no score.
R17. IF a batch is pending AND the user's message is a clarifying or follow-up question about the material THEN R20 applies: answer it, re-display the pending batch, do NOT release any answer, and do NOT advance.
R18. IF the user's message on a pending batch is ambiguous between R14 and R17 THEN treat it as R17: answer it and re-display the batch. Do NOT advance.
     // Example: "wait, is dependability the same as reliability?" → R17. "something about it being an engineering discipline" → R14.
R19. IF a batch's answers have been released under R13a THEN advance: load the next window first if the current one is exhausted (R4d), then deliver the next BATCH questions per R12l. IF mode = teach THEN each question's Teach field precedes its Question field, per R8 and R8b.

// Pacing
R20. IF the user sends a clarifying or follow-up question THEN answer it fully, then re-display the current pending batch in full. Do not ask "Ready to continue?"
R21. Move through units in order. Every question is delivered; nothing gates advancing.

// Wrap up
R28. IF the final batch's answers have been released under R13a AND no unloaded questions remain in the file, THEN display a completion line per R28a and stop.
R28f. Check the R4c index, not the loaded window, to decide whether questions remain.
R28a. The completion line names the topic and the file's full size. Every question in the file was delivered, so the count IS the file.
     // Example: `**Complete — 33 questions delivered** (week1 — all 33 questions in this file.)`
R28b. Do NOT display a score, a correct/total ratio, a list of missed questions, or a summary of weak areas. Nothing was graded.
R28c. IF the topic was a chapter AND `extracted/class/` contains any `week<N>/questions_week<N>.md` files THEN, after the completion line, print one line naming the week files as the course-scoped subset.
R28d. IF the topic was a week AND any delivered entry's `Origin` field records `ORPHANED` THEN, after the completion line, print one line naming the count and the fix: re-run `/generate_questions week<N>` and choose `reselect`.

// Autosave
R29. AUTOSAVE = 10. IF AUTOSAVE questions have had their answer released under R13a since the progress file was last written THEN write it per R30b–R30c1 as part of that same turn, then reset the count.
R29a. An autosave is SILENT. Emit no confirmation.
R29b. R30b1 applies in full: an autosave is ONE Write call. It reads nothing and re-derives nothing.
R29c. IF the autosave Write fails THEN say so in one line, name the path, and continue.
R29d. IF the user types `save` THEN that is a MANUAL save under R30 and it confirms per R30e.
R29e. IF the arguments contain `autosave<N>` THEN AUTOSAVE = N; IF they contain `autosave off` or `noautosave` THEN autosave is disabled for the session. Remove the token before R1a counts arguments.
R29f. The autosave count is reset by ANY write of the progress file, manual or automatic.
R29g. R29 does not fire on a turn that delivered no question — a clarifying answer (R17) or a re-display resolves nothing.

// Save & resume
R30.  IF the argument is `save` THEN this is a save request, not a topic. R30 applies only when a `/learn` session is active (a questions file is loaded and at least one question has been displayed).
R30a. IF `save` is invoked with no active session THEN say "Nothing to save — no /learn session is running." Do NOT stop under R35.
R30b. IF `save` is invoked THEN write a progress file to the same directory as the loaded questions file, named `progress_<arg>.md`.
R30b1. A save is ONE tool call: the Write. Do NOT read the questions file, do NOT re-run the R4c index, and do NOT load a window.
R30b2. IF the state R30c requires is NOT already in context THEN no session is active and R30a applies.
R30c. The progress file contains exactly these fields:
       - `topic:` — the normalized topic argument (e.g. `chapter3`, `week1`)
       - `mode:` — `teach` or `review`
       - `questions_file:` — absolute path to the loaded questions file
       - `current_unit:` — unit number the session is on
       - `current_question:` — the ABSOLUTE POSITION (R4c1) of the NEXT question to deliver
       - `current_label:` — that question's R12k label, for human readability only
       - `batch:` — the BATCH size in force for this session
       - `delivered:` — count of questions whose answer was released
R30c1. Do NOT write a `correct:`, `wrong:`, or `wrong_list:` field. Nothing is graded.
R30d. IF the progress file already exists THEN overwrite it.
R30d1. Writing the progress file means CALLING THE WRITE TOOL. A save is not complete until that tool call has returned successfully.
R30d2. Do NOT emit the R30e confirmation unless the Write tool has actually run and returned success in this turn.
R30d3. IF the Write tool fails or is denied THEN say so plainly, name the path, and do NOT claim the progress was saved.
R30e. After the Write tool returns success, confirm in one line: "Progress saved — question N of M. `/learn resume` in a new chat to continue."
R30e1. IF `save` is invoked and the turn is about to end without a Write tool call having been made THEN stop and perform the write before responding.
R30f. R30 overrides R13–R14: `save` is not a request for the answers.
R30g. IF `save` is invoked on a pending batch THEN the whole batch stays pending: `current_question:` records the FIRST question of that batch. On resume the batch is re-delivered in full.
R30h. Do NOT write a window boundary to the progress file. Windows are a loading detail; a resumed session rebuilds its index and loads whichever window contains `current_question:`.

R31.  IF the argument is `resume` THEN this is a resume request, not a topic.
R31a. Scan all `progress_*.md` files under `extracted/class/` and `extracted/textbook/chapters/`.
R31b. IF exactly one progress file exists THEN load it and proceed to R31e.
R31c. IF multiple progress files exist THEN list them with their topic, the file's MODIFICATION TIME, and progress (question N of M). Ask the user to pick one. STOP until user responds.
R31d. IF no progress file exists THEN say "No saved sessions found." Do NOT stop under R35.
R31e. Load the questions file from the `questions_file:` path per R4c. IF the file does not exist THEN say "Questions file missing — cannot resume." Do NOT stop under R35.
R31f. Restore mode from the progress file's `mode:` field.
R31f1. Restore BATCH from the progress file's `batch:` field. IF the file carries no `batch:` field THEN BATCH = 1.
R31g. Restore the delivered count from the progress file.
R31h. Skip to the unit and question recorded in `current_unit:` and `current_question:`. Deliver a full batch starting at that question.
R31i. After the resumed session ends normally (R28), delete the progress file.
R31j. IF the user saves again during a resumed session (R30) THEN overwrite the same progress file with the updated state.

// Catch-all
R35. IF any condition not covered by R1–R31 (including all lettered sub-rules) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Usage

```
/generate_questions chapter2      ← build the pool first — this is where questions are made
/generate_questions week1         ← then select week 1's subset out of it
/learn week1                      ← first pass over week 1's study list: teach then ask
/learn week1 no_context           ← review pass over the same: blind questions

/learn chapter2                   ← first pass over the whole chapter — the reference bank
/learn chapter2 no_context        ← review pass over the whole chapter
/learn chapter2 batch3            ← three questions per turn instead of one
/learn chapter2 autosave3         ← autosave every 3 questions instead of 10
/learn chapter2 autosave off      ← turn autosave off

/learn save                       ← save right now and confirm it
/learn resume                     ← pick up where you left off in a new chat
```

Your place is **autosaved every 10 questions**, silently. You can close the chat whenever without
typing anything; `/learn resume` picks it up. Typing `save` still works and confirms out loud.

Questions arrive **one at a time** by default: read it, answer out loud, type `next` to see the
stored answer and move on. Pass `batch<N>` to get several per turn instead — fewer round trips,
lower cost, but you hold several questions in your head at once.

Every run delivers the entire file, ten questions at a time behind the scenes — you never see the
window boundaries. To study less, pick a narrower topic — that is what `week<N>` is: the questions
from the book that this week's lectures actually reached.

In-session keywords, typed in reply to a pending question:

```
next      ← show the stored answer, then deliver the next question (R13)
save      ← write progress to disk so you can resume in a new chat (R30)
```

Anything else you type is treated as an attempt and releases the answer the same as `next` — except
a question about the material, which is answered and the question re-asked (R17).

In a multi-unit file, questions are labeled `U2·Q5` — unit 2, question 5. The `Q<n>` numbers restart
in every unit, so the unit prefix is what makes a label unique. Single-unit files just show `Q5`.
