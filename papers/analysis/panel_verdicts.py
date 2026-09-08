# FROZEN PRE-RUN producer (Registration 6): the prospective panel's audit verdicts.
# Committed before any panel judge score existed, and RUN BEFORE any panel best-of-n outcome is
# generated. It computes, for every panel configuration, the two-dimensional audit measurement
# (target loading = soundness partial, nuisance loading = style partial) with bootstrap CIs on
# the same 60-item anchor set as the published audit, applies the frozen CI rule, and freezes the
# baseline predictors it will be compared against. Do not modify after the registration commit.
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/panel_verdicts.py
# Output: papers/analysis/panel_verdicts.json (+ .md)
import glob
import json
import os
import sys

import numpy as np
from scipy import stats

sys.path.insert(0, "scripts")
from panel_specs import BY_ID, PANEL, verdict

rng = np.random.default_rng(0)
B = 2000


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


def pairwise_accuracy(x, s):
    x, s = np.asarray(x, float), np.asarray(s, float)
    tot = conc = 0.0
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            if s[i] == s[j]:
                continue
            tot += 1
            d = (x[i] - x[j]) * (s[i] - s[j])
            conc += 1.0 if d > 0 else (0.5 if d == 0 else 0.0)
    return conc / tot if tot else float("nan")


def auc(x, c):
    x, c = np.asarray(x, float), np.asarray(c, int)
    pos, neg = x[c == 1], x[c == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    r = stats.rankdata(np.concatenate([pos, neg]))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


labs = {r["id"]: r for r in json.load(open("human_eval/labels/phase1/author_1_Sri_random.json"))
        if r.get("soundness") not in (None, "")}
out = {"anchor_n": len(labs), "rule": "frozen CI rule (panel_specs.verdict)", "configs": {}}
for cfg in PANEL:
    path = f"runs/panel_cert/{cfg['id']}.jsonl"
    if not os.path.exists(path):
        print(f"[missing] {path}")
        continue
    sc = {}
    for l in open(path):
        r = json.loads(l)
        if r.get("score") is not None:
            sc[r["task_id"]] = float(r["score"])
    ids = [i for i in labs if i in sc]
    if len(ids) < 20:
        print(f"[skip] {cfg['id']}: join {len(ids)}")
        continue
    x = np.array([sc[i] for i in ids])
    s = np.array([float(labs[i]["soundness"]) for i in ids])
    t = np.array([float(labs[i]["style"]) for i in ids])
    c = np.array([int(labs[i]["machine_correct"]) for i in ids])
    if len(set(x.tolist())) < 3:
        print(f"[warn] {cfg['id']}: {len(set(x.tolist()))} distinct scores (resolution)")
    sp, tp = partial(x, s, t), partial(x, t, s)
    sci, tci = bci(partial, x, s, t), bci(partial, x, t, s)
    out["configs"][cfg["id"]] = dict(
        judge=cfg["judge"], protocol=cfg["protocol"], kind=cfg["kind"], corrupt=cfg["corrupt"],
        n=len(ids), distinct_scores=len(set(x.tolist())),
        target_loading=round(sp, 3), target_ci=sci,
        nuisance_loading=round(tp, 3), nuisance_ci=tci,
        verdict=verdict(sp, sci[0], tp, tci[0]),
        baselines=dict(raw_pearson=round(pearson(x, s), 3),
                       spearman=round(float(stats.spearmanr(x, s).statistic), 3),
                       kendall=round(float(stats.kendalltau(x, s).statistic), 3),
                       pairwise_acc=round(pairwise_accuracy(x, s), 3),
                       auc_vs_correct=round(auc(x, c), 3),
                       ref_bit=int(cfg["protocol"] == "ref")))
json.dump(out, open("../../papers/analysis/panel_verdicts.json", "w"), indent=1)
md = [f"# Prospective panel audit verdicts (frozen CI rule, anchor n={out['anchor_n']})\n",
      "| config | judge | protocol | corrupt | n | target loading [CI] | nuisance loading [CI] | verdict | raw r | ref bit |",
      "|---|---|---|---|---|---|---|---|---|---|"]
for k, r in out["configs"].items():
    md.append(f"| {k} | {r['judge'].split('/')[-1]} | {r['protocol']} | {r['corrupt'] or '-'} | {r['n']} | "
              f"{r['target_loading']:+.2f} {r['target_ci']} | {r['nuisance_loading']:+.2f} {r['nuisance_ci']} | "
              f"**{r['verdict']}** | {r['baselines']['raw_pearson']:+.2f} | {r['baselines']['ref_bit']} |")
open("../../papers/analysis/panel_verdicts.md", "w").write("\n".join(md) + "\n")
print("\n".join(md))
