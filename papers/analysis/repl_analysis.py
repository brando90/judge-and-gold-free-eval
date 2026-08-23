# Registered analysis for Paper D's clean replication (OSF osf.io/ym5x9, registered
# 2026-08-23 before any generation). COMMITTED BEFORE THE MAIN POOL EXISTED.
# Run from experiments/tfa-vs-judge once runs/bon_scores_repl/ has files.
#
# Frozen estimators, exactly as externally registered:
#  E1 (primary): per-item paired referenced-minus-blind excess-gap delta, pooled over the
#     two judges by item-level cluster bootstrap (each resampled item contributes both
#     judges' deltas). Prediction P-R1: positive with 95% CI excluding zero.
#  P-R2: selection collapse. For each judge, on items whose valid samples include both
#     reference-matching and non-matching answers, compare the rep-a argmax selection's
#     reference-match indicator under referenced vs blind scoring with exact McNemar.
#     Prediction: referenced match rate exceeds blind with p < 0.05 per judge.
#  P-R3: anchoring margins (mean score of reference-matching valid samples minus other
#     valid samples, item-mean, bootstrap CI) positive for both judges.
# The excess-gap machinery is the committed bon_analysis estimator (escore rep a selects,
# rep b reports, within-checker-stratum permutation null). Validity labels come from the
# programmatic verifier (repl_oracle.py), exact by construction.
import json
import math
import re
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)
rng = np.random.default_rng(0)

POOL = "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl"
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]


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


def fisher_free_mcnemar(b10, b01):
    nd = b10 + b01
    if nd == 0:
        return 1.0
    p = sum(math.comb(nd, k) for k in range(min(b01, b10) + 1)) * 2 / (2 ** nd)
    return min(p, 1.0)


pool = {r["problem_id"]: r for r in (json.loads(l) for l in open(POOL)) if "oracle" in r}


def scores(jtag, cond, rep):
    return {json.loads(l)["problem_id"]: json.loads(l)["escore"]
            for l in open(f"runs/bon_scores_repl/synthk__{jtag}__{cond}_{rep}.jsonl")}


out = {"n_items_total": len(pool)}
deltas_by_judge = {}
for jtag in JUDGES:
    ra, rb = scores(jtag, "ref", "a"), scores(jtag, "ref", "b")
    na, nb = scores(jtag, "noref", "a"), scores(jtag, "noref", "b")
    d = {}
    for pid, it in pool.items():
        if pid not in ra or pid not in na:
            continue
        pr = float(np.mean(it["oracle"]))
        if not (0.2 <= pr <= 0.8):
            continue  # registered in-band population, by design of the pool
        gr = ns["per_item_curves"](it, ra[pid], rb[pid])
        nr = ns["permutation_null"](it, ra[pid], rb[pid])
        gn = ns["per_item_curves"](it, na[pid], nb[pid])
        nn = ns["permutation_null"](it, na[pid], nb[pid])
        d[pid] = ((gr[64]["judge_gain"] - gr[64]["true_gain"] - nr)
                  - (gn[64]["judge_gain"] - gn[64]["true_gain"] - nn))
    deltas_by_judge[jtag] = d
    v = np.array(list(d.values()))
    boot = [float(np.mean(rng.choice(v, len(v)))) for _ in range(4000)]
    out[f"delta__{jtag}"] = dict(n=len(v), delta=round(float(v.mean()), 3),
                                 ci=[round(float(np.percentile(boot, 2.5)), 3),
                                     round(float(np.percentile(boot, 97.5)), 3)])
pids = sorted(set(deltas_by_judge[JUDGES[0]]) & set(deltas_by_judge[JUDGES[1]]))
D = np.array([[deltas_by_judge[j][p] for p in pids] for j in JUDGES])
idx = np.arange(len(pids))
boots = [float(D[:, rng.choice(idx, len(idx))].mean()) for _ in range(4000)]
out["E1_pooled"] = dict(n_items=len(pids), delta=round(float(D.mean()), 3),
                        ci=[round(float(np.percentile(boots, 2.5)), 3),
                            round(float(np.percentile(boots, 97.5)), 3)],
                        prediction="P-R1: positive, CI excluding zero")

for jtag in JUDGES:
    sa_ref = scores(jtag, "ref", "a")
    sa_bld = scores(jtag, "noref", "a")
    b10 = b01 = n_el = 0
    margins = []
    for pid, it in pool.items():
        if pid not in sa_ref or pid not in sa_bld:
            continue
        refn = norm(it["ref_answer"])
        kinds = {norm(boxed(it["samples"][i]) or it["samples"][i]) == refn
                 for i, ok in enumerate(it["oracle"]) if ok}
        if kinds == {True, False}:
            n_el += 1

            def match(sc):
                sel = int(np.argmax(sc[pid]))
                return bool(it["oracle"][sel]) and \
                    norm(boxed(it["samples"][sel]) or it["samples"][sel]) == refn
            mr, mb = match(sa_ref), match(sa_bld)
            if mr and not mb:
                b10 += 1
            elif mb and not mr:
                b01 += 1
        ms, os_ = [], []
        for i, ok in enumerate(it["oracle"]):
            if not ok:
                continue
            a = norm(boxed(it["samples"][i]) or it["samples"][i])
            (ms if a == refn else os_).append(sa_ref[pid][i])
        if ms and os_:
            margins.append(float(np.mean(ms) - np.mean(os_)))
    mb_ci = None
    if len(margins) >= 3:
        boot = [float(np.mean(rng.choice(margins, len(margins)))) for _ in range(2000)]
        mb_ci = [round(float(np.percentile(boot, 2.5)), 2),
                 round(float(np.percentile(boot, 97.5)), 2)]
    out[f"collapse__{jtag}"] = dict(eligible=n_el, ref_only=b10, blind_only=b01,
                                   mcnemar_p=round(fisher_free_mcnemar(b10, b01), 5),
                                   prediction="P-R2: p < 0.05")
    out[f"margin__{jtag}"] = dict(n=len(margins),
                                  margin=round(float(np.mean(margins)), 2) if margins else None,
                                  ci=mb_ci, prediction="P-R3: positive")

json.dump(out, open("../../papers/analysis/repl_results.json", "w"), indent=1)
print(json.dumps(out, indent=1))
