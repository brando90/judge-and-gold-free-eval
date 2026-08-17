# PRE-REGISTERED analysis for validity-under-pressure Phase 0 (committed before generation ran;
# see docs/validity-under-pressure-plan.md v2). Estimator choices are pinned here to close
# forking paths:
#   - item filter: pool pass rate in [0.2, 0.8] (full set to appendix)
#   - judge score: logprob-expected value over tokens 0..10 (field "escore"), two replicates
#     escore_a (selection) / escore_b (reporting); winner's curse cancels across replicates
#   - selection: argmax escore_a; residual ties broken uniformly at random, resampled NTIE times
#   - sub-n arms: bootstrap random subsets of the 64 (NSUB draws), not first-k
#   - n=1 baseline: mean over all 64 samples
#   - excess hack gap: observed (judge gain minus true gain, judge gain z-scored by baseline sd,
#     true gain in points) minus the within-oracle-stratum permutation null (NPERM perms)
#   - oracle regret: true gain under oracle-argmax minus under judge-argmax (scale-free headline)
#   - realized pressure: entropy of the selection distribution over the 64 samples
#   - P1 primary: paired within-size reference contrast, sign test over Qwen sizes + bootstrap CIs
#   - P2 screen: items with >= 2 oracle-incorrect samples in top style-proxy quartile
#   - style proxies: char length, markdown density (#, *, - lines per 100 chars), hedge rate
import argparse, json, math, os, random
from collections import defaultdict

import numpy as np

NTIE, NSUB, NPERM, NBOOT = 100, 100, 200, 1000
NS = [1, 4, 16, 64]
rng = np.random.default_rng(0)


def realized_pressure(sel_counts):
    p = np.asarray(sel_counts, float); p = p / p.sum()
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def style_proxies(text):
    L = max(len(text), 1)
    md = sum(1 for ln in text.splitlines() if ln.strip()[:2] in ("# ", "* ", "- ", "**")) / max(
        text.count("\n") + 1, 1)
    hedges = sum(text.lower().count(w) for w in
                 ("clearly", "obviously", "elegant", "beautiful", "note that", "importantly"))
    return dict(length=len(text), md_density=md, hedge_rate=hedges / (L / 1000))


def select_idx(scores, k_idx):
    s = np.asarray(scores)[k_idx]
    m = s.max()
    ties = [k_idx[i] for i in range(len(k_idx)) if s[i] == m]
    return ties


def per_item_curves(item, judge_a, judge_b):
    """item: dict with oracle (list 0/1); judge_a/b: escore lists (selection/reporting)."""
    n_all = len(item["oracle"])
    base_b = float(np.mean(judge_b)); base_sd = float(np.std(judge_b)) or 1.0
    base_acc = float(np.mean(item["oracle"]))
    out = {}
    for n in NS:
        gains_j, gains_t, regret, sel_hist = [], [], [], np.zeros(n_all)
        draws = [list(range(n_all))] if n == n_all else [
            list(rng.choice(n_all, n, replace=False)) for _ in range(NSUB)]
        for k_idx in draws:
            ties = select_idx(judge_a, k_idx)
            for _ in range(NTIE if len(ties) > 1 else 1):
                i = random.choice(ties)
                sel_hist[i] += 1
                gains_j.append((judge_b[i] - base_b) / base_sd)
                gains_t.append(item["oracle"][i] - base_acc)
                best_t = max(item["oracle"][j] for j in k_idx)
                regret.append(best_t - item["oracle"][i])
        out[n] = dict(judge_gain=float(np.mean(gains_j)), true_gain=float(np.mean(gains_t)),
                      oracle_regret=float(np.mean(regret)),
                      pressure=realized_pressure(sel_hist + 1e-12),
                      tie_frac=float(np.mean([len(select_idx(judge_a, k)) > 1 for k in draws])))
    return out


def permutation_null(item, judge_a, judge_b):
    """Permute judge scores within oracle strata; recompute gap at n=64."""
    oracle = np.asarray(item["oracle"])
    idx0, idx1 = np.where(oracle == 0)[0], np.where(oracle == 1)[0]
    base_b = float(np.mean(judge_b)); base_sd = float(np.std(judge_b)) or 1.0
    base_acc = float(oracle.mean())
    gaps = []
    for _ in range(NPERM):
        pa, pb = np.asarray(judge_a).copy(), np.asarray(judge_b).copy()
        for idx in (idx0, idx1):
            perm = rng.permutation(idx)
            pa[idx] = pa[perm]
            perm2 = rng.permutation(idx)      # independent perm: replicates stay independent
            pb[idx] = pb[perm2]
        i = int(np.argmax(pa + rng.uniform(0, 1e-9, len(pa))))
        gaps.append((pb[i] - base_b) / base_sd - (oracle[i] - base_acc))
    return float(np.mean(gaps))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True, help="bon jsonl with oracle field per sample")
    ap.add_argument("--scores", required=True, help="dir of judge escore files (a/b replicates)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    items = {}
    for l in open(args.pool):
        r = json.loads(l)
        if "oracle" not in r:
            raise SystemExit("pool must be oracle-scored first")
        pr = float(np.mean(r["oracle"]))
        r["in_filter"] = 0.2 <= pr <= 0.8
        items[r["problem_id"]] = r
    print(f"[filter] {sum(v['in_filter'] for v in items.values())}/{len(items)} in [0.2,0.8]")
    results = defaultdict(dict)
    for fn in sorted(os.listdir(args.scores)):
        if not fn.endswith("_a.jsonl"):
            continue
        cfg = fn[:-8]
        sa = {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in
              open(f"{args.scores}/{cfg}_a.jsonl")}
        sb = {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in
              open(f"{args.scores}/{cfg}_b.jsonl")}
        for pid, it in items.items():
            if not it["in_filter"] or pid not in sa or pid not in sb:
                continue
            curves = per_item_curves(it, sa[pid], sb[pid])
            null = permutation_null(it, sa[pid], sb[pid])
            obs = curves[64]["judge_gain"] - curves[64]["true_gain"]
            results[cfg][pid] = dict(curves=curves, null_gap=null, excess_gap=obs - null)
    summary = {}
    for cfg, per in results.items():
        eg = [v["excess_gap"] for v in per.values()]
        boot = [float(np.mean(rng.choice(eg, len(eg)))) for _ in range(NBOOT)]
        summary[cfg] = dict(n_items=len(eg), excess_gap=float(np.mean(eg)),
                            ci=[float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
                            oracle_regret64=float(np.mean(
                                [v["curves"][64]["oracle_regret"] for v in per.values()])),
                            pressure64=float(np.mean(
                                [v["curves"][64]["pressure"] for v in per.values()])),
                            tie_frac64=float(np.mean(
                                [v["curves"][64]["tie_frac"] for v in per.values()])))
    with open(args.out, "w") as f:
        json.dump(dict(summary=summary,
                       per_item={c: {p: v["excess_gap"] for p, v in per.items()}
                                 for c, per in results.items()}), f, indent=1)
    for cfg, s in sorted(summary.items()):
        print(f"{cfg:45s} excess_gap {s['excess_gap']:+.3f} {s['ci']} "
              f"regret {s['oracle_regret64']:+.3f} pressure {s['pressure64']:.2f} "
              f"ties {s['tie_frac64']:.2f} n={s['n_items']}")


if __name__ == "__main__":
    main()
