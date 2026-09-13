# POST HOC analyses for the round-7 revision (external review of the round-6 draft). No registration weight.
# Run from experiments/tfa-vs-judge. Writes papers/analysis/r7_posthoc_results.json.
#  (a) coverage of frontier score files (are wrong answers scored?) and GPT-4.1 tie-averaged best-of-64 accuracy
#  (b) k-pool accuracy change with wrong candidates that contain the reference's answer text removed, and the k step
#  (c) zero-cost score combinations of blind and referenced scores against blind-then-reveal (original scorer)
#  (d) Qwen3-8B with thinking on, k-subsample picks at k=1 and k>1
#  (e) change in false rejections of correct non-matching answers, per judge, arithmetic vs factual, score-only vs thinking
#  (f) examples of lure picks at k>1 (printed, not stored)
import ast
import json
import os
import re

import numpy as np

NBOOT = 1000
OUT = "../../papers/analysis/r7_posthoc_results.json"


def boot(x, seed=0):
    x = np.asarray([v for v in x if v is not None], float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


def rows(f):
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))} if os.path.exists(f) else None


def idxrows(f):
    return {r["problem_id"]: dict(zip(r["idx"], r["score"])) for r in (json.loads(l) for l in open(f))} if os.path.exists(f) else None


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
kp = jl("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")
band = [t for t in kp if 0.2 <= np.mean(t["oracle"]) <= 0.8]
repl = jl("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl")
repl_band = [t for t in repl if 0.2 <= np.mean(t["oracle"]) <= 0.8]

# (a) frontier coverage and GPT-4.1 accuracy
cov = {}
for name, f, pool in (("sonnet_repl", "runs/bon_scores_repl/synthk__anthropic__claude-sonnet-5__noref_a.jsonl", repl),
                      ("sonnet_kpool", "runs/bon_scores_kstrat/synthk__anthropic__claude-sonnet-5__noref_a.jsonl", kp),
                      ("sonnet_mace", "runs/bon_scores_mace/mace__anthropic__claude-sonnet-5__noref_a.jsonl", None),
                      ("gpt41_repl", "runs/bon_scores_repl/synthk__openai__gpt-4.1-2025-04-14__noref_a.jsonl", repl),
                      ("gpt41_kpool", "runs/bon_scores_kstrat/synthk__openai__gpt-4.1-2025-04-14__noref_a.jsonl", kp)):
    sc = rows(f)
    if sc is None:
        cov[name] = "missing"
        continue
    if pool is None:
        vals = [v for l in sc.values() for v in l]
        cov[name] = dict(scored=int(sum(v is not None for v in vals)), total=len(vals))
        continue
    sv = si = tv = ti = 0
    for t in pool:
        if t["problem_id"] not in sc:
            continue
        for v, o in zip(sc[t["problem_id"]], t["oracle"]):
            if o:
                tv += 1; sv += v is not None
            else:
                ti += 1; si += v is not None
    cov[name] = dict(correct_scored=sv, correct_total=tv, wrong_scored=si, wrong_total=ti)
res["frontier_coverage"] = cov
g = {c: rows(f"runs/bon_scores_kstrat/synthk__openai__gpt-4.1-2025-04-14__{c}_a.jsonl") for c in ("noref", "ref")}
if all(g.values()):
    out = {}
    for kname, sel in (("k1", lambda t: t["k"] == 1), ("kgt1", lambda t: t["k"] > 1)):
        d, ties_b, ties_r = [], [], []
        for t in band:
            if not sel(t) or t["problem_id"] not in g["noref"] or t["problem_id"] not in g["ref"]:
                continue
            ab, ar = sel_acc(g["noref"][t["problem_id"]], t["oracle"]), sel_acc(g["ref"][t["problem_id"]], t["oracle"])
            if ab is None or ar is None:
                continue
            d.append(ar - ab)
            for c, lst in (("noref", ties_b), ("ref", ties_r)):
                s = np.array([-np.inf if v is None else v for v in g[c][t["problem_id"]]], float)
                lst.append(int(np.isclose(s, s.max(), rtol=0, atol=1e-9).sum()))
        out[kname] = dict(ref_minus_blind=boot(d), mean_tied_at_max_blind=round(float(np.mean(ties_b)), 1) if ties_b else None,
                          mean_tied_at_max_ref=round(float(np.mean(ties_r)), 1) if ties_r else None)
    res["gpt41_kpool_accuracy"] = out

