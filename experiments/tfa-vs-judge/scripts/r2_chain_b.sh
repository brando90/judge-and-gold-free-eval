#!/bin/bash
# R2-B relaunch (registration_round2.md, Amendment 2): same runs as r2_chain.sh after the math steps.
set -u
GPU=${GPU:-7}
PY=.venv/bin/python
export CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1
mkdir -p logs/r2
run() { name=$1; shift; echo "[start $(date +%H:%M:%S)] $name"; "$@" > logs/r2/$name.log 2>&1; echo "[end $(date +%H:%M:%S)] $name rc=$?"; }
for C in ref refrot noref; do run "rot_mtbench_$C" $PY scripts/r2_judge.py --protocol mtbench --pool rot --cond $C --judge Qwen/Qwen2.5-7B-Instruct; done
for C in ref noref; do run "ksub_mtbench_$C" $PY scripts/r2_judge.py --protocol mtbench --pool ksub --cond $C --judge Qwen/Qwen2.5-7B-Instruct; done
for C in ref refrot noref; do run "rot_reason_$C" $PY scripts/r2_judge.py --protocol reason --pool rot --cond $C --judge Qwen/Qwen3-8B; done
for C in ref noref; do run "ksub_reason_$C" $PY scripts/r2_judge.py --protocol reason --pool ksub --cond $C --judge Qwen/Qwen3-8B; done
echo "R2B CHAIN DONE $(date)"
