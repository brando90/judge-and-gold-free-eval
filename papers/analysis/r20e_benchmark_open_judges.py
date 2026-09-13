# POST HOC (round-19 review, M10 minimum). Run from experiments/tfa-vs-judge. Writes papers/analysis/r20e_benchmark_open_judges.json.
# What a benchmark would report: Llama-3.1-8B-Instruct's accuracy on MACE River and Language questions with several correct answers
# (all 64 stored samples per question, every question in those domains with k > 1), under three graders: the answer list, an open
# judge blind, and the same judge with the reference (a score of 7 or above counts as correct). Also the undercount among correct
# answers that differ from the reference. Judges: Qwen2.5-7B (exact scorer) and phi-4. Question-level bootstrap (2,000, seed 0).
import ast
import json
import re

import numpy as np

THRESH, NB = 7, 2000


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
        t["match"] = [int(o and (mnorm(boxed(s) or s[-200:]) == refn or (len(refn) > 3 and refn in mnorm(boxed(s) or s[-200:]))))
                      for s, o in zip(t["samples"], t["oracle"])]
        pool.append(t)
JUD = {"Qwen2.5-7B": "runs/r4/scores/mace__Qwen__Qwen2.5-7B-Instruct__{}_a.jsonl", "phi-4": "runs/bon_scores_mace/mace__microsoft__phi-4__{}_a.jsonl"}
res = {"questions": None, "threshold": THRESH, "judges": {}}
rng = np.random.default_rng(0)
for jn, pat in JUD.items():
    b = {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(pat.format("noref"))}
    r = {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(pat.format("ref"))}
    per_q = []  # (answer-list acc, blind acc, referenced acc, nonmatch-correct referenced-rejected share)
    nm_tot = [0, 0, 0]
    for t in pool:
        pid = t["problem_id"]
        if pid not in b or pid not in r:
            continue
        keep = [i for i, (x, y) in enumerate(zip(b[pid], r[pid])) if x is not None and y is not None]
        if not keep:
            continue
        o = np.array([t["oracle"][i] for i in keep], float)
        bl = np.array([b[pid][i] >= THRESH for i in keep], float)
        rf = np.array([r[pid][i] >= THRESH for i in keep], float)
        per_q.append((o.mean(), bl.mean(), rf.mean()))
        for i in keep:
            if t["oracle"][i] and not t["match"][i]:
                nm_tot[0] += 1
                nm_tot[1] += b[pid][i] >= THRESH
                nm_tot[2] += r[pid][i] >= THRESH
    A = np.array(per_q)
    n = len(A)
    boots = [rng.integers(0, n, n) for _ in range(NB)]
    ci = lambda x: [round(float(x.mean()), 4), [round(float(np.percentile([x[k].mean() for k in boots], 2.5)), 4), round(float(np.percentile([x[k].mean() for k in boots], 97.5)), 4)]]
    res["questions"] = n
    res["judges"][jn] = dict(accuracy_answer_list=ci(A[:, 0]), accuracy_blind=ci(A[:, 1]), accuracy_referenced=ci(A[:, 2]),
                             referenced_minus_list=ci(A[:, 2] - A[:, 0]), blind_minus_list=ci(A[:, 1] - A[:, 0]),
                             nonmatching_correct=nm_tot[0], nonmatching_credited_blind=round(nm_tot[1] / nm_tot[0], 4),
                             nonmatching_credited_referenced=round(nm_tot[2] / nm_tot[0], 4))
json.dump(res, open("../../papers/analysis/r20e_benchmark_open_judges.json", "w"), indent=1)
print(json.dumps(res, indent=1))
