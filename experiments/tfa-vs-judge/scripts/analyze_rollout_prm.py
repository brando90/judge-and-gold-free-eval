#!/usr/bin/env python
# TLDR: Test whether the rollout process value tracks the judge beyond correctness.
# First a wash-out diagnostic (does V vary; do non-zero cut-points differ from the
# f=0 base solve-rate?). Then, for several trajectory features, partial ρ(feature,
# judge | correct) plus within-correct and within-wrong, vs. the TFA baseline (~0).
from __future__ import annotations

import argparse
import glob
import json

import numpy as np
from scipy import stats

from tfa.analyze import partial_spearman


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prm", nargs="+", help="rollout_prm jsonl globs")
    args = ap.parse_args()
    R = []
    for pat in args.prm:
        for fp in glob.glob(pat):
            R += [json.loads(l) for l in open(fp) if l.strip()]
    cuts = sorted({float(k) for r in R for k in r["V"]})
    def Vc(r, f): return r["V"][str(f)]
    judge = np.array([r["judge_score"] for r in R], float)
    correct = np.array([r["boxed_correct"] for r in R], float)

    base = np.array([Vc(r, 0.0) for r in R]) if 0.0 in cuts else None
    nz = [f for f in cuts if f > 0]
    meanV = np.array([np.mean([Vc(r, f) for f in nz]) for r in R])
    minV = np.array([min(Vc(r, f) for f in nz) for r in R])
    lastV = np.array([Vc(r, max(nz)) for r in R])
    dropV = np.array([Vc(r, nz[0]) - Vc(r, max(nz)) for r in R])
    lift = (meanV - base) if base is not None else meanV  # prefix value above completer base rate

    print(f"n={len(R)} responses | cuts={cuts} | correct={int(correct.sum())}")
    print("\n### wash-out diagnostic")
    if base is not None:
        print(f"  V(0) completer base solve-rate: mean={base.mean():.3f} sd={base.std():.3f}")
    print(f"  meanV: mean={meanV.mean():.3f} sd={meanV.std():.3f}   (need sd>>0 for any signal)")
    if base is not None:
        print(f"  lift (meanV - base): mean={lift.mean():+.3f} sd={lift.std():.3f}   (>0 => prefix informative, ~0 => wash-out)")

    print("\n### does the value track the judge, beyond correctness?")
    print(f"{'feature':10s} {'r(.,judge)':>11s} {'partial|correct':>16s} {'within-corr':>12s} {'within-wrong':>13s}")
    def show(name, x):
        ok = ~np.isnan(x)
        raw = stats.spearmanr(x[ok], judge[ok]).statistic
        part = partial_spearman(x[ok], judge[ok], correct[ok])
        cm = (correct == 1) & ok; wm = (correct == 0) & ok
        wc = stats.spearmanr(x[cm], judge[cm]).statistic if cm.sum() > 5 else float("nan")
        ww = stats.spearmanr(x[wm], judge[wm]).statistic if wm.sum() > 5 else float("nan")
        print(f"{name:10s} {raw:+11.3f} {part:+16.3f} {wc:+12.3f} {ww:+13.3f}")
    show("meanV", meanV)
    show("minV", minV)
    show("lastV", lastV)
    show("dropV", -dropV)   # more drop = worse; negate so higher=better for sign consistency
    show("lift", lift)
    print("\n(baseline TFA partial|correct ~ 0; want a feature clearly > 0)")


if __name__ == "__main__":
    main()
