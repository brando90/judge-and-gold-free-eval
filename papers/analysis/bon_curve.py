# Pressure curve (Reviewer W9): excess gap and oracle regret at n = 4, 16, 64 for every
# config, from the existing score files. Reuses the pre-registered estimators of
# scripts/bon_analysis.py (same tie handling, same subsample draws, same permutation null at
# n=64; at n<64 the null is not recomputed, so we report raw gap and regret per n and the
# excess gap only at 64). Run from experiments/tfa-vs-judge.
import importlib.util, json, os, sys

import numpy as np

spec = importlib.util.spec_from_file_location("bon_analysis", "scripts/bon_analysis.py")
ba = importlib.util.module_from_spec(spec)
sys.modules["bon_analysis"] = ba
# import module without running main()
src = open("scripts/bon_analysis.py").read().split('if __name__')[0]
exec(compile(src, "bon_analysis.py", "exec"), ba.__dict__)

OUT = {}
for domain, pool_f, scores_dir in [
        ("math", "runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl", "runs/bon_scores_v2"),
        ("code", "runs/bon/bon_mbpp__Qwen__Qwen2.5-7B-Instruct.jsonl", "runs/bon_scores_code")]:
    items = {}
    for l in open(pool_f):
        r = json.loads(l)
        if "oracle" not in r:
            continue
        pr = float(np.mean(r["oracle"]))
        if 0.2 <= pr <= 0.8:
            items[r["problem_id"]] = r
    for fn in sorted(os.listdir(scores_dir)):
        if not fn.endswith("_a.jsonl") or not fn.startswith(f"{domain}__") and not (
                domain == "code" and fn.startswith("code__")):
            continue
        cfg = fn[:-8]
        try:
            sa = {json.loads(l)["problem_id"]: json.loads(l)["escore"]
                  for l in open(f"{scores_dir}/{cfg}_a.jsonl")}
            sb = {json.loads(l)["problem_id"]: json.loads(l)["escore"]
                  for l in open(f"{scores_dir}/{cfg}_b.jsonl")}
        except FileNotFoundError:
            continue
        per_n = {n: dict(jg=[], tg=[], rg=[]) for n in (4, 16, 64)}
        for pid, it in items.items():
            if pid not in sa or pid not in sb:
                continue
            curves = ba.per_item_curves(it, sa[pid], sb[pid])
            for n in (4, 16, 64):
                per_n[n]["jg"].append(curves[n]["judge_gain"])
                per_n[n]["tg"].append(curves[n]["true_gain"])
                per_n[n]["rg"].append(curves[n]["oracle_regret"])
        if not per_n[64]["jg"]:
            continue
        OUT[cfg] = {n: dict(raw_gap=round(float(np.mean(per_n[n]["jg"]) - np.mean(per_n[n]["tg"])), 3),
                            regret=round(float(np.mean(per_n[n]["rg"])), 3))
                    for n in (4, 16, 64)}
        print(cfg, OUT[cfg], flush=True)

json.dump(OUT, open("../../papers/analysis/bon_curve.json", "w"), indent=1)
md = ["| config | gap@4 | gap@16 | gap@64 | regret@4 | regret@16 | regret@64 |", "|---|---|---|---|---|---|---|"]
for cfg, d in sorted(OUT.items()):
    md.append(f"| {cfg} | " + " | ".join(f"{d[n]['raw_gap']:+.2f}" for n in (4, 16, 64)) + " | "
              + " | ".join(f"{d[n]['regret']:.3f}" for n in (4, 16, 64)) + " |")
open("../../papers/analysis/bon_curve.md", "w").write(
    "# Pressure curves: raw gap and regret vs n (pre-registered estimators, existing pools)\n\n"
    + "\n".join(md) + "\n")
