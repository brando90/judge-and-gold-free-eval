# FROZEN analysis for DPO run 3 (GATE-F, the registered FINAL attempt) plus the blind-judge
# attribution arm. Committed BEFORE any run-3 training; estimators are an exact mirror of
# dpo_mv_analysis.py (same NBOOT, rng, metrics, pairing), applied to runs/dpo_mv3 and
# extended to a third arm. The GATE-F predictions (P-DPF1..P-DPF3) are registered in
# papers/D-reference-laws/registration.md commit d33614e; the blind-arm predictions
# (GATE-B, P-DPB1, P-DPB2) are registered in the addendum committed together with this file.
#
# Pinned estimators (identical to dpo_mv_analysis.py):
#   GATE(ref):   per-item gain in single-reference judge rubric-b score, train, vs base, CI > 0.
#   GATE(m1):    same with blind-then-reveal rubric-a score.
#   GATE-B(blind): same with the BLIND judge's rubric-b score (noref_b).
#   P-DPF1: wedge = (ref_b judge-score gain) - 10 * (oracle-accuracy gain), train;
#           ref minus m1, CI > 0 (conditional on both gates).
#   P-DPF2: held-out oracle-accuracy change, m1 minus ref, directional >= 0.
#   P-DPF3: match-rate gain, ref minus m1, CI > 0.
#   P-DPB1: wedge, ref minus blind, CI > 0 (conditional on ref + blind gates).
#   P-DPB2: train oracle-accuracy change, blind minus ref, directional >= 0.
#   Exploratory (disclosed, not registered): wedge per point of own-judge score gain.
# Run from experiments/tfa-vs-judge (or cluster repo root) after the run-3 pipeline.
import json
import os
import re

import numpy as np

NBOOT = 1000
rng = np.random.default_rng(0)
OUT = os.environ.get("DPO_MV_OUT", "runs/dpo_mv3")
JT = "Qwen__Qwen2.5-7B-Instruct"
ARMS = ("ref", "m1", "blind")


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


need = [f"{OUT}/eval_{p}_{s}.jsonl" for p in ("base",) + ARMS for s in ("train", "heldout")]
missing = [f for f in need if not os.path.exists(f)]
if missing:
    print(f"[dpo_mv3_analysis] pre-data: {len(missing)} eval files absent "
          f"(first: {missing[0]}); predictions remain unscored. Nothing written.")
    raise SystemExit


def load_pool(p, s):
    return {r["problem_id"]: r for r in (json.loads(l) for l in open(f"{OUT}/eval_{p}_{s}.jsonl"))}


def load_scores(p, s, prefix, cond, rep):
    f = f"{OUT}/scores_{p}_{s}/{prefix}__{JT}__{cond}_{rep}.jsonl"
    if not os.path.exists(f):
        return None
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))}


def ci(pairs):
    v = np.asarray(pairs, float)
    boots = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(NBOOT)]
    return float(v.mean()), [float(np.percentile(boots, 2.5)),
                             float(np.percentile(boots, 97.5))]


pools = {(p, s): load_pool(p, s) for p in ("base",) + ARMS for s in ("train", "heldout")}
res = {}
md = ["| readout | value [95% CI] | verdict |", "|---|---|---|"]


def item_stats(p, s):
    st = {}
    ref_b = load_scores(p, s, "synthk", "ref", "b")
    noref_b = load_scores(p, s, "synthk", "noref", "b")
    m1_a = load_scores(p, s, "kstrat", "m1", "a") if s == "train" else None
    for pid, r in pools[(p, s)].items():
        acc = float(np.mean(r["oracle"])) if "oracle" in r else None
        match = float(np.mean([1.0 if norm(extract_boxed(x) or x) == norm(r["ref_answer"])
                               else 0.0 for x in r["samples"]]))
        st[pid] = dict(acc=acc, match=match,
                       ref_b=float(np.mean(ref_b[pid])) if ref_b and pid in ref_b else None,
                       noref_b=float(np.mean(noref_b[pid])) if noref_b and pid in noref_b else None,
                       m1_a=float(np.mean(m1_a[pid])) if m1_a and pid in m1_a else None)
    return st


S = {(p, s): item_stats(p, s) for p in ("base",) + ARMS for s in ("train", "heldout")}


