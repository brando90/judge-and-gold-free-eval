# R2-B pools (papers/D-iclr/registration_round2.md). Deterministic, seed 0; run before any judging.
#   runs/r2/rot_sub.jsonl   : replication-pool tasks with up to 3 GAINER / LOSER / PLACEBO valid samples
#   runs/r2/ksub.jsonl      : k-pool tasks with 16 uniformly sampled samples
# Sample classes follow replrot_analysis.py exactly (loose-normalised boxed answer, fallback whole reply).
import json
import os
import re

import numpy as np

os.makedirs("runs/r2", exist_ok=True)
rng = np.random.default_rng(0)


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def extract_boxed(text):
    i = text.rfind("\\boxed{")
    if i < 0:
        return None
    j, depth = i + 7, 1
    while j < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    return text[i + 7:j - 1]


def ans(s):
    return norm(extract_boxed(s) or s)


rot = [json.loads(l) for l in open("runs/bon/bon_replrot__meta-llama__Llama-3.1-8B-Instruct.jsonl")]
n_cls = {"gainer": 0, "loser": 0, "placebo": 0}
with open("runs/r2/rot_sub.jsonl", "w") as f:
    for r in rot:
        orig, new = norm(r["rot_from"]), norm(r["ref_answer"])
        cls = {"gainer": [], "loser": [], "placebo": []}
        for i, (s, ok) in enumerate(zip(r["samples"], r["oracle"])):
            if not ok:
                continue
            a = ans(s)
            c = "gainer" if a == new else "loser" if a == orig else "placebo"
            cls[c].append(i)
        keep = {}
        for c, idx in cls.items():
            if idx:
                pick = sorted(rng.choice(idx, size=min(3, len(idx)), replace=False).tolist())
                keep[c] = pick
                n_cls[c] += len(pick)
        idxs = sorted(i for v in keep.values() for i in v)
        if not idxs:
            continue
        f.write(json.dumps(dict(problem_id=r["problem_id"], question=r["question"], ref_orig=r["rot_from"],
                                ref_rot=r["ref_answer"], idx=idxs, samples=[r["samples"][i] for i in idxs],
                                oracle=[r["oracle"][i] for i in idxs],
                                cls=[next(c for c, v in keep.items() if i in v) for i in idxs])) + "\n")
print("[rot_sub]", n_cls)

kp = [json.loads(l) for l in open("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")]
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
with open("runs/r2/ksub.jsonl", "w") as f:
    for r in kp:
        idxs = sorted(rng.choice(len(r["samples"]), size=16, replace=False).tolist())
        t = tasks[r["problem_id"]]
        f.write(json.dumps(dict(problem_id=r["problem_id"], question=t["problem"], ref_orig=t["ref_answer"],
                                k=t["k"], idx=idxs, samples=[r["samples"][i] for i in idxs],
                                oracle=[r["oracle"][i] for i in idxs])) + "\n")
print("[ksub]", len(kp), "tasks x 16 samples")
