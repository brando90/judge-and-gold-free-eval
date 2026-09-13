# FROZEN producer for R3-D (papers/D-iclr/registration_round3.md), committed before any R3-D score exists.
# Run from experiments/tfa-vs-judge. Writes papers/analysis/r3_mace_accuracy_results.json.
import ast
import json
import os

import numpy as np

NBOOT = 1000
OUT = "../../papers/analysis/r3_mace_accuracy_results.json"
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]


def boot(x, seed=0):
    x = np.asarray(x, float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], len(x)]


def load(f):
    if not os.path.exists(f):
        return None
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))}


def sel_acc(scores, oracle):
    s = np.asarray(scores, float)
    return float(np.asarray(oracle, float)[np.isclose(s, s.max(), rtol=0, atol=1e-9)].mean())


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

res = {"n_tasks": len(pool), "n_k1": sum(r["k"] == 1 for r in pool), "n_kgt1": sum(r["k"] > 1 for r in pool)}
for j in JUDGES:
    sc = dict(noref=load(f"runs/bon_scores_mace/mace__{j}__noref_a.jsonl"), ref=load(f"runs/bon_scores_mace/mace__{j}__ref_a.jsonl"),
              m1=load(f"runs/r3/scores/mace__{j}__m1_a.jsonl"), m2=load(f"runs/r3/scores/mace__{j}__m2_a.jsonl"))
    if any(v is None for v in sc.values()):
        res[j] = "pre-data"
        continue
    items = [r for r in pool if all(r["problem_id"] in v for v in sc.values())]
    # alignment check (exploratory): mean per-task correlation of blind scores with validity
    cors = [np.corrcoef(np.asarray(sc["noref"][r["problem_id"]], float), np.asarray(r["oracle"], float))[0, 1]
            for r in items if np.std(r["oracle"]) > 0 and np.std(sc["noref"][r["problem_id"]]) > 0]
    acc = {c: {r["problem_id"]: sel_acc(sc[c][r["problem_id"]], r["oracle"]) for r in items} for c in sc}
    out = {"blind_score_validity_r": round(float(np.mean(cors)), 3)}
    for gname, sel in (("k1", lambda r: r["k"] == 1), ("kgt1", lambda r: r["k"] > 1), ("all", lambda r: True)):
        ids = [r["problem_id"] for r in items if sel(r)]
        d = {f"acc_{c}": round(float(np.mean([acc[c][p] for p in ids])), 4) for c in sc}
        for c in ("ref", "m1", "m2"):
            d[f"{c}_minus_blind"] = boot([acc[c][p] - acc["noref"][p] for p in ids])
        d["m1_minus_ref"] = boot([acc["m1"][p] - acc["ref"][p] for p in ids])
        out[gname] = d
    d1, dg = out["k1"]["m1_minus_ref"][0], out["kgt1"]["m1_minus_ref"][0]
    # post hoc: multi-answer share p at which m1 and the reference tie, (1-p)*d1 + p*dg = 0
    out["breakeven_multi_share_m1_vs_ref"] = (round(float(-d1 / (dg - d1)), 3) if (dg - d1) != 0 and 0 <= -d1 / (dg - d1) <= 1 else None)
    out["P_R3D1"] = bool(out["kgt1"]["ref_minus_blind"][1][1] < 0)
    out["P_R3D2"] = bool(out["kgt1"]["m1_minus_ref"][1][0] > 0)
    out["P_R3D3"] = bool(out["all"]["acc_m1"] >= out["all"]["acc_ref"])
    res[j] = out
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
