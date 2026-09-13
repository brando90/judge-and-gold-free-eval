# POST HOC (round-15 review). Run from experiments/tfa-vs-judge. Writes papers/analysis/r16b_unique_answer_grading.json.
# Does the max rule give up the reference's grading benefit when the answer is unique? Overall grading AUROC (all correct
# vs. wrong answers, per task) for blind, reference, max(blind, reference), and blind-then-reveal, original scorer:
# MACE River/Language k = 1 (answer lists) and MATH-500 (unique answers), with paired task-bootstrap intervals.
import ast
import json

import numpy as np

NB = 2000


def jl(f):
    return [json.loads(l) for l in open(f)]


def rows(f):
    return {r["problem_id"]: r["escore"] for r in jl(f)}


def boot(x, seed=0):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NB)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


def auroc(s, o):
    s = np.array([np.nan if v is None else v for v in s], float)
    o = np.asarray(o, bool)
    p, n = s[o], s[~o]
    p, n = p[~np.isnan(p)], n[~np.isnan(n)]
    if not len(p) or not len(n):
        return None
    d = p[:, None] - n[None, :]
    return float((d > 0).mean() + 0.5 * (d == 0).mean())


def run(items, b, r, m1):
    per = {k: [] for k in ("blind", "reference", "max_rule", "reveal")}
    for t in items:
        pid = t["problem_id"]
        if not all(pid in x for x in (b, r, m1)):
            continue
        mx = [None if (x is None or y is None) else max(x, y) for x, y in zip(b[pid], r[pid])]
        vals = dict(blind=auroc(b[pid], t["oracle"]), reference=auroc(r[pid], t["oracle"]), max_rule=auroc(mx, t["oracle"]),
                    reveal=auroc(m1[pid], t["oracle"]))
        if any(v is None for v in vals.values()):
            continue
        for k, v in vals.items():
            per[k].append(v)
    out = {k: boot(v) for k, v in per.items()}
    for k in ("reference", "max_rule", "reveal"):
        out[f"{k}_minus_blind"] = boot(np.subtract(per[k], per["blind"]))
    for k in ("max_rule", "reveal"):
        out[f"{k}_minus_reference"] = boot(np.subtract(per[k], per["reference"]))
    return out


res = {"mace_k1": {}, "math500": {}}
mtasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/mace_tasks.jsonl")}
mace = []
for t in jl("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    if "oracle" not in t:
        continue
    tt = mtasks[t["problem_id"]]
    p = tt["params"] if isinstance(tt["params"], dict) else ast.literal_eval(tt["params"])
    if p["domain"] in ("River", "Language") and int(tt["k"]) == 1 and 0.05 <= np.mean(t["oracle"]) <= 0.95:
        mace.append(t)
for jn, jt in (("Qwen2.5-7B", "Qwen__Qwen2.5-7B-Instruct"), ("phi-4", "microsoft__phi-4")):
    res["mace_k1"][jn] = run(mace, rows(f"runs/bon_scores_mace/mace__{jt}__noref_a.jsonl"), rows(f"runs/bon_scores_mace/mace__{jt}__ref_a.jsonl"),
                             rows(f"runs/r3/scores/mace__{jt}__m1_a.jsonl"))
math_pool = [t for t in jl("runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl") if "oracle" in t and 0.2 <= np.mean(t["oracle"]) <= 0.8]
for jn, jt in (("Qwen2.5-7B", "Qwen__Qwen2.5-7B-Instruct"), ("Qwen2.5-14B", "Qwen__Qwen2.5-14B-Instruct")):
    res["math500"][jn] = run(math_pool, rows(f"runs/r2/frozen_math/math__{jt}__noref_a.jsonl"), rows(f"runs/r2/frozen_math/math__{jt}__ref_a.jsonl"),
                             rows(f"runs/r2/scores/math__{jt}__m1_a.jsonl"))
json.dump(res, open("../../papers/analysis/r16b_unique_answer_grading.json", "w"), indent=1)
for pool, d in res.items():
    for jn, g in d.items():
        f = lambda v: f"{v[0]:+.3f} [{v[1][0]:+.3f},{v[1][1]:+.3f}] n={v[2]}"
        print(pool, jn, "blind", f(g["blind"]), "| ref-blind", f(g["reference_minus_blind"]), "| max-blind", f(g["max_rule_minus_blind"]),
              "| max-ref", f(g["max_rule_minus_reference"]), "| reveal-blind", f(g["reveal_minus_blind"]))
