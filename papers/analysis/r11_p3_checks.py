# POST HOC (round-11 review, P3 questions). Run from experiments/tfa-vs-judge. Writes papers/analysis/r11_p3_checks.json.
#  (a) Does "scored 7 or above blind" mean "verified"? Share of wrong and of correct answers scored >= 7 blind, per judge,
#      replication pool (any-format labels), and for Sonnet 5 on its R8-A subsamples (API).
#  (b) Does the swap effect shrink where the judge verifies better? Per replication task, Qwen2.5-7B (exact scorer):
#      swap size = mean(gain of samples the rotated reference moves onto, loss of samples it moves off), against the
#      task's blind AUROC for correct vs wrong answers (any-format labels). Spearman rho with task bootstrap CI, and the
#      mean swap size by tercile of blind AUROC. A pure verification-failure account predicts a negative relation.
import ast
import json
import re

import numpy as np
from scipy.stats import spearmanr

NBOOT = 2000
rng = np.random.default_rng(0)


def jl(f):
    return [json.loads(l) for l in open(f)]


def rows(f):
    return {r["problem_id"]: r["escore"] for r in jl(f)}


def ints_of(a):
    return [int(x) for x in re.findall(r"-?\d+", a or "")]


def auroc(sc, lab):
    pos = np.array([s for s, l in zip(sc, lab) if l and s is not None], float)
    neg = np.array([s for s, l in zip(sc, lab) if not l and s is not None], float)
    if len(pos) == 0 or len(neg) == 0:
        return None
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


res = {}
pool = {t["problem_id"]: t for t in jl("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl")}
LEN = {r["problem_id"]: r for r in jl("runs/r8/lenient_repl.jsonl")}
S4 = "runs/r4/scores"
JUDGES = {"Qwen2.5-7B": f"{S4}/repl__Qwen__Qwen2.5-7B-Instruct__noref_a.jsonl",
          "phi-4": "runs/bon_scores_repl/synthk__microsoft__phi-4__noref_a.jsonl",
          "GPT-4.1": "runs/bon_scores_repl/synthk__openai__gpt-4.1-2025-04-14__noref_a.jsonl"}

# (a) open and API judges, full replication pool
res["accepted_filter"] = {}
for jn, f in JUDGES.items():
    b = rows(f)
    w = c = nw = nc = 0
    for pid, L in LEN.items():
        if pid not in b:
            continue
        for s, lab in zip(b[pid], L["lenient"]):
            if s is None:
                continue
            if lab:
                nc += 1; c += s >= 7
            else:
                nw += 1; w += s >= 7
    res["accepted_filter"][jn] = dict(share_correct_ge7=round(c / nc, 4), share_wrong_ge7=round(w / nw, 4), n_correct=nc, n_wrong=nw)
for pool_name, how in (("repl", "lenient"), ("mace", "oracle"), ("kpool", "lenient")):
    S = {}
    for r in jl(f"runs/r8/sonnet_api/{pool_name}.jsonl"):
        if r.get("score") is not None and r["cond"] == "noref":
            S[(r["problem_id"], r["idx"])] = r["score"]
    w = c = nw = nc = 0
    for t in jl(f"runs/r8/sonnet_{pool_name}.jsonl"):
        for idx, lab in zip(t["idx"], t[how]):
            s = S.get((t["problem_id"], idx))
            if s is None:
                continue
            if lab:
                nc += 1; c += s >= 7
            else:
                nw += 1; w += s >= 7
    res["accepted_filter"][f"Sonnet 5 (API, {pool_name} subsamples)"] = dict(share_correct_ge7=round(c / nc, 4), share_wrong_ge7=round(w / nw, 4), n_correct=nc, n_wrong=nw)

# (b) swap size against blind AUROC, Qwen2.5-7B exact scorer
rot = {t["problem_id"]: t for t in jl("runs/bon/bon_replrot__meta-llama__Llama-3.1-8B-Instruct.jsonl")}
b, r0, r1 = rows(JUDGES["Qwen2.5-7B"]), rows(f"{S4}/repl__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl"), rows(f"{S4}/replrot__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl")
xs, ys = [], []
for pid, t in pool.items():
    if pid not in rot or pid not in b or pid not in r0 or pid not in r1:
        continue
    L = LEN[pid]
    orig, new = sorted(ints_of(t["ref_answer"])), sorted(ints_of(rot[pid]["ref_answer"]))
    if orig == new:
        continue
    gains, losses = [], []
    for i, (lab, ext) in enumerate(zip(L["lenient"], L["extracted"])):
        if not lab or r0[pid][i] is None or r1[pid][i] is None:
            continue
        e = sorted(ints_of(ext))
        if e == new:
            gains.append(r1[pid][i] - r0[pid][i])
        elif e == orig:
            losses.append(r0[pid][i] - r1[pid][i])
    a = auroc(b[pid], L["lenient"])
    if a is None or not (gains or losses):
        continue
    xs.append(a)
    ys.append(float(np.mean(gains + losses)))
xs, ys = np.array(xs), np.array(ys)
rho = spearmanr(xs, ys).correlation
boots = []
for _ in range(NBOOT):
    ix = rng.integers(0, len(xs), len(xs))
    boots.append(spearmanr(xs[ix], ys[ix]).correlation)
q = np.quantile(xs, [1 / 3, 2 / 3])
terc = {}
for name, m in (("low", xs <= q[0]), ("middle", (xs > q[0]) & (xs <= q[1])), ("high", xs > q[1])):
    terc[name] = dict(n=int(m.sum()), blind_auroc_mean=round(float(xs[m].mean()), 3), swap_size_mean=round(float(ys[m].mean()), 3))
res["swap_vs_blind_auroc_qwen7b"] = dict(n_tasks=len(xs), spearman=round(float(rho), 3),
                                          ci=[round(float(np.nanpercentile(boots, 2.5)), 3), round(float(np.nanpercentile(boots, 97.5)), 3)],
                                          terciles=terc)
json.dump(res, open("../../papers/analysis/r11_p3_checks.json", "w"), indent=1)
print(json.dumps(res, indent=1))
