#!/usr/bin/env python
# TLDR: SNAP/GPU sanity check that the throughput vLLM TFA backend matches the
# ground-truth HF backend bit-for-bit on a toy (model, gold) pair. Run this ONCE
# per model family before trusting large runs (harness exit criterion E0).
#   python scripts/verify_backends.py --model Qwen/Qwen2.5-0.5B-Instruct
from __future__ import annotations

import argparse

from tfa.core import score_tfa
from tfa.backends.hf import load_hf, tfa_records_hf
from tfa.backends.vllm_backend import load_vllm, tfa_records_vllm_batch

TOY = [
    ("What is 2+2?", "We add 2 and 2 to get \\boxed{4}.", "math"),
    ("What is the derivative of x^2?", "By the power rule, d/dx x^2 = 2x, so \\boxed{2x}.", "math"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--atol", type=float, default=1e-6)
    args = ap.parse_args()

    hf_model, hf_tok = load_hf(args.model, device="cuda")
    hf = [score_tfa(tfa_records_hf(hf_model, hf_tok, q, g, d)) for (q, g, d) in TOY]

    # Free the HF model before vLLM profiles GPU memory (they share one device).
    import gc, torch
    del hf_model
    gc.collect(); torch.cuda.empty_cache()

    llm, vtok = load_vllm(args.model, gpu_memory_utilization=0.4)
    vll = [score_tfa(r) for r in tfa_records_vllm_batch(llm, vtok, TOY)]

    ok = True
    for i, (h, v) in enumerate(zip(hf, vll)):
        da = abs(h.tfa_argmax - v.tfa_argmax)
        dl = abs(h.tfa_logprob - v.tfa_logprob)
        flag = "OK" if (da < args.atol and dl < 1e-2) else "MISMATCH"
        ok &= flag == "OK"
        print(f"[{flag}] item {i}: HF argmax={h.tfa_argmax:.4f} logprob={h.tfa_logprob:.4f} | "
              f"vLLM argmax={v.tfa_argmax:.4f} logprob={v.tfa_logprob:.4f}")
    print("PASS" if ok else "FAIL -- vLLM backend does not match HF ground truth")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
