# Judge-score a BoN pool with an open-weights judge. Pre-registered machinery (plan v2):
#  - escore = logprob-expected value over score tokens 0..10 at the first generated position
#    (renormalized over captured mass; falls back to the parsed integer if mass < 0.25)
#  - two replicates = two rubric paraphrases (A/B), same construct, different wording;
#    selection uses A, reporting uses B (winner's-curse cancellation)
#  - conditions: noref / ref (gold solution in context) / sabotage (presentation-first control)
# Output: runs/bon_scores/{domain}__{judge}__{cond}_{rep}.jsonl  rows: problem_id, escore(list)
import argparse, json, math, os, re

from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument("--pool", required=True)
ap.add_argument("--judge", required=True)
ap.add_argument("--cond", choices=["noref", "ref", "sabotage", "refinst", "refinst2", "multiref"], required=True)
ap.add_argument("--rep", choices=["a", "b"], required=True)
ap.add_argument("--domain", choices=["math", "code", "ties", "synthk", "simcorr"], default="math")
ap.add_argument("--filter-band", action="store_true", help="only items with pool pass in [0.2,0.8]")
ap.add_argument("--tasks", default=None, help="task file with problem text to join by problem_id")
ap.add_argument("--out", default="runs/bon_scores")
ap.add_argument("--max-model-len", type=int, default=4096,
                help="raise for code ref runs: test suite + candidate can exceed 4096")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
tag = args.judge.replace("/", "__")
out = f"{args.out}/{args.domain}__{tag}__{args.cond}_{args.rep}.jsonl"
if os.path.exists(out):
    print("[skip]", out); raise SystemExit

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bon_rubrics import RUBRIC, RUBRIC_CODE, RUBRIC_TIES

pool = [json.loads(l) for l in open(args.pool)]
if args.tasks:
    tmap = {}
    for l in open(args.tasks):
        t = json.loads(l)
        tmap[t.get("problem_id") or t.get("task_id")] = t
    for r in pool:
        r.update({k: v for k, v in tmap.get(r["problem_id"], {}).items() if k not in r})
missing = sum(1 for r in pool if not (r.get("problem") or r.get("question") or r.get("prompt")))
if missing:
    raise SystemExit(f"{missing} pool rows lack problem text; pass --tasks")
if args.filter_band:
    pool = [r for r in pool if "oracle" in r and 0.2 <= sum(r["oracle"]) / len(r["oracle"]) <= 0.8]
print(f"[judge] {len(pool)} items x {len(pool[0]['samples'])} samples, {args.cond}_{args.rep}",
      flush=True)

tok = AutoTokenizer.from_pretrained(args.judge)
CAND = {}
for v in range(11):
    for s in (str(v), " " + str(v)):
        ids = tok.encode(s, add_special_tokens=False)
        if len(ids) == 1:
            CAND.setdefault(ids[0], v)

def build(r, s):
    cond_key = "ref" if args.cond in ("refinst", "refinst2", "multiref") else args.cond
    sys = {"code": RUBRIC_CODE, "ties": RUBRIC_TIES, "synthk": RUBRIC_TIES,
           "simcorr": RUBRIC_TIES}.get(args.domain, RUBRIC)[(cond_key, args.rep)]
    if args.cond == "refinst":
        sys += (" Note: the reference shown is one valid answer among possibly many; the "
                "question may have several correct answers, and any correct answer deserves "
                "full credit even if it differs from the reference.")
    if args.cond == "refinst2":
        sys += (" Important: do not compare the candidate's answer to the reference. "
                "Use the reference only to understand the problem. Verify the candidate's "
                "answer on its own merits; a correct answer that differs from the reference "
                "must receive the same score as one that matches it.")
    q = r.get("problem") or r.get("question") or r.get("prompt")
    parts = [f"Problem:\n{q}"]
    if args.cond == "multiref":
        parts.append("Reference answers (trusted; a sample of the valid answers):\n"
                     + "\n".join(r["multi_refs"]))
    if args.cond in ("refinst", "refinst2"):
        parts.append(f"Reference answer (trusted):\n{r['ref_answer']}")
    if args.cond == "ref":
        # code reference = the canonical assert set (example_test), NOT the full MBPP+/EvalPlus
        # oracle suite: that suite runs to ~46k tokens and stays held out, mirroring math's
        # human reference solution vs oracle answer check.
        # ties reference = ONE valid answer (fixed at task build), the anchoring manipulation.
        if args.domain == "math":
            parts.append(f"Reference solution (trusted):\n{r['solution']}")
        elif args.domain in ("ties", "synthk"):
            parts.append(f"Reference answer (trusted):\n{r['ref_answer']}")
        else:
            parts.append(f"Trusted reference tests (the candidate must pass these):\n{r['example_test']}")
    parts.append(f"Candidate solution:\n{s}\n\nScore:")
    try:
        return tok.apply_chat_template([{"role": "system", "content": sys},
                                        {"role": "user", "content": "\n\n".join(parts)}],
                                       tokenize=False, add_generation_prompt=True)
    except Exception:
        # some templates (gemma-2) reject the system role; fold it into the user turn
        return tok.apply_chat_template([{"role": "user", "content": sys + "\n\n" + "\n\n".join(parts)}],
                                       tokenize=False, add_generation_prompt=True)

llm = LLM(model=args.judge, dtype="bfloat16", gpu_memory_utilization=args.gpu_util,
          max_model_len=args.max_model_len)
sp = SamplingParams(max_tokens=4, temperature=0.0, logprobs=20)

with open(out, "w") as f:
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
                # digit-tokenizing models emit "10" as "1","0": resolve the "1" token's meaning
                # from the actually-generated continuation
                one_means = 10 if txt.startswith("10") else 1
                num = den = 0.0
                for tid, info in lp.items():
                    if tid in CAND:
                        v = one_means if CAND[tid] == 1 else CAND[tid]
                        p = math.exp(info.logprob)
                        num += p * v; den += p
                if den >= 0.25:
                    esc.append(num / den)
                else:
                    m = re.search(r"\d+", o.outputs[0].text)
                    esc.append(min(int(m.group()), 10) if m else 5.0)
            f.write(json.dumps(dict(problem_id=r["problem_id"], escore=esc)) + "\n")
        f.flush()
        print(f"[judge] {min(i + B, len(pool))}/{len(pool)}", flush=True)
print("[judge done]", out, flush=True)
