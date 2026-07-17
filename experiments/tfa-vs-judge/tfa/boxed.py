# TLDR: Boxed / final-answer extraction and correctness scoring. Correctness is
# the FREE "anchor correlate" that TFA must beat to justify itself. Extraction is
# regex-based and unit-tested on CPU; equivalence uses the `math_verify` library
# when available (SNAP), falling back to normalized string match otherwise.
from __future__ import annotations

import re


def extract_boxed(text: str) -> str | None:
    r"""Extract the content of the LAST \boxed{...} in `text` (brace-balanced)."""
    idx = text.rfind(r"\boxed")
    if idx == -1:
        return None
    i = idx + len(r"\boxed")
    while i < len(text) and text[i] != "{":
        if not text[i].isspace():
            return None
        i += 1
    if i >= len(text):
        return None
    depth = 0
    start = i
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : j].strip()
    return None


def extract_gsm8k_answer(text: str) -> str | None:
    """GSM8K gold answers end with `#### <number>`; free-gen may too."""
    m = re.findall(r"####\s*([-+]?[0-9][0-9,]*\.?[0-9]*)", text)
    if m:
        return m[-1].replace(",", "").strip()
    return None


def extract_final_answer(text: str, dataset: str) -> str | None:
    if dataset.lower().startswith("gsm8k"):
        return extract_gsm8k_answer(text)
    return extract_boxed(text)


def _normalize(s: str) -> str:
    s = s.strip().strip("$").replace(" ", "")
    s = s.replace(r"\left", "").replace(r"\right", "")
    s = s.replace(r"\!", "").replace(r"\,", "")
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1]
    return s


def answers_equivalent(pred: str | None, gold: str | None) -> bool:
    """True if pred and gold denote the same answer.

    Prefers `math_verify` (symbolic, handles LaTeX/algebraic equivalence); falls
    back to normalized string equality when the library is unavailable.
    """
    if pred is None or gold is None:
        return False
    try:
        from math_verify import parse, verify  # type: ignore

        return bool(verify(parse(gold), parse(pred)))
    except Exception:
        return _normalize(pred) == _normalize(gold)


def is_correct(free_gen: str, gold_answer: str, dataset: str) -> int:
    """1 if the free-generated solution's final answer matches gold, else 0."""
    pred = extract_final_answer(free_gen, dataset)
    return int(answers_equivalent(pred, gold_answer))
