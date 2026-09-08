# POST HOC (not registered): manipulation check for the prospective panel's corrupt-prompt cells.
# Registration 6 declared a subtlety ladder of corrupting instructions but, unlike the paper's DPO
# registration, did not gate the corrupt cells on a manipulation check. This producer supplies the
# check after the fact and is reported alongside the registered scoring, never in place of it:
# for every corrupt cell it compares the cell's anchor scores against its OWN honest twin (same
# judge, same protocol, no corrupting sentence) and reports the correlation, the mean shift, and
# the shift in the two audit loadings. A corrupt cell whose scores track its honest twin at
# r > 0.95 with a mean shift near zero did not have its judge corrupted at all, so any registered
# prediction about detecting it is a test of an intervention that never happened.
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/panel_manipulation.py
# Output: papers/analysis/panel_manipulation.json (+ .md)
import json
import os
import sys

import numpy as np

sys.path.insert(0, "scripts")
from panel_specs import BY_ID, PANEL

R_MANIPULATED = 0.95  # a corrupt cell counts as manipulated only if it falls below this


def pearson(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


def partial(x, y, z):
    x, y, z = map(lambda a: np.asarray(a, float), (x, y, z))
    rx = x - np.polyval(np.polyfit(z, x, 1), z)
    ry = y - np.polyval(np.polyfit(z, y, 1), z)
    return pearson(rx, ry)


def load(cid):
    path = f"runs/panel_cert/{cid}.jsonl"
    if not os.path.exists(path):
        return None
    out = {}
    for l in open(path):
        r = json.loads(l)
        if r.get("score") is not None:
            out[r["task_id"]] = float(r["score"])
    return out


labs = {r["id"]: r for r in json.load(open("human_eval/labels/phase1/author_1_Sri_random.json"))
        if r.get("soundness") not in (None, "")}

# honest twin = same judge, same protocol, corrupt=None
TWIN = {}
for c in PANEL:
    if not c["corrupt"]:
        continue
    twins = [d["id"] for d in PANEL if d["judge"] == c["judge"] and d["protocol"] == c["protocol"]
             and not d["corrupt"] and d["kind"] != "rm"]
    TWIN[c["id"]] = twins[0] if twins else None

out = {"threshold_r_manipulated": R_MANIPULATED, "cells": {}}
for cid, twin in TWIN.items():
    a, b = load(twin) if twin else None, load(cid)
    if a is None or b is None:
        print(f"[skip] {cid}: missing scores (twin={twin})")
        continue
    ids = [i for i in a if i in b]
    x, y = np.array([a[i] for i in ids]), np.array([b[i] for i in ids])
    lab_ids = [i for i in ids if i in labs]
    s = np.array([float(labs[i]["soundness"]) for i in lab_ids])
    t = np.array([float(labs[i]["style"]) for i in lab_ids])
    xa = np.array([a[i] for i in lab_ids])
    xb = np.array([b[i] for i in lab_ids])
    r = pearson(x, y)
    out["cells"][cid] = dict(
        honest_twin=twin, judge=BY_ID[cid]["judge"], protocol=BY_ID[cid]["protocol"],
        corrupt=BY_ID[cid]["corrupt"], n=len(ids),
        r_with_twin=round(r, 3), mean_shift=round(float(np.mean(y - x)), 3),
        sd_of_shift=round(float(np.std(y - x)), 3),
        nuisance_honest=round(partial(xa, t, s), 3), nuisance_corrupt=round(partial(xb, t, s), 3),
        target_honest=round(partial(xa, s, t), 3), target_corrupt=round(partial(xb, s, t), 3),
        manipulated=bool(r < R_MANIPULATED))
n = len(out["cells"])
k = sum(v["manipulated"] for v in out["cells"].values())
out["summary"] = dict(n_corrupt_cells=n, n_manipulated=k,
                      verdict=("manipulation failure: the corrupting instructions did not change "
                               "the judges' scores, so the panel's corrupt cells do not test "
                               "detection of a corrupted judge") if k == 0 else
                              f"{k} of {n} corrupt cells moved their judge")
json.dump(out, open("../../papers/analysis/panel_manipulation.json", "w"), indent=1)
md = ["# Manipulation check for the panel's corrupt-prompt cells (post hoc)\n",
      f"A cell counts as manipulated only if its anchor scores correlate with its honest twin's at "
      f"r < {R_MANIPULATED}.\n",
      "| cell | honest twin | corrupt | n | r with twin | mean shift | nuisance honest -> corrupt | target honest -> corrupt | manipulated |",
      "|---|---|---|---|---|---|---|---|---|"]
for cid, v in out["cells"].items():
    md.append(f"| {cid} | {v['honest_twin']} | {v['corrupt']} | {v['n']} | {v['r_with_twin']:.3f} | "
              f"{v['mean_shift']:+.3f} | {v['nuisance_honest']:+.2f} -> {v['nuisance_corrupt']:+.2f} | "
              f"{v['target_honest']:+.2f} -> {v['target_corrupt']:+.2f} | {'yes' if v['manipulated'] else 'NO'} |")
md.append(f"\n**{out['summary']['verdict']}** ({k}/{n} cells).")
open("../../papers/analysis/panel_manipulation.md", "w").write("\n".join(md) + "\n")
print("\n".join(md))
