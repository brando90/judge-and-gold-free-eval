# FROZEN analysis for the frontier-judge Phase 2 extension (P-FR1..P-FR3, P-FK1..P-FK3).
# INTERNAL REGISTRATION: committed together with experiments/tfa-vs-judge/scripts/frontier_api_judge.py
# BEFORE any frontier API score exists; the commit timestamp is the registration.
#
# What this is. A documented SUCCESSOR of the two externally registered producers, repl_analysis.py
# (osf.io/ym5x9) and mitigation_analysis.py (osf.io/qugbd), applied unchanged in estimator to a
# frontier judge whose scores come through a provider API with logprobs (see the harness header for
# the pinned score function). Estimator code below is copied verbatim from those two scripts; the
# only changes are (1) JUDGES is the frontier tag list, (2) the pooled two-judge endpoint is
# computed only when two judges are present, (3) the registered STEP and M1-minus-ref contrasts of
# round6_disclosures are computed here directly, (4) output path.
#
# Pinned judge for the registered run: openai__gpt-5.4-2026-03-05, reasoning_effort="none",
# top_logprobs=5, temperature 0, prompts byte-identical to the open judges'. A second frontier
# family (openai__gpt-4.1-2025-04-14, full logprobs) may be added under the same predictions.
#
# REGISTERED PREDICTIONS (scored per judge, exactly as the open-judge originals):
#   Replication pool (runs/bon_scores_repl, 105 in-band items):
#   P-FR1: the paired referenced-minus-blind excess-gap delta (E1) is positive with 95% item
#          bootstrap CI excluding zero.
#   P-FR2: selection collapse, exact McNemar referenced-only vs blind-only discordant items, p < 0.05.
#   P-FR3: the anchoring margin (rubric a) is positive with CI excluding zero.
#   k-stratified pool (runs/bon_scores_kstrat, 75 items):
#   P-FK1: the step, mean k>1 delta minus mean k=1 delta (single reference vs blind), is positive
#          with CI excluding zero (independent item bootstrap of the two groups, as P-M3).
#   P-FK2: the M1-minus-single-reference paired contrast at k>1 is negative with CI excluding zero.
#   P-FK3 (directional, judge-dependent by the coverage extension): M1's k>1 delta versus blind is
#          smaller in magnitude than the single reference's; reported as a level, with the residual.
# NO cross-scale magnitude claim is made: the frontier score function differs from vLLM's in the
# number of logprob entries (5 vs 20) and the frontier judge's calibration; only signs and CIs
# are predictions. A null on P-FR1 or P-FK1 would bound the paper's claim below frontier scale and
# must be reported as prominently as a confirmation.
#
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/frontier_phase2_analysis.py [judge_tag ...]
import json
import math
import os
import re
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)
rng = np.random.default_rng(0)

JUDGES = sys.argv[1:] or ["openai__gpt-5.4-2026-03-05"]
REPL_POOL = "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl"
KSTRAT_POOL = "runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl"
KS = [1, 2, 4, 8, 16]


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


def fisher_free_mcnemar(b10, b01):
    nd = b10 + b01
    if nd == 0:
        return 1.0
    p = sum(math.comb(nd, k) for k in range(min(b01, b10) + 1)) * 2 / (2 ** nd)
    return min(p, 1.0)


def bci(vals, B=2000):
    v = np.asarray(vals, float)
    b = [float(np.mean(rng.choice(v, len(v)))) for _ in range(B)]
    return [round(float(np.percentile(b, 2.5)), 3), round(float(np.percentile(b, 97.5)), 3)]


def load_scores(path):
    if not os.path.exists(path):
        return None
    return {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(path)}


out = {"judges": JUDGES}

