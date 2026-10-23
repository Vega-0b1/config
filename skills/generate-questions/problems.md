# generate-questions — PROBLEMS run rules

Loaded under R0k2 when the argument carries the `problems` mode token (R0k4, R0k4c). These rules
turn every computational exercise in a textbook chapter's section exercise sets (P2j), or every
computational problem a lecture deck prints, into a checked problem entry. A CHAPTER PROBLEMS run writes `problems_chapter<N>.md` next to the chapter slice; a DECK
PROBLEMS run writes `problems_<DECK ID>.md` next to the deck's extracted notes. There is no cap and
no concept selection: the file is a drill set, not a study pool.

Read this together with the shared core in `SKILL.md`, the rules `book.md` lends it under P1 and
P1c, and on a deck run the rules `lecture.md` lends it under P1d. Rule IDs are global across all
rule files.

## Rules — problems run

// Rules borrowed from book.md — chapter source
P1.  IF this is a CHAPTER PROBLEMS run THEN apply these book.md rules: R0–R0j3 (Source Profile, course scope), R1–R4a (file loading), R4b–R4b6 (visual repair), R5a1 (existing file), R6–R6f (figure gate), R7–R9 (unit segmentation), R9a–R9p3 and R9o–R9o3 (figures), R10–R11j (Teach content and formatting), R12–R12b and R16 (standalone sufficiency), R12e1–R12e2 and R13g–R13g1 (verbatim quoting and the `Source quote:` field), R18a–R18b2 (source grounding), R20 (terms defined), and F1–F7 (format 2).
P1a. IF this is a PROBLEMS run THEN skip every book.md rule P1 does not name: no concept inventory, no core selection, no curated-question adoption, no conceptual question, no question-type quota, no exercise classification, no `practice_<arg>.md`, and no 25-entry maximum.
P1b. IF a borrowed rule names a BOOK run THEN read it as naming this PROBLEMS run.

// Rules borrowed — deck source
P1c. IF this is a DECK PROBLEMS run THEN apply these book.md rules: R5a1 (existing file), R9a (images are not a source), R10–R11j (Teach content and formatting), R12–R12b and R16 (standalone sufficiency), R12e1–R12e2 and R13g–R13g1 (verbatim quoting and the `Source quote:` field), R16f–R16i (translation, per L4), R18a–R18b2 (source grounding), R20 (terms defined), and F1–F7 (format 2).
P1d. IF this is a DECK PROBLEMS run THEN apply these lecture.md rules: L2–L3e (deck resolution), L4 (language), L5c (deck chrome), and L9 (`source:` and `deck:` frontmatter).
P1e. IF this is a DECK PROBLEMS run THEN skip every book.md and lecture.md rule P1c–P1d do not name: no Source Profile, no course-scope notice, no chapter loading, no visual repair, no figure gate, no concept inventory, no conceptual question, no `practice_<arg>.md`, no CAP, and no `cap:` frontmatter line.
P1f. IF this is a DECK PROBLEMS run THEN write no `Figure source`, `Figure quote`, `Diagram`, or `Answer diagram` field. A slide image has no verified registry entry (R9d), so P2c and P3e treat every slide figure as unverified.
P1g. IF a borrowed rule or a rule in this file names a book, a chapter, the chapter's notes, or "the author" THEN on a DECK PROBLEMS run read it as naming the deck, the deck slice, or the slide's wording.
P1h. P1a's skip list applies to both kinds of PROBLEMS run.

// Problem inventory
P2.  IF this is a CHAPTER PROBLEMS run THEN list every PROBLEM SOURCE in the chapter: each numbered exercise inside a SECTION EXERCISE SET that asks for a computed result.
P2j. A SECTION EXERCISE SET is the block of numbered exercises printed at the end of one numbered section under its own heading (`1.1 EXERCISES`, `Exercises 2.3`).
P2k. IF a chapter problems run meets a worked Example, a Learning Assessment, a chapter review (its exercises, concept check, or true-false quiz), or a problem-solving or "Problems Plus" set THEN write no entry for it. P2k overrides P2 and P3a for chapter runs.
     // Example: Stewart chapter 1 → entries come only from 1.1 Exercises through 1.6 Exercises; Example 3, Chapter 1 Review, and Principles of Problem Solving are left out.
