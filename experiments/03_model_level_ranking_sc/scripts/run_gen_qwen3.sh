#!/bin/bash
# Experiment 03 follow-up launcher: the two Qwen3 models have no refs/main in the host's HF cache, so load them from their snapshot directories.
export HF_HUB_OFFLINE=1
cd ~/jfe03
for m in Qwen3-4B Qwen3-1.7B; do
  d=$(ls -d ~/.cache/huggingface/hub/models--Qwen--$m/snapshots/*/ | head -1)
  CUDA_VISIBLE_DEVICES=${1:-4} python3 generate.py --model "$d" --name Qwen/$m --n 16 --out gen --util 0.35 > "log_Qwen_$m.txt" 2>&1
done
echo QWEN3_DONE
