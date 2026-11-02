---
name: code
description: Practice C/C++ problems on two tracks, `leet` (interview deck) and `clrs` (CLRS textbook algorithms), in normal or low-energy (easy) mode, with a PREVIOUS/CURRENT/NEXT lane tracker and a technical debrief in normal mode. Invoked as `/code leet`, `/code clrs`, `/code leet easy`, or `/code clrs easy`.
---

Problems are stored in one file per track in the current working directory. The user solves each problem in C/C++, drawn from the ACTIVE TRACK's file (the ACTIVE DECK).

## Mode

R1. IF the skill is invoked with `easy` among its arguments, alone or joined to a track name (`leet_easy`, `clrs_easy`), THEN set the ACTIVE MODE to EASY.
R2. IF the skill is invoked without `easy` among its arguments THEN set the ACTIVE MODE to NORMAL.
R3. IF either invocation occurs while a problem is active AND the track chosen per Track R1–R2 is the ACTIVE TRACK THEN keep that problem active and apply the new mode from that point forward.
R4. IF either invocation occurs while no problem is active THEN treat the invocation as a request for the next problem in the selected mode and track.
R4a. IF either invocation occurs while a problem is active AND the track chosen per Track R1–R2 differs from the ACTIVE TRACK THEN apply Track R5.
R5. IF no active mode has been set in the session THEN set the ACTIVE MODE to NORMAL.
R6. IF the user asks which mode is active THEN state it in one line.
R7. IF any condition not covered by R1–R6 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Track

The user solves every problem in C/C++: C as the primary language, with C++ used where its tooling helps. There are two tracks. Each track has its own file, lanes, `last:` dates, answer keys, and curriculum order, and its completions are recorded only in its own file.

R1. IF the skill is invoked AND its arguments name a track (`leet` or `clrs`) THEN set the ACTIVE TRACK to that track without asking.
     // Example: `/code leet` → NORMAL, LEET.  `/code clrs easy` → EASY, CLRS.  `/code leet_easy` → EASY, LEET.
R2. IF the skill is invoked AND its arguments name no track THEN ask in one line which track, `leet` or `clrs`, and wait. Select no problem until the user answers.
R3. IF the ACTIVE TRACK is set THEN set the ACTIVE DECK to that track's file per R7, and read and write lane state only in the ACTIVE DECK.
R4. IF Check returns correct THEN apply the completion path for the ACTIVE MODE.
R5. IF the user names the other track while a problem is active THEN leave that problem's entry in its file unchanged, set the ACTIVE TRACK and ACTIVE DECK to the named track, state the switch in one line, and select a problem from the new file per Problem Selection.
     // Commentary: tracks are independent. The old problem is neither completed nor recorded; if it was `[~]`, it stays `[~]` and is presented again the next time that track is used.
R5a. IF an argument is neither a track name nor `easy` THEN state in one line that the tracks are `leet` and `clrs` and leave the ACTIVE TRACK unchanged.
R6. IF the user asks to move on THEN apply Workflow R4.
R7. IF resolving the active track to a file, file extension, or run command THEN use this table:

| Track | Argument | ACTIVE DECK | Extension | Run command (from the scratchpad copy) |
|---|---|---|---|---|
| LEET | `leet` | `decks/c.md` | `.cpp` | `g++ -std=c++17 -Wall -Wextra -o prog FILE && ./prog` |
| CLRS | `clrs` | `CLRS.md` | `.cpp` | `g++ -std=c++17 -Wall -Wextra -o prog FILE && ./prog` |

R8. IF the user asks which track is active THEN state the track and the ACTIVE DECK in one line.
R9. IF the ACTIVE DECK file does not exist THEN stop, name the missing file, and ask how to proceed.
R10. IF any condition not covered by R1–R9 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Problem Selection

There are three lanes per track, identified by the entry's marker in the ACTIVE DECK:

| Lane | Marker | Meaning | Fields |
|---|---|---|---|
| PREVIOUS | `[x]` | completed; the easy lane | `(last: D)` |
| CURRENT | `[~]` | actively being worked | none |
| NEXT | none | unattempted | none |

EASY mode draws only from PREVIOUS. NORMAL mode draws from CURRENT, promoting from NEXT when CURRENT is empty.

