# POST HOC (round-17 review). Run from experiments/tfa-vs-judge. Writes papers/analysis/r19_sonnet_wrong_tens.json.
# Is a blind 10 from Sonnet 5 close to verification? On the R8-A API subsamples (16 candidates per task, with wrong
# answers), the share of wrong answers scored 10 (and 9 or more) blind, against the share of correct answers.
# Labels: any-format for the replication pool and k-pool, the answer lists for MACE (as in r8_sonnet_analysis.py).
import json


def jl(f):
    return [json.loads(l) for l in open(f)]


res = {}
for pool, how in (("mace", "oracle"), ("repl", "lenient"), ("kpool", "lenient")):
    S = {(r["problem_id"], r["idx"]): r["score"] for r in jl(f"runs/r8/sonnet_api/{pool}.jsonl")
         if r.get("cond") == "noref" and r.get("score") is not None and not r.get("error")}
    c = {"wrong": [0, 0, 0], "correct": [0, 0, 0]}  # n, scored 10, scored >= 9
    for t in jl(f"runs/r8/sonnet_{pool}.jsonl"):
        for idx, lab in zip(t["idx"], t[how]):
            s = S.get((t["problem_id"], idx))
            if s is None:
                continue
            k = "correct" if lab else "wrong"
            c[k][0] += 1
            c[k][1] += s == 10
            c[k][2] += s >= 9
    res[pool] = {k: dict(n=v[0], share_blind_10=round(v[1] / v[0], 4), share_blind_ge9=round(v[2] / v[0], 4), blind_10=v[1]) for k, v in c.items()}
    tens_wrong, tens_right = c["wrong"][1], c["correct"][1]
    res[pool]["share_of_blind_10s_that_are_wrong"] = round(tens_wrong / (tens_wrong + tens_right), 4)
json.dump(res, open("../../papers/analysis/r19_sonnet_wrong_tens.json", "w"), indent=1)
print(json.dumps(res, indent=1))
