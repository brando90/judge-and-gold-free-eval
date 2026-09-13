# R3 pools (papers/D-iclr/registration_round3.md). Deterministic, seed 1; run before any R3 judging.
#   runs/r3/macesub.jsonl : MACE River+Language tasks with k>1 that have both matching and non-matching
#                           valid samples; up to 4 matching-valid, 4 non-matching-valid, 4 invalid samples
#   runs/r3/sonnet_rot.jsonl : 60 replication-pool tasks that have all three rotation classes in
#                           runs/r2/rot_sub.jsonl; one sample per class (the first listed)
# MACE matching follows papers/analysis/mace_analysis.py exactly.
import ast
import json
import os
import re

import numpy as np

os.makedirs("runs/r3", exist_ok=True)
rng = np.random.default_rng(1)


def norm(a):
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
n = 0
with open("runs/r3/macesub.jsonl", "w") as f:
    for l in open("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
        r = json.loads(l)
        if "oracle" not in r:
            continue
        t = tasks[r["problem_id"]]
        params = t["params"] if isinstance(t["params"], dict) else ast.literal_eval(t["params"])
        k = int(t["k"])
        if params["domain"] not in ("River", "Language") or k <= 1:
            continue
        refn = norm(t["ref_answer"])
        groups = {"match": [], "nonmatch": [], "invalid": []}
        for i, (s, ok) in enumerate(zip(r["samples"], r["oracle"])):
            if not ok:
                groups["invalid"].append(i)
                continue
            a = norm(boxed(s) or s[-200:])
            groups["match" if (a == refn or (len(refn) > 3 and refn in a)) else "nonmatch"].append(i)
        if not groups["match"] or not groups["nonmatch"]:
            continue
        keep = []
        for g, idx in groups.items():
            if idx:
                keep += sorted(rng.choice(idx, size=min(4, len(idx)), replace=False).tolist())
        keep = sorted(keep)
        f.write(json.dumps(dict(problem_id=r["problem_id"], question=t["question"], ref_orig=t["ref_answer"],
                                k=k, domain=params["domain"], idx=keep, samples=[r["samples"][i] for i in keep],
                                oracle=[r["oracle"][i] for i in keep],
                                group=[next(g for g, v in groups.items() if i in v) for i in keep])) + "\n")
        n += 1
print("[macesub] tasks:", n)

rot = [json.loads(l) for l in open("runs/r2/rot_sub.jsonl")]
full = [t for t in rot if {"gainer", "loser", "placebo"} <= set(t["cls"])]
pick = sorted(rng.choice(len(full), size=min(60, len(full)), replace=False).tolist())
with open("runs/r3/sonnet_rot.jsonl", "w") as f:
    for j in pick:
        t = full[j]
        sel = [t["cls"].index(c) for c in ("gainer", "loser", "placebo")]
        f.write(json.dumps(dict(problem_id=t["problem_id"], question=t["question"], ref_orig=t["ref_orig"],
                                ref_rot=t["ref_rot"], idx=[t["idx"][s] for s in sel],
                                samples=[t["samples"][s] for s in sel], oracle=[t["oracle"][s] for s in sel],
                                cls=["gainer", "loser", "placebo"])) + "\n")
print("[sonnet_rot] tasks:", len(pick), "of", len(full), "eligible")
