# generate_questions — SELECT run rules

Loaded under R0k2 when the argument normalizes to a week. These rules GENERATE NOTHING. They read
the week's registered class material for one purpose — to learn which topics the professor covered —
then COPY the matching questions out of the chapter pool into the week file, which is the study list.

Read this together with the shared core in `SKILL.md`. Rule IDs are global across both files.

## Rules — select run

// What a select run does not do
R0e1. A SELECT run does not need a Source Profile. It reads no notes and segments nothing. IF this is a select run THEN skip R0–R0i entirely; do NOT detect a profile and do NOT write one.
R4b5. IF this is a SELECT run THEN skip R4b–R4b4 entirely. A select run copies from the pool; the book run that wrote the pool is where repair happens.
R8b. R0r overrides R7–R8a on a SELECT run: units come from the POOL, one per origin chapter that contributed a selected entry, in ascending chapter order.
     // Commentary: R0–R0i, R4b–R4b4 and R7–R8a live in book.md and are not loaded on this path. These three rules stay here so the skip is stated, not merely structural.

// Course scope
R0j1. IF this is a SELECT run (R0k) THEN skip R0j–R0j3 entirely. Print no scope notice.
R0j4. Course Scope never restricts a SELECT run's pool. R0o2 draws from every chapter questions file that exists, including chapters the syllabus lists as not covered.

// Reading the week's material
R0m. Read every `### Teaching` entry in the class root's `## Instructor Material` whose line records `week <N>` for the requested week, regardless of the kind of file it is: slide deck, lecture handout, lab manual, code file, or image. Resolve each path relative to the class root.
R0m1. IF a registered path is a code file or an image THEN open it with the Read tool. Its content signals coverage exactly as an extracted markdown file does.
R0m2. IF no `### Teaching` entry records the requested week THEN stop, list the weeks the registry does record, and ask the user how to proceed.
R0m3. IF a `### Teaching` entry records no week at all THEN it is reachable by no select run. Do NOT include it. Report it.
R0m4. IF a registered file cannot be opened or its path cannot be resolved THEN select from the files that did open and report the unreadable one.
R0m5. Do NOT read `### Course Scope` files as teaching. They are a syllabus, not a lecture.

// The coverage profile
R0n. The registered files are read for ONE purpose: to determine which topics the week covered. They are never a question source — no question is ever written from them and no field is ever built from them.
R0n1. The output of reading them is the COVERAGE PROFILE — a list of topics the week's material addresses, each recorded with the locator that addresses it.
R0n2. A topic enters the coverage profile IF the material DEVELOPS it — presents it as content to learn, not merely lists it for future reference. No mechanism-sentence requirement, no depth requirement. A single slide that explains or illustrates a concept is sufficient.
R0n2a. IF a slide, section, or passage ONLY lists a topic by name inside a roadmap, agenda, table of contents, or "what we will cover" enumeration THEN that topic does NOT enter the coverage profile. A roadmap is a promise of future coverage, not coverage itself.
R0n2b. R0n2a does NOT apply when the enumeration is the teaching content itself — e.g., a slide listing the four delay components with a one-line definition of each IS coverage, because the definitions are the lesson.
R0n3. R0p's chrome is the one thing excluded beyond R0n2a. A deck name, a date, or a slide number names no topic.
R0n4. IF a registered code file carries no explanatory comments THEN its profile topics are what the code itself demonstrates — the API it calls, the mechanism it implements.
R0n5. IF the material presents a topic only to EXCLUDE it — "we will skip 4.3", "not on the exam" — THEN do NOT add it to the profile, and report the exclusion.
R0n6. Record each profile topic with the locator that produced it, so the report can name where a topic came from and R0q3 can say which slide asked for a question the pool could not supply.
R0p. Strip repeated per-locator chrome before building the profile. In an extracted deck that is the echoed title line and the trailing footer (deck name, date, slide number); in a paginated handout it is the running header and page number.

// The question pool
R0o. The POOL = every `questions_chapter<N>.md` under `extracted/textbook/chapters/` that exists, or `questions_capitulo<N>.md` under the non-English convention (R1a). Read all of them. Do NOT read the textbook notes — only the questions files.
R0o1. IF the pool is empty — no chapter questions file exists anywhere — THEN stop, say so, and tell the user to run `/generate_questions chapter<N>` first.
R0o2. Selection is by TOPIC, not by chapter number. A week may draw from any chapter, in any combination, and is never restricted to the chapters a syllabus maps to that week.
R0o3. A select run NEVER writes a question that did not already exist in the pool, in any circumstance, for any reason.
R0o4. IF a chapter slice exists but its questions file does not THEN that chapter contributes nothing to the pool. Note it, because R0q3 will need it.

