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

Which file to run is the only scoping decision, and it is made by the topic argument. There is no priority tier, no core subset, and no `+` suffix — `/generate_questions` writes no `Priority` field for anything to filter on.

**The loop:** teach material, ask the question, wait. You answer however you like — out loud, on paper, in your head. Type `next` and the stored answer appears. Compare it yourself, then the next question follows. Nothing you type is judged, and no score is kept.

Two modes: **teach** (default) shows each question's Teach field before asking — first contact with material. **review** (`no_context` flag) hides all Teach fields and asks blind — retrieval practice for material already learned. The modes differ only in Teach field visibility; the loop is identical in both.

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
     // Example: `/learn week1 no_context` = review mode over week 1's study list.
// File lookup
R3.  IF <arg> normalizes to a week — `week<N>` or `wk<N>` — THEN look for `extracted/class/week<N>/questions_week<N>.md`.
R3a. IF <arg> normalizes to a chapter — `chapter<N>` or `capitulo<N>` — THEN look for `extracted/textbook/chapters/chapter<N>/questions_chapter<N>.md` (or `capitulo<N>/questions_capitulo<N>.md` for Spanish-language classes).
R3b. IF <arg> does not match either pattern THEN look for `extracted/questions_<arg>.md` as a fallback.
     // Commentary: the fallback keeps any questions file not yet migrated to the new layout reachable.
R4.  IF the file exists THEN load it per R4b–R4d and proceed to R7.
R4a. IF `--count` reports zero questions THEN stop and tell the user: "Questions file is empty — re-run /generate_questions <arg>."

// Windowed loading — never read the whole questions file
R4b. WINDOW = 10. This is the number of questions loaded into context at a time.
R4c. Loading the file = four small reads, never a whole-file read:
       1. The frontmatter — read the first 10 lines.
       2. The question index — `grep -n '^#### Q' <file> | cut -d: -f1 | nl -ba`. This yields one row per question: POSITION, then the line it starts on. It carries no `Q<n>` labels.
       3. The unit index — `grep -n '^## Unit ' <file>`, for unit headings and titles.
       4. The first window — from the line shown at position 1 through the line before the line shown at position WINDOW+1, or end of file when the index has no such position.
     // Commentary: a chapter file runs 1,100-1,900 lines. Reading it whole puts all of it in context for a sitting that may deliver three questions, and every later turn re-reads it from cache. The index costs one grep and is a few hundred bytes.
R4c1. Address questions by their ABSOLUTE POSITION — the left column of the R4c step-2 index — never by the `Q<n>` label a heading carries.
      // Commentary: `Q<n>` restarts at Q1 in every unit; 6 of the 8 questions files on this system contain several `Q1`s. The step-2 command strips the labels deliberately. An earlier index kept them, and on 2026-08-24 two of three runs computed the window edge by finding the literal string `Q10`/`Q11` in the index instead of counting to position 11 — reading 18 and 19 questions instead of 10. The rule saying "count by position" did not survive contact with an index that displayed tempting-looking labels; removing them from the data is what fixes it.
R4c2. IF the window edge is being determined THEN read it from the step-2 index by POSITION lookup. Do NOT compute it from question labels, from line counts, or by estimating lines-per-question.
R4d. IF the currently loaded window is exhausted AND unloaded questions remain THEN load the next WINDOW questions by the same line-range read. Do NOT re-read the frontmatter or the index.
R4e. IF a question outside the loaded window is needed for any reason THEN load its window first. Never answer from a question that is not in context.
R4f. The index from R4c step 2 is internal metadata. Do NOT display it, and do NOT display line numbers or window boundaries to the user.
R4g. Window boundaries are invisible to the user. Do NOT announce loading, do NOT say "loading the next 10", and do NOT pause at a window edge. A window refill happens mid-advance under R19 and produces no output.
R4h. IF the index shows WINDOW or fewer questions in total THEN the first window is the whole file and R4d never fires.
R5.  IF the file does not exist THEN stop and tell the user: "Run /generate_questions <arg> first."
R6.  IF no <arg> is given THEN list all `questions_*.md` files under `extracted/textbook/chapters/` and `extracted/class/` and ask the user to pick one. STOP until user responds.

// Unit and question delivery
// Course scope notice
R6a. After loading the file per R3–R4 and before the first question: IF the topic is a chapter AND the class `CLAUDE.md` holds a `### Course Scope` entry listing that chapter as not covered THEN print one line saying the course does not cover it. Then proceed normally.
     // Example: `Note: CS4470 does not cover chapter 7 — this is textbook material beyond the course.`
