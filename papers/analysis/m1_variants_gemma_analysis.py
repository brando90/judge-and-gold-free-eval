# Gemma-2-9b extension of the M1 second-pass mechanism variants (P-GV1..P-GV3), registered
# 2026-09-12 in registration.md ("M1-variant decomposition on gemma-2-9b"). This is a SEPARATE
# script, not an edit of the frozen m1_variants_analysis.py, deliberately: that file already
# scored the original, published Qwen-7B/phi-4 result and must not be re-run or perturbed.
# Estimator logic below is copied verbatim from m1_variants_analysis.py (same estimators, same
# pool, same margin/inflation definitions); only the judge, the m1indep source, and the
# reproducibility fix (per-judge seeding of Python's global random module, see the audit note
# in registration.md 2026-09-12) differ.
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)
rng = np.random.default_rng(int.from_bytes(b"google__gemma-2-9b-it", "little") % (2**32))
ns["rng"] = rng
import random
random.seed(int.from_bytes(b"google__gemma-2-9b-it", "little") % (2**32))
NBOOT = 1000
JUDGE = "google__gemma-2-9b-it"
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

need = [(JUDGE, c, r) for c in CONDS for r in ("a", "b")]
if any(load(*x) is None for x in need):
    missing = [x for x in need if load(*x) is None]
    print(f"[m1_variants_gemma_analysis] pre-data: {len(missing)} score files absent "
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
j = JUDGE
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
    mm, mc, mn = bci(list(m.values())) if m else (None, None, 0)
    res[f"{j}|{c}"] = dict(infl=dm, infl_ci=dc, n=dn, margin=mm, margin_ci=mc, margin_n=mn)
    mstr = f"{mm:+.2f} [{mc[0]:+.2f},{mc[1]:+.2f}]" if mm is not None else "n/a"
    md.append(f"| {j} | {c} | {dm:+.3f} [{dc[0]:+.3f},{dc[1]:+.3f}] ({dn}) | {mstr} |")


def contrast(c1, c2):
    shared = sorted(set(deltas[c1]) & set(deltas[c2]))
    return bci([deltas[c1][p] - deltas[c2][p] for p in shared])


v1 = contrast("m1noscore", "m1")
v2 = contrast("m1prev", "m1")
v3 = contrast("m1indep", "m1prev")
res[f"{j}|P_GV1"] = dict(mean=v1[0], ci=v1[1], n=v1[2])
res[f"{j}|P_GV2"] = dict(mean=v2[0], ci=v2[1], n=v2[2])
res[f"{j}|P_GV3"] = dict(mean=v3[0], ci=v3[1], n=v3[2])
res[f"{j}|verdicts"] = dict(
    P_GV1=bool(v1[1][0] > 0),
    P_GV2=bool(v2[1][0] <= 0 <= v2[1][1]),
    P_GV3=bool(v3[1][0] <= 0 <= v3[1][1]))
md.append(f"| {j} | contrasts | V1 noscore-m1 {v1[0]:+.3f} [{v1[1][0]:+.3f},{v1[1][1]:+.3f}] "
          f"V2 prev-m1 {v2[0]:+.3f} [{v2[1][0]:+.3f},{v2[1][1]:+.3f}] "
          f"V3 indep-prev {v3[0]:+.3f} [{v3[1][0]:+.3f},{v3[1][1]:+.3f}] | |")

json.dump(res, open("../../papers/analysis/m1_variants_gemma_results.json", "w"), indent=1)
print("\n".join(md))
print(j, res[f"{j}|verdicts"])
