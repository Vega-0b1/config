---
name: generate_questions
description: Pre-generate and audit quiz questions from extracted notes for a chapter or topic. Saves questions alongside teaching content to extracted/questions_<arg>.md for use by /learn.
---

Pre-generate audited questions for the specified chapter or topic and save them to `extracted/`.

## Rules

// File loading
R1.  IF argument is given AND a file named `extracted/<arg>.md` exists THEN use that file as the notes source.
R2.  IF argument is given AND no file named `extracted/<arg>.md` exists THEN search all `.md` files in `extracted/` — excluding `questions_*.md` files — for a `##` heading containing the argument as a case-insensitive substring.
     // Commentary: questions_*.md files are this skill's own output; matching their `## Unit N of M` headings would generate questions from questions.
R3.  IF R2 finds a heading match THEN use the content under that heading as the notes source.
R4.  IF R1 fails AND R2–R3 fail THEN list all `.md` files in `extracted/` and ask the user which to use. STOP until user responds.
R5.  IF `extracted/questions_<arg>.md` already exists THEN ask "Overwrite?" STOP until user responds.
R6.  IF user answers no to R5 THEN stop execution.
R6a. IF user answers yes to R5 THEN proceed to R7.

// Unit segmentation
R7.  Count all `##` level headings in the notes source. This count is N.
R8.  Each `##` heading and the content until the next `##` heading (or end of file) = one unit.
R9.  Process units in document order.

// Image handling (per unit)
R9a. Treat any markdown image link — `![...](path)` — in a unit's content as potential answerable content, not as decoration. Transcribed image content counts as note content for R10, R16, and R17.
R9b. IF a unit's content contains an image link that plausibly holds a formula, equation, table, or data value THEN view that image with the Read tool before generating that unit's questions. Resolve the image path relative to the directory of the notes source file.
     // Commentary: an `images/...` link in `extracted/<file>.md` resolves under `extracted/`. Standalone image links between prose sentences (e.g. "we get the recurrence" followed by an image) are transcribed formulas.
R9c. IF an image link is immediately followed by a "**Figure N**" caption AND that caption already conveys the content a question would test THEN you MAY rely on the caption text instead of opening the image.
R9d. IF an opened image contains a formula, table, or data needed by a candidate question THEN transcribe its content into that question's Teach field as text, using plain-text / Unicode math consistent with existing Teach fields (e.g. *n*², Θ(n), ⌊x⌋) — never LaTeX and never a re-embedded image link. R11/R11a/R11b then apply to the transcription.
R9e. IF an image needed for a candidate question cannot be opened or its path cannot be resolved THEN drop that question and record the image in the R25 report. Do NOT guess the image's content.

// Teach content (per question)
R10. IF writing a question THEN write a `Teach:` field immediately before `Question:` containing only the note excerpt(s) needed to answer this specific question — no more.
R11. IF a question's Teach field contains a formula THEN include a Legend block immediately after the formula listing every variable and its meaning.
R11a. IF a question's Teach field contains a formula THEN the Answer key MUST include both (a) a formula-path answer (citing specific terms) and (b) a conceptual-path answer (explaining the mechanism without formula notation). Either path alone is sufficient for a correct grade.
R11b. IF a question's Teach field contains a formula THEN do NOT write the question in a way that mandates formula citation (e.g., do not say "using the formula, show that…"). The question must be answerable via conceptual explanation alone.

// Teach field formatting
R11c. IF the Teach field contains sequential steps THEN format them as a numbered list — one step per line. Do NOT write steps inline as a run-on sentence.
     // FAILS: "Step 1: client sends SYN. Step 2: server sends SYNACK. Step 3: client sends ACK."
     // PASSES:
     // 1. Client sends SYN (SYN=1, seq=client_isn).
     // 2. Server sends SYNACK (SYN=1, seq=server_isn, ack=client_isn+1).
     // 3. Client sends ACK (SYN=0, ack=server_isn+1).
