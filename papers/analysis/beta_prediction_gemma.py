# Held-out test of the composition-model beta ordering (staged addition, NOT folded into the
# current submission; see registration.md entry committed with this file).
# INTERNAL REGISTRATION: this header and its prediction are committed BEFORE this script is run
# on gemma's scores; the commit timestamp is the registration. Same convention as
# exploit_lure2d.py, whose fit() this file reuses verbatim (import, not copy-paste) on a
# judge/pool slice that script never saw.
#
# Motivation. exploit_lure2d.py already fit, on Qwen-7B and phi-4 only (kstrat+repl pools,
# zero new judging), a selection model ref_escore ~ beta*blind_escore + c_mv*[matching-valid]
# + c_nv*[nonmatching-valid] + gamma*[lure-invalid]. Frozen result (exploit_lure2d.json):
#   beta: Qwen-7B  a=0.510  b=0.436
#         phi-4    a=0.690  b=0.682
# beta measures how much a judge's raw single-reference score still tracks its OWN blind
# read of quality, as opposed to being pulled onto the match/lure bonuses. Separately, the
# M1-variant decomposition (m1_variants_analysis.py / m1_variants_gemma_analysis.py, a
# different pool and a different manipulation: which anchor NUMBER a blind-then-reveal judge
# is shown) found the identical own-vs-other-anchor contrast (m1indep - m1prev) is
# indistinguishable from zero for phi-4 (+0.003 [-0.095,+0.091], the tightest interval of the
# three) and for Qwen-7B (-0.149 [-0.401,+0.062], CI still crosses zero but the point estimate
# is larger), while it is the only one of the three to clear zero for gemma-2-9b (+0.171
# [+0.007,+0.380], P-GV3 falsified). That ordering (phi-4 least identity-sensitive, Qwen more,
# gemma most) is the same order as ASCENDING match-bonus reliance and DESCENDING beta above.
#
# This file fits the SAME beta model on gemma-2-9b-it, using data neither exploit_lure2d.py
# nor its beta numbers ever touched (gemma's noref/ref kstrat scores, which post-date the
# composition-factorial commit) as a genuine held-out check of whether beta continues to order
# the same way, not a refit that includes the judge the prediction is about.
#
# Data available: gemma has synthk__google__gemma-2-9b-it__{noref,ref}_{a,b}.jsonl on the
# kstrat pool ONLY (no repl-pool gemma scores exist), so eligibility is scored against kstrat
# alone; fewer eligible items than the original 24-item (kstrat+repl) fit, disclosed below
# rather than padded.
#
# REGISTERED PREDICTION (committed before this script has been run on gemma; no peeking):
#   P-BG1: gemma-2-9b-it's fitted beta (rubric a) is LOWER than both Qwen-7B's (0.510) and
#     phi-4's (0.690) rubric-a values, i.e. beta_gemma_a < 0.510. Scored on the point
#     estimate; the item-bootstrap CI is reported alongside but the comparison judges are
#     themselves point estimates from a separate frozen fit, so this is a single-sided
#     descriptive comparison, not a two-sample test. Rubric b is exploratory (same
#     direction expected: beta_gemma_b < 0.436).
#   Status of this file's role in the paper: NOT added to the submitted manuscript. Staged
#   per an explicit user decision (2026-09-12) to keep the beta compression term at its
#   current descriptive framing for this submission round, following a prior AC reviewer's
#   explicit recommendation not to elevate it pre-acceptance. This experiment is run so the
#   result is ready for a future revision, not to change the current draft.
#
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/beta_prediction_gemma.py
# Writes ../../papers/analysis/beta_prediction_gemma.json
import json

import numpy as np

NBOOT = 1000
rng = np.random.default_rng(0)
JUDGE = "google__gemma-2-9b-it"
POOL_F = "runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl"
SDIR = "runs/bon_scores_kstrat"


def norm(a):
    import re
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


