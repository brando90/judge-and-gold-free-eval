# POST HOC (round-9 review, must-fix 4): the OSF k-pool endpoint (E2, osf.io/qugbd) recomputed under corrected
# correctness labels. Run from experiments/tfa-vs-judge. Writes papers/analysis/r9_inflation_relabeled_kpool.json.
# Estimator unchanged from mitigation_analysis.py E2: committed bon_analysis excess gap (rubric a selects, rubric b
# reports, permutation null within correctness classes), per-task condition-minus-blind delta, pass-rate band
# [0.05, 0.95] under the registered labels (population fixed), bootstrap CI (2,000 resamples). Labels: strict
# (reproduction check), lenient (any format), model (unboxed replies read by Qwen2.5-14B). Conditions: ref, m1.
import json
import os
import random
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)
random.seed(0)
rng = np.random.default_rng(0)
POOL = "runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl"
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
pool = {}
for l in open(POOL):
    r = json.loads(l)
    if "oracle" in r:
        r["k"] = int(tasks[r["problem_id"]]["k"])
        pool[r["problem_id"]] = r
LEN = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/r8/lenient_kpool.jsonl")}
MOD = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/r8/model_kpool.jsonl")}
LABELS = {"strict": lambda p: pool[p]["oracle"], "lenient": lambda p: LEN[p]["lenient"], "model": lambda p: MOD[p]["model"]}


def scores(jtag, cond, rep):
    for pref in ("kstrat", "synthk"):
        f = f"runs/bon_scores_kstrat/{pref}__{jtag}__{cond}_{rep}.jsonl"
        if os.path.exists(f):
            return {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(f)}
    raise FileNotFoundError(f"{jtag} {cond} {rep}")


def bci(v, B=2000):
    v = np.asarray(v, float)
    b = [float(np.mean(rng.choice(v, len(v)))) for _ in range(B)]
    return [round(float(np.percentile(b, 2.5)), 3), round(float(np.percentile(b, 97.5)), 3)]


res = {}
for lab in LABELS:
    for jtag in JUDGES:
        per = {}
        for cond in ("noref", "ref", "m1"):
            sa, sb = scores(jtag, cond, "a"), scores(jtag, cond, "b")
            g = {}
            for pid, it in pool.items():
                if pid not in sa or pid not in sb or not (0.05 <= float(np.mean(it["oracle"])) <= 0.95):
                    continue
                item = dict(it, oracle=list(LABELS[lab](pid)))
                c = ns["per_item_curves"](item, sa[pid], sb[pid])
                g[pid] = c[64]["judge_gain"] - c[64]["true_gain"] - ns["permutation_null"](item, sa[pid], sb[pid])
            per[cond] = g
        for cond in ("ref", "m1"):
            for kname, sel in (("k1", lambda k: k == 1), ("kgt1", lambda k: k > 1)):
                d = [per[cond][p] - per["noref"][p] for p in per[cond] if p in per["noref"] and sel(pool[p]["k"])]
                res[f"{lab}|{jtag}|{cond}|{kname}"] = dict(n=len(d), delta=round(float(np.mean(d)), 3), ci=bci(d))
        print(lab, jtag, {k.split("|", 2)[2]: (v["delta"], v["ci"]) for k, v in res.items() if k.startswith(f"{lab}|{jtag}|")}, flush=True)
json.dump(res, open("../../papers/analysis/r9_inflation_relabeled_kpool.json", "w"), indent=1)
