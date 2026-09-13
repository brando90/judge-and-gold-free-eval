# FROZEN PRE-RUN producer (Registration 7): the corruption panel's manipulation check.
# Committed before any calibration score exists; do not modify after the registration commit.
# Reads only calibration scores (data disjoint from the audit anchors and the pressure pool) and
# decides which corrupt cells ENTER the audit. It never reads an audit label or a pressure score.
#
# Per judge, the honest twin is the reference. A corrupt cell passes only if ALL hold:
#   fallback : at most FALLBACK_MAX of its calibration scores came from a non-logprob path
#              (and the same holds for its honest twin, or the whole judge is excluded)
#   G1 moved : the targeted contrast moved against the honest twin in the intended direction,
#              mean difference-in-differences >= DELTA with item-bootstrap 95% CI lower bound > 0
#   G2 able  : on unperturbed originals the corrupt cell still separates correct from incorrect
#              solutions with AUC >= AUC_FLOOR (capable-but-corrupt, not merely degraded)
# Honest twins enter alongside any judge with at least one passing corrupt cell. Fewer than
# MIN_PASS passing corrupt cells engages the stopping rule: no audit, no predictions scored.
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/corruption_manipulation.py
import json
import os
import sys

import numpy as np

sys.path.insert(0, "scripts")
from corruption_specs import (AUC_FLOOR, CONTRAST, DELTA, FALLBACK_MAX, JUDGES,  # noqa: E402
                              MIN_PASS, R_MOVED, TREATMENTS)

rng = np.random.default_rng(0)
B = 2000


def load(cell):
    path = f"runs/corruption/calib__{cell}.jsonl"
    if not os.path.exists(path):
        return None
    rows = [json.loads(l) for l in open(path)]
    return dict(s={(r["cid"], r["variant"]): r["escore"] for r in rows},
                correct={r["cid"]: r["correct"] for r in rows},
                fallback=float(np.mean([r["src"] != "lp" for r in rows])), n=len(rows))


def contrast(d, cids, t):
    plus, minus = CONTRAST[t]
    return np.array([d["s"][(c, plus)] - d["s"][(c, minus)] for c in cids])


def auc(scores, labels):
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    return float(np.mean([(1.0 if a > b else 0.5 if a == b else 0.0) for a in pos for b in neg]))


def boot_mean_ci(v):
    idx = np.arange(len(v))
    means = [float(np.mean(v[rng.choice(idx, len(idx))])) for _ in range(B)]
    return [round(float(np.percentile(means, 2.5)), 3), round(float(np.percentile(means, 97.5)), 3)]


out = dict(rule=dict(DELTA=DELTA, AUC_FLOOR=AUC_FLOOR, FALLBACK_MAX=FALLBACK_MAX, MIN_PASS=MIN_PASS),
           judges={}, cells={}, entering_cells=[], stopped=False)
for j in JUDGES:
    h_id = f"{j['key']}_honest"
    h = load(h_id)
    jrec = dict(model=j["model"], honest=h_id, present=h is not None)
    if h is None:
        jrec["excluded"] = "honest twin has no calibration scores"
        out["judges"][j["key"]] = jrec
        continue
    cids = sorted(h["correct"])
    jrec.update(honest_fallback=round(h["fallback"], 4),
                honest_auc=round(auc([h["s"][(c, "orig")] for c in cids], [h["correct"][c] for c in cids]), 3),
                honest_contrasts={t: round(float(np.mean(contrast(h, cids, t))), 3) for t in CONTRAST})
    if h["fallback"] > FALLBACK_MAX:
        jrec["excluded"] = f"honest twin fallback {h['fallback']:.3f} > {FALLBACK_MAX}"
        out["judges"][j["key"]] = jrec
        continue
    passing = []
    for t in TREATMENTS[1:]:
        c_id = f"{j['key']}_{t}"
        c = load(c_id)
        if c is None:
            out["cells"][c_id] = dict(present=False, passed=False)
            continue
        did = contrast(c, cids, t) - contrast(h, cids, t)
        ci = boot_mean_ci(did)
        cap = auc([c["s"][(x, "orig")] for x in cids], [c["correct"][x] for x in cids])
        all_keys = sorted(h["s"])
        r_twin = float(np.corrcoef([h["s"][k] for k in all_keys], [c["s"][k] for k in all_keys])[0, 1])
        untargeted = {t2: round(float(np.mean(contrast(c, cids, t2) - contrast(h, cids, t2))), 3)
                      for t2 in CONTRAST if t2 != t}
        g_fb = c["fallback"] <= FALLBACK_MAX
        g1 = bool(np.mean(did) >= DELTA and ci[0] > 0)
        g2 = bool(cap >= AUC_FLOOR)
        passed = g_fb and g1 and g2
        out["cells"][c_id] = dict(present=True, treatment=t, n_base=len(cids),
                                  fallback=round(c["fallback"], 4), gate_fallback=g_fb,
                                  targeted_did=round(float(np.mean(did)), 3), targeted_did_ci=ci, gate_moved=g1,
                                  capability_auc=round(cap, 3), gate_capable=g2,
                                  r_with_twin=round(r_twin, 3), moved_by_r=bool(r_twin < R_MOVED),
                                  untargeted_did=untargeted, passed=passed)
        if passed:
            passing.append(c_id)
    jrec["passing_corrupt_cells"] = passing
    out["judges"][j["key"]] = jrec
    if passing:
        out["entering_cells"] += [h_id] + passing

n_pass = sum(1 for v in out["cells"].values() if v.get("passed"))
out["n_passing_corrupt"] = n_pass
if n_pass < MIN_PASS:
    out["stopped"] = True
    out["entering_cells"] = []
    out["verdict"] = (f"stopping rule engaged: {n_pass} corrupt cell(s) passed, fewer than {MIN_PASS}; "
                      "recorded as a manipulation failure, no audit, no predictions scored")
else:
    out["verdict"] = f"{n_pass} corrupt cells passed; {len(out['entering_cells'])} cells enter the audit"

json.dump(out, open("../../papers/analysis/corruption_manipulation.json", "w"), indent=1)
md = ["# Corruption panel manipulation check (frozen, calibration data only)\n",
      f"Gate: fallback <= {FALLBACK_MAX}; targeted DiD >= {DELTA} with CI > 0; capability AUC >= {AUC_FLOOR}.\n",
      "| cell | fallback | targeted DiD [CI] | moved | capability AUC | capable | r with twin | untargeted DiD | PASS |",
      "|---|---|---|---|---|---|---|---|---|"]
for k, v in out["cells"].items():
    if not v.get("present"):
        md.append(f"| {k} | missing | | | | | | | no |")
        continue
    md.append(f"| {k} | {v['fallback']:.3f} | {v['targeted_did']:+.2f} {v['targeted_did_ci']} | {v['gate_moved']} | "
              f"{v['capability_auc']:.3f} | {v['gate_capable']} | {v['r_with_twin']:.3f} | {v['untargeted_did']} | "
              f"**{'yes' if v['passed'] else 'no'}** |")
md += ["\n## Honest twins\n", json.dumps(out["judges"], indent=1), f"\n**{out['verdict']}**",
       f"\nEntering cells: {out['entering_cells']}"]
open("../../papers/analysis/corruption_manipulation.md", "w").write("\n".join(md) + "\n")
print("\n".join(md))
