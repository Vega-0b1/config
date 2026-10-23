# generate-questions — LECTURE run rules

Loaded under R0k2 when the argument names a registered lecture deck (R0k5). These rules GENERATE
audited conceptual questions from one lecture deck's slides and write them next to the deck's
extracted notes. The deck is the only source: the textbook is not read.

Read this together with the shared core in `SKILL.md` and the rules `book.md` lends it under L1.
Rule IDs are global across all rule files.

## Rules — lecture run

// Rules borrowed from book.md
L1.  IF this is a LECTURE run THEN apply these book.md rules: R9a (images are not a source), R10–R11j (Teach content and formatting), R12–R12b and R16 (standalone sufficiency), R12c–R12g1 (concept inventory, as adapted by L5–L5c), R12m (inventory is internal), R12n1–R12n2 (core ranking), R12n5, R12t–R12t11 (curated adoption), R13, R13b–R13c, R13e–R16e (question generation and answer key), R16f–R16i (translation, per L4), R17–R23a (audit and retries), and F1–F7 (format 2).
L1a. IF this is a LECTURE run THEN skip every book.md rule L1 does not name: no Source Profile, no course-scope notice, no chapter loading, no visual repair, no figure gate, no diagram attachment, no exercise classification, no inventory-gap check, no `practice_<arg>.md`, and no `Type: problem` entry.
L1b. IF a borrowed rule names a BOOK run, a chapter, or the chapter's notes THEN read it as naming this LECTURE run, the deck, and the deck slice.
L1c. IF a borrowed rule names the fixed 25-entry maximum THEN read it as CAP (L7).

// Decks
L2.  A DECK HEADING is a level-1 heading (`# <text>`) whose next heading line is `## Slide 1`, in a file listed under `### Teaching` in the class root's `## Instructor Material`.
L2a. A DECK ID is the first whitespace-delimited token of a deck heading's text.
     // Example: `# mitm (lecture deck: Man-in-the-middle Attack)` → `mitm`. `# lec13_dijkstra` → `lec13_dijkstra`.
L2b. A DECK SLICE runs from its deck heading to the line before the next level-1 heading whose next heading line is `## Slide 1` or `## Page 1`, or to the end of the file.
     // Commentary: a `# ` line inside a code listing (`# tcpdump -i eth0 -n`) is followed by no `## Slide 1`/`## Page 1`, so it neither starts nor ends a slice.
L2c. IF a registered file holds exactly one deck heading THEN its FILE ALIAS is the file's stem with any trailing `_notes` removed.
     // Example: `ch1_introduction.md` holding `# ch1_introduction_1` → alias `ch1_introduction`.
L2d. Do NOT treat a registered file without a deck heading as a deck. Handouts, homework, lab manuals, assignment specs, and code files are never a LECTURE run source.

// Resolving the argument
L3.  Match the argument, case-insensitively, against every DECK ID and FILE ALIAS in the registry, in this order, and stop at the first step that matches anything: (a) an exact DECK ID; (b) an exact FILE ALIAS; (c) a DECK ID that begins with `<argument>_`.
     // Example: `lec13` matches `lec13_dijkstra` under (c).
L3a. IF exactly one deck matches THEN that deck slice is the source.
L3b. IF several decks match at the first matching step THEN list their DECK IDs with their files and ask the user which deck. STOP until user responds.
L3c. IF no deck matches AND the argument names a registered file without a deck heading THEN stop and tell the user: "<file> is not a slide deck; lecture runs read slide decks only."
L3d. IF no deck matches AND L3c does not apply THEN stop, list every DECK ID in the registry, and tell the user to register a new deck with `/updateclass` first.
L3e. IF the registry holds no deck at all THEN stop and tell the user that no lecture deck is registered; register one with `/updateclass`.

// Language
L4.  Detect the language of the deck slice. IF it is not `en` THEN R16f–R16g apply; IF it is `en` THEN R16i applies.

// Concept inventory — slide adaptation of R12d–R12f
L5.  A concept belongs in the inventory IF AND ONLY IF at least one slide in the deck slice carries text that explains a mechanism, states a contrast, describes a scenario, defines the concept, or gives its algorithm or steps.
     // PASSES: slide 9 prints Dijkstra's loop, including `D(v) = min( D(v), D(w) + c(w,v) )` → "Dijkstra's distance update" enters.
     // FAILS:  an outline slide listing `4.6 routing in the Internet` / `RIP` / `OSPF` → nothing enters.
