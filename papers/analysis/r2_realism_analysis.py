# FROZEN producer for R2-B (papers/D-iclr/registration_round2.md), committed before any R2-B score exists.
# Run from experiments/tfa-vs-judge. Writes papers/analysis/r2_realism_results.json.
# Per protocol (reason = Qwen3-8B thinking; mtbench = Qwen2.5-7B with MT-Bench templates):
#   P-R2B1 gainer change (refrot - ref) > 0, CI excl. 0     P-R2B2 loser change < 0, CI excl. 0
#   P-R2B3 k>1 referenced margin minus blind margin > 0, CI excl. 0 (paired per task)
#   P-R2B4 accuracy step = mean_{k>1}(acc_ref - acc_noref) - mean_{k=1}(same) < 0 (point estimate)
import json
import os
import re

import numpy as np

NBOOT = 1000
OUT = "../../papers/analysis/r2_realism_results.json"
PROTOCOLS = {"reason": "Qwen__Qwen3-8B", "mtbench": "Qwen__Qwen2.5-7B-Instruct"}


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


def load(pool, proto, cond):
    f = f"runs/r2/scores/{pool}__{proto}__{PROTOCOLS[proto]}__{cond}.jsonl"
    if not os.path.exists(f):
        return None
    out = {}
    for r in (json.loads(l) for l in open(f)):
        out[r["problem_id"]] = dict(zip(r["idx"], r["score"]))
    return out


def boot(x, seed=0):
    x = np.asarray(x, float)
    if len(x) == 0:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 3), [round(float(np.percentile(m, 2.5)), 3), round(float(np.percentile(m, 97.5)), 3)], len(x)]


def sel_acc(scores, oracle):
    pairs = [(s, o) for s, o in zip(scores, oracle) if s is not None]
    if not pairs:
        return None
    s = np.array([p[0] for p in pairs]); o = np.array([p[1] for p in pairs], float)
    return float(o[np.isclose(s, s.max())].mean())


rot = [json.loads(l) for l in open("runs/r2/rot_sub.jsonl")]
ksub = [json.loads(l) for l in open("runs/r2/ksub.jsonl")]
res = {}
for proto in PROTOCOLS:
    R = {}
    ref, rr, nr = load("rot", proto, "ref"), load("rot", proto, "refrot"), load("rot", proto, "noref")
    if ref is not None and rr is not None:
        per = {"gainer": [], "loser": [], "placebo": []}
        gmp = []
        nulls = tot = 0
        for t in rot:
            pid = t["problem_id"]
            ch = {"gainer": [], "loser": [], "placebo": []}
            for idx, c in zip(t["idx"], t["cls"]):
                a, b = ref.get(pid, {}).get(idx), rr.get(pid, {}).get(idx)
                tot += 1
                if a is None or b is None:
                    nulls += 1
                    continue
                ch[c].append(b - a)
            for c in ch:
                if ch[c]:
                    per[c].append(np.mean(ch[c]))
            if ch["gainer"] and ch["placebo"]:
                gmp.append(np.mean(ch["gainer"]) - np.mean(ch["placebo"]))
        R["rot"] = {c: boot(v) for c, v in per.items()}
        R["rot"]["gainer_minus_placebo"] = boot(gmp)
        R["rot"]["pairs_dropped_unparseable"] = [nulls, tot]
        R["P_R2B1"] = bool(R["rot"]["gainer"] and R["rot"]["gainer"][1][0] > 0)
        R["P_R2B2"] = bool(R["rot"]["loser"] and R["rot"]["loser"][1][1] < 0)
    kr, kn = load("ksub", proto, "ref"), load("ksub", proto, "noref")
    if kr is not None and kn is not None:
        mdiff, mref, mnoref, acc1, accg = [], [], [], [], []
        for t in ksub:
            pid = t["problem_id"]
            sr = [kr.get(pid, {}).get(i) for i in t["idx"]]
            sn = [kn.get(pid, {}).get(i) for i in t["idx"]]
            ar, an = sel_acc(sr, t["oracle"]), sel_acc(sn, t["oracle"])
            if ar is not None and an is not None:
                (acc1 if t["k"] == 1 else accg).append(ar - an)
            if t["k"] == 1:
                continue
            refn = norm(t["ref_orig"])
            def margin(sc):
                m = [s for s, o, x in zip(sc, t["oracle"], t["samples"]) if o and s is not None and norm(extract_boxed(x) or x) == refn]
                n = [s for s, o, x in zip(sc, t["oracle"], t["samples"]) if o and s is not None and norm(extract_boxed(x) or x) != refn]
                return (np.mean(m) - np.mean(n)) if m and n else None
            a, b = margin(sr), margin(sn)
            if a is not None:
                mref.append(a)
            if b is not None:
                mnoref.append(b)
            if a is not None and b is not None:
                mdiff.append(a - b)
        step = float(np.mean(accg) - np.mean(acc1)) if acc1 and accg else None
        rng = np.random.default_rng(0)
        bs = []
        if step is not None:
            g, o = np.array(accg), np.array(acc1)
            for _ in range(NBOOT):
                bs.append(g[rng.integers(0, len(g), len(g))].mean() - o[rng.integers(0, len(o), len(o))].mean())
        R["ksub"] = dict(margin_ref_kgt1=boot(mref), margin_noref_kgt1=boot(mnoref), margin_diff_kgt1=boot(mdiff),
                         acc_delta_k1=boot(acc1), acc_delta_kgt1=boot(accg),
                         acc_step=[round(step, 3), [round(float(np.percentile(bs, 2.5)), 3), round(float(np.percentile(bs, 97.5)), 3)]] if step is not None else None)
        R["P_R2B3"] = bool(R["ksub"]["margin_diff_kgt1"] and R["ksub"]["margin_diff_kgt1"][1][0] > 0)
        R["P_R2B4"] = bool(step is not None and step < 0)
    res[proto] = R if R else "pre-data"
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
