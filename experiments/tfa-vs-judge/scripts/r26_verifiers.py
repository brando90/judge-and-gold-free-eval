# R26 (papers/D-iclr-v2/registration_round26.md): open RL-reward verifiers, run locally (Apple MPS, float16, greedy), on the benchmark
# pool with one reference or the full answer list as the gold answer. Resumable. Run from experiments/tfa-vs-judge.
#   --verifier general : TIGER-Lab/general-verifier with General-Reasoner's VERIFIER_PROMPT_TEMPLATE (raw string, no chat template, as in
#                        General-Reasoner verifier.py); reward = "Final Decision: Yes" in the output (official rule); max_new_tokens 512.
#   --verifier compass : opencompass/CompassVerifier-3B with CV_PROMPT through the tokenizer's chat template (as in its model card);
#                        grade = first A/B/C in the output (A correct; B, C incorrect; none = missing); max_new_tokens 32.
# Templates are read verbatim from the survey's pinned copies (papers/D-iclr-v2/survey/prompts/). Score 10 = correct, 0 = incorrect.
import argparse
import ast
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROMPTS = os.path.join(HERE, "../../../papers/D-iclr-v2/survey/prompts")
ap = argparse.ArgumentParser()
ap.add_argument("--verifier", choices=("general", "compass"), required=True)
ap.add_argument("--conds", default="ref,reflist")
ap.add_argument("--pool", default="runs/r20/mace_gen/pool.jsonl")
ap.add_argument("--tasks", default="runs/mace_tasks.jsonl")
ap.add_argument("--out", required=True)
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()


def template(fname, name):
    code = open(os.path.join(PROMPTS, fname)).read().split("# ---- verbatim template below ----\n", 1)[1]
    for node in ast.parse(code).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit(name)


GENERAL = template("general_verifier.txt", "VERIFIER_PROMPT_TEMPLATE")
COMPASS = template("compassverifier_prompts.txt", "CV_PROMPT")
TASKS = {json.loads(l)["problem_id"]: json.loads(l) for l in open(args.tasks)}
pool = [json.loads(l) for l in open(args.pool)]


def gold(t, cond):
    if cond == "ref":
        return t["ref"]
    return "Any one of the following is a complete correct answer: " + "; ".join(sorted(TASKS[t["problem_id"]]["valid_answers"]))


def build(t, j, cond):
    if args.verifier == "general":
        return GENERAL.format(question=t["question"], ground_truth=gold(t, cond), student_answer=t["samples"][j])
    return COMPASS.format(question=t["question"], gold_answer=gold(t, cond), llm_response=t["samples"][j])


conds = args.conds.split(",")
if args.dry_run:
    for c in conds:
        print(f"===== {args.verifier} / {c} =====\n{build(pool[0], 0, c)}\n")
    sys.exit(0)

import torch  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

name = {"general": "TIGER-Lab/general-verifier", "compass": "opencompass/CompassVerifier-3B"}[args.verifier]
tok = AutoTokenizer.from_pretrained(name)
model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float16).to("mps").eval()
max_new = 512 if args.verifier == "general" else 32

outf = os.path.abspath(args.out)
os.makedirs(os.path.dirname(outf), exist_ok=True)
done = set()
if os.path.exists(outf):
    for l in open(outf):
        r = json.loads(l)
        done.add((r["problem_id"], r["idx"], r["cond"]))
jobs = [(t, j, c) for t in pool for j in range(len(t["samples"])) for c in conds if (t["problem_id"], t["idx"][j], c) not in done]
print(f"[r26 verifier {name}] {len(jobs)} generations", flush=True)
t0 = time.time()
with open(outf, "a") as f:
    for i, (t, j, c) in enumerate(jobs):
        text_in = build(t, j, c)
        if args.verifier == "compass":
            text_in = tok.apply_chat_template([{"role": "user", "content": text_in}], tokenize=False, add_generation_prompt=True)
        enc = tok(text_in, return_tensors="pt").to("mps")
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=max_new, do_sample=False, pad_token_id=tok.eos_token_id)
        gen = tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)
        if args.verifier == "general":
            score = 10.0 if "Final Decision: Yes" in gen else 0.0
            parsed = ("Final Decision: Yes" in gen) or ("Final Decision: No" in gen)
        else:
            m = re.search(r"\\boxed\{([ABC])\}", gen) or re.search(r"\b([ABC])\b", gen)
            score = None if not m else (10.0 if m.group(1) == "A" else 0.0)
            parsed = m is not None
        f.write(json.dumps(dict(problem_id=t["problem_id"], idx=t["idx"][j], cond=c, verifier=name, score=score, parsed=parsed,
                                new_tokens=int(out.shape[1] - enc["input_ids"].shape[1]), tail=gen[-300:])) + "\n")
        f.flush()
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(jobs)} {(time.time() - t0) / (i + 1):.1f}s per generation", flush=True)
print(f"[r26 verifier done] {outf}", flush=True)
