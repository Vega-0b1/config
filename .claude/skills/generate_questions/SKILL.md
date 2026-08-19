---
name: generate_questions
description: Pre-generate and audit quiz questions from extracted notes for a chapter or topic. Saves questions alongside teaching content to extracted/questions_<arg>.md for use by /learn. Re-running on an existing file MERGES by default rather than starting over — it recomputes priority against any new instructor material and adds questions for concepts not yet covered, leaving already-audited entries and their numbering untouched. Also writes extracted/gaps_<arg>.md naming topics the professor taught that the textbook cannot answer.
---

Pre-generate audited questions for the specified chapter or topic and save them to `extracted/`.

## Rules

// Source profile
R0.  Before loading notes, look for a `## Source Profile` section in the class root's `CLAUDE.md`.
R0a. IF a Source Profile exists THEN use it. Do NOT re-detect.
R0b. IF no Source Profile exists THEN detect the source's shape per R0c–R0f, write it to `CLAUDE.md` as a `## Source Profile` section, and report that it was created.
R0c. Chapter heading = the shallowest heading level whose text matches a chapter form (`# Chapter N`, `## N`, `# N`). A heading-like line is NOT a heading if it is a code comment — judge by whether it sits among code lines rather than prose.
     // Commentary: a PDF extraction can turn `# !/usr/bin/python3` into what looks like a top-level heading. Counting those destroys the chapter map.
R0c1. A heading whose entire trimmed text matches `Page <N>` or `Slide <N>` — with or without a trailing `— <title>` — is a LOCATOR, not a heading. Exclude locators when determining the chapter level under R0c, the unit level under R0d, and the unit count under R7.
     // Commentary: /extract R11b and R14b emit these so a dump can be cited and grepped by position. Counting them as structure turns a 400-page PDF into 400 one-page units and a 42-slide deck into 42 units, and every one of those units would then demand its own questions.
R0c2. IF a file's only headings are locators THEN it has no chapter heading and no unit heading. Record `Unit heading: none` and let R8a treat the whole file as one unit.
R0c3. Locators remain valid citation targets. R0c1 removes them from segmentation only — R12o cites them by name.
R0c4. IF a Source Profile records `Chapter heading: none` AND its unit heading pattern is numbered `N.N` THEN the chapter of a unit is the leading `N` of its section number. R2 matches the requested chapter against that derived number, and R7's N = the count of units whose leading `N` equals it.
     // Commentary: `~/edu/cybersecurity` is this case. Its PDF extraction turned 141 shell and Python comments (`# !/usr/bin/python3`, `# Encryption`) into what parse as top-level headings, so there is no usable chapter level — but its 171 `## N.N` sections still carry the chapter number. Before this rule the profile recorded a state no rule handled: R7 said to count unit headings "inside the selected chapter" and R1–R2 had no chapter to select.
     // Example: `## 3.4 Message Authentication Codes` belongs to chapter 3. `/generate_questions chapter3` selects every `## 3.N` section.
R0c5. IF a Source Profile records `Chapter heading: none` AND its unit heading pattern carries no chapter number THEN the file has no chapter level at all. Do NOT derive one. R2 finds no match and R4 asks the user which file to use.
     // Commentary: R0c4 works because the section number encodes the chapter. With nothing encoding it, a derived chapter would be invented structure, and R4's existing prompt is the honest outcome.
R0c6. R0c4 does not repair the extraction. IF a profile records `Chapter heading: none` because its notes are damaged THEN say so in the R25 report every run, naming the re-extraction as the real fix.
     // Commentary: the derivation is a workaround that works well enough to keep a class usable, which is exactly why it would otherwise be forgotten.
R0d. Unit heading = the heading level one deeper than the chapter level. IF only one heading level exists THEN unit = chapter.
R0e. Anchor source = `instructor` IF `CLAUDE.md` holds an `## Instructor Material` section with at least one entry under `### Teaching`; ELSE `apparatus` IF an alias from R12i0 appears in at least 80% of chapters AND that section is enumerated per R0e1; ELSE `none`.
R0e0. R0e's `instructor` test reads the registry and nothing else. Do NOT infer instructor provenance from a file sitting in `source/`, from a filename, or from an extension.
     // Commentary: the registry records a y/n answer the user gave in /updateclass, which is the only place that fact exists. A deck in source/ that the user said was NOT instructor-provided must not promote anything — inferring from location would silently overrule them.
R0e1. An apparatus section is `enumerated` IF its content is a bulleted or numbered list of discrete claims. A running-prose recap is NOT enumerated, even when titled "Summary".
     // Commentary: presence of the heading is not enough. The anchor has to be a set of separable statements that concepts can be ranked against one at a time.
     // PASSES R0e1: Sommerville Key Points — "■ Software engineering is an engineering discipline that is concerned with all aspects of software production." Discrete and rankable.
     // FAILS R0e1:  Kurose chapter Summary — "In this chapter we've covered a tremendous amount of material! We've looked at the various pieces of hardware and software that make up the Internet..." It renarrates the whole chapter, so every concept matches it and it ranks nothing.
R0e2. R0e's order is deliberate: instructor material outranks textbook apparatus. IF a chapter has both THEN the apparatus stops promoting concepts for that chapter entirely.
     // Commentary: what the professor put in front of the class is what is testable. Taking the union instead would let a broad Key Point promote most of a chapter, and the core tier would stop discriminating — which is the whole reason to have a tier.
