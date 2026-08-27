# Similarity-vs-correctness 2x2 — frozen analysis producer (Paper D follow-up).
# INTERNAL REGISTRATION: this header pins the design, estimators, and predictions, and this
# file is git-committed BEFORE any judge scores exist (the commit timestamp is the
# registration). No OSF post per current hold; predictions P-SC1/P-SC2 below. NO JUDGING HAS
# BEEN RUN when this file is committed; it exits cleanly until score files appear.
#
# Motivation. Paper D shows reference anchoring inflates best-of-n on multi-valid tasks, and
# its rotation experiment shows the flips follow the reference ANSWER string. This experiment
# fully crosses similarity-to-the-reference with correctness to ask the adversarial headline
# question: can showing the reference make a judge prefer a WRONG but reference-like solution
# over a RIGHT but different one?
#
# Design (pinned):
#   - Tasks: runs/simcorr_tasks.jsonl — 40 items (8 per constraint family) built
#     deterministically by scripts/build_simcorr_candidates.py from the frozen replication
#     pool; per item four templated candidates in FIXED order
#       [valid_near, valid_far, invalid_near, invalid_far] = [A, B, C, D]
#     A = correct + reference-style route; B = correct per oracle, different valid answer and
#     visibly different route; C = reference-style route with exactly one substantive slip
#     (fails the oracle); D = wrong and structurally unrelated. Oracle verdicts [1,1,0,0] by
#     construction; candidate lengths within a 1.6x band.
#   - Judging: bon_judge.py machinery unchanged (escore = logprob-expected value over score
#     tokens 0..10; RUBRIC_TIES; conditions noref (blind) / ref; rubric paraphrases a/b).
#     Score files expected at runs/bon_scores_simcorr/simcorr__{judge}__{cond}_{rep}.jsonl
#     with rows {problem_id, escore: [4 scores in candidate order]} (rename or extend
#     bon_judge's domain tag to "simcorr" at run time; the frozen rubric text is unchanged).
#   - Optional pairwise files: runs/bon_scores_simcorr/simcorrpair__{judge}__{cond}_{rep}.jsonl
#     rows {problem_id, pref_bc, pref_cb}, values in {"B", "C", "tie"}; pref_bc = the choice
#     when B is shown first, pref_cb = the choice with the order reversed.
# Estimators (pinned):
#   - Rubric b is the reporting rubric (primary); rubric a is reported as robustness.
#   - Per-candidate readout: mean score per candidate type by condition, and the per-type
#     referenced-minus-blind delta with item-level bootstrap CI.
#   - PRIMARY ENDPOINT: P(score(C) > score(B)) per condition, per-item indicator with ties
#     scored 0.5; the registered contrast is the per-item PAIRED difference, referenced minus
#     blind. All CIs: item-level bootstrap, NBOOT = 1000, rng = numpy default_rng(0).
#   - P-SC2 endpoint: per-item (ref - blind) score delta of B minus the same delta of A.
#   - Pairwise (if files exist): P(prefer C) with tie = 0.5, averaged over the two orders;
#     order-reversal consistency = fraction of items where both orders pick the same letter;
#     paired referenced-minus-blind difference with CI.
#
# REGISTERED PREDICTIONS (committed before running):
#   P-SC1: the referenced condition RAISES P(score(C) > score(B)) relative to blind — the
#     per-item paired difference (ref minus blind, rubric b) is positive with a 95% item-level
#     bootstrap CI excluding zero, for each judge run.
#   P-SC2: valid-far B suffers a referenced-minus-blind score penalty relative to valid-near
#     A — the per-item (ref-blind) delta of B minus that of A is negative with a 95% CI
#     excluding zero, for each judge run.
#   Interpretation pinned in advance: a NULL on P-SC1 is an informative bound, not a failed
#   experiment — it means anchoring does NOT override validity (the judge does not come to
#   prefer a wrong-but-reference-like solution over a right-but-different one), confining
#   Paper D's measured harm to selection among valid answers. Everything beyond P-SC1/P-SC2
#   (per-family splits, rubric-a numbers, invalid_far levels, pairwise magnitudes) is
#   exploratory.
#
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/simcorr_analysis.py
# Writes ../../papers/analysis/simcorr_results.json and prints a markdown summary.
# Exits cleanly (code 0, no JSON written) while runs/bon_scores_simcorr/ has no data.
import glob
import json
import os
import re

import numpy as np

SDIR = "runs/bon_scores_simcorr"
TASKS = "runs/simcorr_tasks.jsonl"
TYPES = ["valid_near", "valid_far", "invalid_near", "invalid_far"]
A, B, C, D = 0, 1, 2, 3
NBOOT = 1000
rng = np.random.default_rng(0)

if not os.path.isdir(SDIR):
    print(f"[simcorr] {SDIR} not found — no judge scores exist yet. This producer is "
          f"committed pre-data (internal registration); run the simcorr judging first, "
          f"then re-run this script.")
    raise SystemExit(0)
files = sorted(glob.glob(f"{SDIR}/simcorr__*.jsonl"))
if not files:
    print(f"[simcorr] no simcorr__* score files in {SDIR} yet — nothing to analyze.")
    raise SystemExit(0)

judges = sorted({m.group(1) for m in
                 (re.match(r"simcorr__(.+)__(noref|ref)_([ab])\.jsonl", os.path.basename(f))
                  for f in files) if m})


