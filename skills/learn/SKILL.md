---
name: learn
description: 'Deliver pre-generated questions for `/learn chapter1` or a lecture deck such as `/learn lec13`. Questions arrive one at a time with a Teach block paired to each question; `next` reveals the stored answer and advances. Supports a start argument, and `/learn chapter1 problems` or `/learn lec13 problems` delivers the chapter's or deck's computational problems. Does not generate or grade questions.'
---

Deliver course material question by question using a pre-generated questions file. `/learn` is a delivery engine — it does not generate content or questions, and it does not grade. Content comes from `/generate-questions`; the verdict comes from you.

Two topics, two files, both delivered from the selected starting position through the end:

- `/learn lec13` — the questions generated from one lecture deck's slides. This is the study list for a course you are currently taking.
- `/learn chapter1` — the whole textbook chapter. This is the reference bank: everything the book explains, whether the course reached it or not.

`/generate-questions chapter<N>` writes a chapter file from the textbook, and
`/generate-questions <deck>` writes a lecture file from that deck's slides. The two are independent.

The topic argument selects the file. The optional `start<N>` argument selects the first absolute question position to deliver; without it, delivery begins at position 1.

**The loop:** teach material, ask the current question, wait. You answer however you like — out loud, on paper, in your head. Type `next` and the stored answer appears. Compare it yourself, then the next question follows. Nothing you type is judged, and no score is kept.


## Rules

// Argument parsing and loading
R1. IF a `/learn` invocation begins THEN preserve its unmodified argument tokens as ORIGINAL_ARGUMENTS.
R1a. IF more than one argument remains after removing the option tokens under R1b and R1f THEN stop and ask the user which one is the topic. STOP until user responds.
R1b. IF ORIGINAL_ARGUMENTS contains exactly one token matching `start<N>` where N is an integer greater than zero THEN START = N; remove that token from the working arguments.
R1b1. IF ORIGINAL_ARGUMENTS contains no token beginning with `start` THEN START = 1.
R1b2. IF ORIGINAL_ARGUMENTS contains more than one token beginning with `start` THEN stop and tell the user: "Use exactly one start<N> argument."
R1b3. IF an ORIGINAL_ARGUMENTS token begins with `start` but does not match `start<N>` where N is an integer greater than zero THEN stop and tell the user: "Invalid start position — use start<N> with N greater than zero."
R1b5. IF R1b2 and R1b3 both apply THEN R1b2 overrides R1b3.
R1f. IF ORIGINAL_ARGUMENTS contains a `problems` token, case-insensitively, THEN PROBLEMS = true; remove that token from the working arguments. Otherwise PROBLEMS = false.
R1f1. IF PROBLEMS = true AND no topic remains after removing the option tokens THEN stop and tell the user: "Name a chapter or a deck: /learn chapter<N> problems or /learn <deck> problems."
R1f2. IF PROBLEMS = true THEN the topic name shown in R7b and R28a–R28a1 reads `<topic> problems` — `chapter<N> problems` for a chapter, `<DECK ID> problems` for a deck.
     // Example: `/learn lec13 problems` opens with `network — lec13_dijkstra problems, 5 questions.`
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
R3.  IF <arg> matches `week<N>` or `wk<N>`, case-insensitively, THEN stop and tell the user: "Week files were removed; use /learn <deck> for each lecture deck."
R3d. IF <arg> matches neither `week<N>`, `wk<N>`, nor `chapter<N>` THEN look under `extracted/class/` for `*/questions_<arg>.md`; IF none exists THEN look for `*/questions_<arg>_*.md`. Match case-insensitively. Apply this lookup during R2b's class search too.
R3d1. IF R3d finds exactly one file THEN use it.
R3d2. IF R3d finds several files at the same step THEN list them and ask the user which deck. STOP until user responds.
     // Example: `/learn lec13` finds `lectures/questions_lec13_dijkstra.md` through the `questions_lec13_*.md` step.
R3a. IF <arg> matches `chapter<N>` THEN check both `extracted/textbook/chapters/chapter<N>/questions_chapter<N>.md` and `extracted/textbook/chapters/capitulo<N>/questions_capitulo<N>.md`; use the sole existing path, or the class's recorded chapter convention when both exist, and ask only if both remain ambiguous. Apply this lookup during R2b's class search too.
R3c. IF PROBLEMS = true THEN R3a checks `problems_chapter<N>.md` and `problems_capitulo<N>.md` in the same directories instead of the `questions_` files. R3c overrides R3a's filenames only.
R3c1. IF PROBLEMS = true THEN R3d looks for `*/problems_<arg>.md`, then `*/problems_<arg>_*.md`, instead of the `questions_` files. R3c1 overrides R3d's filenames only.
     // Example: `/learn lec13 problems` finds `lectures/problems_lec13_dijkstra.md` through the `problems_lec13_*.md` step.
