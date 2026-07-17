#!/usr/bin/env python
# TLDR: E1 reproduction report. Putnam-AXIOM showed TFA correlates ~0.66 with
# boxed final-answer accuracy on MATH. This aggregates per-model JSONL rows and
# reports the MODEL-LEVEL correlation between mean-TFA and accuracy (the headline
# reproduction number), plus the item-level TFA<->correct correlation. No judge
# needed. If this brackets ~0.66, our TFA instrument is validated.
from __future__ import annotations

import argparse
import glob
import json

import numpy as np

from tfa.analyze import bootstrap_corr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", nargs="+")
    ap.add_argument("--metric", default="tfa_argmax")
    args = ap.parse_args()

    rows = []
    for pat in args.jsonl:
        for fp in glob.glob(pat):
            with open(fp) as f:
                rows += [json.loads(l) for l in f if l.strip()]
    rows = [r for r in rows if r.get(args.metric) is not None
            and not (isinstance(r[args.metric], float) and np.isnan(r[args.metric]))]
    if not rows:
        raise SystemExit("no usable rows")

    by_model: dict[str, list[dict]] = {}
    for r in rows:
        by_model.setdefault(r["model"], []).append(r)

    print(f"\n=== E1: TFA ({args.metric}) vs boxed accuracy on {rows[0]['dataset']} ===")
    print(f"{'model':40s} {'mean-TFA':>9s} {'accuracy':>9s} {'n':>5s}")
    models, mtfa, macc = [], [], []
    for m in sorted(by_model):
        rs = by_model[m]
        t = float(np.mean([r[args.metric] for r in rs]))
        a = float(np.mean([r["boxed_correct"] for r in rs]))
        models.append(m); mtfa.append(t); macc.append(a)
        print(f"{m:40s} {t:9.3f} {a:9.3f} {len(rs):5d}")

    # Item-level (pooled) TFA vs correctness.
    tfa = np.array([r[args.metric] for r in rows], float)
    cor = np.array([r["boxed_correct"] for r in rows], float)
    item = bootstrap_corr(tfa, cor, method="spearman")
    print(f"\n  item-level  rho(TFA, correct)  = {item.rho:+.3f}  95% CI [{item.lo:+.3f}, {item.hi:+.3f}]  (n={item.n})")

    if len(models) >= 3:
        ml = bootstrap_corr(np.array(mtfa), np.array(macc), method="spearman", n_boot=5000)
        mlp = bootstrap_corr(np.array(mtfa), np.array(macc), method="pearson", n_boot=5000)
        print(f"  model-level rho(mean-TFA, acc)  = {ml.rho:+.3f}  (Pearson r={mlp.rho:+.3f})   [reproduction target ~0.66]")
    else:
        print(f"  (need >=3 models for a model-level correlation; have {len(models)})")


if __name__ == "__main__":
    main()
