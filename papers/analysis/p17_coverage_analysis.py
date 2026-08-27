# Scorer for Registration 5 (judge-coverage extension, pipeline17). The predictions
# P-X1..P-X4 and all estimators were registered externally BEFORE any of these judges ran
# (osf_drafts.md Registration 5; harness commit e75e465). This script applies the frozen
# estimators of mitigation_analysis.py, unchanged, to whichever new judges have complete
# score files, and scores the registered predictions:
#   P-X1: single-reference k>1 pooled delta vs blind positive, CI excluding zero, per judge.
#   P-X2: M1-minus-single-reference contrast at k>1 negative, CI excluding zero, per judge.
#   P-X3 (directional): |M1 delta vs blind| < |single-ref delta vs blind| at k>1.
#   P-X4 (exploratory): M2's per-judge behavior recorded, no confirmatory claim.
# P-X1/P-X2 are confirmed only if they hold for EVERY new judge that runs.
# Run from experiments/tfa-vs-judge after pulling runs/bon_scores_kstrat from the cluster.
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

NEW_JUDGES = ["google__gemma-2-9b-it", "mistralai__Mistral-7B-Instruct-v0.3",
              "Qwen__Qwen2.5-14B-Instruct", "01-ai__Yi-1.5-9B-Chat"]
CONDS = ["noref", "ref", "m1", "m2"]


def bci(vals, B=2000):
    v = np.asarray(vals, float)
    b = [float(np.mean(rng.choice(v, len(v)))) for _ in range(B)]
    return [round(float(np.percentile(b, 2.5)), 3), round(float(np.percentile(b, 97.5)), 3)]


tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
pool = {}
for l in open("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    r = json.loads(l)
    if "oracle" not in r:
        continue
    r["k"] = tasks[r["problem_id"]]["k"]
    pool[r["problem_id"]] = r


def scores(jtag, cond, rep):
    for pref in ("kstrat", "synthk"):
        f = f"runs/bon_scores_kstrat/{pref}__{jtag}__{cond}_{rep}.jsonl"
        if os.path.exists(f):
            return {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(f)}
    return None


out = {}
md = ["| judge | readout | value [95% CI] | verdict |", "|---|---|---|---|"]
ran = []
for jtag in NEW_JUDGES:
    have = all(scores(jtag, c, r) is not None for c in CONDS for r in ("a", "b"))
    if not have:
        print(f"[skip] {jtag}: incomplete score files")
        continue
    ran.append(jtag)
    per_cond = {}
    for cond in CONDS:
        sa, sb = scores(jtag, cond, "a"), scores(jtag, cond, "b")
        g = {}
        for pid, it in pool.items():
            if pid not in sa:
                continue
            pr = float(np.mean(it["oracle"]))
            if not (0.05 <= pr <= 0.95):
                continue
            c = ns["per_item_curves"](it, sa[pid], sb[pid])
            nl = ns["permutation_null"](it, sa[pid], sb[pid])
            g[pid] = c[64]["judge_gain"] - c[64]["true_gain"] - nl
        per_cond[cond] = g
    j = {}
    kg = lambda cond, kf: [per_cond[cond][p] - per_cond["noref"][p]
                           for p in per_cond[cond] if p in per_cond["noref"] and kf(pool[p]["k"])]
    ref_gt1 = kg("ref", lambda k: k > 1)
    m1_gt1 = kg("m1", lambda k: k > 1)
    m2_gt1 = kg("m2", lambda k: k > 1)
    ref_k1 = kg("ref", lambda k: k == 1)
    m1_k1 = kg("m1", lambda k: k == 1)
    contrast = [per_cond["m1"][p] - per_cond["ref"][p]
                for p in per_cond["m1"] if p in per_cond["ref"] and pool[p]["k"] > 1]
    j["ref_kgt1"] = dict(delta=round(float(np.mean(ref_gt1)), 3), ci=bci(ref_gt1), n=len(ref_gt1))
    j["m1_kgt1"] = dict(delta=round(float(np.mean(m1_gt1)), 3), ci=bci(m1_gt1), n=len(m1_gt1))
    j["m2_kgt1"] = dict(delta=round(float(np.mean(m2_gt1)), 3), ci=bci(m2_gt1), n=len(m2_gt1))
    j["ref_k1"] = dict(delta=round(float(np.mean(ref_k1)), 3), ci=bci(ref_k1), n=len(ref_k1))
    j["m1_k1"] = dict(delta=round(float(np.mean(m1_k1)), 3), ci=bci(m1_k1), n=len(m1_k1))
    j["m1_minus_ref_kgt1"] = dict(delta=round(float(np.mean(contrast)), 3), ci=bci(contrast),
                                  n=len(contrast))
    j["step"] = dict(delta=round(float(np.mean(ref_gt1) - np.mean(ref_k1)), 3))
    px1 = j["ref_kgt1"]["ci"][0] > 0
    px2 = j["m1_minus_ref_kgt1"]["ci"][1] < 0
    px3 = abs(j["m1_kgt1"]["delta"]) < abs(j["ref_kgt1"]["delta"])
    j["verdicts"] = dict(PX1=px1, PX2=px2, PX3_directional=px3)
    out[jtag] = j
    md.append(f"| {jtag} | single-ref k>1 vs blind (P-X1) | {j['ref_kgt1']['delta']:+.3f} "
              f"[{j['ref_kgt1']['ci'][0]:+.3f},{j['ref_kgt1']['ci'][1]:+.3f}] n={j['ref_kgt1']['n']} | "
              f"{'CONFIRMED' if px1 else 'NOT confirmed'} |")
    md.append(f"| {jtag} | M1 minus single-ref k>1 (P-X2) | {j['m1_minus_ref_kgt1']['delta']:+.3f} "
              f"[{j['m1_minus_ref_kgt1']['ci'][0]:+.3f},{j['m1_minus_ref_kgt1']['ci'][1]:+.3f}] | "
              f"{'CONFIRMED' if px2 else 'NOT confirmed'} |")
    md.append(f"| {jtag} | M1 k>1 vs blind (P-X3 ctx) | {j['m1_kgt1']['delta']:+.3f} "
              f"[{j['m1_kgt1']['ci'][0]:+.3f},{j['m1_kgt1']['ci'][1]:+.3f}] | "
              f"{'direction holds' if px3 else 'direction fails'} |")
    md.append(f"| {jtag} | M2 k>1 vs blind (P-X4, expl.) | {j['m2_kgt1']['delta']:+.3f} "
              f"[{j['m2_kgt1']['ci'][0]:+.3f},{j['m2_kgt1']['ci'][1]:+.3f}] | recorded |")
    md.append(f"| {jtag} | ref k=1 vs blind | {j['ref_k1']['delta']:+.3f} "
              f"[{j['ref_k1']['ci'][0]:+.3f},{j['ref_k1']['ci'][1]:+.3f}] | context |")

if ran:
    out["_summary"] = dict(judges_run=ran,
                           PX1_all=all(out[j]["verdicts"]["PX1"] for j in ran),
                           PX2_all=all(out[j]["verdicts"]["PX2"] for j in ran))
    json.dump(out, open("../../papers/analysis/p17_coverage_results.json", "w"), indent=1)
    print("\n".join(md))
    print(f"\nP-X1 (all judges): {'CONFIRMED' if out['_summary']['PX1_all'] else 'NOT confirmed'}; "
          f"P-X2 (all judges): {'CONFIRMED' if out['_summary']['PX2_all'] else 'NOT confirmed'}")
else:
    print("[p17_coverage_analysis] no complete new-judge score sets yet")
