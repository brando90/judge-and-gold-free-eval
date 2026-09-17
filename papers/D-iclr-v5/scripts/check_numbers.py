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
                # The post hoc blind-accepted filter quoted in tab:rotation's caption lives here, not in
                # any JSON: "gainers +4.99 [+4.69, +5.32] vs +4.97 unfiltered (Qwen-7B, 91% retained),
                # +4.08 vs +4.09 (phi-4, 98% retained)". Without this file, +4.69 was flagged for seven
                # rounds and cleared by the prose note "a CI bound quoted in a caption", which read as
                # harmless and nearly got the sentence deleted as unsourced. Clear flags by naming the
                # source, not by describing them.
                D / "RESULTS_SUMMARY.md",
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
    # argv wins OUTRIGHT. Previously the project copy was listed first, so a path passed on the
    # command line was silently discarded whenever the project copy existed: running the checker on
    # a deliberately mangled copy still printed "rows sum to 290, matching the printed total",
    # because it had read a different file. That makes a guard's success indistinguishable from it
    # checking the wrong document, and the supplement workflow depends on this argument.
    argv_app = [Path(a) for a in sys.argv[1:] if Path(a).name == "appendix.tex"]
    candidates = argv_app or [PAPER / "appendix.tex", PAPER / "paper" / "appendix.tex"]
    src = next((c.read_text(errors="ignore") for c in candidates if c.exists()), None)
    read_from = next((c for c in candidates if c.exists()), None)
    if read_from is not None:
        print(f"ledger guards reading: {read_from}")
    if src is None:
        return []
    i = src.find(r"\label{tab:ledger-totals}")
    if i < 0:
        return []
    block = src[i:src.find(r"\end{tabular}", i)]
    # Any number of verdict columns: the table gains one per round, so do not hardcode two.
    rows = []
    for line in block.splitlines():
        m = re.match(r"^\s*([A-Za-z][^&]*?)\s*&\s*((?:\d+\s*&\s*)*\d+)\s*\\\\", line)
        if m:
            rows.append((m.group(1), [int(x) for x in re.findall(r"\d+", m.group(2))]))
    body = [r for r in rows if not r[0].strip().lower().startswith("total")]
    total = [r for r in rows if r[0].strip().lower().startswith("total")]
    if not body or not total:
        return []
    ncol = len(total[0][1])
    if any(len(r[1]) != ncol for r in body):
        print("LEDGER MISMATCH: rows of tab:ledger-totals do not all have the same number of columns")
        return []
    out = []
    for col in range(ncol):
        s = sum(r[1][col] for r in body)
        printed = total[0][1][col]
        out.append(str(s))
        if printed != s:
            print(f"LEDGER MISMATCH: column {col + 1} rows sum to {s}, table prints {printed}")
        else:
            print(f"ledger column {col + 1}: rows sum to {s}, matching the printed total")
    for r in body:
        out.extend(str(v) for v in r[1])
    # The main text quotes the ledger's size across all columns, so emit the pooled total too:
    # checking each column against its own total cannot catch a figure equal to one column alone.
    out.append(str(sum(v for r in body for v in r[1])))
    return out


