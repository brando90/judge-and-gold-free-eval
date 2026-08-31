# Analysis for the MACE domain-diversity extension. Predictions P-MC1..P-MC3 were pinned in
# scripts/build_mace_tasks.py and committed before any MACE generation existed; this producer
# is written while generation runs and before any MACE score file exists, and it scores those
# predictions with the frozen estimator machinery used throughout the paper.
#
# Populations. NON-MATH = River + Language (the audited entity domains, absent-from-list rates
# 2.3% and 8.1%). MATH = the exact-oracle control (2000/2000 shipped answer sets verified equal
# to computed truth). Reporting is always split so that a divergence between them is visible
# rather than averaged away.
#
# Estimators, identical to the rest of the paper:
#   inflation = excess hack gap at n=64 via scripts/bon_analysis.py (rubric a selects, rubric b
#     reports, within-oracle-stratum permutation null), per-item paired referenced-minus-blind
#     delta, item-level cluster bootstrap (NBOOT=1000, numpy default_rng(0))
#   margin    = mean score of reference-matching valid samples minus other valid samples,
#     item mean, same bootstrap; defined only where both groups are present
#   step      = mean paired delta over k>1 items minus the same over k=1 items (P-MC1)
# Items enter the inflation deltas only if their pool pass rate lies in [0.05, 0.95], the band
# used by the k-stratified experiment.
#
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/mace_analysis.py
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)
rng = np.random.default_rng(0)
NBOOT = 1000
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
POOL = "runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"


def norm(a):
    return re.sub(r"[^a-z0-9]+", "", a.strip().casefold())


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


def bci(v):
    v = np.asarray(v, float)
    if len(v) < 3:
        return None
    b = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(NBOOT)]
    return round(float(v.mean()), 3), [round(float(np.percentile(b, 2.5)), 3),
                                       round(float(np.percentile(b, 97.5)), 3)], len(v)


need = [POOL] + [f"runs/bon_scores_mace/mace__{j}__{c}_{r}.jsonl"
                 for j in JUDGES for c in ("noref", "ref") for r in ("a", "b")]
missing = [f for f in need if not os.path.exists(f)]
if missing:
    print("[mace_analysis] pre-data: missing", len(missing), "file(s), e.g.", missing[0])
    print("  P-MC1..P-MC3 remain unscored. Nothing written.")
    raise SystemExit

tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/mace_tasks.jsonl")}
pool = {}
for l in open(POOL):
    r = json.loads(l)
    if "oracle" not in r:
        continue
    t = tasks[r["problem_id"]]
    r["k"] = t["k"]
    r["domain"] = t["params"]["domain"]
    r["ref_answer"] = t["ref_answer"]
    r["valid_answers"] = t["valid_answers"]
    pool[r["problem_id"]] = r


def scores(j, c, rep):
    f = f"runs/bon_scores_mace/mace__{j}__{c}_{rep}.jsonl"
    return {x["problem_id"]: x["escore"] for x in (json.loads(l) for l in open(f))}


out = {"n_items": len(pool), "predictions": {}}
groups = {"nonmath": lambda d: d in ("River", "Language"),
          "math": lambda d: d == "Math",
          "River": lambda d: d == "River", "Language": lambda d: d == "Language"}

print(f"pool: {len(pool)} items")
print("\n=== P-MC1 / P-MC3: paired referenced-minus-blind inflation delta, and the k-step")
for j in JUDGES:
    sa_n, sb_n = scores(j, "noref", "a"), scores(j, "noref", "b")
    sa_r, sb_r = scores(j, "ref", "a"), scores(j, "ref", "b")
    gaps = {}
    for cond, (sa, sb) in (("noref", (sa_n, sb_n)), ("ref", (sa_r, sb_r))):
        g = {}
        for pid, it in pool.items():
            if pid not in sa:
                continue
            pr = float(np.mean(it["oracle"]))
            if not (0.05 <= pr <= 0.95):
                continue
            c = ns["per_item_curves"](it, sa[pid], sb[pid])
            g[pid] = c[64]["judge_gain"] - c[64]["true_gain"] - ns["permutation_null"](it, sa[pid], sb[pid])
        gaps[cond] = g
    ids = [p for p in gaps["ref"] if p in gaps["noref"]]
    for gname, gf in groups.items():
        d1 = [gaps["ref"][p] - gaps["noref"][p] for p in ids if gf(pool[p]["domain"]) and pool[p]["k"] == 1]
        dg = [gaps["ref"][p] - gaps["noref"][p] for p in ids if gf(pool[p]["domain"]) and pool[p]["k"] > 1]
        r1, rg = bci(d1), bci(dg)
        step = bci([x - float(np.mean(d1)) for x in dg]) if (d1 and dg) else None
        out["predictions"].setdefault(j, {})[gname] = dict(k1=r1, kgt1=rg, step=step)
        f = lambda x: "n/a" if x is None else f"{x[0]:+.3f} [{x[1][0]:+.3f},{x[1][1]:+.3f}] n={x[2]}"
        print(f"  {j:26s} {gname:9s} k=1 {f(r1):28s} k>1 {f(rg):28s} step {f(step)}")

print("\n=== P-MC2: anchoring margins at k>1 (rubric a)")
for j in JUDGES:
    for cond in ("ref", "noref"):
        sa = scores(j, cond, "a")
        for gname in ("nonmath", "math"):
            gf = groups[gname]
            vals = []
            for pid, it in pool.items():
                if it["k"] <= 1 or pid not in sa or not gf(it["domain"]):
                    continue
                refn = norm(it["ref_answer"])
                ms, os_ = [], []
                for i, ok in enumerate(it["oracle"]):
                    if not ok:
                        continue
                    a = norm(boxed(it["samples"][i]) or it["samples"][i][-200:])
                    (ms if (a == refn or (len(refn) > 3 and refn in a)) else os_).append(sa[pid][i])
                if ms and os_:
                    vals.append(float(np.mean(ms) - np.mean(os_)))
            r = bci(vals)
            out.setdefault("margins", {}).setdefault(j, {})[f"{cond}_{gname}"] = r
            f = "n/a" if r is None else f"{r[0]:+.3f} [{r[1][0]:+.3f},{r[1][1]:+.3f}] n={r[2]}"
            print(f"  {j:26s} {cond:6s} {gname:9s} margin {f}")

json.dump(out, open("../../papers/analysis/mace_results.json", "w"), indent=1)
print("\nwrote ../../papers/analysis/mace_results.json")
