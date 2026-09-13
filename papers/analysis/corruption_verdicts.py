# FROZEN PRE-RUN producer (Registration 7): audit verdicts for the cells that passed the frozen
# manipulation check. Committed before any score exists; run only after corruption_manipulation
# is committed, and committed itself BEFORE any pressure score exists (the harness refuses to
# submit best-of-n batches until this file's output exists). Do not modify after registration.
# Same 60-item anchor set, estimators, bootstrap and frozen CI rule as the published audit and
# Registration 6, plus a second, mechanical nuisance axis (log trace length) for the verbosity
# prediction. Run from experiments/tfa-vs-judge:
#   python3 ../../papers/analysis/corruption_verdicts.py
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, "scripts")
from corruption_specs import cell_judge, cell_treatment, verdict  # noqa: E402

rng = np.random.default_rng(0)
B = 2000
M = json.load(open("../../papers/analysis/corruption_manipulation.json"))


def pearson(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


def partial(x, y, z):
    x, y, z = map(lambda a: np.asarray(a, float), (x, y, z))
    rx = x - np.polyval(np.polyfit(z, x, 1), z)
    ry = y - np.polyval(np.polyfit(z, y, 1), z)
    return pearson(rx, ry)


def bci(f, *arrs):
    arrs = [np.asarray(a, float) for a in arrs]
    idx = np.arange(len(arrs[0]))
    vs = []
    for _ in range(B):
        i = rng.choice(idx, len(idx))
        try:
            v = f(*[a[i] for a in arrs])
            if np.isfinite(v):
                vs.append(v)
        except Exception:
            pass
    if len(vs) < 100:
        return [float("nan"), float("nan")]
    return [round(float(np.percentile(vs, 2.5)), 3), round(float(np.percentile(vs, 97.5)), 3)]


out = dict(anchor_n=None, stopped=M.get("stopped", False), configs={})
if out["stopped"]:
    out["note"] = "manipulation stopping rule engaged; no audit phase"
else:
    labs = {r["id"]: r for r in json.load(open("human_eval/labels/phase1/author_1_Sri_random.json"))
            if r.get("soundness") not in (None, "")}
    tr = {json.loads(l)["id"]: json.loads(l) for l in open("human_eval/traces_to_label.jsonl")}
    out["anchor_n"] = len(labs)
    for cell in M["entering_cells"]:
        rows = [json.loads(l) for l in open(f"runs/corruption/cert__{cell}.jsonl")]
        sc = {r["task_id"]: r["score"] for r in rows if r.get("score") is not None}
        fb = float(np.mean([r["src"] != "lp" for r in rows]))
        ids = [i for i in labs if i in sc]
        x = np.array([sc[i] for i in ids])
        s = np.array([float(labs[i]["soundness"]) for i in ids])
        t = np.array([float(labs[i]["style"]) for i in ids])
        L = np.array([math.log1p(len(tr[i]["trace"])) for i in ids])
        sp, tp, lp = partial(x, s, t), partial(x, t, s), partial(x, L, s)
        sci, tci, lci = bci(partial, x, s, t), bci(partial, x, t, s), bci(partial, x, L, s)
        out["configs"][cell] = dict(
            judge=cell_judge(cell)["model"], treatment=cell_treatment(cell), n=len(ids),
            fallback=round(fb, 4), distinct_scores=len(set(np.round(x, 4).tolist())),
            target_loading=round(sp, 3), target_ci=sci,
            nuisance_loading=round(tp, 3), nuisance_ci=tci,
            length_loading=round(lp, 3), length_ci=lci,
            raw_pearson=round(pearson(x, s), 3),
            verdict=verdict(sp, sci[0], tp, tci[0]))
json.dump(out, open("../../papers/analysis/corruption_verdicts.json", "w"), indent=1)
md = ["# Corruption panel audit verdicts (frozen CI rule)\n",
      "| cell | treatment | n | fallback | target [CI] | style nuisance [CI] | length [CI] | raw r | verdict |",
      "|---|---|---|---|---|---|---|---|---|"]
for k, r in out["configs"].items():
    md.append(f"| {k} | {r['treatment']} | {r['n']} | {r['fallback']:.3f} | {r['target_loading']:+.2f} {r['target_ci']} | "
              f"{r['nuisance_loading']:+.2f} {r['nuisance_ci']} | {r['length_loading']:+.2f} {r['length_ci']} | "
              f"{r['raw_pearson']:+.2f} | **{r['verdict']}** |")
if out["stopped"]:
    md.append("\nStopping rule engaged at the manipulation check; no audit was run.")
open("../../papers/analysis/corruption_verdicts.md", "w").write("\n".join(md) + "\n")
print("\n".join(md))
