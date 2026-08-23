# Build the multi-valid-answer BoN task file from RewardBench-2's Ties subset (102 items:
# prompts with an enumerated set of equally-valid answers, e.g. "Pick a number between 1 and 10").
# Each task stores the full valid-answer set (the oracle) and ONE seeded-random valid answer
# (ref_answer) that the judge's ref condition will show, fixed at build time for auditability.
import json, random

from datasets import load_dataset

ds = load_dataset("allenai/reward-bench-2", split="test")
rng = random.Random(20260822)
n = 0
with open("runs/bon_ties_tasks.jsonl", "w") as f:
    for r in ds:
        if r.get("subset") != "Ties":
            continue
        valid = [c for c in r["chosen"] if isinstance(c, str) and c.strip()]
        if len(valid) < 2:
            continue
        f.write(json.dumps(dict(
            problem_id=f"ties/{r['id']}",
            problem=r["prompt"],
            valid_answers=valid,
            ref_answer=rng.choice(valid),
            n_valid=len(valid),
        )) + "\n")
        n += 1
print(f"wrote runs/bon_ties_tasks.jsonl ({n} tasks)")
