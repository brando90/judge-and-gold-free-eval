# R23-A (papers/D-iclr/registration_round23.md): seed the same-reference regrade score files with each grader's existing blind calls,
# so that scripts/sonnet_api_pool.py --conds ref adds only referenced calls with the first reference. Run from experiments/tfa-vs-judge.
# Outputs: runs/r23/regrade_{sonnet,opus,haiku}_api/pool.jsonl (blind rows copied from the first-draw files).
import json
import os

GRADERS = {"sonnet": "runs/r20/leaderboard_sonnet_api/pool.jsonl", "opus": "runs/r21/leaderboard_opus_api/pool.jsonl",
           "haiku": "runs/r21/leaderboard_haiku_api/pool.jsonl"}
for g, src in GRADERS.items():
    dst = f"runs/r23/regrade_{g}_api/pool.jsonl"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        print("[exists]", dst)
        continue
    n = 0
    with open(dst, "w") as f:
        for l in open(src):
            r = json.loads(l)
            if r["cond"] == "noref" and r.get("score") is not None and not r.get("error"):
                f.write(json.dumps(r) + "\n")
                n += 1
    print(f"[seeded] {dst}: {n} blind rows")
