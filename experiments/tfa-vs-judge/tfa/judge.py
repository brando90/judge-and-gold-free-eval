# TLDR: The "most capable LLM judge" baseline TFA is validated against. Grades a
# model's OWN free-generated reasoning trace for QUALITY (validity of steps, not
# just final answer) on a 0-10 scale, given the gold solution as reference.
# Provider-agnostic via litellm; pin the exact frontier model at call time
# (web-search current SOTA before a run, per the SOTA-model-id rule).
from __future__ import annotations

import json
import re

RUBRIC = """You are grading the QUALITY OF MATHEMATICAL REASONING in a candidate solution.
You are given the problem, a gold reference solution, and a candidate solution.

Score the candidate's REASONING (not just its final answer) from 0 to 10:
- 10: fully valid, complete, rigorous reasoning that reaches a correct result.
- 5: partially valid; some correct steps but with a real gap, unjustified jump, or error.
- 0: invalid, incoherent, or empty reasoning (even if the final boxed answer happens to be right).

A correct final answer with hand-wavy or wrong intermediate reasoning must NOT score high.
An answer that is wrong only due to a small arithmetic slip but is otherwise rigorous can score in the middle.

Return STRICT JSON only: {{"score": <float 0-10>, "justification": "<one sentence>"}}.

Problem:
{question}

Gold reference solution:
{gold}

Candidate solution:
{candidate}
"""


def build_prompt(question: str, gold: str, candidate: str) -> str:
    return RUBRIC.format(question=question, gold=gold, candidate=candidate)


def _parse_score(text: str) -> float | None:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return float(json.loads(m.group(0))["score"])
        except Exception:
            pass
    m = re.search(r"score\D{0,5}([0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
    return float(m.group(1)) if m else None


def judge_score(model: str, question: str, gold: str, candidate: str,
                temperature: float = 0.0, seed: int = 0) -> float | None:
    """Return the judge's 0-10 reasoning-quality score, or None on parse failure."""
    import litellm

    litellm.drop_params = True  # e.g. Anthropic doesn't support `seed`; drop it silently
    resp = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": build_prompt(question, gold, candidate)}],
        temperature=temperature, seed=seed, max_tokens=400,
    )
    return _parse_score(resp.choices[0].message.content or "")