R11d. IF the Teach field enumerates parallel items (reasons, costs, conditions, features) with no strict order THEN format them as a bulleted list — one item per line. Do NOT write them inline as numbered prose.
     // FAILS: "Applications choose UDP for: (1) finer control (2) no delay (3) no state (4) small header."
     // PASSES:
     // - Finer application-level control: UDP sends immediately; TCP may buffer or throttle.
     // - No connection delay: no handshake before data flows.
R11e. All items within a list MUST use parallel grammatical structure — same form for every item (e.g., all "term: explanation" pairs, all imperative clauses). Do NOT mix forms within a single list.
R11f. IF the Teach field contrasts two or more named concepts THEN introduce each concept on its own line as: a colored diamond anchor, then a bold label, then its description. Use the same structure for every concept.
R11f1. Assign each concept's anchor by its order in the contrast, cycling through this fixed sequence: 🔹, 🔸, 🔶, 🔷.
     // Commentary: distinct colors per concept give low-vision readers a per-concept visual anchor that bold alone does not; the fixed order keeps it deterministic.
     // PASSES:
     // 🔹 **Go-Back-N:** receiver discards out-of-order packets; sender retransmits the lost packet plus all subsequent ones.
     // 🔸 **Selective Repeat:** receiver buffers out-of-order packets; only the missing packet is retransmitted.
R11g. IF a Teach field covers two or more clearly distinct sub-concepts THEN separate them with a blank line. Do NOT run distinct concepts together in one paragraph.
R11h. Each sentence in a Teach field MUST express one idea only. Max 25 words per sentence. Do NOT chain multiple concepts with "and," commas, or semicolons into a single sentence.
R11i. Bold each key term the first time it appears in a Teach field.
R11j. No single list in a Teach field should exceed 7 items. IF a natural grouping exceeds 7 THEN split into labeled sub-groups with a bold label for each.

R12. The Teach field is sufficient IF AND ONLY IF the question is fully answerable from that Teach field alone, given that the user has already seen all prior questions' Teach fields within the same unit in order.
     // Commentary: later questions in a unit may omit foundational context that an earlier question's Teach field already covered.
R12a. IF a concept required to answer this question was already covered in a prior question's Teach field within the same unit THEN the Teach field MAY omit re-explaining that concept.
R12b. R12 overrides R12a: IF omitting the prior context would make the Teach field insufficient to answer the question THEN include it anyway.

// Question generation (per unit)
R13. Generate between 2 and 5 candidate questions per unit.
R13a. Order questions within each unit from most foundational concept to most complex, so later questions may safely rely on earlier ones having been seen.
R14. Each question MUST target exactly ONE concept from this unit's notes.
R14a. R15 overrides R14 for contrast questions: a question contrasting two concepts counts as targeting the one contrast, provided both concepts appear in this unit's notes.
     // Commentary: contrasting two ideas forces deeper processing than recalling one — contrast questions serve retention and must not be blocked by R14.
R15. Each question MUST require the user to explain a mechanism, describe a scenario, or contrast two ideas.
     A question is prohibited if it can be answered by pattern-matching a single definition phrase.
     // Mental test: "Does answering this correctly prove the user understands how it works — not just that they remember its name?"
     // PASSES R15: "Describe why non-persistent HTTP is expensive in terms of delay."
     // FAILS R15: "What does HTTP stand for?"
R15a. Each `Question:` field MUST contain exactly one question — one interrogative, one `?`. Compound questions are prohibited.
     // FAILS R15a: "What distinguishes the network layer from the transport layer? Explain what this means for an application sending data."
     // PASSES: Two separate entries — Q1 asks the first; Q2 asks the implication.
R15b. IF a concept produces two natural sub-questions (e.g., "what is X" and "what does X imply for Y") THEN generate them as two separate entries in the same unit, each with its own Teach, Question, Answer key, and Audit.
R15c. R15a overrides R15: IF satisfying R15 would require two interrogatives in one entry THEN split into two entries per R15b.
R15d. IF a unit yields 3 or more PASS questions THEN the unit MUST include at least two different R15 question types (mechanism, scenario, contrast).
     // Commentary: varied retrieval aids retention — five mechanism questions in a row is monotone drilling.
