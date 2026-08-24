---
name: generate_questions
description: Pre-generate and audit quiz questions for use by /learn. Two independent paths. A BOOK run (chapter1, ch1) reads the chapter slice at extracted/textbook/chapters/chapter<N>/chapter<N>.md and writes questions next to it. A CLASS run (week1, wk1) reads from extracted/class/week<N>/ via ### Teaching and writes questions_week<N>.md there. The two never read each other's sources. Re-running a CLASS file MERGES by default (extend only). Re-running a BOOK file warns before overwriting — no merge, since textbook chapters don't change.
---

Pre-generate audited questions for the specified chapter or week.

Two paths, selected by the argument (R0k–R0l):

- **Book run** — `chapter1` — questions from the textbook notes. Everything the book explains.
- **Class run** — `week1` — questions from the week's registered class material. Everything the
  professor taught.

Whether the two happen to cover the same ground does not matter and is never computed.

## Rules

// Source profile
R0.  Before loading notes, look for a `## Source Profile` section in the class root's `CLAUDE.md`.
R0a. IF a Source Profile exists THEN use it. Do NOT re-detect.
R0b. IF no Source Profile exists THEN detect the source's shape per R0c–R0e, write it to `CLAUDE.md` as a `## Source Profile` section, and report that it was created.
R0c. Chapter heading = the shallowest heading level whose text matches a chapter form (`# Chapter N`, `## N`, `# N`). A heading-like line is NOT a heading if it is a code comment — judge by whether it sits among code lines rather than prose.
     // Commentary: a PDF extraction can turn `# !/usr/bin/python3` into what looks like a top-level heading. Counting those destroys the chapter map.
R0c0. Detection under R0c is per-LINE, never per-level. Match every line at a level against the chapter forms and keep the matches. A heading level is NOT disqualified because other lines share its depth, however many of them there are.
     // Commentary: this is the rule whose absence produced the only two `Chapter heading: none` profiles on this system, and both were wrong. `~/edu/cybersecurity` has 141 `#` lines — 26 real `# Chapter <N>: <Title>` headings and 115 code comments — and was recorded as having no chapter level. `~/edu/algorithms` has 39 `#` lines — 35 `# <N> <Title>` chapters and 4 appendices, no code comments at all — and was recorded the same way. In both cases a count was taken, a few lines were sampled, and the sample's character was generalized to the whole level.
R0c0a. Before recording `Chapter heading: none`, state the count of lines matching each chapter form. `none` is admissible ONLY when every form counts zero.
     // Commentary: the wrong profiles both asserted a total ("141 lines beginning `# ` are code comments") that was never broken down by form. Requiring the breakdown makes the false claim impossible to write, because producing it means running the filter.
R0c0b. IF a level holds both chapter-form matches and non-matching lines THEN the level IS the chapter level and the non-matching lines are simply not chapters. Do NOT reach for a fallback pattern.
     // Commentary: a fallback anchored on section headings cuts each slice one chapter-opener late, so every slice loses its own opening and inherits the next chapter's. Measured on the Du textbook: 1,110 opening lines dropped and 1,034 lines bled in across 26 slices.
R0c1. A heading whose entire trimmed text matches `Page <N>` or `Slide <N>` — with or without a trailing `— <title>` — is a LOCATOR, not a heading. Exclude locators when determining the chapter level under R0c, the unit level under R0d, and the unit count under R7.
     // Commentary: /extract R11b and R14b emit these so a dump can be cited and grepped by position. Counting them as structure turns a 400-page PDF into 400 one-page units and a 42-slide deck into 42 units, and every one of those units would then demand its own questions.
R0c2. IF a file's only headings are locators THEN it has no chapter heading and no unit heading. Record `Unit heading: none` and let R8a treat the whole file as one unit.
R0c3. Locators remain valid citation targets. R0c1 removes them from segmentation only — R0q tests them for admissibility and R17 quotes them by name.
R0c4. IF a Source Profile records `Chapter heading: none` AND that `none` satisfies R0c0a AND its unit heading pattern is numbered `N.N` THEN the chapter of a unit is the leading `N` of its section number. R2 matches the requested chapter against that derived number, and R7's N = the count of units whose leading `N` equals it.
     // Commentary: this rule has no user on this system and is expected to have none. It was written for `~/edu/cybersecurity` on the belief that the class had no chapter level; that belief was false — the file carries 26 `# Chapter <N>:` headings, inserted deliberately by an earlier extraction that documented doing so in a comment at the top of the notes file. The rule survives only for a source that genuinely numbers its sections and genuinely has no chapter headings. R0c0a is the gate, and it is what keeps this from becoming a soft landing for a failed detection.
     // Example: `## 3.4 Message Authentication Codes` belongs to chapter 3. `/generate_questions chapter3` selects every `## 3.N` section.
R0c4a. R0c4 is a last resort, never a convenience. IF chapter-form matches exist at any level THEN R0c0b applies and R0c4 does NOT fire, whatever the profile currently records.
     // Commentary: a stale profile must not be able to keep a correct detection from happening. R0a says a recorded profile is authoritative, which is right for a judgment call and wrong for a claim this rule can check.
R0c5. IF a Source Profile records `Chapter heading: none` AND its unit heading pattern carries no chapter number THEN the file has no chapter level at all. Do NOT derive one. R2 finds no match and R4 asks the user which file to use.
     // Commentary: R0c4 works because the section number encodes the chapter. With nothing encoding it, a derived chapter would be invented structure, and R4's existing prompt is the honest outcome.
R0c6. R0c4 does not repair the extraction. IF a profile records `Chapter heading: none` because its notes are damaged THEN say so in the R25 report every run, and name the fix per R0c6a.
     // Commentary: the derivation is a workaround that works well enough to keep a class usable, which is exactly why it would otherwise be forgotten.
R0c6a. Name the fix by the KIND of damage. Structural damage — headings lost, mis-levelled, or unfenced code parsed as headings — is repaired by re-running `/extract`. Character-level damage — `nonnal` for `normal`, `pri vil eged` for `privileged` — is baked into the source's own text layer and re-extraction reproduces it exactly. Do NOT name re-extraction as the fix for the second kind.
     // Commentary: the Du textbook is a 690-page scan of 1-bit page images at 150 ppi with an Acrobat Paper Capture OCR layer; 10.4% of chapter 1's words are one- or two-letter fragments. The class profile told every run that re-extraction was "the real fix" for that, which would have wasted the effort and left the damage in place. Fixing it needs a different extractor or re-OCR, and at 150 ppi bitonal even re-OCR is not a certain win.
R0d. Unit heading = the heading level one deeper than the chapter level. IF only one heading level exists THEN unit = chapter.
R0e. A Source Profile describes the NOTES source only — the textbook at `extracted/textbook/`. It says nothing about class material, which is reached through the registry under R0m and never needs detecting.
     // Commentary: the profile used to carry `Anchor source` and `Generation mode` fields. Both existed to decide which textbook concepts the professor's slides blessed as `core`. Nothing computes that any more — the class material generates its own questions under R0m–R0q — so both fields are gone. A profile that still carries them is stale metadata, not an instruction; ignore them.
R0g. The user may correct a Source Profile by hand. R0a makes the correction permanent.
     // Commentary: detection is a heuristic and will sometimes be wrong. Persisting the result means a wrong guess is corrected once rather than re-made every run.
