---
name: learn
description: 'Deliver course material concept by concept — teach, ask, then serve the stored answers on request. `/learn week1` drills the textbook questions covering what the professor taught that week — the study list; `/learn chapter1` drills the whole textbook chapter — the reference bank. By default both deliver every question in their file; pass start<N> to begin at absolute question position N. Every question comes from the textbook. Questions arrive one at a time; nothing is graded and no score is kept: type "next" to see the stored answer and move on. Pass batch<N> for several questions per turn. Requires a pre-generated questions file from /generate-questions. Week files live in extracted/class/week<N>/, chapter files in extracted/textbook/chapters/chapter<N>/.'
---

Deliver course material question by question using a pre-generated questions file. `/learn` is a delivery engine — it does not generate content or questions, and it does not grade. Content comes from `/generate-questions`; the verdict comes from you.

Two topics, two files, both delivered from the selected starting position through the end:

- `/learn week1` — the textbook questions covering what the professor taught in week 1. This is the study list for a course you are currently taking.
- `/learn chapter1` — the whole textbook chapter. This is the reference bank: everything the book explains, whether the course reached it or not.

Every question in both files was generated from the textbook. The difference is scope, not source:
`/generate-questions chapter<N>` writes the pool, and `/generate-questions week<N>` copies the subset
of that pool matching what the professor covered. A week file is therefore a strict subset of the
chapter files it draws from, and each of its entries records where it came from.

The topic argument selects the file. The optional `start<N>` argument selects the first absolute question position to deliver; without it, delivery begins at position 1.

**The loop:** teach material, ask the question, wait. You answer however you like — out loud, on paper, in your head. Type `next` and the stored answer appears. Compare it yourself, then the next question follows. Nothing you type is judged, and no score is kept.


## Rules

// Argument parsing and loading
R1. IF a `/learn` invocation begins THEN preserve its unmodified argument tokens as ORIGINAL_ARGUMENTS.
R1a. IF more than one argument remains after removing the option tokens under R1b and R12i THEN stop and ask the user which one is the topic. STOP until user responds.
R1b. IF ORIGINAL_ARGUMENTS contains exactly one token matching `start<N>` where N is an integer greater than zero THEN START = N; remove that token from the working arguments.
R1b1. IF ORIGINAL_ARGUMENTS contains no token beginning with `start` THEN START = 1.
R1b2. IF ORIGINAL_ARGUMENTS contains more than one token beginning with `start` THEN stop and tell the user: "Use exactly one start<N> argument."
R1b3. IF an ORIGINAL_ARGUMENTS token begins with `start` but does not match `start<N>` where N is an integer greater than zero THEN stop and tell the user: "Invalid start position — use start<N> with N greater than zero."
R1b5. IF R1b2 and R1b3 both apply THEN R1b2 overrides R1b3.
// Delivery scope
R1c. IF START = 1 THEN deliver EVERY entry in the loaded file.
R1c1. IF START > 1 THEN deliver EVERY entry at absolute position START or later and deliver no entry before START.
R1c2. IF START is resolved THEN interpret it as the ABSOLUTE POSITION from the R4c step-2 index, never as the `Q<n>` label carried by a question heading.
R1d. IF the user asks /learn to save or resume a session position THEN say: "Learn sessions are not saved; start a new run with /learn <topic> start<N>."
R1d1. IF R1d applies THEN stop without treating save or resume as a topic.
R1e. IF a learn session advances or ends THEN write no session state to disk.

// Class root — resolve BEFORE any path in R3 is opened
R2.  The paths in R3–R3b are relative to the CLASS ROOT, never to the current directory blindly. Resolve the class root first.
R2a. IF the current working directory contains an `extracted/` directory THEN it is the class root.
R2b. IF R2a does not apply THEN search one level under `~/edu/` for a directory whose `extracted/` tree holds the topic file named by R3–R3b.
R2c. IF R2b finds EXACTLY ONE class holding that file THEN it is the class root. Do NOT prompt.
R2d. IF R2b finds SEVERAL classes holding that file THEN stop, list them by directory name, and ask the user which course. STOP until user responds. Do NOT guess from conversation context and do NOT pick the most recently modified.
R2e. IF R2b finds NO class holding that file THEN R5 applies.
R2f. IF the class root was resolved under R2c or R2d THEN name that course in the R7b opener, so the user can see which one loaded.