R3c2. IF PROBLEMS = true THEN skip R3b. A problems topic never falls back to a `questions_` file.
R3b. IF R3d finds no file THEN look for `extracted/questions_<arg>.md` as a fallback.
R4. IF the file exists THEN set QUESTION_COUNT to the output of `grep -c '^#### Q' <file>`.
R4a. IF QUESTION_COUNT = 0 THEN stop and tell the user: "Questions file is empty — re-run /generate-questions <arg>." IF PROBLEMS = true THEN the command reads `/generate-questions <arg> problems`.
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
R5.  IF the file does not exist THEN stop and tell the user: "Run /generate-questions <arg> first." IF PROBLEMS = true THEN the command reads `/generate-questions <arg> problems`.
R6.  IF no <arg> is given THEN display the `/learn` usage examples from the Usage section and stop.

// Course scope notice
R6a. After loading the file per R3–R4 and before the first question: IF the topic is a chapter AND the class `CLAUDE.md` holds a `### Course Scope` entry listing that chapter as not covered THEN print one line saying the course does not cover it. Then proceed normally.
R6a1. IF the topic is a lecture deck THEN print no scope notice. A lecture file comes from the professor's own slides, so it is in scope by construction.
R6b. R6a is a notice, not a gate. Do NOT refuse, do NOT ask for confirmation.
R6d. IF a `### Course Scope` entry exists but carries no derivable chapter list — `covers` reads `NOT DETERMINED`, is empty, or names no chapter — THEN treat the class as having no scope entry and print no notice. Do NOT stop under R29.

// Question delivery
R7.  Delivery is FLAT. Do NOT display unit headings, unit numbers, unit titles, or unit boundaries at any point. The `## Unit X of Y` headings in the questions file are provenance metadata, not display structure.
R7a. IF the file holds several units THEN deliver its questions as one continuous sequence across them. A unit boundary is invisible to the user and is never announced.
R7b. Before the first question of a session, display ONE line naming the resolved course, the topic, and the delivery range — e.g. `network — lec13_dijkstra, 12 questions.` IF START > 1 THEN the range reads `positions <START>–<M> of <M>`. This is the whole session opener; do NOT add a title, a rule, a summary, or a unit heading.
R7c. R7b fires exactly once per session, before the first question only. Do NOT repeat it at a window edge, at a unit boundary, or when re-displaying a pending question under R13c/R14/R20b.
R8.  IF about to display a question THEN first display the level-3 markdown heading `### 📘 Teach`.
     // Example: Display `### 📘 Teach`, then its blockquote, then `### ❓ Q6 — <question text>`.
R8e. IF R8 applies THEN display that question's `Teach:` field verbatim as a markdown blockquote and prefix every line with `> `.
R8d. IF R8e displays Teach AND the entry has a `Legend:` field AND R8f does not apply THEN append Legend inside the same blockquote.
R8f. IF the entry's `Legend:` field is a GIVENS legend THEN display it after the Teach blockquote, under its own level-3 heading `### 📋 Given`, as a bulleted list, and NOT inside the Teach blockquote.
R8f1. A Legend is a GIVENS legend IF its first non-blank line begins with neither `- **` (a symbol-definition list) nor `A)` (multiple-choice options).
     // PASSES: `Host A → router → router → Host B (3 links). Packet = 1500 bytes.` → givens → own block.
     // FAILS:  `- **L** — the length of the packet, in bits.` → symbol definitions → stays inside Teach per R8d.
     // FAILS:  `A) d/s  B) R/L  C) L/R  D) L·R` → options → stays inside Teach per R8d.
R8f2. IF R8f applies THEN make one bullet per Legend line, and split a line into further bullets at each `. ` and each ` · ` that falls outside backticks. Drop each item's trailing period. Do NOT change any other character.
     // Example: `One link: 20,000 km, s = 2.5×10⁸ m/s, R = 10 Mbps. Packet = 1000 bytes.` → `- One link: 20,000 km, s = 2.5×10⁸ m/s, R = 10 Mbps` and `- Packet = 1000 bytes`.
