# Registered analysis for the synthetic-multiplicity experiment (P-S1..P-S5 in
# scripts/build_synth_multiplicity.py, commit c505c23). COMMITTED BEFORE ANY SYNTHK SCORES
# EXISTED so the analysis itself is pre-registered. Run from experiments/tfa-vs-judge once
# runs/bon_scores_synthk/ has files.
#
# Estimands, per judge and per k stratum (k in {1, 2, 4, 8, 16}):
#  margin(k, cond): among oracle-valid samples, mean(score | matches shown ref) minus
#    mean(score | other valid), item-mean, bootstrap CI over items. Defined only for k > 1.
#  gap(k, cond): mean excess hack gap at n=64 over the within-item permutation null,
#    per item then averaged, bootstrap CI. Defined for all k including the k=1 control.
#  P-S1: margin and (gap_ref - gap_blind) increase with k; at k=1 gap_ref < gap_blind.
#  P-S2: margin(refinst) < margin(ref) per k stratum.
#  P-S3: margin(multiref) < margin(ref) per k stratum.
#  P-S4: same directional pattern for Llama-3.1-8B and phi-4 judges.
#  P-S5: same directional pattern on the Llama-generator pool (Qwen-7B judge).
import glob
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)
rng = np.random.default_rng(0)


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


def boot_ci(vals, B=2000):
    vals = np.asarray(vals, float)
    b = [float(np.mean(rng.choice(vals, len(vals)))) for _ in range(B)]
    return [round(float(np.percentile(b, 2.5)), 2), round(float(np.percentile(b, 97.5)), 2)]


def load_pool(path):
    pool = {}
    for l in open(path):
        r = json.loads(l)
        if "oracle" in r:
            pool[r["problem_id"]] = r
    return pool


def analyze(pool, scores_dir, judges, tag_prefix="synthk"):
    out = {}
    ks = sorted({r["k"] for r in pool.values()})
    for jm in judges:
        jtag = jm.replace("/", "__")
        for cond in ("noref", "ref", "refinst", "multiref"):
            for rep in ("a", "b"):
                f = f"{scores_dir}/{tag_prefix}__{jtag}__{cond}_{rep}.jsonl"
                if not os.path.exists(f):
                    continue
                sa = {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(f)}
                # margins per k stratum (k > 1)
                for k in ks:
                    items = [r for r in pool.values() if r["k"] == k and r["problem_id"] in sa]
                    if k > 1:
                        margins = []
                        for it in items:
                            refn = norm(it["ref_answer"])
                            ms, os_ = [], []
                            for i, ok in enumerate(it["oracle"]):
                                if not ok:
                                    continue
                                a = norm(boxed(it["samples"][i]) or it["samples"][i])
                                (ms if a == refn else os_).append(sa[it["problem_id"]][i])
                            if ms and os_:
                                margins.append(float(np.mean(ms) - np.mean(os_)))
                        if len(margins) >= 3:
                            out[f"margin__{jtag}__{cond}_{rep}__k{k}"] = dict(
                                n=len(margins), margin=round(float(np.mean(margins)), 2),
                                ci=boot_ci(margins))
        # gaps per k need both reps of a cond
        for cond in ("noref", "ref", "refinst", "multiref"):
            fa = f"{scores_dir}/{jtag}"
            fa = f"{scores_dir}/{tag_prefix}__{jtag}__{cond}_a.jsonl"
            fb = f"{scores_dir}/{tag_prefix}__{jtag}__{cond}_b.jsonl"
            if not (os.path.exists(fa) and os.path.exists(fb)):
                continue
            sa = {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(fa)}
            sb = {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(fb)}
            for k in ks:
                gaps = []
                for it in pool.values():
                    pid = it["problem_id"]
                    if it["k"] != k or pid not in sa:
                        continue
                    # in-band filter within stratum: degenerate pools carry no signal
                    pr = float(np.mean(it["oracle"]))
                    if not (0.05 <= pr <= 0.95):
                        continue
                    curves = ns["per_item_curves"](it, sa[pid], sb[pid])
                    null = ns["permutation_null"](it, sa[pid], sb[pid])
                    gaps.append(curves[64]["judge_gain"] - curves[64]["true_gain"] - null)
                if len(gaps) >= 3:
                    out[f"gap__{jtag}__{cond}__k{k}"] = dict(
                        n=len(gaps), gap=round(float(np.mean(gaps)), 3), ci=boot_ci(gaps))
    return out


QWEN = ["Qwen/Qwen2.5-1.5B-Instruct", "Qwen/Qwen2.5-3B-Instruct",
        "Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen2.5-14B-Instruct"]
XFAM = ["meta-llama/Llama-3.1-8B-Instruct", "microsoft/phi-4"]

results = {}
qpool_path = "runs/bon/bon_synthk__Qwen__Qwen2.5-7B-Instruct.jsonl"
if os.path.exists(qpool_path):
    qpool = load_pool(qpool_path)
    results["qwen_pool"] = analyze(qpool, "runs/bon_scores_synthk", QWEN + XFAM)
lpool_path = "runs/bon/bon_synthk__meta-llama__Llama-3.1-8B-Instruct.jsonl"
if os.path.exists(lpool_path):
    lpool = load_pool(lpool_path)
    results["llama_pool"] = analyze(lpool, "runs/bon_scores_synthk_llamagen",
                                    ["Qwen/Qwen2.5-7B-Instruct"])

json.dump(results, open("../../papers/analysis/synthk_results.json", "w"), indent=1)
for pool_name, res in results.items():
    print(f"== {pool_name}: {len(res)} cells")
    for key in sorted(res):
        v = res[key]
        val = v.get("margin", v.get("gap"))
        print(f"  {key:60s} {val:+.2f} [{v['ci'][0]:+.2f},{v['ci'][1]:+.2f}] n={v['n']}")
