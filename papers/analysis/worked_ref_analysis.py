# Worked-reference arm (E1) and method rotation (H-METHOD) for Paper D.
# INTERNAL REGISTRATION: this header pins the design, the estimators, and the predictions,
# and the file is git-committed BEFORE any refsol/refsol2 judge score exists (the commit
# timestamp is the registration; no OSF post per current hold). The construction half is
# scripts/build_worked_refs.py + runs/kstrat_worked_refs.jsonl, committed in the same commit.
# NO judging has been run at registration time, so nothing below can be tuned to an outcome.
#
# Motivation. Every reference-condition number in Paper D shows the judge a BARE answer
# string as the reference ("31"). Practitioners hand judges a worked solution instead. Two
# things follow, and both are measured by RE-JUDGING THE FROZEN 64-sample k-stratified pool
# (runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl) — no new generation, so the
# samples cannot adapt to the manipulation:
#
#   E1 (worked-reference arm). New condition refsol shows a short worked derivation ending
#   in the item's ref_answer, in place of the bare answer. On k > 1 items, does the longer
#   reference anchor MORE (more surface to match on) or LESS (more information about what the
#   problem actually requires)? Direction is NOT predicted.
#
#   H-METHOD (method rotation; Sri's hypothesis). On the 15 k = 1 items there is exactly ONE
#   valid answer, so every oracle-valid sample carries the SAME final answer. Show the judge
#   method A (refsol = sol_a), then re-judge showing method B (refsol2 = sol_b): same answer,
#   visibly different derivation route (build_worked_refs.py asserts both routes box the
#   item's ref_answer, pass the family oracle, have token Jaccard < 0.6, and sit within a
#   1.6 length ratio). Answer-matching is therefore held constant BY CONSTRUCTION, and any
#   score movement is PURE method anchoring. This is the exact analog of the paper's
#   answer-rotation experiment, run in method space.
#
# Design (pinned):
#   - Pool: the frozen k-stratified pool, 75 items x 64 Llama-3.1-8B samples, "oracle" labels
#     as already committed. Items and samples are untouched; only the reference block moves.
#   - Judges: Qwen__Qwen2.5-7B-Instruct and microsoft__phi-4. Conditions: the existing noref
#     (blind) and ref (bare answer), plus the new refsol / refsol2. Rubrics a (selection) and
#     b (reporting), the standing winner's-curse split. Score files:
#     runs/bon_scores_kstrat/synthk__{judge}__{cond}_{rep}.jsonl.
#   - Estimators are the committed ones, not new ones:
#       margin  = mean rubric-a score of reference-ANSWER-matching valid samples minus other
#                 valid samples, item-mean (defined only for k > 1), exactly as in
#                 papers/analysis/mitigation_analysis.py;
#       gap     = excess hack gap at n = 64 from scripts/bon_analysis.py (per_item_curves for
#                 judge_gain - true_gain, minus permutation_null), reached by exec'ing that
#                 file, the same reuse pattern mitigation_analysis.py uses;
#       delta   = per-item paired condition-minus-blind gap; item filter 0.05 <= pool pass
#                 rate <= 0.95, as in mitigation_analysis.py.
#   - All CIs: item-level nonparametric bootstrap, NBOOT = 1000, rng = numpy default_rng(0).
#     Paired contrasts resample ITEMS (the cluster), never samples.
#   - Method classifier (H-METHOD): for each ORACLE-VALID sample on a k = 1 item, token-level
#     Jaccard similarity against sol_a and against sol_b; the sample is labelled A or B by the
#     larger similarity, and ties (equal similarity) are dropped and counted. THE CLASSIFIER
#     IS HEURISTIC. It has no validation set, its accuracy is unknown, and its accuracy BOUNDS
#     THE READOUT: label noise attenuates the method-split contrasts toward zero, so a
#     confirmed P-W2 (a CI containing zero) is the weaker half of the inference and a
#     falsified P-W2 is the stronger half. The classifier affects only the method-SPLIT
#     contrasts and the method-matching margins; the pooled paired refsol2-minus-refsol delta
#     (the P-W2 headline) is classifier-free and is reported both pooled and split.
#
# REGISTERED PREDICTIONS (committed before any refsol/refsol2 data exists):
#   P-W1 (E1). On k > 1 items, the refsol anchoring margin DIFFERS from the bare-ref margin:
#     the paired per-item difference (margin_refsol - margin_ref) has a 95% item-bootstrap CI
#     EXCLUDING zero, for at least one of the two judges. Direction is deliberately NOT
#     predicted — "more surface to match" and "more information about the problem" pull
#     opposite ways and the paper has no basis to choose. The paired inflation delta vs blind
#     under refsol is reported alongside the standing ref number as the same contrast on the
#     selection-level endpoint.
#   P-W2 (H-METHOD; Sri's hypothesis). On k = 1 items, the paired same-sample delta between
#     refsol2 and refsol (mean over oracle-valid samples, item-mean, item bootstrap) has a
#     95% CI CONTAINING zero, for BOTH judges: rotating the reference's METHOD does not move
#     scores once the answer is held constant.
#   P-W3 (positive control). The SAME refsol2-minus-refsol rotation computed on k > 1 items —
#     where the valid samples span several distinct answers, so answer-level surface varies
#     across the pool — DOES move scores: CI excluding zero for at least one judge. This is
#     the control that the machinery can detect movement at all; the standing ref-minus-noref
#     delta at k > 1 (already positive in the paper) is reported as a second, independent
#     machinery check in the same table.
#
# WHAT THE OUTCOME MEANS. Confirming P-W2 supports ANSWER-anchoring over METHOD-anchoring as
# the mechanism behind the paper's reference-inflation result, and certifies worked references
# as SAFE on unique-answer tasks: practitioners may show the judge a full derivation at k = 1
# without inducing measurable anchoring. Falsifying P-W2 extends the paper's warning to
# unique-answer tasks — the one regime the paper currently reports as benign — and means a
# worked reference leaks a preferred SOLUTION ROUTE even when the answer is pinned.
# Everything else printed here (per-family splits, per-k levels, classifier diagnostics,
# rubric-b replicates) is EXPLORATORY.
#
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/worked_ref_analysis.py
# Writes ../../papers/analysis/worked_ref_results.json and prints a markdown summary.
# Exits gracefully with a clear message if the refsol/refsol2 score files do not exist yet.
import json
import os
import re
import sys

