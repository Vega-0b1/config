---
name: generate_questions
description: Pre-generate and audit quiz questions from extracted notes for a chapter or topic. Saves questions alongside teaching content to extracted/questions_<arg>.md for use by /learn.
---

Pre-generate audited questions for the specified chapter or topic and save them to `extracted/`.

## Rules

// Source profile
R0.  Before loading notes, look for a `## Source Profile` section in the class root's `CLAUDE.md`.
R0a. IF a Source Profile exists THEN use it. Do NOT re-detect.
R0b. IF no Source Profile exists THEN detect the source's shape per R0c–R0f, write it to `CLAUDE.md` as a `## Source Profile` section, and report that it was created.
R0c. Chapter heading = the shallowest heading level whose text matches a chapter form (`# Chapter N`, `## N`, `# N`). A heading-like line is NOT a heading if it is a code comment — judge by whether it sits among code lines rather than prose.
     // Commentary: a PDF extraction can turn `# !/usr/bin/python3` into what looks like a top-level heading. Counting those destroys the chapter map.
R0d. Unit heading = the heading level one deeper than the chapter level. IF only one heading level exists THEN unit = chapter.
R0e. Anchor source = `apparatus` IF an alias from R12i0 appears in at least 80% of chapters AND that section is enumerated per R0e1; ELSE `instructor` IF the class root holds a syllabus, exam, or slide deck; ELSE `none`.
R0e1. An apparatus section is `enumerated` IF its content is a bulleted or numbered list of discrete claims. A running-prose recap is NOT enumerated, even when titled "Summary".
     // Commentary: presence of the heading is not enough. The anchor has to be a set of separable statements that concepts can be ranked against one at a time.
     // PASSES R0e1: Sommerville Key Points — "■ Software engineering is an engineering discipline that is concerned with all aspects of software production." Discrete and rankable.
     // FAILS R0e1:  Kurose chapter Summary — "In this chapter we've covered a tremendous amount of material! We've looked at the various pieces of hardware and software that make up the Internet..." It renarrates the whole chapter, so every concept matches it and it ranks nothing.
R0f. Generation mode = `tiered` IF anchor source is not `none`; ELSE `capped`.
R0g. The user may correct a Source Profile by hand. R0a makes the correction permanent.
     // Commentary: detection is a heuristic and will sometimes be wrong. Persisting the result means a wrong guess is corrected once rather than re-made every run.

// File loading
R1.  IF argument is given AND a file named `extracted/<arg>.md` exists THEN use that file as the notes source.
R2.  IF argument is given AND no file named `extracted/<arg>.md` exists THEN normalize the argument and search all `.md` files in `extracted/` — excluding `questions_*.md` and `practice_*.md` files — for a chapter heading matching it under the Source Profile's chapter heading pattern.
R2a. Normalization: `chapter<N>`, `ch<N>`, and `<N>` all match the chapter whose number is `<N>`. Matching is on the chapter NUMBER, not on the argument as a literal substring.
     // Commentary: `chapter5` is not a substring of `## 5`. Before R2a this failed on every chapter and had to be bridged by hand.
R2b. IF the argument does not normalize to a chapter number THEN fall back to matching it as a case-insensitive substring of a heading.
     // Commentary: keeps non-chapter arguments such as `wk10` working.
     // Commentary: questions_*.md and practice_*.md are this skill's own output; matching their headings would generate questions from questions.
R3.  IF R2 finds a heading match THEN use the content under that heading as the notes source.
R4.  IF an argument is given AND neither R1 nor R2–R3 locates a source THEN list all `.md` files in `extracted/` — excluding `questions_*.md` and `practice_*.md` — and ask the user which to use. STOP until user responds.
R4a. IF no argument is given THEN list those same files, ask the user which to use, and STOP until user responds. Do not proceed on an empty argument.
R4b. IF the source was chosen under R4 or R4a AND no argument was given THEN ask the user for the `<arg>` to name the output file, and STOP until user responds. Do not derive it.
     // Commentary: R24, R24a, and R24e all build filenames from `<arg>`. Picking a source without an `<arg>` leaves the output path undefined, and a guessed name is what /learn will fail to find later.
R5.  IF `extracted/questions_<arg>.md` already exists THEN ask "Overwrite?" STOP until user responds.
R6.  IF user answers no to R5 THEN stop execution.
R6a. IF user answers yes to R5 THEN proceed to R7.

