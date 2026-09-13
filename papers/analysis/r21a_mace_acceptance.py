# POST HOC (round-20 review, M2). Run from experiments/tfa-vs-judge. Writes papers/analysis/r21a_mace_acceptance.json.
# P3 on factual questions for open judges: the matched-threshold acceptance test of r20d_matched_acceptance.py on MACE River and
# Language questions with several correct answers (all stored Llama-3.1-8B samples; answer-list labels and the containment match rule
# of r20e_benchmark_open_judges.py). Judges: Qwen2.5-7B (exact scorer) and phi-4. Threshold: the lowest blind expected score on a 0.05
# grid at or above which at most TARGET of wrong answers score; TARGET 3% (about Sonnet 5's rate for a blind 10) and 5% (about Opus 5's).
# Among correct answers at or above the threshold blind: the share scored 3 or below with the reference, differing and matching.
import ast
import json
import re

import numpy as np


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


tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/mace_tasks.jsonl")}
pool = []
for t in (json.loads(l) for l in open("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl")):
    tt = tasks[t["problem_id"]]
    p = tt["params"] if isinstance(tt["params"], dict) else ast.literal_eval(tt["params"])
    if p["domain"] in ("River", "Language") and int(tt["k"]) > 1 and "oracle" in t:
        refn = mnorm(tt["ref_answer"])
        t["match"] = [int(bool(o) and (mnorm(boxed(s) or s[-200:]) == refn or (len(refn) > 3 and refn in mnorm(boxed(s) or s[-200:]))))
                      for s, o in zip(t["samples"], t["oracle"])]
        pool.append(t)
JUD = {"Qwen2.5-7B": "runs/r4/scores/mace__Qwen__Qwen2.5-7B-Instruct__{}_a.jsonl", "phi-4": "runs/bon_scores_mace/mace__microsoft__phi-4__{}_a.jsonl"}
res = {"questions": len(pool)}
for jn, pat in JUD.items():
    b = {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(pat.format("noref"))}
    r = {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(pat.format("ref"))}
    W, C = [], []
    for t in pool:
        pid = t["problem_id"]
        if pid not in b or pid not in r:
            continue
        for bs, rs, o, m in zip(b[pid], r[pid], t["oracle"], t["match"]):
            if bs is None or rs is None:
                continue
            if o:
                C.append((bs, rs, "match" if m else "nonmatch"))
            else:
                W.append(bs)
    W = np.array(W)
    grid = np.round(np.arange(5.0, 10.001, 0.05), 2)
    for target in (0.03, 0.05):
        t_ = next((g for g in grid if (W >= g).mean() <= target), None)
        out = dict(threshold=None if t_ is None else float(t_), wrong_pass_rate=None if t_ is None else round(float((W >= t_).mean()), 4), wrong_n=int(len(W)),
                   correct_n=len(C))
        if t_ is not None:
            for g in ("nonmatch", "match"):
                sel = [rs for bs, rs, gg in C if gg == g and bs >= t_]
                out[g] = dict(n=len(sel), share_le3_with_reference=round(float(np.mean([x <= 3 for x in sel])), 4) if sel else None)
        res[f"{jn}|target{int(100 * target)}"] = out
json.dump(res, open("../../papers/analysis/r21a_mace_acceptance.json", "w"), indent=1)
print(json.dumps(res, indent=1))
