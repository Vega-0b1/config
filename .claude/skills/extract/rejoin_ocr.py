#!/usr/bin/env python3
"""Rejoin words that OCR split across spaces, using the corpus as its own dictionary.

Scanned books extract with words broken apart — `pri vil eged`, `thi s`, `fi le`.
The fix needs a dictionary, and the document already is one: in a book that says
`privileged` 118 times intact, the intact spellings vastly outnumber the broken
ones, so the corpus itself says which merges are real.

What this does NOT fix: substitutions. `nonnal` for `normal`, `tum` for `turn`,
`Lel` for `Let`. Those are plausible-looking tokens and no frequency method can
see them — they need the page image read by eye. This script is deliberately the
safe half of that job.

Safety rules, in order of how much they matter:
  1. Merge only when the joined form is a corpus word occurring >= MIN_FREQ times.
  2. Merge only when at least one piece is NOT a standalone word — evidence of
     actual damage. `the file` is never merged into `thefile`.
  3. Never merge across anything but a single space.
  4. Skip shell transcripts, preprocessor lines, and symbol-dense lines (code).
     Indentation is NOT a code signal: this extraction indents the first line of
     every paragraph, and treating that as code skips half the body text.

Usage:
    rejoin_ocr.py <corpus.md> <target.md> <output.md>     # target may equal corpus
    rejoin_ocr.py --report <corpus.md> <target.md>        # show merges, write nothing
"""

import collections
import re
import sys

MIN_FREQ = 5        # a joined form must be this common in the corpus to be trusted
MIN_VOCAB_LEN = 3
MIN_VOCAB_FREQ = 3
MAX_SPAN = 5        # most pieces one broken word may be split into
SYMBOL_DENSITY = 0.08

REAL_SHORT = {
    "a", "i", "an", "as", "at", "be", "by", "do", "go", "he", "if", "in", "is",
    "it", "me", "my", "no", "of", "on", "or", "so", "to", "up", "us", "we", "am",
    "the", "id", "os", "ls", "sh", "fd", "pc", "ip", "tcp", "udp",
}

CODE_PREFIXES = ("$", "#include", "#define", "```", "//", "/*", "-rw", "drw")


def build_vocab(corpus_text):
    freq = collections.Counter(
        t.lower() for t in re.findall(r"[A-Za-z]+", corpus_text)
    )
    vocab = {
        w for w, c in freq.items()
        if len(w) >= MIN_VOCAB_LEN and c >= MIN_VOCAB_FREQ
    }
    return freq, vocab


def is_code(line):
    st = line.strip()
    if not st:
        return True
    if st.startswith(CODE_PREFIXES):
        return True
    sym = sum(
        1 for c in st
        if not (c.isalnum() or c.isspace() or c in ".,;:'’()-")
    )
    return sym / len(st) > SYMBOL_DENSITY


def rejoin_line(line, freq, vocab, log):
    if is_code(line):
        return line
    parts = re.split(r"(\W+)", line)
    words = [(i, p) for i, p in enumerate(parts) if p and p[0].isalpha()]
    used = set()
    for wi in range(len(words)):
        if wi in used:
            continue
        for span in range(MAX_SPAN, 1, -1):
            if wi + span > len(words):
                continue
            if any(wi + k in used for k in range(span)):
                continue
            idxs = [words[wi + k][0] for k in range(span)]
            if any(parts[idxs[k] + 1] != " " for k in range(span - 1)):
                continue
            pieces = [words[wi + k][1] for k in range(span)]
            joined = "".join(pieces)
            low = joined.lower()
            if low not in vocab or freq[low] < MIN_FREQ:
                continue
            broken = [
                p for p in pieces
                if p.lower() not in vocab and p.lower() not in REAL_SHORT
            ]
            if not broken:
                continue
            # NOTE: an earlier version also required the joined form to be
            # commoner than each piece standing alone. That backfires: a
            # fragment is frequent precisely BECAUSE the same word keeps
            # breaking the same way. `ow` occurs 51 times against `allow`'s 36,
            # so `all ow` was refused. Rule 2 above — at least one piece must
            # not be a standalone word — is the real safeguard, and it already
            # protects `the file`, `no one`, `so me`, and `in to`.
            parts[idxs[0]] = joined
            for k in range(1, span):
                parts[idxs[k]] = ""
                parts[idxs[k] - 1] = ""
            used.update(wi + k for k in range(span))
            log[(" ".join(pieces), joined)] += 1
            break
    return "".join(parts)


def rejoin_text(corpus_text, target_text, max_passes=4):
    """Rejoin repeatedly until no further merges are found.

    One pass can stop short. A word broken into more than MAX_SPAN pieces gets
    partially assembled — `En c r ypt i` + `on` becomes `Encrypti` + `on`, which
    is still not a word. Because a recurring broken form is itself frequent
    enough to enter the vocabulary, the leftover is mergeable on the next pass.
    Iterating to a fixpoint finishes those instead of leaving a half-repair.
    """
    freq, vocab = build_vocab(corpus_text)
    log = collections.Counter()
    text = target_text
    for _ in range(max_passes):
        pass_log = collections.Counter()
        text = "\n".join(
            rejoin_line(l, freq, vocab, pass_log) for l in text.split("\n")
        )
        if not pass_log:
            break
        log.update(pass_log)
    return text, log


def main(argv):
    report_only = "--report" in argv
    args = [a for a in argv[1:] if a != "--report"]
    if len(args) < (2 if report_only else 3):
        print(__doc__.strip(), file=sys.stderr)
        return 2

    corpus_text = open(args[0], encoding="utf-8").read()
    target_text = open(args[1], encoding="utf-8").read()
    result, log = rejoin_text(corpus_text, target_text)

    heads_before = len(re.findall(r"^#{1,4} .*$", target_text, re.M))
    heads_after = len(re.findall(r"^#{1,4} .*$", result, re.M))

    print(f"merge patterns : {len(log)}")
    print(f"total merges   : {sum(log.values())}")
    print(f"headings       : {heads_before} before, {heads_after} after", end="")
    print("  OK" if heads_before == heads_after else "  ** CHANGED — investigate **")
    print("\nmost frequent merges:")
    for (src, dst), n in log.most_common(15):
        print(f"   {n:5}x  {src!r:34} -> {dst}")

    if heads_before != heads_after:
        print("\nRefusing to write: heading count changed.", file=sys.stderr)
        return 1
    if not report_only:
        open(args[2], "w", encoding="utf-8").write(result)
        print(f"\nwrote {args[2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
