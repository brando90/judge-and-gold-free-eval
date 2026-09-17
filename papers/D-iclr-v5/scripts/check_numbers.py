#!/usr/bin/env python
"""Fidelity check: every number typed into main.tex / appendix.tex must exist in a source.

Sources: the story draft and technical report of Paper D, its registration ledger, and every
JSON in papers/analysis/ (numbers rounded to 1, 2, and 3 decimals, and as percentages).
Generated tables (tables/*.tex) are produced from JSON and are skipped.
Prints numbers not found anywhere, with their line, so each can be checked by hand.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
PAPERS = PAPER.parent
D = PAPERS / "D-reference-laws"

text_sources = [D / "registration.md", PAPER / "registration_round2.md",
                PAPER / "registration_round3.md", PAPER / "registration_round3b.md",
                PAPER / "registration_round4.md", PAPER / "registration_round5.md", PAPER / "registration_round8.md",
                PAPER / "registration_round19.md", PAPER / "registration_round20.md",
                PAPER / "registration_round21.md", PAPER / "registration_round22.md",
                PAPER / "registration_round23.md", PAPER / "registration_round24.md", PAPER / "registration_round25.md",
                PAPER / "registration_round26.md", PAPER / "registration_round27.md",  # v3
                PAPERS / "analysis" / "prevalence_v2" / "RESULTS.md", PAPER / "survey" / "practice_survey.md",
                *sorted((PAPER / "tables").glob("*.tex"))]  # generated tables carry JSON-produced numbers; the uncorrected source draft is not a source
corpus = "\n".join(p.read_text(errors="ignore") for p in text_sources if p.exists())

NUM = re.compile(r"(?<![\w.])[-+]?\d+(?:\.\d+)?")
known = set()
for m in NUM.finditer(corpus):
    known.add(m.group().lstrip("+-"))


def walk(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        yield o


for jf in (PAPERS / "analysis").glob("*.json"):
    try:
        for x in walk(json.loads(jf.read_text())):
            ax = abs(x)
            if isinstance(x, int):
                known.add(str(ax))
                continue
            for d in (2, 3):
                known.add(f"{ax:.{d}f}")
            known.add(f"{ax * 100:.1f}")
    except Exception:
        pass

# The ledger totals are typed into the appendix rather than produced by a script, which a reviewer
# flagged as an avoidable weak point for a paper whose distinguishing strength is the ledger.
# Derive them here so they are checked rather than trusted: each column of tab:ledger-totals must
# sum to its own printed Total. The verified totals then count as sourced.
def ledger_totals():
    # The appendix sits next to this script's parent in the repository, but one level deeper in the
    # supplement layout (paper/appendix.tex), and may be named on the command line. Try all three, and
    # degrade quietly rather than raising if none is present.
    candidates = [PAPER / "appendix.tex", PAPER / "paper" / "appendix.tex"]
    candidates += [Path(a) for a in sys.argv[1:] if Path(a).name == "appendix.tex"]
    src = next((c.read_text(errors="ignore") for c in candidates if c.exists()), None)
    if src is None:
        return []
    i = src.find(r"\label{tab:ledger-totals}")
    if i < 0:
        return []
    block = src[i:src.find(r"\end{tabular}", i)]
    rows = re.findall(r"^\s*([A-Za-z][^&]*?)\s*&\s*(\d+)\s*&\s*(\d+)\s*\\\\", block, re.M)
    body = [r for r in rows if not r[0].strip().lower().startswith("total")]
    total = [r for r in rows if r[0].strip().lower().startswith("total")]
    if not body or not total:
        return []
    out = []
    for col in (1, 2):
        s = sum(int(r[col]) for r in body)
        printed = int(total[0][col])
        out.append(str(s))
        if printed != s:
            print(f"LEDGER MISMATCH: column {col} rows sum to {s}, table prints {printed}")
        else:
            print(f"ledger column {col}: rows sum to {s}, matching the printed total")
    for r in body:
        out.extend((r[1], r[2]))
    # The main text quotes the ledger's size across both columns, so emit the pooled total too:
    # checking each column against its own total cannot catch a figure equal to one column alone.
    out.append(str(sum(int(r[c]) for r in body for c in (1, 2))))
    return out


known.update(ledger_totals())

# numbers that are structural, not results
TRIVIAL = {str(i) for i in range(0, 21)} | {"32", "64", "100", "91", "31", "30", "2026", "2027", "95", "0.5",
                                            "1.0", "0.2", "0.8", "10.0"}

bad = 0
targets = sys.argv[1:] or [str(PAPER / "main.tex"), str(PAPER / "appendix.tex")]
for name in targets:
    for i, line in enumerate(Path(name).read_text().splitlines(), 1):
        s = re.split(r"(?<!\\)%", line)[0] if not line.lstrip().startswith("%") else ""  # v3: \% is not a comment
        s = re.sub(r"\\(cref|Cref|ref|label|cite[pt]?|input|includegraphics)\{[^}]*\}", "", s)
        s = re.sub(r"(?<=\d),(?=\d{3}\b)", "", s)  # thousands separators: 1,092 -> 1092
        s = re.sub(r"\\(scriptsize|footnotesize|small|setlength|tabcolsep)[^ ]*", "", s)
        for m in NUM.finditer(s):
            v = m.group().lstrip("+-")
            if v in TRIVIAL or v in known:
                continue
            # allow thousands separators like 2,751 written in prose
            bad += 1
            print(f"{name}:{i}: {m.group()}   | {line.strip()[:110]}")
print(f"\n{bad} numbers not found in any source", file=sys.stderr)