L5a. IF a slide ONLY lists a topic by name inside an outline, agenda, roadmap, or "what we will cover" list THEN that topic does NOT enter the inventory.
L5b. L5a does NOT apply when the list is the lesson itself — each item carries its own definition or explanation.
L5c. Exclude deck chrome from the inventory and from every quote: the deck heading, a slide's echoed title line, the repeated footer (deck or chapter name, page-number placeholder such as `4-<number>`), title slides, and copyright or usage-notice slides.
L5d. IF L5 admits a concept THEN record the slide line(s) that satisfy it, verbatim per R12e1, as that concept's R12e quote. A quote never joins lines that are separate lines in the slice; record each as its own fragment per R13g1.
L5e. IF a slide's text is only a worked numeric table or graph labels with no explanatory line THEN it supports no concept by itself.
L5f. IF a slide poses a computational exercise ("use Dijkstra's algorithm to calculate…") THEN write no entry for it and report it.
     // Commentary: `/generate-questions <deck> problems` turns these slides into checked problem entries (problems.md P2f).

// Core selection
L6.  IF beginning question planning THEN read the entire deck slice and build its inventory, including R12g1 deduplication, before selecting concepts or writing any candidate.
L6a. Rank eligible concepts per R12n1–R12n2 and select the highest-ranked concepts, up to CAP (L7).
L6b. The deck slice is ONE unit. Write it as `## Unit 1 of 1 — <DECK ID>`.

// Cap
L7.  CAP = 25 unless the argument carries a `cap<N>` token (R0k1a), in which case CAP = N.
L7a. IF preparing to save THEN count all PASS entries; IF more than CAP remain THEN keep one highest-priority entry per selected concept first, fill remaining slots by R12n2 priority, and re-audit retained entries before saving.
L7b. Generate fewer than CAP when fewer eligible concepts or passing questions exist. Do NOT pad.

// Existing file — lecture branch of R5
L8.  IF this is a LECTURE run AND the output file exists THEN warn the user and ask whether to `regenerate` or `cancel`. STOP until user responds.

// Frontmatter
L9.  IF saving THEN write `source:` as the deck's registered file name, relative to the questions file's directory, and `deck: <DECK ID>`.
L9a. IF saving THEN write `cap: <CAP>`.
     // Commentary: verify_quotes.py checks quotes against the whole registered file. A file holding two decks lets a quote from the other deck pass; L5d keeps every quote inside this deck slice.

// Contents entry
L10. A lecture file's Contents description MUST name the deck, the question count, and the slide count of the deck slice.
     // Example: `- lectures/questions_lec13_dijkstra.md — lec13_dijkstra questions: 9 questions generated from 14 slides`

// Report
L11. IF reporting a LECTURE run THEN also report: the deck resolved and its file, the slide count, every slide excluded as chrome or roadmap under L5a–L5c (as a slide-number list), every computational exercise skipped under L5f, and whether CAP bound the selection.

## Output Format — lecture run

Same entry fields and Format 2 rules F1–F7 as `book.md`, except:

- Frontmatter: `name: questions_<DECK ID>`, `source:` per L9, `deck: <DECK ID>`, `generated:`, `kind: lecture`, `format: 2`, `cap:`, `model:`, `effort:`.
- One unit: `## Unit 1 of 1 — <DECK ID>` (L6b).
- No `Figure source`, `Figure quote`, `Diagram`, `Answer diagram`, `Type`, `Legend` given-values block for a problem, or `Check` field.
- `Source quote:` fragments are verbatim slide lines, one fragment per slide line, separated by blank lines.

```
---
name: questions_lec13_dijkstra
source: lec13_dijkstra_notes.md
deck: lec13_dijkstra
generated: <today's date>
kind: lecture
format: 2
cap: 25
model: <model ID>
effort: <reasoning effort level>
---

## Unit 1 of 1 — lec13_dijkstra

#### Q1
Concept: ...
Source quote: <slide line>

  <slide line>
Teach:
  ...
Question: ...
Tests: ...
Answer key: ...
Audit: PASS — ...
```

## Notes

A lecture run is a book run pointed at one slide deck instead of a textbook chapter. Slides are
terse, so L5 admits a concept on a definition, an algorithm, or a list of steps, not only on an
explanatory sentence — but every Teach field is still audited against the slide lines it quotes
(R18b), so a terse slide yields a short Teach, never one padded from the textbook.

The deck is named by its DECK ID — the first word of its `# ` heading in the extracted notes —
or by its file name without `_notes`, or by any unambiguous prefix ending before an underscore:
`lec13` and `lec13_dijkstra` name the same deck. A prefix that reads as a chapter (`ch4`) is
always a book run (R0l); name such a deck in full (`ch4_req_eng`). A file that holds two decks
(`wk5_notes.md`) yields two DECK IDs, one per lecture.

Homework, assignment specs, lab manuals and code are registered teaching material but never a
lecture-run source (L2d).
