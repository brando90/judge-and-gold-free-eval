# R27 (papers/D-iclr-v2/registration_round27.md): build the hard-question pool from the two generators' HLE answers.
# Run from experiments/tfa-vs-judge. Reads papers/analysis/prevalence_v2/items_hle.jsonl (200 text-only exact-answer HLE questions,
# sampled with seed 0 for the prevalence audit) and runs/r27/gen_<model>.jsonl. Writes runs/r27/hle_pool.jsonl with one row per
# question: problem_id, question, ref (the HLE answer), idx [0, 1], generators, samples (each generator's full reply; an empty string
# when its call failed, which the judges then grade as given).
import json

ITEMS = "../../papers/analysis/prevalence_v2/items_hle.jsonl"
GENS = ["gpt-4.1-mini-2025-04-14", "claude-haiku-4-5-20251001"]
items = [json.loads(l) for l in open(ITEMS)]
replies = {}
for g in GENS:
    for l in open(f"runs/r27/gen_{g}.jsonl"):
        r = json.loads(l)
        replies[(g, r["problem_id"])] = r.get("text") or ""
with open("runs/r27/hle_pool.jsonl", "w") as f:
    for it in items:
        f.write(json.dumps(dict(problem_id=it["id"], question=it["question"], ref=it["reference"], idx=[0, 1], generators=GENS,
                                samples=[replies.get((g, it["id"]), "") for g in GENS])) + "\n")
print("wrote runs/r27/hle_pool.jsonl", len(items), "questions;", sum(1 for k, v in replies.items() if not v), "empty replies")
