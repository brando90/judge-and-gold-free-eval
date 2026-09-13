# POST HOC (round-9 review, must-fix 4): the OSF replication endpoint (E1, osf.io/ym5x9) recomputed under corrected
# correctness labels. Run from experiments/tfa-vs-judge. Writes papers/analysis/r9_inflation_relabeled.json.
# Estimator unchanged from repl_analysis.py: the committed bon_analysis excess-gap machinery (rubric a selects, rubric b
# reports, permutation null within correctness classes), per-item referenced-minus-blind delta, pooled over Qwen2.5-7B
# and phi-4 by item-cluster bootstrap (4,000 resamples). Only the per-sample correctness labels change:
#   strict   registered labels (reproduces the registered endpoint up to tie-break and permutation randomness)
#   lenient  answers read in any format (runs/r8/lenient_repl.jsonl)
#   model    unboxed replies read by Qwen2.5-14B (runs/r8/model_repl.jsonl)
# Population: primary = the registered in-band tasks (pass rate in [0.2, 0.8] under the registered labels), so only the
# labels change; secondary = the band recomputed under each labeling.
import json
import random
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)
random.seed(0)
rng = np.random.default_rng(0)

POOL = "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl"
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
pool = {r["problem_id"]: r for r in (json.loads(l) for l in open(POOL)) if "oracle" in r}
LEN = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/r8/lenient_repl.jsonl")}
MOD = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/r8/model_repl.jsonl")}
LABELS = {"strict": lambda pid: pool[pid]["oracle"], "lenient": lambda pid: LEN[pid]["lenient"], "model": lambda pid: MOD[pid]["model"]}


def scores(jtag, cond, rep):
    return {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(f"runs/bon_scores_repl/synthk__{jtag}__{cond}_{rep}.jsonl")}


S = {(j, c, r): scores(j, c, r) for j in JUDGES for c in ("ref", "noref") for r in ("a", "b")}


def endpoint(labname, population):
    deltas = {}
    for jtag in JUDGES:
        d = {}
        for pid, it in pool.items():
            lab = LABELS[labname](pid)
            band_lab = pool[pid]["oracle"] if population == "registered_band" else lab
            if not (0.2 <= float(np.mean(band_lab)) <= 0.8):
                continue
            if pid not in S[(jtag, "ref", "a")] or pid not in S[(jtag, "noref", "a")]:
                continue
            item = dict(it, oracle=list(lab))
            ra, rb, na, nb = (S[(jtag, "ref", "a")][pid], S[(jtag, "ref", "b")][pid], S[(jtag, "noref", "a")][pid], S[(jtag, "noref", "b")][pid])
            gr, nr = ns["per_item_curves"](item, ra, rb), ns["permutation_null"](item, ra, rb)
            gn, nn = ns["per_item_curves"](item, na, nb), ns["permutation_null"](item, na, nb)
            d[pid] = (gr[64]["judge_gain"] - gr[64]["true_gain"] - nr) - (gn[64]["judge_gain"] - gn[64]["true_gain"] - nn)
        deltas[jtag] = d
    out = {}
    for jtag in JUDGES:
        v = np.array(list(deltas[jtag].values()))
        b = [float(np.mean(rng.choice(v, len(v)))) for _ in range(4000)]
        out[jtag] = dict(n=len(v), delta=round(float(v.mean()), 3), ci=[round(float(np.percentile(b, 2.5)), 3), round(float(np.percentile(b, 97.5)), 3)])
    pids = sorted(set(deltas[JUDGES[0]]) & set(deltas[JUDGES[1]]))
    D = np.array([[deltas[j][p] for p in pids] for j in JUDGES])
    idx = np.arange(len(pids))
    bs = [float(D[:, rng.choice(idx, len(idx))].mean()) for _ in range(4000)]
    out["pooled"] = dict(n_items=len(pids), delta=round(float(D.mean()), 3), ci=[round(float(np.percentile(bs, 2.5)), 3), round(float(np.percentile(bs, 97.5)), 3)])
    return out


res = {}
for population in ("registered_band", "band_under_labeling"):
    for labname in LABELS:
        if population == "band_under_labeling" and labname == "strict":
            continue
        res[f"{population}|{labname}"] = endpoint(labname, population)
        print(population, labname, json.dumps(res[f"{population}|{labname}"]["pooled"]), flush=True)
json.dump(res, open("../../papers/analysis/r9_inflation_relabeled.json", "w"), indent=1)
