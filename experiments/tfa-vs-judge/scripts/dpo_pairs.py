# DPO gating experiment for the certificate paper (registered pre-run; predictions below
# committed before any training). Builds preference pairs from the EXISTING judge-scored
# BoN pools, one arm per judge:
#   certified arm: GPT-5.2 honest referenced judge (math__gpt-5.2__ref_a escores)
#   convicted arm: GPT-5.2 sabotaged judge (math__gpt-5.2__sabotage_a escores)
# Same items, same candidate samples, same pairing rule, identical training downstream.
#
# REGISTERED PREDICTIONS (the audit's verdicts, applied to training pressure):
#  P-D1: the policy trained against the certified judge improves true (oracle) accuracy over
#        the base policy on held-out items; its judge-score gain and true gain agree in sign.
#  P-D2: the policy trained against the convicted judge shows a larger gap between its own
#        judge's score gain and its true-accuracy gain than the certified arm does (scoreboard
#        inflation appears under training exactly where the audit convicted), and its
#        true-accuracy gain is smaller than the certified arm's.
#  P-D3: instrument specificity: the sabotage-trained policy's score gain is larger under the
#        sabotaged judge than under the honest judge; the certified-trained policy's gain
#        transfers across the two judges.
# Disclosure: pairs are built from Qwen2.5-7B-Instruct samples (the audited pools), and the
# trained policy is the same model, so training is on-policy at the level of the generator.
import argparse, json, os, random

ap = argparse.ArgumentParser()
ap.add_argument("--cond", choices=["ref", "sabotage"], required=True)
ap.add_argument("--pool", default="runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl")
ap.add_argument("--scores", default=None, help="defaults to runs/bon_scores_v2/math__gpt-5.2__{cond}_a.jsonl")
ap.add_argument("--pairs-per-item", type=int, default=8)
ap.add_argument("--min-gap", type=float, default=2.0, help="min escore gap chosen-rejected")
ap.add_argument("--out", default="runs/dpo")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
rng = random.Random(0)

scores_f = args.scores or f"runs/bon_scores_v2/math__gpt-5.2__{args.cond}_a.jsonl"
sc = {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(scores_f)}
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/bon_math_tasks.jsonl")}

PROMPT = ("Solve the following math problem. Show your reasoning step by step, "
          "then give the final answer in \\boxed{}.\n\n")

n_pairs = 0
with open(f"{args.out}/pairs_{args.cond}.jsonl", "w") as f:
    for l in open(args.pool):
        r = json.loads(l)
        pid = r["problem_id"]
        if pid not in sc:
            continue
        es = sc[pid]
        order = sorted(range(len(es)), key=lambda i: es[i], reverse=True)
        top, bot = order[:16], order[-16:]
        made = 0
        tries = 0
        seen = set()
        while made < args.pairs_per_item and tries < 200:
            tries += 1
            i, j = rng.choice(top), rng.choice(bot)
            if (i, j) in seen or es[i] - es[j] < args.min_gap:
                continue
            seen.add((i, j))
            f.write(json.dumps(dict(
                problem_id=pid,
                prompt=PROMPT + tasks[pid]["problem"],
                chosen=r["samples"][i], rejected=r["samples"][j],
                score_chosen=es[i], score_rejected=es[j])) + "\n")
            made += 1
        n_pairs += made
print(f"[dpo_pairs] {args.cond}: {n_pairs} pairs -> {args.out}/pairs_{args.cond}.jsonl")
