#!/bin/bash
# R24 OpenAI runs (papers/D-iclr-v2/registration_round24.md). Run from experiments/tfa-vs-judge.
set -u
P=runs/r20/mace_gen/pool.jsonl
H="python3 scripts/r24_grader_pool.py --provider openai"
$H --model gpt-4.1-2025-04-14 --template simpleqa --conds ref,reflist --pool $P --out runs/r24/std_s41/pool.jsonl --cap-usd 8 --price-in 2 --price-out 8 &
$H --model gpt-4.1-2025-04-14 --template hle --conds ref,reflist --pool $P --out runs/r24/std_h41/pool.jsonl --cap-usd 8 --price-in 2 --price-out 8 &
$H --model o3-mini-2025-01-31 --template hle --conds ref,reflist --pool $P --out runs/r24/std_h03/pool.jsonl --cap-usd 8 --price-in 1.1 --price-out 4.4 &
$H --model gpt-4.1-2025-04-14 --template rubric --conds noref,ref,reflist --pool runs/r8/sonnet_mace.jsonl --out runs/r24/reflist_gpt41_api/mace.jsonl --cap-usd 2 --price-in 2 --price-out 8 &
( $H --model gpt-4.1-2025-04-14 --template rubric --conds noref,ref --pool $P --out runs/r24/leaderboard_gpt41_api/pool.jsonl --cap-usd 3 --price-in 2 --price-out 8 \
  && python3 scripts/r24_seed.py --part b \
  && $H --model gpt-4.1-2025-04-14 --template rubric --conds ref --pool runs/r22/redraw_pool.jsonl --out runs/r24/redraw_gpt41_api/pool.jsonl --cap-usd 2 --price-in 2 --price-out 8 ) &
wait
echo "[r24 openai all done]"