// Unit segmentation
R7.  Count the headings matching the Source Profile's unit heading pattern inside the selected chapter. This count is N.
R8.  Each unit heading and its content until the next unit heading, or the end of the chapter, = one unit.
R8a. IF the Source Profile records `Unit heading: none` THEN the whole chapter is a single unit and N = 1.
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
R11c1. R11c applies only when each step is an action (a verb phrase describing something done). IF the ordered items are named concepts (nouns naming a phase, component, or mechanism) THEN R11f applies instead of R11c.
     // Example: SYN → SYNACK → ACK are actions → numbered list (R11c). Divide / Conquer / Combine are named phases → diamond anchors (R11f).
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
R11f2. R11f overrides R11d: IF each item names a distinct concept, mechanism, protocol, or component (a noun naming a thing) THEN use diamond anchors (R11f), even if the items could also be read as parallel items. R11d bullets apply only when the items are NOT named concepts (reasons, costs, conditions, features, effects).
     // PASSES R11f2 (diamonds): Daemon vs Set-UID; UDP vs TCP; Static linking vs Dynamic linking.
     // PASSES R11d (bullets): the reasons an application chooses UDP; the costs of static linking.
R11g. IF a Teach field covers two or more clearly distinct sub-concepts THEN separate them with a blank line. Do NOT run distinct concepts together in one paragraph.
R11h. Each sentence in a Teach field MUST express one idea only. Max 25 words per sentence. Do NOT chain multiple concepts with "and," commas, or semicolons into a single sentence.
R11i. Bold each key term the first time it appears in a Teach field.
R11j. No single list in a Teach field should exceed 7 items. IF a natural grouping exceeds 7 THEN split into labeled sub-groups with a bold label for each.

R12. The Teach field is sufficient IF AND ONLY IF the question is fully answerable from that Teach field alone, given that the user has already seen all prior questions' Teach fields within the same unit in order.
     // Commentary: later questions in a unit may omit foundational context that an earlier question's Teach field already covered.
R12a. IF a concept required to answer this question was already covered in a prior question's Teach field within the same unit THEN the Teach field MAY omit re-explaining that concept.
R12b. R12 overrides R12a: IF omitting the prior context would make the Teach field insufficient to answer the question THEN include it anyway.

// Concept inventory (per unit)
R12c. Before generating any question for a unit, enumerate that unit's testable concepts. This list is the unit's concept inventory.
R12d. A concept belongs in the inventory IF AND ONLY IF the unit's notes contain at least one sentence explaining a mechanism, stating a contrast, or describing a scenario for that concept.
R12e. IF adding a concept to the inventory THEN record alongside it the exact sentence from the notes that satisfies R12d. IF no such sentence can be quoted THEN do NOT add the concept.
     // Commentary: this is R17 applied before writing rather than after. A concept whose explanation cannot be quoted cannot yield a question that survives audit.
     // PASSES R12e: Generalization — "common information will be maintained in one place only . . . you do not have to look at all classes in the system to see if they are affected by the change."
     // FAILS R12e:  Aggregation — the notes give only a definition (one object is composed of others) and a notation (a diamond on the link). No sentence explains a mechanism.
R12f. Exclude from the inventory: bibliographic references, author names, tool and product names, chapter objective lists, further-reading sections, end-of-chapter exercises, and page headers.
     // Commentary: R12f excludes objectives and key points as a SOURCE of questions. R12i uses them as EVIDENCE OF PRIORITY. These are not in conflict — no question is generated from an objective, but every concept is graded against them.
R12g. IF two inventory concepts would produce questions with the same Answer key idea THEN merge them into one concept.

// Exercise classification (per unit) — runs before priority assignment; R12i reads its output
R12h0. IF the chapter contains an `Exercises` section THEN classify each numbered exercise as `analytical` or `constructive`.
R12h0a. An exercise is `analytical` IF it asks the reader to explain, discuss, describe, compare, suggest a reason, or give examples.
R12h0b. An exercise is `constructive` IF it asks the reader to produce an artifact — draw, design, develop, model, write, or rewrite.
R12h0c. IF an exercise contains both an analytical and a constructive clause THEN classify it `analytical`.
     // Example: 5.8 "Draw a sequence diagram for the same system. Explain why you might want to develop both activity and sequence diagrams" → analytical, on the strength of the second clause.
     // Commentary: only analytical exercises have an answer that fits the Teach + Answer key format. Constructive exercises are preserved under R24e.

// Priority assignment (per inventory concept)
R12h. IF a concept is admitted to the inventory THEN assign it a priority of `core` or `supporting`.
R12h1. R12h1 overrides R12h: IF generation mode = `capped` THEN skip R12h–R12m and R12r–R12s entirely and emit `Priority: untiered` on every entry.
R12h2. R12h1 does NOT skip R12h0–R12h0c. Exercise classification runs in every generation mode.
     // Commentary: R24e writes constructive exercises to practice_<arg>.md regardless of mode. Folding classification into the skipped range would silently drop that file for every capped class.
     // Commentary: `untiered` is not `supporting`. It records that this class's textbook offers no anchor to rank against, so /learn can say so precisely instead of advising a regeneration that would not help.
