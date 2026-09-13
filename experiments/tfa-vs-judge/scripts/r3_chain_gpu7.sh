#!/bin/bash
# R3-A and R3-C (registration_round3.md), Qwen3-8B, sequential on one GPU. Run from tfa-vs-judge root.
set -u
export CUDA_VISIBLE_DEVICES=${GPU:-7} HF_HUB_OFFLINE=1
PY=.venv/bin/python
mkdir -p logs/r3
run() { name=$1; shift; echo "[start $(date +%H:%M:%S)] $name"; "$@" > logs/r3/$name.log 2>&1; echo "[end $(date +%H:%M:%S)] $name rc=$?"; }
$PY scripts/r3_build_subsamples.py > logs/r3/build.log 2>&1
for C in ref refrot noref; do run "rot_off_$C" $PY scripts/r3_judge.py --pool rot --cond $C --thinking off; done
for C in ref noref; do run "ksub_off_$C" $PY scripts/r3_judge.py --pool ksub --cond $C --thinking off; done
for T in on off; do for C in ref noref; do run "macesub_${T}_$C" $PY scripts/r3_judge.py --pool macesub --cond $C --thinking $T; done; done
echo "R3 GPU7 CHAIN DONE $(date)"
