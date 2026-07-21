#!/usr/bin/env python
# TLDR: Same as run_judge.py, but the Anthropic judge runs through the local
# `claude` CLI (Claude Code session login) instead of a metered API key via
# litellm. Use this for Anthropic judge families so cross-judge D1 runs do not
# consume ANTHROPIC_API_KEY credits. The subprocess env has ANTHROPIC_API_KEY
# stripped so `claude` falls back to the session OAuth login, not the key.
#
# Same rubric (tfa/judge.build_prompt) and same score parser (tfa/judge._parse_score)
# as run_judge.py, so scores are directly comparable to the API path. Slower
# (~5-6 s per call: CLI startup + one model turn) but free; parallelize with --workers.
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

from tfa.judge import build_prompt, _parse_score

# Env for the claude subprocess: drop ANTHROPIC_API_KEY so the CLI uses the
# Claude Code session login (subscription), not the metered API key.
_ENV = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}


def judge_via_cli(prompt: str, model: str | None, timeout: float) -> float | None:
    cmd = ["claude", "-p"]
    if model:
        cmd += ["--model", model]
    out = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True,
        env=_ENV, timeout=timeout,
    )
    if out.returncode != 0:
        return None
    return _parse_score(out.stdout or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", nargs="+", help="run_all.py outputs with free_gen saved (.judged.jsonl)")
    ap.add_argument("--model", default=None, help="claude model id to pin (default: session model)")
    ap.add_argument("--workers", type=int, default=8, help="parallel claude subprocesses")
    ap.add_argument("--timeout", type=float, default=120.0, help="per-call timeout seconds")
    ap.add_argument("--suffix", required=True, help="write to <file>.<suffix>.jsonl")
    ap.add_argument("--judge-tag", default="claude-cli", help="value stored in judge_model")
    args = ap.parse_args()

    for pat in args.jsonl:
        for fp in glob.glob(pat):
            rows = [json.loads(l) for l in open(fp) if l.strip()]
            if not rows or "free_gen" not in rows[0]:
                print(f"[skip] {fp}: no saved free_gen"); continue

            def _j(r):
                # Per-item resilience: a transient CLI failure or timeout must not
                # kill the run — skip it (None), same contract as run_judge.py.
                try:
                    p = build_prompt(r["question"], r["gold_solution"], r["free_gen"])
                    return judge_via_cli(p, args.model, args.timeout)
                except Exception:
                    return None
            with ThreadPoolExecutor(max_workers=args.workers) as ex:
                scores = list(ex.map(_j, rows))
            tag = args.model or args.judge_tag
            for r, s in zip(rows, scores):
                r["judge_score"] = s
                r["judge_model"] = f"cli:{tag}"

            out = fp.replace(".jsonl", f".{args.suffix}.jsonl")
            with open(out, "w") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
            n = sum(s is not None for s in scores)
            print(f"[done] {out}: judged {n}/{len(rows)} via claude CLI ({tag})")


if __name__ == "__main__":
    main()
