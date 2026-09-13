# POST HOC (round-19 review, M1 part 2). Run from experiments/tfa-vs-judge. Writes papers/analysis/r20d_matched_acceptance.json.
# Does P3 hold beyond Sonnet 5? For each open judge on the constructed pools (full 64-candidate pools, any-format labels, exact
# scorer for Qwen2.5 and gemma-2), pick the lowest blind-score threshold t at which at most 3% of wrong answers score t or above
# (about Sonnet 5's rate for a blind 10). Among correct answers scored t or above blind, report the share scored 3 or below with the
# reference, for answers that differ from the reference and answers that match it, and the swap-free contrast between them.
import json

import numpy as np

S4 = "runs/r4/scores"
JUDGES = {
    "repl": {"Qwen2.5-7B": f"{S4}/repl__Qwen__Qwen2.5-7B-Instruct__{{}}_a.jsonl", "phi-4": "runs/bon_scores_repl/synthk__microsoft__phi-4__{}_a.jsonl"},
    "kpool": {"Qwen2.5-7B": f"{S4}/kstrat__Qwen__Qwen2.5-7B-Instruct__{{}}_a.jsonl", "phi-4": "runs/bon_scores_kstrat/synthk__microsoft__phi-4__{}_a.jsonl",
              "Qwen2.5-14B": f"{S4}/kstrat__Qwen__Qwen2.5-14B-Instruct__{{}}_a.jsonl", "gemma-2-9b": f"{S4}/kstrat__google__gemma-2-9b-it__{{}}_a.jsonl"},
}
TARGET = 0.03


def rows(f):
    return {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(f)}


res = {"target_wrong_pass_rate": TARGET}
for pool, js in JUDGES.items():
    LAB = {json.loads(l)["problem_id"]: json.loads(l) for l in open(f"runs/r8/lenient_{pool}.jsonl")}
    for jn, pat in js.items():
        b, r = rows(pat.format("noref")), rows(pat.format("ref"))
        W, C = [], []  # wrong blind scores; (blind, ref, group) for correct answers
        for pid, L in LAB.items():
            if pool == "kpool" and int(L["k"]) <= 1:
                continue
            if pid not in b or pid not in r:
                continue
            for bs, rs, lab, m in zip(b[pid], r[pid], L["lenient"], L["match"]):
                if bs is None or rs is None:
                    continue
                if lab:
                    C.append((bs, rs, "match" if m else "nonmatch"))
                else:
                    W.append(bs)
        W = np.array(W)
        grid = np.round(np.arange(5.0, 10.001, 0.05), 2)
        t = next((g for g in grid if (W >= g).mean() <= TARGET), None)
        out = dict(threshold=None if t is None else float(t), wrong_pass_rate=None if t is None else round(float((W >= t).mean()), 4), wrong_n=int(len(W)))
        if t is not None:
            for g in ("nonmatch", "match"):
                sel = [rs for bs, rs, gg in C if gg == g and bs >= t]
                out[g] = dict(n=len(sel), share_le3_with_reference=round(float(np.mean([x <= 3 for x in sel])), 4) if sel else None)
        res[f"{pool}|{jn}"] = out
json.dump(res, open("../../papers/analysis/r20d_matched_acceptance.json", "w"), indent=1)
print(json.dumps(res, indent=1))