def paired(metric, p, s, q="base"):
    ids = [i for i in S[(p, s)] if i in S[(q, s)]
           and S[(p, s)][i][metric] is not None and S[(q, s)][i][metric] is not None]
    return [S[(p, s)][i][metric] - S[(q, s)][i][metric] for i in ids]


gates = dict(ref=ci(paired("ref_b", "ref", "train")),
             m1=ci(paired("m1_a", "m1", "train")),
             blind=ci(paired("noref_b", "blind", "train")))
res["gate"] = gates
for arm, g in gates.items():
    md.append(f"| GATE {arm} arm (own-judge score gain, train) | {g[0]:+.3f} "
              f"[{g[1][0]:+.3f},{g[1][1]:+.3f}] | "
              f"{'PASS' if g[1][0] > 0 else 'FAIL — arm void'} |")


def wedge(p):
    j = paired("ref_b", p, "train")
    a = paired("acc", p, "train")
    return [x - 10 * y for x, y in zip(j, a)]


for name, a, b in (("P_DPF1_wedge_ref_minus_m1", "ref", "m1"),
                   ("P_DPB1_wedge_ref_minus_blind", "ref", "blind")):
    d = ci([x - y for x, y in zip(wedge(a), wedge(b))])
    res[name] = dict(delta=d, **{f"{a}_wedge": ci(wedge(a)), f"{b}_wedge": ci(wedge(b))})
    md.append(f"| {name} | {d[0]:+.3f} [{d[1][0]:+.3f},{d[1][1]:+.3f}] | "
              f"{'CONFIRMED' if d[1][0] > 0 else 'not confirmed'} |")

d2 = ci([x - y for x, y in zip(paired("acc", "m1", "heldout"), paired("acc", "ref", "heldout"))])
res["P_DPF2_heldout_m1_minus_ref"] = dict(delta=d2,
                                          ref=ci(paired("acc", "ref", "heldout")),
                                          m1=ci(paired("acc", "m1", "heldout")),
                                          blind=ci(paired("acc", "blind", "heldout")))
md.append(f"| P-DPF2 held-out acc, m1 minus ref (directional) | {d2[0]:+.3f} "
          f"[{d2[1][0]:+.3f},{d2[1][1]:+.3f}] | "
          f"{'direction holds' if d2[0] >= 0 else 'direction fails'} |")

d3r, d3m = paired("match", "ref", "train"), paired("match", "m1", "train")
d3 = ci([x - y for x, y in zip(d3r, d3m)])
res["P_DPF3_parroting"] = dict(delta=d3, ref_gain=ci(d3r), m1_gain=ci(d3m),
                               blind_gain=ci(paired("match", "blind", "train")))
md.append(f"| P-DPF3 parroting (match-rate gain, ref minus m1) | {d3[0]:+.3f} "
          f"[{d3[1][0]:+.3f},{d3[1][1]:+.3f}] | "
          f"{'CONFIRMED' if d3[1][0] > 0 else 'not confirmed'} |")

d4 = ci([x - y for x, y in zip(paired("acc", "blind", "train"), paired("acc", "ref", "train"))])
res["P_DPB2_train_acc_blind_minus_ref"] = dict(delta=d4,
                                               ref=ci(paired("acc", "ref", "train")),
                                               blind=ci(paired("acc", "blind", "train")),
                                               m1=ci(paired("acc", "m1", "train")))
md.append(f"| P-DPB2 train acc, blind minus ref (directional) | {d4[0]:+.3f} "
          f"[{d4[1][0]:+.3f},{d4[1][1]:+.3f}] | "
          f"{'direction holds' if d4[0] >= 0 else 'direction fails'} |")

# exploratory: wedge per point of own-judge gain
own = dict(ref="ref_b", m1="m1_a", blind="noref_b")
expl = {}
for p in ARMS:
    g = float(np.mean(paired(own[p], p, "train"))) if paired(own[p], p, "train") else None
    w = float(np.mean(wedge(p)))
    expl[p] = dict(own_gain=g, wedge=w, wedge_per_point=(w / g if g else None))
res["exploratory_wedge_per_reward_point"] = expl

json.dump(res, open("../../papers/analysis/dpo_mv3_results.json"
                    if os.path.exists("../../papers/analysis") else "dpo_mv3_results.json",
                    "w"), indent=1)
print("\n".join(md))
