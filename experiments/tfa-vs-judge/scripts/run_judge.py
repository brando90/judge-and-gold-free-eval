#!/usr/bin/env python
# TLDR: GPU-free judging of saved free-gen traces. Reads a JSONL that already has
# free_gen/question/gold_solution (written by run_all.py), scores each trace with a
# frontier judge via litellm, and writes judge_score back. Lets us add judges (or
# judge families) without re-running any GPU inference. Needs the provider API key
# in the environment (e.g. ANTHROPIC_API_KEY).
from __future__ import annotations

import argparse
import glob
import json
import os
from concurrent.futures import ThreadPoolExecutor

from tfa.judge import judge_score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", nargs="+", help="run_all.py outputs with free_gen saved")
    ap.add_argument("--judge-model", required=True, help="litellm id, e.g. anthropic/claude-opus-4-8")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--suffix", default=None, help="write to <file>.<suffix>.jsonl instead of in place")
    args = ap.parse_args()

    for pat in args.jsonl:
        for fp in glob.glob(pat):
            rows = [json.loads(l) for l in open(fp) if l.strip()]
            if not rows or "free_gen" not in rows[0]:
                print(f"[skip] {fp}: no saved free_gen"); continue

            def _j(r):
                return judge_score(args.judge_model, r["question"], r["gold_solution"], r["free_gen"])
            with ThreadPoolExecutor(max_workers=args.workers) as ex:
                scores = list(ex.map(_j, rows))
            for r, s in zip(rows, scores):
                r["judge_score"] = s
                r["judge_model"] = args.judge_model

            out = fp if not args.suffix else fp.replace(".jsonl", f".{args.suffix}.jsonl")
            with open(out, "w") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
            n = sum(s is not None for s in scores)
            print(f"[done] {out}: judged {n}/{len(rows)} with {args.judge_model}")


if __name__ == "__main__":
    main()
