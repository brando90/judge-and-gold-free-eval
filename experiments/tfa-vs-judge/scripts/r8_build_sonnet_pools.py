# R8-A pools (papers/D-iclr/registration_round8.md). Deterministic; run before any R8-A judging. Run from experiments/tfa-vs-judge.
# Three pools of 16-candidate subsamples that include wrong answers, for Claude Sonnet 5 through the CLI:
#   repl  : replication pool, format-lenient labels (runs/r8/lenient_repl.jsonl), tasks with lenient pass rate in [0.2, 0.8]
#           and at least one matching-correct, non-matching-correct, and wrong sample; 8 tasks per constraint family.
#   mace  : MACE River and Language, k > 1, pass rate in [0.05, 0.95] (the registered MACE band); groups as in
#           r7_posthoc.py (match = boxed answer or last 200 characters equals or contains the reference); 40 tasks.
#   kpool : k-pool, k > 1, lenient labels, lenient pass rate in [0.2, 0.8]; every eligible task.
# Per task, 16 of the 64 samples are drawn without replacement, redrawn until the subsample holds at least one sample of
# each group (at most 200 draws). Generator: numpy default_rng(8), consumed in the order repl, mace, kpool.
import ast
import json
import os
import re

import numpy as np

rng = np.random.default_rng(8)
os.makedirs("runs/r8", exist_ok=True)


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


def mnorm(a):
    return re.sub(r"[^a-z0-9]+", "", (a or "").strip().casefold())


def subsample(group):
    for _ in range(200):
        s = sorted(rng.choice(len(group), size=16, replace=False).tolist())
        if {"match", "nonmatch", "invalid"} <= {group[i] for i in s}:
            return s
    return None


def write(name, items):
    with open(f"runs/r8/sonnet_{name}.jsonl", "w") as f:
        for t in items:
            f.write(json.dumps(t) + "\n")
    print(f"[r8 pools] {name}: {len(items)} tasks, {sum(len(t['samples']) for t in items)} candidates")


def constructed(poolfile, labfile, sel):
    src = {json.loads(l)["problem_id"]: json.loads(l) for l in open(poolfile)}
    lab = {json.loads(l)["problem_id"]: json.loads(l) for l in open(labfile)}
    elig = []
    for pid in sorted(src):
        t, L = src[pid], lab[pid]
        grp = ["invalid" if not o else ("match" if m else "nonmatch") for o, m in zip(L["lenient"], L["match"])]
        if sel(t) and 0.2 <= np.mean(L["lenient"]) <= 0.8 and {"match", "nonmatch", "invalid"} <= set(grp):
            p = t["params"] if isinstance(t["params"], dict) else ast.literal_eval(t["params"])
            elig.append((p["fam"], t, L, grp))
    return elig


def pack(t, L, grp, s, ref):
    return dict(problem_id=t["problem_id"], question=t["question"], ref=ref, k=t["k"], idx=s, samples=[t["samples"][i] for i in s],
                group=[grp[i] for i in s], lenient=[L["lenient"][i] for i in s], strict=[L["strict"][i] for i in s])


# repl: 8 tasks per family
elig = constructed("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl", "runs/r8/lenient_repl.jsonl", lambda t: True)
items = []
for fam in ("crt", "subset", "goldbach", "divcount", "digitsum"):
    cand = [e for e in elig if e[0] == fam]
    for j in sorted(rng.choice(len(cand), size=min(8, len(cand)), replace=False).tolist()):
        _, t, L, grp = cand[j]
        s = subsample(grp)
        if s is not None:
            items.append(pack(t, L, grp, s, t["ref_answer"]))
print("[r8 pools] repl eligible per family:", {f: sum(e[0] == f for e in elig) for f in ("crt", "subset", "goldbach", "divcount", "digitsum")})
write("repl", items)

# mace
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/mace_tasks.jsonl")}
elig = []
for t in sorted((json.loads(l) for l in open("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl")), key=lambda x: x["problem_id"]):
    if "oracle" not in t:
        continue
    tt = tasks[t["problem_id"]]
    p = tt["params"] if isinstance(tt["params"], dict) else ast.literal_eval(tt["params"])
    if p["domain"] not in ("River", "Language") or int(tt["k"]) == 1 or not (0.05 <= np.mean(t["oracle"]) <= 0.95):
        continue
    refn = mnorm(tt["ref_answer"])
    grp = []
    for s_, o in zip(t["samples"], t["oracle"]):
        a = mnorm(boxed(s_) or s_[-200:])
        grp.append("invalid" if not o else ("match" if (a == refn or (len(refn) > 3 and refn in a)) else "nonmatch"))
    if {"match", "nonmatch", "invalid"} <= set(grp):
        elig.append((t, tt, grp))
items = []
for j in sorted(rng.choice(len(elig), size=min(40, len(elig)), replace=False).tolist()):
    t, tt, grp = elig[j]
    s = subsample(grp)
    if s is not None:
        items.append(dict(problem_id=t["problem_id"], question=tt.get("question", t.get("question")), ref=tt["ref_answer"], k=int(tt["k"]),
                          idx=s, samples=[t["samples"][i] for i in s], group=[grp[i] for i in s], oracle=[t["oracle"][i] for i in s]))
print("[r8 pools] mace eligible:", len(elig))
write("mace", items)

# kpool k>1
elig = constructed("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl", "runs/r8/lenient_kpool.jsonl", lambda t: int(t["k"]) > 1)
items = []
for _, t, L, grp in elig:
    s = subsample(grp)
    if s is not None:
        items.append(pack(t, L, grp, s, t["ref_answer"]))
write("kpool", items)
