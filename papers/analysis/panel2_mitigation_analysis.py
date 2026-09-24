"""POST HOC (no registration weight): the second-panel mitigation grid, tab:panel2-mitig.

WHY THIS FILE EXISTS. The paper's AI-use statement says every number in it is produced by a
committed analysis script from stored model outputs. That was not true of this table. Its 50 cells
were computed ad hoc during the 2026-09-18/19 run and typed straight into appendix.tex; no producer
was ever committed. The numbers themselves are correct -- this script reproduces all 30 printed
point estimates to the printed precision -- but until now nothing in the repository could show that.
This closes the gap. If a cell here disagrees with the table, the table is wrong.

THE ESTIMATOR, recovered from the run files and from the comment block in
experiments/tfa-vs-judge/scripts/v4_judge_prompts.py (which quotes bare -0.204 for GPT-4.1 and
-3.419 for Qwen2.5-7B, the same two numbers to three decimals):

  keep rows with candidate_valid true and, on MACE, group == "nonmatch"
      (the 'group' field exists only on MACE rows; replication rows carry correctness in
       candidate_valid alone, which is the pool difference that cost this project a day earlier on)
  a candidate is (question_id, sample)
  delta(candidate) = mean(grade | C1_differ) - mean(grade | C0)
  estimate = unweighted mean of delta over candidates that have both conditions

'grade' is an int 0-10 or the string "NA"; non-numeric grades are dropped, not read as zero.
Intervals are an item-clustered bootstrap over question_id, 10,000 resamples, matching the caption.
The original run recorded no seed, so bounds can differ from the printed ones in the second decimal;
SEED below fixes ours so this script is reproducible going forward.

THE GRID IS NOT RECTANGULAR. MACE has all six judges under all five arms. The replication pool has
only four: GPT-4.1 and Sonnet 5 were run there on the bare arm alone, so their four mitigation cells
do not exist. That is missing data, not a typesetting omission, and the table is right to omit the
rows. Their unprinted bare values are computed here anyway (--all) because a reader may reasonably
ask why those two judges were dropped, and the answer is that their bare effect is already ~0.
"""

import argparse
import json
import os
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent.parent / "experiments" / "tfa-vs-judge" / "runs" / "v4_judge"
OUT = HERE / "panel2_mitigation_results.json"
SEED, B = 20260918, 10000

ARMS = ["None", "Several", "Forbid", "CoT", "Verify"]

# Filenames are irregular: the same judge changes prefix between arms, and GPT-4.1 uses the older
# r10 naming. Enumerated explicitly rather than globbed, because a naive glob silently drops cells.
FILES = {
    ("MACE", "Qwen2.5-7B"):  ["QWEN_mace_bare", "QWEN_mace_SCAFFOLD", "QWEN7B_mace_FORBID",
                              "QWEN7B_mace_M1", "QWEN7B_mace_M2"],
    ("MACE", "Qwen2.5-14B"): ["QWEN14B_mace_bare", "QWEN14B_mace_SCAFFOLD", "QWEN14B_mace_FORBID",
                              "QWEN14B_mace_M1", "QWEN14B_mace_M2"],
    ("MACE", "gemma-2-9b"):  ["GEMMA_mace_bare", "GEMMA_mace_SCAFFOLD", "GEMMA_mace_FORBID",
                              "GEMMA_mace_M1", "GEMMA_mace_M2"],
    ("MACE", "phi-4"):       ["PHI4_mace_bare", "PHI4_mace_SCAFFOLD", "PHI4_mace_FORBID",
                              "PHI4_mace_M1", "PHI4_mace_M2"],
    ("MACE", "GPT-4.1"):     ["GPT41_mace_r10bare", "GPT41_mace_r10", "GPT41_mace_FORBID",
                              "GPT41_mace_M1", "GPT41_mace_M2"],
    ("MACE", "Sonnet 5"):    ["SONNET_mace_bare", "SONNET_mace_SCAFFOLD", "SONNET_mace_FORBID",
                              "SONNET_mace_M1", "SONNET_mace_M2"],
    ("Replication", "Qwen2.5-7B"):  ["QWEN_repl_bare", "QWEN7B_repl_SCAFFOLD", "QWEN7B_repl_FORBID",
                                     "QWEN7B_repl_M1", "QWEN7B_repl_M2"],
    ("Replication", "Qwen2.5-14B"): ["QWEN14B_repl_bare", "QWEN14B_repl_SCAFFOLD",
                                     "QWEN14B_repl_FORBID", "QWEN14B_repl_M1", "QWEN14B_repl_M2"],
    ("Replication", "gemma-2-9b"):  ["GEMMA_repl_bare", "GEMMA_repl_SCAFFOLD", "GEMMA_repl_FORBID",
                                     "GEMMA_repl_M1", "GEMMA_repl_M2"],
    ("Replication", "phi-4"):       ["PHI4_repl_bare", "PHI4_repl_SCAFFOLD", "PHI4_repl_FORBID",
                                     "PHI4_repl_M1", "PHI4_repl_M2"],
}
# Bare-arm only; the four mitigation arms were never run for these two on this pool.
EXTRA = {("Replication", "GPT-4.1"): "BRIDGE_gpt41_repl",
         ("Replication", "Sonnet 5"): "SONNET_repl_bare"}


