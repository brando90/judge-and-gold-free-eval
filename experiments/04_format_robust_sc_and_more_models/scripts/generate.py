#!/usr/bin/env python3
"""Experiment 03 generation: n samples per MATH-500 problem from one model (vLLM), same harness as
experiments/tfa-vs-judge/scripts/bon_generate.py (same prompt, temperature 1.0, top_p 0.95, max_tokens 1024, seed 0),
except: Qwen3 chat templates are rendered with enable_thinking=False (non-thinking mode), and n defaults to 16.
Run on a GPU host with vLLM (skampere1):
    CUDA_VISIBLE_DEVICES=3 python3 generate.py --model Qwen/Qwen2.5-7B-Instruct --n 16 --out ~/jfe03/gen --util 0.35
Writes <out>/bon_math__<model with / as __>.jsonl, one row per problem (problem_id, model, samples, answer, level, subject).
Resumes: problems already in the output file are skipped.
"""
import argparse, json, os

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True, help="HF id or a local snapshot directory")
ap.add_argument("--name", default=None, help="HF id used in the output file name and the Qwen3 check (when --model is a path)")
ap.add_argument("--tasks", default="bon_math_tasks.jsonl")
ap.add_argument("--n", type=int, default=16)
ap.add_argument("--out", default="gen")
ap.add_argument("--util", type=float, default=0.35)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
name = args.name or args.model
out = f"{args.out}/bon_math__{name.replace('/', '__')}.jsonl"

tasks = [json.loads(l) for l in open(args.tasks)]
done = set()
if os.path.exists(out):
    for l in open(out):
        try:
            done.add(json.loads(l)["problem_id"])
        except Exception:
            pass
tasks = [r for r in tasks if r["problem_id"] not in done]
print(f"[gen] {args.model}: {len(tasks)} problems remaining, n={args.n}", flush=True)
if not tasks:
    raise SystemExit

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

tok = AutoTokenizer.from_pretrained(args.model)
kw = {"enable_thinking": False} if "Qwen3" in name else {}


def prompt_of(r):
    return ("Solve the following math problem. Show your reasoning step by step, "
            "then give the final answer in \\boxed{}.\n\n" + r["problem"])


prompts = [tok.apply_chat_template([{"role": "user", "content": prompt_of(r)}], tokenize=False,
                                   add_generation_prompt=True, **kw) for r in tasks]
llm = LLM(model=args.model, dtype="bfloat16", gpu_memory_utilization=args.util, max_model_len=4096)
sp = SamplingParams(n=args.n, max_tokens=1024, temperature=1.0, top_p=0.95, seed=0)
B = 50
with open(out, "a") as f:
    for i in range(0, len(tasks), B):
        outs = llm.generate(prompts[i:i + B], sp)
        for r, o in zip(tasks[i:i + B], outs):
            row = dict(problem_id=r["problem_id"], model=args.model, samples=[c.text for c in o.outputs],
                       finish=[c.finish_reason for c in o.outputs], answer=r["answer"], level=r["level"],
                       subject=r["subject"])
            f.write(json.dumps(row) + "\n")
        f.flush()
        print(f"[gen] {min(i + B, len(tasks))}/{len(tasks)}", flush=True)
print("[gen done]", out, flush=True)