# (b) lures removed
S4 = "runs/r4/scores"
J = {"Qwen2.5-7B": f"{S4}/kstrat__Qwen__Qwen2.5-7B-Instruct__{{}}_a.jsonl", "Qwen2.5-14B": f"{S4}/kstrat__Qwen__Qwen2.5-14B-Instruct__{{}}_a.jsonl",
     "gemma-2-9b": f"{S4}/kstrat__google__gemma-2-9b-it__{{}}_a.jsonl", "phi-4": "runs/bon_scores_kstrat/synthk__microsoft__phi-4__{}_a.jsonl"}
res["lures_removed"] = {}
lure_examples = []
for j, pat in J.items():
    sc = {c: rows(pat.format(c)) for c in ("noref", "ref")}
    out = {}
    per = {}
    for kname, sel in (("k1", lambda t: t["k"] == 1), ("kgt1", lambda t: t["k"] > 1)):
        full, nolure, share = [], [], []
        for t in band:
            if not sel(t):
                continue
            pid = t["problem_id"]
            refn = norm(t["ref_answer"])
            lure = [(not o) and bool(refn) and refn in norm(s) for s, o in zip(t["samples"], t["oracle"])]
            keep = [not x for x in lure]
            share.append(float(np.mean(lure)))
            full.append(sel_acc(sc["ref"][pid], t["oracle"]) - sel_acc(sc["noref"][pid], t["oracle"]))
            a, b = sel_acc(sc["ref"][pid], t["oracle"], keep), sel_acc(sc["noref"][pid], t["oracle"], keep)
            nolure.append(None if a is None or b is None else a - b)
            if j == "Qwen2.5-7B" and kname == "kgt1" and len(lure_examples) < 8:
                s_ = np.array(sc["ref"][pid], float)
                top = int(np.argmax(s_))
                if lure[top]:
                    lure_examples.append(dict(question=t.get("question", "")[:160], reference=t["ref_answer"],
                                              picked_answer=(boxed(t["samples"][top]) or t["samples"][top][-120:])))
        out[kname] = dict(with_lures=boot(full), lures_removed=boot(nolure), mean_share_lure_candidates=round(float(np.mean(share)), 3))
        per[kname] = [x for x in nolure if x is not None]
    a1, ag = np.array(per["k1"]), np.array(per["kgt1"])
    rng = np.random.default_rng(0)
    bs = [ag[rng.integers(0, len(ag), len(ag))].mean() - a1[rng.integers(0, len(a1), len(a1))].mean() for _ in range(NBOOT)]
    out["step_lures_removed"] = [round(float(ag.mean() - a1.mean()), 4), [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]]
    res["lures_removed"][j] = out

