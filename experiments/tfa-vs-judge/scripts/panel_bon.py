# Best-of-n scoring for one PANEL judge configuration and rubric replicate (Registration 6).
# Committed before any panel score exists. Identical machinery to the registered bon_judge.py
# (expected value over the 0..10 token distribution, replicate a = selection, b = reporting);
# the only difference is that the system instruction comes from the frozen panel spec.
# Output: runs/bon_scores_panel/math__{config_id}_{rep}.jsonl  rows {problem_id, escore:[64]}
# Usage: python panel_bon.py --config p01_phi4_blind --rep a
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
ap.add_argument("--rep", choices=["a", "b"], required=True)
ap.add_argument("--pool", default="runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl")
ap.add_argument("--tasks", default="runs/bon_math_tasks.jsonl")
ap.add_argument("--out", default="runs/bon_scores_panel")
ap.add_argument("--max-model-len", type=int, default=4096)
ap.add_argument("--gpu-util", type=float, default=0.45)
args = ap.parse_args()
cfg = BY_ID[args.config]
if cfg["kind"] == "rm":
    raise SystemExit(f"{args.config} is a reward model: use panel_rm_bon.py")
os.makedirs(args.out, exist_ok=True)
outf = f"{args.out}/math__{args.config}_{args.rep}.jsonl"
if os.path.exists(outf):
    print("[skip]", outf)
    raise SystemExit

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

pool = [json.loads(l) for l in open(args.pool)]
tmap = {}
for l in open(args.tasks):
    t = json.loads(l)
    tmap[t.get("problem_id") or t.get("task_id")] = t
for r in pool:
    r.update({k: v for k, v in tmap.get(r["problem_id"], {}).items() if k not in r})
pool = [r for r in pool if "oracle" in r and 0.2 <= sum(r["oracle"]) / len(r["oracle"]) <= 0.8]
print(f"[panel bon] {args.config} rep {args.rep}: {len(pool)} in-band items x "
      f"{len(pool[0]['samples'])} samples", flush=True)

SYS = system_prompt(cfg, args.rep)
tok = AutoTokenizer.from_pretrained(cfg["judge"], trust_remote_code=True)
CAND = {}
for v in range(11):
    for s in (str(v), " " + str(v)):
        ids = tok.encode(s, add_special_tokens=False)
        if len(ids) == 1:
            CAND.setdefault(ids[0], v)


def build(r, s):
    q = r.get("problem") or r.get("question") or r.get("prompt")
    parts = [f"Problem:\n{q}"]
    if cfg["protocol"] == "ref":
        parts.append(f"Reference solution (trusted):\n{r['solution']}")
    parts.append(f"Candidate solution:\n{s}\n\nScore:")
    body = "\n\n".join(parts)
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

with open(outf, "w") as f:
    B = 25
    for i in range(0, len(pool), B):
        chunk = pool[i:i + B]
        prompts, spans = [], []
        for r in chunk:
            spans.append((len(prompts), len(prompts) + len(r["samples"])))
            prompts += [build(r, s) for s in r["samples"]]
        outs = llm.generate(prompts, sp)
        for r, (a, b) in zip(chunk, spans):
            esc = []
            for o in outs[a:b]:
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
                    esc.append(num / den)
                else:
                    m = re.search(r"\d+", txt)
                    esc.append(min(int(m.group()), 10) if m else 5.0)
            f.write(json.dumps(dict(problem_id=r["problem_id"], escore=esc)) + "\n")
        f.flush()
        print(f"[panel bon] {min(i + B, len(pool))}/{len(pool)}", flush=True)

def _hard_exit():
    """vLLM 0.25.1 on this cluster hangs in engine teardown after generate(). The output file is
    written and flushed by this point, so SIGKILL the engine subprocesses (which would otherwise
    keep the GPU allocated and starve the next cell in the lane) and leave immediately."""
    import os as _os, signal as _sig, subprocess as _sp, time as _t
    def _kids(pid):
        try:
            return [int(x) for x in _sp.run(["pgrep", "-P", str(pid)], capture_output=True,
                                            text=True).stdout.split()]
        except Exception:
            return []
    seen, stack = [], _kids(_os.getpid())
    while stack:
        pid = stack.pop()
        if pid in seen:
            continue
        seen.append(pid)
        stack += _kids(pid)
    for pid in seen:
        try:
            _os.kill(pid, _sig.SIGKILL)
        except Exception:
            pass
    _t.sleep(2)
    _os._exit(0)

print("[panel bon done]", outf, flush=True)
_hard_exit()
