# POST HOC (round-19 review, M1 part 2). Run from experiments/tfa-vs-judge. Writes papers/analysis/r20f_qwen3_acceptance.json.
# The acceptance readout for Qwen3-8B and Qwen3-14B, thinking off (explanation first) and on, on the 81-task MACE subsample with
# wrong answers (runs/r3/macesub.jsonl; groups match / nonmatch / invalid): the share of wrong answers scored 10 blind, and among
# correct answers scored 10 blind, the share scored 3 or below with the reference, non-matching against matching.
import json

pool = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/r3/macesub.jsonl")}
FILES = {("Qwen3-8B", "off"): "runs/r3/scores/macesub__thinkoff__Qwen__Qwen3-8B__{}.jsonl",
         ("Qwen3-8B", "on"): "runs/r3/scores/macesub__thinkon__Qwen__Qwen3-8B__{}.jsonl",
         ("Qwen3-14B", "off"): "runs/r4/qwen3_14b/macesub__thinkoff__Qwen__Qwen3-14B__{}.jsonl",
         ("Qwen3-14B", "on"): "runs/r4/qwen3_14b/macesub__thinkon__Qwen__Qwen3-14B__{}.jsonl"}


def load(f):
    out = {}
    for l in open(f):
        r = json.loads(l)
        for idx, s in zip(r["idx"], r["score"]):
            out[(r["problem_id"], idx)] = s
    return out


res = {}
for (j, mode), pat in FILES.items():
    B, R = load(pat.format("noref")), load(pat.format("ref"))
    wrong = [0, 0]
    acc = {"nonmatch": [0, 0], "match": [0, 0]}
    for pid, t in pool.items():
        for idx, g in zip(t["idx"], t["group"]):
            b, r = B.get((pid, idx)), R.get((pid, idx))
            if b is None:
                continue
            if g == "invalid":
                wrong[0] += 1
                wrong[1] += b == 10
            elif b == 10 and r is not None:
                acc[g][0] += 1
                acc[g][1] += r <= 3
    res[f"{j}|thinking {mode}"] = dict(wrong_n=wrong[0], wrong_blind_10_share=round(wrong[1] / wrong[0], 4) if wrong[0] else None,
                                       **{g: dict(scored_10_blind=v[0], share_le3_with_reference=round(v[1] / v[0], 4) if v[0] else None) for g, v in acc.items()})
json.dump(res, open("../../papers/analysis/r20f_qwen3_acceptance.json", "w"), indent=1)
print(json.dumps(res, indent=1))