P2l. Do NOT report the items P2k excludes; they are out of scope, not skipped parts.
P2i. A COMPUTED RESULT is a number, an expression or formula, a set or interval, a point, or a classification the problem asks the reader to determine (`even`, `one-to-one`, `Yes`).
     // Example: "Find the domain of f(x) = x/(3x - 1)" asks for a set; "Determine whether f is even, odd, or neither" asks for a classification. Both are problem sources.
P2f. IF this is a DECK PROBLEMS run THEN list every PROBLEM SOURCE in the deck slice: each slide that poses a computational exercise (lecture.md L5f) and each slide that works a computational example.
     // Example: lec13_dijkstra slide 11 ("Use Dijkstra's algorithm to calculate the shortest path from source node "u"") is an exercise; slide 10 ("Dijkstra's algorithm: example") is a worked example.
P2g. IF a later slide prints the solution to an earlier slide's exercise THEN the two slides are ONE problem source, located by the exercise slide.
     // Example: slide 12 prints the table that solves slide 11 → one problem source, `Slide 11`.
P2h. IF a slide's text is only an implementation or programming task with no single computed value THEN write no entry for it and report it under P2b.
P2a. IF a problem source has lettered or numbered parts OR asks for several values THEN each part asking for one value is its own problem entry.
     // Example: Example 1.9 part 1 asks for recharge time AND stored charge → two entries; part 2 asks for charge left AND energy → two more.
P2b. IF a part asks for no computed value (a connection, a sketch, an explanation) THEN write no entry for that part and report it.
P2c. IF a problem source's setup depends on a figure without a verified registry Question image (R9d) AND the setup cannot be stated completely in `Question:` and `Legend:` THEN write no entry for it and report it.
P2d. Order entries in document order within each unit, one unit per unit heading (R7–R8).
P2d1. IF this is a DECK PROBLEMS run THEN the deck slice is ONE unit, written `## Unit 1 of 1 — <DECK ID>`, with entries in slide order. P2d1 overrides P2d.
P2e. IF a unit contains no problem source THEN keep its unit heading with a one-line note that it has no computational problem.

// Answer source
P3.  IF the source prints the final answer for a part THEN record `Origin: curated — <locator>` and use the printed answer as the Answer key value.
P3a. IF a worked Example prints its solution THEN its final value counts as a printed answer under P3.
P3b. IF the source prints no answer for a part THEN solve it and record `Origin: solved — <locator>`.
     // Commentary: books that answer only odd or even exercises still print the unanswered ones as practice; P3b keeps them in the drill set.
P3c. IF writing a solved entry THEN solve it twice: once to write `Elaboration:`, and again under R18c from Teach, Legend, Diagram, and Question alone.
P3d. IF the two P3c solutions disagree THEN drop the entry and report it.
P3e. IF a solved entry needs a value the source does not state AND no verified Diagram shows it THEN drop the entry and report it.
P3f. P3 overrides P3b: a part whose answer is printed anywhere in the source — beside the problem, in an answer appendix, in the Example's solution, or on a later solution slide (P2g) — is curated, never solved.
P3g. IF a locator carries a part THEN name the part in it — `E1.4(a)`, `Example 1.9, part 1 (stored charge)`, `Slide 11 (least cost to z)`.
P3h. IF this is a DECK PROBLEMS run THEN a locator names the slide by its `## Slide N` anchor — `Slide 10`, never a page or footer number.

// Problem entry wording and fields
R13q2. IF a book problem is used THEN preserve the author's wording in `Question:`.
     // Example: `Origin: curated — E1.4(a)` with `Question: Determine the power supplied by the dependent source in Fig. E1.4(a).`
R13q2a. IF a book problem has several lettered parts or asks for several values THEN each entry uses exactly one part asking for one value, and names that part in `Origin:` and in `Question:`.
R13q2b. IF an entry uses only one part AND the author's setup carries a condition that only another part needs THEN drop that condition from `Question:` and keep the rest of the author's wording. R13q2b overrides R13q2 for the dropped condition only.
     // Example: Example 1.9 asks for recharge time AND stored charge. Using only the stored-charge part, "has been fully discharged" serves only the recharge-time part, so the Question reads "How much charge is stored in a 1000 mAh lithium-ion battery when it is fully charged?"