R0e3. `### Course Scope` entries do NOT satisfy R0e and never contribute to the anchor. They are read only by R0j–R0j3.
     // Commentary: a syllabus names a whole week's topic — "Week 6: Transport layer". Every concept in that chapter answers to it, so it ranks nothing, which is the same defect R0e1 rejects narrative summaries for. A class holding only a syllabus has no anchor and stays `capped`.
R0f. Generation mode = `tiered` IF anchor source is not `none`; ELSE `capped`.
R0f1. R0e and R0f record the CLASS-level default. The anchor that governs a given run is the EFFECTIVE anchor, resolved per chapter under R0f2.
R0f2. Effective anchor = `instructor` IF the registry maps at least one `### Teaching` entry to the chapter being generated; ELSE resolve it per R0f2a.
R0f2a. IF no `### Teaching` entry maps to the chapter being generated THEN re-run R0e's ladder with its `instructor` test SKIPPED: effective anchor = `apparatus` IF an alias from R12i0 appears in at least 80% of chapters AND that section is enumerated per R0e1; ELSE `none`.
     // Commentary: R0e raises the CLASS-level anchor to `instructor` the moment one `### Teaching` entry exists anywhere in the file. Falling back to that value handed an unregistered chapter the instructor anchor with no instructor file behind it — R12n found nothing to promote, R12q1 marked every concept `supporting`, and R13 generated one question per concept with no bound, because R13a's 2–5 cap only fires in `capped` mode. Skipping the instructor test is what makes R0f3's own example reachable and what keeps a textbook's apparatus usable for the chapters the professor has not reached yet.
R0f2b. R0f2a resolves the anchor for ONE chapter. It does not rewrite the class-level anchor recorded by R0e, and it does not change the Source Profile.
     // Commentary: the class-level value is still correct as a statement about the class — the registry does hold instructor material. R0f2a says only that this chapter cannot use it.
R0f3. Effective generation mode = `tiered` IF the effective anchor is not `none`; ELSE `capped`. Every rule below that tests generation mode tests the EFFECTIVE mode.
     // Commentary: a professor covers chapters 1–5 and skips 6–9. Chapter 1 tiers against its slides; chapter 8 falls back to its textbook apparatus, or to capped/untiered when the book has none — same class, same skill, no user intervention and no wrong answer in any of the three cases. A single class-level mode could only be right for one of them.
R0g. The user may correct a Source Profile by hand. R0a makes the correction permanent.
     // Commentary: detection is a heuristic and will sometimes be wrong. Persisting the result means a wrong guess is corrected once rather than re-made every run.
R0h. Detect the language of the notes content. Record `language: <code>` (e.g. `es`, `en`) in the Source Profile.
R0i. IF language = `en` THEN skip R16f–R16g. No `Teach_EN` or `Question_EN` fields are generated.

// Course scope
R0j. IF `CLAUDE.md` holds a `### Course Scope` entry THEN read its `covers` and `not covered` chapter lists.
R0j1. A `### Course Scope` entry NEVER promotes a concept to `core` and never participates in R12n–R12q1.
R0j2. IF the chapter being generated is listed as not covered THEN generate its questions normally and say in the R25 report that the course does not cover this chapter.
     // Commentary: out of scope is not out of bounds. The material is still in the book and still worth studying after the course ends — /learn reaches it with `+`. Refusing to generate would delete the option; reporting it sets the expectation.
R0j3. IF a `### Course Scope` entry carries no derivable chapter list — its `covers` field reads `NOT DETERMINED`, is empty, or names no chapter — THEN treat the class as having NO scope entry. Skip R0j–R0j2, generate normally, and say in the R25 report that a scope entry exists but determined nothing. Do NOT stop under R26.
     // Commentary: /updateclass R26d writes such an entry deliberately — a syllabus that defers its schedule to Canvas still records provenance worth keeping, and inventing a scope would be worse than recording none. `~/edu/software_engineering` holds exactly this entry. Before this rule its `covers: NOT DETERMINED` matched neither R0j's "read the lists" nor R0j2's "listed as not covered", so R26's catch-all fired and every run in that class stopped to ask about a state the chain itself had created.

// File loading
R1.  IF argument is given AND a file named `extracted/<arg>.md` exists THEN use that file as the notes source.
R2.  IF argument is given AND no file named `extracted/<arg>.md` exists THEN normalize the argument and search all `.md` files in `extracted/` — excluding `questions_*.md`, `practice_*.md`, and `gaps_*.md` files — for a chapter heading matching it under the Source Profile's chapter heading pattern.
R2a. Normalization: `chapter<N>`, `ch<N>`, and `<N>` all match the chapter whose number is `<N>`. Matching is on the chapter NUMBER, not on the argument as a literal substring.
     // Commentary: `chapter5` is not a substring of `## 5`. Before R2a this failed on every chapter and had to be bridged by hand.
R2b. IF the argument does not normalize to a chapter number THEN fall back to matching it as a case-insensitive substring of a heading.
     // Commentary: keeps non-chapter arguments such as `wk10` working.
     // Commentary: questions_*.md, practice_*.md, and gaps_*.md are this skill's own output; matching their headings would generate questions from questions.
