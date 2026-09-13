# POST HOC: per-task points behind the split-half scatter (split 0 of r5_posthoc.py, same task order and seeds).
# Run from experiments/tfa-vs-judge. Writes papers/analysis/r5_splithalf_points.json.
import ast
import json

import numpy as np


def auroc(sc, lab):
    pos = np.array([s for s, l in zip(sc, lab) if l and s is not None], float)
    neg = np.array([s for s, l in zip(sc, lab) if not l and s is not None], float)
    if len(pos) == 0 or len(neg) == 0:
        return None
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def rows(f):
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))}


mtasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/mace_tasks.jsonl")}
mace = []
for l in open("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    t = json.loads(l)
    if "oracle" not in t:
        continue
    tt = mtasks[t["problem_id"]]
    params = tt["params"] if isinstance(tt["params"], dict) else ast.literal_eval(tt["params"])
    if params["domain"] in ("River", "Language") and 0.05 <= np.mean(t["oracle"]) <= 0.95:
        t["k"] = int(tt["k"])
        mace.append(t)
FILES = {"Qwen2.5-7B": ("runs/r4/scores/mace__Qwen__Qwen2.5-7B-Instruct__noref_a.jsonl", "runs/r4/scores/mace__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl"),
         "phi-4": ("runs/bon_scores_mace/mace__microsoft__phi-4__noref_a.jsonl", "runs/bon_scores_mace/mace__microsoft__phi-4__ref_a.jsonl")}
out = {}
for j, (fb, fr) in FILES.items():
    b, r = rows(fb), rows(fr)
    items = [t for t in mace if t["problem_id"] in b and t["problem_id"] in r and sum(t["oracle"]) >= 2 and len(t["oracle"]) - sum(t["oracle"]) >= 2]
    rng = np.random.default_rng(0)
    xs, ys, ks = [], [], []
    for t in items:
        pid = t["problem_id"]
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
        if None in (va, bb, rb):
            continue
        xs.append(round(va, 4)); ys.append(round(rb - bb, 4)); ks.append(t["k"])
    out[j] = dict(x=xs, y=ys, k=ks)
json.dump(out, open("../../papers/analysis/r5_splithalf_points.json", "w"))
from scipy import stats
print({j: (len(v["x"]), round(float(stats.spearmanr(v["x"], v["y"]).correlation), 3)) for j, v in out.items()})
