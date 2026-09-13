# R20 (papers/D-iclr/registration_round20.md): builds inputs for R20-A and R20-B from stored files, before any R20 call.
# Run from experiments/tfa-vs-judge.
#   R20-A retest pools: for each API judge (Sonnet 5 from R8-A, Opus 5 from R19-A) and each R8-A subsample, the correct answers
#     (matching or non-matching the reference) that the judge scored 10 on its first blind call -> runs/r20/retest_pools/<judge>_<pool>.jsonl
#   R20-B instruction score files: seeded with the judge's existing blind calls, so the harness adds only referenced calls
#     with the full-credit sentence -> runs/r20/<judge>_inst_api/<pool>.jsonl
import json
import os


def jl(f):
    return [json.loads(l) for l in open(f)]


LAB = {"mace": "oracle", "repl": "lenient", "kpool": "lenient"}
SRC = {"sonnet": "runs/r8/sonnet_api", "opus": "runs/r19/opus_api"}
os.makedirs("runs/r20/retest_pools", exist_ok=True)
for judge, src in SRC.items():
    for pool, how in LAB.items():
        S = {(r["problem_id"], r["idx"], r["cond"]): r["score"] for r in jl(f"{src}/{pool}.jsonl")
             if r.get("score") is not None and not r.get("error")}
        out = []
        for t in jl(f"runs/r8/sonnet_{pool}.jsonl"):
            keep = [j for j, (idx, g, lab) in enumerate(zip(t["idx"], t["group"], t[how]))
                    if lab and g in ("match", "nonmatch") and S.get((t["problem_id"], idx, "noref")) == 10]
            if keep:
                row = {k: t[k] for k in ("problem_id", "question", "ref")}
                for k in ("idx", "samples", "group", how):
                    row[k] = [t[k][j] for j in keep]
                out.append(row)
        with open(f"runs/r20/retest_pools/{judge}_{pool}.jsonl", "w") as f:
            for r in out:
                f.write(json.dumps(r) + "\n")
        print(f"retest pool {judge} {pool}: {len(out)} tasks, {sum(len(r['idx']) for r in out)} answers")
for judge, pools in (("sonnet", ("mace", "repl")), ("opus", ("mace",))):
    d = f"runs/r20/{judge}_inst_api"
    os.makedirs(d, exist_ok=True)
    for pool in pools:
        dst = f"{d}/{pool}.jsonl"
        if os.path.exists(dst):
            print("exists, not reseeded:", dst)
            continue
        n = 0
        with open(dst, "w") as f:
            for r in jl(f"{SRC[judge]}/{pool}.jsonl"):
                if r.get("cond") == "noref" and not r.get("error"):
                    f.write(json.dumps(r) + "\n")
                    n += 1
        print(f"seeded {dst} with {n} blind calls")
