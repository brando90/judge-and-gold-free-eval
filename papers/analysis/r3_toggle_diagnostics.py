# POST HOC diagnostics for R3-A / R3-C (no registration weight). Run from experiments/tfa-vs-judge.
# Mean generated tokens and mean valid-sample score per pool, condition, and thinking arm for Qwen3-8B.
import json
import os

import numpy as np

OUT = "../../papers/analysis/r3_toggle_diagnostics.json"
POOLS = {"rot": "runs/r2/rot_sub.jsonl", "ksub": "runs/r2/ksub.jsonl", "macesub": "runs/r3/macesub.jsonl"}
res = {}
for pool, pf in POOLS.items():
    tasks = {r["problem_id"]: r for r in (json.loads(l) for l in open(pf))}
    conds = ("ref", "refrot", "noref") if pool == "rot" else ("ref", "noref")
    for arm in ("on", "off"):
        for c in conds:
            f = (f"runs/r2/scores/{pool}__reason__Qwen__Qwen3-8B__{c}.jsonl" if arm == "on" and pool != "macesub"
                 else f"runs/r3/scores/{pool}__think{arm}__Qwen__Qwen3-8B__{c}.jsonl")
            if not os.path.exists(f):
                continue
            tok, val = [], []
            for r in (json.loads(l) for l in open(f)):
                orc = dict(zip(tasks[r["problem_id"]]["idx"], tasks[r["problem_id"]]["oracle"]))
                for idx, s, n in zip(r["idx"], r["score"], r["n_tokens"]):
                    tok.append(n)
                    if s is not None and orc[idx]:
                        val.append(s)
            res[f"{pool}|{arm}|{c}"] = dict(tokens_mean=int(round(float(np.mean(tok)))), valid_score_mean=round(float(np.mean(val)), 2),
                                            valid_share_10=round(float(np.mean([v == 10 for v in val])), 3))
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