R6a1. IF the topic is a week — `week<N>` or `wk<N>` — THEN print no scope notice, whatever the `### Course Scope` entry says. A week file holds only questions the professor's own material selected, so it is in scope by construction.
     // Commentary: this holds even when a week file draws on a chapter the syllabus lists as not covered. /generate_questions R0j4 deliberately lets that happen — if the professor taught it, what the syllabus planned is beside the point.
R6b. R6a is a notice, not a gate. Do NOT refuse, do NOT ask for confirmation, and do NOT change the filter.
     // Commentary: studying a chapter the course skipped is a deliberate act — after the final, or out of interest. The notice sets the expectation that none of it will be on the exam; blocking it would remove the reason the questions were generated at all.
R6c. IF the loaded chapter is in scope, or the class has no `### Course Scope` entry, THEN print no notice.
R6d. IF a `### Course Scope` entry exists but carries no derivable chapter list — its `covers` field reads `NOT DETERMINED`, is empty, or names no chapter — THEN treat the class as having no scope entry and print no notice. Do NOT stop under R35.
     // Commentary: mirrors /generate_questions R0j3. /updateclass R26d writes such an entry when a syllabus defers its schedule elsewhere. The chapter is then neither in scope nor out of it, which matched no branch of R6a–R6c and sent a plain `/learn chapter3` to the catch-all.

R7.  IF starting a new unit THEN display "Unit X of Y — <title>" as a level-2 markdown heading: `## Unit X of Y — <title>`.
R8.  IF mode = teach AND about to display a question THEN first display that question's `Teach:` field verbatim as a markdown blockquote — prefix every line of the Teach content, including blank lines between sub-concepts, with `> `. IF the entry has a `Legend:` field THEN append it inside the same blockquote.
     // Commentary: the blockquote renders as a distinct callout; the `> ` on blank lines keeps a multi-paragraph Teach field inside one quote block. `Legend` belongs to the visible teaching content — it names the variables in a formula — unlike the fields R11 hides.
R8a. The `> ` blockquote prefix in R8 is display framing, not content. R10 does not prohibit it.
R8b. IF mode = teach THEN after the Teach blockquote and before the Question, output a blank line, a `---` horizontal rule, and a blank line.
     // Commentary: the blank lines keep `---` from being parsed as a setext underline of the blockquote; the rule chunks "reference" from "what to answer".
R8c. R8b overrides the global CLAUDE.md response-style ban on `---` horizontal rules, for the Teach/Question separator only.
     // Commentary: that ban is scoped to terminal output, where `---` renders as three literal dashes. /learn's output is markdown-rendered, so the rule is the correct separator here.
R9.  IF mode = review THEN do NOT display Teach or Legend fields at any point.
     // Commentary: review mode is retrieval practice — showing the material before the question makes it an open-book read of text on screen.
R10. Do NOT rewrite, summarize, or add to the Teach field.
R11. Do NOT display `Concept`, `Source quote`, `Tests`, `Audit`, `Origin`, `Origin generated`, `Teach_EN`, `Question_EN`, or a legacy `Priority` field at any point.
     // Commentary: `Concept` names the answer and `Source quote` frequently restates it outright — on network chapter1 Q1 it sits three lines above the question. Showing either gives the question away.
R11d. R11 is a denylist and R8/R12k are the allowlist. IF an entry carries a field they do not name THEN do NOT display it, whether or not R11 lists it.
     // Commentary: a denylist that must be amended every time /generate_questions gains a field will eventually leak one; R11d makes silence the default.
R11a. Do NOT display the `Answer key` or `Elaboration` field when delivering a question, in either mode. They are released only under R13a.
R11a2. IF an entry's `Origin` field records `ORPHANED` THEN still deliver the question normally and say nothing about it during delivery. Report it once in the R28 wrap-up per R28d.
// Batch delivery
R12. BATCH = 1. Deliver BATCH questions per turn, then STOP and wait for the user.
     // Commentary: one at a time is the default because it is the study rhythm the user prefers. The batching machinery below stays because R12i can raise BATCH, and every rule downstream is written to handle any BATCH size including 1.
R12i. IF the user's arguments contain `batch<N>` (e.g. `batch3`, `batch5`) THEN BATCH = N for this session; remove that token from the arguments before R1a counts them.
R12j. IF fewer than BATCH questions remain undelivered THEN the final batch is however many remain. Do NOT pad it and do NOT mention that it is short.
R12k. Displaying one question = its `Question` field rendered as a level-3 markdown heading with a `❓` anchor and a UNIT-QUALIFIED label: `### ❓ U<u>·Q<n> — <question text>`, where `<u>` is its unit number and `<n>` is the `Q<n>` label its heading carries. IF mode = teach THEN R8 and R8b precede it.
R12k1. IF the file holds exactly one unit THEN drop the `U<u>·` prefix and label the question `Q<n>`.
     // Commentary: a `Unit 1 of 1` file has unambiguous labels already, and `U1·Q7` would be noise on every question.
