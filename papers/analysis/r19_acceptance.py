# PRE-SPECIFIED producer for R19 (papers/D-iclr/registration_round19.md); committed before any R19 call.
# Run from experiments/tfa-vs-judge:  python ../../papers/analysis/r19_acceptance.py --scores <dir> --out <json>
# For an API judge's scores on the R8-A subsamples (<dir>/<pool>.jsonl), per pool and pooled over pools:
#   (a) among correct answers scored 10 blind, the share scored 3 or below with the reference, for answers that differ from
#       the reference (nonmatch) and answers that match it (match);
#   (b) the share of wrong answers and of correct answers scored 10 blind.
# Labels: any-format for the replication pool and k-pool, the answer lists for MACE (as in r8_sonnet_analysis.py).
import argparse
import json
import os

ap = argparse.ArgumentParser()
ap.add_argument("--scores", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()


def jl(f):
    return [json.loads(l) for l in open(f)]


res, tot = {}, {"nonmatch": [0, 0], "match": [0, 0]}
for pool, how in (("mace", "oracle"), ("repl", "lenient"), ("kpool", "lenient")):
    f = os.path.join(args.scores, f"{pool}.jsonl")
    if not os.path.exists(f):
        continue
    S = {}
    for r in jl(f):
        if r.get("score") is not None and not r.get("error"):
            S[(r["problem_id"], r["idx"], r["cond"])] = r["score"]
    acc = {"nonmatch": [0, 0], "match": [0, 0]}
    tens = {"wrong": [0, 0], "correct": [0, 0]}
    for t in jl(f"runs/r8/sonnet_{pool}.jsonl"):
        for idx, g, lab in zip(t["idx"], t["group"], t[how]):
            b, r = S.get((t["problem_id"], idx, "noref")), S.get((t["problem_id"], idx, "ref"))
            if b is None:
                continue
            k = "correct" if lab else "wrong"
            tens[k][0] += 1
            tens[k][1] += b == 10
            if lab and g in acc and b == 10 and r is not None:
                acc[g][0] += 1
                acc[g][1] += r <= 3
    for g in acc:
        tot[g][0] += acc[g][0]
        tot[g][1] += acc[g][1]
    res[pool] = dict(
        acceptance={g: dict(scored_10_blind=v[0], scored_le3_with_reference=v[1], share=round(v[1] / v[0], 4) if v[0] else None) for g, v in acc.items()},
        blind_10_rate={k: dict(n=v[0], blind_10=v[1], share=round(v[1] / v[0], 4) if v[0] else None) for k, v in tens.items()})
res["pooled_acceptance"] = {g: dict(scored_10_blind=v[0], scored_le3_with_reference=v[1], share=round(v[1] / v[0], 4) if v[0] else None) for g, v in tot.items()}
json.dump(res, open(args.out, "w"), indent=1)
print(json.dumps(res, indent=1))
