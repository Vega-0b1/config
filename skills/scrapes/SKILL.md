---
name: scrapes
description: Maintain the offline documentation dumps in ~/edu/scrapes — add a source, refresh stale dumps, extract a PDF (datasheets, manuals) into a greppable dump, audit, and diagnose a blocked promotion. Use when adding or refreshing reference material, not when merely reading it.
---

Maintain the dumps in `~/edu/scrapes`. Every dump is build output produced from
`sources.toml` by `scrapes.py`; nothing there is hand-written.

`~/.claude/CLAUDE.md` (Uncertainty & Verification) already governs **when** to consult the
dumps. This skill governs **how to maintain** them, and is not a substitute for it.

## Status — toolchain absent (verified 2026-09-10)

`sources.toml`, `scrapes.py`, `audit_dumps.py`, `index_dumps.py` and
`~/edu/scrapes/README.md` are **not present on this host**. Only the `.txt` dumps and a
stale `__pycache__/` (holding `audit_dumps` and `index_dumps` bytecode) survived the
NixOS-to-Debian migration. `~/edu` is Nextcloud-synced and deliberately untracked by
R26, so there is no git history to restore them from.

R0.  IF the task requires any tool in the Tools section THEN report that the toolchain is absent and stop. R0 overrides every rule below.
     // Commentary: reading dumps still works and is governed by `~/.claude/CLAUDE.md`. Only maintenance is blocked.
R0a. IF asked to work around the absence THEN do NOT hand-write, hand-edit, or hand-index a `.txt` dump.
     // Commentary: a dump is build output whose CONTENTS header is generated. Hand-editing desynchronizes the index from the body, R3's page counts stop meaning anything, and the next real scrape discards the work.
R0b. IF the toolchain is restored THEN delete this section and drop R0–R0b.

The rules below describe the intended workflow and stay authoritative for what to
rebuild. Treat them as a specification until R0b fires.

## Tools

    scrapes.py list | scrape NAME... | update --stale N | audit    [--dry-run] [--force]
    audit_dumps.py  pages | compare A B | options | stale | coverage | verify
    index_dumps.py  [FILE...] | --check | --strip | --scraped YYYY-MM-DD

Source kinds: `nix-options`, `markdown`, `mediawiki`, `texinfo`, `doxygen`, `pdf`.

## Rules

// Reading and editing
R1.  IF a `.txt` dump needs changing THEN change `sources.toml` and re-scrape. Do NOT edit a dump by hand.
     // Commentary: dumps are build output. The next scrape silently discards hand edits.
R2.  IF asked what a dump contains THEN grep its CONTENTS index for the page, then `sed -n 'START,ENDp'` that range. Do NOT read the whole file.
R3.  IF reporting a page count THEN take it from `audit_dumps.py pages` or the CONTENTS header, never from `grep -c '^# '`.
     // Commentary: raw banner counts overcount by 40-60%. Scrapers emit '# ' for shell comments and stray body lines.

// Adding a source
R4.  IF adding a source THEN add a `sources.toml` entry with `kind`, its source field, `min_pages` (or `min_options`), and `sentinels`.
R5.  IF choosing sentinels THEN pick strings that would vanish first if extraction regressed, not strings that appear everywhere.
     // Example: `useGrimAdapter` sits inside a code template — it disappears the moment template parsing breaks. "NixOS" does not.
R6.  IF a source is reachable both locally and over the network THEN prefer local.
     // Commentary: home_manager_options, openocd_manual and stm32f4_hal are generated from what is installed, so they match the running system and need no network. nixos_options was too, on the former NixOS host; it no longer describes this one.
R7.  IF a flake package is the source THEN reference it through `builtins.getFlake "/home/jcvega/repos/debian-config"`, never a bare `github:owner/repo/branch` ref.
     // Commentary: a branch ref resolves to that branch's HEAD, which drifts ahead of flake.lock and documents a version this system does not have. The flake moved here from /etc/nixos when the host became Debian — there is no system flake now, only this Home Manager one.
