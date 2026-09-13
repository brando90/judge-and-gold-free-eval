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
# ---------------------------------------------------------------- blind-accepted rotation filter under the exact estimator (Qwen2.5-7B)
import re


def _norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def _boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


def _rows(f):
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))} if os.path.exists(f) else None


S4 = "runs/r4/scores"
bl, o4, r4s = (_rows(f"{S4}/repl__Qwen__Qwen2.5-7B-Instruct__noref_a.jsonl"), _rows(f"{S4}/repl__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl"),
               _rows(f"{S4}/replrot__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl"))
if bl and o4 and r4s:
    rp = [json.loads(l) for l in open("runs/bon/bon_replrot__meta-llama__Llama-3.1-8B-Instruct.jsonl")]
    G, n_keep, n_all = [], 0, 0
    for it in rp:
        pid = it["problem_id"]
        if pid not in o4 or pid not in r4s or pid not in bl:
            continue
        rotn = _norm(it["ref_answer"])
        g = []
        for i, (smp, ok) in enumerate(zip(it["samples"], it["oracle"])):
            if not ok or _norm(_boxed(smp) or smp) != rotn or o4[pid][i] is None or r4s[pid][i] is None or bl[pid][i] is None:
                continue
            n_all += 1
            if bl[pid][i] >= 7:
                n_keep += 1
                g.append(r4s[pid][i] - o4[pid][i])
        if g:
            G.append(float(np.mean(g)))
    res["blind_accepted_gainers_exact_q7"] = dict(change=boot(G), share_kept=round(n_keep / n_all, 4) if n_all else None)

# ---------------------------------------------------------------- MACE selection accuracy under the exact estimator (Qwen2.5-7B)
m_b = _rows(f"{S4}/mace__Qwen__Qwen2.5-7B-Instruct__noref_a.jsonl")
m_r = _rows(f"{S4}/mace__Qwen__Qwen2.5-7B-Instruct__ref_a.jsonl")
if m_b and m_r:
    def _sel(sc, orc):
        s_ = np.array([-np.inf if v is None else v for v in sc], float)
        return float(np.asarray(orc, float)[np.isclose(s_, s_.max(), rtol=0, atol=1e-9)].mean())

    out = {}
    for gname, sel in (("k1", lambda r: r["k"] == 1), ("kgt1", lambda r: r["k"] > 1), ("all", lambda r: True)):
        ids = [r for r in pool if sel(r) and r["problem_id"] in m_b and r["problem_id"] in m_r]
        ab = [_sel(m_b[r["problem_id"]], r["oracle"]) for r in ids]
        ar = [_sel(m_r[r["problem_id"]], r["oracle"]) for r in ids]
        out[gname] = dict(n=len(ids), acc_blind=boot(ab), acc_ref=boot(ar), ref_minus_blind=boot(np.subtract(ar, ab)))
    res["mace_exact_q7"] = out

# ---------------------------------------------------------------- grading and verification AUROC for other judges (original score files)
# phi-4 writes "10" as one token and its main files carry no fallback scores, so its original files are valid here.


def _auroc(sc, lab):
    pos = np.array([x for x, l in zip(sc, lab) if l and x is not None], float)
    neg = np.array([x for x, l in zip(sc, lab) if not l and x is not None], float)
    if len(pos) == 0 or len(neg) == 0:
        return None
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def _mnorm(a):
    return re.sub(r"[^a-z0-9]+", "", a.strip().casefold())


def _groups(t, rule):
    g = []
    for smp, ok in zip(t["samples"], t["oracle"]):
        if not ok:
            g.append("invalid")
        elif rule == "mace":
            refn, a = _mnorm(t["ref_answer"]), _mnorm(_boxed(smp) or smp[-200:])
            g.append("match" if (a == refn or (len(refn) > 3 and refn in a)) else "nonmatch")
        else:
            g.append("match" if _norm(_boxed(smp) or smp) == _norm(t["ref_answer"]) else "nonmatch")
    return g


def _grading(tasks_, b, r, rule):
    d = {"nm": ([], [], []), "all": ([], [], [])}
    for t in tasks_:
        pid = t["problem_id"]
        if pid not in b or pid not in r:
            continue
        g = _groups(t, rule)
        for key, keep, pos in (("nm", {"nonmatch", "invalid"}, {"nonmatch"}), ("all", {"match", "nonmatch", "invalid"}, {"match", "nonmatch"})):
            ix = [i for i, x in enumerate(g) if x in keep]
            lab = [g[i] in pos for i in ix]
            ab, ar = _auroc([b[pid][i] for i in ix], lab), _auroc([r[pid][i] for i in ix], lab)
            if ab is not None and ar is not None:
                d[key][0].append(ab); d[key][1].append(ar); d[key][2].append(ar - ab)
    return {f"G_{k}": dict(blind=boot(v[0]), ref=boot(v[1]), ref_minus_blind=boot(v[2])) for k, v in d.items()}


mace_tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/mace_tasks.jsonl")}
for t in pool:
    t["ref_answer"] = mace_tasks[t["problem_id"]]["ref_answer"]
repl_pool = [json.loads(l) for l in open("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl")]
kp_pool = [json.loads(l) for l in open("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")]
res["grading_other_judges"] = {}
for jt, files in (("microsoft__phi-4", dict(repl=("runs/bon_scores_repl/synthk__microsoft__phi-4__noref_a.jsonl", "runs/bon_scores_repl/synthk__microsoft__phi-4__ref_a.jsonl"),
                                               mace=("runs/bon_scores_mace/mace__microsoft__phi-4__noref_a.jsonl", "runs/bon_scores_mace/mace__microsoft__phi-4__ref_a.jsonl"),
                                               kpool=("runs/bon_scores_kstrat/synthk__microsoft__phi-4__noref_a.jsonl", None))),
                  ):  # Sonnet 5 files score correct samples only, so no AUROC against wrong answers can be computed
    out = {}
    for name, (fb, fr) in files.items():
        tasks_ = {"repl": repl_pool, "mace": pool, "kpool": kp_pool}[name]
        b = _rows(fb)
        if b is None:
            continue
        vals = [_auroc(b[t["problem_id"]], t["oracle"]) for t in tasks_ if t["problem_id"] in b]
        out[f"verification_{name}"] = boot([v for v in vals if v is not None])
        if fr:
            r = _rows(fr)
            if r is not None:
                out[f"grading_{name}"] = _grading(tasks_, b, r, "mace" if name == "mace" else "repl")
    res["grading_other_judges"][jt] = out

json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
