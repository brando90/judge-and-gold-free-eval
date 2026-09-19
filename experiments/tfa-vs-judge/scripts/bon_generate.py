# Phase 0 of validity-under-pressure: sample n=64 solutions per problem from a fixed generator.
# Nested-n design: sample order is the pressure schedule (best-of-n uses the first n samples),
# so one generation run yields the whole pressure curve.
import argparse, json, os

from vllm import LLM, SamplingParams

ap = argparse.ArgumentParser()
ap.add_argument("--domain", choices=["math", "code", "mbpp", "ties", "synthk", "replpilot", "repl", "kstrat", "mace", "holdout"], required=True)
ap.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
ap.add_argument("--n", type=int, default=64)
ap.add_argument("--out", default="runs/bon")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
tag = args.model.replace("/", "__")
out = f"{args.out}/bon_{args.domain}__{tag}.jsonl"

if args.domain == "math":
    tasks = [json.loads(l) for l in open("runs/bon_math_tasks.jsonl")]
    def prompt_of(r):
        return ("Solve the following math problem. Show your reasoning step by step, "
                "then give the final answer in \\boxed{}.\n\n" + r["problem"])
elif args.domain in ("replpilot", "repl", "kstrat", "holdout"):
    fn = {"replpilot": "runs/repl_pilot_tasks.jsonl", "repl": "runs/repl_main_tasks.jsonl",
          "kstrat": "runs/kstrat_tasks.jsonl",
          # added 2026-09-19 for the registration-32 holdout; identical prompt and sampling
          "holdout": "runs/holdout_main_tasks.jsonl"}[args.domain]
    tasks = [json.loads(l) for l in open(fn)]
    def prompt_of(r):
        return ("Answer the following question. Think step by step if needed. You MUST end "
                "your response with the final answer inside \\boxed{...}, with nothing after "
                "it. Example ending: The answer is \\boxed{42}\n\n" + r["problem"])
elif args.domain == "mace":
    tasks = [json.loads(l) for l in open("runs/mace_tasks.jsonl")]
    def prompt_of(r):
        return ("Answer the following question. Give exactly one answer. You MUST end your "
                "response with the answer inside \\boxed{...}, with nothing after it. "
                "Example ending: The answer is \\boxed{Paris}\n\n" + r["problem"])
elif args.domain == "synthk":
    tasks = [json.loads(l) for l in open("runs/bon_synthk_tasks.jsonl")]
    def prompt_of(r):
        return ("Answer the following question. Think briefly if needed, then give your final "
                "answer in \\boxed{}.\n\n" + r["problem"])
elif args.domain == "ties":
    tasks = [json.loads(l) for l in open("runs/bon_ties_tasks.jsonl")]
    def prompt_of(r):
        return ("Answer the following question. Think briefly if needed, then give your final "
                "answer in \\boxed{}.\n\n" + r["problem"])
elif args.domain == "mbpp":
    tasks = [json.loads(l) for l in open("runs/bon_mbpp_tasks.jsonl")]
    def prompt_of(r):
        return (r["prompt"] + "\nYour code should pass this test:\n" + r["example_test"]
                + "\nOutput the complete function in a python code block.")
else:
    tasks = [json.loads(l) for l in open("humaneval.jsonl")]
    def prompt_of(r):
        return ("Complete the following Python function. Output the full function implementation.\n\n"
                + r["prompt"] + "\n")

done = set()
if os.path.exists(out):
    for l in open(out):
        try:
            done.add(json.loads(l)["problem_id"])
        except Exception:
            pass
tasks = [r for r in tasks if (r.get("problem_id") or r.get("task_id")) not in done]
print(f"[bon] {args.domain} {len(tasks)} tasks remaining, n={args.n}", flush=True)
if not tasks:
    print("[bon] nothing to do"); raise SystemExit

from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(args.model)
llm = LLM(model=args.model, dtype="bfloat16", gpu_memory_utilization=0.9, max_model_len=4096)
sp = SamplingParams(n=args.n, max_tokens=1024, temperature=1.0, top_p=0.95, seed=0)

prompts = [tok.apply_chat_template([{"role": "user", "content": prompt_of(r)}],
                                   tokenize=False, add_generation_prompt=True) for r in tasks]
B = 50
mode = "a" if done else "w"
with open(out, mode) as f:
    for i in range(0, len(tasks), B):
        outs = llm.generate(prompts[i:i + B], sp)
        for r, o in zip(tasks[i:i + B], outs):
            pid = r.get("problem_id") or r.get("task_id")
            row = dict(problem_id=pid, model=args.model, samples=[c.text for c in o.outputs])
            if args.domain == "math":
                row.update(answer=r["answer"], level=r["level"], subject=r["subject"])
            elif args.domain in ("ties", "synthk", "replpilot", "repl", "kstrat", "mace"):
                row.update(valid_answers=r["valid_answers"], ref_answer=r["ref_answer"],
                           question=r["problem"], k=r.get("k"), multi_refs=r.get("multi_refs"))
            else:
                row.update(test=r["test"], entry_point=r["entry_point"], question=r["prompt"])
            f.write(json.dumps(row) + "\n")
        f.flush()
        print(f"[bon] {min(i + B, len(tasks))}/{len(tasks)}", flush=True)
print("[bon done]", out, flush=True)
