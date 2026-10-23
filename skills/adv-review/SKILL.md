---
name: adv-review
description: Read-only review with four reviewers for correctness, hazards, fix complexity, and removal or simplification opportunities. Reviews diffs, files, functions, directories, codebases, and behavioral rule files. Reports whether to fix, simplify, remove, or accept an issue; never modifies code.
---

## Read-Only Guarantee

R1. IF running this skill THEN do not modify files, git state, or system state.
R2. IF the harness provides a structurally read-only reviewer type THEN use it for every reviewer.
R3. IF the harness does not provide a structurally read-only reviewer type THEN explicitly prohibit file, git, and system-state mutations in every reviewer prompt.
R4. IF another rule conflicts with R1–R3 THEN R1–R3 override that rule.

## Scope Resolution

R5. IF no argument is given THEN review `git diff HEAD` plus the contents of untracked files listed by `git status --porcelain`.
R6. IF R5 applies AND both lists are empty THEN report "Nothing to review: working tree is clean." and stop without spawning reviewers.
R7. IF the argument matches `path:START-END` THEN review that line range, reading the enclosing file for context and excluding findings outside the range.
R8. IF the argument is an existing file path AND R7 does not apply THEN review the entire file.
R9. IF the argument is an existing directory path AND R7 does not apply THEN group its source files into batches of at most five related files.
R10. IF the argument is `all` AND R7–R9 do not apply THEN enumerate source files excluding vendored, generated, and lock files and group them by module or directory into batches of at most five files.
R11. IF an argument does not match R7–R10 THEN locate it as a code identifier using `rg`.
R12. IF R11 finds exactly one definition THEN review its definition and direct uses, reading the enclosing file for context.
R13. IF R11 finds zero or multiple definitions THEN report the candidates and ask which identifier or path the user intends before spawning reviewers.
R14. IF a batch mixes numbered behavioral rule files and ordinary source files THEN split it into separate batches by file type.

## Four Reviewer Roles

R15. IF scope is resolved THEN assign four reviewer agents per batch: A for correctness, B for hazards, C for fix value, and D for removal and simplification; run A, B, and D independently within available concurrency limits, then run C after verifying their findings under R29.
R16. IF prompting any reviewer THEN provide the scope, its role, the user's stated requirements and usage information, and the following shared instructions:
     - Read the enclosing functions or rules and their callers or references before making a finding.
     - Cite file:line for every finding and remain within scope; outside context supplies evidence only.
     - Describe a concrete trigger for a bug or hazard, or concrete evidence and the behavior lost for a removal or simplification proposal.
     - Do not invent usage frequency or require a finding quota. Return no findings when evidence does not support one.
     - Do not modify files, git state, or system state.
R17. IF assigning A to source code THEN request logic bugs, boundary conditions, error paths, and broken invariants, with concrete failing inputs attempted even when no findings survive.
R18. IF assigning B to source code THEN request inefficiencies, silent failures, misuse-prone behavior, races, and resource or lifecycle leaks, with concrete triggering scenarios attempted even when no findings survive.
R19. IF assigning A to behavioral rules THEN request conflicting actions, missing precedence, precedence cycles, dead rules, and uncovered situations, with concrete inputs that expose each failure.
R20. IF assigning B to behavioral rules THEN request undecidable conditions, hedge words, unsplit compound instructions, embedded rationale, malformed catch-alls, contradictory examples, and numbering defects, citing the affected rule.
R21. IF assigning C THEN provide verified A/B findings and D proposals and request one recommendation per item: FIX, SIMPLIFY, REMOVE, or ACCEPT, comparing the smallest feasible correction, reduced behavior, removal, and leaving the issue alone against the user's requirements.
R22. IF C evaluates an item THEN require its triggering conditions, impact, evidence of relevance to the user's workflow, and the added branches, state, dependencies, configuration, and maintenance burden of each feasible response; mark unknown likelihood or usage as unknown.
R23. IF a finding describes a valid limitation but fixing it requires disproportionate complexity for the supported workflow THEN recommend ACCEPT and state the remaining limitation; retain the finding's impact classification separately from that recommendation.
     // Example: Preventing Run from appending to half-typed terminal input needs prompt tracking, but the user says they never leave terminal input unfinished → ACCEPT the limitation and explain its trigger.
R24. IF assigning D THEN request candidates for removing or simplifying dead paths, duplicate mechanisms, compatibility branches, defensive machinery, and optional features, including the concrete maintenance burden and behavior lost for each candidate.
R25. IF D proposes removal based on rare or absent use THEN require evidence from user statements, available usage data, or verified reachability; lack of local callers alone does not establish disuse for exported APIs, plugins, callbacks, or dynamic entry points.
R26. IF usage evidence is missing THEN label the proposal conditional on the stated usage assumption instead of claiming the feature is rarely used; C must retain that condition in its recommendation.
     // Example: No usage data exists for an optional terminal pane → "If this pane is unused, removing it eliminates its window and lifecycle state; usage is unknown."
R27. IF a reviewer comments only on naming, formatting, or stylistic architecture preferences THEN discard that comment; R20 permits behavioral-rule style findings, and R21–R26 permit evidence-backed complexity and simplification findings.
R28. IF A or B returns zero findings without describing the failing cases attempted THEN resume that reviewer once to request those cases and accept its second report even when it remains empty; do not require C or D to invent findings.

## Verification and Report

R29. IF A, B, or D returns a finding THEN verify its mechanism or evidence against the actual code or rules before sending it to C; discard unsupported findings and merge duplicates while retaining which reviewers found them.
R30. IF C returns its assessment THEN verify that the proposed response fits the code, the user's requirements, and any stated usage assumptions; discard unsupported reasoning before reporting.
R31. IF classifying verified A/B findings THEN label each BUG, FOOTGUN, or INEFFICIENCY and HIGH, MEDIUM, or LOW by impact; classify D proposals as SIMPLIFICATION rather than manufacturing a correctness defect.
R32. IF reporting findings THEN sort A/B findings HIGH → MEDIUM → LOW and include classification, severity, file:line, mechanism, trigger, and C's recommendation with its benefit/complexity tradeoff; report D's verified proposals with the behavior lost and C's assessment.
R33. IF recommending a response THEN prefer the least complex option that satisfies the user's stated requirements; do not treat a discovered issue as automatic justification for added code or an accepted limitation as permission to violate a requirement.
R34. IF printing a terminal report THEN separate sections with Unicode lines and do not use Markdown horizontal rules, HTML, or LaTeX.
R35. IF all reviewers return zero verified findings THEN report that and name the failure cases and simplification opportunities examined.
R36. IF the report is complete THEN end with "N bugs, N footguns, N inefficiencies, N simplification opportunities — no code was modified." and do not offer fixes unless the user asks.

## Catch-All

R37. IF any condition not covered by R1–R36 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.