R1. IF selecting any problem THEN read the problem list and lane markers from the ACTIVE DECK only. Markers in the other track's file do not affect selection, except that `CLRS.md` markers affect LEET concept counting as R3h allows.
R2. IF the ACTIVE MODE is NORMAL AND CURRENT holds one or more problems THEN select the earliest CURRENT problem in curriculum order.
R3. IF the ACTIVE MODE is NORMAL AND CURRENT is empty AND the ACTIVE TRACK is LEET THEN mark the NEXT problem chosen per R3a–R3i `[~]`, then select it.
R3a. IF R3 fires AND PREVIOUS is not empty THEN consider only NEXT problems whose solution reuses at least one concept PREVIOUS covers AND adds at most one concept PREVIOUS does not cover, counted per R12a, R12b, and R12d. R3a overrides R11.
     // Commentary: each new problem must build on what is already owned and add one step. An Easy label measures difficulty for someone who already owns the concepts, not the size of the step from PREVIOUS; set/clear/toggle/test a bit is Easy and still introduces four operators at once.
R3b. IF R3 fires AND no NEXT problem in the ACTIVE DECK satisfies R3a THEN present no problem. Name the closest candidate and the concepts it would add, propose one bridging problem that adds exactly one of them, and add that problem to the ACTIVE DECK only after the user says yes.
R3c. IF R3 fires THEN choose, among the NEXT problems admitted by R3a in the ACTIVE DECK, the problem with the smallest delta: the number of concepts its reference solution adds that PREVIOUS does not cover, counted per R12a, R12b, and R12d. R3c overrides R10–R13.
     // Example: PREVIOUS owns frequency counting. A Medium whose reference solution is pure frequency counting (delta 0) is chosen over an Easy that adds one look-ahead comparison (delta 1).
R3d. IF two or more problems tie under R3c THEN choose the one whose reference solution reuses the most distinct concepts PREVIOUS covers.
R3e. IF two or more problems remain tied after R3d THEN choose the one whose C/C++ reference solution has the fewest lines of code, counting non-blank lines of the solution body and excluding imports and the signature.
     // Example: Kth Largest Element in a Stream (a `std::priority_queue` min-heap trimmed to k, about 4 lines) is chosen over Top K Frequent Elements (a count map plus a heap, about 8 lines).
R3f. IF two or more problems remain tied after R3e THEN present no problem. List the tied problems with the concept each adds and the PREVIOUS concepts each reuses, and promote the one the user picks.
R3g. IF choosing a problem under R3c–R3f THEN do not use its deck position, its section, or its stated Easy, Medium, or Hard difficulty as a reason.
     // Commentary: Roman to Integer was once promoted because it was the first Easy entry in the deck among one-concept candidates. Deck order says where an entry was typed, not how far it sits from what is owned.
R3h. IF counting covered concepts under R3a–R3d or R12a THEN also treat as covered each concept implemented by a `[x]` entry in `CLRS.md` in the current working directory, subject to R3i.
R3i. IF a concept is covered only through `CLRS.md` AND no PREVIOUS problem's reference solution uses it AND the NEXT problem being counted is labeled Hard THEN count that concept as not covered for that problem. R3i overrides R3h and R3g.
     // Commentary: implementing an algorithm from the book's pseudocode is weaker evidence than applying it to an interview problem. One Easy or Medium deck problem must use the concept before it counts toward a Hard.
     // Example: CLRS chapter 6 heaps are `[x]` and no PREVIOUS problem uses a heap. Kth Largest Element in a Stream (Easy) counts the heap as covered (delta 0); Merge K Sorted Lists (Hard) counts it as new (delta 1). After Kth Largest in a Stream moves to PREVIOUS, Merge K Sorted Lists counts it as covered.
R3j. IF the ACTIVE MODE is NORMAL AND CURRENT is empty AND the ACTIVE TRACK is CLRS THEN mark the first NEXT entry in curriculum order `[~]`, then select it.
     // Commentary: the CLRS track is the book read front to back. R3a–R3i do not apply to it.
R4. IF R2 fires AND the problem presented most recently is still in CURRENT THEN select it again. Do not exclude it for having been presented.
     // Commentary: CURRENT is serial by design. A problem stays in front of the user until they answer `easy`, which is the only thing that moves it to PREVIOUS.
