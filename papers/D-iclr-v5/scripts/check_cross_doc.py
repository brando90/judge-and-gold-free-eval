#!/usr/bin/env python
"""Test appendix.tex's promise that every number in it also appears in the extended appendix.

appendix.tex states: "Every number in this condensed appendix also appears in the extended appendix."
That was an assertion, not a check, and it shipped false: the two files printed -0.164 vs -0.165 and
-0.091 [-0.140,-0.050] vs -0.090 [-0.140,-0.051] for the same two quantities, from the v5 base commit
until round 6. Six reviews read past it.

check_numbers.py cannot catch this class. It asks "does this number exist in some source?", and both
-0.164 and -0.165 do, since the producer value -0.1645 rounds to either. Its three ledger guards all
compare a document against the ledger TABLE; none compares one document against the other. The real
class is "the same quantity printed in two documents", and the ledger is only its most visible member.

Method: split both appendices into sentences, bucket by the first 80 characters (the extended appendix
often expands a sentence, so whole-sentence similarity misses the very pairs that matter), and report
any matched pair whose multiset of numbers differs. Legitimate condensation shows up here too, so this
prints a report to read rather than a pass/fail: the extended appendix may carry EXTRA numbers, but a
number in the condensed file that is absent from its twin is a defect.

KNOWN BLIND SPOT: this reads only the two .tex sources and does NOT resolve \\input, so numbers that
live in generated tables/*.tex are invisible to it. Example: the exact-scorer swap values +5.25 and
-5.41 ship inside tables/r4_rotation.tex, which appendix_extended.tex \\inputs, yet neither string
occurs in that file, so quoting them in appendix.tex would be reported as a violation that is not one.
Before "fixing" a MISSING NUMBER, grep tables/ as well; the number may already ship.

Usage: python3 scripts/check_cross_doc.py [condensed.tex extended.tex]
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent

NUM = re.compile(r"[-+]?\d+(?:\.\d+)?")
# Drop cross-references and float/label machinery: they carry digits that legitimately differ.
STRIP = re.compile(r"\\(?:cref|Cref|ref|label|cite[pt]?|input|includegraphics|begin|end)\{[^}]*\}"
                   # Dimensions are layout, never results. Without this, a column width leaks through
                   # as a "number": \begin{longtable}{L{3.5cm}L{9.5cm}} reported 9.5 as missing from
                   # the extended appendix, and copying it across to satisfy the check would have been
                   # a false fix. A checker that cries wolf gets muted, so strip these.
                   r"|\d+(?:\.\d+)?\s*(?:cm|mm|pt|em|ex|in|bp|sp)\b"
                   r"|Section~\d+ of the paper|\\[a-zA-Z]+")
# For KEYS only, also drop a command together with its braced argument. The extended appendix often
# inserts one early in a sentence (e.g. "(\texttt{claude-opus-5})"), which shifts the prefix and made
# the first version of this script miss the very pair it was written to catch: -0.164 vs -0.165.
KEYSTRIP = re.compile(r"\\[a-zA-Z]+\s*\{[^}]*\}|\\[a-zA-Z]+|Section~\d+ of the paper")

INPUT = re.compile(r"\\input\{([^}]*)\}")


def read_expanded(path):
    """Read a .tex file with one level of \\input substituted in. TRIED AND DELIBERATELY NOT USED.

    The motivation was sound: numbers living in generated tables/*.tex are invisible to the checks
    below, so quoting +0.12 [-0.07,+0.30] in appendix.tex raised a MISSING NUMBER even though
    tables/r4_rotation.tex prints it. But wiring this in COST MORE THAN IT BOUGHT. Measured against
    the controls: the positive control fell from 4 detected defects to 1 (it kept 1011 but lost 28.1,
    -0.050 and -0.164), and the sign-injection control fell from 1 to 0 -- a flipped $-0.164$ to
    $+0.164$ went undetected. The reason is that generated tables carry the CORRECT current values,
    so a stale wrong number in prose is "found" in a table and silently passes.

    That trade is backwards: it removes a cosmetic false positive at the cost of real sensitivity.
    Kept here, unused, so the next person does not re-derive the idea and re-introduce the hole.
    If you ever do wire it in, re-run both controls first and require 4 and 1.
    """
    src = path.read_text(errors="ignore")

    def sub(m):
        name = m.group(1).strip()
        rel = name if name.endswith(".tex") else name + ".tex"
        # Try the file's own directory first, then the paper directory. Without the fallback a file
        # analysed out of tree (say a copy in /tmp, which is how you validate this script against an
        # old commit) resolves NONE of its inputs while the in-tree side resolves all of them, and
        # the comparison fills with hundreds of spurious "missing" numbers.
        for cand in (path.parent / rel, PAPER / rel):
            try:
                return "\n" + cand.read_text(errors="ignore") + "\n"
            except OSError:
                continue
        return m.group(0)

    return INPUT.sub(sub, src)


def sentences(path):
    # NOT read_expanded: see the note on that function. Resolving \input masked real defects.
    src = path.read_text(errors="ignore")
    src = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("%"))
    src = re.sub(r"\s+", " ", src)
    out = []
    for s in re.split(r"(?<=[.:;])\s+(?=[A-Z\\$])", src):
        s = s.strip()
        if len(s) >= 60:
            out.append(s)
    return out


def numbers(s):
    return sorted(NUM.findall(STRIP.sub(" ", s)))


def key(s):
    # Letters only: the key must NOT contain digits. A first version kept them, so two sentences
    # differing solely in the number under comparison got different keys, were never paired, and the
    # script was structurally blind to its own motivating defect (-0.164 vs -0.165). The give-away was
    # that the mismatch count was identical before and after that defect was fixed.
    return re.sub(r"[^a-z]", "", KEYSTRIP.sub(" ", s).lower())[:80]


def main():
    args = sys.argv[1:]
    cond = Path(args[0]) if args else PAPER / "appendix.tex"
    ext = Path(args[1]) if len(args) > 1 else PAPER / "appendix_extended.tex"
    if not cond.exists() or not ext.exists():
        print("cross-doc check skipped: one of the appendices is missing")
        return 0

    ext_by_key = {}
    for s in sentences(ext):
        ext_by_key.setdefault(key(s), []).append(s)

    mismatches, matched = [], 0
    for s in sentences(cond):
        k = key(s)
        if len(k) < 30 or k not in ext_by_key:
            continue
        matched += 1
        want, have = numbers(s), numbers(ext_by_key[k][0])
        missing = [n for n in want if n not in have]
        if missing:
            mismatches.append((missing, s, ext_by_key[k][0]))

    # The direct test of the claim, and the stronger of the two. Sentence pairing needs a twin to
    # compare against, so it rates a number benign when the twin was reorganised and misses one whose
    # sentence has no twin at all -- which is exactly how 1,011 and 28.1 survived the pairing pass.
    # This asks only what appendix.tex actually promises: does every number in it appear SOMEWHERE?
    def all_numbers(path):
        # NOT read_expanded: see the note on that function. Resolving \input masked real defects.
        src = path.read_text(errors="ignore")
        src = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("%"))
        src = STRIP.sub(" ", src)
        src = re.sub(r"(?<=\d),(?=\d{3}\b)", "", src)  # 1,011 -> 1011
        return [m.group().lstrip("+") for m in NUM.finditer(src)]

    ca, ea = all_numbers(cond), all_numbers(ext)
    # Sign-SENSITIVE. An earlier version unioned both signs here to absorb "+0.045" vs "0.045", and
    # that made the test blind to sign: flipping $-0.164$ to $+0.164$ in the extended appendix --
    # inverting the paper's central grading result -- still reported clean. all_numbers() already
    # strips a leading "+", which gives the notation tolerance without discarding direction.
    seen = set(ea)
    absent = sorted({x for x in ca if x not in seen}, key=lambda s: (len(s), s))
    raw = cond.read_text(errors="ignore")
    for v in absent:
        i = raw.find(v)
        if i < 0:  # thousands separator: 1011 is written 1,011 in the source
            i = raw.find(f"{v[:-3]},{v[-3:]}") if len(v) > 3 else -1
        ctx = re.sub(r"\s+", " ", raw[max(0, i - 120):i + 80]) if i >= 0 else "(context not located)"
        print(f"MISSING NUMBER: {v} appears in {cond.name} but nowhere in {ext.name}\n  ...{ctx}")
    if absent:
        print(f"-- {len(absent)} number(s) missing entirely; {cond.name}'s claim is false --")
    else:
        print(f"direct test: every number in {cond.name} appears somewhere in {ext.name}")

    print(f"cross-doc: matched {matched} sentence pairs between {cond.name} and {ext.name}")
    for missing, a, b in mismatches:
        print(f"\nCROSS-DOC MISMATCH: {missing} in {cond.name} but not its twin")
        print(f"  condensed: {a[:200]}")
        print(f"  extended : {b[:200]}")
    if not mismatches:
        print("cross-doc: every number in the condensed appendix appears in its extended twin")
    print(f"\n{len(mismatches)} sentence pairs disagree", file=sys.stderr)
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
