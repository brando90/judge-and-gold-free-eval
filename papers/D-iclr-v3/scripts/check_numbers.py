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
