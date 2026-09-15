# R24 (papers/D-iclr-v2/registration_round24.md): seed round-24 score files with calls that already exist, so the harness adds only
# the new condition. Run from experiments/tfa-vs-judge.
#   --part c : runs/r24/reflist_{sonnet,opus}_api/mace.jsonl <- the blind and referenced rows of runs/r8/sonnet_api/mace.jsonl
#              (Sonnet 5, R8-A) and runs/r19/opus_api/mace.jsonl (Opus 5, R19-A)
#   --part d : runs/r24/think_inst_sonnet_api/mace.jsonl <- the blind rows of runs/r19/sonnet_think_api/mace.jsonl (R19-B)
#   --part b : runs/r24/redraw_gpt41_api/pool.jsonl <- the blind rows of runs/r24/leaderboard_gpt41_api/pool.jsonl (after R24-B1)
import argparse
import json
import os

ap = argparse.ArgumentParser()
ap.add_argument("--part", choices=("b", "c", "d"), required=True)
args = ap.parse_args()
PLAN = {
    "c": [("runs/r8/sonnet_api/mace.jsonl", "runs/r24/reflist_sonnet_api/mace.jsonl", ("noref", "ref")),
          ("runs/r19/opus_api/mace.jsonl", "runs/r24/reflist_opus_api/mace.jsonl", ("noref", "ref"))],
    "d": [("runs/r19/sonnet_think_api/mace.jsonl", "runs/r24/think_inst_sonnet_api/mace.jsonl", ("noref",))],
    "b": [("runs/r24/leaderboard_gpt41_api/pool.jsonl", "runs/r24/redraw_gpt41_api/pool.jsonl", ("noref",))],
}
for src, dst, keep in PLAN[args.part]:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        print("[exists]", dst)
        continue
    n = 0
    with open(dst, "w") as f:
        for line in open(src):
            r = json.loads(line)
            if r["cond"] in keep and r.get("score") is not None and not r.get("error"):
                f.write(json.dumps(r) + "\n")
                n += 1
    print(f"[seeded] {dst}: {n} rows ({', '.join(keep)})")