R5. IF the ACTIVE MODE is NORMAL AND CURRENT and NEXT are both empty THEN state that and present no problem.
R6. IF the ACTIVE MODE is EASY THEN select the PREVIOUS problem with the oldest `last:` date.
R7. IF the ACTIVE MODE is EASY AND PREVIOUS is empty THEN state that PREVIOUS is empty and present no problem.
R8. IF two or more PREVIOUS problems tie on `last:` THEN select the earliest one in curriculum order.
R9. IF the ACTIVE MODE is EASY THEN exclude the three most recently presented problems when another PREVIOUS problem exists. R9 overrides R6 and R8.
R10. IF ranking problems into curriculum order THEN place prerequisite problems before problems that build on them.
R11. IF two problems have no prerequisite relationship THEN place the problem with the lower stated Easy, Medium, or Hard difficulty first.
R12. IF two problems remain tied after R10–R11 THEN place the problem requiring fewer distinct concepts or state variables first.
R12a. IF counting distinct concepts under R12 THEN count only concepts the PREVIOUS lane does not already cover. A problem that reuses owned machinery counts as requiring none.
     // Commentary: this is what makes the order cumulative. Without R12a, a one-variable problem resting on an unsupported trick (Single Number's XOR cancellation) outranks a two-variable problem that is pure reuse of a PREVIOUS entry (First Unique Character over Valid Anagram's counter), which inverts the intent.
R12b. IF counting distinct concepts under R12 THEN count each language mechanic the solution depends on as a concept: character-code arithmetic, digit extraction with `%` and `/`, sign handling, integer-overflow edge cases, pointer casts, and each bitwise operator (`|`, `&`, `^`, `~`, shifts) separately. Do not count only named data structures and algorithms.
     // Example: with strlen, reverse a string, and memcpy in PREVIOUS: itoa counts four (digit extraction, `'0' + d`, sign, the most negative `int`); set/clear/toggle/test a bit counts four (shift, `|`, `&` with `~`, `^`); memmove counts one (copy direction when the regions overlap).
R12c. IF ranking NEXT problems under R10–R13 THEN rank every NEXT entry in the ACTIVE DECK against every other. Do not favor an entry for sitting in the same section as, or directly after, the problem completed last.
     // Commentary: itoa was once promoted for following memcpy in the deck while a one-concept problem earlier in the same section went unranked. Deck position never decides a NEXT promotion (R3g).
R12d. IF counting concepts under R3a or R12 THEN count the concepts of the problem's reference solution: the standard C/C++ solution an interviewer expects for that problem. Do not count a workaround that avoids the mechanics the problem exists to test.
     // Example: Swap byte order of a 32-bit integer was once promoted as zero new concepts by counting a memcpy-and-reverse workaround, then shown with shifts, `&`, and `|`. Its reference solution is shift-and-mask, which adds three concepts and fails R3a.
R12e. IF the user asks to see a solution THEN show the reference solution counted under R12d.
R13. IF two problems remain tied after R10–R12e AND the ranking is not a NEXT promotion under R3 THEN preserve their order in the ACTIVE DECK.
R13a. IF the ACTIVE TRACK is CLRS THEN curriculum order is the order of entries in `CLRS.md`. R13a overrides R10–R13.
R14. IF the user asks why a problem was selected THEN state the active mode, the ACTIVE TRACK, the ACTIVE DECK, the lane it came from, and its `last:` value when that field exists.
R15. IF the user names an Easy, Medium, or Hard difficulty while requesting a problem outside an invocation carrying the `easy` argument THEN ignore that filter and state that NORMAL mode follows CURRENT then NEXT while EASY mode means PREVIOUS.
R16. IF the user asks to add a named problem to CURRENT THEN mark that entry `[~]` in the ACTIVE DECK regardless of curriculum order.
R17. IF the ACTIVE MODE is EASY AND a problem is about to be presented THEN show a table of all PREVIOUS problems in the ACTIVE DECK with their Problem name and Last date before presenting the selected problem.
R18. IF the ACTIVE MODE is NORMAL AND a problem is about to be presented THEN show no table.
R19. IF any condition not covered by R1–R18 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Completion Tracking

Each PREVIOUS problem carries `(last: D)`. Every update in this section is written to the ACTIVE DECK only.
`last` is the most recent completion date in `YYYY-MM-DD` form. CURRENT and NEXT problems carry no tracking fields.

