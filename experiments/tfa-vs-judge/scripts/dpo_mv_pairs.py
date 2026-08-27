# Multi-valid DPO training-pressure experiment: what happens when the judge is used for
# TRAINING on tasks with multiple valid answers?
# INTERNAL REGISTRATION (git commit precedes any training; no OSF post per hold).
#
# Design. Policy = meta-llama/Llama-3.1-8B-Instruct (the generator of the k-stratified
# pool, so pairs are on-policy). Two LoRA-DPO arms with identical hyperparameters
# (4 epochs, lr 2e-5, beta 0.1, the registered R1-rerun settings), differing ONLY in the
# judge protocol that built the preference pairs, both from the Qwen2.5-7B judge (cross-
# family with the policy):
#   ref arm: pairs from the plain single-reference scores (synthk__...__ref_a)
#   m1 arm:  pairs from the blind-then-reveal scores    (kstrat__...__m1_a)
# Pairing rule identical to the registered paper-A pipeline: up to 8 pairs per item,
# min escore gap 2.0, seed 0. Items: k-stratified pool, k > 1 strata only.
# Evaluation (dpo_mv_eval.py): n=8 samples per item from base and both arms on the k>1
# TRAIN items and on the 120 replication-pool items as HELD-OUT (same five families, never
# trained on); true accuracy by the exact programmatic oracle; judge scores of the eval
# generations by the frozen Qwen-7B judge, blind and single-reference (and blind-then-
# reveal on the train split, for the m1 arm's manipulation check).
#
# REGISTERED PREDICTIONS (frozen estimators in papers/analysis/dpo_mv_analysis.py,
# committed together with this file):
#   GATE (manipulation check, gates everything; the paper-A lesson): each arm raises the
#     score its OWN training judge assigns to its train-item generations relative to base,
#     95% item-bootstrap CI excluding zero. Arms failing the gate void their predictions.
#   P-DP1 (parroting): the ref arm increases its rate of emitting the exact reference
#     answer on train items relative to base, and by MORE than the m1 arm does (paired
#     item-level difference, CI excluding zero).
#   P-DP2 (the wedge): under the frozen single-reference judge, the ref arm's
#     (judge-score gain minus true-accuracy gain) on train items exceeds the m1 arm's
#     (CI excluding zero). Disclosure: the analogous k=1 wedge prediction in paper A was
#     FALSIFIED (the corrupted signal damaged the policy instead); multi-valid tasks are
#     exactly where the wedge has room to appear, which is what this tests.
#   P-DP3 (the fix protects, directional): the m1 arm's held-out true-accuracy change is
#     no worse than the ref arm's (directional prediction, reported with CI).
#
# Usage: dpo_mv_pairs.py --arm {ref,m1}   (run from the cluster repo root)
import argparse
import json
import os
import random

ap = argparse.ArgumentParser()
ap.add_argument("--arm", choices=["ref", "m1"], required=True)
ap.add_argument("--pairs-per-item", type=int, default=8)
ap.add_argument("--min-gap", type=float, default=2.0)
ap.add_argument("--out", default="runs/dpo_mv")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
rng = random.Random(0)

JUDGE = "Qwen__Qwen2.5-7B-Instruct"
scores_f = (f"runs/bon_scores_kstrat/synthk__{JUDGE}__ref_a.jsonl" if args.arm == "ref"
            else f"runs/bon_scores_kstrat/kstrat__{JUDGE}__m1_a.jsonl")
sc = {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(scores_f)}
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
pool = {json.loads(l)["problem_id"]: json.loads(l)
        for l in open("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")}

PROMPT = ("Answer the following question. Think step by step if needed. You MUST end "
          "your response with the final answer inside \\boxed{...}, with nothing after "
          "it. Example ending: The answer is \\boxed{42}\n\n")

n_pairs = 0
with open(f"{args.out}/pairs_{args.arm}.jsonl", "w") as f:
    for pid, it in sorted(pool.items()):
        if tasks[pid].get("k", 0) <= 1 or pid not in sc:
            continue
        es = sc[pid]
        order = sorted(range(len(es)), key=lambda i: -es[i])
        made = 0
        for hi in order:
            if made >= args.pairs_per_item:
                break
            lows = [i for i in order[::-1] if es[hi] - es[i] >= args.min_gap and i != hi]
            if not lows:
                break
            lo = rng.choice(lows[:16])
            f.write(json.dumps(dict(
                problem_id=pid, prompt=PROMPT + it["question"],
                chosen=it["samples"][hi], rejected=it["samples"][lo],
                gap=round(es[hi] - es[lo], 3))) + "\n")
            made += 1
            n_pairs += 1
print(f"[dpo_mv_pairs] arm={args.arm}: {n_pairs} pairs -> {args.out}/pairs_{args.arm}.jsonl")