R12i0. Apparatus sections are recognized case-insensitively by any of these headings: Objectives, Learning Objectives, Chapter Objectives, Key Points, Summary, Chapter Summary, Key Terms, Exercises, Problems, Homework Problems, Review Questions, Discussion Questions.
     // Commentary: different publishers name the same apparatus differently. The Source Profile records which aliases a given book actually uses.
R12i. A concept is `core` IF AND ONLY IF it is required to answer at least one statement in an apparatus section of the kind named by the Source Profile — for example an `Objectives` list, a `Key Points` list, or an `analytical` exercise.
     // Commentary: the anchors are complementary, not redundant. Sommerville chapter 1's exercises are almost entirely analytical and its Key Points miss the generic-vs-custom distinction that exercise 1.2 asks about directly. Chapter 4's exercises are mostly constructive and its Key Points already cover the chapter well.
R12i1. Each `core` concept is assigned to exactly ONE statement — the statement it most directly serves.
R12i2. No statement may carry more than 3 `core` concepts. IF more than 3 concepts are assigned to one statement THEN retain as `core` the 3 that most directly deliver that statement; reassign the rest to `supporting`.
     // Commentary: some Key Points are written as topic headings rather than claims — Sommerville's "General process models describe the organization of software processes. Examples include the waterfall model, incremental development, and reusable component configuration and integration" matches 9 concepts in chapter 2 on its own. Without a cap, a broad statement silently promotes an entire chapter section to core and the priority tier stops discriminating.
R12j. R12i counts an Objective only when that Objective is phrased with a mastery verb ("understand", "know about"). IF an Objective is phrased "have been introduced to" THEN a concept serving only that Objective is `supporting`.
     // Commentary: "have been introduced to" states familiarity, not mastery.
     // PASSES R12j (core): "understand the fundamental system modeling perspectives of context, interaction, structure, and behavior" — mastery verb.
     // FAILS R12j (supporting): "have been introduced to four systems, of different types, which are used as examples throughout the book" — familiarity verb.
R12k. IF a concept is not `core` under R12i–R12j THEN it is `supporting`.
R12l. IF assigning `core` THEN record alongside the concept the Objective or Key Point statement it serves.
     // Commentary: R12i is a lookup against the author's own statements, not a judgment about importance. Naming the statement is what makes the assignment checkable after the fact.
R12m. The concept inventory is internal metadata. Do NOT write it to the output file. The priority assigned under R12h–R12l and the statement recorded under R12l ARE written to the output file, in the `Priority:` field defined in the Output Format block.

// Inventory gap check (per unit)
R12r. IF an `analytical` exercise asks about a topic that no inventory concept covers THEN record it as an inventory gap.
R12s. IF an inventory gap is recorded THEN attempt to admit the missing concept under R12d–R12e. IF no sentence in the chapter body explains it THEN leave it uncovered and report it under R25.
     // Commentary: an exercise can ask about something the chapter never explains — ch1 exercise 1.7 (how electronic connectivity between development teams supports software engineering) is one. A question for it would fail R17/R18. Reporting the gap is more honest than manufacturing an unanswerable question.

// Question generation (per unit)
R13. IF generation mode = `tiered` THEN generate exactly one candidate question per concept in the unit's concept inventory. There is no fixed upper or lower bound on the number of questions per unit.
R13a. IF generation mode = `capped` THEN generate between 2 and 5 candidate questions per unit, choosing the concepts that most directly carry that unit's subject. R13a overrides R13.
     // Commentary: the priority tier and this cap are two solutions to the same problem — stopping over-generation. The tier is better but needs an anchor. Without one, the cap is what keeps a 300,000-word textbook from producing 900 questions nobody has time to answer.
R13b. Order questions within each unit from most foundational concept to most complex, so later questions may safely rely on earlier ones having been seen.
R13c. R15b overrides R13: IF one inventory concept produces two natural sub-questions THEN that concept yields two entries.
R13d. IF a unit's concept inventory is empty THEN stop, show the user the unit's notes, and ask how to proceed. Do not improvise.
R13e. Before saving, check each candidate question against the inventory. IF a question does not map to exactly one inventory concept THEN drop it.
     // Commentary: R13e is the anti-padding guard — it catches questions invented to fill space rather than derived from the material.
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
R15e. IF a unit yields 6 or more PASS questions THEN all three R15 question types (mechanism, scenario, contrast) MUST appear in that unit.
     // Commentary: R15d's two-type floor is adequate for a short unit and toothless for a long one.