R2c. Exclude from the R2 search, and from the candidate lists R4 and R4a show the user, every file listed in `## Instructor Material`.
     // Commentary: instructor extractions live in `extracted/` alongside the textbook notes, so R2 would happily select a slide deck as the notes source. R9i bars that material from supplying Teach content; without R2c the file-selection step routes around R9i before it ever runs, and the result is a chapter of questions whose answers are three-word bullets.
R3.  IF R2 finds a heading match THEN use the content under that heading as the notes source.
R4.  IF an argument is given AND neither R1 nor R2–R3 locates a source THEN list all `.md` files in `extracted/` — excluding `questions_*.md`, `practice_*.md`, and `gaps_*.md` — and ask the user which to use. STOP until user responds.
R4a. IF no argument is given THEN list those same files, ask the user which to use, and STOP until user responds. Do not proceed on an empty argument.
R4b. IF the source was chosen under R4 or R4a AND no argument was given THEN ask the user for the `<arg>` to name the output file, and STOP until user responds. Do not derive it.
     // Commentary: R24, R24a, and R24e all build filenames from `<arg>`. Picking a source without an `<arg>` leaves the output path undefined, and a guessed name is what /learn will fail to find later.
// Existing-file handling
R5.  IF `extracted/questions_<arg>.md` already exists THEN read its frontmatter, state the recommended operation per R5a, and ask the user to choose `merge`, `regenerate`, or `cancel`. STOP until user responds.
R5a. The recommended operation is `merge` unless the notes source has been re-extracted since the file's `generated:` date, in which case it is `regenerate`.
     // Commentary: merge is right whenever the textbook is unchanged, which is every week that only new instructor material arrived. Recommending it — rather than defaulting to the destructive path as the old "Overwrite?" prompt did — is what keeps a weekly registry update from rewriting 32 audited questions.
R5b. IF the user chooses `merge` THEN proceed under R5f–R5m. IF `regenerate` THEN discard the existing file and proceed to R7 as a first generation. IF `cancel` THEN stop execution.
R5c. IF `extracted/questions_<arg>.md` does not exist THEN proceed to R7 as a first generation. Do NOT prompt.

// Recorded state
R5d. Read `mode:` and `anchor:` from the existing file's frontmatter. These record how it was generated.
R5e. IF the frontmatter carries no `mode:` or no `anchor:` THEN treat the file as `mode: capped`, `anchor: none`.
     // Commentary: correct for every file generated before this field existed — those runs had no anchor to rank against, which is exactly what capped/none records.

// Merge operation selection
R5f. Under a merge, compare the file's recorded state (R5d–R5e) against the EFFECTIVE state for this run (R0f2–R0f3), and compare the current concept inventory against the concepts the file already questions.
R5g. IF the effective mode equals the recorded mode AND the inventory yields no concept the file lacks THEN the operation is RE-TIER. Apply R5h only.
R5h. RE-TIER: recompute the `Priority:` field of every existing entry against the current registry, per R12h–R12q1. Leave every other field of every entry byte-identical — Teach, Teach_EN, Question, Question_EN, Tests, Concept, Answer key, Elaboration, and Audit.
R5h1. A re-tier MUST NOT re-run the audit (R17–R23b), MUST NOT rewrite question text, and MUST NOT touch `extracted/flagged_questions_<arg>.md`.
     // Commentary: R9i makes this safe rather than merely convenient. Questions derive only from the notes source; instructor material only assigns priority. New slides therefore cannot change which questions exist, only which are core — so re-auditing could not discover anything, and rewriting would churn text the user has already studied.
R5i. IF the effective mode differs from the recorded mode, OR the inventory yields at least one concept the file lacks, THEN the operation is EXTEND. Apply R5j–R5m, then R5h.
R5j. EXTEND: build the unit's concept inventory per R12c–R12g, then subtract the concepts the file already questions. Generate candidates for the remainder only, and audit those candidates per R17–R23b.
R5k. Match an existing entry to a concept by its `Concept:` field. IF an entry has no `Concept:` field THEN match on its `Tests:` field instead.
     // Commentary: R13e already guarantees one question maps to exactly one inventory concept, but no field recorded which until now. `Tests:` is a one-line description of the concept under test, which is close enough to carry the four legacy files through their first merge; every entry written after this rule carries `Concept:` and matches exactly.
R5k1. IF R5k's field match does not connect a candidate concept to an existing entry THEN test that concept against every existing entry's `Answer key` using R12g's same-idea test. IF an existing Answer key already carries the idea THEN treat the concept as covered and generate nothing for it.
     // Commentary: questions files get hand-edited. `~/edu/network` chapter 1 Unit 1 Q3 was replaced by hand with a socket-interface question, and its `Tests:` prose resembles no phrasing this skill would generate — so a field match alone misses it and extend appends a second question on the same concept. R12g already defines "same idea" for comparing two inventory concepts; R5k1 applies that same test across the merge boundary.
R5k2. R5k1 governs whether a concept is COVERED, not whether an existing entry is correct. Do NOT rewrite or replace an entry that R5k1 matched.
     // Commentary: a hand-edited question is the user's deliberate correction of something this skill produced. Treating a match as license to regenerate it would undo that edit silently — which is exactly the failure R5h exists to prevent.
