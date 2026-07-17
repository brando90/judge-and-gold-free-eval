#!/usr/bin/env python
# TLDR: Join the TFA variants (run_variants.py) to the existing judge scores
# (*.judged.jsonl, by model+problem_id) and test whether any variant improves the
# item-level correlation with the judge over baseline tfa_argmax. Reports raw
# r(variant, judge), partial r(variant, judge | correct), and within-correct r.
from __future__ import annotations

import argparse
import glob
import json

import numpy as np
from scipy import stats

from tfa.analyze import partial_spearman


def load(paths):
    rows = []
    for pat in paths:
        for fp in glob.glob(pat):
            rows += [json.loads(l) for l in open(fp) if l.strip()]
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", nargs="+", required=True)
    ap.add_argument("--judged", nargs="+", required=True)
    args = ap.parse_args()

    var = {(r["model"], r["problem_id"]): r for r in load(args.variants)}
    jud = {(r["model"], r["problem_id"]): r for r in load(args.judged)}
    keys = sorted(set(var) & set(jud))
    if not keys:
        raise SystemExit("no overlap between variants and judged files")

    judge = np.array([jud[k]["judge_score"] for k in keys], float)
    correct = np.array([jud[k]["boxed_correct"] for k in keys], float)
    cmask = correct == 1

    metrics = ["tfa_argmax", "tfa_surprisal", "tfa_idf", "contrast_answer", "contrast_shuffle"]
    print(f"joined n={len(keys)} items ({int(cmask.sum())} correct)\n")
    print(f"{'variant':18s} {'r(.,judge)':>11s} {'partial|correct':>16s} {'within-correct':>15s}")
    for m in metrics:
        x = np.array([var[k].get(m, np.nan) for k in keys], float)
        ok = ~np.isnan(x)
        raw = stats.spearmanr(x[ok], judge[ok]).statistic
        part = partial_spearman(x[ok], judge[ok], correct[ok])
        wc = stats.spearmanr(x[cmask & ok], judge[cmask & ok]).statistic
        tag = "  <- baseline" if m == "tfa_argmax" else ""
        print(f"{m:18s} {raw:+11.3f} {part:+16.3f} {wc:+15.3f}{tag}")

    print("\n(want: a variant whose partial|correct is clearly > baseline's, ideally positive)")


if __name__ == "__main__":
    main()
