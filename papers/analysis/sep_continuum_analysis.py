# FROZEN analysis for the answer-separability continuum (P-SC1..P-SC4).
# INTERNAL REGISTRATION: committed together with scripts/build_sep_tasks.py,
# sep_generate.py, sep_oracle.py BEFORE any generation, oracle, or judging runs; the
# commit timestamp is the registration.
#
# The prospective test the code falsification owed. The separability hypothesis says
# anchoring needs a short answer token the judge can compare; the external review proposed
# a continuum scalar -> tuple -> structured -> program and assumed attenuation would be
# GRADUAL. Our hypothesis predicts a CLIFF at the artifact boundary instead: comma-pairs
# and small JSON objects are still short canonicalizable strings (list-valued families
# already anchor fully in the frozen data), while a program is not. The predictions below
# encode the cliff and are falsifiable in both directions: a flat profile through program
# falsifies separability outright; a smooth gradient falsifies the cliff reading and
# supports the review's complexity account.
#
# Estimators (mirroring worked_ref_analysis E1 and exploit_dose.py, frozen here):
#   Margin (per item): mean rubric-a escore of matching valid samples minus mean of
#     non-matching valid samples; matching = canon == ref_canon (canon from sep_oracle.py).
#     Item-level bootstrap NBOOT=1000, default_rng(0). Rubric b replicates.
#   Inflation (per item): paired ref-minus-blind excess gap at full n: select argmax of
#     rubric-a escore (1e-9 uniform tie-jitter), gap = (escore_b[sel]-mean_b)/sd_b -
#     (oracle[sel]-mean_oracle), minus within-oracle-stratum permutation null (NPERM=50);
#     paired delta = excess(ref) - excess(blind).
#   Cross-stratum contrasts pair items by shared base instance.
#
# REGISTERED PREDICTIONS (committed before any data exists; scored per judge, rubric a):
#   P-SC1 (separability survives structure): the referenced margin is positive with 95%
#     CI excluding zero at EACH of scalar, pair, json, for both judges.
#   P-SC2 (the cliff): the instance-paired margin drop json-minus-program is positive with
#     CI excluding zero, for both judges.
#   P-SC3 (cliff, not gradient): within {scalar->pair, pair->json} the largest
#     instance-paired absolute margin change is smaller than HALF the json->program drop
#     (point estimates), for both judges.
#   P-SC4 (inflation follows): the paired referenced-minus-blind excess-gap delta pooled
#     over scalar+pair+json is positive with CI excluding zero, AND the program stratum's
#     delta is not positive (CI includes zero or sits below), for both judges.
#   Everything else (pass rates, per-stratum levels, rubric-b, blind margins) exploratory.
#
# Run from experiments/tfa-vs-judge after pipeline23 completes.
import json
import os

import numpy as np

NBOOT, NPERM = 1000, 50
rng = np.random.default_rng(0)
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
STRATA = ["scalar", "pair", "json", "program"]
POOL_F = "runs/bon/bon_sep__meta-llama__Llama-3.1-8B-Instruct.jsonl"
SDIR = "runs/bon_scores_sep"


def load(judge, cond, rep):
    f = f"{SDIR}/synthk__{judge}__{cond}_{rep}.jsonl"
    if not os.path.exists(f):
        return None
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))}


pool = [json.loads(l) for l in open(POOL_F)]
if any(load(j, c, r) is None for j in JUDGES for c in ("noref", "ref") for r in ("a", "b")):
    print("[sep_continuum_analysis] pre-data: score files not all present. Nothing written.")
    raise SystemExit


def bci(vals):
    v = np.asarray(vals, float)
    boots = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(NBOOT)]
    return float(v.mean()), [float(np.percentile(boots, 2.5)),
                             float(np.percentile(boots, 97.5))], len(v)


def excess_gap(a, b, o):
    a, b, o = np.asarray(a, float), np.asarray(b, float), np.asarray(o, float)
    mb, sb = b.mean(), b.std() or 1.0
    mo = o.mean()
    sel = int(np.argmax(a + rng.uniform(0, 1e-9, len(a))))
    gap = (b[sel] - mb) / sb - (o[sel] - mo)
    i0, i1 = np.where(o == 0)[0], np.where(o == 1)[0]
    nulls = []
    for _ in range(NPERM):
        pa, pb = a.copy(), b.copy()
        for s in (i0, i1):
            pa[s] = pa[rng.permutation(s)]
            pb[s] = pb[rng.permutation(s)]
        ns = int(np.argmax(pa + rng.uniform(0, 1e-9, len(pa))))
        nulls.append((pb[ns] - mb) / sb - (o[ns] - mo))
    return gap - float(np.mean(nulls))


