# Mistral-family score-resolution SCREEN for Ministral-8B-Instruct-2410.
# INTERNAL REGISTRATION: this header pins the screen metrics, the pass thresholds, and the
# predictions, and the file is git-committed BEFORE Ministral produces any score file.
# No OSF post (external registration on hold). Registration 5's substitution rule does NOT
# cover this run: it permits a replacement only for a judge that fails to load or produce
# scores, and Mistral-7B produced valid scores. Ministral-8B is therefore a NEW judge under a
# new internal registration, and its results are reported as such, not as a Registration 5 arm.
#
# Motivation. Mistral-7B-Instruct-v0.3 emits exactly-integer scores (11 distinct values
# pool-wide), ties 17.8 of 64 samples at the maximum, and consequently captures only +0.18
# selection lift over random against +0.36 to +0.46 for four other judges. Its null inflation
# delta is a resolution artifact, not anchoring resistance. This screen asks whether coarse
# integer scoring is a property of the Mistral FAMILY or of that one checkpoint.
#
# Procedure. One judging run only: bon_judge.py on the frozen k-stratified pool, condition
# ref, rubric a (the cheapest arm that exposes both resolution and anchoring). Metrics on
# k>1 items, computed by score_resolution_screen.py's definitions:
#   distinct  = distinct rounded score values pool-wide
#   ties@max  = mean samples sharing the item's maximum score
#   int_dev   = maximum deviation of any score from the nearest integer
#
# PASS THRESHOLD, pinned before the run (chosen to sit far from both observed regimes: the
# four discriminating judges show 2491-2751 distinct and ties@max 1.0; Mistral-7B shows 11
# and 17.8):
#   PASS if distinct >= 100 AND ties@max <= 3.0. Otherwise FAIL.
# Only a judge that PASSES earns the full four-condition, two-rubric grid; a FAIL is reported
# as a family-level finding and no further compute is spent on that checkpoint.
#
# REGISTERED PREDICTIONS:
#   P-MS1: Ministral-8B PASSES the screen (distinct >= 100, ties@max <= 3.0). Rationale: the
#     coarse integer behavior is expected to be a checkpoint property, not a family property.
#   P-MS2 (conditional on PASS): its referenced anchoring margin on k>1 items exceeds
#     Mistral-7B's +1.38, i.e. once a Mistral-family judge can express graded scores, the
#     anchoring the family already shows becomes visible at a magnitude comparable to the
#     other families ( +4.0 or above would match gemma/Qwen/phi-4 territory ).
#   A FAIL on P-MS1 is informative: it would make coarse scoring a Mistral-family trait and
#     the family unsuitable as a best-of-n selector without decoding changes.
#
# Run from experiments/tfa-vs-judge after the judging run lands:
#   python3 ../../papers/analysis/ministral_screen.py
import json
import os
import re

import numpy as np

JT = "mistralai__Ministral-8B-Instruct-2410"
DISTINCT_MIN, TIES_MAX = 100, 3.0


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


path = None
for pref in ("kstrat", "synthk"):
    p = f"runs/bon_scores_kstrat/{pref}__{JT}__ref_a.jsonl"
    if os.path.exists(p):
        path = p
        break
if path is None:
    print("[ministral_screen] pre-data: no score file for Ministral-8B yet; "
          "predictions P-MS1/P-MS2 remain unscored. Nothing written.")
    raise SystemExit

sa = {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(path)}
pool = {json.loads(l)["problem_id"]: json.loads(l)
        for l in open("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")}
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
items = [p for p in pool if tasks[p]["k"] > 1 and p in sa]

allv = np.concatenate([np.array(sa[p]) for p in items])
vals, counts = np.unique(np.round(allv, 3), return_counts=True)
pr = counts / counts.sum()
ties, margins = [], []
for pid in items:
    e = np.array(sa[pid])
    ties.append(len(np.where(e == e.max())[0]))
    o = np.array(pool[pid]["oracle"])
    refn = norm(pool[pid]["ref_answer"])
    ms, os_ = [], []
    for i, ok in enumerate(o):
        if not ok:
            continue
        a_ = norm(boxed(pool[pid]["samples"][i]) or pool[pid]["samples"][i])
        (ms if a_ == refn else os_).append(e[i])
    if ms and os_:
        margins.append(float(np.mean(ms) - np.mean(os_)))

res = dict(judge=JT, n_items=len(items),
           distinct_values=int(len(vals)),
           entropy_bits=round(float(-(pr * np.log2(pr)).sum()), 2),
           max_deviation_from_integer=round(float(np.abs(allv - np.round(allv)).max()), 6),
           mean_ties_at_max=round(float(np.mean(ties)), 1),
           anchoring_margin=round(float(np.mean(margins)), 2) if margins else None,
           threshold=dict(distinct_min=DISTINCT_MIN, ties_max=TIES_MAX))
res["P_MS1_pass"] = bool(res["distinct_values"] >= DISTINCT_MIN
                         and res["mean_ties_at_max"] <= TIES_MAX)
res["P_MS2_margin_exceeds_mistral7b"] = (
    bool(res["anchoring_margin"] > 1.38) if res["anchoring_margin"] is not None else None)

for k, v in res.items():
    print(f"  {k}: {v}")
print(f"\nSCREEN VERDICT: {'PASS' if res['P_MS1_pass'] else 'FAIL'} "
      f"(P-MS1); P-MS2 {'confirmed' if res['P_MS2_margin_exceeds_mistral7b'] else 'not confirmed'}")
json.dump(res, open("../../papers/analysis/ministral_screen.json", "w"), indent=1)
