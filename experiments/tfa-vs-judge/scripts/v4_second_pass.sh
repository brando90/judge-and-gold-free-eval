#!/bin/bash
# Waits for the running pool job to finish, then relaunches the generator.
#
# No separate item list is needed: v4_generate.py now selects 317 items, and resume is keyed on
# (question_id, sample), so this pass generates ONLY the ~3,904 draws for the 61 newly-adopted
# Math-Constraint items and skips everything already written.
set -u
cd "$(dirname "$0")/.."
WATCH_PID="${1:?usage: v4_second_pass.sh <pid-of-running-generator>}"
echo "[second-pass] waiting for pid $WATCH_PID to finish..." >> logs/v4_pool_gen.log
while ps -p "$WATCH_PID" >/dev/null 2>&1; do sleep 60; done
echo "[second-pass] pid $WATCH_PID exited; starting pass 2 over the 61 new items" >> logs/v4_pool_gen.log
exec python3 scripts/v4_generate.py \
  --model gpt-4.1-mini-2025-04-14 --provider openai \
  --price-in 0.4 --price-out 1.6 \
  --n-samples 64 --workers 24 --cap-usd 140 >> logs/v4_pool_gen.log 2>&1
