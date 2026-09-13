# FROZEN producer for R4-A, R4-B, R4-D (papers/D-iclr/registration_round4.md), committed before any R4 score exists.
# Run from experiments/tfa-vs-judge. Writes papers/analysis/r4_results.json.
import ast
import json
import os
import re

import numpy as np

NBOOT = 1000
OUT = "../../papers/analysis/r4_results.json"
S = "runs/r4/scores"
Q7 = "Qwen__Qwen2.5-7B-Instruct"
Q14 = "Qwen__Qwen2.5-14B-Instruct"
KJ = [Q7, Q14, "google__gemma-2-9b-it", "mistralai__Mistral-7B-Instruct-v0.3"]


def boot(x, seed=0):
    x = np.asarray([v for v in x if v is not None], float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


def rows(name, judge, cond):
    f = f"{S}/{name}__{judge}__{cond}_a.jsonl"
    if not os.path.exists(f):
        return None
    return {r["problem_id"]: r for r in (json.loads(l) for l in open(f))}


def col(rw, key="escore"):
    return None if rw is None else {p: r[key] for p, r in rw.items()}


def norm(a):  # replication / k-pool matching (replrot_analysis.py)
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def mnorm(a):  # MACE matching (mace_analysis.py, r3_build_subsamples.py)
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


def sel_acc(scores, oracle):
    s = np.array([-np.inf if v is None else v for v in scores], float)
    return float(np.asarray(oracle, float)[np.isclose(s, s.max(), rtol=0, atol=1e-9)].mean())


def auroc(sc, lab):
    pos = np.array([s for s, l in zip(sc, lab) if l and s is not None], float)
    neg = np.array([s for s, l in zip(sc, lab) if not l and s is not None], float)
    if len(pos) == 0 or len(neg) == 0:
        return None
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def inband(pool, lo=0.2, hi=0.8):
    return [r for r in pool if lo <= np.mean(r["oracle"]) <= hi]


def jl(f):
    return [json.loads(l) for l in open(f)]


res = {"files": {}}
if os.path.isdir(S):
    for fn in sorted(os.listdir(S)):
        if not fn.endswith(".jsonl"):
            continue
        fl, dif = [0, 0, 0], []
        for r in jl(f"{S}/{fn}"):
            for e, g, x in zip(r["escore"], r["escore_legacy"], r["flag"]):
                fl[x] += 1
                if x == 0:
                    dif.append(abs(e - g))
        res["files"][fn] = dict(flag_counts=fl, mean_abs_exact_minus_legacy=round(float(np.mean(dif)), 4) if dif else None)

# ---------------------------------------------------------------- R4-A: rotation (Qwen2.5-7B)
rp = jl("runs/bon/bon_replrot__meta-llama__Llama-3.1-8B-Instruct.jsonl")
orig, rot = rows("repl", Q7, "ref"), rows("replrot", Q7, "ref")
if orig is not None and rot is not None:
    res["rotation"] = {}
    for key in ("escore", "escore_legacy", "greedy"):
        G, L, P = [], [], []
        for it in rp:
            pid = it["problem_id"]
            if pid not in orig or pid not in rot:
                continue
            rotn, orign = norm(it["ref_answer"]), norm(it["rot_from"])
            g, lo, pl = [], [], []
            for i, (s, ok) in enumerate(zip(it["samples"], it["oracle"])):
                a, b = orig[pid][key][i], rot[pid][key][i]
                if not ok or a is None or b is None:
                    continue
                x = norm(boxed(s) or s)
                (g if x == rotn else lo if x == orign else pl).append(b - a)
            for acc, lst in ((G, g), (L, lo), (P, pl)):
                if lst:
                    acc.append(float(np.mean(lst)))
        res["rotation"][key] = dict(gainer=boot(G), loser=boot(L), placebo=boot(P))

# ---------------------------------------------------------------- R4-A: replication false rejection (Qwen2.5-7B)
repl = jl("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl")
b, r = col(rows("repl", Q7, "noref")), col(rows("repl", Q7, "ref"))
if b is not None and r is not None:
    out = {}
    for thr, tag in ((3, "le3"), (5, "posthoc_le5")):
        fb, fr = [], []
        for t in repl:
            pid = t["problem_id"]
            refn = norm(t["ref_answer"])
            m = [norm(boxed(s) or s) == refn for s in t["samples"]]
            nm = [i for i, (o, c) in enumerate(zip(t["oracle"], m)) if o and not c]
            mm = [i for i, (o, c) in enumerate(zip(t["oracle"], m)) if o and c]
            if not nm or not mm or pid not in b or pid not in r:
                continue
            xb = [b[pid][i] <= thr for i in nm if b[pid][i] is not None]
            xr = [r[pid][i] <= thr for i in nm if r[pid][i] is not None]
            if xb and xr:
                fb.append(np.mean(xb)); fr.append(np.mean(xr))
        out[tag] = dict(blind=boot(fb), ref=boot(fr), diff=boot(np.subtract(fr, fb)))
    res["repl_false_reject"] = out
    items = inband(repl)
    ab = [sel_acc(b[t["problem_id"]], t["oracle"]) for t in items if t["problem_id"] in b and t["problem_id"] in r]
    ar = [sel_acc(r[t["problem_id"]], t["oracle"]) for t in items if t["problem_id"] in b and t["problem_id"] in r]
    res["repl_accuracy"] = dict(acc_blind=boot(ab), acc_ref=boot(ar), ref_minus_blind=boot(np.subtract(ar, ab)))

# ---------------------------------------------------------------- R4-A: k-pool accuracy
kp = jl("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")
res["kpool"] = {}
for j in KJ:
    rn, rr = rows("kstrat", j, "noref"), rows("kstrat", j, "ref")
    if rn is None or rr is None:
        continue
    out = {}
    for key in ("escore", "escore_legacy"):
        n0, r0 = col(rn, key), col(rr, key)
        o = {}
        for kname, sel in (("k1", lambda t: t["k"] == 1), ("k2", lambda t: t["k"] == 2), ("k4", lambda t: t["k"] == 4),
                           ("k8", lambda t: t["k"] == 8), ("k16", lambda t: t["k"] == 16), ("kgt1", lambda t: t["k"] > 1)):
            items = [t for t in inband(kp) if sel(t) and t["problem_id"] in n0 and t["problem_id"] in r0]
            an = [sel_acc(n0[t["problem_id"]], t["oracle"]) for t in items]
            ar = [sel_acc(r0[t["problem_id"]], t["oracle"]) for t in items]
            o[kname] = dict(acc_blind=boot(an), acc_ref=boot(ar), ref_minus_blind=boot(np.subtract(ar, an)))
        out[key] = o
    res["kpool"][j] = out

# ---------------------------------------------------------------- R4-B: MATH-500
mp = inband(jl("runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl"))
res["math"] = {}
for j in (Q7, Q14):
    sc = {c: col(rows("math", j, c)) for c in ("noref", "ref", "refans")}
    if any(v is None for v in sc.values()):
        continue
    items = [t for t in mp if all(t["problem_id"] in v for v in sc.values())]
    acc = {c: [sel_acc(sc[c][t["problem_id"]], t["oracle"]) for t in items] for c in sc}
    res["math"][j] = dict(n=len(items), **{f"acc_{c}": boot(v) for c, v in acc.items()},
                          refans_minus_noref=boot(np.subtract(acc["refans"], acc["noref"])),
                          ref_minus_noref=boot(np.subtract(acc["ref"], acc["noref"])),
                          refans_minus_ref=boot(np.subtract(acc["refans"], acc["ref"])))

# ---------------------------------------------------------------- R4-D: verification and grading (Qwen2.5-7B)
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/mace_tasks.jsonl")}
mace = []
for t in jl("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    if "oracle" not in t:
        continue
    tt = tasks[t["problem_id"]]
    params = tt["params"] if isinstance(tt["params"], dict) else ast.literal_eval(tt["params"])
    if params["domain"] in ("River", "Language") and 0.05 <= np.mean(t["oracle"]) <= 0.95:
        t["k"], t["ref_answer"] = int(tt["k"]), tt["ref_answer"]
        mace.append(t)


def verification(pool, sc):
    return boot([auroc(sc[t["problem_id"]], t["oracle"]) for t in pool if t["problem_id"] in sc])


def groups(t, rule):
    out = []
    for s, o in zip(t["samples"], t["oracle"]):
        if not o:
            out.append("invalid")
        elif rule == "mace":
            refn, a = mnorm(t["ref_answer"]), mnorm(boxed(s) or s[-200:])
            out.append("match" if (a == refn or (len(refn) > 3 and refn in a)) else "nonmatch")
        else:
            out.append("match" if norm(boxed(s) or s) == norm(t["ref_answer"]) else "nonmatch")
    return out


def grading(pool, b, r, rule):
    d = {"nm": ([], [], []), "m": ([], [], []), "all": ([], [], [])}
    for t in pool:
        pid = t["problem_id"]
        if pid not in b or pid not in r:
            continue
        g = groups(t, rule)
        for key, keep, pos in (("nm", {"nonmatch", "invalid"}, {"nonmatch"}), ("m", {"match", "invalid"}, {"match"}),
                               ("all", {"match", "nonmatch", "invalid"}, {"match", "nonmatch"})):
            ix = [i for i, x in enumerate(g) if x in keep]
            lab = [g[i] in pos for i in ix]
            ab, ar = auroc([b[pid][i] for i in ix], lab), auroc([r[pid][i] for i in ix], lab)
            if ab is not None and ar is not None:
                d[key][0].append(ab); d[key][1].append(ar); d[key][2].append(ar - ab)
    return {f"G_{k}": dict(blind=boot(v[0]), ref=boot(v[1]), ref_minus_blind=boot(v[2])) for k, v in d.items()}


V = {}
for name, pool in (("repl", repl), ("kpool", kp), ("mace", mace)):
    sc = col(rows(name if name != "kpool" else "kstrat", Q7, "noref"))
    if sc is not None:
        V[name] = verification(pool, sc)
scm = col(rows("math", Q7, "noref"))
if scm is not None:
    V["math"] = verification(mp, scm)
res["verification_auroc"] = V
res["grading"] = {}
for name, pool, rule in (("mace", mace, "mace"), ("repl", repl, "repl")):
    b, r = col(rows(name, Q7, "noref")), col(rows(name, Q7, "ref"))
    if b is not None and r is not None:
        res["grading"][name] = grading(pool, b, r, rule)


# ---------------------------------------------------------------- predictions
def get(*path):
    d = res
    for k in path:
        if not isinstance(d, dict) or k not in d or d[k] is None:
            return None
        d = d[k]
    return d


def hi_lt0(v):
    return None if v is None else bool(v[1][1] < 0)


def lo_gt0(v):
    return None if v is None else bool(v[1][0] > 0)


res["P_R4A1"] = hi_lt0(get("rotation", "escore", "loser"))
res["P_R4A2"] = lo_gt0(get("rotation", "escore", "gainer"))
cells = {j: hi_lt0(get("kpool", j, "escore", "kgt1", "ref_minus_blind")) for j in KJ}
res["P_R4A3_cells"] = cells
res["P_R4A3"] = None if any(v is None for v in cells.values()) else all(cells.values())
res["P_R4A4"] = lo_gt0(get("repl_false_reject", "le3", "diff"))
b1 = {j: lo_gt0(get("math", j, "refans_minus_noref")) for j in (Q7, Q14)}
b2 = {j: lo_gt0(get("math", j, "ref_minus_noref")) for j in (Q7, Q14)}
res["P_R4B1_cells"], res["P_R4B2_cells"] = b1, b2
res["P_R4B1"] = None if any(v is None for v in b1.values()) else all(b1.values())
res["P_R4B2"] = None if any(v is None for v in b2.values()) else all(b2.values())
vm, vk, vr = get("verification_auroc", "mace"), get("verification_auroc", "kpool"), get("verification_auroc", "repl")
res["P_R4D1"] = None if None in (vm, vk, vr) else bool(vm[0] < vk[0] and vm[0] < vr[0])
res["P_R4D2"] = hi_lt0(get("grading", "mace", "G_nm", "ref_minus_blind"))
res["P_R4D3"] = lo_gt0(get("grading", "mace", "G_all", "ref_minus_blind"))
res["P_R4D4"] = hi_lt0(get("grading", "repl", "G_nm", "ref_minus_blind"))
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k.startswith("P_")}, indent=1))
