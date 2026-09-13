# FROZEN producer for R3-A and R3-C (papers/D-iclr/registration_round3.md), committed before any R3 score exists.
# Run from experiments/tfa-vs-judge. Writes papers/analysis/r3_toggle_results.json.
import json
import os
import re

import numpy as np

NBOOT = 1000
OUT = "../../papers/analysis/r3_toggle_results.json"
J = "Qwen__Qwen3-8B"


def boot(x, seed=0):
    x = np.asarray(x, float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 3), [round(float(np.percentile(m, 2.5)), 3), round(float(np.percentile(m, 97.5)), 3)], len(x)]


def load(path):
    if not os.path.exists(path):
        return None
    return {r["problem_id"]: dict(zip(r["idx"], r["score"])) for r in (json.loads(l) for l in open(path))}


def arm_file(pool, arm, cond):
    if arm == "on" and pool in ("rot", "ksub"):
        return f"runs/r2/scores/{pool}__reason__{J}__{cond}.jsonl"  # identical protocol, thinking on
    return f"runs/r3/scores/{pool}__think{arm}__{J}__{cond}.jsonl"


def norm_boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


def normA(a):  # replication / k-pool matching (replrot_analysis.py)
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def sel_acc(scores, oracle):
    pairs = [(s, o) for s, o in zip(scores, oracle) if s is not None]
    if not pairs:
        return None
    s = np.array([p[0] for p in pairs]); o = np.array([p[1] for p in pairs], float)
    return float(o[np.isclose(s, s.max())].mean())


res = {}
rot = [json.loads(l) for l in open("runs/r2/rot_sub.jsonl")]
ksub = [json.loads(l) for l in open("runs/r2/ksub.jsonl")]
loser_by_arm = {}
for arm in ("on", "off"):
    R = {}
    ref, rr = load(arm_file("rot", arm, "ref")), load(arm_file("rot", arm, "refrot"))
    if ref is not None and rr is not None:
        per = {"gainer": {}, "loser": {}, "placebo": {}}
        for t in rot:
            pid = t["problem_id"]
            ch = {"gainer": [], "loser": [], "placebo": []}
            for idx, c in zip(t["idx"], t["cls"]):
                a, b = ref.get(pid, {}).get(idx), rr.get(pid, {}).get(idx)
                if a is not None and b is not None:
                    ch[c].append(b - a)
            for c in ch:
                if ch[c]:
                    per[c][pid] = float(np.mean(ch[c]))
        R["rot"] = {c: boot(list(v.values())) for c, v in per.items()}
        loser_by_arm[arm] = per["loser"]
    kr, kn = load(arm_file("ksub", arm, "ref")), load(arm_file("ksub", arm, "noref"))
    if kr is not None and kn is not None:
        mdiff, acc1, accg = [], [], []
        for t in ksub:
            pid = t["problem_id"]
            sr = [kr.get(pid, {}).get(i) for i in t["idx"]]
            sn = [kn.get(pid, {}).get(i) for i in t["idx"]]
            ar, an = sel_acc(sr, t["oracle"]), sel_acc(sn, t["oracle"])
            if ar is not None and an is not None:
                (acc1 if t["k"] == 1 else accg).append(ar - an)
            if t["k"] == 1:
                continue
            refn = normA(t["ref_orig"])
            def margin(sc):
                m = [s for s, o, x in zip(sc, t["oracle"], t["samples"]) if o and s is not None and normA(norm_boxed(x) or x) == refn]
                n = [s for s, o, x in zip(sc, t["oracle"], t["samples"]) if o and s is not None and normA(norm_boxed(x) or x) != refn]
                return (np.mean(m) - np.mean(n)) if m and n else None
            a, b = margin(sr), margin(sn)
            if a is not None and b is not None:
                mdiff.append(a - b)
        R["ksub"] = dict(margin_diff_kgt1=boot(mdiff), acc_delta_k1=boot(acc1), acc_delta_kgt1=boot(accg))
    mr, mn = load(arm_file("macesub", arm, "ref")), load(arm_file("macesub", arm, "noref"))
    if mr is not None and mn is not None:
        mace = [json.loads(l) for l in open("runs/r3/macesub.jsonl")]
        mdiff, frdiff = [], []
        for t in mace:
            pid = t["problem_id"]
            def by_group(sc, g):
                return [sc.get(pid, {}).get(i) for i, gg in zip(t["idx"], t["group"]) if gg == g and sc.get(pid, {}).get(i) is not None]
            rm, rn, bm, bn = by_group(mr, "match"), by_group(mr, "nonmatch"), by_group(mn, "match"), by_group(mn, "nonmatch")
            if rm and rn and bm and bn:
                mdiff.append((np.mean(rm) - np.mean(rn)) - (np.mean(bm) - np.mean(bn)))
            if rn and bn:
                frdiff.append(np.mean([s <= 3 for s in rn]) - np.mean([s <= 3 for s in bn]))
        R["macesub"] = dict(margin_diff=boot(mdiff), false_reject_diff=boot(frdiff))
    res[arm] = R

if "on" in loser_by_arm and "off" in loser_by_arm:
    common = [p for p in loser_by_arm["off"] if p in loser_by_arm["on"]]
    res["loser_off_minus_on"] = boot([loser_by_arm["off"][p] - loser_by_arm["on"][p] for p in common])

g = lambda *ks: (lambda d: d)(res)
def val(path):
    d = res
    for k in path:
        if not isinstance(d, dict) or k not in d or d[k] is None:
            return None
        d = d[k]
    return d
v = val(("off", "rot", "loser")); res["P_R3A1"] = None if v is None else bool(v[1][1] < 0)
v = val(("off", "rot", "gainer")); res["P_R3A2"] = None if v is None else bool(v[1][0] > 0)
v = val(("loser_off_minus_on",)); res["P_R3A3"] = None if v is None else bool(v[1][1] < 0)
v = val(("off", "ksub", "margin_diff_kgt1")); res["P_R3A4"] = None if v is None else bool(v[1][0] > 0)
v = val(("on", "macesub", "margin_diff")); res["P_R3C1"] = None if v is None else bool(v[1][0] > 0)
w = val(("off", "macesub", "margin_diff")); res["P_R3C2"] = None if w is None else bool(w[1][0] > 0)
res["P_R3C3"] = None if (v is None or w is None) else bool(v[0] < w[0])
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
