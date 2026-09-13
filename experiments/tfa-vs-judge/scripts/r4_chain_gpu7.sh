#!/bin/bash
# R4-A and R4-B (registration_round4.md), Qwen2.5-7B-Instruct, exact estimator, sequential on one GPU.
# Run from tfa-vs-judge root.
set -u
export CUDA_VISIBLE_DEVICES=${GPU:-7} HF_HUB_OFFLINE=1
PY=.venv/bin/python
U=${UTIL:-0.5}
mkdir -p logs/r4
run() { name=$1; shift; echo "[start $(date +%H:%M:%S)] $name"; "$@" > logs/r4/$name.log 2>&1; echo "[end $(date +%H:%M:%S)] $name rc=$?"; }
J=Qwen/Qwen2.5-7B-Instruct
X="$PY scripts/r4_judge_exact.py --judge $J --gpu-util $U"
for C in noref ref; do run "q7_repl_$C" $X --pool runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl --name repl --domain synthk --cond $C; done
run q7_replrot_ref $X --pool runs/bon/bon_replrot__meta-llama__Llama-3.1-8B-Instruct.jsonl --name replrot --domain synthk --cond ref
for C in noref ref; do run "q7_kstrat_$C" $X --pool runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl --name kstrat --domain synthk --cond $C; done
for C in noref ref; do run "q7_mace_$C" $X --pool runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl --tasks runs/mace_tasks.jsonl --band 0.05 0.95 --name mace --domain mace --cond $C; done
for C in noref ref refans; do run "q7_math_$C" $X --pool runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl --tasks runs/bon_math_tasks.jsonl --band 0.2 0.8 --name math --domain math --cond $C; done
echo "R4 GPU7 CHAIN DONE $(date)"
