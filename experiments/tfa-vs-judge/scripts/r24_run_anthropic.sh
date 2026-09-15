#!/bin/bash
# R24 Anthropic runs (papers/D-iclr-v2/registration_round24.md). Run from experiments/tfa-vs-judge.
set -u
P=runs/r20/mace_gen/pool.jsonl
H="python3 scripts/r24_grader_pool.py --provider anthropic"
python3 scripts/r24_seed.py --part c
python3 scripts/r24_seed.py --part d
$H --model claude-sonnet-5 --template simpleqa --conds ref,reflist --pool $P --out runs/r24/std_sS5/pool.jsonl --max-tokens 512 --cap-usd 6 --price-in 3 --price-out 15 &
$H --model claude-sonnet-5 --template hle --conds ref,reflist --pool $P --out runs/r24/std_hS5/pool.jsonl --max-tokens 1024 --cap-usd 6 --price-in 3 --price-out 15 &
$H --model claude-sonnet-5 --template rubric --conds reflist --pool runs/r8/sonnet_mace.jsonl --out runs/r24/reflist_sonnet_api/mace.jsonl --max-tokens 512 --cap-usd 3 --price-in 3 --price-out 15 &
$H --model claude-opus-5 --template rubric --conds reflist --pool runs/r8/sonnet_mace.jsonl --out runs/r24/reflist_opus_api/mace.jsonl --max-tokens 512 --cap-usd 8 --price-in 15 --price-out 75 &
$H --model claude-sonnet-5 --template rubric --conds ref --pool runs/r8/sonnet_mace.jsonl --out runs/r24/think_inst_sonnet_api/mace.jsonl --thinking adaptive --max-tokens 8000 --instruction anyvalid --cap-usd 8 --price-in 3 --price-out 15 --workers 4 &
wait
echo "[r24 anthropic all done]"
