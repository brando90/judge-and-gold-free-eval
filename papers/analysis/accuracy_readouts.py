# POST HOC readouts in plain units for the ICLR revision (no registration weight).
# Run from experiments/tfa-vs-judge. Writes papers/analysis/accuracy_readouts.json.
#   - selected-answer accuracy under best-of-64 (rubric-a selection, validity averaged over max ties)
#     for blind / reference / blind-then-reveal (m1) / validity gate (m2), per pool and per k;
#   - false-rejection rate: share of oracle-valid samples scored <= 3 by the judge (rubric a),
#     split by whether the sample's answer matches the shown reference.
# Populations match the paper's registered analyses: tasks with pool pass rate in [0.2, 0.8].
import json
import os
import re

import numpy as np

NBOOT = 1000
OUT = "../../papers/analysis/accuracy_readouts.json"


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def extract_boxed(text):
    i = text.rfind("\\boxed{")
    if i < 0:
        return None
    j, depth = i + 7, 1
    while j < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    return text[i + 7:j - 1]


def load(f):
    if not os.path.exists(f):
        return None
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))}


def sel_acc(scores, oracle):
    s = np.asarray(scores, float)
    return float(np.asarray(oracle, float)[np.isclose(s, s.max(), rtol=0, atol=1e-9)].mean())


def boot(x, seed=0):
    x = np.asarray(x, float)
    if len(x) == 0:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


def inband(pool):
    return [r for r in pool if 0.2 <= np.mean(r["oracle"]) <= 0.8]


res = {}

# ---------------------------------------------------------------- replication pool
repl = [json.loads(l) for l in open("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl")]
res["repl"] = {}
for j in ("Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"):
    b = load(f"runs/bon_scores_repl/synthk__{j}__noref_a.jsonl")
    r = load(f"runs/bon_scores_repl/synthk__{j}__ref_a.jsonl")
    items = inband(repl)
    ab = [sel_acc(b[t["problem_id"]], t["oracle"]) for t in items]
    ar = [sel_acc(r[t["problem_id"]], t["oracle"]) for t in items]
    fr = {"blind_nonmatch": [], "ref_nonmatch": [], "blind_match": [], "ref_match": []}
    for t in repl:
        refn = norm(t["ref_answer"])
        cls = [norm(extract_boxed(s) or s) == refn for s in t["samples"]]
        valid_nm = [i for i, (o, c) in enumerate(zip(t["oracle"], cls)) if o and not c]
        valid_m = [i for i, (o, c) in enumerate(zip(t["oracle"], cls)) if o and c]
        if not valid_nm or not valid_m:
            continue
        pid = t["problem_id"]
        fr["blind_nonmatch"].append(np.mean([b[pid][i] <= 3 for i in valid_nm]))
        fr["ref_nonmatch"].append(np.mean([r[pid][i] <= 3 for i in valid_nm]))
        fr["blind_match"].append(np.mean([b[pid][i] <= 3 for i in valid_m]))
        fr["ref_match"].append(np.mean([r[pid][i] <= 3 for i in valid_m]))
    res["repl"][j] = dict(acc_blind=boot(ab), acc_ref=boot(ar), acc_ref_minus_blind=boot(np.subtract(ar, ab)),
                          false_reject={k: boot(v) for k, v in fr.items()},
                          false_reject_diff_nonmatch=boot(np.subtract(fr["ref_nonmatch"], fr["blind_nonmatch"])))

# ---------------------------------------------------------------- k-pool
kp = [json.loads(l) for l in open("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")]
res["kpool"] = {}
for j in ("Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4", "Qwen__Qwen2.5-14B-Instruct", "google__gemma-2-9b-it",
          "mistralai__Mistral-7B-Instruct-v0.3"):
    sc = {c: load(f"runs/bon_scores_kstrat/synthk__{j}__{c}_a.jsonl") for c in ("noref", "ref")}
    sc.update({c: load(f"runs/bon_scores_kstrat/kstrat__{j}__{c}_a.jsonl") for c in ("m1", "m2")})
    if sc["noref"] is None or sc["ref"] is None:
        continue
    out = {}
    for kname, sel in (("k1", lambda t: t["k"] == 1), ("k2", lambda t: t["k"] == 2), ("k4", lambda t: t["k"] == 4),
                       ("k8", lambda t: t["k"] == 8), ("k16", lambda t: t["k"] == 16), ("kgt1", lambda t: t["k"] > 1)):
        items = [t for t in inband(kp) if sel(t) and all(sc[c] is None or t["problem_id"] in sc[c] for c in sc)]
        acc = {c: [sel_acc(sc[c][t["problem_id"]], t["oracle"]) for t in items] for c in sc if sc[c] is not None}
        out[kname] = {f"acc_{c}": boot(v) for c, v in acc.items()}
        for c in acc:
            if c != "noref":
                out[kname][f"{c}_minus_blind"] = boot(np.subtract(acc[c], acc["noref"]))
    res["kpool"][j] = out