R5k3. Before generating a candidate under R5j, read `extracted/flagged_questions_<arg>.md` if it exists. IF a concept's question was previously removed or replaced there — a flag whose `Status:` field records it as upheld — THEN treat that concept as DELIBERATELY REMOVED. Generate nothing for it and report it under R25.
     // Commentary: found on the first real extend. `~/edu/network` chapter 1 Q3 tested the router vs link-layer-switch contrast; the user flagged it as answerable by repeating the notes verbatim, the flag was upheld, and it was replaced by hand with a socket-interface question. The concept is still in §1.1 and still passes R12d, so a rebuilt inventory readmits it and extend re-adds the exact question the user rejected. The flag file is the only record that the removal was deliberate.
R5k3a. IF a flag's `Status:` field reads `OPEN` THEN it is NOT deliberately removed. The concept is eligible for generation under R5j exactly as an unflagged concept is.
     // Commentary: /learn R23b writes `OPEN` at flag time because nothing has been decided yet — the user has said only that something is wrong with the question. Treating an open flag as a removal would delete a concept on the strength of a complaint nobody has adjudicated.
R5k3b. IF a flag entry carries no `Status:` field at all THEN treat it as `OPEN` under R5k3a, and name it in the R25 report as an unadjudicated flag.
     // Commentary: backward compatibility for flags written before /learn R23b existed. Defaulting to removal would silently drop every concept the user ever flagged, including the ones they flagged and then decided were fine.
R5k3c. Do NOT write to `extracted/flagged_questions_<arg>.md`. R5k3–R5k3b read it only; R5h1 already bars a re-tier from touching it, and an extend has no more licence than a re-tier does.
     // Commentary: adjudicating a flag is the user's call. This skill reporting an unadjudicated flag under R5k3b is the prompt for that call, not a substitute for it.
R5k4. IF the user has since added instructor material that presents a deliberately-removed concept THEN it stays removed. Do NOT treat a new `### Teaching` entry as grounds to reinstate it.
     // Commentary: the flag was about the question being shallow, not about the topic being unimportant. A slide covering the same topic does not repair the defect the user objected to, and R12o will still cite that slide for whatever other concepts it presents.
R5l. Append new entries at the END of their unit. Existing entry numbers MUST NOT change.
R5l1. R5l overrides R13b for extended entries: the foundational-to-complex ordering applies within a generation, not across a merge.
     // Commentary: /learn R23 writes question numbers into `flagged_questions_<arg>.md`. Renumbering to restore R13b's ordering would invalidate every reference in that file, which is a worse outcome than a late entry that happens to be foundational.
R5m. IF an existing entry maps to no concept in the current inventory THEN keep it, and report it under R25. Do NOT delete it.
     // Commentary: an audited question that survived R17–R21 is not garbage merely because a rebuilt inventory phrased its concept differently. Deleting on an inventory mismatch would silently shrink a file the user has been studying.

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

// Instructor material (per chapter) — read before the inventory; R12n reads its output
R9f. IF the effective anchor is `instructor` THEN read every `### Teaching` file the registry maps to the chapter being generated, before building any unit's concept inventory. Resolve each path relative to the class root. Do NOT read `### Course Scope` files here.
R9g. IF a registered path is a code file or an image THEN open it with the Read tool. Its content counts as instructor coverage under R12n exactly as an extracted markdown file does.
     // Commentary: /updateclass R21 registers code and images by path rather than extracting them, because converting a diagram or a socket demo to markdown only loses fidelity. Reading them here is what makes that decision work.
R9h. IF a registered file cannot be opened or its path cannot be resolved THEN do NOT treat its absence as evidence that a concept is uncovered. Assign priority from the registered files that did open, and report the unreadable file under R25.
     // Commentary: a stale path would otherwise demote a chapter's entire core tier to supporting, producing a short and confidently wrong study list with no signal that anything went missing.
R9i. Instructor material is read to ASSIGN PRIORITY. It is not a source of questions and not a source of Teach content.
     // Commentary: questions come from the notes source selected under R1–R4; R17 audits every answer against a Teach field drawn from it. A slide's three-word bullet cannot support a question that survives that audit, and treating it as note content would produce exactly the unanswerable questions R23a exists to catch.

// Teach content (per question)
R10. IF writing a question THEN write a `Teach:` field immediately before `Question:` containing only the note excerpt(s) needed to answer this specific question — no more.
R11. IF a question's Teach field contains a formula THEN include a Legend block immediately after the formula listing every variable and its meaning.
R11a. IF a question's Teach field contains a formula THEN write the conceptual-path answer (the mechanism, without formula notation) in `Answer key`, and the formula-path answer (citing specific terms) in `Elaboration`. Either path alone is sufficient for a correct grade.
R11a1. R16a overrides R11a: the `Answer key` field carries the conceptual path ONLY. Do NOT pack both paths into it.
     // Commentary: before R16a this rule required both paths in one field, which is exactly the over-specification R16a exists to stop. The two paths are still both recorded — they now live in two fields.
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
R12h1. R12h1 overrides R12h: IF the effective generation mode = `capped` THEN skip R12h–R12q1 and R12r–R12s entirely and emit `Priority: untiered` on every entry.
R12h2. R12h1 does NOT skip R12h0–R12h0c. Exercise classification runs in every generation mode.
     // Commentary: R24e writes constructive exercises to practice_<arg>.md regardless of mode. Folding classification into the skipped range would silently drop that file for every capped class.
