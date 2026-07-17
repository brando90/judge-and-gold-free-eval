# TLDR: Free-generate each model's OWN solution trace (what the judge grades and
# what boxed-correctness is scored on). Same vLLM engine as the TFA backend, so
# one model load serves both TFA (teacher-forced on gold) and free-gen.
from __future__ import annotations

from tfa.backends.common import build_tf_prompt


def free_generate(llm, tokenizer, items: list[tuple[str, str]], max_tokens: int = 2048,
                  temperature: float = 0.0, seed: int = 0) -> list[str]:
    """items: list of (question, dataset). Returns the model's generated solution text."""
    from vllm import SamplingParams

    prompts = [build_tf_prompt(q, d) for (q, d) in items]
    sp = SamplingParams(max_tokens=max_tokens, temperature=temperature, seed=seed)
    outputs = llm.generate(prompts, sp)
    return [o.outputs[0].text for o in outputs]