R16. Each question MUST be fully answerable using only this question's Teach field, given that prior questions' Teach fields within the same unit have been shown in order.

// Audit (per candidate question)
R17. Identify the specific sentence(s) in this question's Teach field that contain the answer. IF no such sentence exists THEN mark FAIL.
R17a. IF the Question field contains more than one `?` THEN mark FAIL with reason "compound question — split into two entries per R15a–R15b".
R18. IF the answer requires knowledge beyond those sentence(s) THEN mark FAIL.
R18a. IF a Teach field transcribes content from an image THEN the cited answer sentence(s) must faithfully match the opened image's actual content. IF the transcription was not verified against the opened image THEN mark FAIL.
R19. IF this question's Teach field states a fact without an explanation AND the question asks "why" about that fact THEN mark FAIL.
R20. IF an acronym or term appears in the question AND it is not defined in this question's Teach field AND it was not defined in a prior question's Teach field within the same unit THEN mark FAIL.
R21. IF a candidate question is not marked FAIL by R17–R20 THEN mark PASS.
R22. Drop all FAIL questions. Only PASS questions go into the output file.
R23. R23 overrides R13: IF all candidates for a unit fail audit THEN generate a new round of candidates targeting different concepts, contrasts, or scenarios within the unit's notes and re-audit each.
R23a. IF 3 rounds of candidates for a unit have all failed audit THEN stop, show the user the failed candidates with their fail reasons and the unit's notes, and ask whether to (a) keep generating or (b) skip the unit. STOP until user responds.
     // Commentary: no near-miss option — a question not fully answerable from its Teach field produces frustration, not retention.
R23b. Do NOT declare a unit unquestionable without completing R23a.

// Output
R24. Save to `extracted/questions_<arg>.md` using the exact structure in the Output Format block below.
R24a. IF the questions file is saved AND the class root contains a `CLAUDE.md` with a `## Contents` section THEN add a one-line entry for `questions_<arg>.md` under its `**extracted/**` group. IF the section has no `**extracted/**` group THEN create the group header first. IF an entry for the file already exists THEN replace that line instead of duplicating.
R24b. IF the questions file is saved AND the class root contains a `CLAUDE.md` without a `## Contents` section THEN append a `## Contents` section (format: `**<dir>/**` bold group headers, one `- file — description` line per entry) and add the entry per R24a.
R24c. IF the class root contains no `CLAUDE.md` THEN skip R24a–R24b.
R24d. IF updating the Contents section THEN do not modify any other part of `CLAUDE.md`.
R25. After saving, report: (1) units processed, (2) questions saved, (3) candidates dropped and their fail reasons, (4) output file path, (5) whether `CLAUDE.md` Contents was updated, (6) images opened (count), (7) any candidate questions dropped because an image could not be opened or resolved (per R9e).

// Catch-all
R26. IF any condition not covered by R1–R25 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Output Format

```
---
name: questions_<arg>
source: <notes filename>
generated: <today's date>
---

## Unit 1 of N — <Unit Title>

#### Q1
Teach:
<only the note excerpt(s) needed to answer Q1 — no more>
Question: <question text>
Tests: <one-line description of the concept being tested>
Answer key: <the key idea(s) a correct answer must include — be specific>
Audit: PASS — <cite the exact phrase in the Teach field that contains the answer>

#### Q2
Teach:
<excerpt for Q2 — may omit concepts already covered in Q1's Teach per R12a>
Question: <question text>
Tests: ...
Answer key: ...
Audit: PASS — ...

## Unit 2 of N — <Unit Title>

#### Q1
Teach:
...
```

// Note: Tests and Audit are internal metadata. /learn displays only the Teach field (teach mode) and Question, and uses Answer key for grading.

## Usage

```
/generate_questions chapter2
/generate_questions wk10
```
