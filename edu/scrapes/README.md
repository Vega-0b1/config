# Offline documentation dumps

Flat-text scrapes kept for grep-first lookup, so answers come from a static local
copy instead of model recall or a web round-trip. Moved here from `/etc/nixos/scrapes`
on 2026-08-13 — they were reference material, not configuration, and did not belong
in the nix-config repo. The lookup order itself is a rule in `~/CLAUDE.md`
(Uncertainty & Verification); it is not repeated here.

## How to read one

Every file opens with a **CONTENTS index** listing each page and the line range it
occupies. Grep the index, then pull the range — no full-file scan needed.

```
grep -n "  WireGuard$" nixos_wiki.txt     →   116612   117377  WireGuard
sed -n '116612,117377p' nixos_wiki.txt
```

Line numbers in the index include the index itself, so they are absolute.

Below the index, pages are delimited two different ways depending on the source:

- **Wiki dumps** (`arch_wiki`, `nixos_wiki`, `openocd_manual`, `stm32f4_hal`): a `# <Title>` line
  fenced above and below by 60 `=` characters.
- **Repo doc dumps** (`hypr_waybar_docs`, `nvim_plugins_docs`): a `## <Title>` line
  followed by `(source: <URL>)`.

## Files

| File | Pages | Origin |
|---|---|---|
| `arch_wiki.txt` | 4,349 | scraped, MediaWiki API |
| `nixos_options.txt` | 24,558 options | **generated** from the pinned flake |
| `home_manager_options.txt` | 5,406 options | **generated** from the pinned flake |
| `nixos_wiki.txt` | 1,356 | scraped, MediaWiki API |
| `hypr_waybar_docs.txt` | 103 | scraped, raw markdown |
| `nvim_plugins_docs.txt` | 22 | scraped, raw markdown |
| `cortex_debug_docs.txt` | 2 | scraped, raw markdown |
| `stm32cube_getting_started.txt` | 28 | **extracted** from a local PDF (UM1730) |
| `openocd_manual.txt` | 28 | **generated** from the installed openocd |
| `stm32f4_hal.txt` | 94 | **generated** from the on-disk F4 firmware |

Run `python3 scrapes.py list` for live counts and ages.

Every dump here regenerates from `sources.toml`. Nothing in this directory is
now unreproducible.

Roughly half of `arch_wiki.txt` is non-English: ~2,000 localized pages (Русский 478,
Español 448, Português 334, Magyar 288, Français 165, and six smaller). `nixos_wiki.txt`
carries 351 translation pages.

## The options references

Option lookups go to `nixos_options.txt` (24,558) and `home_manager_options.txt`
(5,406). Both are **generated** by `scrapes.py` from the flake this system pins, so
they match what is actually installed rather than what a website showed on the day
someone scraped it. Neither needs the network.

Until 2026-08-14 both NixOS wiki dumps carried their own embedded, web-scraped copies
of the options — 18,441 in `nixos_wiki.txt` (unlabeled, so it read as part of the Zsh
page) and 23,236 in the now-retired `nix_manual_wiki.txt`. Those were stripped.
They documented NixOS
25.11: 349 of their options no longer exist upstream at all, `programs.adb.enable`
among them, verified gone from the pinned nixpkgs. The generated dumps have 1,623
options the old scrape lacked.

`nix_manual_wiki.txt` itself was retired 2026-08-14 — see below.

`audit_dumps.py options` counts slightly low (5,402 of 5,406; 24,510 of 24,558). Its
pattern requires a dotted, lowercase-initial name, so top-level options without a dot
(`lib`, `specialisation`, `uninstall`) and `_module.args` are not counted. They are
present in the dumps — this is a counting artifact, not missing data, and the pattern
is left strict because loosening it would start matching indented prose.

## Why nix_manual_wiki.txt was retired

Deleted 2026-08-14. It had been kept on the belief that it held content
`nixos_wiki.txt` lacked. After `nixos_wiki.txt` was re-scraped that stopped being
true, and a page-set comparison settled it: of its 1,150 pages, **exactly 2** were
not in `nixos_wiki.txt` — a placeholder note, and the `configuration.nix(5)` man
page section, which was 330 lines of `NAME`/`DESCRIPTION`/`OPTIONS` boilerplate.

Everything else it held was a worse copy: older, and code-stripped with 250 bare
`lang=nix` stubs where snippets belonged. Its options listing had already been
superseded by `nixos_options.txt` (24,558 from the pinned flake, against 23,236 from
a 25.11-era web scrape).

The prose was never at risk — `man configuration.nix` renders it on this system, and
it is declaratively reachable at
`config.system.build.manual.nixos-configuration-reference-manpage` if it is ever
wanted as a dump. No generator was written for it: the full render is 388,148 lines
because it re-includes every option, and the useful head is text you can get by
typing `man configuration.nix`.

So: wiki page or config snippet → `nixos_wiki.txt`. Option lookup →
`nixos_options.txt`. The man page → `man configuration.nix`.

## Known extraction artifacts

Both NixOS dumps emit `# ` banners for stray body sentences and list items, not just
real page titles — `# With Zplug:` and `# Manual` are shell comments, not pages. About
55–60% of raw `# ` lines are misparsed this way (arch: 11,019 raw vs 4,359 real;
nixos_wiki: 3,035 raw vs 1,356 real). The
CONTENTS index counts only properly fenced banners, so trust the index over a raw
`grep -c '^# '`. A grep hit whose enclosing banner reads like a sentence is inside a
misparsed section, and page boundaries are unreliable there.

