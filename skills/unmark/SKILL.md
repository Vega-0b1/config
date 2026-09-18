---
name: unmark
description: Release a code mark set by /mark. `/unmark` pops the active mark and returns to the previous one (or to no mark); `/unmark all` clears every mark; `/unmark <id>` removes one specific mark. Carry-forward behavior is defined in AGENT.md "Code Marks".
---

Marks are a stack. The top of the stack is the active mark.

## Rules

R1. IF invoked as `/unmark` AND a mark is active THEN pop the active mark.
R2. IF invoked as `/unmark all` THEN remove every mark.
R3. IF invoked as `/unmark <id>` AND `<id>` is on the stack THEN remove that mark from wherever it is on the stack.
R4. IF no mark is active THEN reply `No mark active.` and change nothing.
R5. IF invoked as `/unmark <id>` AND `<id>` is not on the stack THEN reply with one line naming the marks on the stack, and change nothing.

// Response
R6. IF the stack is not empty after R1–R3 THEN the entire response is the new active mark, with its trailing label reading `<id> (marked, level <N>)` per AGENT.md M1. Add no commentary.
R7. IF the stack is empty after R1–R3 THEN the entire response is the line `Unmarked. No mark active.` followed by the latest version of the full code block that contained the removed mark, with every section id per AGENT.md M1.
    // Example: `/mark j` then `/unmark` -> `Unmarked. No mark active.` then the whole .c file with ids e–k.
R8. IF any condition not covered by R1–R7 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.
