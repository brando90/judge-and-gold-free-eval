# Audit one PANEL judge configuration on the 242 anchor traces (Registration 6).
# Committed before any panel score exists. Same anchor file and the same expected-value scoring
# machinery as bon_judge.py, so panel partials are comparable to the published ones.
# Output: runs/panel_cert/{config_id}.jsonl  rows {task_id, score}
# Usage (from the flat working dir):  python panel_audit.py --config p01_phi4_blind
import argparse
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from panel_specs import BY_ID, system_prompt

ap = argparse.ArgumentParser()
ap.add_argument("--config", required=True)
ap.add_argument("--traces", default="human_eval/traces_to_label.jsonl")
ap.add_argument("--out", default="runs/panel_cert")
ap.add_argument("--max-model-len", type=int, default=8192)
ap.add_argument("--gpu-util", type=float, default=0.90)
args = ap.parse_args()
cfg = BY_ID[args.config]
if cfg["kind"] == "rm":
    raise SystemExit(f"{args.config} is a reward model: use panel_rm_audit.py")
os.makedirs(args.out, exist_ok=True)
outf = f"{args.out}/{args.config}.jsonl"
if os.path.exists(outf):
    print("[skip]", outf)
    raise SystemExit

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

rows = [json.loads(l) for l in open(args.traces)]
SYS = system_prompt(cfg, "a")
tok = AutoTokenizer.from_pretrained(cfg["judge"], trust_remote_code=True)
CAND = {}
for v in range(11):
    for s in (str(v), " " + str(v)):
        ids = tok.encode(s, add_special_tokens=False)
        if len(ids) == 1:
            CAND.setdefault(ids[0], v)


def build(r):
    parts = [f"Problem:\n{r['question']}"]
    if cfg["protocol"] == "ref":
        parts.append(f"Reference solution (trusted):\n{r['gold_solution'][:6000]}")
    parts.append(f"Candidate solution:\n{r['trace'][:12000]}\n\nScore:")
    body = "\n\n".join(parts)
    # some templates reject a system role (gemma-2 style) and some take enable_thinking (Qwen3);
    # try system+user first, then fold the system message into the user turn
    for msgs in ([{"role": "system", "content": SYS}, {"role": "user", "content": body}],
                 [{"role": "user", "content": SYS + "\n\n" + body}]):
        for kw in ({"enable_thinking": False}, {}):
            try:
                return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **kw)
            except Exception:
                continue
    raise SystemExit(f"no usable chat template for {cfg['judge']}")


llm = LLM(model=cfg["judge"], dtype="bfloat16", gpu_memory_utilization=args.gpu_util,
          max_model_len=args.max_model_len, trust_remote_code=True)
sp = SamplingParams(max_tokens=4, temperature=0.0, logprobs=20)
outs = llm.generate([build(r) for r in rows], sp)
with open(outf, "w") as f:
    for r, o in zip(rows, outs):
        lp = o.outputs[0].logprobs[0] if o.outputs[0].logprobs else {}
        txt = (o.outputs[0].text or "").strip()
        one_means = 10 if txt.startswith("10") else 1
        num = den = 0.0
        for tid, info in lp.items():
            if tid in CAND:
                v = one_means if CAND[tid] == 1 else CAND[tid]
                p = math.exp(info.logprob)
                num += p * v
                den += p
        if den >= 0.25:
            score = num / den
        else:
            m = re.search(r"\d+", txt)
            score = float(min(int(m.group()), 10)) if m else None
        f.write(json.dumps(dict(task_id=r["id"], score=score)) + "\n")
print("[panel audit done]", outf, flush=True)