// Matching
R0q. Select a pool entry IF its `Concept:` field names a topic in the coverage profile. IF the entry carries no `Concept:` field THEN match on its `Tests:` field instead.
R0q1. Matching is on the IDEA, judged by R12g's same-idea test — not on the string.
     // PASSES R0q1: profile topic "3-way handshake" matches pool concept "TCP connection establishment".
     // FAILS R0q1: profile topic "congestion control" does NOT match pool concept "flow control" — adjacent, distinct mechanisms.
R0q2. IF a profile topic matches no pool entry THEN record it as an UNCOVERED TOPIC and report it. Generate nothing for it and write nothing to the file.
R0q3. IF an uncovered topic plausibly belongs to a chapter that has no questions file (R0o4) THEN say so by name in the report and name the command that would fix it.
     // Example: "Uncovered: 'distance-vector routing' (week3 deck, slide 14). Chapter 5 has a slice but no questions file — run `/generate_questions chapter5`, then re-run `/generate_questions week3`."
R0q4. IF one profile topic matches several pool entries THEN select ALL of them. Do NOT pick one and do NOT cap the count.
R0q6. Selection is per-run and stateless. A pool entry selected into week 2 is fully eligible for week 5 as well. Do NOT deduplicate across weeks.

// Unit structure and copying
R0r. Units come from the POOL, not from the registry: one unit per origin chapter that contributed at least one selected entry, in ascending chapter order. N = the number of such chapters. The unit title is the origin chapter's own title.
     // Example: week 3 selects 8 entries from chapter 4 and 4 from chapter 5 → `## Unit 1 of 2 — Chapter 4: The Network Layer` and `## Unit 2 of 2 — Chapter 5: The Link Layer`.
R0r1. Order entries within a unit by their original order in the origin chapter file.
R0r2. Copy each selected entry VERBATIM — `Concept:`, `Source quote:`, `Teach:`, `Teach_EN:`, `Question:`, `Question_EN:`, `Tests:`, `Answer key:`, `Elaboration:`, `Audit:` — every field it carries, byte for byte, including fields this skill no longer writes.
R0r3. Do NOT rewrite, reword, shorten, reformat, re-translate, or re-audit a copied entry.
R0r4. Add exactly three fields to each copied entry, placed immediately after `Concept:`:
     - `Origin: chapter<N> Q<n>` — the origin file and the entry's number IN that file.
     - `Origin generated: <the origin file frontmatter `generated:` date>`
     - `Origin fingerprint: <SHA-256 of the exact origin entry bytes>`
R0r5. Renumber copied entries sequentially within their unit — Q1, Q2, Q3. `Origin:` preserves the original number.

// Existing file — select branch of R5
R5a. IF this is a SELECT run THEN state the recommended operation and ask the user to choose `resync`, `reselect`, or `cancel`. STOP until user responds. The recommended operation is `resync` unless the week's registered material has changed since the file's `generated:` date or a new chapter has entered the pool, in which case it is `reselect`.

// Existing file: resync
R0s. RESYNC keeps the current selection and refreshes each copied entry from its origin. It does NOT reconsider which concepts are selected.
R0s1. For each copied entry, open the file named by its `Origin:` and calculate the SHA-256 fingerprint of the exact current origin entry bytes. IF it equals the entry's `Origin fingerprint:` THEN the entry is current; leave it byte-identical. For a legacy entry without an Origin fingerprint, compare every copied origin field byte-for-byte before declaring it current.
R0s2. IF the fingerprint differs, or the legacy field comparison differs, locate the origin entry by its `Concept:` field, NEVER by its Q number. Q numbers do not survive a regeneration.
R0s3. IF the concept IS found in the regenerated origin file THEN replace every copied field with the current origin values, update `Origin:` to its new Q number, `Origin generated:` to the new date, and `Origin fingerprint:` to the current SHA-256, and report the entry as REFRESHED. R5k6 overrides this rule for `Source quote:` only: an entry that lacked that field retains no such field during resync.
R0s4. IF the concept is NOT found in the regenerated origin file THEN keep the copied entry exactly as it stands, rewrite its `Origin:` field to `chapter<N> Q<n> — ORPHANED`, and report it.
R0s5. IF an origin chapter questions file no longer exists at all THEN every entry copied from it is ORPHANED under R0s4.
R0s7. IF a resync refreshes nothing and orphans nothing THEN write NOTHING. Report no change and stop.

// Existing file: reselect
R0t. RESELECT discards the existing file, rebuilds the coverage profile and the selection from scratch, and writes the result as a first run.
R0t1. IF the existing file holds any ORPHANED entry THEN warn the user by name that a reselect drops those entries, and STOP until they respond.
R0t3. A reselect does NOT modify any chapter questions file. IF the user wants a pool entry itself changed THEN that is a book-run `regenerate` under R5a1, or a hand edit. Say so.

