#!/bin/bash
# Cross-family completer rerun of the prefix-repair curve (kills the family-overlap caveat):
# identical 200 random-stratum (model, problem_id) pairs, completer = microsoft/phi-4 instead
# of Qwen2.5-14B. Registered prediction (docs/multi-valid-bon-registration.md sibling; written
# before the run): the monotone depth profile and the deep-truncation correlation with human
# soundness survive a completer from a different family (headline within +/-0.15 of +0.79).
# Run ON skampere1 from /lfs/skampere1/0/srivatsavad/tfa-vs-judge; 1 GPU (2-GPU cap respected
# when run alongside bon_chain_ties.sh).
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=/lfs/skampere1/0/srivatsavad/.cache
export HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface
export HF_HUB_OFFLINE=1
export TMPDIR=/lfs/skampere1/0/srivatsavad/tmp
GPU=${1:?usage: launch_pv_crossfam.sh GPU}
mkdir -p logs runs/prm_labelset_phi4
nohup env CUDA_VISIBLE_DEVICES=$GPU .venv/bin/python scripts/run_rollout_prm.py \
  --completer microsoft/phi-4 \
  --responses 'runs/math500/*.judged.jsonl' \
  --pairs-file pv_topup_pairs.json --k 8 \
  --out runs/prm_labelset_phi4 \
  > logs/pv_crossfam.log 2>&1 &
echo "pv crossfam gpu$GPU PID $!"
