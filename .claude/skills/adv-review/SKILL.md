---
name: adv-review
description: Adversarial read-only review — spawn parallel reviewer agents to hunt bugs, inefficiencies, and footguns in a diff, file, line range, function, directory, or the whole codebase. Also reviews black-letter rule files (SKILL.md, CLAUDE.md) for conflicts, gaps, and ambiguity. Never modifies code.
---

You are running an adversarial review. Your job is to find reasons the code does not
work — bugs, inefficiencies, and footguns — and report them. You do not fix anything.

## Read-Only Guarantee

R1. IF running this skill THEN do NOT use Edit, Write, or NotebookEdit, and do NOT run
    any Bash command that modifies files, git state, or system state.
R2. IF spawning reviewer subagents THEN use subagent_type "Explore" only.
    // Commentary: Explore agents lack Edit/Write, so the read-only guarantee is
    // structural, not just prompted.
R3. R1 and R2 override every other rule in this skill.

## Scope Resolution

R4. IF no argument is given THEN scope = output of `git diff HEAD` plus the contents of
    untracked files listed by `git status --porcelain`.
R5. IF R4 applies AND both the diff and untracked list are empty THEN print "Nothing to
    review: working tree is clean." and stop. Spawn no agents.
R6. IF the argument is a path to an existing file THEN scope = that entire file.
R7. IF the argument matches the pattern `path:START-END` THEN scope = that line range.
    Reviewers read the whole file for context; findings outside the range are dropped.
R8. IF the argument is a path to an existing directory THEN scope = the source files in
    it. Group the files into batches of at most 5 related files; each batch gets its
    own reviewer pair (see R12), all pairs launched in parallel.
R9. IF the argument is `all` THEN scope = the whole codebase: enumerate source files
    (excluding vendored/generated/lock files), group by module or directory, and apply
    the per-batch fan-out from R8.
R10. IF the argument is not a path and not `all` THEN treat it as a code identifier:
     locate it with Grep. IF exactly one definition matches THEN scope = that
     definition's file, with findings restricted to the identifier's definition and
     direct uses. IF zero or multiple definitions match THEN list the candidates and
     ask the user which one; do not guess.
R11. IF the argument matches more than one of R6–R10 THEN precedence is R7 over R6
     over R8 over R9 over R10.

## Reviewer Protocol

R12. IF scope is resolved THEN spawn exactly 2 Explore agents per scope batch, both in
     a single message so they run in parallel:
     - Lens A — correctness: logic bugs, edge cases, boundary conditions, off-by-one,
       error/exit paths, broken invariants that callers depend on.
     - Lens B — hazards: inefficiencies (needless allocations, copies, syscalls,
       O(n²) where O(n) exists), footguns (misuse-prone APIs, silent failure modes,
       race windows, resource and lifecycle leaks).
R12a. IF a file in scope is a black-letter rule file (a markdown file whose body is
     numbered `IF ... THEN ...` rules, e.g. a SKILL.md or a CLAUDE.md rules section)
     THEN review it with these lenses instead of the R12 lenses:
     - Lens A — rule correctness: two rules that can both fire on the same situation
       with no explicit precedence rule; precedence rules that contradict each other
       or form a cycle; rules whose condition can never fire (dead rules); rules whose
       action contradicts another rule's action; situations the rule set does not
       cover (forcing the catch-all where a real rule should exist).
     - Lens B — rule hazards: hedge words ("generally," "usually," "as needed," "where
       appropriate," "be mindful of," "try to"); conditions that are not observable or
       decidable at execution time; compound rules with multiple triggers or actions
       not joined by explicit AND/OR; rationale embedded inside a rule instead of a
       `// Commentary:` line; missing or malformed catch-all rule; examples that
       contradict the rule they illustrate; rule numbering gaps or duplicates.
R12b. IF R12a applies THEN "concrete trigger" (R13c) means a concrete situation or user
     input under which the rule failure occurs — e.g. an input where two rules both
     fire and prescribe different actions, or an input no rule covers.
R12c. IF R12a applies THEN black-letter style violations found by Lens B are findings,
     not style comments. R12c overrides R13d for black-letter rule files only.
R12d. IF a scope batch mixes black-letter rule files and ordinary source files THEN
     split it: rule files get an R12a reviewer pair, source files get an R12 reviewer
     pair.
R13. IF writing a reviewer prompt THEN include all of the following instructions,
     plus the scope content (diff or file list) and the lens definition:
     a. "Assume bugs exist. Your review has failed if you return 'looks good' without
        having attempted to construct a concrete failing input."
     b. "Before making any finding, read the surrounding context: the full enclosing
        function, its callers, and everything the code in scope touches. Never judge
        a diff hunk in isolation."
     c. "Every finding must cite file:line and describe a concrete trigger — an input,
        call sequence, or state that causes the failure. A finding with no mechanism
        is not a finding; omit it."
     d. "Do not comment on style, naming, formatting, or architecture. These are
        forbidden."
     e. "Classify every finding as BUG, INEFFICIENCY, or FOOTGUN, with severity HIGH,
        MEDIUM, or LOW."
     f. "Report findings only within the given scope; context outside the scope
        informs findings but does not generate them."
R14. IF a reviewer returns zero findings AND its report does not describe the failing
     inputs it attempted THEN reject the result and re-run that reviewer once with a
     reminder of R13a. IF the re-run also returns zero findings THEN accept it.

## Consolidation & Report

R15. IF both reviewers report the same underlying issue THEN merge into one finding
     marked "confirmed by both lenses".
R16. IF a finding is received THEN verify its cited mechanism against the actual code
     before reporting. IF the mechanism does not hold THEN drop the finding silently.
     // Commentary: this filters hallucinated bugs, the main failure mode of LLM
     // reviewers.
R17. IF reporting THEN print a terminal report: findings sorted HIGH → MEDIUM → LOW,
     each entry showing classification, severity, file:line, a one-sentence mechanism,
     and the concrete trigger. Separate sections with a Unicode line
     (────────────────────────────────────────) — never `---`, HTML, or LaTeX.
R18. IF the report is printed THEN end with one summary line in the form
     "N bugs, N footguns, N inefficiencies — no code was modified." Do not offer to
     fix findings unless the user asks.
R19. IF all reviewers return zero verified findings THEN report that, list the attack
     angles the reviewers tried, and end with the R18 summary line showing zeros.

## Catch-All

R20. IF any condition not covered by R1–R19 arises THEN stop, describe the situation
     to the user, and ask how to proceed. Do not improvise.