R12h2a. R12h1 does NOT skip R12m either. The inventory stays internal in every generation mode.
     // Commentary: R12m sits inside the R12h–R12q1 span by number but is not a priority-assignment rule — it says where the inventory may and may not be written. Letting the capped skip swallow it would permit a capped run to dump its concept inventory into the questions file, which no mode should ever do.
     // Commentary: `untiered` is not `supporting`. It records that this class's textbook offers no anchor to rank against, so /learn can say so precisely instead of advising a regeneration that would not help.
R12h3. IF the effective anchor is `instructor` THEN assign priority under R12n–R12q1. R12i0–R12l do NOT apply, including R12i2's per-statement cap.
     // Commentary: R12i ranks concepts against the author's own statements; R12n ranks them against the professor's teaching. Running both would produce the union R0e2 rejects. R12i2's cap in particular has no denominator here — a slide is a locator, not a claim that nine concepts can be over-matched against.
R12h4. IF the effective anchor is `apparatus` THEN assign priority under R12i0–R12l. R12n–R12q1 do NOT apply.
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
R12k. IF the effective anchor is `apparatus` AND a concept is not `core` under R12i–R12j THEN it is `supporting`.
R12l. IF assigning `core` THEN record alongside the concept the Objective or Key Point statement it serves.
     // Commentary: R12i is a lookup against the author's own statements, not a judgment about importance. Naming the statement is what makes the assignment checkable after the fact.
R12m. The concept inventory is internal metadata. Do NOT write it to the output file. The priority assigned under R12h–R12q1 and the statement or locator recorded under R12l or R12o ARE written to the output file, in the `Priority:` field defined in the Output Format block.
     // Commentary: R12m closes the whole priority block and forward-references R12n–R12q1 below it, the same way R0f1 forward-references R0f2.

// Priority assignment — instructor anchor (per inventory concept)
R12n. IF the effective anchor is `instructor` THEN a concept is `core` IF AND ONLY IF a `### Teaching` file registered for this chapter presents it.
R12n1. A locator that only ENUMERATES topics does not present them. A slide or page whose content is a roadmap, agenda, outline, table of contents, or chapter-objective list is scope, not teaching, and promotes nothing.
     // Commentary: found on the first real run. `lec1_intro_computer_networks_notes.md` slide 3 is a roadmap reading "1.4 delay, loss, throughput in networks / 1.5 protocol layers / 1.6 security / 1.7 history" — the deck then teaches none of them. Counting it as presence would promote four entire units to `core` on the strength of a table of contents, which is precisely the defect R0e3 rejects a syllabus for. The test is whether the locator SAYS something about the concept, not whether it names it.
     // FAILS R12n1 (enumeration): `## Slide 3 — Chapter 1: roadmap` listing "1.4 delay, loss, throughput in networks".
     // PASSES R12n1 (presentation): `## Slide 8 — Two key network-core functions` stating "forwarding: move packets from router's input to appropriate router output".
R12o. IF assigning `core` under R12n THEN record alongside the concept the exact locator that presents it — the `## Slide <N>` heading, the `## Page <N>` heading, or the code file and line. IF no locator can be cited THEN the concept is `supporting`.
     // Commentary: the same quotable-evidence discipline R12e imposes on inventory admission. Naming the slide is what makes the tier checkable after the fact rather than a judgment about importance, and it is what R25 (18) reports.
R12p. Depth of treatment is not the test under R12n. Presence is. A concept the instructor material states in three words is `core` even when the textbook spends three pages on it.
R12p1. R12n1 overrides R12p. Three words that TEACH are presence; three words that merely LIST are not.
     // Commentary: R12p exists so a terse deck still anchors the tier. R12n1 keeps that from collapsing into "any occurrence of the word counts", which would make the anchor unfalsifiable.
     // Commentary: a slide reading only "Nagle's algorithm" still means the professor put it in front of the class. Requiring the slide to match the textbook's depth would make the anchor unreachable for exactly the terse decks it is meant to read.
R12q. IF the registry maps more than one file to this chapter THEN a concept presented by ANY of them is `core`.
R12q1. IF the effective anchor is `instructor` AND a concept is not `core` under R12n–R12q THEN it is `supporting`.

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
R13f. Record each question's inventory concept in its `Concept:` field. This is the merge key R5k reads.
     // Commentary: R13e has always required the one-question-one-concept mapping; nothing wrote it down, so a later run had to re-derive it from prose. Recording it makes a merge exact instead of approximate.
R14. Each question MUST target exactly ONE concept from this unit's notes.
R14a. R15 overrides R14 for contrast questions: a question contrasting two concepts counts as targeting the one contrast, provided both concepts appear in this unit's notes.
     // Commentary: contrasting two ideas forces deeper processing than recalling one — contrast questions serve retention and must not be blocked by R14.
R15. Each question MUST require the user to explain a mechanism, describe a scenario, or contrast two ideas.
     A question is prohibited if it can be answered by pattern-matching a single definition phrase.
     // Mental test: "Does answering this correctly prove the user understands how it works — not just that they remember its name?"
     // PASSES R15: "Describe why non-persistent HTTP is expensive in terms of delay."
     // FAILS R15: "What does HTTP stand for?"
