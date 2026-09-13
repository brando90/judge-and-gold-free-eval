# POST HOC robustness for the round-7 revision (no registration weight). Run from experiments/tfa-vs-judge.
# Writes papers/analysis/r7b_posthoc_results.json.
#  (a) what the "lure" candidates are: wrong candidates whose text contains the reference's answer, by pool
#  (b) replication-pool grading AUROC and selection accuracy with those candidates removed
#  (c) MACE: share of wrong candidates containing the reference's answer text, and grading with them removed
#  (d) MATH-500: score-combination rules against blind-then-reveal (original scorer), Qwen2.5-7B and 14B
import ast
import json
import os
import re

import numpy as np

NBOOT = 1000
OUT = "../../papers/analysis/r7b_posthoc_results.json"
S4 = "runs/r4/scores"


def boot(x, seed=0):
    x = np.asarray([v for v in x if v is not None], float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


def rows(f, key="escore"):
    return {r["problem_id"]: r[key] for r in (json.loads(l) for l in open(f))} if os.path.exists(f) else None


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", (a or "").strip().casefold())


def mnorm(a):
    return re.sub(r"[^a-z0-9]+", "", (a or "").strip().casefold())


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


def auroc(sc, lab):
    pos = np.array([s for s, l in zip(sc, lab) if l and s is not None], float)
    neg = np.array([s for s, l in zip(sc, lab) if not l and s is not None], float)
    if len(pos) == 0 or len(neg) == 0:
        return None
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def sel_acc(scores, oracle, keep=None):
    ix = [i for i in range(len(oracle)) if (keep is None or keep[i]) and scores[i] is not None]
    if not ix:
        return None
    s = np.array([scores[i] for i in ix], float)
    o = np.array([oracle[i] for i in ix], float)
    return float(o[np.isclose(s, s.max(), rtol=0, atol=1e-9)].mean())


def jl(f):
    return [json.loads(l) for l in open(f)]


res = {}
repl = jl("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl")
kp = jl("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")

# (a) lure characterization on the constructed pools
res["lure_character"] = {}
for name, pool in (("replication", repl), ("kpool", kp)):
    n_wrong = n_lure = n_lure_nobox = n_lure_boxed_other = n_lure_boxed_eq = 0
    for t in pool:
        refn = norm(t["ref_answer"])
        for s, o in zip(t["samples"], t["oracle"]):
            if o:
                continue
            n_wrong += 1
            if refn and refn in norm(s):
                n_lure += 1
                b = boxed(s)
                if b is None:
                    n_lure_nobox += 1
                elif norm(b) == refn:
                    n_lure_boxed_eq += 1
                else:
                    n_lure_boxed_other += 1
    res["lure_character"][name] = dict(wrong=n_wrong, lure=n_lure, lure_share_of_wrong=round(n_lure / n_wrong, 4),
                                       lure_no_box=n_lure_nobox, lure_boxed_equal_reference=n_lure_boxed_eq, lure_boxed_other=n_lure_boxed_other)

# (b) replication pool with lure candidates removed
res["replication_lures_removed"] = {}
for jn, (fb, fr) in {"Qwen2.5-7B": (f"{S4}/repl__Qwen__Qwen2.5-7B-Instruct__noref_a.jsonl", f"{S4}/repl__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl"),
                     "phi-4": ("runs/bon_scores_repl/synthk__microsoft__phi-4__noref_a.jsonl", "runs/bon_scores_repl/synthk__microsoft__phi-4__ref_a.jsonl")}.items():
    b, r = rows(fb), rows(fr)
    Gnm, Gall, acc = [], [], []
    for t in repl:
        pid = t["problem_id"]
        refn = norm(t["ref_answer"])
        lure = [(not o) and bool(refn) and refn in norm(s) for s, o in zip(t["samples"], t["oracle"])]
        match = [bool(o) and norm(boxed(s) or s) == refn for s, o in zip(t["samples"], t["oracle"])]
        keep = [not x for x in lure]
        ix_nm = [i for i in range(len(keep)) if keep[i] and (not t["oracle"][i] or not match[i])]
        lab_nm = [bool(t["oracle"][i]) for i in ix_nm]
        ab, ar = auroc([b[pid][i] for i in ix_nm], lab_nm), auroc([r[pid][i] for i in ix_nm], lab_nm)
        if ab is not None and ar is not None:
            Gnm.append(ar - ab)
        ix = [i for i in range(len(keep)) if keep[i]]
        lab = [bool(t["oracle"][i]) for i in ix]
        ab, ar = auroc([b[pid][i] for i in ix], lab), auroc([r[pid][i] for i in ix], lab)
        if ab is not None and ar is not None:
            Gall.append(ar - ab)
        if 0.2 <= np.mean(t["oracle"]) <= 0.8:
            a1, a0 = sel_acc(r[pid], t["oracle"], keep), sel_acc(b[pid], t["oracle"], keep)
            if a1 is not None and a0 is not None:
                acc.append(a1 - a0)
    res["replication_lures_removed"][jn] = dict(G_nm_change=boot(Gnm), G_all_change=boot(Gall), accuracy_change=boot(acc))

# (c) MACE lures
mtasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/mace_tasks.jsonl")}
mace = []
for t in jl("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    if "oracle" not in t:
        continue
    tt = mtasks[t["problem_id"]]
    params = tt["params"] if isinstance(tt["params"], dict) else ast.literal_eval(tt["params"])
    if params["domain"] in ("River", "Language") and 0.05 <= np.mean(t["oracle"]) <= 0.95:
        t["k"], t["ref_answer"] = int(tt["k"]), tt["ref_answer"]
        mace.append(t)
nw = nl = 0
Gnm = []
b, r = rows(f"{S4}/mace__Qwen__Qwen2.5-7B-Instruct__noref_a.jsonl"), rows(f"{S4}/mace__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl")
for t in mace:
    refn = mnorm(t["ref_answer"])
    lure = [(not o) and len(refn) > 3 and refn in mnorm(s) for s, o in zip(t["samples"], t["oracle"])]
    nw += sum(1 for o in t["oracle"] if not o); nl += sum(lure)
    if t["k"] == 1:
        continue
    pid = t["problem_id"]
    grp = []
    for s, o in zip(t["samples"], t["oracle"]):
        a = mnorm(boxed(s) or s[-200:])
        grp.append("invalid" if not o else ("match" if (a == refn or (len(refn) > 3 and refn in a)) else "nonmatch"))
    ix = [i for i, g in enumerate(grp) if g in ("nonmatch", "invalid") and not lure[i]]
    lab = [grp[i] == "nonmatch" for i in ix]
    ab, ar = auroc([b[pid][i] for i in ix], lab), auroc([r[pid][i] for i in ix], lab)
    if ab is not None and ar is not None:
        Gnm.append(ar - ab)
res["mace_lures"] = dict(wrong=nw, lure=nl, lure_share_of_wrong=round(nl / nw, 4) if nw else None, G_nm_change_lures_removed_qwen=boot(Gnm))

# (d) MATH-500 score rules
mp = [t for t in jl("runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl") if 0.2 <= np.mean(t["oracle"]) <= 0.8]
RULES = {"reference": lambda x, y: y, "mean": lambda x, y: (x + y) / 2, "min": lambda x, y: min(x, y), "max": lambda x, y: max(x, y),
         "blind_then_ref_tiebreak": lambda x, y: x * 1000 + y}
res["math_rules"] = {}
for jn, jt in (("Qwen2.5-7B", "Qwen__Qwen2.5-7B-Instruct"), ("Qwen2.5-14B", "Qwen__Qwen2.5-14B-Instruct")):
    b, r, m1 = rows(f"runs/r2/frozen_math/math__{jt}__noref_a.jsonl"), rows(f"runs/r2/frozen_math/math__{jt}__ref_a.jsonl"), rows(f"runs/r2/scores/math__{jt}__m1_a.jsonl")
    if not (b and r and m1):
        res["math_rules"][jn] = "missing files"
        continue
    items = [t for t in mp if all(t["problem_id"] in x for x in (b, r, m1))]
    base = [sel_acc(b[t["problem_id"]], t["oracle"]) for t in items]
    out = {name: boot(np.subtract([sel_acc([fn(x, y) for x, y in zip(b[t["problem_id"]], r[t["problem_id"]])], t["oracle"]) for t in items], base)) for name, fn in RULES.items()}
    out["blind_then_reveal"] = boot(np.subtract([sel_acc(m1[t["problem_id"]], t["oracle"]) for t in items], base))
    res["math_rules"][jn] = out
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res["lure_character"], indent=0))
print("REPL lures removed", json.dumps(res["replication_lures_removed"]))
print("MACE lures", json.dumps(res["mace_lures"]))
print("MATH rules", json.dumps({j: ({k: (v[0] if v else None) for k, v in d.items()} if isinstance(d, dict) else d) for j, d in res["math_rules"].items()}))
