# Generate the separability-continuum candidate pools (mirror of bon_generate.py sampling:
# n=64, temperature 1.0, top_p 0.95, seed 0, max_tokens 1024, bfloat16).
# Part of the registered P-SC suite (see build_sep_tasks.py header).
import argparse
import json
import os

from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="meta-llama/Llama-3.1-8B-Instruct")
ap.add_argument("--n", type=int, default=64)
ap.add_argument("--out", default="runs/bon")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
tag = args.model.replace("/", "__")
out = f"{args.out}/bon_sep__{tag}.jsonl"

tasks = [json.loads(l) for l in open("runs/sep_tasks.jsonl")]
done = set()
if os.path.exists(out):
    for l in open(out):
        try:
            done.add(json.loads(l)["problem_id"])
        except Exception:
            pass
tasks = [r for r in tasks if r["problem_id"] not in done]
print(f"[sep_generate] {len(tasks)} tasks remaining, n={args.n}", flush=True)
if not tasks:
    print("[sep_generate] nothing to do")
    raise SystemExit

tok = AutoTokenizer.from_pretrained(args.model)
llm = LLM(model=args.model, dtype="bfloat16", gpu_memory_utilization=0.9, max_model_len=4096)
sp = SamplingParams(n=args.n, max_tokens=1024, temperature=1.0, top_p=0.95, seed=0)
prompts = [tok.apply_chat_template([{"role": "user", "content": r["problem"]}],
                                   tokenize=False, add_generation_prompt=True) for r in tasks]
B = 50
mode = "a" if done else "w"
with open(out, mode) as f:
    for i in range(0, len(tasks), B):
        outs = llm.generate(prompts[i:i + B], sp)
        for r, o in zip(tasks[i:i + B], outs):
            f.write(json.dumps(dict(
                problem_id=r["problem_id"], model=args.model, stratum=r["stratum"],
                inst=r["inst"], question=r["problem"], ref_answer=r["ref_answer"],
                ref_canon=r["ref_canon"], params=r["params"],
                base_solutions=r["base_solutions"],
                samples=[c.text for c in o.outputs])) + "\n")
        print(f"[sep_generate] {i + B}/{len(tasks)}", flush=True)
print("[sep_generate] done")
