---
name: coding_interview
description: Practice essential CS problems in Python then Rust, with set-based review selection and a post-completion debrief on data structures, algorithms, and complexity.
---

Run coding interview practice. Problems are stored in `CLAUDE.md` in the current working directory. The user solves each problem in Python, then Rust. After Rust is complete, a four-question debrief runs.

## Problem Selection

R1. IF the user says "give me a [difficulty] problem" THEN pick a completed problem at that difficulty using set-based selection: lowest `(sets: N)` count wins; ties broken randomly.
R2. IF the user says "give me a new [difficulty] problem" THEN pick an uncompleted problem at that difficulty; mark it `[x]` and set `(sets: 0)` upon first completion.
R3. IF the user says "next problem" or "next question" THEN apply R1 using the difficulty of the current/last problem.
R4. IF the user says "next new problem" or "give me a new problem" THEN apply R2 using the difficulty of the current/last problem.
R5. IF no problem has been given yet in this session AND no difficulty is specified THEN ask the user for a difficulty before proceeding. Do not pick a problem.
R6. IF picking any problem THEN read the problem list from `CLAUDE.md` in the current working directory.
R7. IF any condition not covered by R1–R6 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Set Tracking

R1. IF a problem is completed (Python → Rust → debrief done) THEN immediately increment its `(sets: N)` count in CLAUDE.md — do not defer to the next problem request.
R2. IF picking a completed problem for review THEN select the problem(s) with the lowest set count. IF tied THEN pick randomly.
R3. IF a problem's set count is 2 or more below the median set count of all completed problems at that difficulty THEN mark it `[growing]`. Growing problems get 2× weight in selection.
R4. IF a growing problem's set count gap closes to 1 or less from the median THEN remove the `[growing]` tag.

## Workflow

R1. IF the user solves the problem in Python correctly THEN re-prompt the same problem in full and ask for Rust.
R2. IF the user solves the problem in Rust correctly THEN run the debrief (see Debrief section); after the debrief completes, mark the problem done and apply Set Tracking R1.
R3. IF "correct" is ambiguous THEN a solution is correct when it fulfills the problem requirements OR the user requests to move on / says "next one."
R4. IF re-prompting for Rust THEN always include the full problem statement — do not write "now do it in Rust" alone.
R5. IF any condition not covered by R1–R4 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Debrief

Fires after both Python and Rust are complete. Questions are about the Python solution. One question at a time.

R1. IF the Rust solution is graded correct THEN start the debrief immediately before marking the problem done.
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
R8. IF all four questions are answered and graded THEN mark the problem done and apply Set Tracking R1 immediately.
R9. IF any condition not covered by R1–R8 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.
