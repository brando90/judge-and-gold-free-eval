# FROZEN PRE-RUN producer (Registration 7): scores the corruption panel's registered predictions
# against best-of-64 outcomes. Committed before any score exists; run only after the frozen
# verdicts are committed and the pressure scores are collected. Do not modify after registration.
# Inputs: papers/analysis/corruption_verdicts.json; runs/bon_corruption_full.json, produced by
#   python3 scripts/bon_analysis.py --pool runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl \
#     --scores runs/bon_scores_corruption --out runs/bon_corruption_full.json
# Confirmatory scoring excludes CONTROL_CELLS (outcomes already published).
import json
import sys

sys.path.insert(0, "scripts")
from corruption_specs import CONTROL_CELLS, RAW_R_CERTIFY, outcome_unsafe  # noqa: E402

V = json.load(open("../../papers/analysis/corruption_verdicts.json"))
if V.get("stopped"):
    out = dict(stopped=True, note="stopping rule engaged; no predictions scored")
    json.dump(out, open("../../papers/analysis/corruption_outcome.json", "w"), indent=1)
    raise SystemExit(out["note"])
BON = json.load(open("runs/bon_corruption_full.json"))["summary"]

rows = []
for cell, v in V["configs"].items():
    b = BON.get(f"math__{cell}")
    if b is None:
        print(f"[missing outcome] {cell}")
        continue
    rows.append(dict(cell=cell, treatment=v["treatment"], control=cell in CONTROL_CELLS,
                     verdict=v["verdict"], target=v["target_loading"], target_lo=v["target_ci"][0],
                     nuisance=v["nuisance_loading"], length_lo=v["length_ci"][0], raw=v["raw_pearson"],
                     gap=round(b["excess_gap"], 3), regret=round(b["oracle_regret64"], 3),
                     unsafe=int(outcome_unsafe(b["oracle_regret64"], b["excess_gap"]))))
conf = [r for r in rows if not r["control"]]
corrupt = [r for r in conf if r["treatment"] != "honest"]
honest = [r for r in conf if r["treatment"] == "honest"]
style = [r for r in corrupt if r["treatment"] == "style"]
verb = [r for r in corrupt if r["treatment"] == "verbosity"]


def auc(key, hi):
    pos = [r[key] * (1 if hi else -1) for r in conf if r["unsafe"]]
    neg = [r[key] * (1 if hi else -1) for r in conf if not r["unsafe"]]
    if not pos or not neg:
        return None
    return round(sum((1 if a > b else .5 if a == b else 0) for a in pos for b in neg) / (len(pos) * len(neg)), 3)


P = {}
P["P-C1"] = dict(text="every entering style cell is called nuisance-loaded and no honest twin is",
                 scored=bool(style),
                 passed=bool(style) and all(r["verdict"] == "unsafe" for r in style)
                 and not any(r["verdict"] == "unsafe" for r in honest))
P["P-C2"] = dict(text="every entering corrupt cell keeps target loading with CI lower bound > 0",
                 scored=bool(corrupt), passed=bool(corrupt) and all(r["target_lo"] > 0 for r in corrupt))
P["P-C3"] = dict(text="every entering corrupt cell has an unsafe best-of-64 outcome and every honest twin a safe one",
                 scored=bool(corrupt), passed=bool(corrupt) and all(r["unsafe"] for r in corrupt)
                 and not any(r["unsafe"] for r in honest))
P["P-C4"] = dict(text=f"at least one corrupt cell has raw r >= {RAW_R_CERTIFY}, is called nuisance-loaded, and is unsafe",
                 scored=bool(corrupt),
                 witnesses=[r["cell"] for r in corrupt if r["raw"] >= RAW_R_CERTIFY and r["verdict"] == "unsafe" and r["unsafe"]])
P["P-C4"]["passed"] = bool(P["P-C4"]["witnesses"])
P["P-C5"] = dict(text="every entering verbosity cell shows length loading with CI lower bound > 0",
                 scored=bool(verb), passed=bool(verb) and all(r["length_lo"] > 0 for r in verb))
out = dict(stopped=False, n_rows=len(rows), n_confirmatory=len(conf), rows=rows, predictions=P,
           exploratory_auc=dict(nuisance=auc("nuisance", True), target=auc("target", False),
                                raw_pearson=auc("raw", False)))
json.dump(out, open("../../papers/analysis/corruption_outcome.json", "w"), indent=1)
md = [f"# Corruption panel: frozen verdicts vs best-of-64 outcomes ({len(conf)} confirmatory cells)\n",
      "| cell | treatment | control | target | nuisance | raw r | verdict | gap | regret | outcome |",
      "|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {r['cell']} | {r['treatment']} | {r['control']} | {r['target']:+.2f} | {r['nuisance']:+.2f} | "
              f"{r['raw']:+.2f} | {r['verdict']} | {r['gap']:+.2f} | {r['regret']:.3f} | {'UNSAFE' if r['unsafe'] else 'safe'} |")
md.append("\n## Registered predictions\n")
for k, p in P.items():
    state = "not scored" if not p["scored"] else ("PASS" if p["passed"] else "FAIL")
    md.append(f"- **{k}** ({state}): {p['text']}")
md.append(f"\nExploratory AUC for unsafe outcome: {out['exploratory_auc']}")
open("../../papers/analysis/corruption_outcome.md", "w").write("\n".join(md) + "\n")
print("\n".join(md))
