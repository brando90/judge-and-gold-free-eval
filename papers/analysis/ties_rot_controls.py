# Rotation-arm controls and provenance for Paper D (single canonical script; run from
# experiments/tfa-vs-judge). Produces ties_rot_controls.json with:
#  provenance: per-arm counts of reference-in-pool items (the rotated assignment was
#    constructed pool-aware, preferring a valid answer present among the pool's valid
#    samples, to make the paired within-answer analysis possible; disclosed, not hidden)
#  blind_margin_rotated: the blind judges' margin on the rotated-split items (placebo:
#    blind scores are fixed under rotation, so a nonzero value means modal-answer preference)
#  placebo: across-run paired deltas for valid samples matching NEITHER reference
#  losers: across-run paired deltas for samples matching the original but not rotated ref
#  collapse_rotated: repowered conditional selection collapse on the rotation arm
import glob
import json
import os
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


orig_pool = {r["problem_id"]: r for r in
             (json.loads(l) for l in open("runs/bon/bon_ties__Qwen__Qwen2.5-7B-Instruct.jsonl"))}
rot_pool = {r["problem_id"]: r for r in
            (json.loads(l) for l in open("runs/bon/bon_tiesrot__Qwen__Qwen2.5-7B-Instruct.jsonl"))}

JUDGES = ["Qwen2.5-1.5B-Instruct", "Qwen2.5-3B-Instruct", "Qwen2.5-7B-Instruct",
          "Qwen2.5-14B-Instruct"]


def scores(d, jm, cond, rep):
    return {json.loads(l)["problem_id"]: json.loads(l)["escore"]
            for l in open(f"{d}/ties__Qwen__{jm}__{cond}_{rep}.jsonl")}


def valid_answer_of(item, i):
    s = item["samples"][i]
    return norm(boxed(s) or s)


# ------------------------------------------------------------------ provenance
def ref_in_pool(pool):
    n = 0
    for it in pool.values():
        refn = norm(it["ref_answer"])
        if any(ok and valid_answer_of(it, i) == refn
               for i, ok in enumerate(it["oracle"])):
            n += 1
    return n


out = {"provenance": dict(
    n_items=len(rot_pool),
    orig_ref_in_pool=ref_in_pool(orig_pool),
    rotated_ref_in_pool=ref_in_pool(rot_pool),
    note="rotated assignment constructed pool-aware (prefers a different valid answer "
         "present among the pool's valid samples) to enable the paired analysis")}

# --------------------------------------------------- blind margin, rotated split
res = []
for jm in JUDGES:
    for rep in ("a", "b"):
        sc = scores("runs/bon_scores_ties_full", jm, "noref", rep)
        margins = []
        for pid, it in rot_pool.items():
            if pid not in sc:
                continue
            refn = norm(it["ref_answer"])
            # blind scores come from the ORIGINAL run; align samples by text
            o_it = orig_pool[pid]
            o_idx = {}
            for i, (s, ok) in enumerate(zip(o_it["samples"], o_it["oracle"])):
                if ok:
                    o_idx.setdefault(s, i)
            ms, os_ = [], []
            for i, (s, ok) in enumerate(zip(it["samples"], it["oracle"])):
                if not ok or s not in o_idx:
                    continue
                (ms if valid_answer_of(it, i) == refn else os_).append(sc[pid][o_idx[s]])
            if ms and os_:
                margins.append(float(np.mean(ms) - np.mean(os_)))
        if len(margins) >= 3:
            res.append(dict(judge=jm, rep=rep, n_items=len(margins),
                            margin=round(float(np.mean(margins)), 2), ci=boot_ci(margins)))
out["blind_margin_rotated"] = res

# ------------------------------------------------------- paired placebo / losers
def paired(kind):
    res = []
    for jm in JUDGES:
        for rep in ("a", "b"):
            so = scores("runs/bon_scores_ties_full", jm, "ref", rep)
            sr = scores("runs/bon_scores_ties_rot", jm, "ref", rep)
            deltas = []
            for pid, it in rot_pool.items():
                if pid not in so or pid not in sr:
                    continue
                o_it = orig_pool[pid]
                refo, refr = norm(o_it["ref_answer"]), norm(it["ref_answer"])
                if refo == refr:
                    continue
                o_idx = {}
                for i, (s, ok) in enumerate(zip(o_it["samples"], o_it["oracle"])):
                    if ok:
                        o_idx.setdefault(s, i)
                ds = []
                for i, (s, ok) in enumerate(zip(it["samples"], it["oracle"])):
                    if not ok or s not in o_idx:
                        continue
                    a = valid_answer_of(it, i)
                    hit = (a == refr and a != refo) if kind == "gainers" else \
                          (a == refo and a != refr) if kind == "losers" else \
                          (a != refo and a != refr)
                    if hit:
                        ds.append(sr[pid][i] - so[pid][o_idx[s]])
                if ds:
                    deltas.append(float(np.mean(ds)))
            if len(deltas) >= 3:
                res.append(dict(judge=jm, rep=rep, n_items=len(deltas),
                                delta=round(float(np.mean(deltas)), 2), ci=boot_ci(deltas)))
    return res


out["gainers"] = paired("gainers")
out["placebo_neither"] = paired("neither")
out["losers"] = paired("losers")

# --------------------------------------------- repowered conditional collapse
# Among rotation-arm items whose valid samples include both ref-matching and non-matching
# answers, select with rep-a scores at n=64; report P(selected matches shown ref | selected
# valid). Blind baseline: same items, blind rep-a selection, same match test.
res = []
for jm in JUDGES:
    row = {"judge": jm}
    for cond, d, pool_for_scores in (("ref", "runs/bon_scores_ties_rot", "rot"),
                                     ("noref", "runs/bon_scores_ties_full", "orig")):
        sc = scores(d, jm, cond, "a")
        n_el = n_valid = n_match = 0
        for pid, it in rot_pool.items():
            if pid not in sc:
                continue
            refn = norm(it["ref_answer"])
            if cond == "noref":
                o_it = orig_pool[pid]
                o_idx = {}
                for i, (s, ok) in enumerate(zip(o_it["samples"], o_it["oracle"])):
                    if ok:
                        o_idx.setdefault(s, i)
                idxs = [i for i, s in enumerate(it["samples"]) if s in o_idx]
                if not idxs:
                    continue
                esc = {i: sc[pid][o_idx[it["samples"][i]]] for i in idxs}
            else:
                esc = {i: sc[pid][i] for i in range(len(it["samples"]))}
            answers = {i: valid_answer_of(it, i) for i in esc if it["oracle"][i]}
            kinds = {a == refn for a in answers.values()}
            if kinds != {True, False}:
                continue
            n_el += 1
            sel = max(esc, key=esc.get)
            if it["oracle"][sel]:
                n_valid += 1
                if valid_answer_of(it, sel) == refn:
                    n_match += 1
        row[cond] = dict(eligible=n_el, selected_valid=n_valid, matched_ref=n_match,
                         rate=round(n_match / n_valid, 2) if n_valid else None)
    res.append(row)
out["collapse_rotated"] = res

json.dump(out, open("../../papers/analysis/ties_rot_controls.json", "w"), indent=1)
print(json.dumps(out, indent=1))