def ledger_caption():
    """Check tab:ledger-failures' caption against tab:ledger-totals.

    The totals table is verified column-by-column above, but its counts are also restated in prose
    in the caption below it. That prose went stale twice: once when round 27 was folded in and once
    when round 30 was, each time under-reporting the paper's own failures. Checking the table against
    itself cannot catch that, so compare the caption's numbers with the row sums.
    """
    # argv wins OUTRIGHT. Previously the project copy was listed first, so a path passed on the
    # command line was silently discarded whenever the project copy existed: running the checker on
    # a deliberately mangled copy still printed "rows sum to 290, matching the printed total",
    # because it had read a different file. That makes a guard's success indistinguishable from it
    # checking the wrong document, and the supplement workflow depends on this argument.
    argv_app = [Path(a) for a in sys.argv[1:] if Path(a).name == "appendix.tex"]
    candidates = argv_app or [PAPER / "appendix.tex", PAPER / "paper" / "appendix.tex"]
    src = next((c.read_text(errors="ignore") for c in candidates if c.exists()), None)
    read_from = next((c for c in candidates if c.exists()), None)
    if read_from is not None:
        print(f"ledger guards reading: {read_from}")
    if src is None:
        return
    i = src.find(r"\label{tab:ledger-totals}")
    if i < 0:
        return
    block = src[i:src.find(r"\end{tabular}", i)]
    sums = {}
    for line in block.splitlines():
        m = re.match(r"^\s*([A-Za-z][^&]*?)\s*&\s*((?:\d+\s*&\s*)*\d+)\s*\\\\", line)
        if m:
            name = m.group(1).split("(")[0].strip().lower()
            if not name.startswith("total"):
                sums[name] = sum(int(x) for x in re.findall(r"\d+", m.group(2)))
    cap = re.search(r"rows contain\s+(\d+)\s+not confirmed,\s+(\d+)\s+falsified,\s+(\d+)\s+split,"
                    r"\s+(\d+)\s+not evaluable,\s+and\s+(\d+)\s+not scored", src)
    if not cap or not sums:
        return
    for verdict, stated in zip(("not confirmed", "falsified", "split", "not evaluable", "not scored"),
                               (int(g) for g in cap.groups())):
        actual = sums.get(verdict)
        if actual is None:
            continue
        if actual != stated:
            print(f"LEDGER CAPTION MISMATCH: caption says {stated} {verdict}, rows sum to {actual}")
        else:
            print(f"ledger caption: {verdict} = {stated}, matching the rows")
    m = re.search(r"the\s+(\d+)\s+excluded ones", src)
    if m and "excluded" in sums and int(m.group(1)) != sums["excluded"]:
        print(f"LEDGER CAPTION MISMATCH: caption says {m.group(1)} excluded, rows sum to {sums['excluded']}")

    # The extended appendix restates the same counts in its own prose. That sentence is what shipped
    # stale (290 against the paper's 321), so guard it against the same row sums rather than fixing
    # only the two copies found so far.
    ext = next((p.read_text(errors="ignore") for p in
                (PAPER / "appendix_extended.tex", PAPER / "paper" / "appendix_extended.tex")
                if p.exists()), None)
    if ext is None:
        return
    e = re.search(r"ledger records\s+(\d+)\s+confirmed,\s+(\d+)\s+not confirmed,\s+and\s+(\d+)\s+falsified,"
                  r"\s+of\s+(\d+)", ext)
    if not e:
        # Fail loudly. A silent return is indistinguishable from success, so rewording the prose
        # would quietly drop the guard while the other lines still print "matching".
        print("LEDGER GUARD NOT FOUND: the extended appendix's ledger sentence did not match; guard skipped")
        return
    grand = sum(sums.values())
    # The same sentence continues with the four remaining verdicts. Split is the count that went
    # stale last round, so guard it too; require digits rather than a spelled-out number.
    tail = re.search(r"(\d+)\s+predictions registered for several judges[^.]*?"
                     r"(\d+)\s+could not be evaluated,\s*(\d+)\s+were not scored, and\s+(\d+)\s+", ext)
    if tail:
        for label, stated, actual in (("split", int(tail.group(1)), sums.get("split")),
                                      ("not evaluable", int(tail.group(2)), sums.get("not evaluable")),
                                      ("not scored", int(tail.group(3)), sums.get("not scored")),
                                      ("excluded", int(tail.group(4)), sums.get("excluded"))):
            if actual is None:
                continue
            if stated != actual:
                print(f"EXTENDED LEDGER MISMATCH: prose says {stated} {label}, rows give {actual}")
            else:
                print(f"extended ledger prose: {label} = {stated}, matching the rows")
    else:
        print("LEDGER GUARD NOT FOUND: the extended appendix's split/evaluable/scored/excluded counts "
              "did not match (is a number spelled out as a word?); those four are unguarded")
    for label, stated, actual in (("confirmed", int(e.group(1)), sums.get("confirmed")),
                                  ("not confirmed", int(e.group(2)), sums.get("not confirmed")),
                                  ("falsified", int(e.group(3)), sums.get("falsified")),
                                  ("total", int(e.group(4)), grand)):
        if actual is None:
            continue
        if stated != actual:
            print(f"EXTENDED LEDGER MISMATCH: prose says {stated} {label}, rows give {actual}")
        else:
            print(f"extended ledger prose: {label} = {stated}, matching the rows")


known.update(ledger_totals())
ledger_caption()

# numbers that are structural, not results
TRIVIAL = {str(i) for i in range(0, 21)} | {"32", "64", "100", "91", "31", "30", "2026", "2027", "95", "0.5",
                                            "1.0", "0.2", "0.8", "10.0"}

bad = 0
# The extended appendix ships in the supplement and was unguarded until round 4, which is how its
# ledger prose kept a stale total (290) after the paper moved to 321. Scan it whenever it is present.
targets = sys.argv[1:] or [str(p) for p in (PAPER / "main.tex", PAPER / "appendix.tex",
                                            PAPER / "appendix_extended.tex") if p.exists()]
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
