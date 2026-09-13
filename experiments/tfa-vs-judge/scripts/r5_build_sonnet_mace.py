# R5-A pool (papers/D-iclr/registration_round5.md). Deterministic; run before any R5-A judging.
# From runs/r3/macesub.jsonl (MACE River+Language, k>1, tasks with matching and non-matching correct samples), draw 40
# tasks with numpy default_rng(5) and keep, per task, the first listed sample of each group: match, nonmatch, invalid.
import json
import os

import numpy as np

os.makedirs("runs/r5", exist_ok=True)
src = sorted((json.loads(l) for l in open("runs/r3/macesub.jsonl")), key=lambda t: t["problem_id"])
elig = [t for t in src if {"match", "nonmatch", "invalid"} <= set(t["group"])]
pick = sorted(np.random.default_rng(5).choice(len(elig), size=min(40, len(elig)), replace=False).tolist())
with open("runs/r5/sonnet_mace.jsonl", "w") as f:
    for j in pick:
        t = elig[j]
        sel = [t["group"].index(g) for g in ("match", "nonmatch", "invalid")]
        f.write(json.dumps(dict(problem_id=t["problem_id"], question=t["question"], ref_orig=t["ref_orig"], k=t["k"],
                                idx=[t["idx"][s] for s in sel], samples=[t["samples"][s] for s in sel],
                                oracle=[t["oracle"][s] for s in sel], group=["match", "nonmatch", "invalid"])) + "\n")
print("[r5 sonnet_mace] tasks:", len(pick), "of", len(elig), "eligible")
