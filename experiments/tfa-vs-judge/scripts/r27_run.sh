#!/bin/bash
# R27-B runs (papers/D-iclr-v2/registration_round27.md). Run from experiments/tfa-vs-judge.
set -u
python3 scripts/r27_generate.py --provider openai --model gpt-4.1-mini-2025-04-14 --cap-usd 3 --price-in 0.4 --price-out 1.6 &
python3 scripts/r27_generate.py --provider anthropic --model claude-haiku-4-5-20251001 --cap-usd 4 --price-in 1 --price-out 5 &
wait
python3 scripts/r27_build_pool.py
P=runs/r27/hle_pool.jsonl
# labels: HLE's official judge (verbatim prompt, o3-mini, structured output) against the HLE answer
python3 scripts/r24_grader_pool.py --provider openai --model o3-mini-2025-01-31 --template hle --conds ref --pool $P --out runs/r27/labels_o3mini/pool.jsonl --cap-usd 6 --price-in 1.1 --price-out 4.4 &
J="python3 scripts/r26_judges.py"
for T in hle direct solve; do
  C=ref; [ $T != hle ] && C=noref,ref
  $J --provider openai --model gpt-4.1-2025-04-14 --template $T --conds $C --pool $P --out runs/r27/hle_${T}_gpt41/scores.jsonl --cap-usd 6 --price-in 2 --price-out 8 &
  $J --provider anthropic --model claude-sonnet-5 --template $T --conds $C --pool $P --out runs/r27/hle_${T}_sonnet/scores.jsonl --cap-usd 10 --price-in 3 --price-out 15 --workers 6 &
done
wait
echo "[r27 all done]"
