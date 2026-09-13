# POST HOC (round-16 review; accuracy_kgt1 added after the round-20 review). Run from experiments/tfa-vs-judge. Writes papers/analysis/r16c_protocols_exact.json.
# The protocol comparison of Table 2 under the exact scorer (no reveal calls exist under it): reference and max rule
# (max of blind and referenced score) against blind, and max rule minus reference, with paired task-bootstrap intervals.
# Accuracy: k-pool k > 1 (any-format labels, pass-rate band recomputed), MACE River/Language natural mix (pass rate in
# [0.05, 0.95], as in the registered MACE accuracy analysis), MATH-500 (pass rate in [0.2, 0.8]; reference solution and
# final answer alone). Grading AUROC: non-matching correct vs. wrong (k-pool, MACE k > 1); all correct vs. wrong (MATH-500,
# MACE k = 1). Exact scorer for Qwen2.5 and gemma-2 (runs/r4/scores); phi-4 writes "10" as one token (bon_scores files).
import ast
import json
import re

import numpy as np

NB = 2000


def jl(f):
    return [json.loads(l) for l in open(f)]


def rows(f):
    return {r["problem_id"]: r["escore"] for r in jl(f)}


def boot(x, seed=0):
    x = np.asarray(x, float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NB)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


def arr(s):
    return np.array([np.nan if v is None else v for v in s], float)


def auroc(s, pos, neg):
    s = arr(s)
    p, n = s[pos], s[neg]
    p, n = p[~np.isnan(p)], n[~np.isnan(n)]
    if not len(p) or not len(n):
        return None
    d = p[:, None] - n[None, :]
    return float((d > 0).mean() + 0.5 * (d == 0).mean())


def sel_acc(s, o):
    s = arr(s)
    s[np.isnan(s)] = -np.inf
    return float(np.asarray(o, float)[np.isclose(s, s.max(), rtol=0, atol=1e-9)].mean())


def mx(b, r):
    return [None if (x is None or y is None) else max(x, y) for x, y in zip(b, r)]


def compare(items, b, r, metric):
    per = {"blind": [], "reference": [], "max_rule": []}
    for t in items:
        pid = t["problem_id"]
        if pid not in b or pid not in r:
            continue
        vals = {"blind": metric(b[pid], t), "reference": metric(r[pid], t), "max_rule": metric(mx(b[pid], r[pid]), t)}
        if any(v is None for v in vals.values()):
            continue
        for k, v in vals.items():
            per[k].append(v)
    return dict(blind=boot(per["blind"]), reference_minus_blind=boot(np.subtract(per["reference"], per["blind"])),
                max_rule_minus_blind=boot(np.subtract(per["max_rule"], per["blind"])),
                max_rule_minus_reference=boot(np.subtract(per["max_rule"], per["reference"])))


def g_nm(lab, match):
    return lambda s, t: auroc(s, np.array([bool(l and not m) for l, m in zip(t[lab], t[match])]), np.array([not l for l in t[lab]]))


def g_all(lab):
    return lambda s, t: auroc(s, np.array([bool(l) for l in t[lab]]), np.array([not l for l in t[lab]]))


def acc(lab):
    return lambda s, t: sel_acc(s, t[lab])


S4 = "runs/r4/scores"
res = {"kpool": {}, "mace": {}, "math500": {}}
LAB = [dict(problem_id=pid, **{k: L[k] for k in ("lenient", "match", "k")}) for pid, L in ((json.loads(l)["problem_id"], json.loads(l)) for l in open("runs/r8/lenient_kpool.jsonl"))]
kgt1 = [t for t in LAB if int(t["k"]) > 1]
for jn, f in (("Qwen2.5-7B", f"{S4}/kstrat__Qwen__Qwen2.5-7B-Instruct__{{}}_a.jsonl"), ("Qwen2.5-14B", f"{S4}/kstrat__Qwen__Qwen2.5-14B-Instruct__{{}}_a.jsonl"),
              ("gemma-2-9b", f"{S4}/kstrat__google__gemma-2-9b-it__{{}}_a.jsonl"), ("phi-4", "runs/bon_scores_kstrat/synthk__microsoft__phi-4__{}_a.jsonl")):
    b, r = rows(f.format("noref")), rows(f.format("ref"))
    res["kpool"][jn] = dict(accuracy=compare([t for t in kgt1 if 0.2 <= np.mean(t["lenient"]) <= 0.8], b, r, acc("lenient")),
                            grading=compare(kgt1, b, r, g_nm("lenient", "match")))