R0h. Detect the language of the notes content. Record `language: <code>` (e.g. `es`, `en`) in the Source Profile.
R0i. IF language = `en` THEN skip R16f–R16g. No `Teach_EN` or `Question_EN` fields are generated.

// Course scope
R0j. IF this is a BOOK run (R0l) AND `CLAUDE.md` holds a `### Course Scope` entry THEN read its `covers` and `not covered` chapter lists.
R0j1. IF this is a CLASS run (R0k) THEN skip R0j–R0j3 entirely. Print no scope notice.
     // Commentary: scope is a statement about chapters. A week has no chapter number, and material the professor delivered is in scope by definition — it is the definition.
R0j2. IF the chapter being generated is listed as not covered THEN generate its questions normally and say in the R25 report that the course does not cover this chapter.
     // Commentary: out of scope is not out of bounds. The material is still in the book and still worth studying after the course ends, and `/learn <chapter>` delivers it. Refusing to generate would delete the option; reporting it sets the expectation.
R0j3. IF a `### Course Scope` entry carries no derivable chapter list — its `covers` field reads `NOT DETERMINED`, is empty, or names no chapter — THEN treat the class as having NO scope entry. Skip R0j–R0j2, generate normally, and say in the R25 report that a scope entry exists but determined nothing. Do NOT stop under R26.
     // Commentary: /updateclass R26d writes such an entry deliberately — a syllabus that defers its schedule to Canvas still records provenance worth keeping, and inventing a scope would be worse than recording none. `~/edu/software_engineering` holds exactly this entry. Before this rule its `covers: NOT DETERMINED` matched neither R0j's "read the lists" nor R0j2's "listed as not covered", so R26's catch-all fired and every run in that class stopped to ask about a state the chain itself had created.

// Run type — selects which loading block runs; resolve before anything else touches a file
R0k. IF the argument normalizes to a week — `week<N>` or `wk<N>`, case-insensitively — THEN this is a CLASS run. Apply R0m–R0q5 and SKIP R1–R4b.
R0l. IF the argument does not normalize to a week THEN this is a BOOK run. Apply R1–R4b.
R0k1. `week<N>` and `wk<N>` are reserved forms. R2b's substring fallback never sees them, and a file literally named `extracted/wk10.md` does NOT satisfy R1 for such an argument.
     // Commentary: `wk10` previously meant "find a heading containing wk10" and was advertised that way in the Usage block. The class run takes the form over. A user who wants a heading-matched topic file names it something that is not a week.
R0k2. The run type decides the SOURCE, not the machinery. Everything from R9a onward — image handling, concept inventory, generation, audit, output — runs identically for both.

// Class run — source loading (R0k only)
R0m. Source = every `### Teaching` entry in the class root's `## Instructor Material` whose line records `week <N>` for the requested week, regardless of the kind of file it is: slide deck, lecture handout, lab manual, code file, or image. Resolve each path relative to the class root.
R0m1. IF a registered path is a code file or an image THEN open it with the Read tool. Its content is source exactly as an extracted markdown file is.
     // Commentary: /updateclass R21 registers code and images by path rather than extracting them, because converting a diagram or a socket demo to markdown only loses fidelity.
R0m2. IF no `### Teaching` entry records the requested week THEN stop, list the weeks the registry does record, and ask the user how to proceed. Do NOT fall back to the notes source and do NOT guess which files belong to that week.
     // Commentary: falling back would silently produce a book file under a week's name — the exact conflation this split exists to end.
R0m3. IF a `### Teaching` entry records no week at all THEN it is reachable by no class run. Do NOT include it. Report it under R25.
R0m4. IF a registered file cannot be opened or its path cannot be resolved THEN generate from the files that did open and report the unreadable one under R25. Do NOT treat its absence as evidence that anything is uncovered.
R0m5. Do NOT read `### Course Scope` files as source. They are a syllabus, not teaching.
R0n. One unit per registered file, in registry order. N = the number of files. The unit title names the file's own subject.
     // Example: `/generate_questions week1` in `~/edu/software_engineering` reads two decks registered to week 1 → `## Unit 1 of 2 — Introduction` and `## Unit 2 of 2 — Software Processes`.
R0o. On a class run the registered files ARE the question source and the Teach source. The notes source named by the Source Profile is NOT read.
R0o1. R0o is symmetric with R2c: a book run never reads class material, and a class run never reads the textbook. Neither path may reach across to fill a gap in the other.
     // Commentary: a thin slide is not repaired by pulling the textbook's explanation under it. That would rebuild the book/slide correlation this split removed, and it would make a question's Teach field claim the professor said something they did not.

// Class run — admissibility (per locator)
R0p. Strip repeated per-locator chrome before building the inventory. In an extracted deck that is the echoed title line and the trailing footer (deck name, date, slide number); in a paginated handout it is the running header and page number. Chrome is never quotable by R12e and never citable by R17.
     // Example: `## Slide 4 — Software costs` whose body repeats "Software costs" and ends "Chapter 1 Introduction / 30/10/2014 / 4" contributes neither the echo nor the three footer lines.
R0q. A locator is ADMISSIBLE only if it satisfies R12d — its content holds at least one sentence explaining a mechanism, stating a contrast, or describing a scenario. IF a locator is not admissible THEN generate nothing from it and count it in the R25 report.
R0q1. A locator that only ENUMERATES is not admissible. A roadmap, agenda, topic list, table of contents, section divider, or bare title names things without saying anything about them.
     // FAILS R0q1 (enumeration): `## Slide 2 — Topics covered` listing "Professional software development / Software engineering ethics / Case studies".
     // FAILS R0q  (no content):  `## Slide 6 — Professional software development` whose entire body is that same phrase — a section divider.
     // PASSES R0q (presentation): `## Slide 5 — Software project failure` stating "It is fairly easy to write computer programs without using software engineering methods... Consequently, their software is often more expensive and less reliable than it should be."
R0q2. A code file has no sentences. IF a registered code file carries explanatory comments THEN those comments are its R12d sentences and the code they describe is the scenario. IF it carries none THEN the file is inadmissible under R0q and is REPORTED, not silently skipped.
R0q3. Admissibility is not depth. A locator that explains a mechanism in one sentence is admissible; the question is whether it SAYS something, not how much.
R0q4. IF a locator presents two or more PARALLEL definitions that are set against one another — same grammatical form, one list, offered as the members of a single category — THEN it satisfies R12d's contrast clause and is admissible. A question generated from it MUST be a contrast question under R15. Do NOT generate a definition-recall question from it.
     // Commentary: this is the rule the cybersecurity class turns on. `introduction_notes.md ## Page 10 — What is cybersecurity?` gives four one-line definitions — confidentiality, authenticity, integrity, availability — and not one explains a mechanism. Read definition-by-definition, R12d rejects every one of them (exactly as R12e's Aggregation example rejects a bare definition) and the page produces nothing. Read as the contrast it is, the page supports a real question about what distinguishes the four. Without R0q4 the class path fails on precisely the deck it was built to reach.
     // PASSES R0q4: `## Page 11 — Cybersecurity model` — threat/vulnerability, attack, and protection as three members of one model. A question asking how an attack differs from a vulnerability is a contrast (R15).
     // FAILS R15 even under R0q4: "What is confidentiality?" — single definition, pattern-matched. R0q4 admits the LOCATOR; it does not license a recall question.
