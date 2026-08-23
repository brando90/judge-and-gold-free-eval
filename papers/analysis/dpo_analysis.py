# Registered analysis for the DPO gating experiment (P-D1..P-D3 in scripts/dpo_pairs.py,
# commit 3a964f1). COMMITTED BEFORE TRAINING RAN so the analysis is pre-registered.
# Run from experiments/tfa-vs-judge once runs/dpo/eval_*.jsonl and
# runs/dpo/scores_{policy}__judge_{cond}.jsonl exist.
#
# Estimands, per split (train items, held-out items):
#  true_acc(policy): mean oracle pass rate over samples.
#  judge_score(policy, judge): mean escore over samples under each frozen judge.
#  Gains are policy minus base, with item-paired bootstrap CIs.
#  P-D1: certified arm (trained on honest-referenced pairs): true-accuracy gain > 0 on
#    held-out items, and its judge gain under the honest judge agrees in sign.
#  P-D2: convicted arm (sabotage pairs): wedge = (own-judge score gain, standardized by the
#    base pool score sd) minus (true gain) is LARGER than the certified arm's wedge, and its
#    true gain is smaller than the certified arm's.
#  P-D3: instrument specificity: the sabotage-trained policy's score gain is larger under
#    the sabotaged judge than under the honest judge; the certified arm's gain transfers.
import json
import os
from collections import defaultdict

import numpy as np

rng = np.random.default_rng(0)

POLICIES = ["base", "ref", "sabotage"]
JUDGES = ["ref", "sabotage"]

acc = {}   # (policy, split) -> {pid: pass rate}
for p in POLICIES:
    f = f"runs/dpo/eval_{p}.jsonl"
    if not os.path.exists(f):
        raise SystemExit(f"missing {f}")
    for l in open(f):
        r = json.loads(l)
        acc[(p, r["split"], r["problem_id"])] = float(np.mean(r["oracle"]))

js = {}    # (policy, judge, split) -> {pid: mean escore}
for p in POLICIES:
    for j in JUDGES:
        f = f"runs/dpo/scores_{p}__judge_{j}.jsonl"
        if not os.path.exists(f):
            continue
        for l in open(f):
            r = json.loads(l)
            js[(p, j, r["split"], r["problem_id"])] = float(np.mean(r["escore"]))


def paired_gain(metric, policy, split, base="base"):
    pids = sorted({k[2] for k in metric if k[0] == policy and k[1] == split}
                  & {k[2] for k in metric if k[0] == base and k[1] == split})
    d = np.array([metric[(policy, split, p)] - metric[(base, split, p)] for p in pids])
    boot = [float(np.mean(rng.choice(d, len(d)))) for _ in range(4000)]
    return dict(n=len(pids), gain=round(float(d.mean()), 4),
                ci=[round(float(np.percentile(boot, 2.5)), 4),
                    round(float(np.percentile(boot, 97.5)), 4)])


acc_metric = {(p, s, pid): v for (p, s, pid), v in acc.items()}
out = {"true_gain": {}, "judge_gain": {}, "wedge": {}}
for p in ("ref", "sabotage"):
    for split in ("train", "heldout"):
        out["true_gain"][f"{p}__{split}"] = paired_gain(acc_metric, p, split)

for p in ("ref", "sabotage"):
    for j in JUDGES:
        for split in ("train", "heldout"):
            metric = {(pp, s, pid): v for (pp, jj, s, pid), v in js.items() if jj == j}
            if not any(k[0] == p for k in metric):
                continue
            out["judge_gain"][f"{p}__under_{j}__{split}"] = paired_gain(metric, p, split)

# wedge: standardized own-judge gain minus true gain, item-paired
for p, own in (("ref", "ref"), ("sabotage", "sabotage")):
    for split in ("train", "heldout"):
        pids = sorted({k[3] for k in js if k[0] == p and k[1] == own and k[2] == split}
                      & {k[2] for k in acc if k[0] == "base" and k[1] == split})
        base_scores = [js[("base", own, split, pid)] for pid in pids
                       if ("base", own, split, pid) in js]
        sd = float(np.std(base_scores)) or 1.0
        d = []
        for pid in pids:
            if ("base", own, split, pid) not in js:
                continue
            jg = (js[(p, own, split, pid)] - js[("base", own, split, pid)]) / sd
            tg = acc[(p, split, pid)] - acc[("base", split, pid)]
            d.append(jg - tg)
        d = np.array(d)
        boot = [float(np.mean(rng.choice(d, len(d)))) for _ in range(4000)]
        out["wedge"][f"{p}__{split}"] = dict(
            n=len(d), wedge=round(float(d.mean()), 3),
            ci=[round(float(np.percentile(boot, 2.5)), 3),
                round(float(np.percentile(boot, 97.5)), 3)])

json.dump(out, open("../../papers/analysis/dpo_results.json", "w"), indent=1)
print(json.dumps(out, indent=1))
