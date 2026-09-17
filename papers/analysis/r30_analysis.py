#!/usr/bin/env python
# R30 (papers/D-iclr-v5/registration_round30.md). Run from experiments/tfa-vs-judge.
# A score of 7 or above counts as credited, as in r24_analysis.py and r27_analysis.py (the binary templates
# store 10 or 0). Question bootstrap, 2,000 resamples, seed 0, as in both.
#
#   --part a --judge NAME --draw1 FILE --draw2 FILE --out JSON
#       The swap under the direct prompt. draw1 is the EXISTING runs/r26/bench_direct_<judge>/scores.jsonl,
#       whose referenced rows were made on runs/r20/mace_gen/pool.jsonl (ref = draw 1); draw2 is the new run
#       on runs/r22/redraw_pool.jsonl (ref = draw 2). The two arms cover the same questions and answers, so
#       they are joined on (problem_id, idx). Match-change classes come from the redraw pool's own
#       group_draw1 and group, restricted to correct answers:
#           stop   match under draw 1, nonmatch under draw 2
#           start  nonmatch under draw 1, match under draw 2
#           neither  nonmatch under both (placebo)
#       Reports the credited share of each class under each draw and the shift, with intervals.
#
#   --part b --grader NAME --arm first|modal --scores FILE --baseline FILE --out JSON
#       The benchmark study with a chosen reference. scores is the run on the arm's pool from
#       r30_build_canonical_pools.py; baseline is the existing random-draw run on runs/r20/mace_gen/pool.jsonl
#       for the same grader. Reports accuracy minus answer-list accuracy under each, their difference, and
#       the credited share of correct answers that differ from the reference.
import argparse
import json

import numpy as np

T = 7
NB, SEED = 2000, 0

ap = argparse.ArgumentParser()
ap.add_argument("--part", choices=("a", "b"), required=True)
ap.add_argument("--judge")
ap.add_argument("--grader")
ap.add_argument("--arm", choices=("first", "modal"))
ap.add_argument("--draw1")
ap.add_argument("--draw2")
ap.add_argument("--scores")
ap.add_argument("--baseline")
ap.add_argument("--pool", default="runs/r22/redraw_pool.jsonl")
ap.add_argument("--out", required=True)
args = ap.parse_args()


def load(f):
    """(problem_id, idx, cond) -> credited, skipping errors and ungraded calls (as r24/r27)."""
    S = {}
    for line in open(f):
        r = json.loads(line)
        if r.get("score") is not None and not r.get("error"):
            S[(r["problem_id"], r["idx"], r["cond"])] = r["score"] >= T
    return S


def boot_rows(n):
    rng = np.random.default_rng(SEED)
    return [rng.integers(0, n, n) for _ in range(NB)]


def ci_masked(mask, val, boots):
    """Share of val among mask, with a question bootstrap. Returns [point, [lo, hi], n]."""
    def f(ix):
        d = mask[ix].sum()
        return float((mask[ix] * val[ix]).sum() / d) if d else np.nan
    m = [f(b) for b in boots]
    return [round(f(np.arange(len(mask))), 6),
            [round(float(np.nanpercentile(m, 2.5)), 6), round(float(np.nanpercentile(m, 97.5)), 6)],
            int(mask.sum())]


def ci_mean(x, boots):
    x = np.asarray(x, float)
    m = [x[b].mean() for b in boots]
    return [round(float(x.mean()), 6),
            [round(float(np.percentile(m, 2.5)), 6), round(float(np.percentile(m, 97.5)), 6)]]


def shift(mask, later, earlier, boots):
    """Change in credited share within a class, later minus earlier."""
    def f(ix):
        d = mask[ix].sum()
        return float((mask[ix] * (later[ix] - earlier[ix])).sum() / d) if d else np.nan
    m = [f(b) for b in boots]
    return [round(f(np.arange(len(mask))), 6),
            [round(float(np.nanpercentile(m, 2.5)), 6), round(float(np.nanpercentile(m, 97.5)), 6)],
            int(mask.sum())]


res = {"part": args.part}

