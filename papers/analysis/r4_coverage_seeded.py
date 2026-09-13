# POST HOC seeded rerun of the judge-coverage scorer (p17_coverage_analysis.py, unchanged estimators).
# The frozen scorer draws its permutation nulls from an RNG created inside bon_analysis.py and its
# bootstrap from a second generator; reruns of the analysis could differ. This runs the frozen code
# SEEDS times, with both generators seeded (0..SEEDS-1), and records the per-seed Mistral-7B and
# per-judge P-X1/P-X2 verdicts and the seed-0 values. Writes papers/analysis/r4_coverage_seeded_results.json.
# Run from experiments/tfa-vs-judge.
import json
import os

import numpy as np

SEEDS = 20
src = open("../../papers/analysis/p17_coverage_analysis.py").read()
res = {"seeds": {}}
frozen_out = "../../papers/analysis/p17_coverage_results.json"
keep = open(frozen_out).read()
try:
    for seed in range(SEEDS):
        patched = src.replace("exec(compile(src, \"bon_analysis\", \"exec\"), ns)",
                              f"exec(compile(src, \"bon_analysis\", \"exec\"), ns)\nns[\"rng\"] = np.random.default_rng({seed})")
        patched = patched.replace("rng = np.random.default_rng(0)", f"rng = np.random.default_rng({seed})")
        assert patched != src
        g = {"__name__": "__coverage__"}
        exec(compile(patched, "p17_coverage_seeded", "exec"), g)
        out = json.load(open(frozen_out))
        res["seeds"][seed] = {j: dict(ref_kgt1=v["ref_kgt1"], m1_minus_ref_kgt1=v["m1_minus_ref_kgt1"], verdicts=v["verdicts"])
                              for j, v in out.items() if not j.startswith("_")}
finally:
    open(frozen_out, "w").write(keep)  # the frozen results file is restored byte for byte
judges = sorted(res["seeds"][0])
res["verdict_rates"] = {j: {k: float(np.mean([res["seeds"][s][j]["verdicts"][k] for s in res["seeds"]]))
                            for k in ("PX1", "PX2", "PX3_directional")} for j in judges}
json.dump(res, open("../../papers/analysis/r4_coverage_seeded_results.json", "w"), indent=1)
print(json.dumps(res["verdict_rates"], indent=1))
print(json.dumps(res["seeds"][0], indent=1))