R1. IF a problem moves from NEXT to CURRENT THEN change its marker to `[~]` and add no tracking fields.
R2. IF the user answers `easy` THEN interpret it as "comfortable; move it to PREVIOUS."
R3. IF the user answers `keep` THEN interpret it as "not yet; leave it in CURRENT."
R4. IF the user answers `easy` at the end of a CURRENT problem THEN change its marker to `[x]` and set its fields to `(last: <today>)`.
R5. IF the user answers `keep` at the end of a CURRENT problem THEN change its entry in no way. It stays `[~]` with no fields, and the attempt is not recorded.
R6. IF a problem is completed in EASY mode THEN set `last:` to today's date. Its lane does not change.
R7. IF the user gives an answer other than `easy` or `keep` THEN ask for `easy` or `keep` before updating the tracker.
R8. IF a PREVIOUS problem lacks `last:` THEN stop and repair its entry before selecting or completing it.
R9. IF any entry carries `sets:` or `rating:` THEN delete those fields.
R9a. IF a CURRENT or NEXT entry carries `last:` THEN delete it.
     // Commentary: only PREVIOUS carries state. A field on a `[~]` or unmarked entry is stale data from an earlier schema, not a value to preserve.
R10. IF any condition not covered by R1–R9 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Problem Presentation

R1. IF presenting a problem THEN state only: the problem title, a prose description of the task, and example input/output pairs.
R2. IF presenting a problem THEN do not state a function name, parameter names, parameter types, type hints, or a return type.
R3. IF presenting a problem THEN do not name a data structure, algorithm, or technique in the description.
R4. IF presenting a problem THEN do not state a target time or space complexity.
R5. IF the problem's entry in the ACTIVE DECK names an algorithm as the assignment itself THEN that name may appear in the title; R5 overrides R3 for the title only.
     // Example: "Insertion sort" and "Kruskal's minimum spanning tree" are assignments to implement a named algorithm — the name is the problem, not a hint.
R5a. IF the ACTIVE TRACK is CLRS AND a problem is presented THEN also give the file and line of the procedure's pseudocode in the chapter slice under `../extracted/textbook/chapters/chapter<N>/`.
R6. IF a requirement constrains the result (in-place modification, a specific return value, no extra allocation) THEN state it in prose in the task description.
     // Commentary: These are requirements, not hints. R6 does not license restating them as a signature.
R7. IF any condition not covered by R1–R6 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Workflow

R1. IF the user says `check` THEN apply the Check section.
R2. IF the user asks a question THEN answer that question only.
R2a. IF answering a question THEN do not add code, next steps, hints, or offers of further help that the question did not ask for.
     // Commentary: the user decides when they want more. Volunteering the next step does their work for them.
R2b. IF answering a question about the user's code THEN use the identifiers, signature, and style already present in the problem file. Do not rename the user's variables or functions.
R2c. Workflow R2 overrides Workflow R3 and Problem Presentation R2–R4 for the content the question asks about, and for nothing else.
     // Example: "what type is the source?" gets the type. It does not also get the signature, the return type, or the loop.
R3. IF the user has not said `check`, asked for a grade, or asked to move on THEN do not grade, review, or comment on the code. Wait.
R4. IF the user asks to move on from an active problem THEN treat the problem as completed and apply the completion path for the ACTIVE MODE.
R5. IF a problem is completed in NORMAL mode THEN apply the Debrief section and let that section perform the required Completion Tracking update.
R6. IF a problem is completed in EASY mode THEN skip the Debrief section and immediately apply Completion Tracking R6. Ask no `easy`/`keep` question — the problem is already in PREVIOUS.
R7. IF completion bookkeeping finishes in either mode THEN immediately treat that event as a `next problem` request and present the selected problem. Do not ask whether the user wants another problem.
R8. IF any condition not covered by R1–R7 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Problem File

R1. IF this skill needs the user's current work THEN read the most recently modified file under the working directory whose extension matches the active track per Track R7. That file is "the problem file".
R2. IF two or more files with that extension under the working directory were modified within the last 10 minutes THEN ask which one is the problem file before answering. R2 overrides R1.
R3. IF no file with that extension exists under the working directory THEN ask the user what they have so far and wait for the answer. R3 fires only when R1 cannot.
R3a. IF a file with the active track's extension exists THEN ignore files of every other extension. R3a overrides R1 only as to which files are candidates.
     // Commentary: a `.py` or `.rs` file left on disk can be newer than `fun.cpp`. Matching on extension keeps answers aimed at the file the user is actually editing.
R4. IF answering a question about the user's code or a check request THEN re-read the problem file from disk at that moment, before composing the answer. Never answer from a previously read copy, including one read earlier in the same session.
     // Commentary: the user edits between requests; a stale copy produces answers about code that no longer exists.
