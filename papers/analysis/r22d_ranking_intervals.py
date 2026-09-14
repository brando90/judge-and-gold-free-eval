# POST HOC (round-21 review, M7). Run from experiments/tfa-vs-judge. Writes papers/analysis/r22d_ranking_intervals.json.
# For each benchmark grader (R20-C Sonnet 5; R21-A Opus 5 and Haiku 4.5): Haiku 4.5 minus Llama-3.1-8B accuracy under the answer
# list, the blind judge, the referenced judge, and the max rule, with a paired question-level bootstrap (2,000 resamples, seed 0).
# Questions: those with all eight calls scored for that grader, as in r20_leaderboard_analysis.py. A score of 7 or above counts.
import json

import numpy as np

GR = {"Sonnet 5": "runs/r20/leaderboard_sonnet_api/pool.jsonl", "Opus 5": "runs/r21/leaderboard_opus_api/pool.jsonl",
      "Haiku 4.5": "runs/r21/leaderboard_haiku_api/pool.jsonl"}
pool = [json.loads(l) for l in open("runs/r20/mace_gen/pool.jsonl")]
G = pool[0]["generators"]
h, l_ = G.index("claude-haiku-4-5-20251001"), G.index("meta-llama__Llama-3.1-8B-Instruct")
res = {}
for gn, f in GR.items():
    S = {}
    for line in open(f):
        r = json.loads(line)
        if r.get("score") is not None and not r.get("error"):
            S[(r["problem_id"], r["idx"], r["cond"])] = r["score"]
    rows = [t for t in pool if all((t["problem_id"], i, c) in S for i in t["idx"] for c in ("noref", "ref"))]
    n = len(rows)
    M = {"answer_list": np.array([[t["oracle"][i] for i in range(len(G))] for t in rows], float),
         "blind": np.array([[S[(t["problem_id"], i, "noref")] >= 7 for i in range(len(G))] for t in rows], float),
         "reference": np.array([[S[(t["problem_id"], i, "ref")] >= 7 for i in range(len(G))] for t in rows], float),
         "max_rule": np.array([[max(S[(t["problem_id"], i, "noref")], S[(t["problem_id"], i, "ref")]) >= 7 for i in range(len(G))] for t in rows], float)}
    rng = np.random.default_rng(0)
    boots = [rng.integers(0, n, n) for _ in range(2000)]
    out = {"questions": n}
    for k, mat in M.items():
        d = mat[:, h] - mat[:, l_]
        m = [d[b].mean() for b in boots]
        out[k] = [round(float(d.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)]]
    res[gn] = out
json.dump(res, open("../../papers/analysis/r22d_ranking_intervals.json", "w"), indent=1)
print(json.dumps(res, indent=1))
