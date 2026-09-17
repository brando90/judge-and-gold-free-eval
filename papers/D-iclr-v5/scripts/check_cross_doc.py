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


def sentences(path):
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
        src = path.read_text(errors="ignore")
        src = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("%"))
        src = STRIP.sub(" ", src)
        src = re.sub(r"(?<=\d),(?=\d{3}\b)", "", src)  # 1,011 -> 1011
        return [m.group().lstrip("+") for m in NUM.finditer(src)]

    ca, ea = all_numbers(cond), all_numbers(ext)
    seen = set(ea) | {x.lstrip("-") for x in ea} | {"-" + x for x in ea}
    absent = sorted({x for x in ca if x not in seen and x.lstrip("-") not in seen},
                    key=lambda s: (len(s), s))
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
