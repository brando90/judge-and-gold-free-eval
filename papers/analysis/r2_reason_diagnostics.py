# POST HOC diagnostics for R2-B (no registration weight). Run from experiments/tfa-vs-judge.
# Per protocol / pool / condition: mean score of valid and invalid samples, share of valid samples at the
# modal score, mean generated tokens, and the share of replies whose final text mentions "reference".
import collections
import json

import numpy as np

OUT = "../../papers/analysis/r2_reason_diagnostics.json"
pools = {"rot": {r["problem_id"]: r for r in (json.loads(l) for l in open("runs/r2/rot_sub.jsonl"))},
         "ksub": {r["problem_id"]: r for r in (json.loads(l) for l in open("runs/r2/ksub.jsonl"))}}
res = {}
for proto, judge in (("reason", "Qwen__Qwen3-8B"), ("mtbench", "Qwen__Qwen2.5-7B-Instruct")):
    for pool, conds in (("rot", ("noref", "ref", "refrot")), ("ksub", ("noref", "ref"))):
        for c in conds:
            rows = [json.loads(l) for l in open(f"runs/r2/scores/{pool}__{proto}__{judge}__{c}.jsonl")]
            val, inv, tok, men = [], [], [], []
            for r in rows:
                orc = dict(zip(pools[pool][r["problem_id"]]["idx"], pools[pool][r["problem_id"]]["oracle"]))
                for idx, s, n, t in zip(r["idx"], r["score"], r["n_tokens"], r["tail"]):
                    tok.append(n)
                    men.append("reference" in t.lower())
                    if s is not None:
                        (val if orc[idx] else inv).append(s)
            top = collections.Counter(val).most_common(1)[0]
            res[f"{proto}|{pool}|{c}"] = dict(
                n_valid=len(val), valid_mean=round(float(np.mean(val)), 2), valid_modal_score=top[0],
                valid_share_modal=round(top[1] / len(val), 3), n_invalid=len(inv),
                invalid_mean=round(float(np.mean(inv)), 2) if inv else None,
                tokens_mean=int(round(float(np.mean(tok)))), mention_reference=round(float(np.mean(men)), 3))
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