# ======================================================= replication pool (mirror of repl_analysis.py)
pool = {r["problem_id"]: r for r in (json.loads(l) for l in open(REPL_POOL)) if "oracle" in r}
deltas_by_judge = {}
for jtag in JUDGES:
    sc = {(c, r): load_scores(f"runs/bon_scores_repl/synthk__{jtag}__{c}_{r}.jsonl")
          for c in ("ref", "noref") for r in ("a", "b")}
    if any(v is None for v in sc.values()):
        out[f"repl__{jtag}"] = "score files missing"
        continue
    ra, rb, na, nb = sc[("ref", "a")], sc[("ref", "b")], sc[("noref", "a")], sc[("noref", "b")]
    d = {}
    for pid, it in pool.items():
        if pid not in ra or pid not in na or None in ra[pid] or None in na[pid]:
            continue
        pr = float(np.mean(it["oracle"]))
        if not (0.2 <= pr <= 0.8):
            continue
        gr = ns["per_item_curves"](it, ra[pid], rb[pid])
        nr = ns["permutation_null"](it, ra[pid], rb[pid])
        gn = ns["per_item_curves"](it, na[pid], nb[pid])
        nn = ns["permutation_null"](it, na[pid], nb[pid])
        d[pid] = ((gr[64]["judge_gain"] - gr[64]["true_gain"] - nr)
                  - (gn[64]["judge_gain"] - gn[64]["true_gain"] - nn))
    deltas_by_judge[jtag] = d
    v = np.array(list(d.values()))
    boot = [float(np.mean(rng.choice(v, len(v)))) for _ in range(4000)]
    ci = [round(float(np.percentile(boot, 2.5)), 3), round(float(np.percentile(boot, 97.5)), 3)]
    out[f"repl_delta__{jtag}"] = dict(n=len(v), delta=round(float(v.mean()), 3), ci=ci,
                                      P_FR1=bool(ci[0] > 0))
    # collapse + margins (rubric a)
    sa_ref, sa_bld = ra, na
    b10 = b01 = n_el = 0
    margins = []
    for pid, it in pool.items():
        if pid not in sa_ref or pid not in sa_bld or None in sa_ref[pid] or None in sa_bld[pid]:
            continue
        refn = norm(it["ref_answer"])
        kinds = {norm(boxed(it["samples"][i]) or it["samples"][i]) == refn
                 for i, ok in enumerate(it["oracle"]) if ok}
        if kinds == {True, False}:
            n_el += 1

            def match(s):
                sel = int(np.argmax(s[pid]))
                return bool(it["oracle"][sel]) and \
                    norm(boxed(it["samples"][sel]) or it["samples"][sel]) == refn
            mr, mb = match(sa_ref), match(sa_bld)
            if mr and not mb:
                b10 += 1
            elif mb and not mr:
                b01 += 1
        ms, os_ = [], []
        for i, ok in enumerate(it["oracle"]):
            if not ok:
                continue
            a = norm(boxed(it["samples"][i]) or it["samples"][i])
            (ms if a == refn else os_).append(sa_ref[pid][i])
        if ms and os_:
            margins.append(float(np.mean(ms) - np.mean(os_)))
    p = fisher_free_mcnemar(b10, b01)
    out[f"repl_collapse__{jtag}"] = dict(eligible=n_el, ref_only=b10, blind_only=b01,
                                         mcnemar_p=round(p, 6), P_FR2=bool(p < 0.05 and b10 > b01))
    mci = bci(margins) if len(margins) >= 3 else None
    out[f"repl_margin__{jtag}"] = dict(n=len(margins), margin=round(float(np.mean(margins)), 2),
                                       ci=mci, P_FR3=bool(mci and mci[0] > 0))
if len(deltas_by_judge) == 2:
    j0, j1 = list(deltas_by_judge)
    pids = sorted(set(deltas_by_judge[j0]) & set(deltas_by_judge[j1]))
    D = np.array([[deltas_by_judge[j][p] for p in pids] for j in (j0, j1)])
    idx = np.arange(len(pids))
    boots = [float(D[:, rng.choice(idx, len(idx))].mean()) for _ in range(4000)]
    out["repl_E1_pooled"] = dict(n_items=len(pids), delta=round(float(D.mean()), 3),
                                 ci=[round(float(np.percentile(boots, 2.5)), 3),
                                     round(float(np.percentile(boots, 97.5)), 3)])

# ======================================================= k-stratified pool (mirror of mitigation_analysis.py)
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
kpool = {}
for l in open(KSTRAT_POOL):
    r = json.loads(l)
    if "oracle" not in r:
        continue
    t = tasks[r["problem_id"]]
    r["k"] = t["k"]
    r["ref_answer"] = t["ref_answer"]
    kpool[r["problem_id"]] = r


def kscores(jtag, cond, rep):
    for pref in ("kstrat", "synthk"):
        s = load_scores(f"runs/bon_scores_kstrat/{pref}__{jtag}__{cond}_{rep}.jsonl")
        if s is not None:
            return s
    return None


