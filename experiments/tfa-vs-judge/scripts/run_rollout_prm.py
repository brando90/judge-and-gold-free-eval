#!/usr/bin/env python
# TLDR: Math-Shepherd-style rollout process value with a FIXED strong completer,
# decoupled from the evaluated model. For each stored response, truncate its own
# free-gen at cut-point fractions, let the completer CONTINUE (prefix-committed) K
# times, check answers vs gold -> V(f)=fraction reaching the correct answer. Saves
# the value trajectory + judge/correct for the partial-correlation test. Includes
# f=0 (completer base solve-rate) as a wash-out diagnostic.
#   python scripts/run_rollout_prm.py --completer Qwen/Qwen2.5-32B-Instruct \
#     --responses 'runs/math500/*.judged.jsonl' --models Qwen/Qwen2.5-1.5B-Instruct \
#     Qwen/Qwen2.5-7B-Instruct Qwen/Qwen2.5-14B-Instruct --n-problems 50 --k 8 --tp 2
from __future__ import annotations

import argparse
import collections
import glob
import json
import os

from tfa.boxed import extract_boxed, extract_final_answer, answers_equivalent
from tfa.backends.common import build_tf_prompt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--completer", required=True, help="fixed strong completer model")
    ap.add_argument("--responses", nargs="+", required=True, help="judged.jsonl globs (responses to score)")
    ap.add_argument("--models", nargs="+", default=None, help="restrict to these evaluated models")
    ap.add_argument("--n-problems", type=int, default=50)
    ap.add_argument("--k", type=int, default=8, help="rollouts per cut-point")
    ap.add_argument("--cutpoints", default="0,0.25,0.5,0.75", help="prefix fractions of the response")
    ap.add_argument("--tp", type=int, default=2)
    ap.add_argument("--gpu-mem-util", type=float, default=0.9)
    ap.add_argument("--max-model-len", type=int, default=8192)
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--seed", type=int, default=0, help="rollout sampling seed (for reproducibility)")
    ap.add_argument("--save-raw", default=None, help="dir to dump raw per-rollout completions + correctness")
    ap.add_argument("--out", default="runs/prm")
    args = ap.parse_args()
    cuts = [float(x) for x in args.cutpoints.split(",")]

    rows = []
    for pat in args.responses:
        for fp in glob.glob(pat):
            rows += [json.loads(l) for l in open(fp) if l.strip()]
    if args.models:
        rows = [r for r in rows if r["model"] in args.models]
    pids = sorted({r["problem_id"] for r in rows})[: args.n_problems]
    pset = set(pids)
    rows = [r for r in rows if r["problem_id"] in pset]
    print(f"[data] scoring {len(rows)} responses over {len(pids)} problems | completer={args.completer} K={args.k} cuts={cuts}")

    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from transformers import AutoTokenizer

    llm = LLM(model=args.completer, tensor_parallel_size=args.tp, dtype="bfloat16",
              gpu_memory_utilization=args.gpu_mem_util, max_model_len=args.max_model_len,
              enable_prefix_caching=False)
    tok = AutoTokenizer.from_pretrained(args.completer)

    prompts, meta = [], []
    for ri, r in enumerate(rows):
        base = tok(build_tf_prompt(r["question"], r.get("dataset", "math500")), add_special_tokens=True).input_ids
        resp = tok(r["free_gen"], add_special_tokens=False).input_ids
        for f in cuts:
            kcut = int(f * len(resp))
            ids = (base + resp[:kcut])[: args.max_model_len - args.max_tokens - 8]
            prompts.append(TokensPrompt(prompt_token_ids=ids))
            meta.append((ri, f))

    sp = SamplingParams(n=args.k, temperature=0.8, top_p=0.95, max_tokens=args.max_tokens, seed=args.seed)
    outs = llm.generate(prompts, sp)

    raw_fh = None
    if args.save_raw:
        os.makedirs(args.save_raw, exist_ok=True)
        raw_fh = open(f"{args.save_raw}/rollouts__{args.completer.replace('/','__')}.jsonl", "w")

    V = collections.defaultdict(dict)
    for (ri, f), out in zip(meta, outs):
        ds = rows[ri].get("dataset", "math500")
        gold = extract_boxed(rows[ri]["gold_solution"])
        per = [{"pred": extract_final_answer(o.text, ds),
                "correct": int(answers_equivalent(extract_final_answer(o.text, ds), gold)),
                "text": o.text[:800]} for o in out.outputs]
        V[ri][f] = sum(r["correct"] for r in per) / max(1, len(per))
        if raw_fh:
            raw_fh.write(json.dumps({"problem_id": rows[ri]["problem_id"], "model": rows[ri]["model"],
                                     "completer": args.completer, "cut": f, "seed": args.seed,
                                     "rollouts": per}) + "\n")
    if raw_fh:
        raw_fh.close()

    os.makedirs(args.out, exist_ok=True)
    path = f"{args.out}/rollout_prm__{args.completer.replace('/','__')}.jsonl"
    with open(path, "w") as fo:
        for ri, r in enumerate(rows):
            fo.write(json.dumps({
                "problem_id": r["problem_id"], "model": r["model"], "completer": args.completer,
                "judge_score": r["judge_score"], "boxed_correct": r["boxed_correct"],
                "V": {str(f): V[ri][f] for f in cuts},
            }) + "\n")
    print(f"[done] wrote {path}")


if __name__ == "__main__":
    main()
