# TLDR: TFA backends. `hf` is the ground-truth teacher-forcing reference;
# `vllm_backend` is the throughput path. Both emit list[PosRecord] over the gold
# tokens so `tfa.core.score_tfa` produces identical numbers from either.
