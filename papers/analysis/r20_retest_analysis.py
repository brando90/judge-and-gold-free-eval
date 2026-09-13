# PRE-SPECIFIED producer for R20-A (papers/D-iclr/registration_round20.md); committed before any R20 call.
# Run from experiments/tfa-vs-judge:
#   python ../../papers/analysis/r20_retest_analysis.py --judge sonnet --orig runs/r8/sonnet_api --retest runs/r20/sonnet_retest_api --out ../../papers/analysis/r20a_sonnet_retest.json
# For correct answers the judge scored 10 on its first blind call: the share scored 3 or below on a second blind call through the same
# interface (retest), against the share scored 3 or below on the original referenced call; per pool and pooled; matching and
# non-matching answers separately. Also the share still scored 10 on the second blind call.
import argparse
import json
import os

ap = argparse.ArgumentParser()
ap.add_argument("--judge", required=True)
ap.add_argument("--orig", required=True)
ap.add_argument("--retest", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()


def jl(f):
    return [json.loads(l) for l in open(f)]


def scores(f):
    return {(r["problem_id"], r["idx"], r["cond"]): r["score"] for r in jl(f) if r.get("score") is not None and not r.get("error")}


res = {}
tot = {g: [0, 0, 0, 0] for g in ("nonmatch", "match")}  # n, retest <= 3, referenced <= 3, retest == 10
for pool in ("mace", "repl", "kpool"):
    fr = os.path.join(args.retest, f"{pool}.jsonl")
    if not os.path.exists(fr):
        continue
    O, R = scores(os.path.join(args.orig, f"{pool}.jsonl")), scores(fr)
    c = {g: [0, 0, 0, 0] for g in ("nonmatch", "match")}
    for t in jl(f"runs/r20/retest_pools/{args.judge}_{pool}.jsonl"):
        for idx, g in zip(t["idx"], t["group"]):
            rt, ref = R.get((t["problem_id"], idx, "noref")), O.get((t["problem_id"], idx, "ref"))
            if rt is None or ref is None:
                continue
            for acc in (c[g], tot[g]):
                acc[0] += 1
                acc[1] += rt <= 3
                acc[2] += ref <= 3
                acc[3] += rt == 10
    res[pool] = {g: dict(n=v[0], share_retest_le3=round(v[1] / v[0], 4) if v[0] else None, share_referenced_le3=round(v[2] / v[0], 4) if v[0] else None,
                         share_retest_10=round(v[3] / v[0], 4) if v[0] else None, retest_le3=v[1], referenced_le3=v[2]) for g, v in c.items()}
res["pooled"] = {g: dict(n=v[0], share_retest_le3=round(v[1] / v[0], 4) if v[0] else None, share_referenced_le3=round(v[2] / v[0], 4) if v[0] else None,
                         share_retest_10=round(v[3] / v[0], 4) if v[0] else None, retest_le3=v[1], referenced_le3=v[2]) for g, v in tot.items()}
json.dump(res, open(args.out, "w"), indent=1)
print(json.dumps(res, indent=1))
