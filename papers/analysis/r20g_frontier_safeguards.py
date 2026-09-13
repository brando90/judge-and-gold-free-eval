# POST HOC (round-19 review: one safeguard table). Run from experiments/tfa-vs-judge. Writes papers/analysis/r20g_frontier_safeguards.json.
# API judges on the R8-A 16-candidate subsamples (Sonnet 5: runs/r8/sonnet_api, instruction runs/r20/sonnet_inst_api; Opus 5:
# runs/r19/opus_api, instruction runs/r20/opus_inst_api). Per task, grading AUROC (non-matching correct vs wrong; ties count half) and the
# false-rejection rate (non-matching correct scored 3 or below) under: the plain reference, the reference with the full-credit sentence,
# and the max rule max(blind, referenced). Each comparison uses the candidates scored under every condition it involves, so
# "reference minus blind" and "sentence minus blind" reproduce r8_sonnet_analysis.py on the same score files. Task bootstrap, 1,000
# resamples, default_rng(0), as there.
# Also the R20-C leaderboard under the max rule (a score of 7 or above counts as correct; question bootstrap, 2,000, seed 0).
import json
import os

import numpy as np

JUDGES = {"Sonnet 5": ("runs/r8/sonnet_api", "runs/r20/sonnet_inst_api"), "Opus 5": ("runs/r19/opus_api", "runs/r20/opus_inst_api")}


def boot(x, nb=1000, seed=0):
    x = np.asarray(x, float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(nb)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


def auroc(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if len(pos) == 0 or len(neg) == 0:
        return None
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def scores(d, pool, cond, instruction=False):
    f = f"{d}/{pool}.jsonl"
    if not os.path.exists(f):
        return None
    S = {}
    for l in open(f):
        r = json.loads(l)
        if r.get("error") or r.get("score") is None or r["cond"] != cond:
            continue
        if cond == "ref" and bool(r.get("instruction")) != instruction:
            continue
        S[(r["problem_id"], r["idx"])] = r["score"]
    return S


def readouts(t, grp, S, keys):
    nm = [S[(t["problem_id"], i)] for i, g in zip(t["idx"], grp) if g == "nonmatch" and (t["problem_id"], i) in keys]
    wr = [S[(t["problem_id"], i)] for i, g in zip(t["idx"], grp) if g == "wrong" and (t["problem_id"], i) in keys]
    return auroc(nm, wr), (float(np.mean([s <= 3 for s in nm])) if nm else None)


res = {}
for jn, (plain, inst) in JUDGES.items():
    for pool, how in (("mace", "oracle"), ("repl", "lenient"), ("kpool", "lenient")):
        B, R = scores(plain, pool, "noref"), scores(plain, pool, "ref")
        if B is None:
            continue
        C = {"blind": B, "ref": R, "max": {k: max(B[k], R[k]) for k in B if k in R}}
        I = scores(inst, pool, "ref", instruction=True)
        if I:
            C["inst"] = I
        tasks = [json.loads(l) for l in open(f"runs/r8/sonnet_{pool}.jsonl")]
        out = {}
        pairs = [(c, "blind") for c in C if c != "blind"] + [(a, "ref") for a in ("max", "inst") if a in C]
        for a, b in pairs:
            keys = set(C[a]) & set(C[b]) & set(B)
            G, F = [], []
            for t in tasks:
                grp = ["wrong" if not o else ("match" if g == "match" else "nonmatch") for o, g in zip(t[how], t["group"])]
                ga, fa = readouts(t, grp, C[a], keys)
                gb, fb = readouts(t, grp, C[b], keys)
                if ga is not None and gb is not None:
                    G.append(ga - gb)
                if fa is not None and fb is not None:
                    F.append(fa - fb)
            out[f"G_nm_{a}_minus_{b}"], out[f"FR_{a}_minus_{b}"] = boot(G), boot(F)
        res[f"{jn}|{pool}"] = out

# R20-C leaderboard under the max rule
pool = [json.loads(l) for l in open("runs/r20/mace_gen/pool.jsonl")]
S = {}
for l in open("runs/r20/leaderboard_sonnet_api/pool.jsonl"):
    r = json.loads(l)
    if r.get("score") is not None and not r.get("error"):
        S[(r["problem_id"], r["idx"], r["cond"])] = r["score"]
G = pool[0]["generators"]
rows = [t for t in pool if all((t["problem_id"], i, c) in S for i in t["idx"] for c in ("noref", "ref"))]
n = len(rows)
orc = np.array([[t["oracle"][i] for i in range(len(G))] for t in rows], float)
mx = np.array([[max(S[(t["problem_id"], i, "noref")], S[(t["problem_id"], i, "ref")]) >= 7 for i in range(len(G))] for t in rows], float)
rng = np.random.default_rng(0)
bs = [rng.integers(0, n, n) for _ in range(2000)]
ci = lambda x: [round(float(x.mean()), 4), [round(float(np.percentile([x[b].mean() for b in bs], 2.5)), 4), round(float(np.percentile([x[b].mean() for b in bs], 97.5)), 4)]]
res["leaderboard_max_rule"] = {"questions": n, **{g: dict(accuracy_max_rule=ci(mx[:, i]), max_minus_list=ci(mx[:, i] - orc[:, i])) for i, g in enumerate(G)},
                               "pooled_max_minus_list": ci((mx - orc).mean(1))}
json.dump(res, open("../../papers/analysis/r20g_frontier_safeguards.json", "w"), indent=1)
for k, v in res.items():
    print(k, json.dumps(v))
