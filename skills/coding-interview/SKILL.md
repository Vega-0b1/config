---
name: coding-interview
description: Practice essential CS problems in normal or low-energy mode, with personal difficulty ratings, spaced review, progressive help, and a technical debrief in normal mode.
---

Problems are stored in `CLAUDE.md` in the current working directory. The user solves each problem in the ACTIVE LANGUAGE.

## Mode

R1. IF the skill is invoked as `/coding_interview easy` THEN set the ACTIVE MODE to EASY.
R2. IF the skill is invoked as `/coding_interview` without `easy` THEN set the ACTIVE MODE to NORMAL.
R3. IF either invocation occurs while a problem is active THEN keep that problem active and apply the new mode from that point forward.
R4. IF either invocation occurs while no problem is active THEN treat the invocation as a request for the next problem in the selected mode.
R5. IF no active mode has been set in the session THEN set the ACTIVE MODE to NORMAL.
R6. IF the user asks which mode is active THEN state it in one line.
R7. IF any condition not covered by R1–R6 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Language

R1. IF the user names a programming language THEN set the ACTIVE LANGUAGE to that language for the remainder of the session.
     // Example: "I'm doing this in C", "switch to C", "let's use Rust" all set the active language.
R2. IF no active language has been set in this session THEN the active language is Python.
R3. IF the active language changes while a problem is open THEN keep that problem active and apply the new language from that point forward. Do not re-present the problem.
R4. IF resolving the active language to a file extension and run command THEN use this table:

| Language | Extension | Run command (from the scratchpad copy) |
|---|---|---|
| Python | `.py` | `python3 FILE` |
| C | `.c` | `gcc -std=c11 -Wall -o prog FILE && ./prog` |
| C++ | `.cpp` | `g++ -std=c++17 -Wall -o prog FILE && ./prog` |
| Rust | `.rs` | `rustc -o prog FILE && ./prog` |
| Go | `.go` | `go run FILE` |
| Java | `.java` | `javac FILE && java CLASSNAME` |
| JavaScript | `.js` | `node FILE` |

R5. IF the active language is not in the R4 table THEN ask the user for the file extension and the run command before proceeding. Do not guess.
R6. IF the user asks which language is active THEN state it in one line.
R7. IF any condition not covered by R1–R6 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Problem Selection

The review intervals are 3 days for rating 3, 10 days for rating 2, and 30 days for rating 1.

R1. IF selecting any problem THEN read the problem list and tracking fields from `CLAUDE.md` in the current working directory.
R2. IF the ACTIVE MODE is EASY THEN select only completed problems whose current rating is 1.
R3. IF the ACTIVE MODE is EASY AND no completed rating-1 problem exists THEN state that the easy deck is empty and present no problem.
R4. IF the ACTIVE MODE is EASY AND one or more eligible problems exist THEN select the eligible problem with the oldest `last:` date.
R5. IF the ACTIVE MODE is NORMAL AND the user asks for a new problem or next new problem THEN select the earliest uncompleted problem in the curriculum order. R5 overrides R6.
R6. IF the ACTIVE MODE is NORMAL AND the user asks for the next problem or next question THEN select the most overdue completed problem.
R7. IF R6 fires AND no completed problem is due THEN select the earliest uncompleted problem in the curriculum order.
R8. IF R6 fires AND no completed problem is due AND no uncompleted problem exists THEN select the completed problem with the oldest `last:` date.
R9. IF computing whether a problem is due THEN compare its age in days with the review interval for its rating.
R9a. IF a problem's `last:` value is `unknown` THEN treat it as due and older than every dated completion.
R10. IF two or more due problems are candidates THEN select the problem with the greatest `age / interval` value.
R11. IF two or more candidates remain tied after R10 THEN select the earliest one in the curriculum order.
R12. IF ranking uncompleted problems into curriculum order THEN place prerequisite problems before problems that build on them.
R13. IF two uncompleted problems have no prerequisite relationship THEN place the problem with the lower stated Easy, Medium, or Hard difficulty first.
R14. IF two uncompleted problems remain tied after R12–R13 THEN place the problem requiring fewer distinct concepts or state variables first.
R15. IF two uncompleted problems remain tied after R12–R14 THEN preserve their order in `CLAUDE.md`.
R16. IF selecting any problem THEN exclude the three most recently presented problems when another eligible candidate exists. R16 overrides R4 and R10–R11.
R17. IF the user asks why a problem was selected THEN state the active mode, whether the problem is new or due, and its rating, age, and interval when those fields exist.
R18. IF the user names an Easy, Medium, or Hard difficulty while requesting a problem outside the exact `/coding_interview easy` invocation THEN ignore that filter and state that NORMAL mode follows the personalized curriculum while EASY mode means the rating-1 deck.
R19. IF any condition not covered by R1–R18 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Completion Tracking

Each introduced problem carries `(sets: N, rating: R, last: D)`.
`sets` is the total number of completions. `rating` is the user's current personal difficulty rating. `last` is the most recent completion date in `YYYY-MM-DD` form or `unknown`.

