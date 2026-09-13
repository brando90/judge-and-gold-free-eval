# POST HOC (R19-A follow-up; not registered). Run from experiments/tfa-vs-judge after R19-A finishes.
#   python ../../papers/analysis/r19c_opus_visible_reasoning.py --scores runs/r19/opus_api --out ../../papers/analysis/r19c_opus_visible_reasoning.json
# Claude Opus 5 was called with thinking disabled and a score-only rubric, but on some calls it writes visible reasoning before
# the score. Per pool: (a) the share of calls with visible reasoning (more than 8 output tokens), blind and with the reference;
# (b) the false-rejection rise (share of non-matching correct answers scored 3 or below, referenced minus blind, pooled over answers)
# for all answers and for answers whose two calls both gave a bare score; (c) the acceptance readout (among correct answers scored 10
# blind, share scored 3 or below with the reference, non-matching vs matching) under the same restriction.
# Labels: any-format for the replication pool and k-pool, the answer lists for MACE (as in r8_sonnet_analysis.py).
import argparse
import json
import os

ap = argparse.ArgumentParser()
ap.add_argument("--scores", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()
REASONED = 8


def jl(f):
    return [json.loads(l) for l in open(f)]


def share(n, d):
    return round(n / d, 4) if d else None


res = {}
for pool, how in (("mace", "oracle"), ("repl", "lenient"), ("kpool", "lenient")):
    f = os.path.join(args.scores, f"{pool}.jsonl")
    if not os.path.exists(f):
        continue
    calls = {}
    for r in jl(f):
        if r.get("score") is not None and not r.get("error"):
            calls[(r["problem_id"], r["idx"], r["cond"])] = (r["score"], r.get("output_tokens", 0) > REASONED)
    vis = {"noref": [0, 0], "ref": [0, 0]}
    for (_, _, cond), (_, v) in calls.items():
        vis[cond][0] += 1
        vis[cond][1] += v
    out = {"visible_reasoning_share": {c: share(v[1], v[0]) for c, v in vis.items()}}
    for subset in ("all", "bare_both"):
        fr = [0, 0, 0]  # n non-matching correct, blind <= 3, referenced <= 3
        acc = {"nonmatch": [0, 0], "match": [0, 0]}
        for t in jl(f"runs/r8/sonnet_{pool}.jsonl"):
            for idx, g, lab in zip(t["idx"], t["group"], t[how]):
                b, r = calls.get((t["problem_id"], idx, "noref")), calls.get((t["problem_id"], idx, "ref"))
                if not lab or b is None or r is None:
                    continue
                if subset == "bare_both" and (b[1] or r[1]):
                    continue
                if g == "nonmatch":
                    fr[0] += 1
                    fr[1] += b[0] <= 3
                    fr[2] += r[0] <= 3
                if g in acc and b[0] == 10:
                    acc[g][0] += 1
                    acc[g][1] += r[0] <= 3
        out[subset] = dict(nonmatch_correct=fr[0], false_rejection_blind=share(fr[1], fr[0]), false_rejection_ref=share(fr[2], fr[0]),
                           false_rejection_change=round(share(fr[2], fr[0]) - share(fr[1], fr[0]), 4) if fr[0] else None,
                           acceptance={g: dict(scored_10_blind=v[0], share_le3_with_reference=share(v[1], v[0])) for g, v in acc.items()})
    res[pool] = out
json.dump(res, open(args.out, "w"), indent=1)
print(json.dumps(res, indent=1))
