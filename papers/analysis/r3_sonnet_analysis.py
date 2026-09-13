# FROZEN producer for R3-B (papers/D-iclr/registration_round3b.md), committed before any R3-B pool score exists.
# Run from experiments/tfa-vs-judge. Writes papers/analysis/r3_sonnet_results.json.
import json
import os

import numpy as np

NBOOT = 1000
OUT = "../../papers/analysis/r3_sonnet_results.json"
pool = [json.loads(l) for l in open("runs/r3/sonnet_rot.jsonl")]
ARMS = ("fast", "visible", "think")


def boot(x, seed=0):
    x = np.asarray(x, float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 3), [round(float(np.percentile(m, 2.5)), 3), round(float(np.percentile(m, 97.5)), 3)], len(x)]


def load(arm, cond):
    f = f"runs/r3/sonnet/{arm}__{cond}.jsonl"
    if not os.path.exists(f):
        return None
    scores, meta = {}, dict(rows=0, unparseable=0, errors=0)
    out_tok, think_tok = [], []
    for r in (json.loads(l) for l in open(f)):
        if r.get("error"):
            meta["errors"] += 1
            continue
        meta["rows"] += 1
        if r["score"] is None:
            meta["unparseable"] += 1
            continue
        scores[(r["problem_id"], r["idx"])] = r["score"]
        out_tok.append(r.get("output_tokens") or 0)
        think_tok.append(r.get("thinking_tokens") or 0)
    meta["output_tokens_mean"] = int(np.mean(out_tok)) if out_tok else None
    meta["thinking_tokens_mean"] = int(np.mean(think_tok)) if think_tok else None
    return scores, meta


res, per = {}, {}
for arm in ARMS:
    a, b = load(arm, "ref"), load(arm, "refrot")
    if a is None or b is None:
        res[arm] = "pre-data"
        continue
    (sref, mref), (srot, mrot) = a, b
    ch = {"gainer": {}, "loser": {}, "placebo": {}}
    fr = {}
    for t in pool:
        pid = t["problem_id"]
        rej = []
        for idx, c in zip(t["idx"], t["cls"]):
            x, y = sref.get((pid, idx)), srot.get((pid, idx))
            if x is not None and y is not None:
                ch[c][pid] = y - x
            if c in ("gainer", "placebo") and x is not None:  # does not match the original reference
                rej.append(x <= 3)
            if c in ("loser", "placebo") and y is not None:  # does not match the rotated reference
                rej.append(y <= 3)
        if rej:
            fr[pid] = float(np.mean(rej))
    per[arm] = dict(ch=ch, fr=fr)
    res[arm] = dict(rot={c: boot(list(v.values())) for c, v in ch.items()}, false_reject=boot(list(fr.values())),
                    meta=dict(ref=mref, refrot=mrot))


def paired(x, y):
    return boot([x[p] - y[p] for p in x if p in y])


if all(isinstance(res.get(a), dict) for a in ARMS):
    res["think_minus_fast_loser"] = paired(per["think"]["ch"]["loser"], per["fast"]["ch"]["loser"])
    res["visible_minus_fast_loser"] = paired(per["visible"]["ch"]["loser"], per["fast"]["ch"]["loser"])
    res["think_minus_fast_false_reject"] = paired(per["think"]["fr"], per["fast"]["fr"])
    res["P_R3B1"] = bool(res["fast"]["rot"]["loser"][1][1] < 0)
    res["P_R3B2"] = bool(res["think_minus_fast_loser"][1][0] > 0)
    res["P_R3B3"] = bool(res["think_minus_fast_false_reject"][1][1] < 0)
    res["P_R3B4"] = bool(res["visible_minus_fast_loser"][1][0] > 0)
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
