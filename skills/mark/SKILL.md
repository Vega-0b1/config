---
name: mark
description: Pin a displayed code block (or part of one) so it is re-shown at the top of every response while the user asks questions about it. `/mark a` pins the block labeled a; `/mark a 12-18` or `/mark a main` pins part of it; `/mark` alone pins the most recently shown block. Marks stack — marking inside a mark zooms in, and /unmark returns to the previous level. Code labels and the carry-forward behavior are defined in AGENT.md "Code Marks".
---

Marks are a stack. The top of the stack is the active mark. AGENT.md "Code Marks" M4–M6 govern
how the active mark is shown on every response; this skill only changes the stack.

## Rules

// Choosing what to mark
R1. IF invoked as `/mark <id>` AND a code block labeled `<id>` was displayed in this conversation THEN push the latest version of that block onto the stack.
R2. IF invoked as `/mark <id> <start>-<end>` THEN push only lines <start> through <end> of block `<id>`, counting line 1 as the first line of the block.
R3. IF invoked as `/mark <id> <name>` AND <name> is not a line range THEN push only the function, section, or statement group in block `<id>` that <name> identifies.
    // Example: `/mark a main` pins `int main(){ ... }`. `/mark a printBN` pins the printBN function.
R4. IF invoked as `/mark` with no argument THEN push the most recently displayed code block.
R5. IF the id does not match any displayed label, OR <name> matches nothing in the block, OR the range is outside the block THEN say so in one line, list the labels displayed so far, and do not change the stack.
R6. IF <name> matches more than one part of the block THEN list the matches and do not change the stack.

// Naming a partial mark
R7. IF R2 or R3 pushed part of a block THEN the mark's id is `<id>:<start>-<end>` or `<id>:<name>`.

// Stacking
R8. IF a mark is already active THEN push the new mark on top. The previous mark stays on the stack below it.
R9. IF the requested mark is identical to the active mark THEN do not push; re-display the active mark.

// Response
R10. IF the stack changed THEN the entire response is the pinned code, with its trailing label reading `<id> (marked, level <N>)` per AGENT.md M1, where N is the stack depth. Add no commentary.
R11. IF any condition not covered by R1–R10 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.
