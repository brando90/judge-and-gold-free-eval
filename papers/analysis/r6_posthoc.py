# POST HOC analyses for the round-6 revision (external review of the round-5 draft). No registration weight.
# Run from experiments/tfa-vs-judge. Writes papers/analysis/r6_posthoc_results.json.
#  (a) what best-of-64 picks on the k-pool, by k=1 and k>1: share of the tied picks that are correct, wrong but containing
#      the reference's answer text (a lure), or other wrong answers; blind and referenced, per judge
#  (b) k-pool overall AUROC change (referenced minus blind), by k=1 and k>1, per judge
import json
import os
import re

import numpy as np

NBOOT = 1000
OUT = "../../papers/analysis/r6_posthoc_results.json"
S4 = "runs/r4/scores"


def boot(x, seed=0):
    x = np.asarray([v for v in x if v is not None], float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


def rows(f):
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))} if os.path.exists(f) else None


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or ""


def auroc(sc, lab):
    pos = np.array([s for s, l in zip(sc, lab) if l and s is not None], float)
    neg = np.array([s for s, l in zip(sc, lab) if not l and s is not None], float)
    if len(pos) == 0 or len(neg) == 0:
        return None
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


kp = [json.loads(l) for l in open("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")]
band = [t for t in kp if 0.2 <= np.mean(t["oracle"]) <= 0.8]
J = {"Qwen2.5-7B": f"{S4}/kstrat__Qwen__Qwen2.5-7B-Instruct__{{}}_a.jsonl", "Qwen2.5-14B": f"{S4}/kstrat__Qwen__Qwen2.5-14B-Instruct__{{}}_a.jsonl",
     "gemma-2-9b": f"{S4}/kstrat__google__gemma-2-9b-it__{{}}_a.jsonl", "Mistral-7B": f"{S4}/kstrat__mistralai__Mistral-7B-Instruct-v0.3__{{}}_a.jsonl",
     "phi-4": "runs/bon_scores_kstrat/synthk__microsoft__phi-4__{}_a.jsonl"}
res = {"picks": {}, "kpool_overall_auroc": {}}
for j, pat in J.items():
    sc = {c: rows(pat.format(c)) for c in ("noref", "ref")}
    out = {}
    for kname, sel in (("k1", lambda t: t["k"] == 1), ("kgt1", lambda t: t["k"] > 1)):
        shares = {c: {"correct": [], "lure": [], "other_wrong": []} for c in sc}
        for t in band:
            if not sel(t):
                continue
            pid = t["problem_id"]
            refn = norm(t["ref_answer"])
            for c in sc:
                s = np.array([-np.inf if v is None else v for v in sc[c][pid]], float)
                tied = np.flatnonzero(np.isclose(s, s.max(), rtol=0, atol=1e-9))
                cat = []
                for i in tied:
                    if t["oracle"][i]:
                        cat.append("correct")
                    elif refn and refn in norm(t["samples"][i]):
                        cat.append("lure")
                    else:
                        cat.append("other_wrong")
                for k_ in shares[c]:
                    shares[c][k_].append(float(np.mean([x == k_ for x in cat])))
        out[kname] = {c: {k_: boot(v) for k_, v in d.items()} for c, d in shares.items()}
        out[kname]["n_tasks"] = len(shares["noref"]["correct"])
    res["picks"][j] = out
    au = {}
    for kname, sel in (("k1", lambda t: t["k"] == 1), ("kgt1", lambda t: t["k"] > 1)):
        d = []
        for t in kp:
            if not sel(t):
                continue
            pid = t["problem_id"]
            ab, ar = auroc(sc["noref"][pid], t["oracle"]), auroc(sc["ref"][pid], t["oracle"])
            if ab is not None and ar is not None:
                d.append((ab, ar))
        au[kname] = dict(blind=boot([x[0] for x in d]), ref=boot([x[1] for x in d]), ref_minus_blind=boot([x[1] - x[0] for x in d]))
    res["kpool_overall_auroc"][j] = au
json.dump(res, open(OUT, "w"), indent=1)
for j in J:
    p = res["picks"][j]
    print(j, "k1 picks blind", {k: p["k1"]["noref"][k][0] for k in ("correct", "lure", "other_wrong")}, "ref", {k: p["k1"]["ref"][k][0] for k in ("correct", "lure", "other_wrong")})
    print("   kgt1 picks blind", {k: p["kgt1"]["noref"][k][0] for k in ("correct", "lure", "other_wrong")}, "ref", {k: p["kgt1"]["ref"][k][0] for k in ("correct", "lure", "other_wrong")})
    a = res["kpool_overall_auroc"][j]
    print("   AUROC k1", a["k1"]["blind"][0], a["k1"]["ref"][0], a["k1"]["ref_minus_blind"], "kgt1", a["kgt1"]["blind"][0], a["kgt1"]["ref"][0], a["kgt1"]["ref_minus_blind"])