def num(g):
    try:
        return float(g)
    except (TypeError, ValueError):
        return None


def deltas(stem):
    """Per-candidate C1_differ minus C0, keyed by question_id so the bootstrap can cluster."""
    f = RUNS / f"{stem}.jsonl"
    if not f.exists():
        return None, 0
    cond = defaultdict(lambda: defaultdict(list))   # (qid, sample) -> condition -> grades
    rows = 0
    with open(f) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            rows += 1
            if r.get("candidate_valid") is not True:
                continue
            if r.get("group", "nonmatch") != "nonmatch":      # no-op on replication rows
                continue
            g = num(r.get("grade"))
            if g is None:
                continue
            cond[(r["question_id"], r["sample"])][r["condition"]].append(g)

    by_item = defaultdict(list)
    for (qid, _s), c in cond.items():
        if "C0" in c and "C1_differ" in c:
            by_item[qid].append(sum(c["C1_differ"]) / len(c["C1_differ"])
                                - sum(c["C0"]) / len(c["C0"]))
    return by_item, rows


def estimate(by_item, tag):
    flat = [d for v in by_item.values() for d in v]
    if not flat:
        return None
    point = sum(flat) / len(flat)
    items = list(by_item)
    rng = random.Random(f"{SEED}|{tag}")
    means = []
    for _ in range(B):
        draw = [d for _ in items for d in by_item[rng.choice(items)]]
        means.append(sum(draw) / len(draw))
    means.sort()
    return dict(estimate=round(point, 4),
                ci=[round(means[int(.025 * B)], 4), round(means[int(.975 * B)], 4)],
                n_candidates=len(flat), n_items=len(items))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true",
                    help="also compute the two unprinted replication bare cells")
    ap.add_argument("--check", action="store_true",
                    help="compare every cell against the values printed in appendix.tex")
    a = ap.parse_args()

    if not RUNS.exists():
        sys.exit(f"run files not found: {RUNS}")

    out = defaultdict(dict)
    print(f"  reading {RUNS}")
    for (pool, judge), stems in FILES.items():
        out[pool][judge] = {}
        for arm, stem in zip(ARMS, stems):
            by_item, rows = deltas(stem)
            if by_item is None:
                print(f"    MISSING FILE  {pool}/{judge}/{arm}: {stem}.jsonl", file=sys.stderr)
                continue
            r = estimate(by_item, f"{pool}|{judge}|{arm}")
            r["source"] = f"{stem}.jsonl"
            r["rows"] = rows
            out[pool][judge][arm] = r
            print(f"    {pool:<12}{judge:<14}{arm:<9}{r['estimate']:>8.3f} "
                  f"[{r['ci'][0]:>6.2f},{r['ci'][1]:>6.2f}]  {rows} rows")
    if a.all:
        for (pool, judge), stem in EXTRA.items():
            by_item, rows = deltas(stem)
            if by_item:
                r = estimate(by_item, f"{pool}|{judge}|None")
                r["source"], r["rows"] = f"{stem}.jsonl", rows
                r["note"] = "bare arm only; the four mitigation arms were never run for this cell"
                out[pool].setdefault(judge, {})["None"] = r
                print(f"    {pool:<12}{judge:<14}{'None':<9}{r['estimate']:>8.3f} "
                      f"[{r['ci'][0]:>6.2f},{r['ci'][1]:>6.2f}]  (unprinted)")

    OUT.write_text(json.dumps(out, indent=1))
    print(f"\n  wrote {OUT.relative_to(HERE.parent.parent)}")

    if a.check:
        tex = (HERE.parent / "D-iclr-v6" / "appendix.tex").read_text()
        i = tex.find("\\label{tab:panel2-mitig}")
        body = tex[i:tex.find("\\end{tabular}", i)]
        cell = re.compile(r"\$([+-]?[\d.]+)\$\s*\\ci")
        pool, bad, ok = None, 0, 0
        for line in body.split("\n"):
            if "\\multicolumn" in line and "\\emph" in line:
                pool = "MACE" if "MACE" in line else "Replication"
                continue
            if pool is None or "&" not in line:
                continue
            judge = line.split("&")[0].strip().replace("\\textsc{", "").replace("}", "")
            judge = judge.replace("~", " ").strip()
            vals = cell.findall(line)
            if judge not in out.get(pool, {}) or len(vals) != len(ARMS):
                continue
            for arm, printed in zip(ARMS, vals):
                got = out[pool][judge].get(arm, {}).get("estimate")
                if got is None:
                    continue
                if abs(round(got, 2) - float(printed)) > 0.005:
                    print(f"    MISMATCH {pool}/{judge}/{arm}: table {printed}, computed {got:.3f}")
                    bad += 1
                else:
                    ok += 1
        print(f"\n  check: {ok} cells reproduce the printed table, {bad} disagree")
        sys.exit(1 if bad else 0)
