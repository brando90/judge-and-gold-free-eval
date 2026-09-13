# POST HOC (round-12 review). Run from experiments/tfa-vs-judge. Writes papers/analysis/r12_checks.json.
#  (a) Sonnet 5 (R8-A, API): among correct answers that differ from the reference and were scored >= 7 blind, how many
#      were scored 10 blind, and what share of those fell to <= 3 with the reference.
#  (b) Where does the selection loss sit? Per task (any-format labels), whether some correct candidate matches the
#      reference; best-of-64 accuracy change (referenced minus blind, ties averaged) by stratum, k-pool k>1 and the
#      replication pool, tasks with any-format pass rate in [0.2, 0.8].
import json

import numpy as np

NBOOT = 2000


def jl(f):
    return [json.loads(l) for l in open(f)]


def rows(f):
    return {r["problem_id"]: r["escore"] for r in jl(f)}


def boot(x, seed=0):
    x = np.asarray(x, float)
    if len(x) < 2:
        return [round(float(x.mean()), 4) if len(x) else None, None, int(len(x))]
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


def sel_acc(scores, oracle):
    s = np.array([-np.inf if v is None else v for v in scores], float)
    o = np.asarray(oracle, float)
    return float(o[np.isclose(s, s.max(), rtol=0, atol=1e-9)].mean())


res = {}
# (a)
res["sonnet_blind_ten"] = {}
for pool, how in (("mace", "oracle"), ("repl", "lenient"), ("kpool", "lenient")):
    S = {}
    for r in jl(f"runs/r8/sonnet_api/{pool}.jsonl"):
        if r.get("score") is not None and not r.get("error"):
            S[(r["problem_id"], r["idx"], r["cond"])] = r["score"]
    n7 = n10 = fell10 = fell7 = 0
    for t in jl(f"runs/r8/sonnet_{pool}.jsonl"):
        for idx, g, lab in zip(t["idx"], t["group"], t[how]):
            b, r = S.get((t["problem_id"], idx, "noref")), S.get((t["problem_id"], idx, "ref"))
            if not lab or g != "nonmatch" or b is None or r is None or b < 7:
                continue
            n7 += 1
            fell7 += r <= 3
            if b == 10:
                n10 += 1
                fell10 += r <= 3
    res["sonnet_blind_ten"][pool] = dict(accepted_ge7=n7, share_scored_10_blind=round(n10 / n7, 4) if n7 else None,
                                         scored_10_blind=n10, share_of_10s_scored_le3_with_reference=round(fell10 / n10, 4) if n10 else None,
                                         share_of_ge7_scored_le3=round(fell7 / n7, 4) if n7 else None)
# (b)
S4 = "runs/r4/scores"
JUD = {"kpool": {"Qwen2.5-7B": f"{S4}/kstrat__Qwen__Qwen2.5-7B-Instruct__{{}}_a.jsonl", "phi-4": "runs/bon_scores_kstrat/synthk__microsoft__phi-4__{}_a.jsonl",
                 "Qwen2.5-14B": f"{S4}/kstrat__Qwen__Qwen2.5-14B-Instruct__{{}}_a.jsonl", "gemma-2-9b": f"{S4}/kstrat__google__gemma-2-9b-it__{{}}_a.jsonl"},
       "repl": {"Qwen2.5-7B": f"{S4}/repl__Qwen__Qwen2.5-7B-Instruct__{{}}_a.jsonl", "phi-4": "runs/bon_scores_repl/synthk__microsoft__phi-4__{}_a.jsonl"}}
res["selection_by_match_presence"] = {}
for pool, js in JUD.items():
    LAB = {r["problem_id"]: r for r in jl(f"runs/r8/lenient_{pool}.jsonl")}
    for jn, pat in js.items():
        b, r = rows(pat.format("noref")), rows(pat.format("ref"))
        strata = {"matching_correct_present": [], "no_matching_correct": []}
        for pid, L in LAB.items():
            if pool == "kpool" and int(L["k"]) <= 1:
                continue
            if pid not in b or pid not in r or not (0.2 <= np.mean(L["lenient"]) <= 0.8):
                continue
            has = any(l and m for l, m in zip(L["lenient"], L["match"]))
            d = sel_acc(r[pid], L["lenient"]) - sel_acc(b[pid], L["lenient"])
            strata["matching_correct_present" if has else "no_matching_correct"].append(d)
        res["selection_by_match_presence"][f"{pool}|{jn}"] = {k: boot(v) for k, v in strata.items()}
json.dump(res, open("../../papers/analysis/r12_checks.json", "w"), indent=1)
print(json.dumps(res, indent=1))
