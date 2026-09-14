# POST HOC (round-21 review, M5). Run from experiments/tfa-vs-judge. Writes papers/analysis/r22c_acceptance_bins.json.
# Equation 1 predicts that under verification failure the referenced rejection of correct answers that differ from the reference
# falls toward zero as the judge's own confidence rises (lambda(v) = lambda0 (1 - v)); under agreement it stays up. Here, by blind
# score bin: the share of correct answers scored 3 or below with the reference, for answers that differ from the reference and
# answers that match it. Open judges (expected scores): MACE k > 1 (all stored Llama-3.1-8B samples; answer lists; containment
# match) and the constructed pools (any-format labels), bins [0,5), [5,7), [7,9), [9,9.6), [9.6,9.8), [9.8,10]. API judges (integer
# scores) on their 16-candidate subsamples: bins <=6, 7-8, 9, 10. Counts are answers.
import ast
import json
import re

EDGES_OPEN = [(0, 5), (5, 7), (7, 9), (9, 9.6), (9.6, 9.8), (9.8, 10.01)]
EDGES_API = [(0, 7), (7, 9), (9, 10), (10, 10.01)]


def mnorm(a):
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


def binned(items, edges):  # items: (blind, referenced, group)
    out = []
    for lo, hi in edges:
        row = {"bin": [lo, min(hi, 10)]}
        for g in ("nonmatch", "match"):
            sel = [rs for bs, rs, gg in items if gg == g and lo <= bs < hi]
            row[g] = dict(n=len(sel), share_le3_with_reference=round(sum(x <= 3 for x in sel) / len(sel), 4) if sel else None)
        out.append(row)
    return out


res = {}
# open judges, MACE k > 1
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/mace_tasks.jsonl")}
pool = []
for t in map(json.loads, open("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl")):
    tt = tasks[t["problem_id"]]
    p = tt["params"] if isinstance(tt["params"], dict) else ast.literal_eval(tt["params"])
    if p["domain"] in ("River", "Language") and int(tt["k"]) > 1 and "oracle" in t:
        refn = mnorm(tt["ref_answer"])
        t["match"] = [int(bool(o) and (mnorm(boxed(s) or s[-200:]) == refn or (len(refn) > 3 and refn in mnorm(boxed(s) or s[-200:]))))
                      for s, o in zip(t["samples"], t["oracle"])]
        pool.append(t)
MJ = {"Qwen2.5-7B": "runs/r4/scores/mace__Qwen__Qwen2.5-7B-Instruct__{}_a.jsonl", "phi-4": "runs/bon_scores_mace/mace__microsoft__phi-4__{}_a.jsonl"}
for jn, pat in MJ.items():
    b = {r["problem_id"]: r["escore"] for r in map(json.loads, open(pat.format("noref")))}
    r = {x["problem_id"]: x["escore"] for x in map(json.loads, open(pat.format("ref")))}
    items = []
    for t in pool:
        pid = t["problem_id"]
        if pid in b and pid in r:
            for bs, rs, o, m in zip(b[pid], r[pid], t["oracle"], t["match"]):
                if bs is not None and rs is not None and o:
                    items.append((bs, rs, "match" if m else "nonmatch"))
    res[f"mace|{jn}"] = binned(items, EDGES_OPEN)
# open judges, constructed pools
S4 = "runs/r4/scores"
CJ = {"repl": {"Qwen2.5-7B": f"{S4}/repl__Qwen__Qwen2.5-7B-Instruct__{{}}_a.jsonl", "phi-4": "runs/bon_scores_repl/synthk__microsoft__phi-4__{}_a.jsonl"},
      "kpool": {"Qwen2.5-7B": f"{S4}/kstrat__Qwen__Qwen2.5-7B-Instruct__{{}}_a.jsonl", "phi-4": "runs/bon_scores_kstrat/synthk__microsoft__phi-4__{}_a.jsonl",
                "Qwen2.5-14B": f"{S4}/kstrat__Qwen__Qwen2.5-14B-Instruct__{{}}_a.jsonl", "gemma-2-9b": f"{S4}/kstrat__google__gemma-2-9b-it__{{}}_a.jsonl"}}
for pn, js in CJ.items():
    LAB = {x["problem_id"]: x for x in map(json.loads, open(f"runs/r8/lenient_{pn}.jsonl"))}
    for jn, pat in js.items():
        b = {x["problem_id"]: x["escore"] for x in map(json.loads, open(pat.format("noref")))}
        r = {x["problem_id"]: x["escore"] for x in map(json.loads, open(pat.format("ref")))}
        items = []
        for pid, L in LAB.items():
            if (pn == "kpool" and int(L["k"]) <= 1) or pid not in b or pid not in r:
                continue
            for bs, rs, lab, m in zip(b[pid], r[pid], L["lenient"], L["match"]):
                if bs is not None and rs is not None and lab:
                    items.append((bs, rs, "match" if m else "nonmatch"))
        res[f"{pn}|{jn}"] = binned(items, EDGES_OPEN)
# API judges on their subsamples
for jn, d in (("Sonnet 5", "runs/r8/sonnet_api"), ("Opus 5", "runs/r19/opus_api")):
    for pn, how in (("mace", "oracle"), ("repl", "lenient"), ("kpool", "lenient")):
        S = {}
        for l in open(f"{d}/{pn}.jsonl"):
            x = json.loads(l)
            if x.get("score") is not None and not x.get("error"):
                S[(x["problem_id"], x["idx"], x["cond"])] = x["score"]
        items = []
        for t in map(json.loads, open(f"runs/r8/sonnet_{pn}.jsonl")):
            for i, lab, g in zip(t["idx"], t[how], t["group"]):
                bs, rs = S.get((t["problem_id"], i, "noref")), S.get((t["problem_id"], i, "ref"))
                if lab and bs is not None and rs is not None:
                    items.append((bs, rs, "match" if g == "match" else "nonmatch"))
        res[f"{pn}|{jn}"] = binned(items, EDGES_API)
json.dump(res, open("../../papers/analysis/r22c_acceptance_bins.json", "w"), indent=1)
for k, v in res.items():
    print(k, [(row["bin"], row["nonmatch"]["n"], row["nonmatch"]["share_le3_with_reference"], row["match"]["share_le3_with_reference"]) for row in v])
