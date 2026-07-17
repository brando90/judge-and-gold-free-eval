#!/usr/bin/env python
# TLDR: Run the full crux pipeline for ONE model on ONE dataset and write per-item
# rows (TFA on gold, free-gen, boxed-correct, judge score) to JSONL. One vLLM load
# serves both TFA and free-gen; the judge is a frontier API model. Repeat per model,
# then aggregate with analyze_crux.py.
#
# Example (on a SNAP GPU node, inside the env):
#   python scripts/run_all.py --model Qwen/Qwen2.5-7B-Instruct --dataset math500 \
#       --limit 500 --judge-model openai/gpt-5.2 --tp 1 --out runs/math500
from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor

from tfa.core import score_tfa
from tfa.data import load_problems
from tfa.boxed import is_correct
from tfa.judge import judge_score
from tfa.freegen import free_generate
from tfa.backends.vllm_backend import load_vllm, tfa_records_vllm_batch


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--dataset", default="math500")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--judge-model", default=None, help="litellm id, e.g. openai/gpt-5.2 (web-search current SOTA first); not needed with --dry-run")
    ap.add_argument("--tp", type=int, default=1, help="tensor-parallel size")
    ap.add_argument("--max-model-len", type=int, default=None)
    ap.add_argument("--gpu-mem-util", type=float, default=0.85,
                    help="vLLM gpu_memory_utilization; lower it to fit on partially-used shared GPUs")
    ap.add_argument("--judge-workers", type=int, default=8)
    ap.add_argument("--out", default="runs/out")
    ap.add_argument("--dry-run", action="store_true",
                    help="no GPU/API: fake backends with a planted signal, to smoke-test the plumbing")
    ap.add_argument("--no-judge", action="store_true",
                    help="E1 mode: compute TFA + free-gen accuracy only, skip the LLM judge")
    args = ap.parse_args()
    if not args.dry_run and not args.no_judge and not args.judge_model:
        ap.error("--judge-model is required unless --dry-run or --no-judge is set")

    if args.dry_run:
        from tfa.dryrun import fake_problems, fake_tfa_records, fake_free_and_judge
        cap = {"weak": -1.0, "mid": 0.0, "strong": 1.5}.get(args.model, 0.0)
        problems = fake_problems(args.limit or 60)
        tfa_scores, free, correct, judge_scores = [], [], [], []
        for i, p in enumerate(problems):
            tfa_scores.append(score_tfa(fake_tfa_records(p.meta["latent"], cap, seed=i)))
            fr, c, j = fake_free_and_judge(p.meta["latent"], cap, p.gold_answer, seed=i)
            free.append(fr); correct.append(is_correct(fr, p.gold_answer, p.dataset)); judge_scores.append(j)
        print(f"[dry-run] {len(problems)} fake problems, model-capability={cap}")
    else:
        problems = load_problems(args.dataset, limit=args.limit)
        print(f"[data] {len(problems)} problems from {args.dataset}")

        llm, tok = load_vllm(args.model, tp_size=args.tp, max_model_len=args.max_model_len,
                             gpu_memory_utilization=args.gpu_mem_util)

        # 1) TFA on the gold trace (teacher-forced), batched.
        tfa_items = [(p.question, p.gold_solution, p.dataset) for p in problems]
        tfa_recs = tfa_records_vllm_batch(llm, tok, tfa_items)
        tfa_scores = [score_tfa(r) for r in tfa_recs]

        # 2) Free-generation (the model's own trace) for judge + boxed correctness.
        free = free_generate(llm, tok, [(p.question, p.dataset) for p in problems])

        # 3) Boxed correctness (the FREE anchor correlate TFA must beat).
        correct = [is_correct(free[i], problems[i].gold_answer, problems[i].dataset) for i in range(len(problems))]

        # 4) Frontier LLM judge on reasoning quality of the free-gen trace.
        #    E1 (the TFA<->accuracy reproduction) does not need the judge; skip with --no-judge.
        if args.no_judge:
            judge_scores = [None] * len(problems)
        else:
            def _judge(i):
                return judge_score(args.judge_model, problems[i].question, problems[i].gold_solution, free[i])
            with ThreadPoolExecutor(max_workers=args.judge_workers) as ex:
                judge_scores = list(ex.map(_judge, range(len(problems))))

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    safe_model = args.model.replace("/", "__")
    path = f"{args.out}/{args.dataset}__{safe_model}.jsonl"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for i, p in enumerate(problems):
            f.write(json.dumps({
                "problem_id": p.id, "dataset": p.dataset, "model": args.model,
                "judge_model": args.judge_model,
                "tfa_argmax": tfa_scores[i].tfa_argmax,
                "tfa_logprob": tfa_scores[i].tfa_logprob,
                "bpc_bits": tfa_scores[i].bpc_bits,
                "tfa_argmax_content": tfa_scores[i].tfa_argmax_content,
                "n_gold_tokens": tfa_scores[i].n,
                "boxed_correct": correct[i],
                "judge_score": judge_scores[i],
                "question": p.question,
                "gold_solution": p.gold_solution,
                "free_gen": free[i],
            }) + "\n")
    n_judged = sum(j is not None for j in judge_scores)
    print(f"[done] wrote {path}  (judged {n_judged}/{len(problems)}, acc={sum(correct)/len(correct):.3f})")


if __name__ == "__main__":
    main()
