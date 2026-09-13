# POST HOC analyses for the round-5 revision (external review of the round-4 draft). No registration weight.
# Run from experiments/tfa-vs-judge. Writes papers/analysis/r5_posthoc_results.json.
#  (a) MACE grading AUROC by k (k=1 vs k>1), Qwen2.5-7B exact scorer and phi-4 original scorer
#  (b) split-half moderator test: per-task blind AUROC on one half of the samples against the reference's change in
#      overall AUROC on the other half, within each pool and pooled, 20 random stratified splits
#  (c) k-pool selection: change at k>1 minus change at k=1, per judge (independent task sets)
#  (d) power: labeled tasks (and candidates per task) needed to tell the replication pool's blind AUROC from MACE's
#  (e) blind-accepted rotation filter at >=7 and >=9, gainers and losers, Qwen2.5-7B exact scorer
import ast
import json
import os
import re

import numpy as np
from scipy import stats

NBOOT = 1000
OUT = "../../papers/analysis/r5_posthoc_results.json"
S4 = "runs/r4/scores"


def boot(x, seed=0):
    x = np.asarray([v for v in x if v is not None], float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


def rows(f):
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))} if os.path.exists(f) else None


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def mnorm(a):
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


def auroc(sc, lab):
    pos = np.array([s for s, l in zip(sc, lab) if l and s is not None], float)
    neg = np.array([s for s, l in zip(sc, lab) if not l and s is not None], float)
    if len(pos) == 0 or len(neg) == 0:
        return None
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def sel_acc(scores, oracle):
    s = np.array([-np.inf if v is None else v for v in scores], float)
    return float(np.asarray(oracle, float)[np.isclose(s, s.max(), rtol=0, atol=1e-9)].mean())


def jl(f):
    return [json.loads(l) for l in open(f)]


mtasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/mace_tasks.jsonl")}
mace = []
for t in jl("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    if "oracle" not in t:
        continue
    tt = mtasks[t["problem_id"]]
    params = tt["params"] if isinstance(tt["params"], dict) else ast.literal_eval(tt["params"])
    if params["domain"] in ("River", "Language") and 0.05 <= np.mean(t["oracle"]) <= 0.95:
        t["k"], t["ref_answer"] = int(tt["k"]), tt["ref_answer"]
        mace.append(t)
repl = jl("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl")
kp = jl("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")

FILES = {
    "Qwen2.5-7B": dict(repl=(f"{S4}/repl__Qwen__Qwen2.5-7B-Instruct__noref_a.jsonl", f"{S4}/repl__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl"),
                       kpool=(f"{S4}/kstrat__Qwen__Qwen2.5-7B-Instruct__noref_a.jsonl", f"{S4}/kstrat__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl"),
                       mace=(f"{S4}/mace__Qwen__Qwen2.5-7B-Instruct__noref_a.jsonl", f"{S4}/mace__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl")),
    "phi-4": dict(repl=("runs/bon_scores_repl/synthk__microsoft__phi-4__noref_a.jsonl", "runs/bon_scores_repl/synthk__microsoft__phi-4__ref_a.jsonl"),
                  kpool=("runs/bon_scores_kstrat/synthk__microsoft__phi-4__noref_a.jsonl", "runs/bon_scores_kstrat/synthk__microsoft__phi-4__ref_a.jsonl"),
                  mace=("runs/bon_scores_mace/mace__microsoft__phi-4__noref_a.jsonl", "runs/bon_scores_mace/mace__microsoft__phi-4__ref_a.jsonl")),
}
POOLS = {"repl": repl, "kpool": kp, "mace": mace}
res = {"scorer": {"Qwen2.5-7B": "exact (R4)", "phi-4": "original (single-token 10, no fallbacks)"}}

# (a) MACE grading by k
res["mace_grading_by_k"] = {}
for j, f in FILES.items():
    b, r = rows(f["mace"][0]), rows(f["mace"][1])
    out = {}
    for gname, sel in (("k1", lambda t: t["k"] == 1), ("kgt1", lambda t: t["k"] > 1)):
        G = {"nm": [], "all": []}
        for t in mace:
            if not sel(t) or t["problem_id"] not in b or t["problem_id"] not in r:
                continue
            pid = t["problem_id"]
            refn = mnorm(t["ref_answer"])
            g = []
            for s, o in zip(t["samples"], t["oracle"]):
                if not o:
                    g.append("invalid")
                else:
                    a = mnorm(boxed(s) or s[-200:])
                    g.append("match" if (a == refn or (len(refn) > 3 and refn in a)) else "nonmatch")
            for key, keep, pos in (("nm", {"nonmatch", "invalid"}, {"nonmatch"}), ("all", {"match", "nonmatch", "invalid"}, {"match", "nonmatch"})):
                ix = [i for i, x in enumerate(g) if x in keep]
                lab = [g[i] in pos for i in ix]
                ab, ar = auroc([b[pid][i] for i in ix], lab), auroc([r[pid][i] for i in ix], lab)
                if ab is not None and ar is not None:
                    G[key].append((ab, ar))
        out[gname] = {f"G_{k}": dict(blind=boot([x[0] for x in v]), ref=boot([x[1] for x in v]), ref_minus_blind=boot([x[1] - x[0] for x in v]))
                      for k, v in G.items()}
    res["mace_grading_by_k"][j] = out


# (b) split-half moderator test
def halves(pid, t, b, r, rng):
    o = np.asarray(t["oracle"])
    idx = np.arange(len(o))
    A, B = [], []
    for cls in (0, 1):
        ii = idx[o == cls].copy()
        rng.shuffle(ii)
        h = len(ii) // 2
        A += list(ii[:h]); B += list(ii[h:])
    va = auroc([b[pid][i] for i in A], [o[i] for i in A])
    bb = auroc([b[pid][i] for i in B], [o[i] for i in B])
    rb = auroc([r[pid][i] for i in B], [o[i] for i in B])
    return (None if None in (va, bb, rb) else (va, rb - bb))


def split_test(items):
    rhos, x0, y0 = [], None, None
    for sp in range(20):
        rng = np.random.default_rng(sp)
        xy = [halves(pid, t, b, r, rng) for pid, t, b, r in items]
        xy = [p for p in xy if p is not None]
        x, y = np.array([p[0] for p in xy]), np.array([p[1] for p in xy])
        rhos.append(float(stats.spearmanr(x, y).correlation))
        if sp == 0:
            x0, y0 = x, y
    rng = np.random.default_rng(0)
    bs = []
    for _ in range(NBOOT):
        ii = rng.integers(0, len(x0), len(x0))
        bs.append(stats.spearmanr(x0[ii], y0[ii]).correlation)
    return dict(n_tasks=int(len(x0)), rho_split0=round(rhos[0], 3), rho_split0_ci=[round(float(np.nanpercentile(bs, 2.5)), 3), round(float(np.nanpercentile(bs, 97.5)), 3)],
                rho_mean_20=round(float(np.mean(rhos)), 3), rho_range_20=[round(min(rhos), 3), round(max(rhos), 3)],
                slope_split0=round(float(np.polyfit(x0, y0, 1)[0]), 3))


res["split_half"] = {}
for j, f in FILES.items():
    out, pooled = {}, []
    for name, pool in POOLS.items():
        b, r = rows(f[name][0]), rows(f[name][1])
        items = [(t["problem_id"], t, b, r) for t in pool if t["problem_id"] in b and t["problem_id"] in r
                 and sum(t["oracle"]) >= 2 and len(t["oracle"]) - sum(t["oracle"]) >= 2]
        out[name] = split_test(items)
        if name == "mace":
            out["mace_kgt1"] = split_test([it for it in items if it[1]["k"] > 1])
        pooled += items
    out["pooled"] = split_test(pooled)
    res["split_half"][j] = out

# (c) k-pool step, k>1 minus k=1
KS = {"Qwen2.5-7B": f"{S4}/kstrat__Qwen__Qwen2.5-7B-Instruct__{{}}_a.jsonl", "Qwen2.5-14B": f"{S4}/kstrat__Qwen__Qwen2.5-14B-Instruct__{{}}_a.jsonl",
      "gemma-2-9b": f"{S4}/kstrat__google__gemma-2-9b-it__{{}}_a.jsonl", "Mistral-7B": f"{S4}/kstrat__mistralai__Mistral-7B-Instruct-v0.3__{{}}_a.jsonl",
      "phi-4 (original scorer)": "runs/bon_scores_kstrat/synthk__microsoft__phi-4__{}_a.jsonl"}
res["kpool_step"] = {}
band = [t for t in kp if 0.2 <= np.mean(t["oracle"]) <= 0.8]
for j, pat in KS.items():
    n0, r0 = rows(pat.format("noref")), rows(pat.format("ref"))
    d1 = [sel_acc(r0[t["problem_id"]], t["oracle"]) - sel_acc(n0[t["problem_id"]], t["oracle"]) for t in band if t["k"] == 1]
    dg = [sel_acc(r0[t["problem_id"]], t["oracle"]) - sel_acc(n0[t["problem_id"]], t["oracle"]) for t in band if t["k"] > 1]
    rng = np.random.default_rng(0)
    a1, ag = np.array(d1), np.array(dg)
    bs = [ag[rng.integers(0, len(ag), len(ag))].mean() - a1[rng.integers(0, len(a1), len(a1))].mean() for _ in range(NBOOT)]
    res["kpool_step"][j] = dict(k1=boot(d1), kgt1=boot(dg), step=[round(float(ag.mean() - a1.mean()), 4),
                                [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]])

# (d) power to separate blind AUROC between the replication pool and MACE (Qwen2.5-7B, exact)
b_rep, b_mace = rows(FILES["Qwen2.5-7B"]["repl"][0]), rows(FILES["Qwen2.5-7B"]["mace"][0])
T_rep = [(np.asarray(b_rep[t["problem_id"]], float), np.asarray(t["oracle"])) for t in repl if 0 < sum(t["oracle"]) < len(t["oracle"])]
T_mace = [(np.asarray(b_mace[t["problem_id"]], float), np.asarray(t["oracle"])) for t in mace if 0 < sum(t["oracle"]) < len(t["oracle"])]


def draw_aurocs(T, n, m, rng):
    out = []
    while len(out) < n:
        s, o = T[rng.integers(0, len(T))]
        ii = rng.choice(len(o), size=min(m, len(o)), replace=False)
        a = auroc(list(s[ii]), list(o[ii]))
        if a is not None:
            out.append(a)
    return np.array(out)


res["power_rep_vs_mace"] = {}
rng = np.random.default_rng(0)
for m in (8, 16, 64):
    for n in (5, 10, 20, 40):
        hits = 0
        for _ in range(400):
            x, y = draw_aurocs(T_rep, n, m, rng), draw_aurocs(T_mace, n, m, rng)
            t_, p_ = stats.ttest_ind(x, y, equal_var=False)
            hits += int(p_ < 0.05 and x.mean() > y.mean())
        res["power_rep_vs_mace"][f"m{m}_n{n}"] = round(hits / 400, 3)

# (e) blind-accepted rotation filter, gainers and losers
bl, o4, r4s = rows(f"{S4}/repl__Qwen__Qwen2.5-7B-Instruct__noref_a.jsonl"), rows(f"{S4}/repl__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl"), rows(f"{S4}/replrot__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl")
rp = jl("runs/bon/bon_replrot__meta-llama__Llama-3.1-8B-Instruct.jsonl")
res["blind_accepted"] = {}
for thr in (7, 9):
    for cls in ("gainer", "loser"):
        per, keep, tot = [], 0, 0
        for it in rp:
            pid = it["problem_id"]
            target = norm(it["ref_answer"] if cls == "gainer" else it["rot_from"])
            d = []
            for i, (s, ok) in enumerate(zip(it["samples"], it["oracle"])):
                if not ok or norm(boxed(s) or s) != target:
                    continue
                tot += 1
                if bl[pid][i] is not None and bl[pid][i] >= thr:
                    keep += 1
                    d.append(r4s[pid][i] - o4[pid][i])
            if d:
                per.append(float(np.mean(d)))
        res["blind_accepted"][f"{cls}_ge{thr}"] = dict(change=boot(per), share_kept=round(keep / tot, 4))

json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