R13q3. IF writing a curated entry THEN `Source quote:` MUST carry the problem statement and its printed answer, each verbatim per R12e1–R12e2, in addition to the sentences Teach is built from (R13g1).
R13q3a. IF writing a curated entry THEN express the `Answer key` and `Check:` values in the unit and form of the printed answer.
R13q3b. IF writing a solved entry THEN `Source quote:` carries the problem statement verbatim per R12e1–R12e2, plus the sentences Teach is built from.
R13q5. IF writing a problem entry THEN record `Type: problem` as its first field and `Origin:` as its second.
R13q6. IF writing a problem entry THEN its `Concept:` names the chapter concept the problem computes with, worded as a BOOK run would word that concept. On a DECK PROBLEMS run it names the deck concept, worded as a LECTURE run would word it.
R13q7. A PROBLEMS run never writes a generated variant. Every entry is a problem the book or deck prints.
R13q8. IF a deck problem's slide text is a heading or fragment rather than a sentence THEN `Question:` keeps the slide's wording and adds only the words needed to ask for the one value the entry names. R13q8 overrides R13q2 for the added words only.
     // Example: slide 11 "Use Dijkstra's algorithm to calculate the shortest path from source node "u"" → entry for z reads "Use Dijkstra's algorithm to calculate the least cost of the shortest path from source node u to node z."
R13r. IF writing a problem entry THEN its `Teach:` carries the formula(s) with a symbol Legend per R11, then the solution method as a numbered list per R11c.
R13r0. A problem entry's `Teach:` MUST NOT contain that problem's own given values or its result.
R13r0a. IF the entry comes from a worked Example THEN its `Teach:` MUST NOT reproduce the Example's printed solution steps with their values.
R13r1. IF writing a problem entry THEN its `Legend:` field carries the given values, one value statement per sentence, its first line not beginning with `- **`.
R13r1a. IF every given value is stated in `Question:` or shown in `Diagram:` THEN omit `Legend:`.
     // Commentary: /learn displays a `Legend:` whose first line does not begin with `- **` as a separate 📋 Given block (learn R8f–R8f2).
R13r2. A problem entry's `Question:` asks for exactly one quantity, as one question or one imperative sentence ("Find …", "Determine …").
R13r3. A problem entry's `Answer key:` states the final result — a value with its unit, or the expression, set, point, or classification — in one sentence of at most 25 words.
R13r4. A problem entry MUST carry `Elaboration:` holding the full solution as a numbered list, one step per line, ending at the Answer key value. R13r4 overrides R16e.
R13r5. IF a problem entry's result is a single number THEN it MUST carry `Check:` in the form `<expression> == <value>`: an arithmetic expression reproducing the solution's computation, then the final value exactly as `Answer key:` shows it.
R13r5b. IF a problem entry's result is not a single number — an expression, formula, set, interval, point, list of several values, or classification — THEN write `Check: none`.
R13r5c. Do NOT write `Check: none` on an entry whose result is a single number. R13r5c overrides R13r5b.
     // Commentary: /learn grades nothing; Check exists to catch errors in the answer key itself. A non-numeric result has no single number to evaluate, so its only check is the R18c independent re-solve, which applies to every entry.
R13r5a. IF writing a `Check:` expression THEN use only numbers, `+ - * / **`, parentheses, `pi`, `e`, and the functions `verify_problems.py` allows.
R13r5d. IF the printed answer is rounded more coarsely than the 0.5% Check tolerance THEN wrap the computation in `round(<expression>, <digits>)` matching the printed precision.
     // Example: `Check: (2.5 / 4) * (1 - exp(-4 * 0.25)) * 1000 == 395.1` for an energy integral answered in mJ.
R13r6. IF auditing a problem entry THEN replace conceptual-answer rules R11a, R11a1, R11b, R15, R15a, R15d–R15f, R16a, R16b, R16e, R17, R18, and R19 with R13r–R13r5a and R18c–R18c4a; the result must be derivable, not printed in Teach.
R13r7. IF auditing a problem entry THEN retain every other entry rule P1 borrows, including source grounding R18a–R18b2 and standalone sufficiency R12/R16; R13r6 overrides any conflicting conceptual-answer requirement.

