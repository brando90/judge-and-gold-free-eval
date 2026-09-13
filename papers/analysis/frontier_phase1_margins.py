# FROZEN analysis for the frontier-judge Phase 1 extension (P-FM1..P-FM4): margin readouts for a
# sampled-integer frontier judge (Claude Sonnet 5 via the Messages API; no logprobs, so NO inflation).
# INTERNAL REGISTRATION: committed BEFORE any Phase 1 batch is submitted; the commit timestamp is
# the registration. Registered design and predictions: papers/D-reference-laws/registration.md,
# "frontier-judge extension" entry of 2026-09-07.
#
# Definitions are copied from the open-judge producers and applied to score files that may hold
# null for samples not judged (--valid-only): a null sample is skipped wherever the original
# producer would have used it; every readout here uses oracle-valid samples only, exactly as the
# originals do, so nothing is lost by judging valid samples only.
#   P-FM1 rotation (mirror of replrot_analysis.py): on the exact-oracle replication pool, same-sample
#         delta = rotated-reference score minus original-reference score; gainers = valid samples
#         matching the rotated reference, losers = matching the original, placebo = matching neither;
#         item means, item bootstrap. Predictions: gainers > 0 and losers < 0 with CIs excluding
#         zero, gainer-minus-placebo > 0, each rubric.
#   P-FM2 masking (mirror of maskident_analysis.py margins_for): anchoring margin on the replication
#         pool, matching defined against the ORIGINAL numeral reference, for bare reference, blind,
#         reference-as-words, reference-as-expression. Predictions: words margin > 0 (CI excluding
#         zero); expression-minus-bare paired difference < 0 (CI excluding zero).
#   P-FM3 MACE (mirror of mace_analysis.py P-MC2): k>1 anchoring margin, non-math (River+Language)
#         and Math, referenced and blind. Predictions: referenced non-math margin > 0 (CI excluding
#         zero); blind non-math margin CI contains zero.
#   P-FM4 blind-certified (mirror of anchor_vs_weakness.py, bar 7.0 on the mean of the two blind
#         rubrics): P-FM1 recomputed on samples the judge itself blindly scored >= 7. Prediction:
#         gainer and loser CIs still exclude zero, each rubric; retention reported.
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/frontier_phase1_margins.py [judge_tag]
import json
import os
import re
import sys

import numpy as np

import hashlib
def _rng_for(tag):
    # Per-judge, order-independent seed: analyzing multiple judges in one run must not
    # perturb any single judge's bootstrap draws (found 2026-09-12: a shared global rng
    # consumed across judges in list order shifted CI bounds by ~0.01-0.04 depending on
    # which other judges were passed; point estimates were unaffected, but this makes
    # every number exactly reproducible regardless of invocation order).
    return np.random.default_rng(int(hashlib.sha256(tag.encode()).hexdigest(), 16) % (2**32))
rng = None  # set below, once JUDGE is known
NBOOT = 1000
JUDGE = sys.argv[1] if len(sys.argv) > 1 else "anthropic__claude-sonnet-5"
rng = _rng_for(JUDGE)
BAR = 7.0


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


def load(path):
    if not os.path.exists(path):
        return None
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(path))}


def ci(vals):
    v = np.asarray(vals, float)
    if len(v) == 0:
        return dict(mean=None, ci=None, n_items=0)
    boots = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(NBOOT)]
    return dict(mean=round(float(v.mean()), 3), ci=[round(float(np.percentile(boots, 2.5)), 3),
                                                  round(float(np.percentile(boots, 97.5)), 3)], n_items=len(v))


def rows(path):
    return [json.loads(l) for l in open(path)]


out = dict(judge=JUDGE)
repl = rows("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl")
S = lambda d, cond, rep: load(f"{d}/synthk__{JUDGE}__{cond}_{rep}.jsonl")

