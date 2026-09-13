# R20-C (papers/D-iclr/registration_round20.md): after generation, builds one judging pool with one answer per generator per
# question (Llama-3.1-8B-Instruct: the first stored sample of runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl;
# API generators: runs/r20/mace_gen/<model>.jsonl). Labels use the MACE oracle and matching rule of mace_oracle.py and
# r8_build_sonnet_pools.py: an answer (last \boxed{} content, else the last 200 characters, normalized) is correct if it equals or
# contains a listed answer (entries longer than three characters) and matches the reference by the same test on the reference alone.
# Run from experiments/tfa-vs-judge. Output: runs/r20/mace_gen/pool.jsonl (idx = generator index, in GENERATORS order).
import json
import re

GENERATORS = ["meta-llama__Llama-3.1-8B-Instruct", "claude-haiku-4-5-20251001", "claude-sonnet-5", "claude-opus-5"]


def norm(a):
    return re.sub(r"[^a-z0-9]+", "", a.strip().casefold())


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


def contains(a, v):
    na, nv = norm(a), norm(v)
    return na == nv or (len(nv) > 3 and nv in na)


tasks = {t["problem_id"]: t for t in (json.loads(l) for l in open("runs/mace_tasks.jsonl"))}
llama = {r["problem_id"]: r["samples"][0] for r in (json.loads(l) for l in open("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"))}
gen = {g: {} for g in GENERATORS[1:]}
for g in GENERATORS[1:]:
    for l in open(f"runs/r20/mace_gen/{g}.jsonl"):
        r = json.loads(l)
        if r.get("sample") and not r.get("error"):
            gen[g][r["problem_id"]] = r["sample"]
out = []
for pid in sorted(gen["claude-sonnet-5"]):
    if not all(pid in gen[g] for g in GENERATORS[1:]) or pid not in llama:
        continue
    t = tasks[pid]
    samples = [llama[pid]] + [gen[g][pid] for g in GENERATORS[1:]]
    oracle, group = [], []
    for s in samples:
        a = boxed(s) or s[-200:]
        ok = int(any(contains(a, v) for v in t["valid_answers"]))
        oracle.append(ok)
        group.append("invalid" if not ok else ("match" if contains(a, t["ref_answer"]) else "nonmatch"))
    out.append(dict(problem_id=pid, question=t["question"], ref=t["ref_answer"], k=int(t["k"]), idx=list(range(len(GENERATORS))),
                    generators=GENERATORS, samples=samples, oracle=oracle, group=group))
with open("runs/r20/mace_gen/pool.jsonl", "w") as f:
    for r in out:
        f.write(json.dumps(r) + "\n")
print(f"leaderboard pool: {len(out)} questions x {len(GENERATORS)} generators")
for i, g in enumerate(GENERATORS):
    print(f"  {g}: correct {sum(r['oracle'][i] for r in out)}, correct and differing from the reference {sum(r['group'][i] == 'nonmatch' for r in out)}")
