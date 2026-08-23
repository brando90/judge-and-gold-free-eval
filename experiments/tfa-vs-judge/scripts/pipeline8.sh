#!/bin/bash
# Pipeline 8: completer-strength sweep for Paper B (the "middle band" claim is currently a
# design expectation, not a measured result; this measures it). Same anchor pairs and
# machinery as the existing Qwen-14B and phi-4 completer runs; only completer size varies.
# Registered prediction P-C1 (committed pre-run): the process-value validity (Pearson vs
# human soundness) is low for the 1.5B completer (washed out: too weak to repair any prefix),
# rises through 3B/7B, and does NOT exceed the 14B value at 32B by a large margin
# (saturation: a too-strong completer repairs everything, eroding prefix sensitivity).
# Waits for PIPELINE7_DONE. Run ON skampere1: bash pipeline8.sh <GPU>
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=$HOME/.cache
export HF_HOME=$HOME/.cache/huggingface
export HF_HUB_OFFLINE=1
export TMPDIR=$HOME/tmp
export PY=/lfs/skampere1/0/srivatsavad/tfa-vs-judge/.venv/bin/python
export PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline8.sh GPU}
mkdir -p logs

nohup bash -c "cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge; \
  until grep -q PIPELINE7_DONE logs/pipeline7.log 2>/dev/null; do sleep 300; done; \
  for m in Qwen/Qwen2.5-1.5B-Instruct Qwen/Qwen2.5-3B-Instruct Qwen/Qwen2.5-7B-Instruct Qwen/Qwen2.5-32B-Instruct; do \
    CUDA_VISIBLE_DEVICES=$GPU \$PY scripts/run_rollout_prm.py --completer \$m \
      --responses 'runs/math500/*.judged.jsonl' --pairs-file pv_topup_pairs.json --k 8 --tp 1 \
      --out runs/prm_sweep >> logs/pipeline8.log 2>&1; \
  done; \
  echo PIPELINE8_DONE >> logs/pipeline8.log" > logs/pipeline8_outer.log 2>&1 &
echo "pipeline8 gpu$GPU PID $!"
