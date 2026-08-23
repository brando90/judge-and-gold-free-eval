#!/bin/bash
# Pipeline 14: PILOT ONLY for the Paper D clean replication (registered calibration step;
# pilot items never enter the analysis). Generates Llama-3.1-8B best-of-64 on the 20 pilot
# tasks and reports oracle pass rates. The MAIN pool run is gated on the external (OSF)
# registration being posted and is launched separately. Waits for PIPELINE12C_DONE.
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline14.sh GPU}
mkdir -p logs
nohup env HOME=/lfs/skampere1/0/srivatsavad XDG_CACHE_HOME=/lfs/skampere1/0/srivatsavad/.cache HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface HF_HUB_OFFLINE=1 TMPDIR=/lfs/skampere1/0/srivatsavad/tmp PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge bash -c "cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge; \
  until grep -q PIPELINE12C_DONE logs/pipeline12c.log 2>/dev/null; do sleep 300; done; \
  CUDA_VISIBLE_DEVICES=$GPU .venv/bin/python bon_generate.py --domain replpilot --model meta-llama/Llama-3.1-8B-Instruct >> logs/pipeline14.log 2>&1; \
  .venv/bin/python repl_oracle.py --pool runs/bon/bon_replpilot__meta-llama__Llama-3.1-8B-Instruct.jsonl >> logs/pipeline14.log 2>&1; \
  echo PIPELINE14_DONE >> logs/pipeline14.log" > logs/pipeline14_outer.log 2>&1 &
echo "pipeline14 gpu$GPU PID $!"