# ---------------------------------------------------------------- MATH-500 (unique answers)
mp = inband([json.loads(l) for l in open("runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl")])
res["math"] = {}
for size in ("1.5B", "3B", "7B", "14B"):
    j = f"Qwen__Qwen2.5-{size}-Instruct"
    b = load(f"runs/r2/frozen_math/math__{j}__noref_a.jsonl")  # cluster copies; local bon_scores/math copies are misaligned
    r = load(f"runs/r2/frozen_math/math__{j}__ref_a.jsonl")
    if b is None or r is None:
        continue
    items = [t for t in mp if t["problem_id"] in b and t["problem_id"] in r]
    ab = [sel_acc(b[t["problem_id"]], t["oracle"]) for t in items]
    ar = [sel_acc(r[t["problem_id"]], t["oracle"]) for t in items]
    res["math"][j] = dict(acc_blind=boot(ab), acc_ref=boot(ar), acc_ref_minus_blind=boot(np.subtract(ar, ab)))

# ---------------------------------------------------------------- blind-then-reveal variants, k-pool k>1
res["kpool_variants"] = {}
for j in ("Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4", "google__gemma-2-9b-it"):
    sc = {c: load(f"runs/bon_scores_kstrat/synthk__{j}__{c}_a.jsonl") for c in ("noref", "ref")}
    sc.update({c: load(f"runs/bon_scores_kstrat/kstrat__{j}__{c}_a.jsonl") for c in ("m1", "m1noscore", "m1prev", "m1indep")})
    sc = {c: v for c, v in sc.items() if v is not None}
    items = [t for t in inband(kp) if t["k"] > 1 and all(t["problem_id"] in v for v in sc.values())]
    acc = {c: [sel_acc(v[t["problem_id"]], t["oracle"]) for t in items] for c, v in sc.items()}
    res["kpool_variants"][j] = {f"{c}_minus_blind": boot(np.subtract(acc[c], acc["noref"])) for c in acc if c != "noref"}

# ---------------------------------------------------------------- frontier CLI judge (k-pool, 37 tasks)
cli = [json.loads(l) for l in open("runs/frontier_judge/frontier_sonnet.jsonl")]
res["frontier_cli"] = {}
for g in ("match", "nomatch"):
    for c in ("noref", "ref"):
        per = {}
        for r in cli:
            if r["group"] == g and r["cond"] == c and r["score"] is not None:
                per.setdefault(r["problem_id"], []).append(r["score"] <= 3)
        res["frontier_cli"][f"fail_{g}_{c}"] = boot([np.mean(v) for v in per.values()])
        res["frontier_cli"][f"n_samples_{g}_{c}"] = int(sum(len(v) for v in per.values()))

# ---------------------------------------------------------------- Sonnet 5 false rejection, replication pool
b = load("runs/bon_scores_repl/synthk__anthropic__claude-sonnet-5__noref_a.jsonl")
r = load("runs/bon_scores_repl/synthk__anthropic__claude-sonnet-5__ref_a.jsonl")
fr = {"blind_nonmatch": [], "ref_nonmatch": []}
for t in repl:
    pid = t["problem_id"]
    if pid not in b or pid not in r:
        continue
    refn = norm(t["ref_answer"])
    idx = [i for i, s in enumerate(t["samples"]) if t["oracle"][i] and norm(extract_boxed(s) or s) != refn
           and b[pid][i] is not None and r[pid][i] is not None]
    if idx:
        fr["blind_nonmatch"].append(np.mean([b[pid][i] <= 3 for i in idx]))
        fr["ref_nonmatch"].append(np.mean([r[pid][i] <= 3 for i in idx]))
res["repl_sonnet5_false_reject"] = {k: boot(v) for k, v in fr.items()}

# ---------------------------------------------------------------- Sonnet 5 API: mean scores of valid answers, replication pool
res["repl_sonnet5_scores"] = {}
for cond in ("noref", "ref"):
    sc = load(f"runs/bon_scores_repl/synthk__anthropic__claude-sonnet-5__{cond}_a.jsonl")
    m_all, n_all, per_m, per_n = [], [], [], []
    for t in repl:
        pid = t["problem_id"]
        if pid not in sc:
            continue
        refn = norm(t["ref_answer"])
        m = [sc[pid][i] for i, s in enumerate(t["samples"]) if t["oracle"][i] and sc[pid][i] is not None and norm(extract_boxed(s) or s) == refn]
        n = [sc[pid][i] for i, s in enumerate(t["samples"]) if t["oracle"][i] and sc[pid][i] is not None and norm(extract_boxed(s) or s) != refn]
        if m and n:
            per_m.append(np.mean(m)); per_n.append(np.mean(n))
    res["repl_sonnet5_scores"][cond] = dict(match=boot(per_m), nonmatch=boot(per_n), margin=boot(np.subtract(per_m, per_n)))

json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1)[:6000])
