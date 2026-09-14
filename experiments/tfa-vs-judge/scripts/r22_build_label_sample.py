# R22-A (papers/D-iclr/registration_round22.md): stratified sample of unboxed replies for a frontier-model label audit.
# From the replication pool and the k-pool, every reply without \boxed{ is grouped by pool and any-format label
# (runs/r8/lenient_{repl,kpool}.jsonl); 50 per stratum are drawn with random.Random(22). Run from experiments/tfa-vs-judge.
# Output: runs/r22/label_sample.jsonl rows {pool, problem_id, idx, question, reply, params, registered, any_format, qwen14b,
# stratum, stratum_size}.
import ast
import json
import os
import random

POOLS = {"repl": "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl",
         "kpool": "runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl"}
PER = 50
rng = random.Random(22)
os.makedirs("runs/r22", exist_ok=True)
rows = []
for name, f in POOLS.items():
    lab = {json.loads(l)["problem_id"]: json.loads(l) for l in open(f"runs/r8/lenient_{name}.jsonl")}
    mod = {json.loads(l)["problem_id"]: json.loads(l) for l in open(f"runs/r8/model_{name}.jsonl")}
    strata = {1: [], 0: []}
    for t in (json.loads(l) for l in open(f)):
        L, M = lab[t["problem_id"]], mod[t["problem_id"]]
        p = t["params"] if isinstance(t["params"], dict) else ast.literal_eval(t["params"])
        for i, s in enumerate(t["samples"]):
            if "\\boxed{" in s:
                continue
            strata[int(L["lenient"][i])].append(dict(pool=name, problem_id=t["problem_id"], idx=i, question=t["question"], reply=s, params=p,
                                                     registered=int(bool(t["oracle"][i])), any_format=int(L["lenient"][i]), qwen14b=int(M["model"][i])))
    for lab_value, items in strata.items():
        for r in rng.sample(items, PER):
            rows.append(dict(r, stratum=f"{name}|{'correct' if lab_value else 'wrong'}", stratum_size=len(items)))
with open("runs/r22/label_sample.jsonl", "w") as g:
    for r in rows:
        g.write(json.dumps(r) + "\n")
print("label sample:", len(rows), {s: next(r["stratum_size"] for r in rows if r["stratum"] == s) for s in sorted({r["stratum"] for r in rows})})