// Audit (per entry)
R18c. IF auditing a problem entry THEN solve it a second time from its Teach, Legend, Diagram, and Question alone, without reading its Elaboration, Answer key, or Check.
R18c1. IF the R18c result differs from the Answer key value THEN mark FAIL with reason "solution does not reproduce".
R18c2. IF a curated entry's Answer key value differs from the printed answer in its Source quote THEN mark FAIL with reason "answer differs from the book" (on a DECK PROBLEMS run: "answer differs from the slides").
R18c3. IF a problem entry's Teach field states that problem's given values or its result THEN mark FAIL with reason "answer leaked into Teach — R13r0".
R18c4. IF a problem entry's Question asks for more than one quantity THEN mark FAIL with reason "compound problem — use one part per R13q2a".
R18c4a. IF a problem entry's Question or Legend states a condition or value that the R18c solution never uses THEN mark FAIL with reason "unused setup — drop it per R13q2b".
P4.  IF an entry is not marked FAIL by R18a–R18b2, R18c–R18c4a, or R20 THEN mark PASS.
P4a. IF an entry is marked FAIL THEN repair it once against the source and re-audit it.
P4b. IF the repaired entry fails again THEN drop it and report it with its fail reason. No substitute problem is written.

// Catch-all
P5.  IF any condition not covered by P1–P4b (including lettered sub-rules) or the borrowed rules arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Output Format — problems run

```
---
name: problems_<arg>
source: <notes filename>
generated: <today's date>
kind: problems
format: 2
model: <model ID>
effort: <reasoning effort level>
---

## Unit 1 of N — <Unit Title>

#### Q1
Type: problem
Origin: curated — <locator>   ← or `solved — <locator>` when the book prints no answer (P3b)
Concept: <the chapter concept the problem computes with (R13q6)>
Source quote: <problem statement, printed answer when curated (R13q3/R13q3b), plus Teach's sentences>
Figure source: <class-root-relative-registry>#<figure-id>  ← optional diagram provenance
Figure quote:
  <supporting Description sentence(s), verbatim; omit with no attachment>
Teach:
  <formula(s), symbol Legend (R11), numbered solution method — none of this problem's values (R13r0)>
Question: <the author's wording, asking for exactly one quantity (R13q2, R13r2)>
Diagram: ![Figure <number>](<class-root-relative-PNG>)  ← optional question image
Legend: <given values, one statement per sentence — shown as 📋 Given; omit per R13r1a>
Tests: <one-line description of the computation being tested>
Answer key: <final result: value with unit, or expression/set/classification — one sentence (R13r3)>
Elaboration:
  <numbered solution steps, ending at the Answer key value (R13r4)>
Check: <expression> == <value as shown in Answer key>   (R13r5) — or `none` for a non-numeric result (R13r5b)
Audit: PASS — <the R18c independent re-solve result>

## Unit 2 of N — <Unit Title>

#### Q2
<same entry structure — numbering does NOT restart at a unit boundary (F4)>
```

## Output Format — deck problems run

Same entry fields as the chapter format above, except:

- Frontmatter: `name: problems_<DECK ID>`, `source:` and `deck:` per L9, `generated:`, `kind: problems`, `format: 2`, `model:`, `effort:`. No `cap:` line.
- One unit: `## Unit 1 of 1 — <DECK ID>` (P2d1).
- No `Figure source`, `Figure quote`, `Diagram`, or `Answer diagram` field (P1f).
- `Origin:` locators name slides (P3h). `Source quote:` fragments are verbatim slide lines, one fragment per slide line, separated by blank lines.

```
---
name: problems_lec13_dijkstra
source: lec13_dijkstra_notes.md
deck: lec13_dijkstra
generated: <today's date>
kind: problems
format: 2
model: <model ID>
effort: <reasoning effort level>
---

## Unit 1 of 1 — lec13_dijkstra

#### Q1
Type: problem
Origin: curated — Slide 11 (least cost to z)
...
```

## Notes

A chapter problems run reads the same chapter slice as a book run and writes
`problems_chapter<N>.md` beside `questions_chapter<N>.md`. A deck problems run reads the same deck
slice as a lecture run and writes `problems_<DECK ID>.md` beside `questions_<DECK ID>.md`. Either
file holds every computational problem in its scope — a chapter's section exercise sets, or a
deck's slides — one entry per part, in source order. A
part with a printed answer is curated and checked against that answer; a part without one is
solved twice and kept only when both solutions agree. `/learn chapter<N> problems` delivers a
chapter file and `/learn <deck> problems` a deck file.

A slide problem whose setup lives only in a drawing — a graph whose edges the extracted text does
not connect — is skipped under P2c, exactly as an unverified textbook figure is, because decks have
no figure registry.
