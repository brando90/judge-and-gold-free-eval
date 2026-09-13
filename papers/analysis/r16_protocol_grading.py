# POST HOC (round-15 review). Run from experiments/tfa-vs-judge. Writes papers/analysis/r16_protocol_grading.json.
# Grading and selection under three protocols built from stored scores (original scorer, as in the protocol table):
#   reference (referenced score), max rule (max of blind and referenced score), blind-then-reveal (stored m1 reveal calls).
# Grading AUROC: correct answers that differ from the reference vs. wrong answers, per task; changes vs. blind and vs. the
# reference, paired task bootstrap. k-pool (k > 1, any-format labels) and MACE (River/Language, k > 1, answer lists).
# Selection: best-of-64 accuracy, paired intervals for rule minus reference and rule minus blind (k-pool any-format and
# registered labels; MACE natural mix; MATH-500).
import ast
import glob
import json
import re

import numpy as np

NB = 2000


def jl(f):
    return [json.loads(l) for l in open(f)]


def rows(f):
    try:
        return {r["problem_id"]: r["escore"] for r in jl(f)}
    except FileNotFoundError:
        return None


def boot(x, seed=0):
    x = np.asarray(x, float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NB)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


def auroc(s, pos, neg):
    s = np.array([np.nan if v is None else v for v in s], float)
    p, n = s[pos], s[neg]
    p, n = p[~np.isnan(p)], n[~np.isnan(n)]
    if not len(p) or not len(n):
        return None
    d = p[:, None] - n[None, :]
    return float((d > 0).mean() + 0.5 * (d == 0).mean())


def sel_acc(s, o):
    s = np.array([-np.inf if v is None else v for v in s], float)
    return float(np.asarray(o, float)[np.isclose(s, s.max(), rtol=0, atol=1e-9)].mean())


def mx(b, r):
    return [None if (x is None or y is None) else max(x, y) for x, y in zip(b, r)]


def protocols(b, r, m1, pid):
    return {"blind": b[pid], "reference": r[pid], "max_rule": mx(b[pid], r[pid]), "reveal": m1[pid]}


def grading(items, S, lab_fn):
    per = {k: [] for k in ("blind", "reference", "max_rule", "reveal")}
    for t in items:
        pid = t["problem_id"]
        if not all(pid in x for x in S):
            continue
        pos, neg = lab_fn(t)
        if not pos.any() or not neg.any():
            continue
        pr = protocols(*S, pid)
        vals = {k: auroc(v, pos, neg) for k, v in pr.items()}
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


def selection(items, S, lab_key):
    per = {k: [] for k in ("blind", "reference", "max_rule", "reveal")}
    for t in items:
        pid = t["problem_id"]
        if not all(pid in x for x in S):
            continue
        for k, v in protocols(*S, pid).items():
            per[k].append(sel_acc(v, t[lab_key]))
    out = {}
    for k in ("reference", "max_rule", "reveal"):
        out[f"{k}_minus_blind"] = boot(np.subtract(per[k], per["blind"]))
    for k in ("max_rule", "reveal"):
        out[f"{k}_minus_reference"] = boot(np.subtract(per[k], per["reference"]))
    return out


res = {"kpool": {}, "mace": {}, "math500": {}, "sanity": {}}
KP = "runs/bon_scores_kstrat"
kp_pool = {t["problem_id"]: t for t in jl("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")}
LAB = {t["problem_id"]: t for t in jl("runs/r8/lenient_kpool.jsonl")}
for jn, jt in (("Qwen2.5-7B", "Qwen__Qwen2.5-7B-Instruct"), ("Qwen2.5-14B", "Qwen__Qwen2.5-14B-Instruct"),
               ("gemma-2-9b", "google__gemma-2-9b-it"), ("phi-4", "microsoft__phi-4")):
    S = (rows(f"{KP}/synthk__{jt}__noref_a.jsonl"), rows(f"{KP}/synthk__{jt}__ref_a.jsonl"), rows(f"{KP}/kstrat__{jt}__m1_a.jsonl"))
    if any(x is None for x in S):
        continue
    items = []
    for pid, L in LAB.items():
        if int(L["k"]) > 1 and pid in kp_pool:
            items.append(dict(problem_id=pid, lenient=L["lenient"], match=L["match"], oracle=kp_pool[pid]["oracle"]))
    g = grading(items, S, lambda t: (np.array([bool(l and not m) for l, m in zip(t["lenient"], t["match"])]),
                                     np.array([not l for l in t["lenient"]])))
    band_any = [t for t in items if 0.2 <= np.mean(t["lenient"]) <= 0.8]
    band_reg = [t for t in items if 0.2 <= np.mean(t["oracle"]) <= 0.8]
    res["kpool"][jn] = dict(grading_any_format=g, selection_any_format=selection(band_any, S, "lenient"),
                            selection_registered=selection(band_reg, S, "oracle"))
