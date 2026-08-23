# Registered analysis for the ladder perturbation-battery arms (P-B3, P-B4 in
# scripts/perturb_battery.py). COMMITTED BEFORE THE LADDER BATTERY DATA EXISTED.
# Run from experiments/tfa-vs-judge once runs/battery_Qwen_*.jsonl exist.
#
# Estimands, fixed here to avoid post-hoc choices:
#  Per configuration (judge x cond), per axis: delta = mean(score(variant) - score(orig))
#    over the labeled items, bootstrap CI over items.
#  P-B3: the blind 1.5B judge shows positive presentation-axis sensitivity
#    (primary read: mean delta over the four presentation axes auth/band/conf/hedge > 0
#    with CI excluding zero; hedge enters with its sign flipped, since a hedge is a
#    negative presentation cue).
#  P-B4 (Tier-1 -> Tier-2 validation): across ALL configurations with both a battery arm
#    and an audited style partial, PRIMARY sensitivity statistic = mean of |delta| over the
#    four presentation axes; validation criterion as registered: Spearman(sensitivity,
#    style partial) > 0.5. Secondary: all-six-axes version, reported alongside.
import glob
import json
import os
from collections import defaultdict

import numpy as np

rng = np.random.default_rng(0)
PRES = ["auth", "band", "conf", "hedge"]
ALL = ["len", "fmt", "auth", "band", "conf", "hedge"]


def load_battery(path):
    per = defaultdict(dict)
    for l in open(path):
        r = json.loads(l)
        if r.get("score") is not None:
            per[r["axis"]][r["id"]] = float(r["score"])
    return per


def deltas(per):
    out = {}
    base = per.get("orig", {})
    for ax in ALL:
        ids = [i for i in per.get(ax, {}) if i in base]
        d = np.array([per[ax][i] - base[i] for i in ids])
        if len(d) < 10:
            continue
        boot = [float(np.mean(rng.choice(d, len(d)))) for _ in range(2000)]
        out[ax] = dict(n=len(d), delta=round(float(d.mean()), 2),
                       ci=[round(float(np.percentile(boot, 2.5)), 2),
                           round(float(np.percentile(boot, 97.5)), 2)])
    return out


def rank(x):
    vals, inv, cnt = np.unique(np.asarray(x, float), return_inverse=True, return_counts=True)
    cum = np.cumsum(cnt) - cnt
    return (cum + (cnt - 1) / 2.0)[inv]


def spearman(x, y):
    return float(np.corrcoef(rank(x), rank(y))[0, 1])


results = {"configs": {}}
FILES = {}
for f in sorted(glob.glob("runs/battery_*_noref.jsonl")) + sorted(glob.glob("runs/battery_*_ref.jsonl")):
    base = os.path.basename(f)[len("battery_"):-6]
    FILES[base] = f
for tag, f in FILES.items():
    results["configs"][tag] = deltas(load_battery(f))
# frontier arms from the canonical JSONs (same axis keys)
for tag, jf in (("gpt_ref", "../../papers/analysis/battery_gpt_ref.json"),
                ("gpt_sabotage", "../../papers/analysis/battery_gpt_sabotage.json")):
    results["configs"][tag] = json.load(open(jf))

# P-B3: blind 1.5B presentation read (hedge sign-flipped)
cfg = results["configs"].get("Qwen_Qwen2.5-1.5B-Instruct_noref")
if cfg:
    parts = [cfg[a]["delta"] * (-1 if a == "hedge" else 1) for a in PRES if a in cfg]
    results["P_B3"] = dict(mean_presentation_delta=round(float(np.mean(parts)), 2),
                           per_axis={a: cfg[a] for a in PRES if a in cfg})

# P-B4: rank correlation of sensitivity vs audited style partial
STYLE = {  # from head_to_head.json (audited style partials)
    "Qwen_Qwen2.5-1.5B-Instruct_noref": 0.51, "Qwen_Qwen2.5-3B-Instruct_noref": 0.16,
    "Qwen_Qwen2.5-7B-Instruct_noref": -0.02, "Qwen_Qwen2.5-14B-Instruct_noref": -0.21,
    "Qwen_Qwen2.5-1.5B-Instruct_ref": 0.10, "Qwen_Qwen2.5-3B-Instruct_ref": -0.02,
    "Qwen_Qwen2.5-7B-Instruct_ref": -0.12, "Qwen_Qwen2.5-14B-Instruct_ref": -0.11,
    "gpt_ref": -0.22, "gpt_sabotage": 0.59,
}
xs, ys, used = [], [], []
for tag, sp in STYLE.items():
    cfg = results["configs"].get(tag)
    if not cfg:
        continue
    sens4 = float(np.mean([abs(cfg[a]["delta"]) for a in PRES if a in cfg]))
    xs.append(sens4); ys.append(sp); used.append(tag)
if len(xs) >= 5:
    sens6 = [float(np.mean([abs(results["configs"][t][a]["delta"])
                            for a in ALL if a in results["configs"][t]])) for t in used]
    results["P_B4"] = dict(n=len(xs), configs=used,
                           spearman_pres4=round(spearman(xs, ys), 2),
                           spearman_all6=round(spearman(sens6, ys), 2),
                           criterion="registered: spearman_pres4 > 0.5")
json.dump(results, open("../../papers/analysis/battery_ladder.json", "w"), indent=1)
print(json.dumps({k: v for k, v in results.items() if k != "configs"}, indent=1))
for tag, cfg in results["configs"].items():
    print(tag, {a: cfg[a]["delta"] for a in cfg})