def load(prefix, judge, cond, rep):
    path = f"{SDIR}/{prefix}__{judge}__{cond}_{rep}.jsonl"
    if not os.path.exists(path):
        return None
    return {r["problem_id"]: r for r in (json.loads(l) for l in open(path))}


def ci(vals):
    vals = np.asarray(vals, float)
    boots = [np.mean(vals[rng.integers(0, len(vals), len(vals))]) for _ in range(NBOOT)]
    return float(vals.mean()), [float(np.percentile(boots, 2.5)),
                                float(np.percentile(boots, 97.5))]


def mci(vals):
    m, c = ci(vals)
    return dict(mean=m, ci=c)


def pcb(e):
    # P(C beats B) indicator, tie = 0.5
    return 1.0 if e[C] > e[B] else 0.5 if e[C] == e[B] else 0.0


def prefc(v):
    return {"C": 1.0, "tie": 0.5, "B": 0.0}[v]


ntasks = sum(1 for _ in open(TASKS)) if os.path.exists(TASKS) else None
out = dict(design=dict(types=TYPES, primary_rep="b", NBOOT=NBOOT, tie_value=0.5,
                       n_tasks=ntasks), judges={})
md = ["| judge | rep | P(C>B) blind | P(C>B) ref | paired diff [95% CI] (P-SC1) | "
      "dB-dA [95% CI] (P-SC2) |", "|---|---|---|---|---|---|"]

for j in judges:
    jout = {}
    for rep in ("b", "a"):
        blind = load("simcorr", j, "noref", rep)
        refd = load("simcorr", j, "ref", rep)
        if not (blind and refd):
            if rep == "b":
                print(f"[simcorr] {j}: rep-b noref/ref files incomplete — skipping judge")
            continue
        its = sorted(set(blind) & set(refd))
        eb = np.asarray([blind[i]["escore"] for i in its], float)
        er = np.asarray([refd[i]["escore"] for i in its], float)
        means = {cond: {TYPES[t]: float(m[:, t].mean()) for t in range(4)}
                 for cond, m in (("blind", eb), ("ref", er))}
        deltas = {TYPES[t]: mci(er[:, t] - eb[:, t]) for t in range(4)}
        pb = np.asarray([pcb(e) for e in eb])
        pr = np.asarray([pcb(e) for e in er])
        d1 = mci(pr - pb)
        d2 = mci((er[:, B] - eb[:, B]) - (er[:, A] - eb[:, A]))
        jout[f"rep_{rep}"] = dict(
            n_items=len(its), means=means, ref_minus_blind=deltas,
            p_c_beats_b=dict(blind=mci(pb), ref=mci(pr), paired_diff=d1),
            psc2_deltaB_minus_deltaA=d2)
        if rep == "b":
            jout["verdicts"] = dict(
                P_SC1=dict(supported=bool(d1["ci"][0] > 0), **d1),
                P_SC2=dict(supported=bool(d2["ci"][1] < 0), **d2))
        md.append(f"| {j} | {rep} | {pb.mean():.3f} | {pr.mean():.3f} | "
                  f"{d1['mean']:+.3f} [{d1['ci'][0]:+.3f}, {d1['ci'][1]:+.3f}] | "
                  f"{d2['mean']:+.3f} [{d2['ci'][0]:+.3f}, {d2['ci'][1]:+.3f}] |")
    # pairwise B-vs-C files, if the pairwise arm was run
    pw = {}
    for cond in ("noref", "ref"):
        for rep in ("b", "a"):
            rows = load("simcorrpair", j, cond, rep)
            if not rows:
                continue
            its = sorted(rows)
            per = np.asarray([(prefc(rows[i]["pref_bc"]) + prefc(rows[i]["pref_cb"])) / 2
                              for i in its])
            cons = float(np.mean([rows[i]["pref_bc"] == rows[i]["pref_cb"] for i in its]))
            pw[f"{cond}_{rep}"] = dict(n_items=len(its), p_prefer_c=mci(per),
                                       order_consistency=cons)
    for rep in ("b", "a"):
        kb, kr = f"noref_{rep}", f"ref_{rep}"
        if kb in pw and kr in pw:
            rb = load("simcorrpair", j, "noref", rep)
            rr = load("simcorrpair", j, "ref", rep)
            its = sorted(set(rb) & set(rr))
            dd = np.asarray([(prefc(rr[i]["pref_bc"]) + prefc(rr[i]["pref_cb"])) / 2
                             - (prefc(rb[i]["pref_bc"]) + prefc(rb[i]["pref_cb"])) / 2
                             for i in its])
            pw[f"paired_diff_{rep}"] = mci(dd)
    if pw:
        jout["pairwise"] = pw
    if jout:
        out["judges"][j] = jout

if not out["judges"]:
    print("[simcorr] no judge with complete rep-b noref/ref files — nothing to analyze.")
    raise SystemExit(0)

json.dump(out, open("../../papers/analysis/simcorr_results.json", "w"), indent=1)
print("\n".join(md))
for j, jout in out["judges"].items():
    v = jout.get("verdicts", {})
    for pname, vv in v.items():
        print(f"[{j}] {pname}: {'SUPPORTED' if vv['supported'] else 'not supported'} "
              f"(mean {vv['mean']:+.3f}, CI [{vv['ci'][0]:+.3f}, {vv['ci'][1]:+.3f}])")
print("[simcorr] wrote ../../papers/analysis/simcorr_results.json")