R8.  IF a new source is added THEN run `scrape NAME --dry-run` first and inspect the candidate before promoting.

// PDFs
R9.  IF adding a PDF THEN use `kind = "pdf"` with `urls` (remote), `files` (local), or both. Each PDF page becomes one dump page, so citations by page number resolve.
R10. IF a PDF source is remote THEN ask the user before the first download of that source. State the filename and origin.
     // Commentary: downloading is the one step here that reaches outside the machine and writes a file the user did not ask for by name.
R11. IF a PDF has been extracted THEN do NOT keep the PDF. The manifest holds the URL and the dump regenerates.
R12. IF extraction reports "no extractable text" THEN the PDF is an image-only scan. Say so and stop. Do NOT work around it.
     // Commentary: pdftotext cannot read it; OCR is out of scope. A silent workaround produces a dump of blank pages.

// Refreshing
R13. IF asked to refresh everything THEN run `scrapes.py update --stale N` (default 60 days).
R14. IF one dump needs refreshing THEN run `scrapes.py scrape NAME`.
R15. IF a dump's age is in question THEN read the `scraped` date in its CONTENTS header, not the file's mtime.
     // Commentary: indexing rewrites the file, so mtime records the last index run. Every dump would read as fresh.

// When the gate blocks
R16. IF promotion is blocked THEN the live dump is untouched and the candidate is kept as `<name>.txt.new`. Investigate that file before doing anything else.
R17. IF promotion is blocked THEN do NOT use `--force` without first stating what the blocker was and why forcing is correct.
     // Commentary: every block so far has been right — a truncated scrape, a fetch error, a redirect-bloated page count.
R18. IF page count dropped below the floor THEN suspect a truncated or partial fetch.
R19. IF page count rose sharply (the 1.5x blocker) THEN suspect the scraper changed WHAT it collects, not that new content appeared.
     // Example: dropping `apfilterredir=nonredirects` turned 4,349 real Arch articles into 16,249, of which 73% were one-line redirect stubs.
R20. IF a fetch error is reported THEN fix the URL in `sources.toml` rather than forcing past it.
     // Example: a 404 on a plugin README usually means the wrong default branch, or the repo ships vim help files instead of a README.

// Reading the audit output
R21. IF the misparse warning rises after a change THEN check whether more code survived before treating it as a regression.
     // Commentary: preserved code blocks contain '# ' shell comments. A better scrape can raise the raw count. The check ignores lines inside ``` fences for this reason.
R22. IF `audit_dumps.py options` reports slightly fewer options than the source JSON THEN this is a known counting artifact, not data loss.
     // Commentary: the pattern requires a dotted lowercase name, so `lib`, `specialisation`, `uninstall` and `_module.args` are present but uncounted.

// Housekeeping
R23. IF a dump is retired THEN remove its manifest entry, delete the `.txt`, and clear references in `~/.claude/CLAUDE.md` and `~/edu/scrapes/README.md`.
R24. IF a dump is added or retired THEN update the file table in `~/edu/scrapes/README.md` and the dump index in `~/.claude/CLAUDE.md`.
     // Commentary: `~/.claude/CLAUDE.md` R1 routes lookups by filename. A stale entry sends the next session to a file that does not exist.
R25. IF deleting any dump THEN first verify what is uniquely in it, and report that before deleting.
     // Commentary: a redundancy call in this directory was wrong once. Title overlap is not content overlap.
R26. IF `sources.toml` or a script changes THEN do NOT stage or commit it. Nothing under `~/edu` is tracked by `~/repos/config`.
     // Commentary: the Nextcloud client syncs ~/edu, so this directory is backed up but not versioned. These files were tracked for one day (2026-08-17 to 2026-08-18) and untracked deliberately. Editing them is still correct; reaching for git afterwards is not.

// Catch-all
R27. IF any condition not covered by R0–R26 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.