import numpy as np

NBOOT = 1000
rng = np.random.default_rng(0)

POOL = "runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl"
TASKS = "runs/kstrat_tasks.jsonl"
WREFS = "runs/kstrat_worked_refs.jsonl"
SDIR = "runs/bon_scores_kstrat"
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
CONDS = ["noref", "ref", "refsol", "refsol2"]
REPS = ["a", "b"]
OUT = "../../papers/analysis/worked_ref_results.json"


def spath(jtag, cond, rep):
    return f"{SDIR}/synthk__{jtag}__{cond}_{rep}.jsonl"


# ---------------- pre-flight: exit gracefully before the data exists
need = [POOL, TASKS, WREFS] + [spath(j, c, r) for j in JUDGES for c in CONDS for r in REPS]
missing = [p for p in need if not os.path.exists(p)]
if missing:
    print("[worked-ref analysis] not runnable yet: "
          f"{len(missing)}/{len(need)} required files are absent.")
    for p in missing[:12]:
        print(f"    missing: {p}")
    if len(missing) > 12:
        print(f"    ... and {len(missing) - 12} more")
    print("  Build the references with `python3 scripts/build_worked_refs.py`, then run the "
          "refsol/refsol2 judging with scripts/pipeline19.sh (8 runs: 2 judges x "
          "{refsol,refsol2} x rubrics {a,b}). Run this file from experiments/tfa-vs-judge.")
    raise SystemExit(0)

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)


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


def toks(t):
    return set(re.findall(r"[a-z]+|\d+", t.lower()))


def jac(a, b):
    return len(a & b) / max(len(a | b), 1)


def bci(vals):
    v = np.asarray(vals, float)
    if len(v) < 2:
        return [float("nan"), float("nan")]
    b = [float(np.mean(v[rng.integers(0, len(v), len(v))])) for _ in range(NBOOT)]
    return [round(float(np.percentile(b, 2.5)), 3), round(float(np.percentile(b, 97.5)), 3)]


def stat(vals):
    v = [x for x in vals if np.isfinite(x)]
    return dict(n=len(v), est=round(float(np.mean(v)), 3) if v else None,
                ci=bci(v) if v else [float("nan"), float("nan")])


tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open(TASKS)}
wrefs = {json.loads(l)["problem_id"]: json.loads(l) for l in open(WREFS)}
pool = {}
for l in open(POOL):
    r = json.loads(l)
    if "oracle" not in r:
        continue
    t = tasks[r["problem_id"]]
    r["k"], r["ref_answer"] = t["k"], t["ref_answer"]
    pool[r["problem_id"]] = r

scores = {(j, c, rp): {json.loads(l)["problem_id"]: json.loads(l)["escore"]
                       for l in open(spath(j, c, rp))}
          for j in JUDGES for c in CONDS for rp in REPS}

out = dict(design=dict(NBOOT=NBOOT, judges=JUDGES, conds=CONDS, n_items=len(pool),
                       n_k1=sum(1 for r in pool.values() if r["k"] == 1),
                       n_kgt1=sum(1 for r in pool.values() if r["k"] > 1)))

# ---------------- E1: anchoring margin (k > 1), refsol vs the standing bare ref
margins = {}
for j in JUDGES:
    per_cond = {}
    for c in ("noref", "ref", "refsol", "refsol2"):
        sa = scores[(j, c, "a")]
        m = {}
        for pid, it in pool.items():
            if it["k"] == 1 or pid not in sa:
                continue
            refn = norm(it["ref_answer"])
            ms, others = [], []
            for i, ok in enumerate(it["oracle"]):
                if not ok:
                    continue
                a = norm(boxed(it["samples"][i]) or it["samples"][i])
                (ms if a == refn else others).append(sa[pid][i])
            if ms and others:
                m[pid] = float(np.mean(ms) - np.mean(others))
        per_cond[c] = m
        margins[f"{j}|{c}"] = stat(list(m.values()))
    shared = sorted(set(per_cond["ref"]) & set(per_cond["refsol"]))
    margins[f"{j}|refsol_minus_ref"] = stat(
        [per_cond["refsol"][p] - per_cond["ref"][p] for p in shared])
out["E1_margins_kgt1"] = margins

# ---------------- E1: paired inflation delta vs blind (excess hack gap at n=64)
gapd = {}
gaps_by_cond = {}
for j in JUDGES:
    per_cond = {}
    for c in CONDS:
        sa, sb = scores[(j, c, "a")], scores[(j, c, "b")]
        g = {}
        for pid, it in pool.items():
            if pid not in sa or pid not in sb:
                continue
            pr = float(np.mean(it["oracle"]))
            if not (0.05 <= pr <= 0.95):
                continue
            cv = ns["per_item_curves"](it, sa[pid], sb[pid])
            g[pid] = cv[64]["judge_gain"] - cv[64]["true_gain"] - \
                ns["permutation_null"](it, sa[pid], sb[pid])
        per_cond[c] = g
    gaps_by_cond[j] = per_cond
    for c in ("ref", "refsol", "refsol2"):
        for lab, keep in (("kgt1", lambda p: pool[p]["k"] > 1), ("k1", lambda p: pool[p]["k"] == 1)):
            pids = [p for p in per_cond[c] if p in per_cond["noref"] and keep(p)]
            gapd[f"{j}|{c}_minus_blind|{lab}"] = stat(
                [per_cond[c][p] - per_cond["noref"][p] for p in pids])
    pids = [p for p in per_cond["refsol"] if p in per_cond["ref"] and pool[p]["k"] > 1]
    gapd[f"{j}|refsol_minus_ref|kgt1"] = stat(
        [per_cond["refsol"][p] - per_cond["ref"][p] for p in pids])
out["E1_gap_deltas"] = gapd

# ---------------- H-METHOD: classify each oracle-valid sample's derivation route
cls = {}
for pid, it in pool.items():
    w = wrefs[pid]
    ta, tb = toks(w["sol_a"]), toks(w["sol_b"])
    lab, marg = {}, []
    for i, ok in enumerate(it["oracle"]):
        if not ok:
            continue
        ja, jb = jac(toks(it["samples"][i]), ta), jac(toks(it["samples"][i]), tb)
        marg.append(abs(ja - jb))
        if ja == jb:
            continue
        lab[i] = "A" if ja > jb else "B"
    cls[pid] = dict(lab=lab, n_valid=int(sum(it["oracle"])),
                    n_tie=int(sum(it["oracle"])) - len(lab),
                    mean_sim_margin=float(np.mean(marg)) if marg else float("nan"))
