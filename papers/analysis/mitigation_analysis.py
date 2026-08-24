# Registered analysis for the k-stratified structural-mitigation experiment
# (OSF osf.io/qugbd, registered 2026-08-23 22:56 before any data existed).
# Run from experiments/tfa-vs-judge. Estimators are the committed ones used throughout:
#   margin  = mean score of reference-matching valid samples minus other valid samples,
#             item-mean, item bootstrap CI (defined for k > 1)
#   gap     = excess hack gap at n=64 (bon_analysis machinery: rep a selects, rep b reports,
#             within-checker-stratum permutation null)
#   delta   = per-item paired condition-minus-blind gap, item-level cluster bootstrap
# Endpoints per the registration: E1 margins by condition and k; E2 paired gap deltas vs
# blind by condition and k, per judge and pooled.
# Predictions: P-M1 (M1 reduces margin and gap vs single-ref at k>1, keeps k=1 benefit),
# P-M2 (M2 removes the margin: CI includes zero at every k>1; gap at or below blind),
# P-M3 (single-ref helps at k=1 and harms at k>1; the step is positive with CI excluding zero).
import json
import re
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)
rng = np.random.default_rng(0)

POOL = "runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl"
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
CONDS = ["noref", "ref", "m1", "m2"]
KS = [1, 2, 4, 8, 16]


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


def bci(vals, B=2000):
    v = np.asarray(vals, float)
    b = [float(np.mean(rng.choice(v, len(v)))) for _ in range(B)]
    return [round(float(np.percentile(b, 2.5)), 2), round(float(np.percentile(b, 97.5)), 2)]


tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
pool = {}
for l in open(POOL):
    r = json.loads(l)
    if "oracle" not in r:
        continue
    t = tasks[r["problem_id"]]
    r["k"] = t["k"]
    r["ref_answer"] = t["ref_answer"]
    pool[r["problem_id"]] = r


def scores(jtag, cond, rep):
    # blind/single-reference were written by bon_judge (synthk__ prefix); the two-call
    # mitigation protocols by mitigation_judge (kstrat__ prefix)
    import os as _os
    for pref in ("kstrat", "synthk"):
        f = f"runs/bon_scores_kstrat/{pref}__{jtag}__{cond}_{rep}.jsonl"
        if _os.path.exists(f):
            return {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(f)}
    raise FileNotFoundError(f"no score file for {jtag} {cond} {rep}")


out = {"n_items": len(pool), "per_k_counts": {}}
for k in KS:
    out["per_k_counts"][f"k{k}"] = sum(1 for r in pool.values() if r["k"] == k)

# ---------------- E1: anchoring margins by condition and k
margins = {}
for jtag in JUDGES:
    for cond in CONDS:
        sa = scores(jtag, cond, "a")
        for k in KS:
            if k == 1:
                continue
            vals = []
            for pid, it in pool.items():
                if it["k"] != k or pid not in sa:
                    continue
                refn = norm(it["ref_answer"])
                ms, os_ = [], []
                for i, ok in enumerate(it["oracle"]):
                    if not ok:
                        continue
                    a = norm(boxed(it["samples"][i]) or it["samples"][i])
                    (ms if a == refn else os_).append(sa[pid][i])
                if ms and os_:
                    vals.append(float(np.mean(ms) - np.mean(os_)))
            if len(vals) >= 3:
                margins[f"{jtag}|{cond}|k{k}"] = dict(n=len(vals),
                                                      margin=round(float(np.mean(vals)), 2),
                                                      ci=bci(vals))
out["E1_margins"] = margins

# ---------------- E2: paired gap deltas vs blind, by condition and k
gaps = {}
for jtag in JUDGES:
    per_cond = {}
    for cond in CONDS:
        sa, sb = scores(jtag, cond, "a"), scores(jtag, cond, "b")
        g = {}
        for pid, it in pool.items():
            if pid not in sa:
                continue
            pr = float(np.mean(it["oracle"]))
            if not (0.05 <= pr <= 0.95):
                continue
            c = ns["per_item_curves"](it, sa[pid], sb[pid])
            nl = ns["permutation_null"](it, sa[pid], sb[pid])
            g[pid] = c[64]["judge_gain"] - c[64]["true_gain"] - nl
        per_cond[cond] = g
    for cond in ("ref", "m1", "m2"):
        for k in KS:
            pids = [p for p in per_cond[cond]
                    if p in per_cond["noref"] and pool[p]["k"] == k]
            if len(pids) < 3:
                continue
            d = np.array([per_cond[cond][p] - per_cond["noref"][p] for p in pids])
            gaps[f"{jtag}|{cond}|k{k}"] = dict(n=len(d), delta=round(float(d.mean()), 3),
                                               ci=bci(d))
        pids = [p for p in per_cond[cond] if p in per_cond["noref"] and pool[p]["k"] > 1]
        d = np.array([per_cond[cond][p] - per_cond["noref"][p] for p in pids])
        gaps[f"{jtag}|{cond}|kgt1"] = dict(n=len(d), delta=round(float(d.mean()), 3), ci=bci(d))
out["E2_gap_deltas"] = gaps

json.dump(out, open("../../papers/analysis/mitigation_results.json", "w"), indent=1)
for key in ("E1_margins", "E2_gap_deltas"):
    print(f"=== {key}")
    for k, v in out[key].items():
        val = v.get("margin", v.get("delta"))
        print(f"  {k:52s} {val:+.2f} [{v['ci'][0]:+.2f},{v['ci'][1]:+.2f}] n={v['n']}")
