# Audit the sabotaged ladder judges (7B, 14B): score the 242 labeling-instrument traces with
# the sabotage rubric (presentation-first), so the two never-audited pressure configurations
# get audit verdicts. Registered prediction (pre-run): both are convicted (style partial > +0.30).
# Output: runs/cert_out/sabotage_<model>.jsonl rows {task_id, score}.
import argparse, json

from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bon_rubrics import RUBRIC

ap = argparse.ArgumentParser()
ap.add_argument("--judge", required=True)
args = ap.parse_args()
SYS = RUBRIC[("sabotage", "a")]

rows = [json.loads(l) for l in open("human_eval/traces_to_label.jsonl")]
tok = AutoTokenizer.from_pretrained(args.judge)
llm = LLM(model=args.judge, dtype="bfloat16", gpu_memory_utilization=0.9, max_model_len=4096)
sp = SamplingParams(max_tokens=4, temperature=0.0)

prompts = [tok.apply_chat_template(
    [{"role": "system", "content": SYS},
     {"role": "user", "content": f"Problem:\n{r['question']}\n\nCandidate solution:\n{r['trace'][:12000]}\n\nScore:"}],
    tokenize=False, add_generation_prompt=True) for r in rows]
outs = llm.generate(prompts, sp)
tag = args.judge.replace("/", "_")
import re
with open(f"runs/cert_out/sabotage_{tag}.jsonl", "w") as f:
    for r, o in zip(rows, outs):
        m = re.search(r"\d+", o.outputs[0].text or "")
        s = min(int(m.group()), 10) if m else None
        f.write(json.dumps(dict(task_id=r["id"], score=s)) + "\n")
print("[sab audit done]", tag, flush=True)
