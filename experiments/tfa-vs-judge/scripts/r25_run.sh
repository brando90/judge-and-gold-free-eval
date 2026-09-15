#!/bin/bash
# R25 runs (papers/D-iclr-v2/registration_round25.md). Run from experiments/tfa-vs-judge.
set -u
P=runs/r20/mace_gen/pool.jsonl
for T in cot verify solve; do
  python3 scripts/r25_judge_types.py --provider openai --model gpt-4.1-2025-04-14 --template $T --pool $P --out runs/r25/${T}_gpt41/pool.jsonl --cap-usd 6 --price-in 2 --price-out 8 &
  python3 scripts/r25_judge_types.py --provider anthropic --model claude-sonnet-5 --template $T --pool $P --out runs/r25/${T}_sonnet/pool.jsonl --cap-usd 9 --price-in 3 --price-out 15 &
done
wait
echo "[r25 all done]"