R15a. Each `Question:` field MUST contain exactly one question — one interrogative, one `?`. Compound questions are prohibited.
R15a1. R15a states two independent conditions. The `?` count is enforced by R17a; the single-interrogative condition is enforced by R20b. A question may satisfy one and still fail R15a on the other.
     // Commentary: until R20b existed, only the `?` count was audited, so a question carrying one `?` and two interrogative pronouns passed. That is how "¿qué ocurre con la oposición /y/ ~ /ll/ y cuál de los dos fonemas sobrevive?" reached a saved questions file — the rule prohibited it, but nothing checked for it.
     // FAILS the one-interrogative condition — one `?`, two required facts, caught by R20b: "What distinguishes the network layer from the transport layer? Explain what this means for an application sending data."
     // FAILS the one-`?` condition — caught by R17a: "What is a dígrafo? Why is ch no longer part of the abecedario?"
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

// Answer key (per question)
R16a. The `Answer key` field MUST state the minimum sufficient answer: the single idea whose absence makes an answer wrong. One sentence, max 25 words.
     // Commentary: the field is a grading threshold, not a model answer. The 25-word cap is the same one R11h sets for Teach sentences, reused rather than reinvented.
     // FAILS R16a: "A computational problem specifies the desired input/output relationship. An algorithm is a concrete, finite sequence of steps that produces that output. The problem defines the goal; the algorithm attains it." — three claims, 40 words.
     // PASSES R16a: "The problem states what result is required; the algorithm is the sequence of steps that produces it."
R16b. IF a correct answer has supporting mechanism, example, or consequence beyond the minimal idea THEN write that material in an `Elaboration:` field placed immediately after `Answer key`. Do NOT write it into `Answer key`.
R16c. An answer that carries the `Answer key` idea is correct regardless of phrasing, length, or whether it reaches any part of the `Elaboration`.
     // Commentary: this is R11a's "either path alone is sufficient" clause generalized out of the formula-only case it was trapped in.
R16d. IF the minimal idea cannot be stated in one sentence because the `Question` field demands two distinct facts THEN split the entry into two entries per R15b.
     // Commentary: R15a's one-`?` test is syntactic and lets "¿qué ocurre con X y cuál sobrevive?" through — one question mark, two required answers. R16d is the semantic test.
R16e. IF a question has no material beyond the minimal idea THEN omit the `Elaboration` field entirely. Do NOT pad it.

// Translation (per question — non-English sources only)
R16f. IF language ≠ `en` THEN for each question entry, write a `Teach_EN:` field containing an accurate English translation of the `Teach:` content. Preserve structure (numbered lists, bulleted lists, bold terms, diamond anchors, legends).
R16g. IF language ≠ `en` THEN for each question entry, write a `Question_EN:` field containing an accurate English translation of the `Question:` field.
R16h. Translations are reference aids, not study material. Translate for clarity, not style. Preserve technical terms that have no standard English equivalent.
R16i. IF language = `en` THEN do NOT write `Teach_EN` or `Question_EN` fields. R16i overrides R16f–R16g.

// Audit (per candidate question)
R17. Identify the specific sentence(s) in this question's Teach field that contain the answer. IF no such sentence exists THEN mark FAIL.
R17a. IF the Question field contains more than one `?` THEN mark FAIL with reason "compound question — split into two entries per R15a–R15b".
     // Commentary: R17a is the syntactic fast path and covers ONLY the `?` count. A compound question carrying a single `?` is out of its scope — R20b catches that one. Do not read a PASS here as evidence the question is not compound.
     // FAILS R17a (two `?`): "What is a dígrafo? Why is ch no longer part of the abecedario?"
R18. IF the answer requires knowledge beyond those sentence(s) THEN mark FAIL.
R18a. IF a Teach field transcribes content from an image THEN the cited answer sentence(s) must faithfully match the opened image's actual content. IF the transcription was not verified against the opened image THEN mark FAIL.
R19. IF this question's Teach field states a fact without an explanation AND the question asks "why" about that fact THEN mark FAIL.
R20. IF an acronym or term appears in the question AND it is not defined in this question's Teach field AND it was not defined in a prior question's Teach field within the same unit THEN mark FAIL.
R20a. IF the `Answer key` field contains more than one independently droppable claim THEN mark FAIL with reason "over-specified answer key — move the surplus to Elaboration per R16b".
     // Test: delete a clause. IF the remaining text still fully answers the Question as asked THEN that clause was droppable and belongs in Elaboration.
R20b. IF the `Question` field demands two distinct facts — even when it contains a single `?` — THEN mark FAIL with reason "compound requirement — split per R15b/R16d".
     // Commentary: R17a is the syntactic check (count the question marks); R20b is the semantic one. A question joined by "and" or "y" passes R17a and fails here. R20b is what gives R15a's single-interrogative condition an enforcement mechanism.
     // Test: count the facts the Answer key must carry to satisfy the question as asked. IF that count exceeds one, the question is compound regardless of its punctuation.
     // FAILS R20b (one `?`, two required facts): "En el habla yeísta, ¿qué ocurre con la oposición /y/ ~ /ll/ y cuál de los dos fonemas es el que sobrevive?" — demands both what happens AND which survives.
     // PASSES R20b: "En el habla yeísta, ¿cuál de los dos fonemas sobrevive?" — one required fact.