# (c) zero-cost score combinations against blind-then-reveal, original scorer
RULES = {
    "blind": lambda b, r: b, "reference": lambda b, r: r, "mean": lambda b, r: (b + r) / 2, "min": lambda b, r: min(b, r), "max": lambda b, r: max(b, r),
    "blind_then_ref_tiebreak": lambda b, r: b * 1000 + r,
}
res["score_rules"] = {}
KJ = {"Qwen2.5-7B": "Qwen__Qwen2.5-7B-Instruct", "phi-4": "microsoft__phi-4", "Qwen2.5-14B": "Qwen__Qwen2.5-14B-Instruct", "gemma-2-9b": "google__gemma-2-9b-it"}
for jn, jt in KJ.items():
    b, r, m1 = (rows(f"runs/bon_scores_kstrat/synthk__{jt}__noref_a.jsonl"), rows(f"runs/bon_scores_kstrat/synthk__{jt}__ref_a.jsonl"),
                rows(f"runs/bon_scores_kstrat/kstrat__{jt}__m1_a.jsonl"))
    if not (b and r and m1):
        continue
    items = [t for t in band if t["k"] > 1 and all(t["problem_id"] in x for x in (b, r, m1))]
    acc = {name: [] for name in list(RULES) + ["blind_then_reveal"]}
    for t in items:
        pid = t["problem_id"]
        for name, fn in RULES.items():
            acc[name].append(sel_acc([fn(x, y) for x, y in zip(b[pid], r[pid])], t["oracle"]))
        acc["blind_then_reveal"].append(sel_acc(m1[pid], t["oracle"]))
    res["score_rules"].setdefault("kpool_kgt1", {})[jn] = {k: boot(np.subtract(v, acc["blind"])) for k, v in acc.items() if k != "blind"}
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
for jn, jt in (("Qwen2.5-7B", "Qwen__Qwen2.5-7B-Instruct"), ("phi-4", "microsoft__phi-4")):
    b, r, m1 = rows(f"runs/bon_scores_mace/mace__{jt}__noref_a.jsonl"), rows(f"runs/bon_scores_mace/mace__{jt}__ref_a.jsonl"), rows(f"runs/r3/scores/mace__{jt}__m1_a.jsonl")
    if not (b and r and m1):
        continue
    items = [t for t in mace if all(t["problem_id"] in x for x in (b, r, m1))]
    acc = {name: [] for name in list(RULES) + ["blind_then_reveal"]}
    for t in items:
        pid = t["problem_id"]
        for name, fn in RULES.items():
            acc[name].append(sel_acc([fn(x, y) for x, y in zip(b[pid], r[pid])], t["oracle"]))
        acc["blind_then_reveal"].append(sel_acc(m1[pid], t["oracle"]))
    res["score_rules"].setdefault("mace_all", {})[jn] = {k: boot(np.subtract(v, acc["blind"])) for k, v in acc.items() if k != "blind"}

# (d) Qwen3-8B thinking on, k-subsample picks
ksub = jl("runs/r2/ksub.jsonl")
kr, kn = idxrows("runs/r2/scores/ksub__reason__Qwen__Qwen3-8B__ref.jsonl"), idxrows("runs/r2/scores/ksub__reason__Qwen__Qwen3-8B__noref.jsonl")
if kr and kn:
    out = {}
    for kname, sel in (("k1", lambda t: t["k"] == 1), ("kgt1", lambda t: t["k"] > 1)):
        cats = {c: {"correct": [], "lure": [], "other_wrong": []} for c in ("noref", "ref")}
        for t in ksub:
            if not sel(t):
                continue
            pid = t["problem_id"]
            refn = norm(t["ref_orig"])
            for c, scd in (("noref", kn), ("ref", kr)):
                s = [scd.get(pid, {}).get(i) for i in t["idx"]]
                if all(v is None for v in s):
                    continue
                arr = np.array([-np.inf if v is None else v for v in s], float)
                tied = np.flatnonzero(np.isclose(arr, arr.max()))
                lab = []
                for i in tied:
                    if t["oracle"][i]:
                        lab.append("correct")
                    elif refn and refn in norm(t["samples"][i]):
                        lab.append("lure")
                    else:
                        lab.append("other_wrong")
                for k_ in cats[c]:
                    cats[c][k_].append(float(np.mean([x == k_ for x in lab])))
        out[kname] = {c: {k_: boot(v) for k_, v in d.items()} for c, d in cats.items()}
    res["qwen3_8b_thinking_ksub_picks"] = out

# (e) false-rejection change for correct non-matching answers (share scored <= 3, referenced minus blind, points)
fr = {}


