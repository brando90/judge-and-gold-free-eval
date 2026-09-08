# FROZEN analysis for the frontier-judge instruction-mitigation extension (P-FI1, P-FI2).
# INTERNAL REGISTRATION: committed together with the harness's refinst/refinst2 support (frontier_api_judge.py)
# BEFORE any frontier refinst/refinst2 score exists; the commit timestamp is the registration.
#
# Question. The paper's registered finding (P-S2, P-S2b, synthetic grid) is that telling the
# judge "any correct answer deserves full credit" is a placebo below frontier capability: it
# fixes phi-4 (14B, the strongest OPEN judge tested) near-completely, does nothing or worse for
# smaller judges. Whether an actual frontier judge (Sonnet 5, GPT-4.1, GPT-5.4) sits "above" that
# capability line has never been tested; phi-4 is not frontier-class. Separately, the frontier
# margin check (no instruction) showed the base anchoring does not shrink with scale up to
# Sonnet 5, which argues against capability being the bottleneck. This tests the instruction
# directly on frontier judges rather than extrapolating either way.
#
# Design. k-stratified pool, k>1 items. Conditions: ref (bare reference, already scored),
# refinst, refinst2 (both verbatim from bon_judge.py). Rubric a only, matching the original
# P-S2/P-S2b scope. Two readouts, estimators copied from mitigation_analysis.py: E1 margin (mean
# score of reference-matching valid samples minus non-matching, item mean, item bootstrap) and
# E2 gap (paired condition-minus-blind excess-gap delta at n=64, bon_analysis machinery), where
# the judge has full (not valid-only) samples so inflation is computable; a valid-only judge
# (no logprobs) gets the margin readout only, as in the rest of Phase 1.
#
# REGISTERED PREDICTIONS (weak/directional, matching the original P-S2 form; the LEVEL, not just
# the sign, is the informative readout and is reported descriptively regardless of verdict):
#   P-FI1: refinst's margin at k>1 is smaller than the bare reference's (paired per-item
#          difference, CI excluding zero), scored per judge that has both conditions.
#   P-FI2: refinst2 reproduces the same direction as refinst (do-not-compare phrasing is not a
#          single-wording artifact), scored per judge.
# A null (margin unchanged or worse under instruction) is reported as prominently as a
# confirmation; it would mean the capability gate does not close even at frontier scale, which
# bears directly on whether "tell the judge" is ever a safe practitioner recommendation.
#
# Run from experiments/tfa-vs-judge: python3 ../../papers/analysis/frontier_instruction_analysis.py [judge_tag ...]
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)
rng = np.random.default_rng(0)

JUDGES = sys.argv[1:] or ["openai__gpt-4.1-2025-04-14"]
KPOOL = "runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl"
KS = [2, 4, 8, 16]


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


def bci(vals, B=2000):
    v = np.asarray(vals, float)
    if len(v) == 0:
        return None
    b = [float(np.mean(rng.choice(v, len(v)))) for _ in range(B)]
    return dict(mean=round(float(v.mean()), 3), n=len(v),
               ci=[round(float(np.percentile(b, 2.5)), 3), round(float(np.percentile(b, 97.5)), 3)])


def load(path):
    if not os.path.exists(path):
        return None
    return {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(path)}


tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
pool = {}
for l in open(KPOOL):
    r = json.loads(l)
    if "oracle" not in r:
        continue
    t = tasks[r["problem_id"]]
    r["k"], r["ref_answer"] = t["k"], t["ref_answer"]
    pool[r["problem_id"]] = r

out = {"judges": JUDGES}
for jtag in JUDGES:
    sc = {c: load(f"runs/bon_scores_kstrat/synthk__{jtag}__{c}_a.jsonl") for c in ("ref", "refinst", "refinst2", "noref")}
    have = {c: v is not None for c, v in sc.items()}
    out[f"{jtag}__have"] = have
    if not (have["ref"] and (have["refinst"] or have["refinst2"])):
        continue
    full = any(x is not None for v in sc.values() if v for x in next(iter(v.values())))
    margins = {}
    for cond in ("ref", "refinst", "refinst2", "noref"):
        if not have.get(cond):
            continue
        sa = sc[cond]
        vals = {}
        for pid, it in pool.items():
            if it["k"] not in KS or pid not in sa:
                continue
            refn = norm(it["ref_answer"])
            ms, os_ = [], []
            for i, ok in enumerate(it["oracle"]):
                if not ok or sa[pid][i] is None:
                    continue
                a = norm(boxed(it["samples"][i]) or it["samples"][i])
                (ms if a == refn else os_).append(sa[pid][i])
            if ms and os_:
                vals[pid] = float(np.mean(ms) - np.mean(os_))
        margins[cond] = vals
        out[f"{jtag}__margin_{cond}"] = bci(list(vals.values()))
    for cond in ("refinst", "refinst2"):
        if cond in margins and "ref" in margins:
            shared = sorted(set(margins[cond]) & set(margins["ref"]))
            d = bci([margins[cond][p] - margins["ref"][p] for p in shared])
            out[f"{jtag}__{cond}_minus_ref_margin"] = d
            out[f"{jtag}__P_FI{'1' if cond == 'refinst' else '2'}"] = bool(d and d["ci"][1] < 0)
    if full:
        gaps = {}
        for cond in ("ref", "refinst", "refinst2", "noref"):
            sb = load(f"runs/bon_scores_kstrat/synthk__{jtag}__{cond}_b.jsonl")
            sa = sc.get(cond)
            if sa is None or sb is None:
                continue
            g = {}
            for pid, it in pool.items():
                if it["k"] not in KS or pid not in sa or None in sa[pid] or None in sb[pid]:
                    continue
                c = ns["per_item_curves"](it, sa[pid], sb[pid])
                nl = ns["permutation_null"](it, sa[pid], sb[pid])
                g[pid] = c[64]["judge_gain"] - c[64]["true_gain"] - nl
            gaps[cond] = g
        if "noref" in gaps:
            for cond in [c for c in ("ref", "refinst", "refinst2") if c in gaps]:
                pids = [p for p in gaps[cond] if p in gaps["noref"]]
                d = bci([gaps[cond][p] - gaps["noref"][p] for p in pids])
                out[f"{jtag}__gap_{cond}_minus_blind"] = d

json.dump(out, open("../../papers/analysis/frontier_instruction_results.json", "w"), indent=1)
for k, v in out.items():
    print(k, json.dumps(v) if not isinstance(v, str) else v)