R20b1. A conjunction in the Question is NOT itself evidence of a compound requirement. Apply the interdependence test: IF either half, answered alone, would fully satisfy the question THEN it is compound and R20b fires. IF neither half alone satisfies it THEN the two halves state ONE relation and R20b does NOT fire.
     // Commentary: R15/R14a/R15d–R15e all push toward contrast questions, and a contrast question necessarily names two values. Firing R20b on that would split questions the ruleset elsewhere requires. The test is interdependence, not the presence of "y" or "and".
     // DOES NOT fire (one relation, halves interdependent): "¿En qué se diferencian el seseo y el ceceo?" — naming only the seseo half answers nothing.
     // FIRES (two independent facts): "¿qué ocurre con la oposición /y/ ~ /ll/ y cuál de los dos fonemas sobrevive?" — "la oposición se neutraliza" is a complete answer on its own, and so is "/y/".
     // DOES NOT fire (conjunction joins coordinated examples, not questions): "¿Por qué la elección entre *b* y *v* no puede resolverse escuchando la palabra?"
R21. IF a candidate question is not marked FAIL by R17–R20 — including all lettered sub-rules — THEN mark PASS.
R22. Drop all FAIL questions. Only PASS questions go into the output file.
R23. R23 overrides R13: IF all candidates for a unit fail audit THEN generate a new round of candidates targeting inventory concepts not yet used, and re-audit each. IF every inventory concept has already been used THEN re-run R12c–R12g over the unit's notes to find concepts the first inventory missed.
R23a. IF 3 rounds of candidates for a unit have all failed audit THEN stop, show the user the failed candidates with their fail reasons and the unit's notes, and ask whether to (a) keep generating or (b) skip the unit. STOP until user responds.
     // Commentary: no near-miss option — a question not fully answerable from its Teach field produces frustration, not retention.
R23b. Do NOT declare a unit unquestionable without completing R23a.

// Output
R24. Save to `extracted/questions_<arg>.md` using the exact structure in the Output Format block below.
R24a. IF the questions file is saved AND the class root contains a `CLAUDE.md` with a `## Contents` section THEN add a one-line entry for `questions_<arg>.md` under its `**extracted/**` group. IF the section has no `**extracted/**` group THEN create the group header first. IF an entry for the file already exists THEN replace that line instead of duplicating.
R24a1. R24a applies identically to every other file this skill writes: `gaps_<arg>.md` (R24l) and `practice_<arg>.md` (R24e). Each gets its own Contents entry under the same `**extracted/**` group, on the run that creates it.
     // Commentary: /updateclass R5 uses Contents as its seen-set. A file this skill writes but never inventories reads as NEW on the next /updateclass run, which then asks the user "instructor-provided?" about the chain's own output. R7 of that skill now also excludes these by name, so the two rules cover each other — but the inventory is the one that should have been right first.
R24a2. IF a file this skill would have written was NOT created on this run — no coverage gaps (R24n), no constructive exercises (R24g) — THEN write no Contents entry for it. Do NOT inventory a file that does not exist.
R24b. IF the questions file is saved AND the class root contains a `CLAUDE.md` without a `## Contents` section THEN append a `## Contents` section (format: `**<dir>/**` bold group headers, one `- file — description` line per entry) and add the entry per R24a.
R24c. IF the class root contains no `CLAUDE.md` THEN skip R24a–R24b.
R24d. IF updating the Contents section THEN do not modify any other part of `CLAUDE.md`.

// Constructive exercises
R24e. IF the chapter contains `constructive` exercises THEN write them to `extracted/practice_<arg>.md` with frontmatter `name: practice_<arg>`, `source: <notes filename>`, `generated: <today's date>`.
R24f. Each `practice_<arg>.md` entry records the exercise number and its text verbatim. Do NOT paraphrase and do NOT attempt an answer.
     // Commentary: these are hand-worked tasks — diagrams, specifications, designs. /learn cannot grade them. The file exists so they are not lost.
R24g. IF the chapter contains no constructive exercises THEN do NOT create `practice_<arg>.md`.

// Frontmatter and per-entry metadata
R24h. IF saving THEN write this run's effective mode (R0f3) and effective anchor (R0f2) into the frontmatter `mode:` and `anchor:` fields.
     // Commentary: R5d reads these to choose between re-tier and extend. A file that does not record them forces R5e's capped/none assumption, and the merge cannot tell a deliberate capped run from a legacy one.
R24i. IF saving an entry THEN write its `Concept:` field per R13f.

// Coverage gaps — instructor topics the notes cannot answer
R24j. IF the effective anchor is `instructor` THEN, for every concept a `### Teaching` file presents, check whether any sentence in the notes source explains it per R12d.
R24k. IF no such sentence exists THEN record the concept as a COVERAGE GAP. Do NOT admit it to the inventory and do NOT generate a question for it.
     // Commentary: R9i bars instructor material from supplying Teach content, so a question for such a concept has no answer sentence to cite and R17 would fail it. The gap is real information, not an error — it means this topic needs a source the class does not have.
