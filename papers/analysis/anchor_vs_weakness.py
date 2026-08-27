# "Anchoring versus weakness": does the rotation flip survive on exactly the samples the
# judge has ALREADY proven it can recognize as correct without any reference?
# INTERNAL REGISTRATION: this header pins the filter, populations, estimator, and predictions;
# the file is git-committed BEFORE being run (commit timestamp = registration; no OSF post).
#
# Objection this closes. The rotation experiment shows the identical sample's score follows
# the shown reference. A skeptic can still say: maybe the judge simply does not KNOW the
# non-matching answer is valid, so the reference is informing rather than anchoring. Filter:
# keep only samples/items the judge itself blindly scored as correct, then re-ask whether the
# reference still moves them.
#
# Data (existing scores only, zero GPU): the 51-item Ties pool; original-arm scores in
# runs/bon_scores_ties_full (noref and ref, rubrics a/b), rotation-arm referenced scores in
# runs/bon_scores_ties_rot (ref, rubrics a/b); judges Qwen2.5-{1.5B,3B,7B,14B}-Instruct.
#
# Pinned definitions:
#   - Blind validation of a SAMPLE: mean of its two blind scores (noref rubric a, noref
#     rubric b) >= 7.0 on the 0-10 scale. The bar is fixed here, pre-run.
#   - Gainers: oracle-valid samples whose normalized boxed answer matches the ROTATED
#     reference and not the original; delta = rotated-ref score minus original-ref score,
#     per rubric. FILTERED gainers additionally pass blind validation.
#   - Losers: oracle-valid samples matching the ORIGINAL reference only; same delta,
#     expected negative; same filter.
#   - Margin (rotation arm, rubric a and b separately): within items where BOTH groups
#     (matching and non-matching valid samples) have blind-validated members, the mean
#     referenced score of blind-validated matching samples minus blind-validated
#     non-matching ones.
#   - CIs: item-level cluster bootstrap (resample items, NBOOT=1000, numpy default_rng(0)).
#
# REGISTERED PREDICTIONS (committed before running):
#   P-AW1: filtered gainer deltas stay positive with 95% CIs excluding zero at every judge
#     size on rubric a (rubric b as replicate). I.e. anchoring survives on samples the judge
#     demonstrably knew were correct: it is anchoring, not ignorance.
#   P-AW2: the filtered rotation-arm margins stay positive with CIs excluding zero for at
#     least three of four judge sizes on rubric a.
#   Retention rates and the unfiltered comparison are reported descriptively.
#
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/anchor_vs_weakness.py
import json
import re

import numpy as np

NBOOT = 1000
rng = np.random.default_rng(0)
SIZES = ["1.5B", "3B", "7B", "14B"]
BAR = 7.0


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


def load(path):
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(path))}


orig = {r["problem_id"]: r for r in
        (json.loads(l) for l in open("runs/bon/bon_ties__Qwen__Qwen2.5-7B-Instruct.jsonl"))}
rot = {r["problem_id"]: r for r in
       (json.loads(l) for l in open("runs/bon/bon_tiesrot__Qwen__Qwen2.5-7B-Instruct.jsonl"))}


def cluster_ci(vals_by_item):
    items = [np.mean(v) for v in vals_by_item.values() if v]
    if not items:
        return None, [None, None], 0
    items = np.asarray(items, float)
    boots = [items[rng.integers(0, len(items), len(items))].mean() for _ in range(NBOOT)]
    return float(items.mean()), [float(np.percentile(boots, 2.5)),
                                 float(np.percentile(boots, 97.5))], len(items)


out = {}
md = ["| judge | rubric | readout | unfiltered | filtered (blind-validated) | retained |",
      "|---|---|---|---|---|---|"]
for size in SIZES:
    tag = f"Qwen__Qwen2.5-{size}-Instruct"
    sc = {}
    for arm, d in (("full", "runs/bon_scores_ties_full"), ("rot", "runs/bon_scores_ties_rot")):
        for cond in (("noref", "ref") if arm == "full" else ("ref",)):
            for rep in ("a", "b"):
                sc[(arm, cond, rep)] = load(f"{d}/ties__{tag}__{cond}_{rep}.jsonl")
    out[size] = {}
    for rep in ("a", "b"):
        g_all, g_fil, l_all, l_fil = {}, {}, {}, {}
        m_fil = {}
        n_g = n_gf = 0
        for pid, it in orig.items():
            ro, rn = norm(it["ref_answer"]), norm(rot[pid]["ref_answer"])
            blind = [(sc[("full", "noref", "a")][pid][i] + sc[("full", "noref", "b")][pid][i]) / 2
                     for i in range(len(it["samples"]))]
            so = sc[("full", "ref", rep)][pid]
            sr = sc[("rot", "ref", rep)][pid]
            mm, nn = [], []
            for i, (s, ok) in enumerate(zip(it["samples"], it["oracle"])):
                if not ok:
                    continue
                a = norm(extract_boxed(s) or s)
                d = sr[i] - so[i]
                if a == rn and a != ro:
                    g_all.setdefault(pid, []).append(d)
                    n_g += 1
                    if blind[i] >= BAR:
                        g_fil.setdefault(pid, []).append(d)
                        n_gf += 1
                elif a == ro and a != rn:
                    l_all.setdefault(pid, []).append(d)
                    if blind[i] >= BAR:
                        l_fil.setdefault(pid, []).append(d)
                if a == rn:
                    mm.append((i, blind[i]))
                else:
                    nn.append((i, blind[i]))
            mmv = [sr[i] for i, b in mm if b >= BAR]
            nnv = [sr[i] for i, b in nn if b >= BAR]
            if mmv and nnv:
                m_fil[pid] = [float(np.mean(mmv) - np.mean(nnv))]
        res = {}
        for key, allv, filv in (("gainers", g_all, g_fil), ("losers", l_all, l_fil)):
            ma, ca, na = cluster_ci(allv)
            mf, cf, nf = cluster_ci(filv)
            res[key] = dict(unfiltered=dict(mean=ma, ci=ca, n_items=na),
                            filtered=dict(mean=mf, ci=cf, n_items=nf))
            if ma is not None:
                md.append(f"| {size} | {rep} | {key} $\\Delta$ | "
                          f"{ma:+.2f} [{ca[0]:+.2f},{ca[1]:+.2f}] (n={na}) | "
                          + (f"{mf:+.2f} [{cf[0]:+.2f},{cf[1]:+.2f}] (n={nf}) |"
                             if mf is not None else "no samples survive |")
                          + (f" {n_gf}/{n_g} samples |" if key == "gainers" else " |"))
        mm_, cm_, nm_ = cluster_ci(m_fil)
        res["margin_filtered"] = dict(mean=mm_, ci=cm_, n_items=nm_)
        if mm_ is not None:
            md.append(f"| {size} | {rep} | margin (blind-validated both groups) |  | "
                      f"{mm_:+.2f} [{cm_[0]:+.2f},{cm_[1]:+.2f}] (n={nm_}) |  |")
        out[size][rep] = res

json.dump(out, open("../../papers/analysis/anchor_vs_weakness.json", "w"), indent=1)
print("\n".join(md))
