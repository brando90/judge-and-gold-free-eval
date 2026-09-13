# Round-8 secondary labeling (post hoc): a model reads each UNBOXED reply in the constructed pools and writes the final
# answer it commits to, or NONE. The producer (papers/analysis/r8_lenient_labels_model.py) checks that answer with the
# task's constraint. Candidate text only; no judge scores are read. Run from experiments/tfa-vs-judge on a GPU host.
import argparse
import json
import os

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Qwen/Qwen2.5-14B-Instruct")
ap.add_argument("--gpu-util", type=float, default=0.4)
args = ap.parse_args()
POOLS = {"repl": "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl",
         "kpool": "runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl"}
os.makedirs("runs/r8", exist_ok=True)
SYSTEM = "You read a reply to a question and report the final answer the reply commits to. You do not solve the question."
USER = ("Question:\n{q}\n\nReply:\n{r}\n\n"
        "What final answer does the reply commit to? If it commits to one answer, write only that answer: a number, or "
        "numbers separated by commas. If it gives no final answer, or ends with several different answers, write NONE.")

tok = AutoTokenizer.from_pretrained(args.model)
llm = LLM(args.model, gpu_memory_utilization=args.gpu_util, max_model_len=6144, enable_prefix_caching=True)
sp = SamplingParams(temperature=0.0, max_tokens=40)
for name, f in POOLS.items():
    out = f"runs/r8/extract_{name}__{args.model.split('/')[-1]}.jsonl"
    if os.path.exists(out):
        print("[skip]", out)
        continue
    jobs, prompts = [], []
    for t in (json.loads(l) for l in open(f)):
        for i, s in enumerate(t["samples"]):
            if "\\boxed{" in s:
                continue
            msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": USER.format(q=t["question"], r=s)}]
            prompts.append(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True))
            jobs.append((t["problem_id"], i))
    print(f"[r8 extract] {name}: {len(prompts)} unboxed replies", flush=True)
    res = llm.generate(prompts, sp)
    with open(out + ".tmp", "w") as g:
        for (pid, i), r in zip(jobs, res):
            g.write(json.dumps(dict(problem_id=pid, idx=i, answer=r.outputs[0].text.strip())) + "\n")
    os.replace(out + ".tmp", out)
    print("[r8 extract done]", out, flush=True)