// Legacy entries
R5k6. Do NOT add a `Source quote:` to an entry that lacks one — not when copying it under R0r2, and not when refreshing it under R0s3. R18b3 skips such entries.
R5k7. IF the user asks for the field to be added to a legacy entry THEN that is a book-run `regenerate` under R5a1, followed by a select-run `resync`. Say so and let them choose.

// Contents entry
R24a3. A select file's Contents description MUST say it is a selection and name its origin chapters.
     // Example: `- week3/questions_week3.md — week 3 practice set: 12 questions selected from chapters 4–5`

// Frontmatter and per-entry metadata
R24h1. On a SELECT run the frontmatter `source:` field lists the textbook chapter SLICES the selected entries were originally generated from. It does NOT list the registered class files.
     // Commentary: verify_quotes.py resolves this field and searches it for every `Source quote:`. Listing the slide decks here would make R24k fail every quote in the file.
R24h2. On a SELECT run additionally write `pool:` — one line per origin chapter questions file, each with the `generated:` date this run read from it.
R24h3. On a SELECT run additionally write `coverage_source:` — every registered `### Teaching` file read to build the coverage profile, comma-separated. Documentation only, never resolved.
R24i1. On a SELECT run R24i is satisfied by COPYING, not by writing: R0r2 carries `Concept:` and `Source quote:` over unchanged from the pool entry. R5k6 governs an entry that has no quote to copy.
R24i2. On a SELECT run every entry additionally carries `Origin:`, `Origin generated:`, and `Origin fingerprint:` per R0r4.

// Mechanical verification — select specifics
R24k4. IF a SELECT questions file is written on a first selection, resync, or reselect THEN run `python3 <skill dir>/verify_quotes.py --legacy <output path>`.
R24k4a. IF the legacy verifier reports a missing quote match or a malformed copied quote field THEN re-copy the named entry verbatim from its origin under R0r2.
R24k4a1. IF an entry is re-copied under R24k4a THEN re-run the verifier.
R24k4a2. IF R24k4a applies THEN do NOT edit the chapter file.
R24k4b. IF the R24k4a1 re-run still fails THEN report the bad pool entry.
R24k4b1. IF reporting a bad pool entry under R24k4b THEN name its chapter and Q number.
R24k4b2. IF reporting a bad pool entry under R24k4b THEN tell the user to regenerate that chapter.
R24k4c. IF the legacy verifier reports zero checked quote fragments THEN stop the SELECT run.
R24k4c1. IF the SELECT run stops under R24k4c THEN report that the file contains no verifiable provenance.
R24k4d. IF the legacy verifier finds an entry with no `Source quote:` field THEN skip it under R18b3.
R24k4d1. IF the legacy verifier skips entries under R24k4d THEN report their count.

## Output Format — select run

Same entry fields as the book format in `book.md`, all copied verbatim from the pool (R0r2). Differences:

- Frontmatter: `kind: select`, `source:` lists textbook SLICES not class files (R24h1), adds `pool:` (R24h2), `coverage_source:` (R24h3), and `model:`/`effort:` (R24h4).
- Each entry adds `Origin: chapter<N> Q<n>`, `Origin generated: <date>`, and an `Origin fingerprint: <SHA-256>` after `Concept:` (R0r4). An orphaned entry reads `Origin: chapter<N> Q<n> — ORPHANED` (R0s4).
- Units = one per origin chapter that contributed entries, in ascending chapter order (R0r). Entries renumbered within each unit (R0r5).

## Notes

A select run reads the `### Teaching` entries registered to that week — slide decks, handouts, labs,
code, images alike — for one purpose only: to learn which topics the professor covered. It generates
nothing from them. It then copies the pool questions matching those topics into the week file, which
is the study list.

Because it selects rather than generates, a terse slide costs nothing: a slide reading only
"Nagle's algorithm" is a perfect coverage signal, and the book supplies the depth — R0n2 imposes no
depth requirement.

A roadmap or agenda slide is the exception. R0n2a keeps it out of the profile: naming a topic in a
"what we will cover" list promises future coverage rather than delivering it. R0n2b readmits the
enumeration whose items carry their own definitions, because there the list is the lesson. The
distinction is whether the slide teaches the topic or merely announces it.

Re-running a week offers two operations:
- `resync` — keep the same selection, refresh each copy from its origin chapter. Use after
  regenerating a chapter.
- `reselect` — rebuild the selection from scratch. Use after new material is registered to the week.

If the professor covered something the book has no question for, it is reported as an UNCOVERED
TOPIC and nothing is invented to fill it.
