# FROZEN producer for R4-C (papers/D-iclr/registration_round4.md), committed before any R4-C score exists.
# Same readouts as r3_toggle_analysis.py, for Qwen3-14B, plus per-task blind verification AUROC.
# The Qwen3-8B verification AUROCs computed here from existing files are post hoc.
# Run from experiments/tfa-vs-judge. Writes papers/analysis/r4_toggle14b_results.json.
import json
import os
import re

import numpy as np

NBOOT = 1000
OUT = "../../papers/analysis/r4_toggle14b_results.json"
J14, J8 = "Qwen__Qwen3-14B", "Qwen__Qwen3-8B"


def boot(x, seed=0):
    x = np.asarray([v for v in x if v is not None], float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 3), [round(float(np.percentile(m, 2.5)), 3), round(float(np.percentile(m, 97.5)), 3)], len(x)]


def load(path):
    if not os.path.exists(path):
        return None
    return {r["problem_id"]: dict(zip(r["idx"], r["score"])) for r in (json.loads(l) for l in open(path))}


def arm_file(model, pool, arm, cond):
    if model == J14:
        return f"runs/r4/qwen3_14b/{pool}__think{arm}__{model}__{cond}.jsonl"
    if arm == "on" and pool in ("rot", "ksub"):
        return f"runs/r2/scores/{pool}__reason__{model}__{cond}.jsonl"
    return f"runs/r3/scores/{pool}__think{arm}__{model}__{cond}.jsonl"


def norm_boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


def normA(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def sel_acc(scores, oracle):
    pairs = [(s, o) for s, o in zip(scores, oracle) if s is not None]
    if not pairs:
        return None
    s = np.array([p[0] for p in pairs]); o = np.array([p[1] for p in pairs], float)
    return float(o[np.isclose(s, s.max())].mean())


def auroc(sc, lab):
    pos = np.array([s for s, l in zip(sc, lab) if l and s is not None], float)
    neg = np.array([s for s, l in zip(sc, lab) if not l and s is not None], float)
    if len(pos) == 0 or len(neg) == 0:
        return None
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


rot = [json.loads(l) for l in open("runs/r2/rot_sub.jsonl")]
ksub = [json.loads(l) for l in open("runs/r2/ksub.jsonl")]
mace = [json.loads(l) for l in open("runs/r3/macesub.jsonl")]


def analyze(model):
    res, loser_by_arm = {}, {}
    for arm in ("on", "off"):
        R = {}
        ref, rr = load(arm_file(model, "rot", arm, "ref")), load(arm_file(model, "rot", arm, "refrot"))
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
        kr, kn = load(arm_file(model, "ksub", arm, "ref")), load(arm_file(model, "ksub", arm, "noref"))
        if kn is not None:
            R["verif_auroc_ksub"] = boot([auroc([kn.get(t["problem_id"], {}).get(i) for i in t["idx"]], t["oracle"]) for t in ksub])
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
        mr, mn = load(arm_file(model, "macesub", arm, "ref")), load(arm_file(model, "macesub", arm, "noref"))
        if mn is not None:
            R["verif_auroc_macesub"] = boot([auroc([mn.get(t["problem_id"], {}).get(i) for i in t["idx"]],
                                                   [g != "invalid" for g in t["group"]]) for t in mace])
        if mr is not None and mn is not None:
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
    return res


out = {"Qwen3-14B": analyze(J14), "Qwen3-8B_posthoc": analyze(J8)}


def val(*path):
    d = out
    for k in path:
        if not isinstance(d, dict) or k not in d or d[k] is None:
            return None
        d = d[k]
    return d


m = "Qwen3-14B"
v = val(m, "off", "rot", "loser"); out["P_R4C1"] = None if v is None else bool(v[1][1] < 0)
v = val(m, "loser_off_minus_on"); out["P_R4C2"] = None if v is None else bool(v[1][1] < 0)
on, off = val(m, "on", "macesub", "margin_diff"), val(m, "off", "macesub", "margin_diff")
out["P_R4C3"] = None if on is None else bool(on[1][0] > 0)
out["P_R4C4"] = None if (on is None or off is None) else bool(on[0] < off[0])
a, b = val(m, "on", "verif_auroc_ksub"), val(m, "on", "verif_auroc_macesub")
out["P_R4C5"] = None if (a is None or b is None) else bool(a[0] > b[0])
json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k.startswith("P_")}, indent=1))
