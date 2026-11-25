#!/bin/bash
# Experiment 03: sample 5 models on 4 GPUs of skampere1 (one lane per GPU, the 5th model after the first lane's).
# Usage: bash run_gen.sh <GPU list "3 7 2 4"> ; needs scripts/generate.py and bon_math_tasks.jsonl in ~/jfe03.
export HF_HUB_OFFLINE=1
cd ~/jfe03
read -r g1 g2 g3 g4 <<< "${1:-3 7 2 4}"
lane() { g=$1; shift; for m in "$@"; do CUDA_VISIBLE_DEVICES=$g python3 generate.py --model "$m" --n 16 --out gen --util 0.35 > "log_$(echo $m | tr / _).txt" 2>&1; done; }
lane $g1 Qwen/Qwen2.5-7B-Instruct Qwen/Qwen3-1.7B &
lane $g2 deepseek-ai/deepseek-math-7b-rl &
lane $g3 mistralai/Mistral-7B-Instruct-v0.2 &
lane $g4 Qwen/Qwen3-4B &
wait
echo ALL_DONE
