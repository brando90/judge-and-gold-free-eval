#!/bin/bash
# R4-A (k-pool, three more judges) and R4-B (Qwen2.5-14B), exact estimator, sequential on one GPU.
# Run from tfa-vs-judge root.
set -u
export CUDA_VISIBLE_DEVICES=${GPU:-4} HF_HUB_OFFLINE=1
PY=.venv/bin/python
U=${UTIL:-0.36}
mkdir -p logs/r4
run() { name=$1; shift; echo "[start $(date +%H:%M:%S)] $name"; "$@" > logs/r4/$name.log 2>&1; echo "[end $(date +%H:%M:%S)] $name rc=$?"; }
KP=runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl
for J in Qwen/Qwen2.5-14B-Instruct google/gemma-2-9b-it mistralai/Mistral-7B-Instruct-v0.3; do
  t=$(basename $J)
  for C in noref ref; do run "${t}_kstrat_$C" $PY scripts/r4_judge_exact.py --judge $J --gpu-util $U --pool $KP --name kstrat --domain synthk --cond $C; done
done
J=Qwen/Qwen2.5-14B-Instruct
for C in noref ref refans; do run "q14_math_$C" $PY scripts/r4_judge_exact.py --judge $J --gpu-util $U --pool runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl --tasks runs/bon_math_tasks.jsonl --band 0.2 0.8 --name math --domain math --cond $C; done
echo "R4 GPU4 CHAIN DONE $(date)"
