#!/bin/bash
# R3-D (registration_round3.md): blind-then-reveal and validity gate on MACE River+Language. Run from tfa-vs-judge root.
set -u
export CUDA_VISIBLE_DEVICES=${GPU:-4} HF_HUB_OFFLINE=1
PY=.venv/bin/python
mkdir -p logs/r3
run() { name=$1; shift; echo "[start $(date +%H:%M:%S)] $name"; "$@" > logs/r3/$name.log 2>&1; echo "[end $(date +%H:%M:%S)] $name rc=$?"; }
for J in Qwen/Qwen2.5-7B-Instruct microsoft/phi-4; do for C in m1 m2; do run "mace_${C}_${J##*/}" $PY scripts/r3_mitigation_mace.py --judge $J --cond $C --gpu-util 0.35; done; done
echo "R3 GPU4 CHAIN DONE $(date)"
