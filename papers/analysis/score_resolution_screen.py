# POST HOC (unregistered): does a judge's SCORE RESOLUTION determine whether it can select at
# all under best-of-n? Motivated by the Mistral-7B correction: that judge anchors but shows no
# measurable inflation because its scores are exact integers and ties dominate selection.
#
# Metrics per judge, blind condition, k>1 items of the k-stratified pool:
#   distinct  = number of distinct rounded score values pool-wide
#   entropy   = Shannon entropy (bits) of the pooled score distribution
#   ties@max  = mean number of samples sharing the maximum rubric-a score within an item
#   sel-acc   = mean validity of the samples tied at the maximum (what selection can achieve)
#   lift      = sel-acc minus the pool's base validity rate (what random picking achieves)
#
# HONEST CAVEAT, stated up front: n = 5 judges, and four of them cluster tightly (2491-2751
# distinct values, lift +0.36 to +0.46) with Mistral the lone outlier (11 values, +0.18). The
# reported correlations are therefore driven by a single leverage point and are ILLUSTRATIVE,
# not inferential. What the data does establish is the MECHANISM, which needs no correlation:
# a judge whose scores take 11 values ties 18 of 64 samples at the maximum, the estimator
# breaks ties at random, and its achievable selection accuracy collapses toward the base rate.
# Run from experiments/tfa-vs-judge.
import json
import re

import numpy as np

JUDGES = ["mistralai__Mistral-7B-Instruct-v0.3", "google__gemma-2-9b-it",
          "Qwen__Qwen2.5-7B-Instruct", "Qwen__Qwen2.5-14B-Instruct", "microsoft__phi-4"]


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


def load(jt, cond, rep):
    for pref in ("kstrat", "synthk"):
        try:
            return {json.loads(l)["problem_id"]: json.loads(l)["escore"]
                    for l in open(f"runs/bon_scores_kstrat/{pref}__{jt}__{cond}_{rep}.jsonl")}
        except FileNotFoundError:
            continue
    return None


pool = {json.loads(l)["problem_id"]: json.loads(l)
        for l in open("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")}
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
items = [p for p in pool if tasks[p]["k"] > 1]
base = float(np.mean([np.mean(pool[p]["oracle"]) for p in items]))

out = {"base_validity_rate": round(base, 3), "judges": {}, "caveat":
       "n=5 judges, one leverage point; correlations illustrative, mechanism is the claim"}
rows = []
for jt in JUDGES:
    sa = load(jt, "noref", "a")
    sa_ref = load(jt, "ref", "a")
    if sa is None:
        continue
    allv = np.concatenate([np.array(sa[p]) for p in items if p in sa])
    vals, counts = np.unique(np.round(allv, 3), return_counts=True)
    p = counts / counts.sum()
    ent = float(-(p * np.log2(p)).sum())
    ties, acc, margins = [], [], []
    for pid in items:
        if pid not in sa:
            continue
        e = np.array(sa[pid])
        idx = np.where(e == e.max())[0]
        ties.append(len(idx))
        o = np.array(pool[pid]["oracle"])
        acc.append(float(o[idx].mean()))
        if sa_ref and pid in sa_ref:
            er = np.array(sa_ref[pid])
            refn = norm(pool[pid]["ref_answer"])
            ms, os_ = [], []
            for i, ok in enumerate(o):
                if not ok:
                    continue
                a_ = norm(boxed(pool[pid]["samples"][i]) or pool[pid]["samples"][i])
                (ms if a_ == refn else os_).append(er[i])
            if ms and os_:
                margins.append(float(np.mean(ms) - np.mean(os_)))
    a = float(np.mean(acc))
    d = dict(distinct_values=int(len(vals)), entropy_bits=round(ent, 2),
             mean_ties_at_max=round(float(np.mean(ties)), 1),
             selection_accuracy=round(a, 3), lift_over_random=round(a - base, 3),
             anchoring_margin=round(float(np.mean(margins)), 2) if margins else None)
    out["judges"][jt] = d
    rows.append([d["distinct_values"], d["mean_ties_at_max"], d["lift_over_random"]])
    print(f"{jt:38s} distinct={d['distinct_values']:5d} entropy={d['entropy_bits']:5.2f} "
          f"ties@max={d['mean_ties_at_max']:5.1f} sel-acc={d['selection_accuracy']:.3f} "
          f"lift={d['lift_over_random']:+.3f} margin={d['anchoring_margin']}")

r = np.array(rows, float)
out["corr_distinct_vs_lift"] = round(float(np.corrcoef(r[:, 0], r[:, 2])[0, 1]), 3)
out["corr_ties_vs_lift"] = round(float(np.corrcoef(r[:, 1], r[:, 2])[0, 1]), 3)
print(f"\nrandom-pick baseline: {base:.3f}")
print(f"corr(distinct, lift) = {out['corr_distinct_vs_lift']:+.3f}  "
      f"corr(ties, lift) = {out['corr_ties_vs_lift']:+.3f}  "
      f"(n=5, single leverage point -- illustrative only)")
json.dump(out, open("../../papers/analysis/score_resolution_screen.json", "w"), indent=1)