R5. IF the problem file contradicts what the user states in chat THEN say so, quote the relevant lines, and ask which is current before answering.
R6. IF answering a question or a check request THEN output in chat only. Do not edit, create, or run the problem file unless the user explicitly asks.
R7. R6 does not restrict ACTIVE DECK bookkeeping required by Completion Tracking or Debrief R11.
R8. IF any condition not covered by R1–R7 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Check

R1. IF the user says "check" THEN resolve and read the problem file per the Problem File section and grade it against the problem requirements.
R2. IF the solution fulfills the problem requirements THEN say "correct" and apply the completion path for the ACTIVE MODE.
R3. IF the solution does not fulfill the requirements THEN state the failure as one concrete case: the input, the expected output, and what the code produces. Name the line it fails on.
R4. IF R3 fires THEN do not give the fix, the corrected line, or pseudocode for it. The user must ask for it.
     // Commentary: "check" is a verdict, not a hint. Fixing on a failed check does the user's work for them.
R5. IF verifying behavior requires running the code THEN copy the problem file to the scratchpad directory and run the copy with the active track's run command per Track R7. Never run, compile, or modify the problem file itself, and never write build output into the working directory.
R5a. IF the active track's run command includes a compile step AND that step fails THEN report the compiler error as the verdict per R3 and give no further grading.
R6. IF the problem file has no implementation for the current problem THEN say so and give no verdict.
R7. IF the solution produces correct output but violates a stated requirement of the problem (in-place, return value, no extra allocation) THEN grade it incorrect and name the violated requirement. R7 overrides R2.
R8. IF "check" arrives AND no problem is active THEN say no problem is active and give no verdict.
R9. IF any condition not covered by R1–R8 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Debrief

The NORMAL-mode technical debrief contains four questions asked one at a time:

1. What data structures does your solution operate on?
2. What approach did you use?
3. What is the time complexity?
4. What is the auxiliary space complexity?

R1. IF a solution is completed in NORMAL mode THEN start the technical debrief before marking the problem complete.
R2. IF a solution is completed in EASY mode THEN do not run any debrief or `easy`/`keep` question.
R3. IF starting the technical debrief THEN ask only question 1.
R4. IF the user answers a technical debrief question THEN grade it as correct or incorrect with one sentence of explanation and ask the next question.
R5. IF grading a technical debrief answer THEN read the expected answer from the problem's inline `| DS: ... | Algo: ... | Time: ... | Space: ...` fields in the ACTIVE DECK.
R6. IF grading question 1 THEN identify every data structure the solution uses, input or created, from the problem, the answer key, and the implementation, and accept an answer that names each of them.
R6a. IF grading question 1 THEN do not count scalar variables (indices, counters, running values, temporaries) as data structures, and do not mark an answer incorrect for omitting them.
     // Example: Container With Most Water operates on the input vector only. "A vector of ints" is correct; its left, right, and best variables are not data structures.
R6b. IF grading question 2 THEN accept a correct plain-language description of how the solution works without requiring the name of an algorithm or technique.
R6c. IF R6b fires AND the reference solution has a standard name THEN mention that name in the one-sentence explanation without marking the answer incorrect.
     // Example: "keep the best sum ending here, restart when it goes negative" is correct for Maximum Subarray; the explanation adds that this is Kadane's algorithm.
R7. IF grading question 4 THEN exclude storage belonging to the input and count only auxiliary space created or consumed by the solution.
R8. IF grading complexity answers THEN accept conceptual answers without requiring Big-O notation.
R9. IF the answer key names a data structure THEN accept an equivalent C/C++ data structure.
     // Example: a `HashMap` key accepts `std::unordered_map`, a C lookup array, or a hand-written table serving the same role.
R10. IF the deck's data-structure, algorithm, or complexity answer differs from the user's implementation THEN grade all four debrief answers against the user's actual code and state that basis; R10 overrides R5, R6, and R9 when they prescribe a different verdict.
R11. IF the problem lacks an answer key in the ACTIVE DECK on its first completion THEN derive the answers from the problem and implementation and write the answer key inline in the ACTIVE DECK before proceeding.
R12. IF all four technical questions are graded THEN ask: `easy = move it to PREVIOUS, keep = leave it in CURRENT.`
R13. IF the user answers R12's question THEN apply Completion Tracking R2–R5 and R7 as applicable.
R14. IF the user answers `keep` THEN say so in one line and do not treat the problem as finished with. It stays in CURRENT and will be presented again.
R15. IF the technical debrief and the R12 step are complete THEN apply Workflow R7 immediately.
R16. IF any condition not covered by R1–R15 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.