for jtag in JUDGES:
    conds = ["noref", "ref", "m1"]
    sc = {(c, r): kscores(jtag, c, r) for c in conds for r in ("a", "b")}
    if any(sc[(c, r)] is None for c in ("noref", "ref") for r in ("a", "b")):
        out[f"kstrat__{jtag}"] = "score files missing"
        continue
    have_m1 = sc[("m1", "a")] is not None and sc[("m1", "b")] is not None
    # E1 margins (rubric a) by cond and k>1
    for cond in conds:
        if cond == "m1" and not have_m1:
            continue
        sa = sc[(cond, "a")]
        for k in KS[1:]:
            vals = []
            for pid, it in kpool.items():
                if it["k"] != k or pid not in sa or None in sa[pid]:
                    continue
                refn = norm(it["ref_answer"])
                ms, os_ = [], []
                for i, ok in enumerate(it["oracle"]):
                    if not ok:
                        continue
                    a = norm(boxed(it["samples"][i]) or it["samples"][i])
                    (ms if a == refn else os_).append(sa[pid][i])
                if ms and os_:
                    vals.append(float(np.mean(ms) - np.mean(os_)))
            if len(vals) >= 3:
                out[f"kstrat_margin__{jtag}|{cond}|k{k}"] = dict(n=len(vals),
                                                                 margin=round(float(np.mean(vals)), 2),
                                                                 ci=bci(vals))
    # E2 gaps per cond
    per_cond = {}
    for cond in conds:
        if cond == "m1" and not have_m1:
            continue
        sa, sb = sc[(cond, "a")], sc[(cond, "b")]
        g = {}
        for pid, it in kpool.items():
            if pid not in sa or None in sa[pid] or None in sb[pid]:
                continue
            pr = float(np.mean(it["oracle"]))
            if not (0.05 <= pr <= 0.95):
                continue
            c = ns["per_item_curves"](it, sa[pid], sb[pid])
            nl = ns["permutation_null"](it, sa[pid], sb[pid])
            g[pid] = c[64]["judge_gain"] - c[64]["true_gain"] - nl
        per_cond[cond] = g
    for cond in [c for c in ("ref", "m1") if c in per_cond]:
        for k in KS:
            pids = [p for p in per_cond[cond] if p in per_cond["noref"] and kpool[p]["k"] == k]
            if len(pids) >= 3:
                d = np.array([per_cond[cond][p] - per_cond["noref"][p] for p in pids])
                out[f"kstrat_gap__{jtag}|{cond}|k{k}"] = dict(n=len(d), delta=round(float(d.mean()), 3), ci=bci(d))
        pids = [p for p in per_cond[cond] if p in per_cond["noref"] and kpool[p]["k"] > 1]
        d = np.array([per_cond[cond][p] - per_cond["noref"][p] for p in pids])
        out[f"kstrat_gap__{jtag}|{cond}|kgt1"] = dict(n=len(d), delta=round(float(d.mean()), 3), ci=bci(d))
    # registered contrasts
    d1 = np.array([per_cond["ref"][p] - per_cond["noref"][p] for p in per_cond["ref"]
                   if p in per_cond["noref"] and kpool[p]["k"] == 1])
    dg = np.array([per_cond["ref"][p] - per_cond["noref"][p] for p in per_cond["ref"]
                   if p in per_cond["noref"] and kpool[p]["k"] > 1])
    steps = [float(np.mean(rng.choice(dg, len(dg))) - np.mean(rng.choice(d1, len(d1)))) for _ in range(4000)]
    sci = [round(float(np.percentile(steps, 2.5)), 3), round(float(np.percentile(steps, 97.5)), 3)]
    out[f"kstrat_step__{jtag}"] = dict(n_k1=len(d1), n_kgt1=len(dg), step=round(float(dg.mean() - d1.mean()), 3),
                                       ci=sci, P_FK1=bool(sci[0] > 0))
    if have_m1:
        pids = [p for p in per_cond["m1"] if p in per_cond["ref"] and kpool[p]["k"] > 1]
        c = np.array([per_cond["m1"][p] - per_cond["ref"][p] for p in pids])
        cci = bci(c)
        out[f"kstrat_m1_minus_ref__{jtag}"] = dict(n=len(c), contrast=round(float(c.mean()), 3), ci=cci,
                                                   P_FK2=bool(cci[1] < 0))
        m1_level = out[f"kstrat_gap__{jtag}|m1|kgt1"]["delta"]
        ref_level = out[f"kstrat_gap__{jtag}|ref|kgt1"]["delta"]
        out[f"kstrat_P_FK3__{jtag}"] = dict(m1_kgt1=m1_level, ref_kgt1=ref_level,
                                            directional=bool(abs(m1_level) < abs(ref_level)))

json.dump(out, open("../../papers/analysis/frontier_phase2_results.json", "w"), indent=1)
for k, v in out.items():
    print(k, json.dumps(v) if not isinstance(v, str) else v)
