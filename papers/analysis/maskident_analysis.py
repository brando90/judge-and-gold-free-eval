# FROZEN analysis for the masking-and-identity mechanistic suite (P-MS1..P-MS3).
# INTERNAL REGISTRATION: committed together with scripts/build_refvariant_pools.py BEFORE
# any variant judging runs; the commit timestamp is the registration.
#
# Question. Paper D's proposed mechanism is a cheap equality check against a separable
# answer token. What kind of equality? Three variants separate the readings, per external
# review: the reference written as English words (semantic identity, lexical mismatch), as
# an arithmetic expression n-1+1 (semantic identity, equality needs one computation), and
# a worked reference with its final answer masked (derivation present, token absent).
#
# Estimator (identical to worked_ref_analysis.py E1): per-item anchoring margin = mean
# rubric-a escore of reference-matching valid samples minus mean escore of non-matching
# valid samples, where "matching" is ALWAYS defined against the item's ORIGINAL numeral
# reference (loose-normalized boxed answer, fallback whole reply); paired per-item
# condition differences on shared items; item-level bootstrap (NBOOT=1000, default_rng(0)).
# Rubric b replicates. Replication pool: all items with both classes present. K-stratified
# masked arm: k>1 items, scalar families (crt, divcount, digitsum) for the registered
# prediction; list families exploratory (masking leaks elements there, disclosed).
#
# REGISTERED PREDICTIONS (committed before the variant judging exists):
#   P-MS1 (semantic, not lexical): the refword margin is positive with CI excluding zero
#     for BOTH judges (rubric a). The judge's equality check survives a total lexical
#     mismatch between reference and candidate; anchoring is on the semantic answer.
#   P-MS2 (cheapness gradient): the refexpr margin is smaller than the bare-ref margin
#     (paired per-item difference, CI excluding zero) for both judges, while remaining
#     positive; equality that must be computed anchors less than equality that can be read.
#   P-MS3 (token necessity): on scalar families at k>1, the masked-worked-ref margin drops
#     relative to the unmasked worked-ref margin (paired difference CI excluding zero) for
#     both judges, and the drop removes more than half of the unmasked margin.
#   Failures are reported as failures; each prediction scored per judge.
#
# Run from experiments/tfa-vs-judge after pipeline22 completes.
import json
import os
import re

import numpy as np

NBOOT = 1000
rng = np.random.default_rng(0)
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
SCALAR_FAMS = {"crt", "divcount", "digitsum"}


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


def load(path):
    if not os.path.exists(path):
        return None
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(path))}


def bci(vals):
    v = np.asarray(vals, float)
    boots = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(NBOOT)]
    return float(v.mean()), [float(np.percentile(boots, 2.5)),
                             float(np.percentile(boots, 97.5))], len(v)


def margins_for(pool_rows, sc, ref_key="ref_answer"):
    m = {}
    for it in pool_rows:
        pid = it["problem_id"]
        if sc is None or pid not in sc:
            continue
        refn = norm(it[ref_key])
        ms, others = [], []
        for i, ok in enumerate(it["oracle"]):
            if not ok:
                continue
            a = norm(boxed(it["samples"][i]) or it["samples"][i])
            (ms if a == refn else others).append(sc[pid][i])
        if ms and others:
            m[pid] = float(np.mean(ms) - np.mean(others))
    return m


repl = [json.loads(l) for l in open("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl")]
kpool = [json.loads(l) for l in open("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")]
ktasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
wrefs = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_worked_refs.jsonl")}
kmv = [r for r in kpool if ktasks[r["problem_id"]].get("k", 0) > 1]
kmv_scalar = [r for r in kmv if wrefs[r["problem_id"]]["family"] in SCALAR_FAMS]

res = {}
md = ["| judge | rubric | condition | margin [CI] (n) | vs baseline [CI] |",
      "|---|---|---|---|---|"]
