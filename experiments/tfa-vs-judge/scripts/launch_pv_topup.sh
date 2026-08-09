#!/bin/bash
# Rollout-PV for all 200 random-stratum labeling traces, uniform 14B completer (the sweet spot
# behind the +0.43 claim). Run ON skampere1 after: scp runs/pv_topup_pairs.json and the patched
# scripts/run_rollout_prm.py to /lfs/skampere1/0/srivatsavad/tfa-vs-judge/.
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=/lfs/skampere1/0/srivatsavad/.cache
export HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface
export HF_HUB_OFFLINE=1
CUDA_VISIBLE_DEVICES=0 nohup .venv/bin/python run_rollout_prm.py \
  --completer Qwen/Qwen2.5-14B-Instruct --tp 1 \
  --responses 'runs/math500/*.judged.jsonl' 'runs/d2/math500__*phi-4*.judged.jsonl' \
  --pairs-file pv_topup_pairs.json --k 8 --out runs/prm_labelset \
  > logs/pv_topup.log 2>&1 &
echo "launched PID $!"