def load_scores(judge, cond, rep):
    path = f"{SDIR}/synthk__{judge}__{cond}_{rep}.jsonl"
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(path))}


pool = [json.loads(l) for l in open(POOL_F)]
scores = {(JUDGE, c, r): load_scores(JUDGE, c, r) for c in ("noref", "ref") for r in ("a", "b")}

items = []
for it in pool:
    if it.get("k") == 1:
        continue
    refn = norm(it["ref_answer"])
    refstr = it["ref_answer"].strip()
    mv, nv, lure, clean = [], [], [], []
    for i, (s, ok) in enumerate(zip(it["samples"], it["oracle"])):
        if not ok:
            (lure if refstr in s else clean).append(i)
        elif norm(extract_boxed(s) or s) == refn:
            mv.append(i)
        else:
            nv.append(i)
    if len(mv) < 4 or len(nv) < 4 or len(lure) < 6 or len(clean) < 10:
        continue
    items.append(dict(it=it, mv=mv, nv=nv, lure=lure, clean=clean))

print(f"[beta_prediction_gemma] eligible kstrat-only items: {len(items)} "
      f"(exploit_lure2d.py's Qwen/phi-4 fit used 24 eligible kstrat+repl items)")
if not items:
    raise SystemExit("no eligible items; nothing to fit")


def design_rows(x, rep):
    it = x["it"]
    pid = it["problem_id"]
    blind = np.asarray(scores[(JUDGE, "noref", rep)][pid], float)
    refsc = np.asarray(scores[(JUDGE, "ref", rep)][pid], float)
    n = len(refsc)
    f_mv = np.zeros(n); f_nv = np.zeros(n); f_lu = np.zeros(n)
    f_mv[x["mv"]] = 1; f_nv[x["nv"]] = 1; f_lu[x["lure"]] = 1
    X = np.column_stack([blind, f_mv, f_nv, f_lu])
    Xd = X - X.mean(axis=0)
    yd = refsc - refsc.mean()
    return Xd, yd


def fit(rows_idx, rep):
    Xs = np.vstack([design_rows(items[i], rep)[0] for i in rows_idx])
    ys = np.concatenate([design_rows(items[i], rep)[1] for i in rows_idx])
    coef, *_ = np.linalg.lstsq(Xs, ys, rcond=None)
    return coef  # beta, c_mv, c_nv, gamma


REF_BETA = {"a": {"Qwen-7B": 0.5095130690860934, "phi-4": 0.6901658548504167},
            "b": {"Qwen-7B": 0.43634331905709234, "phi-4": 0.6815624026467312}}

out = {"n_items": len(items), "rubric": {}}
for rep in ("a", "b"):
    full = fit(range(len(items)), rep)
    betas = []
    for _ in range(NBOOT):
        bs = rng.integers(0, len(items), len(items))
        betas.append(float(fit(bs, rep)[0]))
    beta = float(full[0])
    ci = [float(np.percentile(betas, 2.5)), float(np.percentile(betas, 97.5))]
    lam = float(full[1] - full[2])
    out["rubric"][rep] = dict(beta=beta, beta_ci=ci, c_mv=float(full[1]), c_nv=float(full[2]),
                              lam=lam, gamma=float(full[3]),
                              lower_than_qwen=bool(beta < REF_BETA[rep]["Qwen-7B"]),
                              lower_than_phi4=bool(beta < REF_BETA[rep]["phi-4"]))

out["P_BG1"] = bool(out["rubric"]["a"]["beta"] < REF_BETA["a"]["Qwen-7B"])
json.dump(out, open("../../papers/analysis/beta_prediction_gemma.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print(f"\nP-BG1 (gemma beta_a {out['rubric']['a']['beta']:.3f} < Qwen-7B beta_a "
      f"{REF_BETA['a']['Qwen-7B']:.3f}): {'CONFIRMED' if out['P_BG1'] else 'FALSIFIED'}")
