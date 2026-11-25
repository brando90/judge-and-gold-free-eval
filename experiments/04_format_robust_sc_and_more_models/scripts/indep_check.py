#!/usr/bin/env python3
"""Experiment 04 independent recompute: SC_fr and pass@1_fr per model with plain Python (Counter), from the sample files, fr_extract and the
saved key/gold caches, not through analyze.py's numpy helpers. Compares to results.json; writes results/indep_check.json.
    ~/.venvs/jfe/bin/python experiments/04_format_robust_sc_and_more_models/scripts/analyze.py && ... scripts/indep_check.py"""
import importlib.util, json, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent; EXP = HERE.parent; REPO = EXP.parent.parent; OUT = EXP / "results"
s = importlib.util.spec_from_file_location("fr", HERE / "fr_extract.py"); fr = importlib.util.module_from_spec(s); s.loader.exec_module(fr)
R = json.load(open(OUT / "results.json")); kc = json.load(open(OUT / "key_cache.json")); gc = json.load(open(OUT / "gold_cache.json"))
tasks = [json.loads(l) for l in open(REPO / "experiments/tfa-vs-judge/runs/bon_math_tasks.jsonl")]
paths = {"llama31_8b": REPO / "experiments/tfa-vs-judge/runs/bon/bon_math__meta-llama__Llama-3.1-8B-Instruct.jsonl"}
for p in sorted((OUT / "gen").glob("*.jsonl")) + sorted((REPO / "experiments/03_model_level_ranking_sc/results/gen").glob("*.jsonl")):
    paths[p.name] = p
names = {"qwen25_7b": "Qwen__Qwen2.5-7B", "qwen3_4b": "Qwen__Qwen3-4B", "qwen3_1p7b": "Qwen__Qwen3-1.7B", "dsmath_7b_rl": "deepseek-math-7b-rl", "mistral_7b": "Mistral-7B",
         "qwen3_8b": "Qwen__Qwen3-8B", "qwen35_4b": "Qwen__Qwen3.5-4B", "llama3_8b": "Meta-Llama-3-8B", "dsmath_7b_inst": "deepseek-math-7b-instruct"}
def path_of(m):
    if m == "llama31_8b": return paths[m]
    return next(v for k, v in paths.items() if names[m] in k)
out = {}
for m in R["models"]:
    rows = {}
    for l in open(path_of(m)):
        r = json.loads(l); rows[r["problem_id"]] = r
    sc = p1 = 0.0
    for t in tasks:
        smp = rows[t["problem_id"]]["samples"][:16]
        ans = [fr.fr_answer(x)[0] for x in smp]
        keys = [kc["norm\x00" + a] if a else None for a in ans]
        c = Counter(k for k in keys if k is not None)
        sc += sum(v * (v - 1) for v in c.values()) / (16 * 15)
        p1 += sum(gc[f"{t['problem_id']}\x00{a}"] if a else 0 for a in ans) / 16
    out[m] = dict(sc_fr=sc / 500, p1_fr=p1 / 500, sc_fr_analyze=R["table"][m]["sc_fr"], p1_fr_analyze=R["table"][m]["p1_fr"])
    out[m]["max_abs_diff"] = max(abs(out[m]["sc_fr"] - out[m]["sc_fr_analyze"]), abs(out[m]["p1_fr"] - out[m]["p1_fr_analyze"]))
json.dump(out, open(OUT / "indep_check.json", "w"), indent=1)
for m, v in out.items(): print(m, round(v["sc_fr"], 4), round(v["p1_fr"], 4), "maxdiff", f"{v['max_abs_diff']:.2e}")
