---
name: coding_interview
description: Practice essential CS problems in Python, with review selection weighted by how much help each problem needed, and a post-completion debrief on data structures, algorithms, and complexity.
---

Run coding interview practice. Problems are stored in `CLAUDE.md` in the current working directory. The user solves each problem in Python. After Python is complete, a four-question debrief runs.

## Problem Selection

R1. IF the user says "give me a [difficulty] problem" THEN pick a completed problem at that difficulty using the weighted draw in Set Tracking R9.
R2. IF the user says "give me a new [difficulty] problem" THEN pick an uncompleted problem at that difficulty; mark it `[x]` and initialize it to `(sets: 0, streak: 0, weight: 5)` upon first completion, before Set Tracking R1–R6 apply.
R3. IF the user says "next problem" or "next question" THEN apply R1 using the difficulty of the current/last problem.
R4. IF the user says "next new problem" or "give me a new problem" THEN apply R2 using the difficulty of the current/last problem.
R5. IF no problem has been given yet in this session AND no difficulty is specified THEN ask the user for a difficulty before proceeding. Do not pick a problem.
R6. IF picking any problem THEN read the problem list from `CLAUDE.md` in the current working directory. Every heading in that file — LeetCode-style and CLRS alike — feeds one pool per difficulty.
     // Commentary: the CLRS headings are not a separate track. A request for an easy problem draws from all Easy entries in the file regardless of which section they sit under.
R7. IF selecting a problem THEN exclude the 3 most recently presented problems. R7 overrides R1–R4 when both apply.
     // Commentary: weight only falls after 5 clean solves, so a just-completed problem still carries its full weight. Without this exclusion the draw would serve it straight back.
R8. IF R7 leaves no candidate at the requested difficulty THEN apply R2 instead.
R9. IF any condition not covered by R1–R8 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Set Tracking

Each completed problem carries three fields: `(sets: N, streak: K, weight: W)`.
N = total completions. K = consecutive clean completions since the last weight change.
W = selection weight, an integer 1–5. New problems start at 5.

R1.  IF a problem is completed (Python → debrief done) THEN immediately increment its `(sets: N)` count in CLAUDE.md — do not defer to the next problem request.
R2.  IF R1 fires AND the attempt is UNASSISTED THEN increment `streak: K`.
R3.  IF R2 brings `streak: K` to 5 THEN subtract 1 from `weight: W` AND reset `streak: K` to 0.
R4.  IF R3 would take `weight: W` below 1 THEN hold it at 1 AND still reset `streak: K` to 0. R4 overrides R3.
R5.  IF R1 fires AND the attempt is ASSISTED THEN add 1 to `weight: W` AND reset `streak: K` to 0.
R6.  IF R5 would take `weight: W` above 5 THEN hold it at 5 AND still reset `streak: K` to 0. R6 overrides R5.
R7.  IF any of R2–R6 fire THEN state the outcome to the user in one line naming the new weight:
       "Clean solve — streak 3 of 5 toward weight 4."
       "Clean solve — weight 5 → 4, streak reset."
       "Assisted solve — weight 3 → 4, streak reset."
R8.  IF a problem entry lacks `streak:` or `weight:` THEN treat `streak:` as 0 and `weight:` as 5, and write the full three-field form on the next completion.
R9.  IF picking a completed problem for review THEN draw one at random with probability proportional to its `weight: W`. Candidates are the problems remaining after Problem Selection R7 filters the pool.
     // Commentary: weight is the probability numerator directly. A weight-1 problem against nine weight-5 problems comes up 1 time in 46 — rare, never zero.
R10. IF any condition not covered by R1–R9 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

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

R1. IF the user solves the problem in Python correctly THEN run the debrief (see Debrief section); after the debrief completes, mark the problem done and apply Set Tracking R1–R7.
R2. IF "correct" is ambiguous THEN a solution is correct when it fulfills the problem requirements OR the user requests to move on / says "next one."
R3. IF the user requests help THEN apply the Help section.
R4. IF the user says "check" THEN apply the Check section.
R5. IF the user has not said "check", asked for a grade, or asked to move on THEN do not grade, review, or comment on their code. Wait.
     // Commentary: unsolicited review is the same failure as unsolicited hints — it removes the work.
R6. IF any condition not covered by R1–R5 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Attempt Tracking

Determines whether a completion counts as clean. One flag per attempt.

R1. IF a problem is presented THEN start the attempt UNASSISTED.
R2. IF "help", "help+", "help++", "stuck", or "list" fires on the active problem THEN mark the attempt ASSISTED for the remainder of that attempt. This is one-way — no later action restores UNASSISTED.
R3. IF "check" fires THEN do not change the attempt flag, regardless of verdict.
     // Commentary: a failed check means the user found and fixed their own logic flaw. That is still a clean solve.
