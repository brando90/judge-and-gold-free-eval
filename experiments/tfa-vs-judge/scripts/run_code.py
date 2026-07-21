#!/usr/bin/env python
# WS5: TFA on gold code + free-gen + deterministic code-oracle correctness (pass@1) for ONE model on a code
# dataset (humaneval/mbpp). One vLLM load serves TFA (teacher-forced on the canonical solution) and free-gen.
# Correctness runs the model's extracted code against the benchmark's unit tests. No judge, no API.
from __future__ import annotations
import argparse, json, os, re, sys

from tfa.core import score_tfa
from tfa.data import load_problems
from tfa.backends.vllm_backend import load_vllm, tfa_records_vllm_batch
from tfa.code_oracle import _run, mbpp_pass


def extract_code(text: str) -> str:
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    if m:
        return m.group(1)
    # fallback: from the first def/import to the end
    m = re.search(r"(^(?:def |import |from |class ).*)", text, re.S | re.M)
    return m.group(1) if m else text


def free_gen_code(llm, tok, problems, max_tokens=1024):
    from vllm import SamplingParams
    prompts = []
    for p in problems:
        if p.dataset == "humaneval":
            msg = ("Complete the following Python function. Return the full function in one ```python code "
                   "block and nothing else.\n\n" + p.question)
        else:
            t0 = (p.meta.get("test_list") or [""])[0]
            msg = ("Write a Python function for the task. Return the function in one ```python code block and "
                   f"nothing else.\n\nTask: {p.question}\nIt must satisfy: {t0}")
        prompts.append(tok.apply_chat_template([{"role": "user", "content": msg}],
                                               tokenize=False, add_generation_prompt=True))
    sp = SamplingParams(max_tokens=max_tokens, temperature=0.0, seed=0)
    outs = llm.generate(prompts, sp)
    return [o.outputs[0].text for o in outs]


def code_pass(p, gen: str) -> bool:
    code = extract_code(gen)
    if p.dataset == "humaneval":
        # the extracted code is expected to define entry_point on its own
        return _run(code + "\n" + p.meta["test"] + f"\ncheck({p.meta['entry_point']})\n")
    return mbpp_pass(code, p.meta["test_list"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--dataset", default="humaneval", choices=["humaneval", "mbpp"])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--tp", type=int, default=1)
    ap.add_argument("--gpu-mem-util", type=float, default=0.85)
    ap.add_argument("--out", default="runs/code")
    args = ap.parse_args()

    problems = load_problems(args.dataset, limit=args.limit)
    print(f"[data] {len(problems)} problems from {args.dataset}")
    llm, tok = load_vllm(args.model, tp_size=args.tp, gpu_memory_utilization=args.gpu_mem_util)

    # TFA teacher-forced on the canonical (gold) code.
    tfa_recs = tfa_records_vllm_batch(llm, tok, [(p.question, p.gold_solution, p.dataset) for p in problems])
    tfa_scores = [score_tfa(r) for r in tfa_recs]

    free = free_gen_code(llm, tok, problems)
    passed = [code_pass(problems[i], free[i]) for i in range(len(problems))]

    os.makedirs(args.out, exist_ok=True)
    safe = args.model.replace("/", "__")
    path = f"{args.out}/{args.dataset}__{safe}.jsonl"
    with open(path, "w") as f:
        for i, p in enumerate(problems):
            f.write(json.dumps({
                "problem_id": p.id, "dataset": p.dataset, "model": args.model,
                "tfa_argmax": tfa_scores[i].tfa_argmax, "tfa_logprob": tfa_scores[i].tfa_logprob,
                "n_gold_tokens": tfa_scores[i].n, "code_pass": int(passed[i]),
            }) + "\n")
    print(f"[done] wrote {path}  (pass@1 = {sum(passed)/len(passed):.3f})")
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