R0q5. R0q4 does NOT apply to a locator whose items are unrelated, or to one item standing alone. Two definitions on the same page are not a contrast merely by adjacency — they must be presented as members of one category.
     // Commentary: without this, R0q4 collapses into "any page with two bolded terms is admissible", which readmits every roadmap R0q1 just rejected.
     // Commentary: a slide reading only "Nagle's algorithm" means the professor named it, not that they explained it — R0q rejects it for want of a mechanism sentence. A slide that explains it in one sentence is admissible. Terseness is not the test; saying something is.

// File loading — book run (R0l only)
R1.  IF the argument normalizes to a chapter number (R2a) AND the chapter slice `extracted/textbook/chapters/chapter<N>/chapter<N>.md` exists THEN use that file as the notes source.
R1a. IF the class uses a non-English chapter convention (e.g. `capitulo`) THEN R1 checks `extracted/textbook/chapters/capitulo<N>/capitulo<N>.md` instead.
     // Commentary: `es_orto_escolar` uses `capitulo`, matching /extract R16c and /learn R3a.
R2.  IF the argument normalizes to a chapter number AND no chapter slice exists at the R1/R1a path THEN search the full textbook notes file (named in the Source Profile's `Notes file:`) for a chapter heading matching that number, and use the content under that heading as the notes source.
     // Commentary: this is the fallback for classes whose textbook has not been re-extracted with chapter splitting. Once `/extract` runs on the textbook, the slice exists and R1 fires.
R2a. Normalization: `chapter<N>`, `ch<N>`, and `<N>` all match the chapter whose number is `<N>`. Matching is on the chapter NUMBER, not on the argument as a literal substring.
     // Commentary: `chapter5` is not a substring of `## 5`. Before R2a this failed on every chapter and had to be bridged by hand.
R2b. IF the argument does not normalize to a chapter number THEN fall back to matching it as a case-insensitive substring of a heading in the full textbook notes file.
R2c. Exclude from the R2 search, and from the candidate lists R4 and R4a show the user, every file listed in `## Instructor Material`.
     // Commentary: class material is reached one way only — by registry, on a class run, under R0m. R2c and R0o1 are the two halves of that separation.
R3.  IF R2 finds a heading match THEN use the content under that heading as the notes source.
R4.  IF an argument is given AND neither R1 nor R2–R3 locates a source THEN list available chapter slices in `extracted/textbook/chapters/` and ask the user which to use. STOP until user responds.
R4a. IF no argument is given THEN list those same chapter slices, ask the user which to use, and STOP until user responds. Do not proceed on an empty argument.
R4b. IF the source was chosen under R4 or R4a AND no argument was given THEN ask the user for the `<arg>` to name the output file, and STOP until user responds. Do not derive it.
     // Commentary: R24, R24a, and R24e all build filenames from `<arg>`. Picking a source without an `<arg>` leaves the output path undefined, and a guessed name is what /learn will fail to find later.
// Existing-file handling
R5.  IF the output path (R24) already has a questions file THEN read its frontmatter and apply R5a or R5a1.
R5a. IF this is a CLASS run THEN state the recommended merge operation and ask the user to choose `merge`, `regenerate`, or `cancel`. STOP until user responds. The recommended operation is `merge` unless the source material has changed since the file's `generated:` date, in which case it is `regenerate`.
     // Commentary: class files accumulate weekly — a new deck added to the same week extends the existing questions. Merge is the safe default.
R5a1. IF this is a BOOK run THEN warn the user that the file already exists and ask whether to `regenerate` or `cancel`. STOP until user responds. Do NOT offer merge.
     // Commentary: textbook chapters don't change. A book file that already exists was fully generated on its first run. Re-running overwrites; there is nothing to merge into.
R5b. IF the user chooses `merge` (class only) THEN proceed under R5f–R5m. IF `regenerate` THEN discard the existing file and proceed to R7 as a first generation. IF `cancel` THEN stop execution.
R5c. IF the output path has no existing questions file THEN proceed to R7 as a first generation. Do NOT prompt.

// Recorded state
R5d. Read `kind:` from the existing file's frontmatter. It records which path generated the file.
R5e. IF the frontmatter carries no `kind:` THEN treat the file as `kind: book`, whatever its `mode:` and `anchor:` fields say.
     // Commentary: every questions file written before this field existed was generated from a textbook notes source, so `book` is not a guess — it is what those runs did. Their `mode:`/`anchor:` lines are dead metadata and are read for nothing.
R5e1. A `Priority:` field is inert wherever it is found. Do NOT read it, do NOT act on it, and do NOT recompute it. Never write a new one (R24i).
     // Commentary: the 16 questions files on this system were migrated out of the old format on 2026-08-19 — 304 `Priority` lines and 12 `mode:`/`anchor:` lines removed, 478 entries otherwise byte-identical. This rule now covers only a file restored from a backup or carried in from elsewhere. It says nothing about stripping the field, because a merge has no reason to rewrite an entry it is not otherwise touching.
R5e2. IF the requested run type (R0k/R0l) differs from the file's recorded `kind:` THEN stop, name both, and ask the user how to proceed. Do NOT merge across kinds.
     // Commentary: `questions_week1.md` holding book questions, or the reverse, means one of the two was written under the old conflated design or under a mistyped argument. Merging would interleave two sources in one file and no later run could separate them again.

// Merge operation selection
R5f. Under a merge, build the current concept inventory for this run's source and compare it against the concepts the file already questions.
R5g. IF the inventory yields no concept the file lacks THEN write NOTHING. Report no change under R25 and stop.
     // Commentary: this replaces the RE-TIER operation, which existed only to recompute `Priority` against newly registered slides. With no tier to recompute, an unchanged inventory means there is genuinely nothing to do — and saying so is more useful than rewriting a file identically.
R5i. IF the inventory yields at least one concept the file lacks THEN the operation is EXTEND. Apply R5j–R5m.
R5j. EXTEND: build the unit's concept inventory per R12c–R12g, then subtract the concepts the file already questions. Generate candidates for the remainder only, and audit those candidates per R17–R23b.
R5k. Match an existing entry to a concept by its `Concept:` field. IF an entry has no `Concept:` field THEN match on its `Tests:` field instead.
     // Commentary: R13e already guarantees one question maps to exactly one inventory concept, but no field recorded which until now. `Tests:` is a one-line description of the concept under test, which is close enough to carry the four legacy files through their first merge; every entry written after this rule carries `Concept:` and matches exactly.
R5k1. IF R5k's field match does not connect a candidate concept to an existing entry THEN test that concept against every existing entry's `Answer key` using R12g's same-idea test. IF an existing Answer key already carries the idea THEN treat the concept as covered and generate nothing for it.
     // Commentary: questions files get hand-edited. `~/edu/network` chapter 1 Unit 1 Q3 was replaced by hand with a socket-interface question, and its `Tests:` prose resembles no phrasing this skill would generate — so a field match alone misses it and extend appends a second question on the same concept. R12g already defines "same idea" for comparing two inventory concepts; R5k1 applies that same test across the merge boundary.
R5k2. R5k1 governs whether a concept is COVERED, not whether an existing entry is correct. Do NOT rewrite or replace an entry that R5k1 matched.
     // Commentary: a hand-edited question is the user's deliberate correction of something this skill produced. Treating a match as license to regenerate it would undo that edit silently.
R5k3. Before generating a candidate under R5j, read the flagged questions file in the same directory as the questions file (e.g. `extracted/textbook/chapters/chapter<N>/flagged_questions_chapter<N>.md` or `extracted/class/week<N>/flagged_questions_week<N>.md`) if it exists. IF a concept's question was previously removed or replaced there — a flag whose `Status:` field records it as upheld — THEN treat that concept as DELIBERATELY REMOVED. Generate nothing for it and report it under R25.
     // Commentary: found on the first real extend. `~/edu/network` chapter 1 Q3 tested the router vs link-layer-switch contrast; the user flagged it as answerable by repeating the notes verbatim, the flag was upheld, and it was replaced by hand with a socket-interface question. The concept is still in §1.1 and still passes R12d, so a rebuilt inventory readmits it and extend re-adds the exact question the user rejected. The flag file is the only record that the removal was deliberate.
R5k3a. IF a flag's `Status:` field reads `OPEN` THEN it is NOT deliberately removed. The concept is eligible for generation under R5j exactly as an unflagged concept is.
     // Commentary: /learn R23b writes `OPEN` at flag time because nothing has been decided yet — the user has said only that something is wrong with the question. Treating an open flag as a removal would delete a concept on the strength of a complaint nobody has adjudicated.
R5k3b. IF a flag entry carries no `Status:` field at all THEN treat it as `OPEN` under R5k3a, and name it in the R25 report as an unadjudicated flag.
     // Commentary: backward compatibility for flags written before /learn R23b existed. Defaulting to removal would silently drop every concept the user ever flagged, including the ones they flagged and then decided were fine.
R5k3c. Do NOT write to the flagged questions file. R5k3–R5k3b read it only. An extend has no licence to adjudicate a flag.
     // Commentary: adjudicating a flag is the user's call. This skill reporting an unadjudicated flag under R5k3b is the prompt for that call, not a substitute for it.
R5k4. A deliberately-removed concept stays removed within the file it was removed from. IF new material registered to the same week, or a re-extraction of the same chapter, presents that concept again THEN it stays removed.
     // Commentary: the flag was about the question being shallow, not about the topic being unimportant. A second source covering the same topic does not repair the defect the user objected to.
R5k5. R5k3's removals are scoped to one file. A concept removed from `chapter1/questions_chapter1.md` is NOT removed from `week1/questions_week1.md`, and the reverse. Each reads only the flagged file in its own directory.
     // Commentary: the two paths are independent sources. The user rejecting the textbook's shallow treatment of a concept says nothing about whether the professor's treatment of it is worth a question.
R5k6. A merge does NOT add `Source quote:` to an existing entry that lacks it. New entries appended under R5j carry the field per R13g; untouched entries stay as they are, and R18b3 skips them.
     // Commentary: R5k2 already forbids rewriting an entry a merge matched. R5k6 says the same thing about this specific field, because "just adding a missing field" reads as harmless housekeeping rather than as the rewrite it is. Backfilling would attach a quote to a Teach field this run never checked, producing an audit trail that looks verified and is not.
R5k7. IF the user asks for the field to be added to a legacy file THEN that is a `regenerate` under R5a1, not a merge. Say so and let them choose.
     // Commentary: the only honest way to give an old entry a verified `Source quote:` is to generate it again with R13g and R18b live.
R5l. Append new entries at the END of their unit. Existing entry numbers MUST NOT change.
R5l1. R5l overrides R13b for extended entries: the foundational-to-complex ordering applies within a generation, not across a merge.
     // Commentary: /learn R23 writes question numbers into `flagged_questions_<arg>.md`. Renumbering to restore R13b's ordering would invalidate every reference in that file, which is a worse outcome than a late entry that happens to be foundational.
R5m. IF an existing entry maps to no concept in the current inventory THEN keep it, and report it under R25. Do NOT delete it.
     // Commentary: an audited question that survived R17–R21 is not garbage merely because a rebuilt inventory phrased its concept differently. Deleting on an inventory mismatch would silently shrink a file the user has been studying.

// Unit segmentation — book run
R7.  Count the headings matching the Source Profile's unit heading pattern inside the selected chapter. This count is N.
R8.  Each unit heading and its content until the next unit heading, or the end of the chapter, = one unit.
R8a. IF the Source Profile records `Unit heading: none` THEN the whole chapter is a single unit and N = 1.
R8b. R0n overrides R7–R8a on a CLASS run: units come from the registry, one per registered file. Do NOT segment a deck on its `## Slide <N>` locators — R0c1 already bars that, and a 57-slide deck is one unit, not 57.
R9.  Process units in order — document order on a book run, registry order on a class run.

// Image handling (per unit)
R9a. Treat any markdown image link — `![...](path)` — in a unit's content as potential answerable content, not as decoration. Transcribed image content counts as note content for R10, R16, and R17.
R9b. IF a unit's content contains an image link that plausibly holds a formula, equation, table, or data value THEN view that image with the Read tool before generating that unit's questions. Resolve the image path relative to the notes source file's parent directory.
     // Commentary: an `images/foo.jpg` link in `extracted/textbook/chapters/chapter3/chapter3.md` resolves under `extracted/textbook/chapters/chapter3/`. The same link in `extracted/class/week1/deck_notes.md` resolves under `extracted/class/week1/`. The rule is generic — it covers both textbook and class images without hardcoding either path.
R9c. IF an image link is immediately followed by a "**Figure N**" caption AND that caption already conveys the content a question would test THEN you MAY rely on the caption text instead of opening the image.
R9d. IF an opened image contains a formula, table, or data needed by a candidate question THEN transcribe its content into that question's Teach field as text, using plain-text / Unicode math consistent with existing Teach fields (e.g. *n*², Θ(n), ⌊x⌋) — never LaTeX and never a re-embedded image link. R11/R11a/R11b then apply to the transcription.
R9e. IF an image needed for a candidate question cannot be opened or its path cannot be resolved THEN drop that question and record the image in the R25 report. Do NOT guess the image's content.

// Teach content (per question)
R10. IF writing a question THEN write a `Teach:` field immediately before `Question:` carrying only the source content needed to answer this specific question — no more.
R10a. The Teach field is a RESTATEMENT of that content, not an excerpt of it. R11c–R11j require it to be re-broken into lists, anchors, and short sentences, which no verbatim excerpt survives.
     // Commentary: R10 said "excerpt" from the beginning and nothing has ever produced one — R11c–R11j make that impossible, and they are worth keeping, because extracted source prose arrives line-broken with figure tables dumped mid-paragraph. Naming the restatement is what makes R18b's job legible: the field is allowed to be re-worded, and R18b is the bound on how far.
R10b. R18b and R18b1 are the limit on R10a. Restating, reordering, shortening, and formatting are the licence; adding a claim the source does not carry is not.
     // Commentary: R10a without R10b reads as permission to write freely. The pair is the whole point — reword as needed, assert nothing new.
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
R12e1. The sentence recorded under R12e is quoted VERBATIM from the source, including its own wording and punctuation. Do NOT paraphrase it, do NOT correct its grammar, and do NOT merge two separated sentences into one quotation.
     // Commentary: this sentence becomes the entry's `Source quote:` field under R13g and is the only thing R18b can check a Teach field against. A paraphrase recorded here would make R18b compare a rewrite to a rewrite, which is the exact failure R18b exists to close.
R12e2. IF an extraction has split the sentence that satisfies R12d — a figure, page header, or table interrupts it mid-sentence — THEN record the fragments joined by ` [...] `, each fragment verbatim. Do NOT silently stitch them into a sentence that appears nowhere in the source.
     // Commentary: found on `~/edu/software_engineering` chapter 1. Figure 1.2's table is extracted into the middle of the "Engineering discipline" sentence, so "However, they use them selectively" and "and always try to discover solutions to problems" sit 28 lines apart. An audit quote that joined them was findable in neither the Teach field nor the source, and no rule had said what to do.
     // Example: `"However, they use them selectively [...] and always try to discover solutions to problems even when there are no applicable theories and methods."`
R12f. Exclude from the inventory: bibliographic references, author names, tool and product names, chapter objective lists, further-reading sections, end-of-chapter exercises, page headers, and — on a class run — the chrome R0p strips and the enumerations R0q1 rejects.
     // Commentary: an Objectives or Key Points list states what the chapter will cover, not how anything works. R12d already refuses it for want of a mechanism sentence; R12f names it so the refusal is not left to judgment. Nothing reads those lists for any other purpose any more.
R12f1. R12f excludes those passages from the CONCEPT INVENTORY only. It does NOT remove end-of-chapter exercises from R12h0's classification or from R12t's curated-question scan.
     // Commentary: "exclude end-of-chapter exercises" reads as licence to skip the section entirely, which is how a whole set of curated questions went unscanned on the first chapter-1 run. The exercises are excluded as a source of CONCEPTS; they remain a source of QUESTIONS.
R12g. IF two inventory concepts would produce questions with the same Answer key idea THEN merge them into one concept.
R12g1. R12g's same-idea test also applies ACROSS units within one run. IF a concept would produce a question with the same Answer key idea as a concept already questioned in an EARLIER unit of this run THEN exclude it and report it under R25, naming the unit that already covers it.
     // Commentary: R12g was scoped to a single unit, which is enough for an ordinary section and useless against a chapter summary. `~/edu/network` chapter 1 §1.8 restates §1.1–§1.7 wholesale, and §1.7.5 restates §1.3.3's content-provider networks. Without this rule the run either re-asks them or invents an unwritten policy on the spot, which is what the first full chapter-1 run had to do.
R12g2. R12g1 excludes the LATER concept, never the earlier one. Unit order is document order on a book run and registry order on a class run (R9).
     // Commentary: the earlier unit is where the material is actually taught. A summary's restatement is the copy, so the copy is what goes.
R12g3. R12g1 is scoped to one run over one source. It says nothing about a concept questioned in a different chapter file or in the week file for the same material.
     // Commentary: R5k5 already keeps the book and class paths independent. R12g1 must not become a back door that lets a chapter run suppress a concept because some other file covers it.

// Exercise classification (per unit) — R12r and R24e read its output
R12h0. IF the source contains an `Exercises` section THEN classify each numbered exercise as `analytical` or `constructive`. This runs on both paths — a lab handout registered to a week can carry exercises exactly as a chapter can.
R12h0a. An exercise is `analytical` IF it asks the reader to explain, discuss, describe, compare, suggest a reason, or give examples.
R12h0b. An exercise is `constructive` IF it asks the reader to produce an artifact — draw, design, develop, model, write, or rewrite.
R12h0c. IF an exercise contains both an analytical and a constructive clause THEN classify it `analytical`.
     // Example: 5.8 "Draw a sequence diagram for the same system. Explain why you might want to develop both activity and sequence diagrams" → analytical, on the strength of the second clause.
     // Commentary: only analytical exercises have an answer that fits the Teach + Answer key format. Constructive exercises are preserved under R24e.
R12h0d. R12t overrides R12h0: IF a numbered exercise is interrogative AND its answer appears in the source body THEN it is a CURATED QUESTION and R12t decides its fate. R12h0 classifies only the exercises R12t did not adopt.
     // Commentary: found on the first full chapter-1 run in `~/edu/network`. Kurose's 28 end-of-chapter Review Questions satisfy both rules at once — they are numbered exercises AND they are answerable from the chapter body. The run classified all 28 as `analytical` under R12h0, never scanned them under R12t, and then independently generated "What is the difference between a virus and a worm?" — which is review question R26 almost verbatim. Neither rule was broken. Nothing said which one applied.
R12h0e. IF R12t declines to adopt a curated question because it maps to no inventory concept THEN R12r's inventory-gap handling applies to it exactly as to an unadopted analytical exercise.
     // Commentary: R12h0d must not create a hole in gap detection. A question the author thought worth asking, about something the chapter never explains, is the exact case R12r exists to surface.

// Inventory handling
R12m. The concept inventory is internal metadata. Do NOT write it to the output file. Each question records its own concept in the `Concept:` field per R13f and its own R12e sentence in the `Source quote:` field per R13g. Those two fields are the only trace of the inventory the file carries.
R12m1. No entry carries a priority, a tier, or a rank. There is no `Priority:` field.
     // Commentary: the tier existed to answer "which of these book questions did the professor bless?" A class run answers that by generating from what the professor delivered, so the question is no longer asked of a book run. `week<N>` is the study list; `chapter<N>` is the reference bank.

// Inventory gap check (per unit) — book run only
R12r. IF this is a BOOK run AND an `analytical` exercise asks about a topic that no inventory concept covers THEN record it as an inventory gap.
R12s. IF an inventory gap is recorded THEN attempt to admit the missing concept under R12d–R12e. IF no sentence in the chapter body explains it THEN leave it uncovered and report it under R25.
     // Commentary: an exercise can ask about something the chapter never explains — ch1 exercise 1.7 (how electronic connectivity between development teams supports software engineering) is one. A question for it would fail R17/R18. Reporting the gap is more honest than manufacturing an unanswerable question.

// Curated question adoption (per unit)
R12t. After building the concept inventory, scan the unit's source for curated questions — any interrogative sentence whose answer appears in the same source. Match each to the inventory concept it tests.
R12t1. A curated question is ADOPTABLE if all three hold: (a) it maps to exactly one inventory concept, (b) the source contains enough content after the question to build a Teach field that makes it answerable (R12/R16), and (c) it passes R15 — it requires explaining a mechanism, describing a scenario, or contrasting two ideas, not pattern-matching a definition.
R12t2. A curated question is NOT adoptable if any of these apply: it is a discussion prompt with no answer in the source; it is a skill checklist item (assumed prerequisite knowledge); it is an ethical dilemma or open-ended question the author deliberately left unanswered; it is a process-step definition where the question IS the content, not a test of it; it duplicates a question already adopted for the same concept; or it fails R15 (definitional recall).
     // Commentary: R12t2 is the filter that keeps bad source questions out. The author's judgment is trusted for content selection (which concept to question) but not for question quality (whether the question tests understanding). A definitional "What is X?" fails R15 regardless of who wrote it.
R12t3. For each adopted question: preserve the author's question wording in the `Question:` field. Build `Teach:`, `Answer key:`, `Elaboration:`, and `Audit:` from the source content per the same rules as generated questions (R10–R12b, R16a–R16e, R17). Record `Concept:` per R13f and `Source quote:` per R13g2.
R12t4. IF a curated question's wording is compound (two `?` marks, or two independent facts required) THEN split it into two entries per R15a–R15b, preserving the author's phrasing for each half. Do NOT discard it for being compound — the concept is worth testing, the format just needs fixing.
R12t5. IF a curated question maps to an inventory concept but fails R15 (definitional recall) AND the concept has already been introduced in a prior unit or chapter THEN do NOT adopt it. The concept remains uncovered and R13 generates a question for it. Report the skipped curated question under R25.
     // Commentary: a definitional question about an established term is lazy recall. The concept is still worth testing — just with a better question that R13 can generate.
R12t5a. R12t5a overrides R12t5: IF the concept is being introduced for the first time in this source — its first appearance in the textbook or first mention in the course material — THEN a definitional question IS adoptable even if it would otherwise fail R15. Knowing what something is comes before understanding how it works.
     // Commentary: "What is software?" in chapter 1 is a foundational question that establishes vocabulary. The same question in chapter 15 is lazy recall. The test is whether the reader has seen the term before, not whether the question is deep.
R12t6. IF multiple curated questions map to the same inventory concept THEN adopt the one that best satisfies R15 (mechanism > scenario > contrast > none). Discard the rest.
R12t7. Adopted questions go through the same audit (R17–R23b) as generated questions. An adopted question that fails audit is dropped and its concept becomes eligible for generation under R13.
R12t8. Adoption is per-unit. A curated question in unit 2 does not cover a concept in unit 1.
R12t9. Curated questions are not confined to a unit's own prose. A textbook's end-of-chapter review questions, a handout's checkpoint questions, and a deck's in-line prompts are all in scope. Scan them wherever they physically sit in the source.
     // Commentary: R12t says "scan the unit's source", which reads as the unit's body text and so silently excludes the one place a textbook reliably puts its curated questions — the end of the chapter.
R12t10. R12t10 overrides R12t8: IF a curated question carries an explicit label naming the section, chapter, or slide it tests — `SECTION 1.1`, `Chapter 3 Review`, `Recap of slide 12` — THEN it belongs to the unit that label names, NOT to the unit whose text physically contains it. IF it carries no such label THEN R12t8 stands and it belongs to the unit it sits in.
     // Commentary: without this, every review question in a textbook lands in the summary unit, maps to none of that unit's concepts, and is discarded by R12t1(a) — which looks identical to having scanned and found nothing adoptable.
     // Example: Kurose's review questions sit under the chapter summary but are grouped under `SECTION 1.1` through `SECTION 1.6` headers. R1–R3 are unit 1's curated questions; R26–R28 are unit 6's.
R12t11. IF a unit's scan finds no curated question at all THEN report that as an explicit zero under R25. Do NOT omit the unit from the adoption report.
     // Commentary: a unit that was never scanned and a unit that was scanned and yielded nothing produce the same silence. The zero is what makes the scan auditable.

// Question generation (per unit)
R13. Generate exactly one candidate question per concept in the unit's concept inventory that has no adopted curated question from R12t. There is no fixed upper or lower bound on the number of questions per unit.
R13a. The question count is bounded by the inventory and nothing else. R12d–R12g are what keep it honest: a concept the source does not explain never enters the inventory, so it never becomes a question.
     // Commentary: the old capped mode bounded a unit to 2–5 questions when there was no tier to thin the results with. Both bounds are gone. A book run on a 25-chapter textbook now yields the whole book, which is correct — that file is a reference bank, and the study list is `week<N>`.
R13b. Order questions within each unit from most foundational concept to most complex, so later questions may safely rely on earlier ones having been seen.
R13c. R15b overrides R13: IF one inventory concept produces two natural sub-questions THEN that concept yields two entries.
R13d. IF a unit's concept inventory is empty THEN stop, show the user the unit's notes, and ask how to proceed. Do not improvise.
R13d1. R13d1 overrides R13d: IF a unit's inventory is empty ONLY because every concept it held was excluded under R12g1 as already covered by an earlier unit THEN this is a RESTATEMENT UNIT. Generate nothing for it, continue to the next unit, and report it under R25 naming the units its content repeats. Do NOT stop and do NOT ask.
     // Commentary: a textbook chapter summary is a restatement unit by design. R13d exists for a unit whose notes explain nothing — a genuine extraction failure or a section that is pure roadmap. A summary that successfully repeats six units is neither, and halting on it would interrupt every remaining chapter of a nine-chapter book.
R13d2. A restatement unit still appears in the output file with its heading and its "Unit N of M" numbering, carrying no questions and a one-line note that its content is covered by the units named.
     // Commentary: dropping the heading would renumber every later unit and silently contradict the Source Profile's unit count. /learn delivers every entry in the file (its R1c) and simply finds none here.
R13d3. R13d stands wherever R13d1 does not: an inventory empty because the unit's notes hold no R12d sentence at all is still a stop-and-ask. The two causes are not interchangeable.
     // Commentary: "everything here was already taught" and "nothing here teaches anything" look identical from the empty inventory alone. Only the exclusion reasons recorded under R12g1 tell them apart, which is why R12g1 requires them to be recorded.
R13e. Before saving, check each candidate question against the inventory. IF a question does not map to exactly one inventory concept THEN drop it.
     // Commentary: R13e is the anti-padding guard — it catches questions invented to fill space rather than derived from the material.
R13f. Record each question's inventory concept in its `Concept:` field. This is the merge key R5k reads.
     // Commentary: R13e has always required the one-question-one-concept mapping; nothing wrote it down, so a later run had to re-derive it from prose. Recording it makes a merge exact instead of approximate.
R13g. Record the R12e sentence for this question's concept in its `Source quote:` field, verbatim per R12e1–R12e2. This is the field R18b audits the Teach field against.
     // Commentary: before this rule the R12e sentence was computed, used to admit the concept, and discarded. Everything downstream — Teach, Question, Answer key, Audit — was then checked only against the Teach field, so the one step where a paraphrase can drift from the source was the one step nothing verified.
R13g1. IF a question's Teach field draws on two or more R12e sentences THEN `Source quote:` carries all of them, each verbatim, separated by a blank line. Do NOT record only the first.
     // Commentary: R12a lets a Teach field carry context beyond the concept's own explanation. R18b can only check what R13g recorded, so a partial record silently exempts the rest of the Teach field from the audit.
R13g2. IF a question was adopted under R12t THEN `Source quote:` records the source sentence(s) its Teach field was built from, NOT the curated question's own wording.
     // Commentary: the author's question is preserved in `Question:` under R12t3. What R18b needs is the content the answer rests on.
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
R15g. A `Question:` field MUST name its subject. It MUST NOT point at its own `Teach:` field deictically — "this formula", "these two delays", "the expression above", "the example just given".
     // Commentary: /learn's `no_context` mode hides the Teach field and asks the question alone (its R1c delivers every entry either way). A deictic question is not merely awkward there — it is unanswerable, because the thing it points at is not on screen. The same breaks on `/learn resume`, which reopens a file mid-unit, and whenever the user reads the file directly.
     // FAILS R15g: "Why does this end-to-end expression leave out one of the four delay components entirely?" — "this expression" exists only in the Teach field.
     // PASSES: "The end-to-end delay formula adds only three of the four delay components. What assumption lets it drop the fourth?" — names its subject and stands alone.
R15g1. R15g bars pointing OUTWARD at the Teach field. It does not bar a pronoun whose antecedent the Question itself supplies.
     // Commentary: without this, R15g reads as a ban on the word "this" and starts rejecting well-formed scenario questions.
     // PASSES R15g1: "A radiologist sets up a circuit, requests an x-ray, studies it for two minutes, then requests another. Explain what the network loses during those two minutes." — "those two minutes" was established two clauses earlier, inside the Question.
R15g2. R15g does NOT override R12a. A Question may still rely on a term defined in an EARLIER question's Teach field within the same unit; what it may not do is refer to its own.
     // Commentary: R12a's shared context is cumulative and survives into `no_context` only as prior knowledge, which is the mode's whole premise. A deictic reference to the current entry survives nothing.
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
R18b. Compare the Teach field against this entry's `Source quote:`. IF the Teach field asserts anything the `Source quote:` does not support THEN mark FAIL with reason "Teach drifts from source — rewrite against the quote or drop".
     // Commentary: R17–R20 all audit the Teach field against itself or against the Question. R18b is the only rule that audits the Teach field against the source, and it is the reason R13g records the quote at all. R18a is this same check for images; R18b is the prose case that was missing.
     // Test: read ONLY the `Source quote:`, then read the Teach field. IF the Teach field tells you something the quote did not, that content came from somewhere else and R18b fires.
     // FAILS R18b: quote says "the bandwidth to the satellite is relatively narrow"; Teach says "the satellite link is too slow to carry per-minute readings, so the station compresses them". Compression appears nowhere in the source.
     // PASSES R18b: quote says "the insulin pump delivers one unit of insulin in response to a single pulse from a controller"; Teach says "the pump delivers one unit of insulin per pulse from the controller". Restated, nothing added.
R18b1. Restating, reordering, shortening, and formatting the `Source quote:` are permitted. Adding a mechanism, a cause, a consequence, a number, or an example that the quote does not carry is not.
     // Commentary: R11c–R11j require the Teach field to be reformatted into lists, diamond anchors, and short sentences. R18b would be unusable if reformatting counted as drift — the check is on claims added, not on words changed.
R18b2. R12a does NOT exempt a Teach field from R18b. IF a Teach field carries context from a prior question's concept THEN that context's own R12e sentence belongs in `Source quote:` per R13g1.
     // Commentary: otherwise "an earlier Teach field established this" becomes an unauditable channel for anything at all.
R18b3. IF an entry carries no `Source quote:` field THEN skip R18b for that entry and report it under R25. Do NOT mark FAIL, and do NOT backfill the field.
     // Commentary: every questions file generated before R13g existed lacks it. Failing those entries would fail every legacy entry on its first merge, and backfilling would mean writing a quote this run never verified — a fabricated audit trail is worse than an absent one. R5k6 governs the merge case.
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
R20c. IF the `Question` field points at its own `Teach` field deictically THEN mark FAIL with reason "question not self-contained — rewrite per R15g".
     // Test: cover the Teach field and read the Question alone. IF you cannot tell what it is asking about, R20c fires. Apply the test to every candidate — R17–R20 all read the Question WITH its Teach field in view, so none of them can see this defect.
     // Commentary: this was the one flaw in the chapter-1 output that survived a full R17–R21 audit and was caught only when the 106 questions were listed together, stripped of their Teach fields. That listing is exactly what `no_context` mode does to the file.
R21. IF a candidate question is not marked FAIL by R17–R20 — including all lettered sub-rules — THEN mark PASS.
R22. Drop all FAIL questions. Only PASS questions go into the output file.
R23. R23 overrides R13: IF all candidates for a unit fail audit THEN generate a new round of candidates targeting inventory concepts not yet used, and re-audit each. IF every inventory concept has already been used THEN re-run R12c–R12g over the unit's notes to find concepts the first inventory missed.
R23a. IF 3 rounds of candidates for a unit have all failed audit THEN stop, show the user the failed candidates with their fail reasons and the unit's notes, and ask whether to (a) keep generating or (b) skip the unit. STOP until user responds.
     // Commentary: no near-miss option — a question not fully answerable from its Teach field produces frustration, not retention.
R23b. Do NOT declare a unit unquestionable without completing R23a.

// Output
R24. Save the questions file next to its source:
     - Book run: `extracted/textbook/chapters/chapter<N>/questions_chapter<N>.md`
     - Book run (non-English convention): `extracted/textbook/chapters/capitulo<N>/questions_capitulo<N>.md`
     - Class run: `extracted/class/week<N>/questions_week<N>.md`
     IF the output directory does not exist THEN create it (including intermediate directories).
     Use the exact structure in the Output Format block below.
R24a. IF the questions file is saved AND the class root contains a `CLAUDE.md` with a `## Contents` section THEN add a one-line entry for the questions file under the appropriate group: `**extracted/textbook/**` for book runs, `**extracted/class/**` for class runs. IF the needed group header does not exist THEN create it. IF an entry for the file already exists THEN replace that line instead of duplicating.
R24a1. R24a applies identically to `practice_<arg>.md` (R24e): it gets its own Contents entry under the same `**extracted/**` group, on the run that creates it.
     // Commentary: /updateclass R5 uses Contents as its seen-set. A file this skill writes but never inventories reads as NEW on the next /updateclass run, which then asks the user "instructor-provided?" about the chain's own output. R7 of that skill now also excludes these by name, so the two rules cover each other — but the inventory is the one that should have been right first.
R24a2. IF a file this skill would have written was NOT created on this run — no constructive exercises (R24g) — THEN write no Contents entry for it. Do NOT inventory a file that does not exist.
R24b. IF the questions file is saved AND the class root contains a `CLAUDE.md` without a `## Contents` section THEN append a `## Contents` section (format: `**<dir>/**` bold group headers, one `- file — description` line per entry) and add the entry per R24a.
R24c. IF the class root contains no `CLAUDE.md` THEN skip R24a–R24b.
R24d. IF updating the Contents section THEN do not modify any other part of `CLAUDE.md`.

// Constructive exercises
R24e. IF the chapter contains `constructive` exercises THEN write them next to the questions file (same directory as R24) with frontmatter `name: practice_<arg>`, `source: <notes filename>`, `generated: <today's date>`.
R24f. Each `practice_<arg>.md` entry records the exercise number and its text verbatim. Do NOT paraphrase and do NOT attempt an answer.
     // Commentary: these are hand-worked tasks — diagrams, specifications, designs. /learn cannot grade them. The file exists so they are not lost.
R24g. IF the chapter contains no constructive exercises THEN do NOT create `practice_<arg>.md`.

// Frontmatter and per-entry metadata
R24h. IF saving THEN write `kind: book` or `kind: class` into the frontmatter, from the run type selected by R0k/R0l. Do NOT write `mode:` or `anchor:` fields.
     // Commentary: R5d reads `kind:` to refuse a cross-kind merge under R5e2. It is the only frontmatter field any rule acts on.
R24h1. On a CLASS run the frontmatter `source:` field lists every registered file read, comma-separated, not a single filename.
R24i. IF saving an entry THEN write its `Concept:` field per R13f and its `Source quote:` field per R13g. Do NOT write a `Priority:` field on any entry, on either path.
R24i1. `Source quote:` is written on both paths. On a class run the quote comes from the registered file the concept was admitted from, and R0p chrome is never quotable per R12e.
R24j. Coverage gaps and `gaps_<arg>.md` no longer exist. Do NOT write that file, and do NOT compute whether the notes source covers what a `### Teaching` file taught.
     // Commentary: that file recorded topics the professor taught that the textbook could not answer — the residue of ranking one source against the other. A class run now generates questions for exactly those topics, so the gap is not a gap. IF a stale `gaps_*.md` exists anywhere under `extracted/` THEN leave it alone and name it in the R25 report as obsolete; deleting a user's file is not this skill's call.

// Mechanical verification — after saving, before reporting
R24k. After saving the questions file, run `python3 <skill dir>/verify_quotes.py <output path>`. The run is NOT complete until it has been run.
     // Commentary: R18b is a judgment call and R17–R21 are the model auditing its own output. R24k is the one check in this skill that cannot be talked out of its answer — it asks whether a string is in a file. It exists because an earlier chapter 1 run marked 80 audit quotes PASS and a substring comparison found 5 that were in neither the Teach field nor the source.
R24k1. IF verify_quotes.py exits non-zero THEN fix every quote it names and re-run it. Repeat until it exits 0. Do NOT report the run as complete on a failing verify, and do NOT explain the failures away in prose.
     // Commentary: a named quote is wrong in one of three ways and all three are the skill's fault, not the script's: fabricated, paraphrased where R12e1 requires verbatim, or stitched where R12e2 requires ` [...] `. None is a false positive to be argued with.
R24k2. IF a quote is genuinely present but the script cannot find it THEN that is a normalization defect in verify_quotes.py. Fix the script, do NOT edit the quote to match the script.
     // Commentary: editing the entry to satisfy the checker inverts the whole point — the source is the authority, and the script is the thing that models it imperfectly.
R24k3. IF the script exits 2 — no readable source — THEN say so in the R25 report and name the path it tried. Do NOT report the quotes as verified.
R24k4. R24k runs on a merge too, over the whole file. Legacy entries carrying no `Source quote:` are counted and skipped, not failed (R18b3).
R24k5. The user may run verify_quotes.py themselves against any questions file, with no model involved. IF they ask how to check a file THEN give them the command.
     // Commentary: this is the only part of the audit chain that does not require trusting this skill's output, which makes it the part worth handing over.

// Report
R25. After saving, report: (1) the RUN TYPE — book or class — and the argument that selected it, (2) units processed, (3) questions saved, (4) candidates dropped and their fail reasons, (5) output file path, (6) whether `CLAUDE.md` Contents was updated, (7) images opened (count), (8) any candidate questions dropped because an image could not be opened or resolved (per R9e), (9) the concept inventory size per unit, (10) concepts excluded under R12e–R12f with the reason for each, (11) the analytical/constructive exercise split, (12) inventory gaps found under R12r and whether each was fixable, (13) the Source Profile used and whether it was read from `CLAUDE.md` or newly detected — book runs only, (14) any unit where an R15d–R15e question-type quota was waived under R15f, and which type the material could not supply, (15) language detected and whether `Teach_EN`/`Question_EN` translations were generated, (16) the operation chosen under R5g/R5i — first generation, extend, no change, or regenerate — and what selected it, (17) on an extend, how many entries were added per unit and how many existing entries were left untouched, (18) any existing entry kept under R5m because it matched no current inventory concept, (19) every concept skipped as DELIBERATELY REMOVED under R5k3, naming the flag it came from, (20) every unadjudicated flag found under R5k3b — a flag whose `Status:` is `OPEN` or absent — so the user can resolve it before the next merge, (21) any stale `gaps_*.md` found under R24j, named as obsolete, (22) curated questions adopted per unit (count and which concepts they cover), stating an explicit zero for any unit that yielded none per R12t11, (23) curated questions skipped per unit with reason (failed R15, unanswered, duplicate, etc.), (24) concepts filled by adoption vs. generation (ratio per unit), (25) candidates that failed R18b — Teach drifting from `Source quote:` — with a count and whether each was rewritten or dropped, (26) entries skipped by R18b3 for carrying no `Source quote:`, with a count, (27) the verify_quotes.py result under R24k — quotes checked, quotes not found, and how many re-runs it took to reach exit 0, (28) every concept excluded under R12g1 as already covered by an earlier unit, naming the unit that covers it, (29) every RESTATEMENT UNIT identified under R13d1, naming the units its content repeats.
     // Commentary: (25) is the number that tells the user whether R18b is doing anything. A run reporting 0 failures across 70 questions is reporting that its own audit caught nothing, which is worth seeing plainly rather than reading as a clean bill of health.
R25a. IF this is a CLASS run THEN additionally report: (a) every registered file read, with its week and its locator count, (b) locators dropped as inadmissible under R0q–R0q2, with a count and the reason per locator kind (chrome, enumeration, no explanatory content), (c) any `### Teaching` entry that records no week and is therefore unreachable (R0m3), (d) any registered file that could not be opened (R0m4).
     // Commentary: (b) is the number that makes a class run auditable. "57 slides, 41 admissible, 16 dropped — 3 dividers, 2 roadmaps, 11 chrome-only" is checkable; a bare question count is not, and a deck whose extraction broke would look identical to a deck that was mostly section headers.
     // Commentary: (c) is the only place an entry registered with `week: n` becomes visible. /updateclass permits it, and it is silently unreachable everywhere else.
     // Commentary: (13) matters because a wrong profile silently changes segmentation. Naming it in the report is how a bad detection gets caught on the first run rather than the tenth.
     // Commentary: (9) and (10) make the question count auditable — the user can see whether a unit got N questions because it holds N concepts or because the generator padded.
     // Commentary: (17) is what makes a merge auditable. "Added 4, left 47 untouched" is checkable; "done" is not, and a merge that silently rewrote everything would look identical to one that did not.

// Catch-all
R26. IF any condition not covered by R0–R25 (including lettered sub-rules) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Output Format

```
---
name: questions_<arg>
source: <notes filename — or, on a class run, every registered file read (R24h1)>
generated: <today's date>
kind: book | class             ← the run type that produced this file (R24h)
---

## Unit 1 of N — <Unit Title>

#### Q1
Concept: <the inventory concept this question tests — the merge key, per R5k>
Source quote: <the R12e sentence(s), VERBATIM from the source — what R18b checks Teach against (R13g)>
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
Source quote: <this question's R12e sentence(s) — multiple ones separated by a blank line (R13g1)>
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

// Note: Concept, Source quote, Tests and Audit are internal metadata — /learn never displays them and never acts on them. Source quote in particular is NOT a second Teach field: it is the raw source sentence, kept so R18b can check the Teach field against it and so the user can spot-check a suspect question without reopening the source. Showing it before an answer would hand the user the answer. /learn displays only the Teach field (teach mode) and Question, and grades on Answer key alone. It delivers every entry in the file; there is no filter and nothing to filter on. Concept exists solely as the merge key R5k matches on. Elaboration is never shown before the user answers — /learn displays it only alongside Answer key after a wrong answer or a skip. Teach_EN and Question_EN are never displayed by /learn when it delivers a question — it prints them only when the user types `en` on that question.
// Note: a file written before this format carries a `Priority:` line per entry and `mode:`/`anchor:` frontmatter. R5e reads such a file as `kind: book` and R5e1 leaves those fields exactly where they are. Nothing reads them.

## Usage

```
/generate_questions chapter2     ← book run: reads extracted/textbook/chapters/chapter2/chapter2.md
                                   writes extracted/textbook/chapters/chapter2/questions_chapter2.md
/generate_questions week1        ← class run: reads from ### Teaching entries for week 1
                                   writes extracted/class/week1/questions_week1.md
/generate_questions wk1          ← same as week1
```

A book run reads the chapter slice at `extracted/textbook/chapters/chapter<N>/`. If no slice exists,
it falls back to segmenting the full textbook notes file. It writes questions next to the slice.
Re-running warns before overwriting — no merge, since textbook chapters don't change.

A class run reads the `### Teaching` entries in the class `CLAUDE.md` that record the requested week —
slide decks, handouts, labs, code, images alike. It never opens the textbook. Re-running offers merge
by default (extend only). A book run never opens the class material. Whether the two overlap is not
computed and does not matter.
