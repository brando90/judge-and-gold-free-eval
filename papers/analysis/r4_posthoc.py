# POST HOC readouts for the round-4 revision (no registration weight; papers/D-iclr/registration_round4.md lists them).
# Run from experiments/tfa-vs-judge. Writes papers/analysis/r4_posthoc_results.json.
#   - MACE River+Language selection accuracy by k (1, 2, 4, 6), frozen score files, as r3_mace_accuracy_analysis.py
#   - protocol regret: for blind, reference, and blind-then-reveal, accuracy minus the best of the three in each pool
#     (k-pool k>1, MATH-500, MACE), and the worst case over pools, per judge where all three pools exist
import ast
import json
import os

import numpy as np

NBOOT = 1000
OUT = "../../papers/analysis/r4_posthoc_results.json"
A = "../../papers/analysis"


def boot(x, seed=0):
    x = np.asarray(x, float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


def load(f):
    if not os.path.exists(f):
        return None
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))}


def sel_acc(scores, oracle):
    s = np.asarray(scores, float)
    return float(np.asarray(oracle, float)[np.isclose(s, s.max(), rtol=0, atol=1e-9)].mean())


res = {}
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/mace_tasks.jsonl")}
pool = []
for l in open("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    r = json.loads(l)
    if "oracle" not in r:
        continue
    t = tasks[r["problem_id"]]
    params = t["params"] if isinstance(t["params"], dict) else ast.literal_eval(t["params"])
    if params["domain"] in ("River", "Language") and 0.05 <= np.mean(r["oracle"]) <= 0.95:
        r["k"] = int(t["k"])
        pool.append(r)
res["mace_by_k"] = {}
for j in ("Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"):
    sc = dict(noref=load(f"runs/bon_scores_mace/mace__{j}__noref_a.jsonl"), ref=load(f"runs/bon_scores_mace/mace__{j}__ref_a.jsonl"),
              m1=load(f"runs/r3/scores/mace__{j}__m1_a.jsonl"))
    items = [r for r in pool if all(r["problem_id"] in v for v in sc.values())]
    out = {}
    for k in (1, 2, 4, 6):
        ids = [r for r in items if r["k"] == k]
        acc = {c: [sel_acc(sc[c][r["problem_id"]], r["oracle"]) for r in ids] for c in sc}
        out[f"k{k}"] = dict(n=len(ids), **{f"acc_{c}": round(float(np.mean(v)), 4) if v else None for c, v in acc.items()},
                            ref_minus_blind=boot(np.subtract(acc["ref"], acc["noref"])),
                            m1_minus_ref=boot(np.subtract(acc["m1"], acc["ref"])))
    res["mace_by_k"][j] = out

acc = json.load(open(f"{A}/accuracy_readouts.json"))
m1math = json.load(open(f"{A}/r2_math_m1_results.json"))
mace = json.load(open(f"{A}/r3_mace_accuracy_results.json"))
res["regret"] = {}
for j in ("Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4", "Qwen__Qwen2.5-14B-Instruct"):
    pools = {}
    kp = acc["kpool"].get(j, {}).get("kgt1")
    if kp:
        pools["kpool_kgt1"] = dict(blind=kp["acc_noref"][0], ref=kp["acc_ref"][0], reveal=kp["acc_m1"][0])
    mm = m1math.get(j)
    if isinstance(mm, dict) and "acc_m1" in mm:
        g = lambda v: v[0] if isinstance(v, list) else v
        pools["math500"] = dict(blind=g(mm["acc_blind"]), ref=g(mm["acc_ref"]), reveal=g(mm["acc_m1"]))
    ma = mace.get(j)
    if isinstance(ma, dict):
        pools["mace"] = dict(blind=ma["all"]["acc_noref"], ref=ma["all"]["acc_ref"], reveal=ma["all"]["acc_m1"])
    reg = {p: {c: round(v - max(d.values()), 4) for c, v in d.items()} for p, d in pools.items()}
    worst = {c: round(min(r[c] for r in reg.values()), 4) for c in ("blind", "ref", "reveal")} if reg else None
    res["regret"][j] = dict(accuracy=pools, regret=reg, worst_case=worst, pools_available=sorted(pools))
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