R8a. IF R8, R8e, or R8f adds a heading, a `> ` prefix, or a `- ` bullet THEN treat it as display framing rather than content. R10 does not prohibit it.
R8b. IF R8e displays Teach THEN after the Teach blockquote (and after the R8f Given block, when present) and before the Question, output a blank line, a `---` horizontal rule, and a blank line.
R8c. R8b overrides the global AGENT.md response-style ban on `---` horizontal rules, for the Teach/Question separator only.
R8g. IF a question carries `Diagram` THEN display its Markdown image after Teach and any Given block, before the Teach/Question separator; resolve its path from the class root and emit an absolute local image path in chat.
R8g1. IF an entry carries diagram fields AND those fields have not been checked during this session THEN run `python3 ~/repos/config/skills/generate-questions/verify_diagrams.py <questions-file>` before displaying the entry; this mechanical file read does not load question text into the model's window.
R8g2. IF that verifier fails THEN report the exact error and stop delivery without revealing the answer or advancing; retain the pending position.
R8g3. IF re-displaying a diagram-bearing pending question THEN re-display its question image under R8g.
R8g4. IF the entry has no diagram fields THEN retain the existing text-only delivery without running a diagram verifier or reading figure assets.
R10. Do NOT rewrite, summarize, or add to the Teach field.
R11. Do NOT display `Type`, `Concept`, `Source quote`, `Tests`, `Audit`, `Check`, `Origin`, `Teach_EN`, or `Question_EN` at any point.
R11b. R11d is the governing rule and it is a WHITELIST: an entry field not named there is never displayed, whether or not R11 enumerates it.
R11d. IF delivering a question THEN display only the Teach label, `Teach`, optional `Legend` (inside Teach per R8d, or under the Given label per R8f), optional `Diagram` per R8g, and `Question` per R8–R8f2 and R12k.
R11d1. IF releasing an answer THEN display only `Answer key`, optional `Elaboration`, and optional `Answer diagram` per R13a and R13a1.
R11a. Do NOT display the `Answer key` or `Elaboration` field when delivering a question. They are released only under R13a.

// Question delivery loop
R12. IF a question is delivered THEN STOP and wait for the user.
R12k. Displaying one question = its `Question` field rendered as a level-3 markdown heading with a `❓` anchor and its ABSOLUTE POSITION as the label: `### ❓ Q<p> — <question text>`, where `<p>` is the question's absolute position from the R4c step-2 index. R8 and R8b precede it.
R12k3. IF the `Question` field has continuation lines THEN `<question text>` in R12k is its first line only. Display the continuation lines below the heading as a markdown bulleted list, one option per bullet, with the two-space indent stripped and each line's text otherwise unchanged.
     // Example: `Question: Which are UML diagrams?` + `  - a) Class` + `  - b) State` → `### ❓ Q5 — Which are UML diagrams?`, then `- a) Class` and `- b) State` on separate lines.
R12k4. IF R12k3 adds a bulleted list THEN treat it as display framing under R8a.
R12k1. IF the file is format 1 per R4c1b THEN IGNORE the heading's `Q<n>` label for display; it restarts at Q1 in every unit and is not unique. Do NOT display it and do NOT combine it with a unit prefix.
R12k2. IF the file is format 2 per R4c1a THEN the heading label and the absolute position are the same number, and displaying either is correct.
R12l. IF a question is due for delivery THEN display that one question per R12k. Do NOT reveal its answer.
R12m. IF a question is pending THEN do NOT display the next question until the pending question's answer has been released under R13a.
R12o. IF a question is pending AND the user's message, after trimming whitespace and ignoring case, is exactly `exit` THEN clear the active in-chat question, say "Learn session ended.", and stop. Do NOT release an answer, advance, or write session state. R12o overrides R13c, R14, R17, and R18.

R13. IF a question is pending AND the user's message, after trimming whitespace and ignoring case, is exactly `next` THEN display the answer per R13a and advance per R19.
R13a. Displaying the answer = output the heading `**Answer**`, then the pending question's `Answer key` verbatim, then its `Elaboration` verbatim when it has one.
R13a1. IF releasing an answer with `Answer diagram` THEN display that image after the stored answer and elaboration, resolving its class-root-relative path to an absolute local image path.
R13a2. IF the entry has `Answer diagram` THEN withhold it before R13a releases the answer, including on clarifications and re-displays.
R13b. Do NOT rewrite, summarize, shorten, or expand `Answer key` or `Elaboration`. Display them as written.
R13c. IF a question is pending AND the user requests an answer without sending exactly `next` AND the message is not a clarifying or follow-up question THEN tell the user: "Type `next` to reveal the stored answer and continue." Re-display the pending question. Do NOT release the answer and do NOT advance.
R14. IF a question is pending AND the user's message is an attempted answer rather than a request THEN re-display the pending question. Do NOT release the answer and do NOT advance.
R15. Do NOT grade, score, judge, correct, or comment on anything the user types about a pending question. Do NOT say correct, wrong, close, or partially right.
R16. There is no correct count, no wrong count, and no score.
R17. IF a question is pending AND the user's message is a clarifying or follow-up question about the material, or a tangent on any topic, THEN R20 applies: answer it, do NOT re-display the pending question, do NOT release the answer, and do NOT advance.
R18. IF the user's message on a pending question is ambiguous between R14 and R17 THEN treat it as R17: answer it without re-displaying the question. Do NOT advance.
     // Example: "wait, is dependability the same as reliability?" → R17. "something about it being an engineering discipline" → R14.
