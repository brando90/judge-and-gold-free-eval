# FROZEN analysis for the M1 second-pass mechanism variants (P-M1V1..P-M1V3).
# INTERNAL REGISTRATION: committed together with the mitigation_judge.py cond extensions
# BEFORE any variant judging runs; the commit timestamp is the registration.
#
# Question (external review, 2026-09-07): does blind-then-reveal work because of the
# ORDERING, or because the judge commits to a previously emitted score? Three variants
# decompose M1's second call, everything else identical:
#   m1noscore : reference + keep-correct instruction, NO score shown  (ordering alone)
#   m1prev    : own blind score shown with neutral phrasing "A previous blind assessment
#               scored this candidate X" (commitment to a number, no "your")
#   m1indep   : the OTHER judge's blind score shown with the identical neutral phrasing
#               (commitment to someone else's number)
# Estimators (mirroring the frozen machinery exactly): per-item paired cond-minus-blind
# excess-gap delta at n=64 on kstrat k>1 items (bon_analysis per_item_curves +
# permutation_null; rubric a selects, b reports); anchoring margin per worked_ref E1
# (rubric a, matching vs non-matching valid samples). Item-level bootstrap NBOOT=1000,
# default_rng(0). Judges: Qwen2.5-7B and phi-4; m1indep shows phi-4's blind scores to
# Qwen and vice versa.
#
# REGISTERED PREDICTIONS (committed before any variant scores exist; scored per judge):
#   P-M1V1 (score input is necessary): m1noscore's inflation delta vs blind EXCEEDS m1's
#     (paired per-item difference, CI excluding zero) for both judges — the ordering plus
#     instruction without the score does not reproduce M1's protection (the refinst result
#     predicts instructions alone are placebo below frontier capability).
#   P-M1V2 (the "your" framing is inert): m1prev's inflation delta vs blind differs from
#     m1's by an amount whose CI includes zero, both judges. (A null prediction, disclosed
#     as weak-form: it cannot prove equivalence, only fail to find a difference.)
#   P-M1V3 (commitment is to a number, not to self): m1indep's inflation delta vs blind
#     differs from m1prev's by an amount whose CI includes zero, both judges. If this
#     FAILS with m1indep more inflated, the protection is self-consistency rather than
#     commit-before-context, and the paper should say so.
#   Margins are exploratory throughout.
#
# Run from experiments/tfa-vs-judge after pipeline24 completes.
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
CONDS = ["m1", "m1noscore", "m1prev", "m1indep"]
POOL_F = "runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl"


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


def load(judge, cond, rep):
    pre = "synthk" if cond in ("noref", "ref") else "kstrat"
    f = f"runs/bon_scores_kstrat/{pre}__{judge}__{cond}_{rep}.jsonl"
    if not os.path.exists(f):
        return None
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))}


tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
pool = [json.loads(l) for l in open(POOL_F)
        if tasks[json.loads(l)["problem_id"]].get("k", 0) > 1]

need = [(j, c, r) for j in JUDGES for c in CONDS for r in ("a", "b")]
if any(load(*x) is None for x in need):
    missing = [x for x in need if load(*x) is None]
    print(f"[m1_variants_analysis] pre-data: {len(missing)} score files absent "
          f"(first: {missing[0]}). Nothing written.")
    raise SystemExit


def bci(vals):
    v = np.asarray(vals, float)
    boots = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(NBOOT)]
    return float(v.mean()), [float(np.percentile(boots, 2.5)),
                             float(np.percentile(boots, 97.5))], len(v)


res = {}
md = ["| judge | cond | inflation delta vs blind [CI] (n) | margin(a) [CI] |",
      "|---|---|---|---|"]
for j in JUDGES:
    na, nb = load(j, "noref", "a"), load(j, "noref", "b")
    deltas = {}
    for c in CONDS:
        ca, cb = load(j, c, "a"), load(j, c, "b")
        d = {}
        for it in pool:
            pid = it["problem_id"]
            if pid not in ca or pid not in na or not (0 < sum(it["oracle"]) < len(it["oracle"])):
                continue
            gr = ns["per_item_curves"](it, ca[pid], cb[pid])
            nr = ns["permutation_null"](it, ca[pid], cb[pid])
            gn = ns["per_item_curves"](it, na[pid], nb[pid])
            nn = ns["permutation_null"](it, na[pid], nb[pid])
            d[pid] = ((gr[64]["judge_gain"] - gr[64]["true_gain"] - nr)
                      - (gn[64]["judge_gain"] - gn[64]["true_gain"] - nn))
        deltas[c] = d
        # margin, rubric a
        m = {}
        for it in pool:
            pid = it["problem_id"]
            if pid not in ca:
                continue
            refn = norm(it["ref_answer"])
            ms, ot = [], []
            for i, ok in enumerate(it["oracle"]):
                if not ok:
                    continue
                a_ = norm(boxed(it["samples"][i]) or it["samples"][i])
                (ms if a_ == refn else ot).append(ca[pid][i])
            if ms and ot:
                m[pid] = float(np.mean(ms) - np.mean(ot))
        dm, dc, dn = bci(list(d.values()))
        mm, mc, mn = bci(list(m.values()))
        res[f"{j}|{c}"] = dict(infl=dm, infl_ci=dc, n=dn, margin=mm, margin_ci=mc)
        md.append(f"| {j} | {c} | {dm:+.3f} [{dc[0]:+.3f},{dc[1]:+.3f}] ({dn}) | "
                  f"{mm:+.2f} [{mc[0]:+.2f},{mc[1]:+.2f}] |")
    # registered contrasts (paired per item)
    def contrast(c1, c2):
        shared = sorted(set(deltas[c1]) & set(deltas[c2]))
        return bci([deltas[c1][p] - deltas[c2][p] for p in shared])
    v1 = contrast("m1noscore", "m1")
    v2 = contrast("m1prev", "m1")
    v3 = contrast("m1indep", "m1prev")
    res[f"{j}|P_M1V1"] = dict(mean=v1[0], ci=v1[1], n=v1[2])
    res[f"{j}|P_M1V2"] = dict(mean=v2[0], ci=v2[1], n=v2[2])
    res[f"{j}|P_M1V3"] = dict(mean=v3[0], ci=v3[1], n=v3[2])
    res[f"{j}|verdicts"] = dict(
        P_M1V1=bool(v1[1][0] > 0),
        P_M1V2=bool(v2[1][0] <= 0 <= v2[1][1]),
        P_M1V3=bool(v3[1][0] <= 0 <= v3[1][1]))
    md.append(f"| {j} | contrasts | V1 noscore-m1 {v1[0]:+.3f} [{v1[1][0]:+.3f},{v1[1][1]:+.3f}] "
              f"V2 prev-m1 {v2[0]:+.3f} [{v2[1][0]:+.3f},{v2[1][1]:+.3f}] "
              f"V3 indep-prev {v3[0]:+.3f} [{v3[1][0]:+.3f},{v3[1][1]:+.3f}] | |")

json.dump(res, open("../../papers/analysis/m1_variants_results.json"
                    if os.path.exists("../../papers/analysis") else "m1_variants_results.json",
                    "w"), indent=1)
print("\n".join(md))
for j in JUDGES:
    print(j, res[f"{j}|verdicts"])