// File lookup
R3.  IF <arg> normalizes to a week — `week<N>` or `wk<N>` — THEN look for `extracted/class/week<N>/questions_week<N>.md`.
R3a. IF <arg> normalizes to a chapter — `chapter<N>` or `capitulo<N>` — THEN look for `extracted/textbook/chapters/chapter<N>/questions_chapter<N>.md` (or `capitulo<N>/questions_capitulo<N>.md` for Spanish-language classes).
R3b. IF <arg> does not match either pattern THEN look for `extracted/questions_<arg>.md` as a fallback.
R4. IF the file exists THEN set QUESTION_COUNT to the output of `grep -c '^#### Q' <file>`.
R4a. IF QUESTION_COUNT = 0 THEN stop and tell the user: "Questions file is empty — re-run /generate-questions <arg>."
R4a1. IF QUESTION_COUNT is greater than zero THEN load the file per R4b–R4d, print the R7b opener, print any R6a scope notice, and begin delivery per R12.

// Windowed loading — never read the whole questions file
R4b. WINDOW = 10. This is the number of questions loaded into context at a time.
R4c. Loading the file = three small reads, never a whole-file read:
       1. The frontmatter — read the first 10 lines.
       2. The question index — `grep -n '^#### Q' <file> | cut -d: -f1 | nl -ba`. This yields one row per question: POSITION, then the line it starts on. It carries no `Q<n>` labels.
       3. The initial window — from the line shown at position START through the line before the line shown at position START+WINDOW, or end of file when the index has no such position.
R4c1. Address AND display questions by their ABSOLUTE POSITION — the left column of the R4c step-2 index.
R4c1a. IF the frontmatter carries `format: 2` THEN the `Q<n>` label in a heading EQUALS that question's absolute position, and R12k1 does not apply.
R4c1b. IF the frontmatter carries no `format:` line, or a value other than 2, THEN the file is format 1: its labels restart at Q1 in every unit and MUST be ignored per R12k1.
      // Commentary: format 2 numbers headings absolutely across the whole file, so the label and the position are the same number. Format 1 files restart per unit and multiple `Q1`s exist in them; the step-2 index is the authority for those.
R4c2. IF the window edge is being determined THEN read it from the step-2 index by POSITION lookup. Do NOT compute it from question labels, from line counts, or by estimating lines-per-question.
R4c3. IF a topic launch has START greater than the total number of positions in the step-2 index THEN stop and tell the user: "Start position out of range — this file has M questions."
R4d. IF the currently loaded window is exhausted AND unloaded questions remain THEN load the next WINDOW questions by the same line-range read. Do NOT re-read the frontmatter or the index.
R4e. IF a question outside the loaded window is needed for any reason THEN load its window first.
R4f. The index from R4c step 2 is internal metadata. Do NOT display it, and do NOT display line numbers or window boundaries to the user.
R4g. Window boundaries are invisible to the user. Do NOT announce loading, do NOT say "loading the next 10", and do NOT pause at a window edge.
R4h. IF WINDOW or fewer questions remain at or after the initial position THEN the initial window contains every remaining question and R4d never fires.
R5.  IF the file does not exist THEN stop and tell the user: "Run /generate-questions <arg> first."
R6.  IF no <arg> is given THEN list all `questions_*.md` files under `extracted/textbook/chapters/` and `extracted/class/` and ask the user to pick one. STOP until user responds.
R6c. IF R6 applies AND no class root was resolved under R2a THEN list the files per class across `~/edu/`, labelling each by its course directory, so two courses' `week2` are distinguishable.

// Course scope notice
R6a. After loading the file per R3–R4 and before the first question: IF the topic is a chapter AND the class `CLAUDE.md` holds a `### Course Scope` entry listing that chapter as not covered THEN print one line saying the course does not cover it. Then proceed normally.
R6a1. IF the topic is a week THEN print no scope notice. A week file holds only questions the professor's own material selected, so it is in scope by construction.
R6b. R6a is a notice, not a gate. Do NOT refuse, do NOT ask for confirmation.
R6d. IF a `### Course Scope` entry exists but carries no derivable chapter list — `covers` reads `NOT DETERMINED`, is empty, or names no chapter — THEN treat the class as having no scope entry and print no notice. Do NOT stop under R29.