for j in JUDGES:
    for rep in ("a", "b"):
        base = margins_for(repl, load(f"runs/bon_scores_repl/synthk__{j}__ref_{rep}.jsonl"))
        blind = margins_for(repl, load(f"runs/bon_scores_repl/synthk__{j}__noref_{rep}.jsonl"))
        conds = dict(
            refword=margins_for(repl, load(f"runs/bon_scores_refword/synthk__{j}__ref_{rep}.jsonl")),
            refexpr=margins_for(repl, load(f"runs/bon_scores_refexpr/synthk__{j}__ref_{rep}.jsonl")))
        for cname, m in [("ref (baseline)", base), ("noref", blind)] + list(conds.items()):
            if not m:
                continue
            mm, mc, mn = bci(list(m.values()))
            row = dict(margin=mm, ci=mc, n=mn)
            if cname in ("refword", "refexpr"):
                shared = sorted(set(m) & set(base))
                dm, dc, dn = bci([m[p] - base[p] for p in shared])
                row["minus_ref"] = dict(mean=dm, ci=dc, n=dn)
                md.append(f"| {j} | {rep} | {cname} | {mm:+.2f} [{mc[0]:+.2f},{mc[1]:+.2f}] ({mn}) | "
                          f"{dm:+.2f} [{dc[0]:+.2f},{dc[1]:+.2f}] |")
            else:
                md.append(f"| {j} | {rep} | {cname} | {mm:+.2f} [{mc[0]:+.2f},{mc[1]:+.2f}] ({mn}) | |")
            res[f"{j}|{rep}|{cname}"] = row
        # masked worked ref on kstrat scalar families
        sol = margins_for(kmv_scalar, load(f"runs/bon_scores_kstrat/synthk__{j}__refsol_{rep}.jsonl"))
        msk = margins_for(kmv_scalar, load(f"runs/bon_scores_refsolmask/synthk__{j}__refsol_{rep}.jsonl"))
        if sol and msk:
            shared = sorted(set(sol) & set(msk))
            sm, sc_, sn = bci([sol[p] for p in shared])
            km, kc, kn = bci([msk[p] for p in shared])
            dm, dc, dn = bci([msk[p] - sol[p] for p in shared])
            res[f"{j}|{rep}|refsolmask"] = dict(
                refsol=dict(mean=sm, ci=sc_), masked=dict(mean=km, ci=kc),
                masked_minus_refsol=dict(mean=dm, ci=dc, n=dn),
                drop_frac=(1 - km / sm) if sm else None)
            md.append(f"| {j} | {rep} | refsol scalar k>1 | {sm:+.2f} [{sc_[0]:+.2f},{sc_[1]:+.2f}] ({sn}) | |")
            md.append(f"| {j} | {rep} | refsolMASKED | {km:+.2f} [{kc[0]:+.2f},{kc[1]:+.2f}] ({kn}) | "
                      f"{dm:+.2f} [{dc[0]:+.2f},{dc[1]:+.2f}] |")

# verdicts on rubric a
verd = {}
for j in JUDGES:
    w = res.get(f"{j}|a|refword")
    e = res.get(f"{j}|a|refexpr")
    k = res.get(f"{j}|a|refsolmask")
    verd[j] = dict(
        P_MS1=bool(w and w["ci"][0] > 0),
        P_MS2=bool(e and e["minus_ref"]["ci"][1] < 0 and e["margin"] > 0),
        P_MS3=bool(k and k["masked_minus_refsol"]["ci"][1] < 0
                   and k["drop_frac"] is not None and k["drop_frac"] > 0.5))
res["verdicts_rubric_a"] = verd
json.dump(res, open("../../papers/analysis/maskident_results.json"
                    if os.path.exists("../../papers/analysis") else "maskident_results.json",
                    "w"), indent=1)
print("\n".join(md))
print("verdicts:", json.dumps(verd, indent=1))
