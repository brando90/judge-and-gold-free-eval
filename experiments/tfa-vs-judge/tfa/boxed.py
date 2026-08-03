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
    # Predictions are always prompted for \boxed{}, so try that first regardless of
    # dataset; fall back to the GSM8K `#### N` form (used by GSM8K gold solutions).
    b = extract_boxed(text)
    if b is not None:
        return b
    if dataset.lower().startswith("gsm8k"):
        g = extract_gsm8k_answer(text)
        if g is not None:
            return g
        # Robustness patch (2026-08): many models answer "The answer is 23." with
        # neither \boxed{} nor `#### N`. Without these fallbacks, correct answers
        # were scored 0, the dominant oracle-bug mode found by the oversight study
        # (60/74 externally validated flags). Order: explicit answer phrase, then
        # last number in the text.
        m = re.findall(r"(?:answer|result|total|cost)\s*(?:is|:|=|of)\s*\$?([-+]?[0-9][0-9,]*\.?[0-9]*)",
                       text, re.IGNORECASE)
        if m:
            return m[-1].replace(",", "").strip()
        m = re.findall(r"[-+]?[0-9][0-9,]*\.?[0-9]*", text)
        if m:
            return m[-1].replace(",", "").strip()
    return None


def _normalize(s: str) -> str:
    s = s.strip().strip("$").replace(" ", "")
    s = s.replace(r"\left", "").replace(r"\right", "")
    s = s.replace(r"\!", "").replace(r"\,", "")
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1]
    s = s.replace(",", "").rstrip(".")
    # numeric folding: "6.00" == "6"
    try:
        f = float(s)
        return str(int(f)) if f == int(f) else str(f)
    except ValueError:
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

        # Wrap in $...$ so Math-Verify uses its LaTeX parser; without delimiters it
        # mis-parses many non-scalar answers (fractions, tuples, symbolic), causing
        # both false negatives (identical answers rejected) and false positives
        # (parametric answers collapsed to a trivial value).
        if verify(parse(f"${gold}$"), parse(f"${pred}$")):
            return True
        return _normalize(pred) == _normalize(gold)
    except Exception:
        return _normalize(pred) == _normalize(gold)


def is_correct(free_gen: str, gold_answer: str, dataset: str) -> int:
    """1 if the free-generated solution's final answer matches gold, else 0."""
    pred = extract_final_answer(free_gen, dataset)
    return int(answers_equivalent(pred, gold_answer))