def mnorm(a):
    return re.sub(r"[^a-z0-9]+", "", a.strip().casefold())


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


mtasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/mace_tasks.jsonl")}
mace = []
for t in jl("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    if "oracle" not in t:
        continue
    tt = mtasks[t["problem_id"]]
    p = tt["params"] if isinstance(tt["params"], dict) else ast.literal_eval(tt["params"])
    if p["domain"] not in ("River", "Language") or not (0.05 <= np.mean(t["oracle"]) <= 0.95):
        continue
    refn = mnorm(tt["ref_answer"])
    t["match"] = [int(o and (mnorm(boxed(s) or s[-200:]) == refn or (len(refn) > 3 and refn in mnorm(boxed(s) or s[-200:])))) for s, o in zip(t["samples"], t["oracle"])]
    t["k"] = int(tt["k"])
    mace.append(t)
for jn, f in (("Qwen2.5-7B", f"{S4}/mace__Qwen__Qwen2.5-7B-Instruct__{{}}_a.jsonl"), ("phi-4", "runs/bon_scores_mace/mace__microsoft__phi-4__{}_a.jsonl")):
    b, r = rows(f.format("noref")), rows(f.format("ref"))
    res["mace"][jn] = dict(accuracy_natural_mix=compare(mace, b, r, acc("oracle")),
                           accuracy_kgt1=compare([t for t in mace if t["k"] > 1], b, r, acc("oracle")),  # round 21: multi-answer questions only
                           grading_kgt1=compare([t for t in mace if t["k"] > 1], b, r, g_nm("oracle", "match")),
                           grading_k1_all_correct=compare([t for t in mace if t["k"] == 1], b, r, g_all("oracle")))
math_pool = [t for t in jl("runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl") if "oracle" in t and 0.2 <= np.mean(t["oracle"]) <= 0.8]
for jn, jt in (("Qwen2.5-7B", "Qwen__Qwen2.5-7B-Instruct"), ("Qwen2.5-14B", "Qwen__Qwen2.5-14B-Instruct")):
    b = rows(f"{S4}/math__{jt}__noref_a.jsonl")
    out = {}
    for cond in ("ref", "refans"):
        r = rows(f"{S4}/math__{jt}__{cond}_a.jsonl")
        out[cond] = dict(accuracy=compare(math_pool, b, r, acc("oracle")), grading_all_correct=compare(math_pool, b, r, g_all("oracle")))
    res["math500"][jn] = out
json.dump(res, open("../../papers/analysis/r16c_protocols_exact.json", "w"), indent=1)


def sh(v, sc=1):
    return "None" if v is None else f"{sc * v[0]:+.2f} [{sc * v[1][0]:+.2f},{sc * v[1][1]:+.2f}] n={v[2]}"


for jn, d in res["kpool"].items():
    print("kpool", jn, "ACC ref", sh(d["accuracy"]["reference_minus_blind"], 100), "max", sh(d["accuracy"]["max_rule_minus_blind"], 100),
          "| AUROC ref", sh(d["grading"]["reference_minus_blind"]), "max", sh(d["grading"]["max_rule_minus_blind"]))
for jn, d in res["mace"].items():
    print("mace", jn, "ACC ref", sh(d["accuracy_natural_mix"]["reference_minus_blind"], 100), "max", sh(d["accuracy_natural_mix"]["max_rule_minus_blind"], 100),
          "| AUROC k>1 ref", sh(d["grading_kgt1"]["reference_minus_blind"]), "max", sh(d["grading_kgt1"]["max_rule_minus_blind"]),
          "| k=1 ref", sh(d["grading_k1_all_correct"]["reference_minus_blind"]), "max", sh(d["grading_k1_all_correct"]["max_rule_minus_blind"]))
for jn, d in res["math500"].items():
    for cond, e in d.items():
        print("math", jn, cond, "ACC ref", sh(e["accuracy"]["reference_minus_blind"], 100), "max", sh(e["accuracy"]["max_rule_minus_blind"], 100),
              "max-ref", sh(e["accuracy"]["max_rule_minus_reference"], 100), "| AUROC ref", sh(e["grading_all_correct"]["reference_minus_blind"]),
              "max", sh(e["grading_all_correct"]["max_rule_minus_blind"]))
