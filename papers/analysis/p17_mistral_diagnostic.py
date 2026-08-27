# POST HOC diagnostic (unregistered), written after the Registration 5 coverage run to
# check whether Mistral-7B's null inflation delta means it resists anchoring.
# IT DOES NOT. This script documents the correction.
#
# Finding. Mistral-7B-Instruct-v0.3 emits scores that are EXACTLY integers (max deviation
# from the nearest integer: 0.000000; 11 distinct values across the whole pool), i.e. the
# judge puts essentially all probability mass on one score token, so the logprob-expected
# value of bon_judge.py collapses to that integer. gemma-2-9b and Qwen-7B produce ~900-4500
# distinct values on the same pool.
# Consequence for the estimator: with 11 possible values and 52.6% of referenced scores at
# exactly 10, best-of-64 selection ties MASSIVELY. Mean number of samples tied at the
# maximum rubric-a score, k>1 items: Mistral 17.8 blind / 32.1 referenced, against exactly
# 1.0 for gemma-2-9b and Qwen-7B in both conditions. The frozen estimator breaks ties
# uniformly at random (NTIE resamples), so under Mistral, selection is close to a lottery
# over half the pool and cannot express a scoring preference.
# Mistral DOES anchor, mildly: its referenced anchoring margin is +1.15 (k=2), +1.10 (k=4),
# +2.07 (k=8) points and its mean referenced-minus-blind score shift is +0.79 points. Those
# preferences simply cannot propagate into best-of-64 inflation at this score resolution.
# Corrected reading: Mistral's null is a SCORE-RESOLUTION artifact of that judge's output
# behavior, not evidence of anchoring resistance. Independently, its selection quality is
# poor for the same reason: only 51.6% of its top-tied group is valid, against 65-77% for
# the other judges.
# Run from experiments/tfa-vs-judge.
import json
import re

import numpy as np

JUDGES = ["mistralai__Mistral-7B-Instruct-v0.3", "google__gemma-2-9b-it",
          "Qwen__Qwen2.5-7B-Instruct", "Qwen__Qwen2.5-14B-Instruct", "microsoft__phi-4"]


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


def load(jt, cond, rep):
    for pref in ("kstrat", "synthk"):
        try:
            return {json.loads(l)["problem_id"]: json.loads(l)["escore"]
                    for l in open(f"runs/bon_scores_kstrat/{pref}__{jt}__{cond}_{rep}.jsonl")}
        except FileNotFoundError:
            continue
    return None


pool = {json.loads(l)["problem_id"]: json.loads(l)
        for l in open("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")}
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}

out = {}
for jt in JUDGES:
    sa_r, sa_n = load(jt, "ref", "a"), load(jt, "noref", "a")
    if sa_r is None or sa_n is None:
        continue
    allv = np.concatenate([np.array(e) for e in sa_r.values()])
    ties, valid_in_tie, margins, shifts = [], [], [], []
    for pid, it in pool.items():
        if tasks[pid]["k"] == 1 or pid not in sa_r:
            continue
        e = np.array(sa_r[pid])
        idx = np.where(e == e.max())[0]
        ties.append(len(idx))
        o = np.array(it["oracle"])
        valid_in_tie.append(float(o[idx].mean()))
        refn = norm(it["ref_answer"])
        ms, os_ = [], []
        for i, ok in enumerate(o):
            if not ok:
                continue
            a = norm(boxed(it["samples"][i]) or it["samples"][i])
            (ms if a == refn else os_).append(e[i])
        if ms and os_:
            margins.append(float(np.mean(ms) - np.mean(os_)))
        shifts.append(float(np.mean(sa_r[pid]) - np.mean(sa_n[pid])))
    out[jt] = dict(
        distinct_score_values=int(len(np.unique(np.round(allv, 4)))),
        max_deviation_from_integer=float(np.abs(allv - np.round(allv)).max()),
        frac_exactly_10=float(np.mean(allv > 9.999)),
        mean_tied_at_max_ref=float(np.mean(ties)),
        valid_frac_in_top_tie=float(np.mean(valid_in_tie)),
        mean_anchoring_margin=float(np.mean(margins)) if margins else None,
        mean_ref_minus_blind_score_shift=float(np.mean(shifts)))
    d = out[jt]
    print(f"{jt:40s} distinct={d['distinct_score_values']:5d} "
          f"int_dev={d['max_deviation_from_integer']:.6f} "
          f"tied@max={d['mean_tied_at_max_ref']:5.1f} "
          f"margin={d['mean_anchoring_margin']:+.2f} "
          f"shift={d['mean_ref_minus_blind_score_shift']:+.2f}")

json.dump(out, open("../../papers/analysis/p17_mistral_diagnostic.json", "w"), indent=1)