R12l. Display the batch's questions in ascending position order, one after another in a single turn, each per R12k. Do NOT reveal any answer.
R12m. After the last question of the batch, STOP. Do NOT display the next batch until the current batch's answers have been released under R13a, or every question in it has been flagged.
R12n. IF a unit boundary falls inside a batch THEN display the R7 unit heading at that point and continue the batch across it. A batch is a delivery unit, not a content unit.
     // Commentary: batching exists to cut round trips, not to re-segment the material. Splitting a batch at a unit boundary would reintroduce the round trip it was meant to remove.

R13. IF a batch is pending AND the user's message requests the answers — `next`, `n`, `answer`, `show`, `skip`, `pass`, `I don't know`, or any equivalent — THEN display the answers per R13a and advance per R19.
R13a. Displaying the answers = for EVERY question in the pending batch, in ascending position order, output the heading `**Answer — <label>**` using that question's R12k label, then its `Answer key` verbatim, then its `Elaboration` verbatim when it has one.
R13a2. Label every answer with the same label its question carried under R12k. An unlabeled run of answers is not usable for comparison.
R13a4. IF BATCH = 1 THEN the `— <label>` suffix is optional; a bare `**Answer**` is sufficient.
R13b. Do NOT rewrite, summarize, shorten, or expand `Answer key` or `Elaboration`. Display them as written.
     // Commentary: the file is the reference the user compares their spoken answer against. A paraphrase makes the comparison a comparison against paraphrase.
R13a1. One `next` releases the WHOLE batch. Do NOT release answers one at a time and do NOT ask which one the user wants.
R14. IF a batch is pending AND the user's message is an attempted answer rather than a request THEN display the answers per R13a and advance per R19, exactly as if they had typed `next`.
R15. Do NOT grade, score, judge, correct, or comment on anything the user types on a pending batch. Do NOT say correct, wrong, close, or partially right. Do NOT compare their words to any `Answer key`.
     // Commentary: the user answers out loud, away from the keyboard. Any verdict here is unfounded — the real answer was never seen — and removing the verdict is the point of this loop.
R16. There is no correct count, no wrong count, and no score. No question is ever marked right or wrong.
R17. IF a batch is pending AND the user's message is a clarifying or follow-up question about the material THEN R20 applies: answer it, re-display the pending batch, do NOT release any answer, and do NOT advance.
R18. IF the user's message on a pending batch is ambiguous between R14 and R17 THEN treat it as R17: answer it and re-display the batch. Do NOT advance.
     // Commentary: advancing is destructive — the answers are spent and the moment to think about the questions is gone. Re-asking costs one line.
     // Example: PASSES as R17: "wait, is dependability the same as reliability?" → a question about the material → answer it, re-ask.
     //          PASSES as R14: "something about it being an engineering discipline" → an attempt → release the batch, advance.
R18a. R30 (`save`) overrides R13–R14. It is not a request for the answers.
R19. IF a batch's answers have been released under R13a THEN advance: load the next window first if the current one is exhausted (R4d), then deliver the next BATCH questions per R12l. IF mode = teach THEN each question's Teach field precedes its Question field, per R8 and R8b.
     // Commentary: R19 is the single definition of advancing. R13 and R14 delegate to it rather than restating it, so the teach-mode display requirement and the window refill each have one place to change.

// Pacing
R20. IF the user sends a clarifying or follow-up question THEN answer it fully, then re-display the current pending batch in full — every question still pending, each per R12k. Do not ask "Ready to continue?"
R21. Move through units in order. Every question is delivered; nothing gates advancing to the next question or unit.

// Wrap up (both modes)
R28. IF the final batch's answers have been released under R13a AND no unloaded questions remain in the file, THEN display a completion line per R28a, list any flagged questions, and stop.
R28f. Check the R4c index, not the loaded window, to decide whether questions remain. A window boundary is not the end of the file, and the index total is the finish line, not the odometer.
     // Commentary: two ways this has gone wrong. An exhausted window read as "no more questions" would end a 106-question session at question 10; and on 2026-08-24 a session printed "Complete — 106 questions delivered" as its FIRST output, having only read the total.
R28a. The completion line names the topic and the file's full size, with no filter annotation. Every question in the file was delivered, so the count IS the file.
     // Example: `**Complete — 33 questions delivered** (week1 — all 33 questions in this file.)`
R28b. Do NOT display a score, a correct/total ratio, a list of missed questions, or a summary of weak areas. Nothing was graded, so there is nothing to total.
     // Commentary: this is the rule most likely to be violated by habit. A wrap-up that invents "you seemed shaky on X" is fabricating a judgment from questions whose answers were never seen.
R28c. IF the topic was a chapter AND `extracted/class/` contains any `week<N>/questions_week<N>.md` files THEN, after the completion line, print one line saying this was the full chapter and naming the week files as the subset the course actually covered.
     // Example: `This was the full chapter. The subset the professor covered is in class/week1/questions_week1.md and class/week2/questions_week2.md.`
     // Commentary: a week file is now a strict subset of the chapter files it draws from, so a chapter run necessarily includes material no lecture reached. This is the one moment the user is thinking about coverage.
R28d. IF the topic was a week AND any delivered entry's `Origin` field records `ORPHANED` THEN, after the completion line, print one line naming the count and the fix: re-run `/generate_questions week<N>` and choose `reselect`.
     // Example: `Note: 2 questions in this file are orphaned — their chapter was regenerated and no longer matches. Run /generate_questions week3 and choose reselect to rebuild.`
     // Commentary: an orphaned entry is still a good question, so this is a maintenance note rather than a warning. The end of a session is the right place for it: the user has finished studying and is deciding what to do next.
R28e. IF the topic was a week AND no entry is orphaned THEN print nothing under R28d. Do NOT print a clean bill of health.

// Autosave
R29. AUTOSAVE = 10. IF AUTOSAVE questions have had their answer released under R13a since the progress file was last written THEN write it per R30b–R30c1 as part of that same turn, then reset the count.
R29a. An autosave is SILENT. Emit no confirmation, no "progress saved", and no mention of the file. The user sees only the next question.
     // Commentary: a confirmation every third question would interrupt the study rhythm the batch size was chosen to protect. The manual `save` still confirms, because there the user asked and expects an acknowledgement.
R29b. R30b1 applies in full: an autosave is ONE Write call. It reads nothing and re-derives nothing.
R29c. IF the autosave Write fails THEN say so in one line, name the path, and continue the session. Do NOT stop, and do NOT silently swallow the failure.
     // Commentary: silence is correct for success and wrong for failure — the whole point is that the user can close the chat trusting their place is kept.
R29d. IF the user types `save` THEN that is a MANUAL save under R30 and it confirms per R30e. R29a's silence applies only to autosaves.
R29e. IF the arguments contain `autosave<N>` THEN AUTOSAVE = N; IF they contain `autosave off` or `noautosave` THEN autosave is disabled for the session. Remove the token before R1a counts arguments.
R29f. The autosave count is reset by ANY write of the progress file, manual or automatic.
R29g. R29 does not fire on a turn that delivered no question — a clarifying answer (R17) or a re-display resolves nothing.

// Save & resume
R30.  IF the argument is `save` THEN this is a save request, not a topic. R30 applies only when a `/learn` session is active (a questions file is loaded and at least one question has been displayed).
R30a. IF `save` is invoked with no active session THEN say "Nothing to save — no /learn session is running." Do NOT stop under R35.
R30b. IF `save` is invoked THEN write a progress file to the same directory as the loaded questions file, named `progress_<arg>.md` (e.g. `progress_chapter3.md`, `progress_week1.md`).
R30b1. A save is ONE tool call: the Write. Do NOT read the questions file, do NOT re-run the R4c index, and do NOT load a window. Every field R30c needs is already in this session's context.
      // Commentary: on 2026-08-24 a save issued Read + grep + Read before the Write — four requests of rediscovery to produce a 267-byte file, costing 5.9c, about three questions' worth. R4b–R4d describe loading a session, not saving one.
R30b2. IF the state R30c requires is NOT already in context THEN no session is active and R30a applies. Re-deriving it from disk is never the right response to `save`.
R30c. The progress file contains exactly these fields:
       - `topic:` — the normalized topic argument (e.g. `chapter3`, `week1`)
       - `mode:` — `teach` or `review`
       - `questions_file:` — absolute path to the loaded questions file
       - `current_unit:` — unit number the session is on
       - `current_question:` — the ABSOLUTE POSITION (R4c1) of the NEXT question to deliver — the Nth question in the file, counting from 1 across all units
       - `current_label:` — that question's R12k label (e.g. `U2·Q5`), for human readability only; `current_question:` is what resume seeks on
       - `batch:` — the BATCH size in force for this session (R12/R12i)
       - `delivered:` — count of questions whose answer was released
R30c2. Do NOT write a `saved_at:` field, or any other timestamp. The file's own modification time already records when it was written, and it is the only source that cannot be wrong.
      // Commentary: every field above is copied from session state the model already holds; a timestamp is the one value it would have to obtain, and on 2026-08-24 two saves invented `00:00:00Z` and `16:30:00Z` while the real write times were 21:16 and 04:37 UTC. Reading the clock would cost an extra tool call, and R30b1 caps a save at one.
R30c3. IF an existing progress file carries a legacy `saved_at:` field THEN ignore it. Read the file's modification time instead.
R30c1. Do NOT write a `correct:`, `wrong:`, or `wrong_list:` field. Nothing is graded, so those counts do not exist.
      // Commentary: an older format carried them. A resumed session that restores a correct count will start reporting a score the rest of this skill no longer produces.
R30d. IF the progress file already exists THEN overwrite it.
      // Commentary: only one save point per topic. The user wants to resume from one place, not manage save slots.
R30d1. Writing the progress file means CALLING THE WRITE TOOL. A save is not complete until that tool call has returned successfully.
R30d2. Do NOT emit the R30e confirmation, or any other success message, unless the Write tool has actually run and returned success in this turn. IF no Write tool call was made THEN no save happened, whatever the state of the session.
      // Commentary: on 2026-08-24 a `/learn save` printed "Progress saved — question 5 of 106" with zero tool calls; nothing reached disk, and the next `/learn resume` correctly found nothing. Announcing a save that did not occur is worse than failing to save, because the user closes the chat believing their position is recorded.
R30d3. IF the Write tool fails or is denied THEN say so plainly, name the path that was attempted, and do NOT claim the progress was saved.
R30e. After the Write tool returns success, confirm in one line: "Progress saved — question N of M. `/learn resume` in a new chat to continue."
R30e1. IF `save` is invoked and the turn is about to end without a Write tool call having been made THEN stop and perform the write before responding. Emitting the confirmation is not a substitute for the action it describes.
R30f. R30 overrides R13–R14: `save` is not a request for the answers. Do NOT release any answer and do NOT advance.
R30g. IF `save` is invoked on a pending batch THEN the whole batch stays pending: `current_question:` records the FIRST question of that batch, not the one after it. On resume the batch is re-delivered in full.
      // Commentary: the user has seen the questions but not the answers. Resuming past them would spend the batch without ever showing what it was checking against.
R30h. Do NOT write a window boundary to the progress file. Windows are a loading detail (R4b–R4h); a resumed session rebuilds its index and loads whichever window contains `current_question:`.

R31.  IF the argument is `resume` THEN this is a resume request, not a topic.
R31a. Scan all `progress_*.md` files under `extracted/class/` and `extracted/textbook/chapters/` in the current class directory.
R31b. IF exactly one progress file exists THEN load it and proceed to R31e.
R31c. IF multiple progress files exist THEN list them with their topic, the file's MODIFICATION TIME (from the R31a scan — e.g. `find ... -printf`/`ls -l`, never a value read from inside the file), and progress so far (question N of M). Ask the user to pick one. STOP until user responds.
R31d. IF no progress file exists THEN say "No saved sessions found." Do NOT stop under R35.
R31e. Load the questions file from the `questions_file:` path per R4c — frontmatter, index, then the window containing `current_question:`. IF the file does not exist THEN say "Questions file missing — cannot resume." Do NOT stop under R35.
R31f. Restore mode from the progress file's `mode:` field.
R31f1. Restore BATCH from the progress file's `batch:` field. IF the file carries no `batch:` field THEN BATCH = 3 (the R12 default).
      // Commentary: progress files written before batching carry no such field; defaulting keeps them resumable.
R31g. Restore the delivered count from the progress file.
R31g1. IF the progress file carries a legacy `correct:`, `wrong:`, `wrong_list:`, `flagged:`, or `flagged_list:` field THEN ignore it. Do NOT restore it and do NOT report it.
      // Commentary: progress files written before grading was removed still carry these. Reading them would resurrect a score in a session that grades nothing.
R31h. Skip to the unit and question recorded in `current_unit:` and `current_question:`. Deliver a full batch starting at that question, per the normal flow (R7–R12), as if the session had just reached it.
      // Commentary: questions before this point were already delivered in the prior session.
R31i. After the resumed session ends normally (R28), delete the progress file.
      // Commentary: a completed session has no resume point. Leaving the file would let `/learn resume` reload a finished run.
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
