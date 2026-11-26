#!/bin/bash
# Experiment 05 on SNAP mercury2: 10 idle RTX A4000 16 GB GPUs, local vLLM, no paid API.
# 7B/8B models use 2-GPU tensor parallel. Qwen3-1.7B, Qwen3-4B, and Qwen3.5-4B use one GPU.
# Logs, tasks, and samples: /lfs/mercury2/0/brando9/judge-free-eval-exp05/
#
# From the repo root on mercury2:
#   tmux new-session -d -s exp05 'bash experiments/05_gsm8k_format_robust_sc/scripts/run_mercury2.sh'
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO"

ROOT=/lfs/mercury2/0/brando9/judge-free-eval-exp05
mkdir -p "$ROOT/logs" "$ROOT/gen" "$ROOT/tmp" "$ROOT/results"

export HF_HOME="${HF_HOME:-/lfs/mercury2/0/brando9/.cache/huggingface}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/lfs/mercury2/0/brando9/.cache}"
export TMPDIR="$ROOT/tmp"
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1

if [[ -n "${PY:-}" ]]; then
  :
elif [[ -x "${HOME}/.venvs/jfe/bin/python" ]]; then
  PY="${HOME}/.venvs/jfe/bin/python"
elif [[ -x /lfs/mercury2/0/brando9/.venvs/jfe/bin/python ]]; then
  PY=/lfs/mercury2/0/brando9/.venvs/jfe/bin/python
else
  PY="$(command -v python3)"
fi

SCRIPT="$REPO/experiments/05_gsm8k_format_robust_sc/scripts/generate_gsm8k.py"
TASKS="$ROOT/tasks_gsm8k_test.jsonl"
DRIVER="$ROOT/logs/driver.log"

if [[ "$(hostname)" != "mercury2" ]]; then
  echo "warning: hostname is $(hostname); this launcher targets mercury2" | tee -a "$DRIVER"
fi

echo "START_TASKS $(date -Is) py=$PY" | tee -a "$DRIVER"
"$PY" "$SCRIPT" --write-tasks-only --tasks "$TASKS" >> "$ROOT/logs/tasks.log" 2>&1
echo "TASKS_FROZEN $(date -Is)" | tee -a "$DRIVER"

# gen <CUDA_VISIBLE_DEVICES> <tp> <hf-id> <batch>
gen() {
  local gpus="$1" tp="$2" hf="$3" batch="$4"
  local safe="${hf//\//_}"
  local log="$ROOT/logs/${safe}.log"
  echo "START $(date -Is) gpus=${gpus} tp=${tp} batch=${batch} ${hf}" | tee -a "$DRIVER" | tee -a "$log"
  set +e
  CUDA_VISIBLE_DEVICES="$gpus" "$PY" "$SCRIPT" \
    --model "$hf" --tp "$tp" --n 16 --batch "$batch" --util 0.90 \
    --tasks "$TASKS" --out "$ROOT/gen" \
    >> "$log" 2>&1
  local rc=$?
  set -e
  echo "END $(date -Is) rc=${rc} ${hf}" | tee -a "$DRIVER" | tee -a "$log"
  return "$rc"
}

wait_pids() {
  local fail=0 pid
  for pid in "$@"; do
    wait "$pid" || fail=1
  done
  if (( fail )); then
    echo "WAVE_FAILED $(date -Is)" | tee -a "$DRIVER"
    exit 1
  fi
}

# Wave 1: five 7B/8B models, two GPUs each, all ten cards.
pids=()
gen 0,1 2 meta-llama/Llama-3.1-8B-Instruct 4 & pids+=($!)
gen 2,3 2 Qwen/Qwen2.5-7B-Instruct 4 & pids+=($!)
gen 4,5 2 deepseek-ai/deepseek-math-7b-rl 4 & pids+=($!)
gen 6,7 2 mistralai/Mistral-7B-Instruct-v0.2 4 & pids+=($!)
gen 8,9 2 Qwen/Qwen3-8B 4 & pids+=($!)
wait_pids "${pids[@]}"

# Wave 2: the other two 7B/8B models, then the three smaller models on one GPU each.
pids=()
gen 0,1 2 meta-llama/Meta-Llama-3-8B-Instruct 4 & pids+=($!)
gen 2,3 2 deepseek-ai/deepseek-math-7b-instruct 4 & pids+=($!)
gen 4 1 Qwen/Qwen3-4B 4 & pids+=($!)
gen 5 1 Qwen/Qwen3-1.7B 4 & pids+=($!)
gen 6 1 Qwen/Qwen3.5-4B 4 & pids+=($!)
wait_pids "${pids[@]}"

echo "ALL_DONE $(date -Is)" | tee -a "$DRIVER"
echo "Analyze with: $PY $REPO/experiments/05_gsm8k_format_robust_sc/scripts/analyze_gsm8k.py --tasks $TASKS --gen $ROOT/gen --out $ROOT/results" | tee -a "$DRIVER"
