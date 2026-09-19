# POST-HOC EXTENSION of the frozen replrot_analysis.py (P-RR1..P-RR3 were registered for
# Qwen2.5-7B and phi-4 ONLY). Sonnet 5 and Qwen2.5-14B are added here AFTER seeing data;
# their rows carry no registration weight. Functions are byte-identical to the frozen file.
# FROZEN analysis for the fresh exact-oracle rotation replication (P-RR1..P-RR3).
# INTERNAL REGISTRATION: committed together with scripts/build_replrot_pool.py BEFORE any
# rotated judging runs; the commit timestamp is the registration.
#
# Why. Paper D's P1 rotation (the causal centerpiece) inherits the exploratory Ties pool,
# whose enumerated-set checker is known to be substantially incomplete. External review
# (2026-09-07) named a fresh rotation replication on an exact-oracle pool the single
# highest-value confirmatory run. This is that run, on the externally-registered
# replication pool (120 items, five constraint families, exact programmatic oracles,
# stored full valid sets, Llama-3.1-8B generator, cross-family judges).
#
# Design (pinned).
#   - Pool: runs/bon/bon_replrot__...jsonl (identical samples/oracle to the frozen
#     replication pool; ref_answer rotated by the pinned pool-aware rule; rot_from carries
#     the original reference). Original-reference scores: runs/bon_scores_repl/
#     synthk__{judge}__ref_{a,b}.jsonl (frozen). Rotated scores: runs/bon_scores_replrot/
#     synthk__{judge}__ref_{a,b}.jsonl (new). Blind: runs/bon_scores_repl/
#     synthk__{judge}__noref_{a,b}.jsonl (frozen; reference-independent).
#   - Judges: Qwen2.5-7B-Instruct and microsoft/phi-4; rubrics a and b scored separately.
#   - Sample classes per item (loose-normalized boxed answer, fallback whole reply,
#     identical to exploit_dose.py): GAINER = oracle-valid, answer == rotated reference;
#     LOSER = oracle-valid, answer == original reference; PLACEBO = oracle-valid, answer
#     equals neither. Items in the fallback set (no valid non-matching answer in pool, per
#     build_replrot_pool.py) contribute no gainers by construction and are excluded from
#     the gainer contrast only.
#   - Readout: same-sample delta = rotated-ref escore minus original-ref escore for the
#     IDENTICAL sample text. Per-item means, item-level cluster bootstrap (NBOOT = 1000,
#     numpy default_rng(0)) for all CIs.
#
# REGISTERED PREDICTIONS (committed before the rotated judging exists):
#   P-RR1 (gainers): mean same-sample delta of GAINERS is positive with 95% CI excluding
#     zero, for BOTH judges on BOTH rubrics (4/4 cells).
#   P-RR2 (losers): mean same-sample delta of LOSERS is negative with CI excluding zero,
#     for both judges on both rubrics.
#   P-RR3 (specificity): the gainer-minus-placebo contrast (per-item paired where both
#     classes exist) is positive with CI excluding zero, for both judges on both rubrics.
#   Exploratory (no registration weight): placebo levels, blind-margin comparison,
#   selection-collapse counts, per-family splits.
#
# Run from experiments/tfa-vs-judge after the rotated judging completes.
import json
import os
import re

import numpy as np

NBOOT = 1000
rng = np.random.default_rng(0)
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4", "anthropic__claude-sonnet-5", "Qwen__Qwen2.5-14B-Instruct", "google__gemma-2-9b-it"]  # POST HOC: two judges added after the registration
POOL_F = "runs/bon/bon_replrot__meta-llama__Llama-3.1-8B-Instruct.jsonl"
ORIG_DIR, ROT_DIR = "runs/bon_scores_repl", "runs/bon_scores_replrot"


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


def load(sdir, judge, cond, rep):
    f = f"{sdir}/synthk__{judge}__{cond}_{rep}.jsonl"
    if not os.path.exists(f):
        return None
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))}


pool = [json.loads(l) for l in open(POOL_F)]
need = [(j, rep) for j in JUDGES for rep in ("a", "b")]
if any(load(ROT_DIR, j, "ref", rep) is None for j, rep in need):
    print("[replrot_analysis] pre-data: rotated score files not all present. Nothing written.")
    raise SystemExit


def cluster_ci(per_item):
    v = np.asarray(per_item, float)
    boots = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(NBOOT)]
    return float(v.mean()), [float(np.percentile(boots, 2.5)),
                             float(np.percentile(boots, 97.5))], len(v)


res = {}
md = ["| judge | rubric | gainers [CI] (n items) | losers [CI] | placebo [CI] | "
      "gainer-minus-placebo [CI] |", "|---|---|---|---|---|---|"]
for j in JUDGES:
    for rep in ("a", "b"):
        orig = load(ORIG_DIR, j, "ref", rep)
        rot = load(ROT_DIR, j, "ref", rep)
        g_items, l_items, p_items, gp_items = [], [], [], []
        for it in pool:
            pid = it["problem_id"]
            if pid not in orig or pid not in rot:
                continue
            rotn, orign = norm(it["ref_answer"]), norm(it["rot_from"])
            g, lo, pl = [], [], []
            for i, (s, ok) in enumerate(zip(it["samples"], it["oracle"])):
                if not ok:
                    continue
                b = norm(extract_boxed(s) or s)
                d = rot[pid][i] - orig[pid][i]
                if b == rotn:
                    g.append(d)
                elif b == orign:
                    lo.append(d)
                else:
                    pl.append(d)
            if g:
                g_items.append(float(np.mean(g)))
            if lo:
                l_items.append(float(np.mean(lo)))
            if pl:
                p_items.append(float(np.mean(pl)))
            if g and pl:
                gp_items.append(float(np.mean(g)) - float(np.mean(pl)))
        gm, gci, gn = cluster_ci(g_items)
        lm, lci, ln = cluster_ci(l_items)
        pm, pci, pn = cluster_ci(p_items)
        gpm, gpci, gpn = cluster_ci(gp_items)
        res[f"{j}__{rep}"] = dict(
            gainers=dict(mean=gm, ci=gci, n_items=gn),
            losers=dict(mean=lm, ci=lci, n_items=ln),
            placebo=dict(mean=pm, ci=pci, n_items=pn),
            gainer_minus_placebo=dict(mean=gpm, ci=gpci, n_items=gpn),
            P_RR1=bool(gci[0] > 0), P_RR2=bool(lci[1] < 0), P_RR3=bool(gpci[0] > 0))
        md.append(f"| {j} | {rep} | {gm:+.2f} [{gci[0]:+.2f},{gci[1]:+.2f}] ({gn}) | "
                  f"{lm:+.2f} [{lci[0]:+.2f},{lci[1]:+.2f}] ({ln}) | "
                  f"{pm:+.2f} [{pci[0]:+.2f},{pci[1]:+.2f}] ({pn}) | "
                  f"{gpm:+.2f} [{gpci[0]:+.2f},{gpci[1]:+.2f}] ({gpn}) |")

cells = [res[k] for k in res]
verdict = dict(
    P_RR1_all4=all(c["P_RR1"] for c in cells),
    P_RR2_all4=all(c["P_RR2"] for c in cells),
    P_RR3_all4=all(c["P_RR3"] for c in cells))
res["verdicts"] = verdict
json.dump(res, open("../../papers/analysis/replrot_POSTHOC_results.json"
                    if os.path.exists("../../papers/analysis") else "replrot_POSTHOC_results.json",
                    "w"), indent=1)
print("\n".join(md))
print("verdicts:", verdict)
