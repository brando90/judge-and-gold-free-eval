# Score items with a trained reward model (Skywork-Reward-Llama-3.1-8B-v0.2), the trained-RM
# baseline for the certificate paper. Registered predictions (committed pre-run): (1) on the
# audit, the RM shows a positive soundness partial (it passes weakly or marginally); (2) under
# BoN-64 pressure its behavior matches its audit verdict. Single scoring function: selection and
# reporting share scores, which the within-stratum permutation null also does, so the excess-gap
# estimand remains comparable (the null carries the same winner's-curse bias as the observation).
#
# Modes:
#   --traces human_eval/traces_to_label.jsonl --out runs/rm_scores_traces.jsonl
#       rows: id, rm_score        (question + trace)
#   --pool runs/bon/bon_math__... --tasks runs/bon_math_tasks.jsonl --out runs/rm_scores_math.jsonl
#       rows: problem_id, rm_score (list, one per sample)
import argparse, json

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Skywork/Skywork-Reward-Llama-3.1-8B-v0.2")
ap.add_argument("--traces", default=None)
ap.add_argument("--pool", default=None)
ap.add_argument("--tasks", default=None)
ap.add_argument("--filter-band", action="store_true")
ap.add_argument("--out", required=True)
ap.add_argument("--bs", type=int, default=8)
args = ap.parse_args()

tok = AutoTokenizer.from_pretrained(args.model)
model = AutoModelForSequenceClassification.from_pretrained(
    args.model, torch_dtype=torch.bfloat16, device_map="cuda", num_labels=1)
model.eval()


@torch.no_grad()
def score_batch(convs):
    texts = [tok.apply_chat_template(c, tokenize=False) for c in convs]
    enc = tok(texts, return_tensors="pt", padding=True, truncation=True,
              max_length=4096).to("cuda")
    return model(**enc).logits[:, 0].float().cpu().tolist()


def batched(pairs):
    out = []
    for i in range(0, len(pairs), args.bs):
        out += score_batch(pairs[i:i + args.bs])
        if (i // args.bs) % 20 == 0:
            print(f"[rm] {i}/{len(pairs)}", flush=True)
    return out


if args.traces:
    rows = [json.loads(l) for l in open(args.traces)]
    convs = [[{"role": "user", "content": r["question"]},
              {"role": "assistant", "content": r["trace"]}] for r in rows]
    scores = batched(convs)
    with open(args.out, "w") as f:
        for r, s in zip(rows, scores):
            f.write(json.dumps(dict(id=r["id"], rm_score=s)) + "\n")
else:
    pool = [json.loads(l) for l in open(args.pool)]
    if args.tasks:
        tmap = {}
        for l in open(args.tasks):
            t = json.loads(l)
            tmap[t.get("problem_id") or t.get("task_id")] = t
        for r in pool:
            r.update({k: v for k, v in tmap.get(r["problem_id"], {}).items() if k not in r})
    if args.filter_band:
        pool = [r for r in pool if "oracle" in r and
                0.2 <= sum(r["oracle"]) / len(r["oracle"]) <= 0.8]
    with open(args.out, "w") as f:
        for j, r in enumerate(pool):
            q = r.get("problem") or r.get("question") or r.get("prompt")
            convs = [[{"role": "user", "content": q},
                      {"role": "assistant", "content": s}] for s in r["samples"]]
            scores = batched(convs)
            f.write(json.dumps(dict(problem_id=r["problem_id"], rm_score=scores)) + "\n")
            f.flush()
            print(f"[rm] item {j + 1}/{len(pool)}", flush=True)
print("[rm done]", args.out, flush=True)
