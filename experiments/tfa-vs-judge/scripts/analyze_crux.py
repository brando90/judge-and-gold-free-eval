#!/usr/bin/env python
# TLDR: Aggregate per-model JSONL rows and print the go/no-go crux report:
# rho(TFA, judge), rho(TFA, correct), and the DECISIVE partial rho(TFA, judge |
# correct) with bootstrap CIs, plus model-level means. Answers: does TFA track the
# frontier judge BEYOND free boxed-answer correctness?
from __future__ import annotations

import argparse
import glob
import json

import numpy as np

from tfa.analyze import crux_report, bootstrap_corr


def load_rows(paths: list[str]) -> list[dict]:
    rows = []
    for pat in paths:
        for fp in glob.glob(pat):
            with open(fp) as f:
                rows += [json.loads(l) for l in f if l.strip()]
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", nargs="+", help="glob(s) of run_all.py outputs")
    ap.add_argument("--metric", default="tfa_argmax", choices=["tfa_argmax", "tfa_logprob", "tfa_argmax_content"])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rows = [r for r in load_rows(args.jsonl)
            if r.get("judge_score") is not None and r.get(args.metric) is not None
            and not (isinstance(r[args.metric], float) and np.isnan(r[args.metric]))]
    if not rows:
        raise SystemExit("no usable rows (need judge_score and the TFA metric present)")

    tfa = np.array([r[args.metric] for r in rows], float)
    judge = np.array([r["judge_score"] for r in rows], float)
    correct = np.array([r["boxed_correct"] for r in rows], float)

    rep = crux_report(tfa, judge, correct)

    print(f"\n=== CRUX: TFA ({args.metric}) vs frontier judge  (item-level, pooled n={len(rows)}) ===")
    def show(name, c):
        print(f"  {name:32s} rho={c.rho:+.3f}  95% CI [{c.lo:+.3f}, {c.hi:+.3f}]  (n={c.n})")
    show("TFA vs judge", rep.tfa_vs_judge)
    show("TFA vs boxed-correct (free)", rep.tfa_vs_correct)
    show("judge vs boxed-correct", rep.judge_vs_correct)
    show(">> TFA vs judge | correct (partial)", rep.tfa_vs_judge_partial)
    show("   TFA vs judge (correct-only)", rep.tfa_vs_judge_within_correct)
    show("   TFA vs judge (wrong-only)", rep.tfa_vs_judge_within_wrong)

    # Model-level sanity view (few points, matches Putnam-AXIOM's model-level framing).
    print("\n  model-level means:")
    by_model: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        by_model.setdefault(r["model"], []).append(i)
    ms = sorted(by_model)
    if len(ms) >= 3:
        mt = np.array([tfa[by_model[m]].mean() for m in ms])
        mj = np.array([judge[by_model[m]].mean() for m in ms])
        mc = np.array([correct[by_model[m]].mean() for m in ms])
        show("mean-TFA vs mean-judge", bootstrap_corr(mt, mj, n_boot=2000))
        for m in ms:
            idx = by_model[m]
            print(f"    {m:40s} TFA={tfa[idx].mean():.3f}  judge={judge[idx].mean():.2f}  acc={correct[idx].mean():.3f}  (n={len(idx)})")

    print(f"\n  VERDICT: {rep.verdict}\n")

    if args.out:
        with open(args.out, "w") as f:
            json.dump(rep.to_dict(), f, indent=2)
        print(f"  wrote {args.out}")


if __name__ == "__main__":
    main()
