# FROZEN analysis for the recoverability-cost dose-response suite (P-RC1..P-RC4).
# INTERNAL REGISTRATION: committed together with scripts/build_recoverability_pool.py and
# the bon_judge.py cipher1/cipher2/cipher3 conditions BEFORE any variant judging runs; the
# commit timestamp is the registration.
#
# Question. The separability continuum (sep_continuum_analysis.py) showed a CLIFF between
# short-token answer strata and program -- but that is four qualitatively different artifact
# types, not a graded dose, and two reviewers independently flagged the artifact-level leg
# as underpowered and judge-dependent (phi-4: a genuine cliff, negative on program; Qwen-7B:
# a small positive residue). This experiment converts "is there a token or not" into "how
# expensive is it to extract one," holding the artifact type fixed (a boxed integer, exactly
# as in the bare replication-pool reference) and varying only how many reversible encoding
# steps stand between the judge and a checkable match: 0 (bare numeral, already scored),
# 1 (digit shift), 2 (+ base64), 3 (+ reversed). The decode rule is stated explicitly at
# every level (bon_judge.py's CIPHER_RULE), so a fading effect is read as attenuation with
# cost, not as the judge simply being unable to decode it (that all-or-nothing case is
# already covered by the existing masked-worked-ref condition in maskident_analysis.py).
#
# Estimator (identical to worked_ref_analysis E1 / maskident_analysis, unchanged): per-item
# anchoring margin = mean rubric-a escore of reference-matching valid samples minus mean
# escore of non-matching valid samples, "matching" ALWAYS defined against the item's
# ORIGINAL numeral reference (ref_answer_orig), never against the encoded string shown to
# the judge -- this is what lets the estimator stay identical across levels without needing
# to decode anything itself. Item-level bootstrap (NBOOT=1000, default_rng(0)). Rubric b
# replicates. Inflation (excess-gap dose at n=64, exploratory) mirrors sep_continuum_analysis
# via the frozen bon_analysis.py machinery (exec()'d, not modified).
#
# REGISTERED PREDICTIONS (committed before any cipher-condition judging exists; rubric a,
# scored per judge -- Qwen2.5-7B-Instruct, phi-4):
#   P-RC1 (harm survives one computational step): the cipher1 margin is positive with 95%
#     item-bootstrap CI excluding zero, for BOTH judges.
#   P-RC2 (a curve, not a single cliff): EACH successive paired per-item margin drop
#     (bare-cipher1, cipher1-cipher2, cipher2-cipher3) is positive with CI excluding zero,
#     for BOTH judges. A miss at any one step is reported as a miss at that step, not
#     rounded up to "the curve exists."
#   P-RC3 (attenuation is substantial by three steps): the cipher3 margin is below HALF the
#     bare margin (point estimate), for both judges, mirroring the paper's existing
#     half-margin bar for the masking suite's expression condition.
#   P-RC4 (inflation tracks margin): the paired referenced-minus-blind excess-gap dose at
#     n=64 is monotonically non-increasing across levels 0,1,2,3 (point estimates only) for
#     both judges. Exploratory -- no CI bar, reported as confirmed/falsified on ordering
#     alone, consistent with "everything else... exploratory" elsewhere in this ledger.
#
# Run from experiments/tfa-vs-judge after the cipher1/2/3 judging completes.
import json
import os

import numpy as np

NBOOT, NPERM = 1000, 50
rng = np.random.default_rng(0)
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
LEVELS = ["bare", "cipher1", "cipher2", "cipher3"]
COND = {"bare": "ref", "cipher1": "cipher1", "cipher2": "cipher2", "cipher3": "cipher3"}
POOL_F = {"bare": "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl",
          "cipher1": "runs/bon/bon_replcipher1__meta-llama__Llama-3.1-8B-Instruct.jsonl",
          "cipher2": "runs/bon/bon_replcipher2__meta-llama__Llama-3.1-8B-Instruct.jsonl",
          "cipher3": "runs/bon/bon_replcipher3__meta-llama__Llama-3.1-8B-Instruct.jsonl"}
SDIR = {"bare": "runs/bon_scores_repl", "cipher1": "runs/bon_scores_repl",
        "cipher2": "runs/bon_scores_repl", "cipher3": "runs/bon_scores_repl"}

sys_path_src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(sys_path_src, "bon_analysis", "exec"), ns)


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


import re


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def load(level, judge, cond, rep):
    pool_tag = os.path.basename(POOL_F[level]).split("__")[0].replace("bon_", "")
    f = f"{SDIR[level]}/{pool_tag}__{judge}__{cond}_{rep}.jsonl"
    if not os.path.exists(f):
        return None
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))}


def bci(vals):
    v = np.asarray(vals, float)
    boots = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(NBOOT)]
    return float(v.mean()), [float(np.percentile(boots, 2.5)),
                             float(np.percentile(boots, 97.5))], len(v)