def mace_fr(fb, fr_):
    b, r = rows(fb), rows(fr_)
    d = []
    for t in mace:
        if t["k"] == 1 or t["problem_id"] not in b or t["problem_id"] not in r:
            continue
        refn = mnorm(t["ref_answer"])
        nm = [i for i, (s, o) in enumerate(zip(t["samples"], t["oracle"])) if o and not (mnorm(boxed(s) or s[-200:]) == refn or (len(refn) > 3 and refn in mnorm(boxed(s) or s[-200:])))]
        xb = [b[t["problem_id"]][i] <= 3 for i in nm if b[t["problem_id"]][i] is not None]
        xr = [r[t["problem_id"]][i] <= 3 for i in nm if r[t["problem_id"]][i] is not None]
        if xb and xr:
            d.append(np.mean(xr) - np.mean(xb))
    return boot(d)


fr["Qwen2.5-7B|factual|score"] = mace_fr(f"{S4}/mace__Qwen__Qwen2.5-7B-Instruct__noref_a.jsonl", f"{S4}/mace__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl")
fr["phi-4|factual|score"] = mace_fr("runs/bon_scores_mace/mace__microsoft__phi-4__noref_a.jsonl", "runs/bon_scores_mace/mace__microsoft__phi-4__ref_a.jsonl")
rot = jl("runs/r2/rot_sub.jsonl")


def rot_fr(fb, fr_):
    b, r = idxrows(fb), idxrows(fr_)
    if not b or not r:
        return None
    d = []
    for t in rot:
        pid = t["problem_id"]
        nm = [i for i, c in zip(t["idx"], t["cls"]) if c in ("gainer", "placebo")]
        xb = [b.get(pid, {}).get(i) for i in nm]
        xr = [r.get(pid, {}).get(i) for i in nm]
        xb = [v <= 3 for v in xb if v is not None]
        xr = [v <= 3 for v in xr if v is not None]
        if xb and xr:
            d.append(np.mean(xr) - np.mean(xb))
    return boot(d)


fr["Qwen3-8B|arithmetic|thinking off"] = rot_fr("runs/r3/scores/rot__thinkoff__Qwen__Qwen3-8B__noref.jsonl", "runs/r3/scores/rot__thinkoff__Qwen__Qwen3-8B__ref.jsonl")
fr["Qwen3-8B|arithmetic|thinking on"] = rot_fr("runs/r2/scores/rot__reason__Qwen__Qwen3-8B__noref.jsonl", "runs/r2/scores/rot__reason__Qwen__Qwen3-8B__ref.jsonl")
fr["Qwen3-14B|arithmetic|thinking off"] = rot_fr("runs/r4/qwen3_14b/rot__thinkoff__Qwen__Qwen3-14B__noref.jsonl", "runs/r4/qwen3_14b/rot__thinkoff__Qwen__Qwen3-14B__ref.jsonl")
fr["Qwen3-14B|arithmetic|thinking on"] = rot_fr("runs/r4/qwen3_14b/rot__thinkon__Qwen__Qwen3-14B__noref.jsonl", "runs/r4/qwen3_14b/rot__thinkon__Qwen__Qwen3-14B__ref.jsonl")
res["false_reject_change"] = fr
json.dump(res, open(OUT, "w"), indent=1)

print("COVERAGE", json.dumps(res["frontier_coverage"]))
print("GPT41", json.dumps(res.get("gpt41_kpool_accuracy")))
for j, v in res["lures_removed"].items():
    print("LURES", j, {k: (v[k]["with_lures"][0] if v[k]["with_lures"] else None, v[k]["lures_removed"], v[k]["mean_share_lure_candidates"]) for k in ("k1", "kgt1")}, "step", v["step_lures_removed"])
for pool, d in res["score_rules"].items():
    for j, v in d.items():
        print("RULES", pool, j, {k: (x[0] if x else None) for k, x in v.items()})
print("Q3-8B picks", json.dumps({k: {c: {x: y[0] for x, y in d.items()} for c, d in v.items()} for k, v in res.get("qwen3_8b_thinking_ksub_picks", {}).items()}))
print("FR", json.dumps(fr))
print("LURE EXAMPLES")
for e in lure_examples:
    print(" -", e)
