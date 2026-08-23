# Evaluation for the DPO gating experiment: sample from base and both DPO'd policies on
# (a) the 105 in-band training items and (b) held-out MATH items never in any BoN pool,
# score true accuracy with the oracle, and dump generations for frozen-judge scoring
# (both GPT-5.2 rubrics, honest ref and sabotage) by dpo_judge_gpt.py.
# vllm supports LoRA adapters at inference via --enable-lora.
import argparse, json, os, re

ap = argparse.ArgumentParser()
ap.add_argument("--policy", choices=["base", "ref", "sabotage"], required=True)
ap.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
ap.add_argument("--n", type=int, default=8)
ap.add_argument("--out", default="runs/dpo")
args = ap.parse_args()
out = f"{args.out}/eval_{args.policy}.jsonl"
if os.path.exists(out):
    print("[skip]", out); raise SystemExit

from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest
from transformers import AutoTokenizer

# item split: train = the in-band pool items; heldout = next 100 unseen MATH tasks
pool_pids = set()
for l in open("runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl"):
    r = json.loads(l)
    if 0.2 <= sum(r["oracle"]) / len(r["oracle"]) <= 0.8:
        pool_pids.add(r["problem_id"])
tasks = [json.loads(l) for l in open("runs/bon_math_tasks.jsonl")]
train_items = [t for t in tasks if t["problem_id"] in pool_pids]
unseen = [t for t in tasks if t["problem_id"] not in pool_pids][:100]
print(f"[dpo_eval] {args.policy}: {len(train_items)} train items, {len(unseen)} held-out")

PROMPT = ("Solve the following math problem. Show your reasoning step by step, "
          "then give the final answer in \\boxed{}.\n\n")
tok = AutoTokenizer.from_pretrained(args.model)
lora = None
if args.policy != "base":
    lora = LoRARequest(args.policy, 1, f"{args.out}/adapter_{args.policy}")
llm = LLM(model=args.model, dtype="bfloat16", gpu_memory_utilization=0.9,
          max_model_len=4096, enable_lora=lora is not None, max_lora_rank=16)
sp = SamplingParams(n=args.n, max_tokens=1024, temperature=1.0, top_p=0.95, seed=0)


def extract_boxed(text):
    i = text.rfind("\\boxed{")
    if i < 0:
        return None
    j, depth = i + 7, 1
    while j < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    return text[i + 7:j - 1]


def norm(a):
    if a is None:
        return None
    a = a.strip().strip("$ ").replace("\\!", "").replace("\\,", "").replace(" ", "")
    a = re.sub(r"\\text\{([^}]*)\}", r"\1", a)
    a = re.sub(r"\\dfrac", r"\\frac", a)
    return a.rstrip(".")


with open(out, "w") as f:
    for split, items in (("train", train_items), ("heldout", unseen)):
        B = 50
        for i in range(0, len(items), B):
            chunk = items[i:i + B]
            prompts = [tok.apply_chat_template(
                [{"role": "user", "content": PROMPT + t["problem"]}],
                tokenize=False, add_generation_prompt=True) for t in chunk]
            outs = llm.generate(prompts, sp, lora_request=lora)
            for t, o in zip(chunk, outs):
                gold = norm(t["answer"])
                samples = [c.text for c in o.outputs]
                oracle = [int(norm(extract_boxed(s)) == gold and gold is not None)
                          for s in samples]
                f.write(json.dumps(dict(problem_id=t["problem_id"], split=split,
                                        policy=args.policy, samples=samples,
                                        oracle=oracle)) + "\n")
            f.flush()
            print(f"[dpo_eval] {split} {min(i + B, len(items))}/{len(items)}", flush=True)
print("[dpo_eval done]", out)