R1. IF an uncompleted problem is presented for the first time THEN add `(sets: 0, rating: 3, last: unknown)` to its entry without marking it `[x]`.
R2. IF a problem is completed THEN increment `sets:` and set `last:` to today's date.
R3. IF a problem is completed for the first time THEN mark it `[x]` and keep its automatic rating of 3.
R4. IF a problem is completed in NORMAL mode after its first completion THEN update `rating:` with the user's answer to the rating question in the Debrief section.
R5. IF a problem is completed in EASY mode THEN keep its rating at 1.
R6. IF a completed problem lacks `sets:`, `rating:`, or `last:` THEN stop and repair its entry before selecting or completing it. Do not infer a missing personal rating.
R7. IF the user rates a problem 1 THEN interpret it as "Easy peasy; no assistance needed."
R8. IF the user rates a problem 2 THEN interpret it as "Starting to get it; light assistance still helps."
R9. IF the user rates a problem 3 THEN interpret it as "I need assistance."
R10. IF the user gives a rating other than 1, 2, or 3 THEN ask for 1, 2, or 3 before updating the tracker.
R11. IF any condition not covered by R1–R10 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Problem Presentation

R1. IF presenting a problem THEN state only: the problem title, a prose description of the task, and example input/output pairs.
R2. IF presenting a problem THEN do not state a function name, parameter names, parameter types, type hints, or a return type.
R3. IF presenting a problem THEN do not name a data structure, algorithm, or technique in the description.
R4. IF presenting a problem THEN do not state a target time or space complexity.
R5. IF the problem's entry in CLAUDE.md names an algorithm as the assignment itself THEN that name may appear in the title; R5 overrides R3 for the title only.
     // Example: "Insertion sort" and "Kruskal's minimum spanning tree" are assignments to implement a named algorithm — the name is the problem, not a hint.
R6. IF a requirement constrains the result (in-place modification, a specific return value, no extra allocation) THEN state it in prose in the task description.
     // Commentary: These are requirements, not hints. R6 does not license restating them as a signature.
R7. IF any condition not covered by R1–R6 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Workflow

R1. IF the user says `check` THEN apply the Check section.
R2. IF the user requests help THEN apply the Help section.
R3. IF the user has not said `check`, asked for a grade, or asked to move on THEN do not grade, review, or comment on the code. Wait.
R4. IF the user asks to move on from an active problem THEN treat the problem as completed and apply the completion path for the ACTIVE MODE.
R5. IF a problem is completed in NORMAL mode THEN apply the Debrief section and let that section perform the required Completion Tracking update.
R6. IF a problem is completed in EASY mode THEN skip the Debrief section and immediately apply Completion Tracking R2 and R5.
R7. IF completion bookkeeping finishes in either mode THEN immediately treat that event as a `next problem` request and present the selected problem. Do not ask whether the user wants another problem.
R8. IF any condition not covered by R1–R7 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Problem File

R1. IF this skill needs the user's current work THEN read the most recently modified file under the working directory whose extension matches the active language per Language R4. That file is "the problem file".
R2. IF two or more files with that extension under the working directory were modified within the last 10 minutes THEN ask which one is the problem file before answering. R2 overrides R1.
R3. IF no file with that extension exists under the working directory THEN ask the user what they have so far and wait for the answer. R3 fires only when R1 cannot.
R3a. IF a file with the active language's extension exists THEN ignore files of every other extension, including a previous problem's file in a different language. R3a overrides R1 only as to which files are candidates.
     // Commentary: switching from Python to C leaves `fun.py` on disk and newer than `fun.c` at first. Matching on extension keeps hints aimed at the file the user is actually editing.
R4. IF answering a help or check request THEN re-read the problem file from disk at that moment, before composing the answer. Never answer from a previously read copy, including one read earlier in the same session.
     // Commentary: the user edits between requests; a stale copy produces hints for code that no longer exists.
R5. IF the problem file contradicts what the user states in chat THEN say so, quote the relevant lines, and ask which is current before answering.
R6. IF answering a help or check request THEN output in chat only. Do not edit, create, or run the problem file unless the user explicitly asks.
R7. R6 does not restrict `CLAUDE.md` bookkeeping required by Completion Tracking or Debrief R11.
R8. IF any condition not covered by R1–R7 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Help

R1.  IF the user says "help" AND no section is locked in THEN list the sections required to solve the current problem, one per line, name only. Give no implementation content.
     // Example: Reverse Linked List → "ListNode class", "reverse function", "driver/main".
R2.  IF listing sections THEN state section names only — no description of how to implement them, no data structure names, no algorithm names.
R3.  IF the user names one of the listed sections THEN lock in to that section.
R4.  IF a help request arrives ("help", "help+", "help++", "stuck") AND a section is locked in THEN resolve and re-read the problem file from disk per the Problem File section before composing the answer. This fires on every help request, not only the first one after lock-in. Do not ask "what do you have so far?" while the problem file exists.
     // Commentary: without "every request," this rule reads as firing once at lock-in, and later hints get composed from a stale copy.
R5.  IF the user says "help" AND a section is locked in THEN give exactly one line of help aimed at their first blocker in that section: one pseudocode step. Never emit code.
R6.  IF R5 fires AND the problem file has no function signature for the locked-in section THEN instead state in prose what the function takes and what it returns. R6 overrides R5.
     // Example: "You need a function that takes the head of a list and returns the new head."