out["method_classifier"] = dict(
    note="HEURISTIC token-Jaccard classifier; unvalidated, its accuracy bounds the readout",
    n_valid_total=int(sum(c["n_valid"] for c in cls.values())),
    n_tie_total=int(sum(c["n_tie"] for c in cls.values())),
    frac_A=round(float(np.mean([v == "A" for c in cls.values() for v in c["lab"].values()])), 3),
    mean_sim_margin=round(float(np.nanmean([c["mean_sim_margin"] for c in cls.values()])), 4),
    k1_items_with_both_methods=sum(
        1 for p, c in cls.items()
        if pool[p]["k"] == 1 and {"A", "B"} <= set(c["lab"].values())))

# ---------------- H-METHOD: paired same-sample delta refsol2 - refsol, and P-W3 control
rot = {}
for j in JUDGES:
    for rp in REPS:
        s1, s2 = scores[(j, "refsol", rp)], scores[(j, "refsol2", rp)]
        sn, sr = scores[(j, "noref", rp)], scores[(j, "ref", rp)]
        buckets = {(kl, g): [] for kl in ("k1", "kgt1") for g in ("all", "A", "B")}
        ctrl = {kl: [] for kl in ("k1", "kgt1")}
        for pid, it in pool.items():
            if pid not in s1 or pid not in s2:
                continue
            kl = "k1" if it["k"] == 1 else "kgt1"
            idx = [i for i, ok in enumerate(it["oracle"]) if ok]
            if not idx:
                continue
            d = {i: s2[pid][i] - s1[pid][i] for i in idx}
            buckets[(kl, "all")].append(float(np.mean(list(d.values()))))
            for g in ("A", "B"):
                gi = [i for i in idx if cls[pid]["lab"].get(i) == g]
                if gi:
                    buckets[(kl, g)].append(float(np.mean([d[i] for i in gi])))
            if pid in sn and pid in sr:
                ctrl[kl].append(float(np.mean([sr[pid][i] - sn[pid][i] for i in idx])))
        for (kl, g), v in buckets.items():
            rot[f"{j}|{rp}|{kl}|{g}"] = stat(v)
        for kl, v in ctrl.items():
            rot[f"{j}|{rp}|{kl}|ref_minus_blind_control"] = stat(v)
out["H_METHOD_rotation"] = rot

# ---------------- H-METHOD: method-matching margin within each condition
mm = {}
for j in JUDGES:
    for rp in REPS:
        for kl in ("k1", "kgt1"):
            for cond, shown in (("refsol", "A"), ("refsol2", "B")):
                s = scores[(j, cond, rp)]
                vals = []
                for pid, it in pool.items():
                    if pid not in s:
                        continue
                    if (it["k"] == 1) != (kl == "k1"):
                        continue
                    lab = cls[pid]["lab"]
                    mm_s = [s[pid][i] for i, g in lab.items() if g == shown]
                    ot_s = [s[pid][i] for i, g in lab.items() if g != shown]
                    if mm_s and ot_s:
                        vals.append(float(np.mean(mm_s) - np.mean(ot_s)))
                mm[f"{j}|{rp}|{kl}|{cond}"] = stat(vals)
out["H_METHOD_matching_margin"] = mm

json.dump(out, open(OUT, "w"), indent=1)

print(f"n items {out['design']['n_items']}  (k=1 {out['design']['n_k1']}, "
      f"k>1 {out['design']['n_kgt1']})")
print(f"classifier: {out['method_classifier']}")
for key, title in (("E1_margins_kgt1", "E1 anchoring margin, k>1 (rubric a)"),
                   ("E1_gap_deltas", "E1 paired excess-gap deltas"),
                   ("H_METHOD_rotation", "H-METHOD paired refsol2 - refsol (P-W2/P-W3)"),
                   ("H_METHOD_matching_margin", "H-METHOD method-matching margin")):
    print(f"\n=== {title}")
    for k, v in out[key].items():
        if v["est"] is None:
            print(f"  {k:58s} (empty)")
            continue
        print(f"  {k:58s} {v['est']:+.3f} [{v['ci'][0]:+.3f},{v['ci'][1]:+.3f}] n={v['n']}")
