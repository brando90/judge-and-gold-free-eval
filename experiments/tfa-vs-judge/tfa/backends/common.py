# TLDR: Shared teacher-forcing helpers: build (prompt_ids, gold_ids) with each
# model's OWN tokenizer, and mark content vs. formatting tokens for the
# TFA-content shortcut control. Feeding token-ids (not re-tokenized strings) to
# both backends keeps the prompt/gold boundary exact and identical across HF/vLLM.
from __future__ import annotations

import re

# A gold token counts as "formatting" (non-content) if, once decoded and
# stripped, it is empty or pure punctuation/LaTeX glue. Used only by the
# TFA-content variant (shortcut control); default scoring keeps all tokens.
_FORMATTING = re.compile(r"^[\s\$\{\}\(\)\[\]\\,\.;:&%#~^_+\-=<>|/*'\"`]*$")


def build_tf_prompt(question: str, dataset: str) -> str:
    """The instruction wrapper placed BEFORE the gold trace under teacher forcing.

    Kept minimal and fixed (documented up front) so TFA is reproducible. The gold
    solution is appended after this and only its tokens are scored.
    """
    return (
        "Solve the following problem. Show your reasoning step by step and put the "
        f"final answer in \\boxed{{}}.\n\nProblem:\n{question}\n\nSolution:\n"
    )


def make_ids(tokenizer, question: str, gold_solution: str, dataset: str):
    """Return (prompt_ids, gold_ids, content_flags) using the model's own tokenizer."""
    prompt = build_tf_prompt(question, dataset)
    prompt_ids = tokenizer(prompt, add_special_tokens=True).input_ids
    gold_ids = tokenizer(gold_solution, add_special_tokens=False).input_ids
    content_flags = [not bool(_FORMATTING.match(tokenizer.decode([t]))) for t in gold_ids]
    return prompt_ids, gold_ids, content_flags
