#!/bin/bash
# Pipeline 17: judge-coverage extension of the k-stratified structural-mitigation
# experiment (registration: papers/registrations/osf_drafts.md Registration 5, to be
# posted to OSF BEFORE this pipeline runs). Reuses the existing osf.io/qugbd pool and
# Llama-3.1-8B best-of-64 samples unchanged; only the judging is new.
# Judges (one per invocation): google/gemma-2-9b-it, mistralai/Mistral-7B-Instruct-v0.3,
# Qwen/Qwen2.5-14B-Instruct. Backup on vLLM load failure: 01-ai/Yi-1.5-9B-Chat.
# Conditions: blind, single-ref (bon_judge.py), M1, M2 (mitigation_judge.py), rubrics a/b.
# Usage: pipeline17.sh GPU JUDGE   (e.g. pipeline17.sh 3 google/gemma-2-9b-it)
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline17.sh GPU JUDGE}
JUDGE=${2:?usage: pipeline17.sh GPU JUDGE}
TAG=$(echo "$JUDGE" | tr '/' '_')
mkdir -p logs runs/bon_scores_kstrat
nohup env HOME=/lfs/skampere1/0/srivatsavad XDG_CACHE_HOME=/lfs/skampere1/0/srivatsavad/.cache HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface TMPDIR=/lfs/skampere1/0/srivatsavad/tmp PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge bash -c "cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge; \
  HF_HUB_OFFLINE=0 .venv/bin/huggingface-cli download $JUDGE --exclude '*.pth' '*consolidated*' >> logs/pipeline17_${TAG}.log 2>&1; \
  export HF_HUB_OFFLINE=1; \
  for cond in noref ref; do for rep in a b; do \
    CUDA_VISIBLE_DEVICES=$GPU .venv/bin/python bon_judge.py --pool runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl \
      --judge $JUDGE --cond \$cond --rep \$rep --domain synthk --tasks runs/kstrat_tasks.jsonl --out runs/bon_scores_kstrat >> logs/pipeline17_${TAG}.log 2>&1; \
  done; done; \
  for cond in m1 m2; do for rep in a b; do \
    CUDA_VISIBLE_DEVICES=$GPU .venv/bin/python mitigation_judge.py --pool runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl \
      --judge $JUDGE --cond \$cond --rep \$rep --out runs/bon_scores_kstrat >> logs/pipeline17_${TAG}.log 2>&1; \
  done; done; \
  echo PIPELINE17_${TAG}_DONE >> logs/pipeline17_${TAG}.log" > logs/pipeline17_${TAG}_outer.log 2>&1 &
echo "pipeline17 $JUDGE gpu$GPU PID $!"