R15f. R13 and R14a override R15d–R15e: IF the unit's inventory contains no two concepts the notes actually contrast, or no concept the notes give a scenario for, THEN the missing type is not required. Report the shortfall under R25 instead.
     // Commentary: R13 derives questions from the inventory, one per concept. A type quota that the material cannot supply would force inventing a contrast the notes never draw — which fails audit under R17 anyway. The quota is a diversity target, not a licence to fabricate.
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
R23. R23 overrides R13: IF all candidates for a unit fail audit THEN generate a new round of candidates targeting inventory concepts not yet used, and re-audit each. IF every inventory concept has already been used THEN re-run R12c–R12g over the unit's notes to find concepts the first inventory missed.
R23a. IF 3 rounds of candidates for a unit have all failed audit THEN stop, show the user the failed candidates with their fail reasons and the unit's notes, and ask whether to (a) keep generating or (b) skip the unit. STOP until user responds.
     // Commentary: no near-miss option — a question not fully answerable from its Teach field produces frustration, not retention.
R23b. Do NOT declare a unit unquestionable without completing R23a.

// Output
R24. Save to `extracted/questions_<arg>.md` using the exact structure in the Output Format block below.
R24a. IF the questions file is saved AND the class root contains a `CLAUDE.md` with a `## Contents` section THEN add a one-line entry for `questions_<arg>.md` under its `**extracted/**` group. IF the section has no `**extracted/**` group THEN create the group header first. IF an entry for the file already exists THEN replace that line instead of duplicating.
R24b. IF the questions file is saved AND the class root contains a `CLAUDE.md` without a `## Contents` section THEN append a `## Contents` section (format: `**<dir>/**` bold group headers, one `- file — description` line per entry) and add the entry per R24a.
R24c. IF the class root contains no `CLAUDE.md` THEN skip R24a–R24b.
R24d. IF updating the Contents section THEN do not modify any other part of `CLAUDE.md`.
R24e. IF the chapter contains `constructive` exercises THEN write them to `extracted/practice_<arg>.md` with frontmatter `name: practice_<arg>`, `source: <notes filename>`, `generated: <today's date>`.
R24f. Each `practice_<arg>.md` entry records the exercise number and its text verbatim. Do NOT paraphrase and do NOT attempt an answer.
     // Commentary: these are hand-worked tasks — diagrams, specifications, designs. /learn cannot grade them. The file exists so they are not lost.
R24g. IF the chapter contains no constructive exercises THEN do NOT create `practice_<arg>.md`.
R25. After saving, report: (1) units processed, (2) questions saved, (3) candidates dropped and their fail reasons, (4) output file path, (5) whether `CLAUDE.md` Contents was updated, (6) images opened (count), (7) any candidate questions dropped because an image could not be opened or resolved (per R9e), (8) the concept inventory size per unit, (9) concepts excluded under R12e–R12f with the reason for each, (10) the core/supporting split per unit, (11) the analytical/constructive exercise split, (12) concepts promoted to `core` by an exercise, (13) inventory gaps found under R12r and whether each was fixable, (14) the Source Profile used and whether it was read from `CLAUDE.md` or newly detected, (15) any unit where an R15d–R15e question-type quota was waived under R15f, and which type the material could not supply.
     // Commentary: (14) matters because a wrong profile silently changes segmentation and generation mode. Naming it in the report is how a bad detection gets caught on the first run rather than the tenth.
     // Commentary: (8) and (9) make the question count auditable — the user can see whether a chapter got N questions because it holds N concepts or because the generator padded. (10) makes the study budget visible: only the core count has to fit the available time. (12) and (13) show what the exercise anchor earned its place doing.

// Catch-all
R26. IF any condition not covered by R0–R25 (including lettered sub-rules) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Output Format

```
---
name: questions_<arg>
source: <notes filename>
generated: <today's date>
---

## Unit 1 of N — <Unit Title>

#### Q1
Priority: core — <the Objective or Key Point statement this serves, per R12l>
Teach:
<only the note excerpt(s) needed to answer Q1 — no more>
Question: <question text>
Tests: <one-line description of the concept being tested>
Answer key: <the key idea(s) a correct answer must include — be specific>
Audit: PASS — <cite the exact phrase in the Teach field that contains the answer>

#### Q2
Priority: supporting
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

// Note: Priority, Tests and Audit are internal metadata. /learn displays only the Teach field (teach mode) and Question, and uses Answer key for grading. /learn reads Priority to filter (core-only mode) but never displays it.

## Usage

```
/generate_questions chapter2
/generate_questions wk10
```