R24l. IF at least one coverage gap was recorded THEN write `extracted/gaps_<arg>.md` with frontmatter `name: gaps_<arg>`, `source: <notes filename>`, `generated: <today's date>`.
R24m. Each gap entry records the concept, the locator that taught it (`## Slide <N>` / `## Page <N>` / code file and line, per R12o), and the Teaching file it came from. Do NOT attempt an answer and do NOT paraphrase the textbook at it.
     // Commentary: writing a plausible-sounding answer from model knowledge is the one thing that would make this file dangerous — it would read exactly like the audited material next to it while resting on nothing. The file's job is to name what is missing.
R24n. IF no coverage gaps were recorded THEN do NOT create `gaps_<arg>.md`.
R24o. A merge rewrites `gaps_<arg>.md` in full from the current Teaching files. R5h1's byte-identical guarantee covers `questions_<arg>.md` only.
     // Commentary: gaps are derived entirely from material that just changed, so a stale gap entry would name a topic a newly-added deck has since covered.

// Report
R25. After saving, report: (1) units processed, (2) questions saved, (3) candidates dropped and their fail reasons, (4) output file path, (5) whether `CLAUDE.md` Contents was updated, (6) images opened (count), (7) any candidate questions dropped because an image could not be opened or resolved (per R9e), (8) the concept inventory size per unit, (9) concepts excluded under R12e–R12f with the reason for each, (10) the core/supporting split per unit, (11) the analytical/constructive exercise split, (12) concepts promoted to `core` by an exercise, (13) inventory gaps found under R12r and whether each was fixable, (14) the Source Profile used and whether it was read from `CLAUDE.md` or newly detected, (15) any unit where an R15d–R15e question-type quota was waived under R15f, and which type the material could not supply, (16) language detected and whether `Teach_EN`/`Question_EN` translations were generated, (17) the EFFECTIVE anchor and generation mode for this chapter, and whether it came from the registry (R0f2) or from the instructor-skipped fallback (R0f2a), (18) every instructor file consulted, with the locator count each contributed to `core` assignments, (19) any registered instructor file that could not be opened (per R9h), (20) IF the effective anchor is `instructor` AND the class-level anchor is `apparatus` THEN say so explicitly and name what the apparatus would have promoted but did not, (21) the operation chosen under R5g/R5i — first generation, re-tier, extend, or regenerate — and what selected it, (22) on a re-tier, how many `Priority` fields changed and in which direction, (23) on an extend, how many entries were added per unit and how many existing entries were left untouched, (24) any existing entry kept under R5m because it matched no current inventory concept, (25) coverage gaps written to `gaps_<arg>.md` (per R24l), naming each concept and its locator, (26) every concept skipped as DELIBERATELY REMOVED under R5k3, naming the flag it came from, (27) every unadjudicated flag found under R5k3b — a flag whose `Status:` is `OPEN` or absent — so the user can resolve it before the next merge.
     // Commentary: (22) and (23) are the numbers that make a merge auditable. "Re-tiered, 7 questions moved supporting→core, 0 rewritten" is checkable; "done" is not, and a merge that silently rewrote everything would look identical to one that did not.
     // Commentary: (17) and (20) are how a per-chapter anchor split stays visible. A class where chapters 1–5 tier against slides and 6–9 fall back to untiered is correct behavior, but silently correct behavior looks identical to a bug — the report is what distinguishes them.
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
mode: tiered | capped          ← the EFFECTIVE mode this run used (R0f3)
anchor: instructor | apparatus | none   ← the EFFECTIVE anchor this run used (R0f2)
---

## Unit 1 of N — <Unit Title>

#### Q1
Concept: <the inventory concept this question tests — the merge key, per R5k>
Priority: core — <under the apparatus anchor, the Objective or Key Point statement this serves (R12l); under the instructor anchor, the locator that presents it (R12o), e.g. `lec1_intro_computer_networks_notes.md ## Slide 14 — Internet structure: network of networks`>
Teach:
<only the note excerpt(s) needed to answer Q1 — no more>
Teach_EN:                ← omit when language = en (R16i)
<English translation of the Teach field — preserves structure>
Question: <question text>
Question_EN: <English translation of the Question field>   ← omit when language = en
Tests: <one-line description of the concept being tested>
Answer key: <the single minimal idea whose absence makes an answer wrong — one sentence, max 25 words>
Elaboration: <mechanism, example, or consequence completing the answer — NOT required for a correct grade; omit the field entirely if there is none>
Audit: PASS — <cite the exact phrase in the Teach field that contains the answer>

#### Q2
Concept: <this question's inventory concept>
Priority: supporting
Teach:
<excerpt for Q2 — may omit concepts already covered in Q1's Teach per R12a>
Teach_EN:                ← omit when language = en
...
Question: <question text>
Question_EN: ...         ← omit when language = en
Tests: ...
Answer key: ...
Elaboration: ...        ← omit this line when the minimal idea is the whole answer (R16e)
Audit: PASS — ...

## Unit 2 of N — <Unit Title>

#### Q1
Teach:
...
```

// Note: Concept, Priority, Tests and Audit are internal metadata. /learn displays only the Teach field (teach mode) and Question, and grades on Answer key alone. /learn reads Priority to filter (core-only mode) but never displays it. Concept exists solely as the merge key R5k matches on. Elaboration is never shown before the user answers — /learn displays it only alongside Answer key after a wrong answer or a skip. Teach_EN and Question_EN are never displayed by /learn when it delivers a question — it prints them only when the user types `en` on that question.

## Usage

```
/generate_questions chapter2
/generate_questions wk10
```
