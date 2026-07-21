# Summarize SWE-bench A0 masked patch-TFA across the coder ladder: per-model mean added/changed/whole TFA,
# and (within-family) the Spearman correlation of added-lines TFA with model scale, the capability proxy.
import json, glob, re, numpy as np
from scipy import stats

SIZE = {"1.5B": 1.5, "7B": 7, "14B": 14, "32B": 32, "0.5B": 0.5, "3B": 3}
def size(m):
    z = re.search(r"(\d+\.?\d*)B", m)
    return float(z.group(1)) if z else np.nan

rows = []
for f in sorted(glob.glob("runs/swebench/swebench__*.jsonl")):
    R = [json.loads(l) for l in open(f)]
    if not R: continue
    m = f.split("__", 1)[1].replace(".jsonl", "")
    rows.append((m, size(m), len(R),
                 float(np.mean([r["tfa_masked_added"] for r in R])),
                 float(np.mean([r["tfa_masked_changed"] for r in R])),
                 float(np.mean([r["tfa_whole"] for r in R]))))
rows.sort(key=lambda x: x[1])
print(f"{'model':34s} {'size':>5s} {'n':>4s} {'added':>7s} {'changed':>8s} {'whole':>7s}")
for m, s, n, a, c, w in rows:
    print(f"{m:34s} {s:5.1f} {n:4d} {a:7.3f} {c:8.3f} {w:7.3f}")
if len(rows) >= 3:
    sz = [r[1] for r in rows]; ad = [r[3] for r in rows]
    print(f"\nwithin-family Spearman(model size, added-lines TFA) = {stats.spearmanr(sz, ad).statistic:+.2f}  (n={len(rows)})")
    print(f"within-family Spearman(model size, whole-diff TFA)  = {stats.spearmanr(sz, [r[5] for r in rows]).statistic:+.2f}")