// Question delivery
R7.  Delivery is FLAT. Do NOT display unit headings, unit numbers, unit titles, or unit boundaries at any point. The `## Unit X of Y` headings in the questions file are provenance metadata, not display structure.
R7a. IF the file holds several units THEN deliver its questions as one continuous sequence across them. A unit boundary is invisible to the user and is never announced.
R7b. Before the first question of a session, display ONE line naming the resolved course, the topic, and the delivery range — e.g. `software_engineering — week2, 120 questions.` IF START > 1 THEN the range reads `positions <START>–<M> of <M>`. This is the whole session opener; do NOT add a title, a rule, a summary, or a unit heading.
R7c. R7b fires exactly once per session, before the first question only. Do NOT repeat it at a window edge, at a unit boundary, or when re-displaying a pending batch under R13c/R14/R17/R20.
R8.  IF about to display a question THEN first display that question's `Teach:` field verbatim as a markdown blockquote and prefix every line with `> `.
R8d. IF R8 displays Teach AND the entry has a `Legend:` field THEN append Legend inside the same blockquote.
R8a. The `> ` blockquote prefix in R8 is display framing, not content. R10 does not prohibit it.
R8b. IF R8 displays Teach THEN after the Teach blockquote and before the Question, output a blank line, a `---` horizontal rule, and a blank line.
R8c. R8b overrides the global AGENT.md response-style ban on `---` horizontal rules, for the Teach/Question separator only.
R10. Do NOT rewrite, summarize, or add to the Teach field.
R11. Do NOT display `Concept`, `Source quote`, `Tests`, `Audit`, `Origin`, `Origin generated`, `Origin fingerprint`, `Teach_EN`, or `Question_EN` at any point.
R11b. R11d is the governing rule and it is a WHITELIST: an entry field not named there is never displayed, whether or not R11 enumerates it.
R11d. IF delivering a question THEN display only `Teach`, optional `Legend`, and `Question` per R8 and R12k.
R11d1. IF releasing an answer THEN display only `Answer key` and optional `Elaboration` per R13a.
R11a. Do NOT display the `Answer key` or `Elaboration` field when delivering a question. They are released only under R13a.
R11a2. IF an entry's `Origin` field records `ORPHANED` THEN still deliver the question normally. Report it once in the R28 wrap-up per R28d.

// Batch delivery
R12. BATCH = 1. Deliver BATCH questions per turn, then STOP and wait for the user.
R12i. IF ORIGINAL_ARGUMENTS contains exactly one token matching `batch<N>` where N is an integer greater than zero THEN BATCH = N and remove that token from the working arguments. R12i overrides R12.
R12i1. IF ORIGINAL_ARGUMENTS contains no token beginning with `batch` THEN BATCH = 1.
R12i2. IF ORIGINAL_ARGUMENTS contains more than one token beginning with `batch` THEN stop and tell the user: "Use exactly one batch<N> argument."
R12i3. IF an ORIGINAL_ARGUMENTS token begins with `batch` but does not match `batch<N>` where N is an integer greater than zero THEN stop and tell the user: "Invalid batch size — use batch<N> with N greater than zero."
R12i4. IF R12i2 and R12i3 both apply THEN R12i2 overrides R12i3.
R12j. IF fewer than BATCH questions remain undelivered THEN the final batch is however many remain.
R12k. Displaying one question = its `Question` field rendered as a level-3 markdown heading with a `❓` anchor and its ABSOLUTE POSITION as the label: `### ❓ Q<p> — <question text>`, where `<p>` is the question's absolute position from the R4c step-2 index. R8 and R8b precede it.
R12k1. IF the file is format 1 per R4c1b THEN IGNORE the heading's `Q<n>` label for display; it restarts at Q1 in every unit and is not unique. Do NOT display it and do NOT combine it with a unit prefix.
R12k2. IF the file is format 2 per R4c1a THEN the heading label and the absolute position are the same number, and displaying either is correct.
R12l. Display the batch's questions in ascending position order, one after another in a single turn, each per R12k. Do NOT reveal any answer.
R12m. After the last question of the batch, STOP. Do NOT display the next batch until the current batch's answers have been released under R13a.
R12n. IF a unit boundary falls inside a batch THEN continue the batch across it with no heading, no separator, and no announcement.
R12o. IF a batch is pending AND the user's message, after trimming whitespace and ignoring case, is exactly `exit` THEN clear the active in-chat batch, say "Learn session ended.", and stop. Do NOT release an answer, advance, or write session state. R12o overrides R13c, R14, R17, and R18.

R13. IF a batch is pending AND the user's message, after trimming whitespace and ignoring case, is exactly `next` THEN display the answers per R13a and advance per R19.
R13a. Displaying the answers = for EVERY question in the pending batch, in ascending position order, output the heading `**Answer — <label>**` using that question's R12k label, then its `Answer key` verbatim, then its `Elaboration` verbatim when it has one.
R13a2. Label every answer with the same label its question carried under R12k.
R13a4. IF BATCH = 1 THEN the `— <label>` suffix is optional; a bare `**Answer**` is sufficient.
R13b. Do NOT rewrite, summarize, shorten, or expand `Answer key` or `Elaboration`. Display them as written.
R13a1. One exact `next` releases the WHOLE batch. Do NOT release answers one at a time.
R13c. IF a batch is pending AND the user requests an answer without sending exactly `next` AND the message is not a clarifying or follow-up question THEN tell the user: "Type `next` to reveal the stored answer and continue." Re-display the pending batch. Do NOT release an answer and do NOT advance.
R14. IF a batch is pending AND the user's message is an attempted answer rather than a request THEN re-display the pending batch. Do NOT release an answer and do NOT advance.
R15. Do NOT grade, score, judge, correct, or comment on anything the user types on a pending batch. Do NOT say correct, wrong, close, or partially right.
R16. There is no correct count, no wrong count, and no score.
R17. IF a batch is pending AND the user's message is a clarifying or follow-up question about the material THEN R20 applies: answer it, re-display the pending batch, do NOT release any answer, and do NOT advance.
R18. IF the user's message on a pending batch is ambiguous between R14 and R17 THEN treat it as R17: answer it and re-display the batch. Do NOT advance.
     // Example: "wait, is dependability the same as reliability?" → R17. "something about it being an engineering discipline" → R14.
