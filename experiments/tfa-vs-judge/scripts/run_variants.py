#!/usr/bin/env python
# TLDR: Compute TFA improvement variants (ideas 2 & 3) for one model over a dataset,
# teacher-forcing the gold PLUS corrupted golds. Saves per-item scores keyed by
# problem_id so analyze_variants.py can join them to the existing judge scores
# (no re-judging, no free-gen needed). GPU (vLLM prompt_logprobs).
#   python scripts/run_variants.py --model Qwen/Qwen2.5-14B-Instruct --dataset math500 --limit 500 --out runs/variants
from __future__ import annotations

import argparse
import json
import math
import os
from collections import Counter

from tfa.core import score_tfa, surprisal_weighted_tfa, weighted_tfa
from tfa.data import load_problems
from tfa.corrupt import corrupt_answer, corrupt_shuffle
from tfa.backends.vllm_backend import load_vllm, tfa_records_vllm_batch


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--dataset", default="math500")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--tp", type=int, default=1)
    ap.add_argument("--gpu-mem-util", type=float, default=0.85)
    ap.add_argument("--max-model-len", type=int, default=None)
    ap.add_argument("--out", default="runs/variants")
    args = ap.parse_args()

    problems = load_problems(args.dataset, limit=args.limit)
    llm, tok = load_vllm(args.model, tp_size=args.tp, max_model_len=args.max_model_len,
                         gpu_memory_utilization=args.gpu_mem_util)

    # Build the three teacher-forcing targets per problem: gold, answer-corrupted, shuffled.
    gold = [(p.question, p.gold_solution, p.dataset) for p in problems]
    cans = [(p.question, corrupt_answer(p.gold_solution), p.dataset) for p in problems]
    cshu = [(p.question, corrupt_shuffle(p.gold_solution), p.dataset) for p in problems]

    rec_gold = tfa_records_vllm_batch(llm, tok, gold)
    rec_cans = tfa_records_vllm_batch(llm, tok, cans)
    rec_cshu = tfa_records_vllm_batch(llm, tok, cshu)

    # Corpus IDF weights (idea 2, model-independent): rarer gold tokens weigh more.
    df = Counter()
    for recs in rec_gold:
        for t in {r.gold_id for r in recs}:
            df[t] += 1
    N = max(1, len(rec_gold))
    def idf_w(recs):
        return [math.log((N + 1) / (df.get(r.gold_id, 0) + 1)) + 1.0 for r in recs]

    os.makedirs(args.out, exist_ok=True)
    safe = args.model.replace("/", "__")
    path = f"{args.out}/{args.dataset}__{safe}.variants.jsonl"
    with open(path, "w") as f:
        for i, p in enumerate(problems):
            g = score_tfa(rec_gold[i]).tfa_argmax
            ca = score_tfa(rec_cans[i]).tfa_argmax
            cs = score_tfa(rec_cshu[i]).tfa_argmax
            f.write(json.dumps({
                "problem_id": p.id, "model": args.model, "dataset": p.dataset,
                "tfa_argmax": g,
                "tfa_surprisal": surprisal_weighted_tfa(rec_gold[i]),   # idea 2 (self-surprisal)
                "tfa_idf": weighted_tfa(rec_gold[i], idf_w(rec_gold[i])),  # idea 2 (corpus IDF)
                "tfa_corrupt_answer": ca,
                "tfa_shuffle": cs,
                "contrast_answer": g - ca,                              # idea 3
                "contrast_shuffle": g - cs,                            # idea 3
            }) + "\n")
    print(f"[done] wrote {path}")


if __name__ == "__main__":
    main()
