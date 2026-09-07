# POST-HOC sensitivity: intention-to-treat recomputation of the replication primary
# endpoint E1 over EVERY built item, alongside the registered in-band population and the
# excluded out-of-band remainder. NOT registered; written in response to external review
# (2026-09-07, "report an intention-to-treat analysis over every item, with the filtered
# analysis as sensitivity"). Estimator is byte-identical to repl_analysis.py's E1 (the
# committed bon_analysis machinery: rep a selects, rep b reports, within-checker-stratum
# permutation null, item-level cluster bootstrap pooling both judges); the ONLY change is
# the population filter.
# Run from experiments/tfa-vs-judge. Writes ../../papers/analysis/repl_itt_sensitivity.json
import json
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)
rng = np.random.default_rng(0)

POOL = "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl"
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
pool = {r["problem_id"]: r for r in (json.loads(l) for l in open(POOL)) if "oracle" in r}


def scores(jtag, cond, rep):
    return {json.loads(l)["problem_id"]: json.loads(l)["escore"]
            for l in open(f"runs/bon_scores_repl/synthk__{jtag}__{cond}_{rep}.jsonl")}


def band_of(it):
    pr = float(np.mean(it["oracle"]))
    return "inband" if 0.2 <= pr <= 0.8 else "outband"


deltas = {j: {} for j in JUDGES}
for jtag in JUDGES:
    ra, rb = scores(jtag, "ref", "a"), scores(jtag, "ref", "b")
    na, nb = scores(jtag, "noref", "a"), scores(jtag, "noref", "b")
    for pid, it in pool.items():
        if pid not in ra or pid not in na:
            continue
        if not (0 < sum(it["oracle"]) < len(it["oracle"])):
            continue  # degenerate items carry no selection signal under any estimator
        gr = ns["per_item_curves"](it, ra[pid], rb[pid])
        nr = ns["permutation_null"](it, ra[pid], rb[pid])
        gn = ns["per_item_curves"](it, na[pid], nb[pid])
        nn = ns["permutation_null"](it, na[pid], nb[pid])
        deltas[jtag][pid] = ((gr[64]["judge_gain"] - gr[64]["true_gain"] - nr)
                             - (gn[64]["judge_gain"] - gn[64]["true_gain"] - nn))

out = {}
for popname, keep in (("itt_all", lambda it: True),
                      ("inband", lambda it: band_of(it) == "inband"),
                      ("outband", lambda it: band_of(it) == "outband")):
    pids = sorted(p for p in set(deltas[JUDGES[0]]) & set(deltas[JUDGES[1]])
                  if keep(pool[p]))
    if not pids:
        continue
    D = np.array([[deltas[j][p] for p in pids] for j in JUDGES])
    idx = np.arange(len(pids))
    boots = [float(D[:, rng.choice(idx, len(idx))].mean()) for _ in range(4000)]
    per_judge = {}
    for j in JUDGES:
        v = np.array([deltas[j][p] for p in pids])
        b = [float(np.mean(rng.choice(v, len(v)))) for _ in range(4000)]
        per_judge[j] = dict(delta=round(float(v.mean()), 3),
                            ci=[round(float(np.percentile(b, 2.5)), 3),
                                round(float(np.percentile(b, 97.5)), 3)])
    out[popname] = dict(n_items=len(pids), pooled=round(float(D.mean()), 3),
                        ci=[round(float(np.percentile(boots, 2.5)), 3),
                            round(float(np.percentile(boots, 97.5)), 3)],
                        per_judge=per_judge)
    print(f"{popname:8s} n={len(pids):3d} pooled {out[popname]['pooled']:+.3f} "
          f"{out[popname]['ci']}")

json.dump(out, open("../../papers/analysis/repl_itt_sensitivity.json", "w"), indent=1)
