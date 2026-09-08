# Reward-model panel cells (Registration 6): audit on the 242 anchor traces and best-of-n
# scoring on the math pool, for the two trained reward models in the frozen panel.
# Committed before any panel score exists. Mirrors the published rm_score.py (sequence-
# classification head, single scoring function for selection and reporting, which the
# within-stratum permutation null carries the same winner's-curse bias for).
# Outputs:
#   --mode audit : runs/panel_cert/{config_id}.jsonl          rows {task_id, score}
#   --mode bon   : runs/bon_scores_panel/math__{id}_{a,b}.jsonl rows {problem_id, escore:[64]}
#                  (the a and b files are identical by construction and the analysis discloses it)
# Usage: python panel_rm.py --config p17_rm_skywork_v2 --mode audit
import argparse
import json
import os
import sys

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from panel_specs import BY_ID

ap = argparse.ArgumentParser()
ap.add_argument("--config", required=True)
ap.add_argument("--mode", choices=["audit", "bon"], required=True)
ap.add_argument("--traces", default="human_eval/traces_to_label.jsonl")
ap.add_argument("--pool", default="runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl")
ap.add_argument("--tasks", default="runs/bon_math_tasks.jsonl")
ap.add_argument("--bs", type=int, default=8)
args = ap.parse_args()
cfg = BY_ID[args.config]
assert cfg["kind"] == "rm", f"{args.config} is not a reward model cell"

tok = AutoTokenizer.from_pretrained(cfg["judge"], trust_remote_code=True)
if tok.pad_token is None:  # e.g. Tulu-3 RM ships no pad token; batched scoring needs one
    tok.pad_token = tok.eos_token or tok.unk_token
model = AutoModelForSequenceClassification.from_pretrained(
    cfg["judge"], torch_dtype=torch.bfloat16, num_labels=1, trust_remote_code=True).to("cuda")
if model.config.pad_token_id is None:
    model.config.pad_token_id = tok.pad_token_id
model.eval()


@torch.no_grad()
def score_batch(convs):
    texts = [tok.apply_chat_template(c, tokenize=False) for c in convs]
    enc = tok(texts, return_tensors="pt", padding=True, truncation=True, max_length=4096).to("cuda")
    return model(**enc).logits[:, 0].float().cpu().tolist()


def batched(convs):
    out = []
    for i in range(0, len(convs), args.bs):
        out += score_batch(convs[i:i + args.bs])
    return out


if args.mode == "audit":
    os.makedirs("runs/panel_cert", exist_ok=True)
    outf = f"runs/panel_cert/{args.config}.jsonl"
    if os.path.exists(outf):
        print("[skip]", outf)
        raise SystemExit
    rows = [json.loads(l) for l in open(args.traces)]
    scores = batched([[{"role": "user", "content": r["question"]},
                       {"role": "assistant", "content": r["trace"]}] for r in rows])
    with open(outf, "w") as f:
        for r, s in zip(rows, scores):
            f.write(json.dumps(dict(task_id=r["id"], score=s)) + "\n")
    print("[panel rm audit done]", outf, flush=True)
else:
    os.makedirs("runs/bon_scores_panel", exist_ok=True)
    outf = f"runs/bon_scores_panel/math__{args.config}_a.jsonl"
    if os.path.exists(outf):
        print("[skip]", outf)
        raise SystemExit
    pool = [json.loads(l) for l in open(args.pool)]
    tmap = {}
    for l in open(args.tasks):
        t = json.loads(l)
        tmap[t.get("problem_id") or t.get("task_id")] = t
    for r in pool:
        r.update({k: v for k, v in tmap.get(r["problem_id"], {}).items() if k not in r})
    pool = [r for r in pool if "oracle" in r and 0.2 <= sum(r["oracle"]) / len(r["oracle"]) <= 0.8]
    print(f"[panel rm bon] {args.config}: {len(pool)} in-band items", flush=True)
    with open(outf, "w") as f:
        for j, r in enumerate(pool):
            q = r.get("problem") or r.get("question") or r.get("prompt")
            scores = batched([[{"role": "user", "content": q},
                               {"role": "assistant", "content": s}] for s in r["samples"]])
            f.write(json.dumps(dict(problem_id=r["problem_id"], escore=scores)) + "\n")
            f.flush()
            print(f"[panel rm bon] item {j + 1}/{len(pool)}", flush=True)
    # replicate b is the same scoring function; bon_analysis.py requires both files
    import shutil
    shutil.copyfile(outf, outf.replace("_a.jsonl", "_b.jsonl"))
    print("[panel rm bon done]", outf, flush=True)