if args.part == "a":
    D1, D2 = load(args.draw1), load(args.draw2)
    pool = [json.loads(l) for l in open(args.pool)]
    rows = [t for t in pool
            if all((t["problem_id"], i, "ref") in D1 and (t["problem_id"], i, "ref") in D2 for i in t["idx"])]
    n = len(rows)
    boots = boot_rows(n)
    A1 = np.array([[D1[(t["problem_id"], i, "ref")] for i in t["idx"]] for t in rows], float)
    A2 = np.array([[D2[(t["problem_id"], i, "ref")] for i in t["idx"]] for t in rows], float)

    def cls(kind):
        out = []
        for t in rows:
            r = []
            for o, g1, g2 in zip(t["oracle"], t["group_draw1"], t["group"]):
                ok = o == 1
                r.append(ok and ((g1 == "match" and g2 == "nonmatch") if kind == "stop" else
                                 (g1 == "nonmatch" and g2 == "match") if kind == "start" else
                                 (g1 == "nonmatch" and g2 == "nonmatch")))
            out.append(r)
        return np.array(out, float)

    stop, start, neither = cls("stop"), cls("start"), cls("neither")
    res.update(judge=args.judge, questions=n, questions_in_pool=len(pool))
    for name, mask in (("stop_matching", stop), ("start_matching", start), ("matches_neither", neither)):
        res[name] = dict(credited_draw1=ci_masked(mask, A1, boots),
                         credited_draw2=ci_masked(mask, A2, boots),
                         shift_draw2_minus_draw1=shift(mask, A2, A1, boots))
    res["accuracy"] = dict(draw1=ci_mean(A1.mean(1), boots), draw2=ci_mean(A2.mean(1), boots))
    s_stop = res["stop_matching"]["shift_draw2_minus_draw1"]
    s_start = res["start_matching"]["shift_draw2_minus_draw1"]
    s_none = res["matches_neither"]["shift_draw2_minus_draw1"]
    scored = n >= 100
    res["status"] = "scored" if scored else "not scored (fewer than 100 complete questions)"
    if scored:
        res["predictions"] = {
            "P-R30A1 stop-matching answers credited less under draw 2 (interval)":
                "confirmed" if s_stop[1][1] < 0 else ("falsified" if s_stop[1][0] > 0 else "not confirmed"),
            "P-R30A2 start-matching answers credited more under draw 2 (interval)":
                "confirmed" if s_start[1][0] > 0 else ("falsified" if s_start[1][1] < 0 else "not confirmed"),
            "P-R30A4 answers matching neither reference move at most 5 points (point)":
                "confirmed" if abs(s_none[0]) <= 0.05 else "falsified",
        }
        # P-R30A3 compares each judge's shift with its own shift under our rubric; the rubric comparator is
        # read from the paper rather than recomputed here, so it is recorded for scoring by hand.
        res["predictions"]["P-R30A3 shift smaller than this judge's rubric shift (point, scored by hand)"] = \
            {"observed_stop": s_stop[0], "observed_start": s_start[0],
             "rubric_comparator": {"claude-sonnet-5": {"stop": -0.382, "start": 0.350},
                                   "gpt-4.1": {"stop": -0.125, "start": 0.189}}}
else:
    S, B = load(args.scores), load(args.baseline)
    pool = [json.loads(l) for l in open(f"runs/r30/canon_{args.arm}_pool.jsonl")]
    rows = [t for t in pool
            if all((t["problem_id"], i, "ref") in S and (t["problem_id"], i, "ref") in B for i in t["idx"])]
    n = len(rows)
    boots = boot_rows(n)
    M = np.array([[S[(t["problem_id"], i, "ref")] for i in t["idx"]] for t in rows], float)
    Mb = np.array([[B[(t["problem_id"], i, "ref")] for i in t["idx"]] for t in rows], float)
    orc = np.array([t["oracle"] for t in rows], float)
    nm = np.array([[o == 1 and g == "nonmatch" for o, g in zip(t["oracle"], t["group"])] for t in rows], float)
    nm_b = np.array([[o == 1 and g == "nonmatch" for o, g in zip(t["oracle"], t["group_draw"])] for t in rows], float)
    wr = 1 - orc
    res.update(grader=args.grader, arm=args.arm, questions=n, questions_in_pool=len(pool),
               reference_changed=int(sum(1 for t in rows if t["ref"] != t["ref_draw"])),
               modal_fallbacks=int(sum(1 for t in rows if t.get("modal_fallback"))))
    res["chosen"] = dict(list=ci_mean(orc.mean(1), boots), ref=ci_mean(M.mean(1), boots),
                         ref_minus_list=ci_mean((M - orc).mean(1), boots),
                         nonmatch_correct_credited=ci_masked(nm, M, boots),
                         wrong_credited=ci_masked(wr, M, boots))
    res["random_draw"] = dict(ref=ci_mean(Mb.mean(1), boots),
                              ref_minus_list=ci_mean((Mb - orc).mean(1), boots),
                              nonmatch_correct_credited=ci_masked(nm_b, Mb, boots))
    res["chosen_minus_random"] = dict(ref_minus_list=ci_mean(((M - orc) - (Mb - orc)).mean(1), boots))
    d = res["chosen_minus_random"]["ref_minus_list"]
    shortfall = res["chosen"]["ref_minus_list"]
    scored = n >= 100
    res["status"] = "scored" if scored else "not scored (fewer than 100 complete questions)"
    if scored:
        res["predictions"] = {
            "P-R30B1 shortfall smaller than under the random draw (interval)":
                "confirmed" if d[1][0] > 0 else ("falsified" if d[1][1] < 0 else "not confirmed"),
            "P-R30B2 shortfall still below zero (interval)":
                "confirmed" if shortfall[1][1] < 0 else (
                    "falsified" if shortfall[1][0] > 0 else "not confirmed"),
        }

json.dump(res, open(args.out, "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k in ("part", "judge", "grader", "arm", "questions", "status")}))
