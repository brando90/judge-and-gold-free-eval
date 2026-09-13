# POST HOC (round-14 review). Run from experiments/tfa-vs-judge. Writes papers/analysis/r15_checks.json.
# Noise control for the Sonnet 5 (R8-A, API) "accepted blind, rejected with the reference" statistic: among correct
# answers scored 10 blind, the share scored <= 3 with the reference, separately for answers that differ from the
# reference (the reported statistic) and answers that match it (control), per pool.
import json


def jl(f):
    return [json.loads(l) for l in open(f)]


res = {}
for pool, how in (("mace", "oracle"), ("repl", "lenient"), ("kpool", "lenient")):
    S = {}
    for r in jl(f"runs/r8/sonnet_api/{pool}.jsonl"):
        if r.get("score") is not None and not r.get("error"):
            S[(r["problem_id"], r["idx"], r["cond"])] = r["score"]
    out = {}
    for grp in ("nonmatch", "match"):
        n10 = fell = n_any = fell_any = 0
        for t in jl(f"runs/r8/sonnet_{pool}.jsonl"):
            for idx, g, lab in zip(t["idx"], t["group"], t[how]):
                b, r = S.get((t["problem_id"], idx, "noref")), S.get((t["problem_id"], idx, "ref"))
                if not lab or g != grp or b is None or r is None:
                    continue
                n_any += 1
                fell_any += r <= 3
                if b == 10:
                    n10 += 1
                    fell += r <= 3
        out[grp] = dict(scored_10_blind=n10, share_of_10s_scored_le3_with_reference=round(fell / n10, 4) if n10 else None,
                        all_correct=n_any, share_scored_le3_with_reference=round(fell_any / n_any, 4) if n_any else None)
    res[pool] = out
json.dump(res, open("../../papers/analysis/r15_checks.json", "w"), indent=1)
print(json.dumps(res, indent=1))
