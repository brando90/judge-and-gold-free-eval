#!/bin/bash
# R4-C (registration_round4.md): Qwen3-14B, thinking off then on, R3 protocol (r3_judge.py unchanged). Run from tfa-vs-judge root.
set -u
export CUDA_VISIBLE_DEVICES=${GPU:-5}
PY=.venv/bin/python
U=${UTIL:-0.6}
mkdir -p logs/r4
until grep -q '^DONE' logs/r4/download_qwen3_14b.log; do sleep 60; done
export HF_HUB_OFFLINE=1
run() { name=$1; shift; echo "[start $(date +%H:%M:%S)] $name"; "$@" > logs/r4/$name.log 2>&1; echo "[end $(date +%H:%M:%S)] $name rc=$?"; }
X="$PY scripts/r3_judge.py --judge Qwen/Qwen3-14B --out runs/r4/qwen3_14b --gpu-util $U"
for T in off on; do
  for C in ref refrot noref; do run "q3_14b_rot_${T}_$C" $X --pool rot --cond $C --thinking $T; done
  for C in ref noref; do run "q3_14b_ksub_${T}_$C" $X --pool ksub --cond $C --thinking $T; done
  for C in ref noref; do run "q3_14b_macesub_${T}_$C" $X --pool macesub --cond $C --thinking $T; done
done
echo "R4 GPU5 CHAIN DONE $(date)"