R19. IF a batch's answers have been released under R13a AND the R4c index contains at least one undelivered position THEN advance: load the next window first if the current one is exhausted (R4d), then deliver the next BATCH questions per R12l.

// Pacing
R20. IF the user sends a clarifying or follow-up question AND a batch is pending THEN answer it fully, then re-display the current pending batch in full. Do not ask "Ready to continue?"
R20a. IF the user sends a clarifying or follow-up question AND no batch is pending THEN answer it fully. Do NOT re-display a batch.

// Wrap up
R28. IF the final batch's answers have been released under R13a AND the R4c index contains no undelivered position THEN display a completion line per R28a and stop.
R28f. Check the R4c index, not the loaded window, to decide whether questions remain.
R28e. R28 overrides R19 when the R4c index contains no undelivered position.
R28a. IF START = 1 THEN the completion line names the topic and the file's full size.
     // Example: `**Complete — 33 questions delivered** (week1 — all 33 questions in this file.)`
R28a1. IF START > 1 THEN the completion line names the topic, M - START + 1 questions delivered, positions START through M, and the file's full size M.
     // Example: `**Complete — 24 questions delivered** (chapter1 — positions 10–33 of 33.)`
R28b. Do NOT display a score, a correct/total ratio, a list of missed questions, or a summary of weak areas. Nothing was graded.
R28c. IF the topic was a chapter AND `extracted/class/` contains any `week<N>/questions_week<N>.md` files THEN, after the completion line, print one line naming the week files as the course-scoped subset.
R28d. IF the topic was a week AND any delivered entry's `Origin` field records `ORPHANED` THEN, after the completion line, print one line naming the count and the fix: re-run `/generate-questions week<N>` and choose `reselect`.

// Catch-all
R29. IF any condition not covered by R1–R28 (including all lettered sub-rules) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Usage

```
/generate-questions chapter2      ← build the pool first — this is where questions are made
/generate-questions week1         ← then select week 1's subset out of it
/learn week1                      ← first pass over week 1's study list: teach then ask

/learn chapter2                   ← first pass over the whole chapter — the reference bank
/learn chapter2 start10           ← begin at absolute question position 10
/learn chapter2 batch3            ← three questions per turn instead of one
```

Questions arrive **one at a time** by default: read it, answer out loud, type `next` to see the
stored answer and move on. Pass `batch<N>` to get several per turn instead — fewer round trips,
lower cost, but you hold several questions in your head at once.

Without `start<N>`, every run delivers the entire file. With `start<N>`, the run delivers every
question from absolute position N through the end. Questions load ten at a time behind the scenes —
you never see the window boundaries. To study a course-scoped subset, pick `week<N>`: the questions
from the book that this week's lectures actually reached.

In-session keywords, typed in reply to a pending question:

```
next      ← show the stored answer, then deliver the next question (R13)
exit      ← end the learn session without revealing an answer (R12o)
```

Anything else you type leaves the pending batch in place. An attempted answer is not graded; an answer request prompts you to type `next`; a question about the material is answered and then the pending batch is re-displayed (R14, R13c, R17).

Questions are numbered straight through the file — `Q1` to `Q<M>` — with no unit headings and no
restart at a chapter boundary. A multi-chapter week reads as one continuous sequence. The number on
screen is the absolute position, so `start<N>` takes exactly the number you last saw: stop at `Q47`,
resume with `start47`.

In format 2 files the heading in the file carries that same absolute number, so what you see on
screen, what `start<N>` takes, and what is written in the file all agree. Format 1 files number
their headings per unit instead — several `Q1`s in one file — and for those the position is counted
rather than read.

The questions file still groups entries under `## Unit` headings recording which chapter each came
from. That is provenance for `/generate-questions resync`; `/learn` never displays it.

The course is resolved from the current directory when you are inside a class, and otherwise by
searching `~/edu/` for the topic file. Several courses have a `week2`, so when the search matches
more than one the run stops and asks which — it never guesses. The session opens with one line
naming the course it loaded.
