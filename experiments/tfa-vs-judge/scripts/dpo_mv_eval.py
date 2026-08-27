# Evaluation for the multi-valid DPO experiment (see dpo_mv_pairs.py for the registered
# predictions). Samples n=8 per item from base / ref-arm / m1-arm policies on the k>1
# k-stratified TRAIN items and the 120 replication-pool HELD-OUT items, writing pools in
# the bon_judge-compatible format so the frozen judges can score them, split by task file
# so repl_oracle.py joins params cleanly.
import argparse
import json
import os

ap = argparse.ArgumentParser()
ap.add_argument("--policy", choices=["base", "ref", "m1"], required=True)
ap.add_argument("--model", default="meta-llama/Llama-3.1-8B-Instruct")
ap.add_argument("--n", type=int, default=8)
ap.add_argument("--out", default="runs/dpo_mv")
args = ap.parse_args()

from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest
from transformers import AutoTokenizer

train_items = [json.loads(l) for l in open("runs/kstrat_tasks.jsonl")]
train_items = [t for t in train_items if t.get("k", 0) > 1]
held_items = [json.loads(l) for l in open("runs/repl_main_tasks.jsonl")]

PROMPT = ("Answer the following question. Think step by step if needed. You MUST end "
          "your response with the final answer inside \\boxed{...}, with nothing after "
          "it. Example ending: The answer is \\boxed{42}\n\n")
tok = AutoTokenizer.from_pretrained(args.model)
lora = None
if args.policy != "base":
    lora = LoRARequest(args.policy, 1, f"{args.out}/adapter_{args.policy}")
llm = LLM(model=args.model, dtype="bfloat16", gpu_memory_utilization=0.9,
          max_model_len=4096, enable_lora=lora is not None, max_lora_rank=16)
sp = SamplingParams(n=args.n, max_tokens=1024, temperature=1.0, top_p=0.95, seed=0)

for split, items in (("train", train_items), ("heldout", held_items)):
    out = f"{args.out}/eval_{args.policy}_{split}.jsonl"
    if os.path.exists(out):
        print("[skip]", out)
        continue
    prompts = [tok.apply_chat_template(
        [{"role": "user", "content": PROMPT + t["problem"]}],
        tokenize=False, add_generation_prompt=True) for t in items]
    outs = llm.generate(prompts, sp, lora_request=lora) if lora else llm.generate(prompts, sp)
    with open(out, "w") as f:
        for t, o in zip(items, outs):
            f.write(json.dumps(dict(
                problem_id=t["problem_id"], question=t["problem"], problem=t["problem"],
                params=t["params"], ref_answer=t["ref_answer"],
                valid_answers=t.get("valid_answers"), k=t.get("k"),
                samples=[c.text for c in o.outputs])) + "\n")
    print("[dpo_mv_eval]", out, len(items), "items")
