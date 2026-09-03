# generate_questions — BOOK run rules

Loaded under R0k2 when the argument does not normalize to a week. These rules GENERATE audited
questions from a textbook chapter and write them next to the chapter slice. The resulting file is
the POOL — a reference bank covering everything the chapter explains, not a study list.

Read this together with the shared core in `SKILL.md`. Rule IDs are global across both files.

## Rules — book run

// Source profile
R0.  Before loading notes, look for a `## Source Profile` section in the class root's `CLAUDE.md`.
R0a. IF a Source Profile exists THEN use it. Do NOT re-detect.
R0b. IF no Source Profile exists THEN detect the source's shape per R0c–R0e, write it to `CLAUDE.md` as a `## Source Profile` section, and report that it was created.
R0c. Chapter heading = the shallowest heading level whose text matches a chapter form (`# Chapter N`, `## N`, `# N`). A heading-like line is NOT a heading if it is a code comment — judge by whether it sits among code lines rather than prose.
R0c0. Detection under R0c is per-LINE, never per-level. Match every line at a level against the chapter forms and keep the matches. A heading level is NOT disqualified because other lines share its depth, however many of them there are.
R0c0a. Before recording `Chapter heading: none`, state the count of lines matching each chapter form. `none` is admissible ONLY when every form counts zero.
R0c0b. IF a level holds both chapter-form matches and non-matching lines THEN the level IS the chapter level and the non-matching lines are simply not chapters. Do NOT reach for a fallback pattern.
R0c1. A heading whose entire trimmed text matches `Page <N>` or `Slide <N>` — with or without a trailing `— <title>` — is a LOCATOR, not a heading. Exclude locators when determining the chapter level under R0c, the unit level under R0d, and the unit count under R7.
R0c2. Locators remain valid citation targets. R0c1 removes them from segmentation only — the prose under a locator is tested for inventory admissibility under R12d like any other text.
     // Commentary: this clause pointed at `R0q` until commit cc14901, which deleted the locator-admissibility rules and recycled that number for select-run pool matching. The deleted rule deferred to R12d, which is why R12d is the target. Do not reintroduce an admissibility test for class material — the current design has none.
R0d. Unit heading = the heading level one deeper than the chapter level. IF only one heading level exists THEN unit = chapter.
R0e. A Source Profile describes the NOTES source only — the textbook at `extracted/textbook/`. It says nothing about class material, which is reached through the registry under R0m and never needs detecting.
R0g. The user may correct a Source Profile by hand. R0a makes the correction permanent.
R0h. Detect the language of the notes content. Record `language: <code>` (e.g. `es`, `en`) in the Source Profile.
R0i. IF language = `en` THEN skip R16f–R16g. No `Teach_EN` or `Question_EN` fields are generated.

// Course scope
R0j. IF this is a BOOK run (R0l) AND `CLAUDE.md` holds a `### Course Scope` entry THEN read its `covers` and `not covered` chapter lists.
R0j2. IF the chapter being generated is listed as not covered THEN generate its questions normally and note it in the report.
R0j3. IF a `### Course Scope` entry carries no derivable chapter list — its `covers` field reads `NOT DETERMINED`, is empty, or names no chapter — THEN treat the class as having NO scope entry. Skip R0j–R0j2, generate normally. Do NOT stop under R26.