R4. IF the user answers a debrief question incorrectly THEN do not change the attempt flag.
     // Commentary: clean measures the solve, not the post-mortem.
R5. IF the user asks a clarifying question that is not one of the R2 keywords THEN do not change the flag.
     // Example: "do I have to declare the type?" is a clarifying question, not a help call — the attempt stays UNASSISTED.
R6. IF the attempt flag cannot be determined at completion time THEN treat the attempt as ASSISTED. R6 overrides R1.
     // Commentary: the flag is conversation state and does not survive a compaction or restart. Under-crediting a clean solve is recoverable — the user says so and the count is corrected. Over-crediting silently corrupts the one signal this feature exists to produce.
R7. IF any condition not covered by R1–R6 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Problem File

R1. IF this skill needs the user's current work THEN read the most recently modified `.py` file under the working directory. That file is "the problem file".
R2. IF two or more `.py` files under the working directory were modified within the last 10 minutes THEN ask which one is the problem file before answering. R2 overrides R1.
R3. IF no `.py` file exists under the working directory THEN ask the user what they have so far and wait for the answer. R3 fires only when R1 cannot.
R4. IF answering a help or check request THEN re-read the problem file from disk at that moment, before composing the answer. Never answer from a previously read copy, including one read earlier in the same session.
     // Commentary: the user edits between requests; a stale copy produces hints for code that no longer exists.
R5. IF the problem file contradicts what the user states in chat THEN say so, quote the relevant lines, and ask which is current before answering.
R6. IF answering a help or check request THEN output in chat only. Do not edit, create, or run the problem file unless the user explicitly asks.
R7. R6 does not restrict CLAUDE.md bookkeeping required by Set Tracking R1–R7 or Debrief R7.
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
R14. IF a help request arrives AND no problem is active THEN say no problem is active and apply Problem Selection R5. Do not list sections or give hints.
R15. IF giving help THEN use the identifiers, signature, and style already present in the problem file. Do not rename the user's variables or functions.
R16. IF a step in the locked-in section is already implemented in the problem file THEN do not give it as a hint. Give the first step that is missing or wrong.
R17. Help R1–R16 override the global consult-mode preference against showing code, and override Problem Presentation R2–R4 once help is requested.
     // Commentary: the user asked for these tiers explicitly; refusing code at help++ is the failure mode this section exists to fix.
R18. IF any request in this section fires ("help", "help+", "help++", "stuck", "list") THEN apply Attempt Tracking R2. This includes the bare "help" that only lists sections.
R19. IF any condition not covered by R1–R18 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Check

R1. IF the user says "check" THEN resolve and read the problem file per the Problem File section and grade it against the problem requirements.
R2. IF the solution fulfills the problem requirements THEN say "correct" and start the debrief immediately (Debrief R1).
R3. IF the solution does not fulfill the requirements THEN state the failure as one concrete case: the input, the expected output, and what the code produces. Name the line it fails on.
R4. IF R3 fires THEN do not give the fix, the corrected line, or pseudocode for it. The user must ask for help to get that.
     // Commentary: "check" is a verdict, not a hint tier. Fixing on a failed check collapses the help ladder.
R5. IF verifying behavior requires running the code THEN copy the problem file to the scratchpad directory and run the copy. Never run or modify the problem file itself.
R6. IF the problem file has no implementation for the current problem THEN say so and give no verdict.
R7. IF the solution produces correct output but violates a stated requirement of the problem (in-place, return value, no extra allocation) THEN grade it incorrect and name the violated requirement. R7 overrides R2.
R8. IF "check" arrives AND no problem is active THEN say no problem is active and give no verdict.
R9. IF any condition not covered by R1–R8 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Debrief

Fires after the Python solution is correct. One question at a time.

R1. IF the Python solution is graded correct THEN start the debrief immediately before marking the problem done.
R2. IF starting the debrief THEN ask only the first question: "Looking at your Python solution — what data structure(s) did you use, and why?"
R3. IF the user answers a debrief question THEN grade it (correct or incorrect, plus a one-sentence explanation), then ask the next question.
R4. The four debrief questions, asked in order:
     1. What data structure(s) did you use, and why?
     2. What algorithm or technique did you use?
     3. What is the time complexity?
     4. What is the space complexity?
R5. IF grading debrief answers THEN read the expected answer key from the problem's inline `| DS: ... | Algo: ... | Time: ... | Space: ...` fields in CLAUDE.md.
R6. IF grading complexity answers THEN accept conceptual answers — do not require Big-O notation.
R7. IF the problem has no answer key yet (first completion of a new problem) THEN derive the correct answers from the problem itself, grade the user's responses against them, then write the answer key inline to the problem's line in CLAUDE.md before proceeding.
R8. IF all four questions are answered and graded THEN mark the problem done and apply Set Tracking R1–R7 immediately.
R9. IF any condition not covered by R1–R8 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.