# sanity: exact-scorer reference change on the k-pool for Qwen2.5-7B (compare the published any-format value, -0.23)
S4 = "runs/r4/scores"
b4, r4_ = rows(f"{S4}/kstrat__Qwen__Qwen2.5-7B-Instruct__noref_a.jsonl"), rows(f"{S4}/kstrat__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl")
if b4 and r4_:
    items = [dict(problem_id=pid, lenient=L["lenient"], match=L["match"]) for pid, L in LAB.items() if int(L["k"]) > 1]
    res["sanity"]["kpool_qwen7b_exact_reference_minus_blind"] = grading(items, (b4, r4_, r4_), lambda t: (
        np.array([bool(l and not m) for l, m in zip(t["lenient"], t["match"])]), np.array([not l for l in t["lenient"]])))["reference_minus_blind"]


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
mace_all = []
for t in jl("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    if "oracle" not in t:
        continue
    tt = mtasks[t["problem_id"]]
    p = tt["params"] if isinstance(tt["params"], dict) else ast.literal_eval(tt["params"])
    if p["domain"] not in ("River", "Language"):
        continue
    refn = mnorm(tt["ref_answer"])
    t["match"] = [int(o and (mnorm(boxed(s) or s[-200:]) == refn or (len(refn) > 3 and refn in mnorm(boxed(s) or s[-200:]))))
                  for s, o in zip(t["samples"], t["oracle"])]
    t["k"] = int(tt["k"])
    mace_all.append(t)
for jn, jt in (("Qwen2.5-7B", "Qwen__Qwen2.5-7B-Instruct"), ("phi-4", "microsoft__phi-4")):
    S = (rows(f"runs/bon_scores_mace/mace__{jt}__noref_a.jsonl"), rows(f"runs/bon_scores_mace/mace__{jt}__ref_a.jsonl"),
         rows(f"runs/r3/scores/mace__{jt}__m1_a.jsonl"))
    if any(x is None for x in S):
        continue
    grad_items = [t for t in mace_all if t["k"] > 1 and 0.05 <= np.mean(t["oracle"]) <= 0.95]
    g = grading(grad_items, S, lambda t: (np.array([bool(o and not m) for o, m in zip(t["oracle"], t["match"])]),
                                          np.array([not o for o in t["oracle"]])))
    sel_items = [t for t in mace_all if 0.2 <= np.mean(t["oracle"]) <= 0.8]
    res["mace"][jn] = dict(grading=g, selection_natural_mix=selection(sel_items, S, "oracle"))

math_pool = [t for t in jl("runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl") if "oracle" in t and 0.2 <= np.mean(t["oracle"]) <= 0.8]
for jn, jt in (("Qwen2.5-7B", "Qwen__Qwen2.5-7B-Instruct"), ("Qwen2.5-14B", "Qwen__Qwen2.5-14B-Instruct")):
    m1f = sorted(glob.glob(f"runs/r2/**/math*{jt}*m1*_a.jsonl", recursive=True) + glob.glob(f"runs/**/math__{jt}__m1_a.jsonl", recursive=True))
    S = (rows(f"runs/r2/frozen_math/math__{jt}__noref_a.jsonl"), rows(f"runs/r2/frozen_math/math__{jt}__ref_a.jsonl"), rows(m1f[0]) if m1f else None)
    res["math500"][jn] = dict(files_m1=m1f[:1], selection=selection(math_pool, S, "oracle") if all(x is not None for x in S) else None)
json.dump(res, open("../../papers/analysis/r16_protocol_grading.json", "w"), indent=1)


def show(v, s=1):
    return "None" if v is None else f"{s * v[0]:+.3f} [{s * v[1][0]:+.3f},{s * v[1][1]:+.3f}] n={v[2]}"


for pool in ("kpool", "mace"):
    for jn, d in res[pool].items():
        g = d["grading_any_format"] if pool == "kpool" else d["grading"]
        print(pool, jn, "GRADING ref-blind", show(g["reference_minus_blind"]), "| max-blind", show(g["max_rule_minus_blind"]),
              "| reveal-blind", show(g["reveal_minus_blind"]), "| blind lvl", show(g["blind"]))
        for sk in [k for k in d if k.startswith("selection")]:
            s = d[sk]
            print("   ", sk, "ref-blind", show(s["reference_minus_blind"], 100), "| max-blind", show(s["max_rule_minus_blind"], 100),
                  "| max-ref", show(s["max_rule_minus_reference"], 100), "| reveal-ref", show(s["reveal_minus_reference"], 100))
for jn, d in res["math500"].items():
    s = d["selection"]
    print("math", jn, d["files_m1"], None if not s else ("ref-blind " + show(s["reference_minus_blind"], 100) + " | max-ref " + show(s["max_rule_minus_reference"], 100) + " | reveal-ref " + show(s["reveal_minus_reference"], 100)))
print("sanity", res["sanity"])