`hypr_waybar_docs.txt` is 100 Hyprland wiki pages plus 3 Waybar docs, and its raw `# `
lines are almost entirely shell comments. Re-scraped 2026-08-14 from the wiki repo's
`main` branch, which the wiki's own version selector calls "Latest Git" — at or just
ahead of the v0.56.0 tag, against a stack running 0.56.1. It is not pinned to an exact
release; if that ever matters, point the manifest at a version branch instead.

`nvim_plugins_docs.txt` was re-scraped 2026-08-14 from the manifest and now matches
the configured plugin set exactly — `audit_dumps.py coverage` reports zero drift in
both directions. Three of its sources are not on GitHub (`nvim-dap` and `nvim-lint` on
codeberg, `rainbow-delimiters` on gitlab, which ships vim help files rather than a
README), which is why `sources.toml` carries full URLs rather than owner/repo.

`cortex_debug_docs.txt` is small but load-bearing: `debug_attributes.md` is the
launch.json schema for the VS Code debug adapter that `nvim-dap-cortex-debug` drives.
`svdFile` and `runToEntryPoint` had zero hits anywhere before it existed. Its
CHANGELOG is deliberately not included — 861 lines of release notes, not reference.

## Tooling

Four stdlib-only scripts live here. All are safe to re-run.

`scrapes.py` — produces and refreshes every dump from `sources.toml`.

```
python3 scrapes.py list                 manifest entries, page counts, ages
python3 scrapes.py scrape NAME...       fetch -> index -> audit -> promote on pass
python3 scrapes.py update --stale 60    re-scrape anything past the threshold
python3 scrapes.py audit                gate the live dumps
                   --dry-run            fetch and audit, never promote
                   --force              promote despite blockers
```

**Promotion is gated and atomic.** A candidate is written to `<name>.txt.new`,
indexed, and audited; it replaces the live dump only if it passes. A failing
candidate is kept as `.new` for inspection and the live file is untouched — a
scrape takes minutes, these files are not in git, and a truncated run must never
be able to destroy a good dump.

The gate blocks on: page/option count below the manifest floor, a count under 90%
of the dump being replaced, a missing sentinel string, or any fetch error. It warns
on dropped code blocks, misparsed banners, and reference data filed under a wrong
banner. Each check corresponds to a defect actually found in these dumps.

### PDFs

`kind = "pdf"` takes `urls` (remote), `files` (local paths), or both, and extracts
with `pdftotext -layout` — `-layout` because it preserves column alignment, which is
the difference between a readable register table and a scrambled one. **One PDF page
becomes one dump page**, so an index entry reads `... — page 12` and a citation by
page number resolves directly.

The PDF itself is discarded after extraction; the manifest holds the URL. Two inputs
are rejected rather than turned into a bad dump: a file whose magic bytes are not
`%PDF` (vendors serve HTML error pages from `.pdf` URLs), and a PDF with no text
layer (an image-only scan, which pdftotext reads as zero pages — not as thin ones,
so it is checked separately).

`index_dumps.py` — adds, removes, and verifies the CONTENTS indexes.

```
python3 index_dumps.py                 index every *.txt here (rebuilds if present)
python3 index_dumps.py --check         verify entries resolve; exit 1 on mismatch
python3 index_dumps.py --strip FILE    remove the index, restoring the original
python3 index_dumps.py --dry-run       report changes, write nothing
```

Re-running is idempotent: an existing index is detected and rebuilt, never stacked.
`--strip` restores the pre-index file byte-for-byte.

The header also carries the dump's **scrape** date, set with `--scraped YYYY-MM-DD`
and preserved across re-indexes. It has to live there: indexing rewrites the file,
so mtime records the last index run, not the scrape.

`audit_dumps.py` — the analyses that found everything documented above.

```
python3 audit_dumps.py pages [--translations]     true vs raw page counts
python3 audit_dumps.py compare A B                title/token overlap, code-block loss
python3 audit_dumps.py options [A B]              options reference stats and diff
python3 audit_dumps.py stale [--days N]           scrape age per dump
python3 audit_dumps.py coverage [--config F]      nvim plugin docs vs configured
python3 audit_dumps.py verify FILE [--against ...] promotion gate; exit 1 on block
```

`verify` is the gate `scrapes.py` calls before promoting; run it by hand to check a
candidate without scraping.

Run `pages` rather than `grep -c '^# '`; the raw count is inflated by roughly 60%.
Run `coverage` after changing Neovim plugins to see what the docs no longer match.

## Regenerating

Everything in `sources.toml` regenerates with `scrapes.py scrape <name>`, or
`scrapes.py update --stale N` for whatever has aged out.

The `mediawiki` kind is proven on both wikis (NixOS 1,356 pages, Arch 4,349), so the
old standalone `scrape_arch_wiki.py` was retired 2026-08-14.

It skips redirects by default (`apfilterredir=nonredirects`). This matters: the Arch
wiki has 16,250 entries in namespace 0 but only 4,349 real articles — including the
redirects produced a dump that was 73% one-line stubs. Override with `filterredir` in
`sources.toml` if a wiki ever needs them.

Every dump is manifest-driven; there are no hand-maintained files left here.