# ---------------------------------------------------------------- P-FM1 rotation (+ P-FM4 filter)
rot_pool = rows("runs/bon/bon_replrot__meta-llama__Llama-3.1-8B-Instruct.jsonl")
blind = {rep: S("runs/bon_scores_repl", "noref", rep) for rep in ("a", "b")}
for rep in ("a", "b"):
    orig, rot = S("runs/bon_scores_repl", "ref", rep), S("runs/bon_scores_replrot", "ref", rep)
    if orig is None or rot is None:
        out[f"rotation__{rep}"] = "score files missing"
        continue
    for filt in (False, True):
        g_items, l_items, p_items, gp_items, kept, seen = [], [], [], [], 0, 0
        for it in rot_pool:
            pid = it["problem_id"]
            if pid not in orig or pid not in rot:
                continue
            rotn, orign = norm(it["ref_answer"]), norm(it["rot_from"])
            g, lo, pl = [], [], []
            for i, (s, ok) in enumerate(zip(it["samples"], it["oracle"])):
                if not ok or orig[pid][i] is None or rot[pid][i] is None:
                    continue
                seen += 1
                if filt:
                    ba, bb = blind["a"], blind["b"]
                    if ba is None or bb is None or ba[pid][i] is None or bb[pid][i] is None:
                        continue
                    if (ba[pid][i] + bb[pid][i]) / 2 < BAR:
                        continue
                kept += 1
                b = norm(boxed(s) or s)
                d = rot[pid][i] - orig[pid][i]
                (g if b == rotn else lo if b == orign else pl).append(d)
            if g:
                g_items.append(float(np.mean(g)))
            if lo:
                l_items.append(float(np.mean(lo)))
            if pl:
                p_items.append(float(np.mean(pl)))
            if g and pl:
                gp_items.append(float(np.mean(g)) - float(np.mean(pl)))
        G, L, P, GP = ci(g_items), ci(l_items), ci(p_items), ci(gp_items)
        key = f"rotation_filtered__{rep}" if filt else f"rotation__{rep}"
        out[key] = dict(gainers=G, losers=L, placebo=P, gainer_minus_placebo=GP,
                        retained=(f"{kept}/{seen}" if filt else None),
                        pred_gainers=bool(G["ci"] and G["ci"][0] > 0),
                        pred_losers=bool(L["ci"] and L["ci"][1] < 0),
                        pred_specificity=bool(GP["ci"] and GP["ci"][0] > 0))

# ---------------------------------------------------------------- P-FM2 masking margins
def margins_for(pool_rows, sc):
    m = {}
    for it in pool_rows:
        pid = it["problem_id"]
        if sc is None or pid not in sc:
            continue
        refn = norm(it["ref_answer"])
        ms, others = [], []
        for i, ok in enumerate(it["oracle"]):
            if not ok or sc[pid][i] is None:
                continue
            a = norm(boxed(it["samples"][i]) or it["samples"][i])
            (ms if a == refn else others).append(sc[pid][i])
        if ms and others:
            m[pid] = float(np.mean(ms) - np.mean(others))
    return m


for rep in ("a", "b"):
    conds = dict(bare=margins_for(repl, S("runs/bon_scores_repl", "ref", rep)),
                 blind=margins_for(repl, S("runs/bon_scores_repl", "noref", rep)),
                 words=margins_for(repl, S("runs/bon_scores_refword", "ref", rep)),
                 expr=margins_for(repl, S("runs/bon_scores_refexpr", "ref", rep)))
    res = {c: ci(list(m.values())) for c, m in conds.items()}
    for c in ("words", "expr"):
        shared = sorted(set(conds[c]) & set(conds["bare"]))
        res[f"{c}_minus_bare"] = ci([conds[c][p] - conds["bare"][p] for p in shared])
    res["pred_words_positive"] = bool(res["words"]["ci"] and res["words"]["ci"][0] > 0)
    res["pred_expr_below_bare"] = bool(res["expr_minus_bare"]["ci"] and res["expr_minus_bare"]["ci"][1] < 0)
    out[f"masking__{rep}"] = res

# ---------------------------------------------------------------- P-FM3 MACE k>1 margins
mtasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/mace_tasks.jsonl")}
mace = []
for r in rows("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    if "oracle" not in r:
        continue
    t = mtasks[r["problem_id"]]
    r["k"], r["domain"], r["ref_answer"] = t["k"], t["params"]["domain"], t["ref_answer"]
    mace.append(r)
groups = dict(nonmath=lambda d: d in ("River", "Language"), math=lambda d: d == "Math")
for cond in ("ref", "noref"):
    sa = load(f"runs/bon_scores_mace/mace__{JUDGE}__{cond}_a.jsonl")
    if sa is None:
        out[f"mace__{cond}"] = "score files missing"
        continue
    for gname, gf in groups.items():
        vals = []
        for it in mace:
            pid = it["problem_id"]
            if it["k"] <= 1 or pid not in sa or not gf(it["domain"]):
                continue
            refn = norm(it["ref_answer"])
            ms, os_ = [], []
            for i, ok in enumerate(it["oracle"]):
                if not ok or sa[pid][i] is None:
                    continue
                a = norm(boxed(it["samples"][i]) or it["samples"][i][-200:])
                (ms if (a == refn or (len(refn) > 3 and refn in a)) else os_).append(sa[pid][i])
            if ms and os_:
                vals.append(float(np.mean(ms) - np.mean(os_)))
        out[f"mace__{cond}_{gname}"] = ci(vals)
if isinstance(out.get("mace__ref_nonmath"), dict) and isinstance(out.get("mace__noref_nonmath"), dict):
    out["mace_pred"] = dict(ref_positive=bool(out["mace__ref_nonmath"]["ci"] and out["mace__ref_nonmath"]["ci"][0] > 0),
                            blind_null=bool(out["mace__noref_nonmath"]["ci"] and
                                            out["mace__noref_nonmath"]["ci"][0] <= 0 <= out["mace__noref_nonmath"]["ci"][1]))

json.dump(out, open("../../papers/analysis/frontier_phase1_results.json", "w"), indent=1)
for k, v in out.items():
    print(k, json.dumps(v) if not isinstance(v, str) else v)
