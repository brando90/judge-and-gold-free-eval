# FROZEN analysis for the multi-valid DPO training-pressure experiment. Committed together
# with dpo_mv_pairs.py BEFORE any training ran; the registered predictions (GATE, P-DP1,
# P-DP2, P-DP3) are stated in dpo_mv_pairs.py's header and scored ONLY by the estimators
# pinned here. Exits gracefully pre-data.
#
# Pinned estimators (all vs the base policy, item-level cluster bootstrap, NBOOT=1000,
# numpy default_rng(0); rubric b is the reporting replicate for the single-reference judge,
# rubric a for the m1 gate scores which exist on rubric a):
#   GATE(ref arm): mean per-item gain in the single-reference judge's rubric-b score on
#     train items, CI > 0. GATE(m1 arm): same with the blind-then-reveal rubric-a score.
#   P-DP1: match-rate gain (fraction of samples whose loose-normalized boxed answer equals
#     ref_answer), ref-arm gain minus m1-arm gain on train items, CI > 0.
#   P-DP2: wedge = (single-reference judge-score gain in points) - 10 * (oracle-accuracy
#     gain); ref-arm wedge minus m1-arm wedge on train items, CI > 0.
#   P-DP3: held-out oracle-accuracy change, m1 arm minus ref arm, directional >= 0.
# Run from experiments/tfa-vs-judge (or the cluster repo root) after pipeline18 completes.
import json
import os
import re

import numpy as np

NBOOT = 1000
rng = np.random.default_rng(0)
OUT = "runs/dpo_mv"
JT = "Qwen__Qwen2.5-7B-Instruct"


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


need = [f"{OUT}/eval_{p}_{s}.jsonl" for p in ("base", "ref", "m1") for s in ("train", "heldout")]
if not all(os.path.exists(f) for f in need):
    print("[dpo_mv_analysis] pre-data: eval files not present yet; predictions remain "
          "unscored. Nothing written.")
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


pools = {(p, s): load_pool(p, s) for p in ("base", "ref", "m1") for s in ("train", "heldout")}
res = {}
md = ["| readout | value [95% CI] | verdict |", "|---|---|---|"]

def item_stats(p, s):
    st = {}
    ref_b = load_scores(p, s, "synthk", "ref", "b")
    m1_a = load_scores(p, s, "kstrat", "m1", "a") if s == "train" else None
    for pid, r in pools[(p, s)].items():
        acc = float(np.mean(r["oracle"])) if "oracle" in r else None
        match = float(np.mean([1.0 if norm(extract_boxed(x) or x) == norm(r["ref_answer"])
                               else 0.0 for x in r["samples"]]))
        st[pid] = dict(acc=acc, match=match,
                       ref_b=float(np.mean(ref_b[pid])) if ref_b and pid in ref_b else None,
                       m1_a=float(np.mean(m1_a[pid])) if m1_a and pid in m1_a else None)
    return st

S = {(p, s): item_stats(p, s) for p in ("base", "ref", "m1") for s in ("train", "heldout")}

def paired(metric, p, s, q="base"):
    ids = [i for i in S[(p, s)] if i in S[(q, s)]
           and S[(p, s)][i][metric] is not None and S[(q, s)][i][metric] is not None]
    return [S[(p, s)][i][metric] - S[(q, s)][i][metric] for i in ids]

gate_ref = ci(paired("ref_b", "ref", "train"))
gate_m1 = ci(paired("m1_a", "m1", "train"))
res["gate"] = dict(ref=gate_ref, m1=gate_m1)
md.append(f"| GATE ref arm (ref-judge score gain, train) | {gate_ref[0]:+.3f} "
          f"[{gate_ref[1][0]:+.3f},{gate_ref[1][1]:+.3f}] | "
          f"{'PASS' if gate_ref[1][0] > 0 else 'FAIL — arm void'} |")
md.append(f"| GATE m1 arm (m1-judge score gain, train) | {gate_m1[0]:+.3f} "
          f"[{gate_m1[1][0]:+.3f},{gate_m1[1][1]:+.3f}] | "
          f"{'PASS' if gate_m1[1][0] > 0 else 'FAIL — arm void'} |")

d1_ref, d1_m1 = paired("match", "ref", "train"), paired("match", "m1", "train")
d1 = ci([a - b for a, b in zip(d1_ref, d1_m1)])
res["P_DP1"] = dict(delta=d1, ref_gain=ci(d1_ref), m1_gain=ci(d1_m1))
md.append(f"| P-DP1 parroting (match-rate gain, ref minus m1) | {d1[0]:+.3f} "
          f"[{d1[1][0]:+.3f},{d1[1][1]:+.3f}] | "
          f"{'CONFIRMED' if d1[1][0] > 0 else 'not confirmed'} |")

def wedge(p):
    j = paired("ref_b", p, "train")
    a = paired("acc", p, "train")
    return [x - 10 * y for x, y in zip(j, a)]

d2 = ci([a - b for a, b in zip(wedge("ref"), wedge("m1"))])
res["P_DP2"] = dict(delta=d2, ref_wedge=ci(wedge("ref")), m1_wedge=ci(wedge("m1")))
md.append(f"| P-DP2 wedge (ref minus m1) | {d2[0]:+.3f} "
          f"[{d2[1][0]:+.3f},{d2[1][1]:+.3f}] | "
          f"{'CONFIRMED' if d2[1][0] > 0 else 'not confirmed'} |")

d3 = ci([a - b for a, b in zip(paired("acc", "m1", "heldout"), paired("acc", "ref", "heldout"))])
res["P_DP3"] = dict(delta=d3, ref_heldout=ci(paired("acc", "ref", "heldout")),
                    m1_heldout=ci(paired("acc", "m1", "heldout")))
md.append(f"| P-DP3 held-out acc, m1 minus ref (directional) | {d3[0]:+.3f} "
          f"[{d3[1][0]:+.3f},{d3[1][1]:+.3f}] | "
          f"{'direction holds' if d3[0] >= 0 else 'direction fails'} |")

json.dump(res, open("../../papers/analysis/dpo_mv_results.json"
                    if os.path.exists("../../papers/analysis") else "dpo_mv_results.json",
                    "w"), indent=1)
print("\n".join(md))
