# POST HOC (round-9 review, question 3): an item-level version of P3 on factual questions.
# Among MACE correct answers that differ from the reference and that Sonnet 5 (R8-A, Messages API) scored 7 or above
# blind, how many does it score 3 or below with the reference? Also the same readout for the replication and k-pool
# subsamples (any-format labels). Run from experiments/tfa-vs-judge. Writes papers/analysis/r9_sonnet_item_level.json.
import json

import numpy as np

NBOOT = 1000


def boot(x, seed=0):
    x = np.asarray(x, float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


res = {}
for pool, how in (("mace", "oracle"), ("repl", "lenient"), ("kpool", "lenient")):
    S = {}
    for l in open(f"runs/r8/sonnet_api/{pool}.jsonl"):
        r = json.loads(l)
        if r.get("score") is not None and not r.get("error"):
            S[(r["problem_id"], r["idx"], r["cond"])] = r["score"]
    per_task_fr, per_task_drop, n_ans, n_tasks = [], [], 0, 0
    for t in (json.loads(l) for l in open(f"runs/r8/sonnet_{pool}.jsonl")):
        pid = t["problem_id"]
        keep = []
        for i, (idx, g, lab) in enumerate(zip(t["idx"], t["group"], t[how])):
            b, r = S.get((pid, idx, "noref")), S.get((pid, idx, "ref"))
            if lab and g == "nonmatch" and b is not None and r is not None and b >= 7:
                keep.append((b, r))
        if keep:
            n_tasks += 1
            n_ans += len(keep)
            per_task_fr.append(np.mean([r <= 3 for _, r in keep]))
            per_task_drop.append(np.mean([r - b for b, r in keep]))
    res[pool] = dict(tasks=n_tasks, answers=n_ans, share_scored_le3_with_reference=boot(per_task_fr),
                     mean_score_change=boot(per_task_drop))
json.dump(res, open("../../papers/analysis/r9_sonnet_item_level.json", "w"), indent=1)
print(json.dumps(res, indent=1))
