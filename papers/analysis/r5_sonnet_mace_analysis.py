# FROZEN producer for R5-A (papers/D-iclr/registration_round5.md), committed before any R5-A score exists.
# Run from experiments/tfa-vs-judge. Writes papers/analysis/r5_sonnet_mace_results.json.
import json
import os

import numpy as np

NBOOT = 1000
OUT = "../../papers/analysis/r5_sonnet_mace_results.json"
pool = [json.loads(l) for l in open("runs/r5/sonnet_mace.jsonl")]


def boot(x, seed=0):
    x = np.asarray([v for v in x if v is not None], float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 3), [round(float(np.percentile(m, 2.5)), 3), round(float(np.percentile(m, 97.5)), 3)], int(len(x))]


def load(arm, cond):
    f = f"runs/r5/sonnet_mace/{arm}__{cond}.jsonl"
    if not os.path.exists(f):
        return None, None
    sc, meta = {}, dict(rows=0, errors=0, unparseable=0, out_tok=[], think_tok=[])
    for r in (json.loads(l) for l in open(f)):
        if r.get("error"):
            meta["errors"] += 1
            continue
        meta["rows"] += 1
        if r["score"] is None:
            meta["unparseable"] += 1
            continue
        sc[(r["problem_id"], r["group"])] = r["score"]
        meta["out_tok"].append(r.get("output_tokens") or 0)
        meta["think_tok"].append(r.get("thinking_tokens") or 0)
    meta["output_tokens_mean"] = int(np.mean(meta.pop("out_tok"))) if meta["rows"] - meta["unparseable"] > 0 else None
    tt = meta.pop("think_tok")
    meta["thinking_tokens_mean"] = int(np.mean(tt)) if tt else None
    return sc, meta


res, per = {}, {}
for arm in ("fast", "think"):
    r, mr = load(arm, "ref")
    b, mb = load(arm, "noref")
    if r is None or b is None:
        res[arm] = "pre-data"
        continue
    md, frd, ver = {}, {}, {}
    for t in pool:
        pid = t["problem_id"]
        g = lambda sc, grp: sc.get((pid, grp))
        if None not in (g(r, "match"), g(r, "nonmatch"), g(b, "match"), g(b, "nonmatch")):
            md[pid] = (g(r, "match") - g(r, "nonmatch")) - (g(b, "match") - g(b, "nonmatch"))
        if None not in (g(r, "nonmatch"), g(b, "nonmatch")):
            frd[pid] = float(g(r, "nonmatch") <= 3) - float(g(b, "nonmatch") <= 3)
        if None not in (g(b, "match"), g(b, "nonmatch"), g(b, "invalid")):
            inv = g(b, "invalid")
            ver[pid] = np.mean([1.0 if v > inv else 0.5 if v == inv else 0.0 for v in (g(b, "match"), g(b, "nonmatch"))])
    per[arm] = md
    res[arm] = dict(margin_diff=boot(list(md.values())), false_reject_diff=boot(list(frd.values())),
                    blind_verification=boot(list(ver.values())), meta=dict(ref=mr, noref=mb))


def lo_gt0(v):
    return None if v is None else bool(v[1][0] > 0)


ok = lambda a: isinstance(res.get(a), dict) and res[a]["margin_diff"] is not None
res["P_R5A1"] = lo_gt0(res["fast"]["margin_diff"]) if ok("fast") else None
res["P_R5A2"] = lo_gt0(res["think"]["margin_diff"]) if ok("think") else None
res["P_R5A3"] = bool(res["think"]["margin_diff"][0] < res["fast"]["margin_diff"][0]) if ok("fast") and ok("think") else None
if ok("fast") and ok("think"):
    common = [p for p in per["think"] if p in per["fast"]]
    res["think_minus_fast_margin_diff"] = boot([per["think"][p] - per["fast"][p] for p in common])
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