pools = {lvl: {json.loads(l)["problem_id"]: json.loads(l) for l in open(POOL_F[lvl])}
         for lvl in LEVELS}

need = [(lvl, j, COND[lvl], r) for lvl in LEVELS for j in JUDGES for r in ("a", "b")]
missing = [x for x in need if load(*x) is None]
if missing:
    print(f"[recoverability_analysis] pre-data: {len(missing)} score files absent "
          f"(first: {missing[0]}). Nothing written.")
    raise SystemExit

res = {"margin": {}, "inflation": {}}
md = ["| judge | level | margin(a) [CI] (n) |", "|---|---|---|"]
for j in JUDGES:
    margins = {}
    for lvl in LEVELS:
        ca = load(lvl, j, COND[lvl], "a")
        pool = pools[lvl]
        m = {}
        for pid, it in pool.items():
            if pid not in ca:
                continue
            refn = norm(it["ref_answer_orig"] if lvl != "bare" else it["ref_answer"])
            ms, ot = [], []
            for i, ok in enumerate(it["oracle"]):
                if not ok:
                    continue
                a_ = norm(boxed(it["samples"][i]) or it["samples"][i])
                (ms if a_ == refn else ot).append(ca[pid][i])
            if ms and ot:
                m[pid] = float(np.mean(ms) - np.mean(ot))
        margins[lvl] = m
        mm, mc, mn = bci(list(m.values()))
        res["margin"][f"{j}|{lvl}"] = dict(mean=mm, ci=mc, n=mn)
        md.append(f"| {j} | {lvl} | {mm:+.3f} [{mc[0]:+.3f},{mc[1]:+.3f}] ({mn}) |")

    # registered successive-drop contrasts (paired per item)
    def drop(l1, l2):
        shared = sorted(set(margins[l1]) & set(margins[l2]))
        return bci([margins[l1][p] - margins[l2][p] for p in shared])

    d01 = drop("bare", "cipher1")
    d12 = drop("cipher1", "cipher2")
    d23 = drop("cipher2", "cipher3")
    res[f"{j}|drops"] = dict(bare_minus_c1=d01, c1_minus_c2=d12, c2_minus_c3=d23)
    res[f"{j}|verdicts"] = dict(
        P_RC1=bool(res["margin"][f"{j}|cipher1"]["ci"][0] > 0),
        P_RC2=dict(bare_c1=bool(d01[1][0] > 0), c1_c2=bool(d12[1][0] > 0),
                   c2_c3=bool(d23[1][0] > 0)),
        P_RC3=bool(res["margin"][f"{j}|cipher3"]["mean"] <
                   0.5 * res["margin"][f"{j}|bare"]["mean"]))

    # exploratory inflation dose (n=64 excess gap vs blind), point estimates only
    nb_a, nb_b = load("bare", j, "noref", "a"), load("bare", j, "noref", "b")
    infl = {}
    for lvl in LEVELS:
        ca, cb = load(lvl, j, COND[lvl], "a"), load(lvl, j, COND[lvl], "b")
        na = nb_a if lvl == "bare" else load(lvl, j, "noref", "a")
        nb = nb_b if lvl == "bare" else load(lvl, j, "noref", "b")
        if na is None or nb is None:
            infl[lvl] = None
            continue
        pool = pools[lvl]
        vals = []
        for pid, it in pool.items():
            if pid not in ca or pid not in na or not (0 < sum(it["oracle"]) < len(it["oracle"])):
                continue
            gr = ns["per_item_curves"](it, ca[pid], cb[pid])
            nr = ns["permutation_null"](it, ca[pid], cb[pid])
            gn = ns["per_item_curves"](it, na[pid], nb[pid])
            nn = ns["permutation_null"](it, na[pid], nb[pid])
            vals.append((gr[64]["judge_gain"] - gr[64]["true_gain"] - nr)
                        - (gn[64]["judge_gain"] - gn[64]["true_gain"] - nn))
        infl[lvl] = float(np.mean(vals)) if vals else None
    res["inflation"][j] = infl
    seq = [infl[l] for l in LEVELS if infl[l] is not None]
    res[f"{j}|verdicts"]["P_RC4"] = bool(all(seq[i] >= seq[i + 1] for i in range(len(seq) - 1)))
    md.append(f"| {j} | inflation dose | " + " -> ".join(
        f"{infl[l]:+.3f}" if infl[l] is not None else "NA" for l in LEVELS) + " | |")

json.dump(res, open("../../papers/analysis/recoverability_results.json"
                    if os.path.exists("../../papers/analysis") else "recoverability_results.json",
                    "w"), indent=1)
print("\n".join(md))
for j in JUDGES:
    print(j, res[f"{j}|verdicts"])
