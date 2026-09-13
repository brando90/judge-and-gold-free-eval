# POST HOC (round-16 review). Run from experiments/tfa-vs-judge. Writes papers/analysis/r16d_sonnet_noise_floor.json.
# A noise floor for the Sonnet 5 acceptance statistic, from calls both interfaces completed on the replication subsamples
# (R8-A: API run; the disclosed partial CLI run). Among correct answers the API scored 10 blind, the share that a second,
# independent blind call (CLI) scores 3 or below, against the share the API scores 3 or below once shown the reference.
# The two interfaces differ (67% exact agreement), so this cross-interface rate is an upper bound on same-interface noise.
import json


def load(f):
    out = {}
    for l in open(f):
        r = json.loads(l)
        if r.get("score") is not None and not r.get("error"):
            out[(r["problem_id"], r["idx"], r["cond"])] = r["score"]
    return out


cli, api = load("runs/r8/sonnet/repl.jsonl"), load("runs/r8/sonnet_api/repl.jsonl")
res = {}
for grp in ("nonmatch", "match"):
    n = retest_low = ref_low = 0
    for t in (json.loads(l) for l in open("runs/r8/sonnet_repl.jsonl")):
        for idx, g, lab in zip(t["idx"], t["group"], t["lenient"]):
            k_b, k_r = (t["problem_id"], idx, "noref"), (t["problem_id"], idx, "ref")
            if not lab or g != grp or api.get(k_b) != 10 or k_b not in cli or k_r not in api:
                continue
            n += 1
            retest_low += cli[k_b] <= 3
            ref_low += api[k_r] <= 3
    res[grp] = dict(api_blind_10_with_cli_blind=n, share_cli_blind_le3=round(retest_low / n, 4) if n else None,
                    share_api_referenced_le3=round(ref_low / n, 4) if n else None, cli_blind_le3=retest_low, api_referenced_le3=ref_low)
json.dump(res, open("../../papers/analysis/r16d_sonnet_noise_floor.json", "w"), indent=1)
print(json.dumps(res, indent=1))