res = {}
md = ["| judge | stratum | margin(a) [CI] (n) | inflation delta [CI] (n) |",
      "|---|---|---|---|"]
for j in JUDGES:
    sc = {(c, r): load(j, c, r) for c in ("noref", "ref") for r in ("a", "b")}
    marg = {s: {} for s in STRATA}       # stratum -> inst -> margin (referenced, rubric a)
    infl = {s: {} for s in STRATA}       # stratum -> inst -> paired delta
    for it in pool:
        pid, s, inst = it["problem_id"], it["stratum"], it["inst"]
        if any(pid not in sc[k] for k in sc):
            continue
        o = it["oracle"]
        if not (0 < sum(o) < len(o)):
            continue
        ra = sc[("ref", "a")][pid]
        ms = [ra[i] for i, ok in enumerate(o) if ok and it["canon"][i] == it["ref_canon"]]
        ot = [ra[i] for i, ok in enumerate(o) if ok and it["canon"][i] != it["ref_canon"]]
        if ms and ot:
            marg[s][inst] = float(np.mean(ms) - np.mean(ot))
        er = excess_gap(sc[("ref", "a")][pid], sc[("ref", "b")][pid], o)
        eb = excess_gap(sc[("noref", "a")][pid], sc[("noref", "b")][pid], o)
        infl[s][inst] = er - eb
    jout = {}
    for s in STRATA:
        mm, mc, mn = bci(list(marg[s].values())) if marg[s] else (None, [None, None], 0)
        im, ic, iN = bci(list(infl[s].values())) if infl[s] else (None, [None, None], 0)
        jout[s] = dict(margin=mm, margin_ci=mc, n_margin=mn,
                       infl=im, infl_ci=ic, n_infl=iN)
        md.append(f"| {j} | {s} | "
                  f"{'--' if mm is None else f'{mm:+.2f} [{mc[0]:+.2f},{mc[1]:+.2f}] ({mn})'} | "
                  f"{'--' if im is None else f'{im:+.2f} [{ic[0]:+.2f},{ic[1]:+.2f}] ({iN})'} |")

    def pair_diff(s1, s2, d):
        shared = sorted(set(d[s1]) & set(d[s2]))
        return [d[s1][i] - d[s2][i] for i in shared]

    cliff, cci, cn = bci(pair_diff("json", "program", marg)) if pair_diff("json", "program", marg) else (None, [None, None], 0)
    adj = {}
    for s1, s2 in (("scalar", "pair"), ("pair", "json")):
        v = pair_diff(s1, s2, marg)
        adj[f"{s1}_minus_{s2}"] = float(np.mean(v)) if v else None
    pooled = [v for s in ("scalar", "pair", "json") for v in infl[s].values()]
    pm, pc, pn = bci(pooled)
    prog = bci(list(infl["program"].values())) if infl["program"] else (None, [None, None], 0)
    jout["P_SC2_cliff"] = dict(mean=cliff, ci=cci, n=cn)
    jout["P_SC3_adjacent"] = adj
    jout["P_SC4_pooled_spj"] = dict(mean=pm, ci=pc, n=pn)
    jout["P_SC4_program"] = dict(mean=prog[0], ci=prog[1], n=prog[2])
    jout["verdicts"] = dict(
        P_SC1=all(jout[s]["margin_ci"][0] is not None and jout[s]["margin_ci"][0] > 0
                  for s in ("scalar", "pair", "json")),
        P_SC2=bool(cci[0] is not None and cci[0] > 0),
        P_SC3=bool(cliff is not None and adj and
                   max(abs(v) for v in adj.values() if v is not None) < 0.5 * cliff),
        P_SC4=bool(pc[0] > 0 and (prog[1][0] is None or prog[1][0] <= 0)))
    res[j] = jout
    md.append(f"| {j} | contrasts | cliff(json-prog) "
              f"{'--' if cliff is None else f'{cliff:+.2f} [{cci[0]:+.2f},{cci[1]:+.2f}]'} "
              f"adj {adj} | pooled spj {pm:+.2f} [{pc[0]:+.2f},{pc[1]:+.2f}], "
              f"program {prog[0] if prog[0] is None else round(prog[0], 2)} |")

json.dump(res, open("../../papers/analysis/sep_continuum_results.json"
                    if os.path.exists("../../papers/analysis") else "sep_continuum_results.json",
                    "w"), indent=1)
print("\n".join(md))
for j in JUDGES:
    print(j, "verdicts:", res[j]["verdicts"])
