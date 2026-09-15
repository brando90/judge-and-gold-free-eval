# PRE-SPECIFIED producer for R27 (papers/D-iclr-v2/registration_round27.md); committed before R27 analysis and before any R27 call.
# Run from experiments/tfa-vs-judge. A score of 7 or above counts as credited (every grader here stores 10 or 0).
#   --part a --cell NAME --scores FILE --out JSON
#       P3 for prompts that ask whether the answer is correct, on stored R25/R26 calls on runs/r20/mace_gen/pool.jsonl: among correct
#       answers credited blind, the share not credited with the reference, for answers that differ from the reference and for answers
#       that match it; question bootstrap (2,000 resamples, seed 0) of the difference.
#   --part b --judge J --labels FILE --hle FILE --direct FILE --solve FILE --out JSON
#       Hard single-answer questions (runs/r27/hle_pool.jsonl): each answer labeled by HLE's official judge (o3-mini, --labels). Per
#       condition (verbatim HLE judge with the reference; direct and solve-first, blind and with the reference): false acceptance (share
#       of label-wrong answers credited) and recall (share of label-correct answers credited); question bootstrap (2,000, seed 0).
import argparse
import json

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--part", choices=("a", "b"), required=True)
for k in ("cell", "scores", "judge", "labels", "hle", "direct", "solve"):
    ap.add_argument(f"--{k}")
ap.add_argument("--out", required=True)
args = ap.parse_args()


def load(f):
    S = {}
    for line in open(f):
        r = json.loads(line)
        if r.get("score") is not None and not r.get("error"):
            S[(r["problem_id"], r["idx"], r["cond"])] = r["score"] >= 7
    return S


def boots_for(n):
    rng = np.random.default_rng(0)
    return [rng.integers(0, n, n) for _ in range(2000)]


def ratio(num, den, boots):
    def f(ix):
        d = den[ix].sum()
        return float(num[ix].sum() / d) if d else np.nan
    m = [f(b) for b in boots]
    return [round(f(np.arange(len(den))), 6), [round(float(np.nanpercentile(m, 2.5)), 6), round(float(np.nanpercentile(m, 97.5)), 6)], int(den.sum())]


res = {"part": args.part}
if args.part == "a":
    S = load(args.scores)
    pool = [json.loads(l) for l in open("runs/r20/mace_gen/pool.jsonl")]
    rows = [t for t in pool if all((t["problem_id"], i, c) in S for i in t["idx"] for c in ("noref", "ref"))]
    n = len(rows)
    boots = boots_for(n)
    B = np.array([[S[(t["problem_id"], i, "noref")] for i in t["idx"]] for t in rows], float)
    R = np.array([[S[(t["problem_id"], i, "ref")] for i in t["idx"]] for t in rows], float)
    NM = np.array([[o == 1 and g == "nonmatch" for o, g in zip(t["oracle"], t["group"])] for t in rows], float)
    MT = np.array([[o == 1 and g == "match" for o, g in zip(t["oracle"], t["group"])] for t in rows], float)
    rej = B * (1 - R)
    d_nm, d_mt = NM * B, MT * B
    diff = []
    for b in boots:
        a1, a2 = d_nm[b].sum(), d_mt[b].sum()
        if a1 and a2:
            diff.append((NM * rej)[b].sum() / a1 - (MT * rej)[b].sum() / a2)
    point = float((NM * rej).sum() / d_nm.sum() - (MT * rej).sum() / d_mt.sum())
    res.update(cell=args.cell, questions=n,
               differing_rejected=ratio(NM * rej, d_nm, boots), matching_rejected=ratio(MT * rej, d_mt, boots),
               difference=[round(point, 6), [round(float(np.percentile(diff, 2.5)), 6), round(float(np.percentile(diff, 97.5)), 6)]])
    res["predictions"] = {"P-R27A1 blind-accepted differing correct answers rejected more often than matching ones (point)":
                          ("confirmed" if point > 0 else "falsified") if n >= 100 else "not scored"}
else:
    L = load(args.labels)
    C = {"hle|ref": (load(args.hle), "ref"), "direct|noref": (load(args.direct), "noref"), "direct|ref": (load(args.direct), "ref"),
         "solve|noref": (load(args.solve), "noref"), "solve|ref": (load(args.solve), "ref")}
    pool = [json.loads(l) for l in open("runs/r27/hle_pool.jsonl")]
    rows = [t for t in pool if all((t["problem_id"], i, "ref") in L for i in t["idx"])
            and all((t["problem_id"], i, c) in S for i in t["idx"] for S, c in C.values())]
    n = len(rows)
    boots = boots_for(n)
    Y = np.array([[L[(t["problem_id"], i, "ref")] for i in t["idx"]] for t in rows], float)
    res.update(judge=args.judge, questions=n, answers=int(Y.size), label_correct=int(Y.sum()), conditions={})
    for key, (S, c) in C.items():
        X = np.array([[S[(t["problem_id"], i, c)] for i in t["idx"]] for t in rows], float)
        res["conditions"][key] = dict(false_acceptance=ratio(X * (1 - Y), 1 - Y, boots), recall=ratio(X * Y, Y, boots),
                                      agreement=[round(float((X == Y).mean()), 6)])
    d = res["conditions"]
    ok = n >= 100
    res["predictions"] = {
        "P-R27B1 solve-first with reference: false acceptance at most 5 points above the verbatim HLE judge (point)":
            ("confirmed" if d["solve|ref"]["false_acceptance"][0] - d["hle|ref"]["false_acceptance"][0] <= 0.05 else "falsified") if ok else "not scored",
        "P-R27B2 direct with reference: false acceptance at most 5 points above the verbatim HLE judge (point)":
            ("confirmed" if d["direct|ref"]["false_acceptance"][0] - d["hle|ref"]["false_acceptance"][0] <= 0.05 else "falsified") if ok else "not scored",
        "P-R27B3 solve-first with reference: recall at least the verbatim HLE judge's minus 5 points (point)":
            ("confirmed" if d["solve|ref"]["recall"][0] >= d["hle|ref"]["recall"][0] - 0.05 else "falsified") if ok else "not scored",
    }
json.dump(res, open(args.out, "w"), indent=1)
print(json.dumps(res["predictions"], indent=1))
