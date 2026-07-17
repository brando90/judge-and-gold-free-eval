# TLDR: Throughput TFA via vLLM `prompt_logprobs`. Feeds concatenated token-ids
# so the gold region is exact, batches all problems in one generate() call, and
# reads per-position top-k (rank-1 == argmax) + the forced gold-token logprob.
# IMPORTANT: disable prefix caching for reproducible prompt logprobs.
from __future__ import annotations

from tfa.core import PosRecord
from tfa.backends.common import make_ids

# vLLM includes the actual prompt token's logprob even if outside top-k, but we
# set a generous K so the argmax and gold token are both present.
PROMPT_LOGPROBS_K = 20


def load_vllm(model_name: str, tp_size: int = 1, dtype: str = "bfloat16",
              max_model_len: int | None = None, gpu_memory_utilization: float = 0.85):
    from vllm import LLM
    from transformers import AutoTokenizer

    llm = LLM(
        model=model_name, tensor_parallel_size=tp_size, dtype=dtype,
        enable_prefix_caching=False, max_model_len=max_model_len,
        gpu_memory_utilization=gpu_memory_utilization,
    )
    tok = AutoTokenizer.from_pretrained(model_name)
    return llm, tok


def tfa_records_vllm_batch(llm, tokenizer, items: list[tuple[str, str, str]]) -> list[list[PosRecord]]:
    """items: list of (question, gold_solution, dataset). Returns per-item records."""
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt

    prepared = [make_ids(tokenizer, q, g, d) for (q, g, d) in items]
    prompts = [TokensPrompt(prompt_token_ids=(p + g)) for (p, g, _c) in prepared]
    sp = SamplingParams(max_tokens=1, temperature=1.0, prompt_logprobs=PROMPT_LOGPROBS_K)
    outputs = llm.generate(prompts, sp)

    results: list[list[PosRecord]] = []
    for (prompt_ids, gold_ids, content_flags), out in zip(prepared, outputs):
        plps = out.prompt_logprobs  # list aligned with prompt_token_ids; [0] is None
        p = len(prompt_ids)
        recs: list[PosRecord] = []
        for k, gid in enumerate(gold_ids):
            d = plps[p + k]  # {token_id: Logprob(logprob, rank, ...)}
            if not d:
                continue
            top1 = min(d.items(), key=lambda kv: kv[1].rank)[0]  # rank 1 == argmax over full vocab
            gold_lp = d[gid].logprob if gid in d else None
            recs.append(PosRecord(gold_id=int(gid), top1_id=int(top1),
                                  gold_logprob=gold_lp, is_content=content_flags[k]))
        results.append(recs)
    return results