// File loading
R1.  IF the argument normalizes to a chapter number (R2a) AND the chapter slice `extracted/textbook/chapters/chapter<N>/chapter<N>.md` exists THEN use that file as the notes source.
R1a. IF the class uses a non-English chapter convention (e.g. `capitulo`) THEN R1 checks `extracted/textbook/chapters/capitulo<N>/capitulo<N>.md` instead.
R2.  IF the argument normalizes to a chapter number AND no chapter slice exists at the R1/R1a path THEN search the full textbook notes file (named in the Source Profile's `Notes file:`) for a chapter heading matching that number, and use the content under that heading as the notes source.
R2a. Normalization: `chapter<N>`, `ch<N>`, and `<N>` all match the chapter whose number is `<N>`. Matching is on the chapter NUMBER, not on the argument as a literal substring.
R2c. Exclude from the R2 search, and from the candidate list R4a shows the user, every file listed in `## Instructor Material`.
R3.  IF R2 finds a heading match THEN use the content under that heading as the notes source.
R4.  IF an argument is given AND neither R1 nor R2–R3 locates a source THEN list available chapter slices in `extracted/textbook/chapters/` and ask the user which to use. STOP until user responds.
R4a. IF no argument is given THEN list those same chapter slices, ask the user which to use, and STOP until user responds.

// Visual repair gate — scanned sources only
R4b. IF this is a BOOK run AND the Source Profile describes the source as scanned or names character-level OCR damage THEN check the chapter slice for a `<!-- visual-repair: done -->` marker on its first line.
R4b1. IF the marker is absent THEN visual-repair the chapter before proceeding: extract the page range from the slice's `## Page <N>` headings, render each page with `pdftoppm -f <p> -l <p> -r 170 -png <source PDF> <outprefix>`, read each image, compare against the corresponding text in the slice, and fix character-level OCR errors in place.
R4b2. Visual repair is TRANSCRIPTION from the image, never inference from context. IF a token cannot be read clearly THEN leave it as-is and flag it in the report.
R4b3. After repairing, prepend `<!-- visual-repair: done -->` as the first line of the chapter slice. This prevents re-repair on future runs.
R4b4. IF the chapter slice contains no `## Page <N>` headings THEN stop and tell the user to re-extract the textbook first — page anchors are required for visual repair. Do NOT proceed to generation.
R4b5. AFTER R4b3 stamps the marker, propagate the repair into the full textbook notes file named in the Source Profile's `Notes file:` — run `splice_chapter.py <slice> <notes file>` (next to this skill).
R4b5a. IF `splice_chapter.py` exits non-zero THEN stop and report its message. Do NOT generate questions while the slice and the notes file disagree.
R4b5b. Do NOT write the `<!-- visual-repair: done -->` marker into the notes file. The marker is per-slice bookkeeping; `splice_chapter.py` strips it.
R4b5c. Report the chapter spliced, the line range replaced, and the count of lines changed.
     // Commentary: repair reads the page images one at a time and is the most expensive step in this skill. Left in the slice alone it decays: the notes file keeps the damaged text, and R2 reaches for that file whenever a slice is missing — handing back the exact text the repair already paid to fix.
R4b6. IF the Source Profile does NOT describe the source as scanned or character-damaged THEN skip R4b–R4b5c entirely.

// Existing-file handling — book branch of R5
R5a1. IF this is a BOOK run THEN warn the user that the file already exists and ask whether to `regenerate` or `cancel`. STOP until user responds.
R5a2. IF a BOOK run regenerates a chapter file THEN say in the report that every select file copying from it is now stale, and name the command that fixes each: `/generate_questions week<N>` → `resync`.

// Unit segmentation
R7.  Count the headings matching the Source Profile's unit heading pattern inside the selected chapter. This count is N.
R8.  Each unit heading and its content until the next unit heading, or the end of the chapter, = one unit.
R8a. IF the Source Profile records `Unit heading: none` THEN the whole chapter is a single unit and N = 1.
R9.  Process units in order — document order on a book run, ascending chapter order on a select run.

// Figures (per unit)
R9a. A markdown image link — `![...](path)` — is NOT a question source. Do NOT open it, do NOT transcribe it, and do NOT build a Teach field from it. Treat the surrounding prose and the figure's caption as the only content.
R9b. IF a figure's caption carries content a question would test THEN use the CAPTION TEXT, which is prose in the notes like any other. This is not an exception to R9a.

// Teach content (per question)
R10. IF writing a question THEN write a `Teach:` field immediately before `Question:` carrying only the source content needed to answer this specific question — no more.
R10a. The Teach field is a RESTATEMENT of that content, not an excerpt of it. R11c–R11j require it to be re-broken into lists, anchors, and short sentences.
R10b. R18b and R18b1 are the limit on R10a. Restating, reordering, shortening, and formatting are the licence; adding a claim the source does not carry is not.
R11. IF a question's Teach field contains a formula THEN include a Legend block immediately after the formula listing every variable and its meaning.
R11a. IF a question's Teach field contains a formula THEN write the conceptual-path answer (the mechanism, without formula notation) in `Answer key`, and the formula-path answer (citing specific terms) in `Elaboration`. Either path alone is sufficient for a correct grade.
R11a1. R16a overrides R11a: the `Answer key` field carries the conceptual path ONLY.
R11b. IF a question's Teach field contains a formula THEN do NOT write the question in a way that mandates formula citation. The question must be answerable via conceptual explanation alone.

// Teach field formatting
R11c. IF the Teach field contains sequential steps THEN format them as a numbered list — one step per line.
R11c1. R11c applies only when each step is an action (a verb phrase). IF the ordered items are named concepts (nouns naming a phase, component, or mechanism) THEN R11f applies instead.
R11d. IF the Teach field enumerates parallel items (reasons, costs, conditions, features) with no strict order THEN format them as a bulleted list — one item per line.
R11e. All items within a list MUST use parallel grammatical structure.
R11f. IF the Teach field contrasts two or more named concepts THEN introduce each concept on its own line as: a colored diamond anchor, then a bold label, then its description.
R11f1. Assign each concept's anchor by its order in the contrast, cycling through: 🔹, 🔸, 🔶, 🔷.
R11f2. R11f overrides R11d: IF each item names a distinct concept, mechanism, protocol, or component THEN use diamond anchors (R11f), even if the items could also be read as parallel items. R11d bullets apply only when the items are NOT named concepts.
R11g. IF a Teach field covers two or more clearly distinct sub-concepts THEN separate them with a blank line.
R11h. Each sentence in a Teach field MUST express one idea only. Max 25 words per sentence.
R11i. Bold each key term the first time it appears in a Teach field.
R11j. No single list in a Teach field should exceed 7 items. IF a natural grouping exceeds 7 THEN split into labeled sub-groups with a bold label for each.

R12. The Teach field is sufficient IF AND ONLY IF the question is fully answerable from that Teach field alone, given that the user has already seen all prior questions' Teach fields within the same unit in order.
R12a. IF a concept required to answer this question was already covered in a prior question's Teach field within the same unit THEN the Teach field MAY omit re-explaining that concept.
R12b. R12 overrides R12a: IF omitting the prior context would make the Teach field insufficient to answer the question THEN include it anyway.

// Concept inventory (per unit)
R12c. Before generating any question for a unit, enumerate that unit's testable concepts. This list is the unit's concept inventory.
R12d. A concept belongs in the inventory IF AND ONLY IF the unit's notes contain at least one sentence explaining a mechanism, stating a contrast, or describing a scenario for that concept.
R12e. IF adding a concept to the inventory THEN record alongside it the exact sentence from the notes that satisfies R12d. IF no such sentence can be quoted THEN do NOT add the concept.
R12e1. The sentence recorded under R12e is quoted VERBATIM from the source, including its own wording and punctuation. Do NOT paraphrase it, do NOT correct its grammar, and do NOT merge two separated sentences into one quotation.
R12e2. IF an extraction has split the sentence that satisfies R12d — a figure, page header, or table interrupts it mid-sentence — THEN record the fragments joined by ` [...] `, each fragment verbatim.
     // Example: `"However, they use them selectively [...] and always try to discover solutions to problems even when there are no applicable theories and methods."`
R12f. Exclude from the inventory: bibliographic references, author names, tool and product names, chapter objective lists, further-reading sections, end-of-chapter exercises, and page headers.
R12f1. R12f excludes those passages from the CONCEPT INVENTORY only. It does NOT remove end-of-chapter exercises from R12h0's classification or from R12t's curated-question scan.
R12g1. R12g's same-idea test also applies ACROSS units within one run. IF a concept would produce a question with the same Answer key idea as a concept already questioned in an EARLIER unit of this run THEN exclude it and report it, naming the unit that already covers it.
     // Commentary: R12g itself is in SKILL.md, because select-run matching depends on it.
R12g3. R12g1 is scoped to one run over one source. It says nothing about a concept questioned in a different chapter file or in the week file for the same material.

// Exercise classification (per unit)
R12h0. IF the chapter contains an `Exercises` section THEN classify each numbered exercise as `analytical` or `constructive`. Book runs only — R0k3 suspends this on a select run.
R12h0a. An exercise is `analytical` IF it asks the reader to explain, discuss, describe, compare, suggest a reason, or give examples.
R12h0b. An exercise is `constructive` IF it asks the reader to produce an artifact — draw, design, develop, model, write, or rewrite.
R12h0c. IF an exercise contains both an analytical and a constructive clause THEN classify it `analytical`.
R12h0d. R12t overrides R12h0: IF a numbered exercise is interrogative AND its answer appears in the source body THEN it is a CURATED QUESTION and R12t decides its fate. R12h0 classifies only the exercises R12t did not adopt.
R12h0e. IF R12t declines to adopt a curated question because it maps to no inventory concept THEN R12r's inventory-gap handling applies to it exactly as to an unadopted analytical exercise.

// Inventory handling
R12m. The concept inventory is internal metadata. Do NOT write it to the output file. Each question records its own concept in the `Concept:` field per R13f and its own R12e sentence in the `Source quote:` field per R13g.

// Inventory gap check (per unit)
R12r. IF this is a BOOK run AND an `analytical` exercise asks about a topic that no inventory concept covers THEN record it as an inventory gap.
R12s. IF an inventory gap is recorded THEN attempt to admit the missing concept under R12d–R12e. IF no sentence in the chapter body explains it THEN leave it uncovered and report it.

// Curated question adoption (per unit)
R12t. After building the concept inventory, scan the unit's source for curated questions — any interrogative sentence whose answer appears in the same source. Match each to the inventory concept it tests.
R12t1. A curated question is ADOPTABLE if all three hold: (a) it maps to exactly one inventory concept, (b) the source contains enough content after the question to build a Teach field that makes it answerable (R12/R16), and (c) it passes R15.
R12t2. A curated question is NOT adoptable if any of these apply: it is a discussion prompt with no answer in the source; it is a skill checklist item; it is an ethical dilemma or open-ended question the author deliberately left unanswered; it is a process-step definition where the question IS the content; it duplicates a question already adopted for the same concept; or it fails R15 (definitional recall).
R12t3. For each adopted question: preserve the author's question wording in the `Question:` field. Build `Teach:`, `Answer key:`, `Elaboration:`, and `Audit:` from the source content per the same rules as generated questions (R10–R12b, R16a–R16e, R17). Record `Concept:` per R13f and `Source quote:` per R13g2.
R12t4. IF a curated question's wording is compound (two `?` marks, or two independent facts required) THEN split it into two entries per R15a–R15b, preserving the author's phrasing for each half.
R12t5. R12t5 overrides only R12t1(c), the definitional-recall clause of R12t2, and R15: adopt a curated definitional-recall question only when the first inventory-admissible explanatory occurrence (R12d–R12e) is this occurrence in document order. Bare mentions, objective lists, roadmaps, and headings do not introduce a concept. If an earlier explanatory occurrence exists in any prior unit or chapter, do NOT adopt it — R13 generates a question instead.
R12t6. IF multiple curated questions map to the same inventory concept THEN adopt the one that best satisfies R15 (mechanism > scenario > contrast > none). Discard the rest.
R12t7. Adopted questions go through the same audit (R17–R23a) as generated questions. An adopted question that fails audit is dropped and its concept becomes eligible for generation under R13.
R12t8. Adoption is per-unit: a curated question belongs to the unit whose text physically contains it, UNLESS it carries an explicit label naming the section, chapter, or slide it tests (`SECTION 1.1`, `Chapter 3 Review`) — then it belongs to the unit that label names.
R12t9. Curated questions are not confined to a unit's own prose. A textbook's end-of-chapter review questions, a handout's checkpoint questions, and a deck's in-line prompts are all in scope. Scan them wherever they physically sit in the source.
R12t11. IF a unit's scan finds no curated question at all THEN report that as an explicit zero. Do NOT omit the unit from the adoption report.

// Question generation (per unit)
R13. Generate exactly one candidate question per concept in the unit's concept inventory that has no adopted curated question from R12t. There is no fixed upper or lower bound on the number of questions per unit.
R13b. Order questions within each unit from most foundational concept to most complex, so later questions may safely rely on earlier ones having been seen.
R13c. R15b overrides R13: IF one inventory concept produces two natural sub-questions THEN that concept yields two entries.
R13d. IF a unit's concept inventory is empty THEN stop, show the user the unit's notes, and ask how to proceed. Do not improvise.
R13d1. R13d1 overrides R13d: IF a unit's inventory is empty ONLY because every concept it held was excluded under R12g1 as already covered by an earlier unit THEN this is a RESTATEMENT UNIT. Generate nothing for it, continue to the next unit, and report it naming the units its content repeats. Do NOT stop and do NOT ask.
R13d2. A restatement unit still appears in the output file with its heading and its "Unit N of M" numbering, carrying no questions and a one-line note that its content is covered by the units named.
R13e. Before saving, check each candidate question against the inventory. IF a question does not map to exactly one inventory concept THEN drop it.
R13f. Record each question's inventory concept in its `Concept:` field. This is the merge key R5k reads.
R13g. Record the R12e sentence for this question's concept in its `Source quote:` field, verbatim per R12e1–R12e2. This is the field R18b audits the Teach field against.
R13g1. IF a question's Teach field draws on two or more R12e sentences THEN `Source quote:` carries all of them, each verbatim, separated by a blank line.
R13g2. IF a question was adopted under R12t THEN `Source quote:` records the source sentence(s) its Teach field was built from, NOT the curated question's own wording.
R14. Each question MUST target exactly ONE concept from this unit's notes.
R14a. R15 overrides R14 for contrast questions: a question contrasting two concepts counts as targeting the one contrast, provided both concepts appear in this unit's notes.
R15. Each question MUST require the user to explain a mechanism, describe a scenario, or contrast two ideas. A question is prohibited if it can be answered by pattern-matching a single definition phrase.
     // PASSES: "Describe why non-persistent HTTP is expensive in terms of delay."
     // FAILS: "What does HTTP stand for?"
R15a. Each `Question:` field MUST contain exactly one question — one interrogative, one `?`. Compound questions are prohibited.
R15b. IF a concept produces two natural sub-questions THEN generate them as two separate entries in the same unit, each with its own Teach, Question, Answer key, and Audit.
R15d. IF a unit yields 3 or more PASS questions THEN the unit MUST include at least two different R15 question types (mechanism, scenario, contrast).
R15e. IF a unit yields 6 or more PASS questions THEN all three R15 question types MUST appear in that unit.
R15f. R13 and R14a override R15d–R15e: IF the unit's inventory cannot supply the missing type THEN it is not required. Report the shortfall instead.
R15g. A `Question:` field MUST name its subject. It MUST NOT point at its own `Teach:` field deictically — "this formula", "these two delays", "the expression above".
     // FAILS: "Why does this end-to-end expression leave out one of the four delay components entirely?"
     // PASSES: "The end-to-end delay formula adds only three of the four delay components. What assumption lets it drop the fourth?"
R15g1. R15g bars pointing OUTWARD at the Teach field. It does not bar a pronoun whose antecedent the Question itself supplies.
R15g2. R15g does NOT override R12a. A Question may still rely on a term defined in an EARLIER question's Teach field within the same unit; what it may not do is refer to its own.
R16. Each question MUST be fully answerable using only this question's Teach field, given that prior questions' Teach fields within the same unit have been shown in order.

// Answer key (per question)
R16a. The `Answer key` field MUST state the minimum sufficient answer: the single idea whose absence makes an answer wrong. One sentence, max 25 words.
     // FAILS: "A computational problem specifies the desired input/output relationship. An algorithm is a concrete, finite sequence of steps that produces that output. The problem defines the goal; the algorithm attains it." — three claims, 40 words.
     // PASSES: "The problem states what result is required; the algorithm is the sequence of steps that produces it."
R16b. IF a correct answer has supporting mechanism, example, or consequence beyond the minimal idea THEN write that material in an `Elaboration:` field placed immediately after `Answer key`. Do NOT write it into `Answer key`.
R16c. An answer that carries the `Answer key` idea is correct regardless of phrasing, length, or whether it reaches any part of the `Elaboration`.
R16d. IF the minimal idea cannot be stated in one sentence because the `Question` field demands two distinct facts THEN split the entry into two entries per R15b.
R16e. IF a question has no material beyond the minimal idea THEN omit the `Elaboration` field entirely. Do NOT pad it.

// Translation (per question — non-English sources only)
R16f. IF language ≠ `en` THEN for each question entry, write a `Teach_EN:` field containing an accurate English translation of the `Teach:` content. Preserve structure.
R16g. IF language ≠ `en` THEN for each question entry, write a `Question_EN:` field containing an accurate English translation of the `Question:` field.
R16h. Translations are reference aids, not study material. Translate for clarity, not style. Preserve technical terms that have no standard English equivalent.
R16i. IF language = `en` THEN do NOT write `Teach_EN` or `Question_EN` fields. R16i overrides R16f–R16g.

// Audit (per candidate question)
R17. Identify the specific sentence(s) in this question's Teach field that contain the answer. IF no such sentence exists THEN mark FAIL.
R17a. IF the Question field contains more than one `?` THEN mark FAIL with reason "compound question — split into two entries per R15a–R15b".
R18. IF the answer requires knowledge beyond those sentence(s) THEN mark FAIL.
R18a. IF a Teach field asserts content that appears in no sentence of the notes — a value read off a figure, a relationship inferred from a diagram — THEN mark FAIL with reason "content not in the notes — figures are not a source per R9a".
R18b. Compare the Teach field against this entry's `Source quote:`. IF the Teach field asserts anything the `Source quote:` does not support THEN mark FAIL with reason "Teach drifts from source — rewrite against the quote or drop".
     // FAILS: quote says "the bandwidth to the satellite is relatively narrow"; Teach says "the satellite link is too slow to carry per-minute readings, so the station compresses them". Compression appears nowhere in the source.
R18b1. Restating, reordering, shortening, and formatting the `Source quote:` are permitted. Adding a mechanism, a cause, a consequence, a number, or an example that the quote does not carry is not.
R18b2. R12a does NOT exempt a Teach field from R18b. IF a Teach field carries context from a prior question's concept THEN that context's own R12e sentence belongs in `Source quote:` per R13g1.
     // Commentary: R18b3 — the no-quote skip — is in SKILL.md, because the select-run verify cites it too.
R19. IF this question's Teach field states a fact without an explanation AND the question asks "why" about that fact THEN mark FAIL.
R20. IF an acronym or term appears in the question AND it is not defined in this question's Teach field AND it was not defined in a prior question's Teach field within the same unit THEN mark FAIL.
R20a. IF the `Answer key` field contains more than one independently droppable claim THEN mark FAIL with reason "over-specified answer key — move the surplus to Elaboration per R16b".
R20b. IF the `Question` field demands two distinct facts — even when it contains a single `?` — THEN mark FAIL with reason "compound requirement — split per R15b/R16d".
R20b1. A conjunction in the Question is NOT itself evidence of a compound requirement. Apply the interdependence test: IF either half, answered alone, would fully satisfy the question THEN it is compound and R20b fires. IF neither half alone satisfies it THEN the two halves state ONE relation and R20b does NOT fire.
     // FIRES (two independent facts): "¿qué ocurre con la oposición /y/ ~ /ll/ y cuál de los dos fonemas sobrevive?" — each half is a complete answer on its own.
R20c. IF the `Question` field points at its own `Teach` field deictically THEN mark FAIL with reason "question not self-contained — rewrite per R15g".
R21. IF a candidate question is not marked FAIL by R17–R20 — including all lettered sub-rules — THEN mark PASS.
R22. Drop all FAIL questions. Only PASS questions go into the output file.
R23. R23 overrides R13: IF all candidates for a unit fail audit, count that audited round and generate a new round for every inventory concept not yet represented by a PASS or adopted question; a failed candidate does not make its concept used, so it may be revised. Re-run R12c–R12g to discover additional concepts, but the absence of new concepts does not block retrying failed ones. After the third failed audited round, R23a applies.
R23a. IF 3 rounds of candidates for a unit have all failed audit THEN stop, show the user the failed candidates with their fail reasons and the unit's notes, and ask whether to (a) keep generating or (b) skip the unit. STOP until user responds.

// Constructive exercises
R24e. IF the chapter contains `constructive` exercises THEN write them next to the questions file (same directory as R24) with frontmatter `name: practice_<arg>`, `source: <notes filename>`, `generated: <today's date>`. A select run never writes this file.
R24f. Each `practice_<arg>.md` entry records the exercise number and its text verbatim. Do NOT paraphrase and do NOT attempt an answer.
R24g. IF the chapter contains no constructive exercises THEN do NOT create `practice_<arg>.md`.

## Output Format — book run

```
---
name: questions_<arg>
source: <notes filename>
generated: <today's date>
kind: book
---

## Unit 1 of N — <Unit Title>

#### Q1
Concept: <the inventory concept this question tests>
Source quote: <the R12e sentence(s), VERBATIM from the source>
Teach:
<only the source-grounded restatement(s) needed to answer Q1 — no more>
Teach_EN:                ← omit when language = en (R16i)
<English translation of the Teach field — preserves structure>
Question: <question text>
Question_EN: <English translation of the Question field>   ← omit when language = en
Tests: <one-line description of the concept being tested>
Answer key: <the single minimal idea whose absence makes an answer wrong — one sentence, max 25 words>
Elaboration: <mechanism, example, or consequence completing the answer; omit entirely if there is none>
Audit: PASS — <cite the exact phrase in the Teach field that contains the answer>

#### Q2
<same fields — Teach may omit concepts already covered in Q1's Teach per R12a>
<Elaboration omitted entirely when the minimal idea is the whole answer (R16e)>

## Unit 2 of N — <Unit Title>
<same entry structure>
```

## Notes

A book run reads the chapter slice at `extracted/textbook/chapters/chapter<N>/`. If no slice exists,
it falls back to segmenting the full textbook notes file. It generates questions, audits them, and
writes them next to the slice. This file is the POOL — a reference bank covering everything the
chapter explains, not a study list. Re-running warns before overwriting; there is no merge, since
textbook chapters don't change.