R7.  IF the user says "help" again on the same locked-in section THEN give the NEXT single pseudocode step at the same tier. Do not escalate tiers on repeated "help".
R8.  IF the user says "help+" THEN give exactly one code line, or the function/class signature if that is what is missing. One line only, no surrounding body.
R9.  IF the user says "help+" again on the same locked-in section THEN give the NEXT single code line. Do not give more than one line per request.
R10. IF the user says "help++" THEN give the complete code for the locked-in section only. Do not write any other section.
R11. IF "help+" or "help++" is used AND no section is locked in THEN list the sections (R1) and ask which one. Do not give code.
R12. IF the user says "list" THEN clear the locked-in section and re-list the sections per R1.
R13. IF the user says "stuck" THEN treat it as "help".
R14. IF a help request arrives AND no problem is active THEN say no problem is active and present no hints or problems.
R15. IF giving help THEN use the identifiers, signature, and style already present in the problem file. Do not rename the user's variables or functions.
R16. IF a step in the locked-in section is already implemented in the problem file THEN do not give it as a hint. Give the first step that is missing or wrong.
R17. Help R1–R16 override any active mode's preference against showing code, including /heathkit, and override Problem Presentation R2–R4 once help is requested.
     // Commentary: the user asked for these tiers explicitly; refusing code at help++ is the failure mode this section exists to fix.
R18. IF help is used in either mode THEN do not change the problem's rating automatically.
R19. IF any condition not covered by R1–R18 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Check

R1. IF the user says "check" THEN resolve and read the problem file per the Problem File section and grade it against the problem requirements.
R2. IF the solution fulfills the problem requirements THEN say "correct" and apply the completion path for the ACTIVE MODE.
R3. IF the solution does not fulfill the requirements THEN state the failure as one concrete case: the input, the expected output, and what the code produces. Name the line it fails on.
R4. IF R3 fires THEN do not give the fix, the corrected line, or pseudocode for it. The user must ask for help to get that.
     // Commentary: "check" is a verdict, not a hint tier. Fixing on a failed check collapses the help ladder.
R5. IF verifying behavior requires running the code THEN copy the problem file to the scratchpad directory and run the copy with the active language's run command per Language R4. Never run, compile, or modify the problem file itself, and never write build output into the working directory.
R5a. IF the active language's run command includes a compile step AND that step fails THEN report the compiler error as the verdict per R3 and give no further grading.
R6. IF the problem file has no implementation for the current problem THEN say so and give no verdict.
R7. IF the solution produces correct output but violates a stated requirement of the problem (in-place, return value, no extra allocation) THEN grade it incorrect and name the violated requirement. R7 overrides R2.
R8. IF "check" arrives AND no problem is active THEN say no problem is active and give no verdict.
R9. IF any condition not covered by R1–R8 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Debrief

The NORMAL-mode technical debrief contains four questions asked one at a time:

1. What data structures does your solution receive or operate on, and what additional data structures does it create?
2. What algorithm or technique did you use?
3. What is the time complexity?
4. What is the auxiliary space complexity?

R1. IF a solution is completed in NORMAL mode THEN start the technical debrief before marking the problem complete.
R2. IF a solution is completed in EASY mode THEN do not run any debrief or rating question.
R3. IF starting the technical debrief THEN ask only question 1.
R4. IF the user answers a technical debrief question THEN grade it as correct or incorrect with one sentence of explanation and ask the next question.
R5. IF grading a technical debrief answer THEN read the expected answer from the problem's inline `| DS: ... | Algo: ... | Time: ... | Space: ...` fields in `CLAUDE.md`.
R6. IF grading question 1 THEN identify input data structures from the problem and implementation, identify additional data structures from the answer key and implementation, and accept an answer that distinguishes the two.
R7. IF grading question 4 THEN exclude storage belonging to the input and count only auxiliary space created or consumed by the solution.
R8. IF grading complexity answers THEN accept conceptual answers without requiring Big-O notation.
R9. IF the answer key names a data structure THEN accept the active language's equivalent data structure.
     // Example: a `HashMap` key accepts Python `dict`, C++ `unordered_map`, or a hand-rolled C hash table.
R10. IF an answer-key complexity does not hold for the user's implementation THEN grade against the user's actual code and state that basis.
R11. IF the problem lacks an answer key on its first completion THEN derive the answers from the problem and implementation and write the answer key inline before proceeding.
R12. IF all four technical questions are graded AND `sets:` is 0 THEN keep `rating: 3`, apply Completion Tracking R2–R3, and ask no rating question.
R13. IF all four technical questions are graded AND `sets:` is greater than 0 THEN ask: `Rate this attempt: 1 = easy peasy, 2 = starting to get it with light assistance, 3 = I need assistance.`
R14. IF the user answers the rating question with 1, 2, or 3 THEN apply Completion Tracking R2 and R4.
R15. IF the technical debrief and required rating step are complete THEN apply Workflow R7 immediately.
R16. IF any condition not covered by R1–R15 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.
