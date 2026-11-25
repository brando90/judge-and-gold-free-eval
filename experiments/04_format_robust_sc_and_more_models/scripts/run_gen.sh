#!/bin/bash
# Experiment 04: sample the added models on skampere1 (one lane per GPU), n=16 x 500 MATH-500 problems, same harness as experiment 03.
# Usage: bash run_gen.sh "<gpu1> <gpu2> <gpu3>" ; needs ~/jfe04/generate.py and ~/jfe04/bon_math_tasks.jsonl. Models without refs/main load from their snapshot dir.
export HF_HUB_OFFLINE=1
cd ~/jfe04
read -r g1 g2 g3 <<< "${1:-0 4 7}"
snap() { ls -d ~/.cache/huggingface/hub/models--$1/snapshots/*/ | head -1; }
gen() { g=$1; hf=$2; CUDA_VISIBLE_DEVICES=$g python3 generate.py --model "$(snap ${hf/\//--})" --name "$hf" --n 16 --out gen --util 0.35 > "log_${hf/\//_}.txt" 2>&1; }
( gen $g1 Qwen/Qwen3-8B; gen $g1 deepseek-ai/deepseek-math-7b-instruct ) &
( gen $g2 Qwen/Qwen3.5-4B ) &
( gen $g3 meta-llama/Meta-Llama-3-8B-Instruct ) &
wait
echo ALL_DONE
