#!/bin/bash
# R26 API runs (papers/D-iclr-v2/registration_round26.md). Run from experiments/tfa-vs-judge.
set -u
B=runs/r20/mace_gen/pool.jsonl
S=runs/r8/sonnet_mace.jsonl
J="python3 scripts/r26_judges.py"
run() {  # pool-tag pool template conds
  $J --provider openai --model gpt-4.1-2025-04-14 --template $3 --conds $4 --pool $2 --out runs/r26/$1_$3_gpt41/scores.jsonl --cap-usd 3 --price-in 2 --price-out 8 &
  $J --provider anthropic --model claude-sonnet-5 --template $3 --conds $4 --pool $2 --out runs/r26/$1_$3_sonnet/scores.jsonl --cap-usd 5 --price-in 3 --price-out 15 --workers 6 &
}
run bench $B direct noref,ref
run bench $B hle ref
run bench $B hle_edit ref
wait
run sub $S direct noref,ref
run sub $S verify noref,ref
run sub $S solve noref,ref
wait
run sub $S hle ref
run sub $S hle_edit ref
wait
echo "[r26 api all done]"
