# Rotation-arm analyses for Paper D, single canonical producer (run from
# experiments/tfa-vs-judge). The rotated pool holds the SAME 51 items and IDENTICAL
# 64-sample lists as the original pool; only ref_answer differs (verified: 51/51 identical
# sample lists, 51/51 changed refs), so all pairing is by index.
# Produces ties_rot_controls.json:
#  provenance: pool-aware rotation coverage counts (10/51 original vs 40/51 rotated)
#  ref_margin_rotated: referenced judges' anchoring margin on the rotated assignment
#  blind_margin_rotated: same margin under blind scores (placebo axis 1)
#  gainers / losers / placebo_neither: across-run paired same-sample deltas
#  collapse_rotated: conditional selection collapse, BOTH arms selecting over all 64
#    samples (rep-a scores), with Fisher exact p for ref vs blind match rates
import json
import math
import re

import numpy as np

rng = np.random.default_rng(0)


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


def boot_ci(vals, B=2000):
    b = [float(np.mean(rng.choice(vals, len(vals)))) for _ in range(B)]
    return [round(float(np.percentile(b, 2.5)), 2), round(float(np.percentile(b, 97.5)), 2)]


def fisher_exact_p(a, b, c, d):
    # two-sided Fisher for [[a,b],[c,d]] via hypergeometric enumeration
    def lchoose(n, k):
        return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
    r1, r2, c1 = a + b, c + d, a + c
    n = r1 + r2
    lo, hi = max(0, c1 - r2), min(r1, c1)
    logps = {x: lchoose(r1, x) + lchoose(r2, c1 - x) - lchoose(n, c1)
             for x in range(lo, hi + 1)}
    pobs = logps[a]
    tot = sum(math.exp(v) for v in logps.values())
    return sum(math.exp(v) for v in logps.values() if v <= pobs + 1e-9) / tot


orig_pool = {r["problem_id"]: r for r in
             (json.loads(l) for l in open("runs/bon/bon_ties__Qwen__Qwen2.5-7B-Instruct.jsonl"))}
rot_pool = {r["problem_id"]: r for r in
            (json.loads(l) for l in open("runs/bon/bon_tiesrot__Qwen__Qwen2.5-7B-Instruct.jsonl"))}
for pid in rot_pool:
    assert orig_pool[pid]["samples"] == rot_pool[pid]["samples"]

JUDGES = ["Qwen2.5-1.5B-Instruct", "Qwen2.5-3B-Instruct", "Qwen2.5-7B-Instruct",
          "Qwen2.5-14B-Instruct"]


def scores(d, jm, cond, rep):
    return {json.loads(l)["problem_id"]: json.loads(l)["escore"]
            for l in open(f"{d}/ties__Qwen__{jm}__{cond}_{rep}.jsonl")}


def ans(item, i):
    s = item["samples"][i]
    return norm(boxed(s) or s)


def ref_in_pool(pool):
    return sum(1 for it in pool.values()
               if any(ok and ans(it, i) == norm(it["ref_answer"])
                      for i, ok in enumerate(it["oracle"])))


out = {"provenance": dict(
    n_items=len(rot_pool),
    orig_ref_in_pool=ref_in_pool(orig_pool),
    rotated_ref_in_pool=ref_in_pool(rot_pool),
    note="rotated assignment constructed pool-aware (prefers a different valid answer "
         "present among the pool's valid samples) to enable the paired analysis; "
         "sample lists are identical across the two pools, pairing is by index")}


def margin_rows(score_dir, cond):
    # margin among oracle-valid samples: mean(score | matches rotated ref) - mean(other valid)
    rows = []
    for jm in JUDGES:
        for rep in ("a", "b"):
            sc = scores(score_dir, jm, cond, rep)
            margins = []
            for pid, it in rot_pool.items():
                if pid not in sc:
                    continue
                refn = norm(it["ref_answer"])
                ms, os_ = [], []
                for i, ok in enumerate(it["oracle"]):
                    if not ok:
                        continue
                    (ms if ans(it, i) == refn else os_).append(sc[pid][i])
                if ms and os_:
                    margins.append(float(np.mean(ms) - np.mean(os_)))
            if len(margins) >= 3:
                rows.append(dict(judge=jm, rep=rep, n_items=len(margins),
                                 margin=round(float(np.mean(margins)), 2),
                                 ci=boot_ci(margins)))
    return rows


out["ref_margin_rotated"] = margin_rows("runs/bon_scores_ties_rot", "ref")
out["blind_margin_rotated"] = margin_rows("runs/bon_scores_ties_full", "noref")


def paired(kind):
    rows = []
    for jm in JUDGES:
        for rep in ("a", "b"):
            so = scores("runs/bon_scores_ties_full", jm, "ref", rep)
            sr = scores("runs/bon_scores_ties_rot", jm, "ref", rep)
            deltas = []
            for pid, it in rot_pool.items():
                if pid not in so or pid not in sr:
                    continue
                refo, refr = norm(orig_pool[pid]["ref_answer"]), norm(it["ref_answer"])
                if refo == refr:
                    continue
                ds = []
                for i, ok in enumerate(it["oracle"]):
                    if not ok:
                        continue
                    a = ans(it, i)
                    hit = (a == refr and a != refo) if kind == "gainers" else \
                          (a == refo and a != refr) if kind == "losers" else \
                          (a != refo and a != refr)
                    if hit:
                        ds.append(sr[pid][i] - so[pid][i])
                if ds:
                    deltas.append(float(np.mean(ds)))
            if len(deltas) >= 3:
                rows.append(dict(judge=jm, rep=rep, n_items=len(deltas),
                                 delta=round(float(np.mean(deltas)), 2), ci=boot_ci(deltas)))
    return rows


out["gainers"] = paired("gainers")
out["placebo_neither"] = paired("neither")
out["losers"] = paired("losers")

# ---------------- conditional collapse, both arms over ALL 64 samples (rep-a selection)
res = []
for jm in JUDGES:
    row = {"judge": jm}
    cells = {}
    for cond, d in (("ref", "runs/bon_scores_ties_rot"), ("noref", "runs/bon_scores_ties_full")):
        sc = scores(d, jm, cond, "a")
        n_el = n_valid = n_match = 0
        for pid, it in rot_pool.items():
            if pid not in sc:
                continue
            refn = norm(it["ref_answer"])
            kinds = {ans(it, i) == refn for i, ok in enumerate(it["oracle"]) if ok}
            if kinds != {True, False}:
                continue
            n_el += 1
            sel = int(np.argmax(sc[pid]))
            if it["oracle"][sel]:
                n_valid += 1
                if ans(it, sel) == refn:
                    n_match += 1
        cells[cond] = dict(eligible=n_el, selected_valid=n_valid, matched_ref=n_match,
                           rate=round(n_match / n_valid, 2) if n_valid else None)
        row[cond] = cells[cond]
    a, b = cells["ref"]["matched_ref"], cells["ref"]["selected_valid"] - cells["ref"]["matched_ref"]
    c, dd = cells["noref"]["matched_ref"], cells["noref"]["selected_valid"] - cells["noref"]["matched_ref"]
    row["fisher_p"] = round(fisher_exact_p(a, b, c, dd), 5)
    res.append(row)
out["collapse_rotated"] = res

json.dump(out, open("../../papers/analysis/ties_rot_controls.json", "w"), indent=1)
print(json.dumps(out, indent=1))
