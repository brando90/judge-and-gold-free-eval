# R3-A / R3-C judge harness (papers/D-iclr/registration_round3.md). Same prompt and sampling as the
# R2-B REASON protocol (r2_judge.py), with thinking switchable and an extra MACE subsample pool.
#   --thinking on  : enable_thinking=True  (identical to R2-B REASON)
#   --thinking off : enable_thinking=False (same weights, prompt, sampling)
# Output rows: {problem_id, idx, score (float or null), n_tokens, tail (last 400 chars)}.
import argparse, json, os, re, sys
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument("--pool", choices=["rot", "ksub", "macesub"], required=True)
ap.add_argument("--cond", choices=["noref", "ref", "refrot"], required=True)
ap.add_argument("--thinking", choices=["on", "off"], required=True)
ap.add_argument("--judge", default="Qwen/Qwen3-8B")
ap.add_argument("--out", default="runs/r3/scores")
ap.add_argument("--gpu-util", type=float, default=0.45)
ap.add_argument("--max-model-len", type=int, default=8192)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
tag = args.judge.replace("/", "__")
out = f"{args.out}/{args.pool}__think{args.thinking}__{tag}__{args.cond}.jsonl"
if os.path.exists(out):
    print("[skip]", out); raise SystemExit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bon_rubrics import RUBRIC_TIES

src = {"rot": "runs/r2/rot_sub.jsonl", "ksub": "runs/r2/ksub.jsonl", "macesub": "runs/r3/macesub.jsonl"}[args.pool]
pool = [json.loads(l) for l in open(src)]
tok = AutoTokenizer.from_pretrained(args.judge)
TAIL = ("Think it through, then end your reply with a final line of the form 'Score: N', "
        "where N is an integer from 0 to 10.")


def build(r, s):
    key = "noref" if args.cond == "noref" else "ref"
    sysmsg = re.sub(r"\s*Respond with only the integer score\.\s*$", "", RUBRIC_TIES[(key, "a")]) + " " + TAIL
    parts = [f"Problem:\n{r['question']}"]
    if args.cond != "noref":
        parts.append(f"Reference answer (trusted):\n{r['ref_rot'] if args.cond == 'refrot' else r['ref_orig']}")
    parts.append(f"Candidate solution:\n{s}")
    msgs = [{"role": "system", "content": sysmsg}, {"role": "user", "content": "\n\n".join(parts)}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                   enable_thinking=(args.thinking == "on"))


def parse(text):
    body = text.split("</think>")[-1]
    m = re.findall(r"Score:\s*\**\s*(\d+(?:\.\d+)?)", body)
    if not m:
        return None
    v = float(m[-1])
    return v if 0 <= v <= 10 else None


sp = SamplingParams(max_tokens=4096, temperature=0.6, top_p=0.95, top_k=20, seed=0)
llm = LLM(model=args.judge, dtype="bfloat16", gpu_memory_utilization=args.gpu_util,
          max_model_len=args.max_model_len, seed=0)
prompts, meta = [], []
for r in pool:
    for j, s in enumerate(r["samples"]):
        prompts.append(build(r, s)); meta.append((r["problem_id"], r["idx"][j]))
print(f"[r3 {args.pool}/{args.cond}/think-{args.thinking}] {len(prompts)} prompts", flush=True)
rows, n_bad = {}, 0
for i in range(0, len(prompts), 512):
    for (pid, idx), o in zip(meta[i:i + 512], llm.generate(prompts[i:i + 512], sp)):
        text = o.outputs[0].text or ""
        v = parse(text)
        n_bad += v is None
        rows.setdefault(pid, []).append(dict(idx=idx, score=v, n_tokens=len(o.outputs[0].token_ids), tail=text[-400:]))
    print(f"  {min(i + 512, len(prompts))}/{len(prompts)} unparseable {n_bad}", flush=True)
with open(out + ".part", "w") as f:
    for pid, lst in rows.items():
        f.write(json.dumps(dict(problem_id=pid, idx=[x["idx"] for x in lst], score=[x["score"] for x in lst],
                                n_tokens=[x["n_tokens"] for x in lst], tail=[x["tail"] for x in lst])) + "\n")
os.replace(out + ".part", out)
print(f"[r3 done] {out} unparseable={n_bad}/{len(prompts)}", flush=True)
import psutil
for _c in psutil.Process().children(recursive=True):
    try:
        _c.kill()
    except Exception:
        pass
os._exit(0)