R19. IF a question's answer has been released under R13a AND the R4c index contains at least one undelivered position THEN advance: load the next window first if the current one is exhausted (R4d), then deliver the next question per R12l.

// Pacing
R20. IF the user sends a clarifying or follow-up question AND a question is pending THEN answer it fully and stop. Do NOT re-display the pending question and do NOT ask "Ready to continue?"
R20b. IF a question is pending AND the user's message, after trimming whitespace and ignoring case, is exactly `resume` THEN re-display the pending question per R8–R12k, including its Diagram under R8g3. Do NOT release the answer and do NOT advance.
R20c. IF a tangent under R17 is in progress THEN the question stays pending: `next` still releases its answer under R13, and `exit` still ends the session under R12o.
R20a. IF the user sends a clarifying or follow-up question AND no question is pending THEN answer it fully. Do NOT re-display a question.

// Wrap up
R28. IF the final question's answer has been released under R13a AND the R4c index contains no undelivered position THEN display a completion line per R28a and stop.
R28f. Check the R4c index, not the loaded window, to decide whether questions remain.
R28e. R28 overrides R19 when the R4c index contains no undelivered position.
R28a. IF START = 1 THEN the completion line names the topic and the file's full size.
     // Example: `**Complete — 12 questions delivered** (lec13_dijkstra — all 12 questions in this file.)`
R28a1. IF START > 1 THEN the completion line names the topic, M - START + 1 questions delivered, positions START through M, and the file's full size M.
     // Example: `**Complete — 24 questions delivered** (chapter1 — positions 10–33 of 33.)`
R28b. Do NOT display a score, a correct/total ratio, a list of missed questions, or a summary of weak areas. Nothing was graded.
R28c. IF the topic was a chapter AND PROBLEMS = false AND `extracted/class/` contains any `*/questions_*.md` lecture files THEN, after the completion line, print one line naming those lecture files as the course's own study lists.

// Catch-all
R29. IF any condition not covered by R1–R28 (including all lettered sub-rules) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Usage

```
/learn                            ← show these usage examples
/generate-questions lec13         ← build a lecture deck's questions first
/learn lec13                      ← first pass over that lecture: teach then ask

/learn chapter2                   ← first pass over the whole chapter — the reference bank
/learn chapter2 start10           ← begin at absolute question position 10
/learn chapter2 problems          ← every computational problem in chapter 2 (from /generate-questions chapter2 problems)
/learn lec13 problems             ← every computational problem on lecture 13's slides (from /generate-questions lec13 problems)
```

Questions arrive **one at a time** by default: read it, answer out loud, then type `next` to see the
stored answer and move to the next question.

Every Teach block is headed `📘 Teach` immediately before its matching `❓ Q<N>` question. A
calculation question's scenario values sit between them under `📋 Given`, apart from the reference
material.

Without `start<N>`, every run delivers the entire file. With `start<N>`, the run delivers every
question from absolute position N through the end. Questions load ten at a time behind the scenes —
you never see the window boundaries. To study what a lecture covered, pick that deck: `/learn lec13`.

In-session keywords, typed in reply to a pending question:

```
next      ← show the pending stored answer, then continue (R13)
resume    ← show the pending question again after a tangent (R20b)
exit      ← end the learn session without revealing an answer (R12o)
```

Anything else you type leaves the pending question in place. An attempted answer is not graded; an answer request prompts you to type `next`; a question about the material — or any tangent — is answered without re-showing the pending question, so you can keep asking; type `resume` to see it again (R14, R13c, R17, R20b).

Questions are numbered straight through the file — `Q1` to `Q<M>` — with no unit headings and no
restart at a unit boundary. The number on
screen is the absolute position, so `start<N>` takes exactly the number you last saw: stop at `Q47`,
resume with `start47`.

In format 2 files the heading in the file carries that same absolute number, so what you see on
screen, what `start<N>` takes, and what is written in the file all agree. Format 1 files number
their headings per unit instead — several `Q1`s in one file — and for those the position is counted
rather than read.

The questions file still groups entries under `## Unit` headings recording where each came from.
That is provenance; `/learn` never displays it.

The course is resolved from the current directory when you are inside a class, and otherwise by
searching `~/edu/` for the topic file. Several courses have a `chapter2`, so when the search matches
more than one the run stops and asks which — it never guesses. The session opens with one line
naming the course it loaded.
