# Canonical producer for the Paper D dynamic-inversion JSONs (run from
# experiments/tfa-vs-judge). Reproduces, from the committed pools and score files:
#   ties_fullset.json            per-config excess gap and oracle regret, full 51 items
#   ties_inband.json             same on the in-band [0.2, 0.8] subset (n=7)
#   ties_paired.json             per-scale paired (ref minus blind) gap delta, item bootstrap
#   ties_regret_cis.json         per-scale and pooled regret deltas with CIs
#   ties_pooled_delta.json       pooled gap delta, item-level cluster bootstrap across scales
#   ties_collapse_conditional.json  original-arm conditional selection collapse
# Machinery identical to scripts/bon_analysis.py (escore rep a selects, rep b reports;
# excess gap in baseline-sd units over a within-item permutation null).
import json
import re
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)

rng = np.random.default_rng(0)
pool = {r["problem_id"]: r for r in
        (json.loads(l) for l in open("runs/bon/bon_ties__Qwen__Qwen2.5-7B-Instruct.jsonl"))}
JUDGES = ["Qwen2.5-1.5B-Instruct", "Qwen2.5-3B-Instruct", "Qwen2.5-7B-Instruct",
          "Qwen2.5-14B-Instruct"]
SHORT = {"Qwen2.5-1.5B-Instruct": "1.5B", "Qwen2.5-3B-Instruct": "3B",
         "Qwen2.5-7B-Instruct": "7B", "Qwen2.5-14B-Instruct": "14B"}


def scores(jm, cond, rep):
    return {json.loads(l)["problem_id"]: json.loads(l)["escore"]
            for l in open(f"runs/bon_scores_ties_full/ties__Qwen__{jm}__{cond}_{rep}.jsonl")}


def per_item(jm, cond):
    sa, sb = scores(jm, cond, "a"), scores(jm, cond, "b")
    gaps, regrets = {}, {}
    for pid, it in pool.items():
        if pid not in sa:
            continue
        curves = ns["per_item_curves"](it, sa[pid], sb[pid])
        null = ns["permutation_null"](it, sa[pid], sb[pid])
        gaps[pid] = (curves[64]["judge_gain"] - curves[64]["true_gain"]) - null
        regrets[pid] = curves[64]["oracle_regret"]
    return gaps, regrets


G, R = {}, {}
for jm in JUDGES:
    for cond in ("noref", "ref"):
        G[(jm, cond)], R[(jm, cond)] = per_item(jm, cond)

inband = {pid for pid, it in pool.items()
          if 0.2 <= np.mean(it["oracle"]) <= 0.8}

fullset, inb = {}, {}
for (jm, cond), g in G.items():
    key = f"ties__Qwen__{jm}__{cond}"
    r = R[(jm, cond)]
    fullset[key] = dict(n=len(g), excess_gap=round(float(np.mean(list(g.values()))), 3),
                        regret=round(float(np.mean(list(r.values()))), 3))
    gi = [g[p] for p in g if p in inband]
    ri = [r[p] for p in r if p in inband]
    inb[key] = dict(n=len(gi), excess_gap=round(float(np.mean(gi)), 3),
                    regret=round(float(np.mean(ri)), 3))
json.dump(fullset, open("../../papers/analysis/ties_fullset.json", "w"), indent=1)
json.dump(inb, open("../../papers/analysis/ties_inband.json", "w"), indent=1)

paired, regret_cis = {}, {}
pids = sorted(pool)
scale_gap_deltas, scale_regret_deltas = [], []
for jm in JUDGES:
    dg = np.array([G[(jm, "ref")][p] - G[(jm, "noref")][p] for p in pids])
    dr = np.array([R[(jm, "ref")][p] - R[(jm, "noref")][p] for p in pids])
    scale_gap_deltas.append(dg)
    scale_regret_deltas.append(dr)
    bg = [float(np.mean(rng.choice(dg, len(dg)))) for _ in range(4000)]
    br = [float(np.mean(rng.choice(dr, len(dr)))) for _ in range(4000)]
    paired[SHORT[jm]] = dict(delta=round(float(dg.mean()), 2),
                             ci=[round(float(np.percentile(bg, 2.5)), 2),
                                 round(float(np.percentile(bg, 97.5)), 2)], n=len(pids))
    regret_cis[SHORT[jm]] = dict(delta=round(float(dr.mean()), 3),
                                 ci=[round(float(np.percentile(br, 2.5)), 3),
                                     round(float(np.percentile(br, 97.5)), 3)], n=len(pids))
json.dump(paired, open("../../papers/analysis/ties_paired.json", "w"), indent=1)

# pooled: cluster bootstrap over items; each resampled item contributes its four scale deltas
DG = np.stack(scale_gap_deltas)  # 4 x 51
DR = np.stack(scale_regret_deltas)
idx = np.arange(len(pids))


def pooled(D):
    boot = []
    for _ in range(4000):
        i = rng.choice(idx, len(idx))
        boot.append(float(D[:, i].mean()))
    return float(D.mean()), [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]


pd_, pdci = pooled(DG)
json.dump(dict(pooled_delta=pd_, ci=pdci, n=len(pids)),
          open("../../papers/analysis/ties_pooled_delta.json", "w"), indent=1)
prd, prdci = pooled(DR)
regret_cis["pooled"] = dict(delta=round(prd, 3), ci=[round(v, 3) for v in prdci], n=len(pids))
json.dump(regret_cis, open("../../papers/analysis/ties_regret_cis.json", "w"), indent=1)

# original-arm conditional collapse: items whose valid samples include both ref-matching and
# non-matching answers; selection by rep-a argmax over all 64; rate = matched/selected-valid
def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


# Two eligibility variants, reported separately because they answer different questions:
#  ref_in_pool: the original 10 items whose reference appears among valid samples; 6 of
#    these are FORCED (every valid sample matches the reference), which mechanically
#    inflates both arms' match rates.
#  both_kinds: the 4 free items with matching AND non-matching valid answers, where the
#    match rate is informative.
collapse = {}
for jm in JUDGES:
    for cond in ("noref", "ref"):
        sa = scores(jm, cond, "a")
        cells = {"ref_in_pool": [0, 0, 0], "both_kinds": [0, 0, 0]}
        for pid, it in pool.items():
            if pid not in sa:
                continue
            refn = norm(it["ref_answer"])
            kinds = {norm(boxed(s) or s) == refn
                     for s, ok in zip(it["samples"], it["oracle"]) if ok}
            eligible = ["ref_in_pool"] if True in kinds else []
            if kinds == {True, False}:
                eligible.append("both_kinds")
            if not eligible:
                continue
            sel = int(np.argmax(sa[pid]))
            valid = it["oracle"][sel]
            match = valid and norm(boxed(it["samples"][sel]) or it["samples"][sel]) == refn
            for e in eligible:
                cells[e][0] += 1
                cells[e][1] += int(bool(valid))
                cells[e][2] += int(bool(match))
        for e, (n_el, n_valid, n_match) in cells.items():
            collapse[f"{SHORT[jm]}_{cond}_{e}"] = dict(
                rate=round(n_match / n_valid, 2) if n_valid else None, n=n_el,
                selected_valid=n_valid, matched=n_match)
json.dump(collapse, open("../../papers/analysis/ties_collapse_conditional.json", "w"), indent=1)

print("fullset:", json.dumps(fullset))
print("paired:", json.dumps(paired))
print("pooled:", pd_, pdci)
print("regret:", json.dumps(regret_cis))
print("collapse:", json.dumps(collapse))
