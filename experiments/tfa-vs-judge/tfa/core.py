# TLDR: Backend-agnostic Teacher-Forced Accuracy (TFA) scoring from per-position
# logprob records, so the correctness-critical metric logic is unit-testable
# without a GPU. vLLM and HF backends both emit `PosRecord`s; this module turns
# them into TFA-argmax, TFA-logprob (mean gold logprob), and BPC.
#
# TFA (Putnam-AXIOM, Gulati et al. ICML 2025, arXiv:2508.08292):
#   TFA(model, prompt, gold) = (1/N) * sum_i 1[ argmax_v p(v | prompt, gold_<i) == gold_i ]
# We score only the N gold-solution tokens (prompt positions are masked out).
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class PosRecord:
    """One teacher-forced gold position.

    gold_id:       the ground-truth (gold) token id the model was forced to consume.
    top1_id:       the model's argmax token id at this position (over the full vocab).
    gold_logprob:  natural-log prob the model assigned to gold_id at this position.
                   None only if the backend could not recover it (should not happen
                   when the backend always includes the forced token's logprob).
    is_content:    whether this position is a "content" token (for the shortcut
                   control / TFA-content variant). Default True = score everything.
    """

    gold_id: int
    top1_id: int
    gold_logprob: float | None
    is_content: bool = True


@dataclass(frozen=True)
class TFAResult:
    n: int                    # number of scored positions
    tfa_argmax: float         # canonical TFA: fraction of positions where argmax == gold
    tfa_logprob: float        # mean gold-token natural-log prob (higher = better)
    bpc_bits: float           # bits per token: -mean(log2 gold_prob) (lower = better)
    tfa_argmax_content: float | None  # TFA-argmax over content tokens only (None if no content mask)
    n_content: int


def _safe_mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def score_tfa(records: list[PosRecord]) -> TFAResult:
    """Compute the TFA family from per-position records for a single (model, problem).

    Deterministic and pure: given identical records, returns identical numbers.
    """
    if not records:
        return TFAResult(0, float("nan"), float("nan"), float("nan"), None, 0)

    argmax_hits = [1.0 if r.gold_id == r.top1_id else 0.0 for r in records]
    gold_lps = [r.gold_logprob for r in records if r.gold_logprob is not None]

    content = [r for r in records if r.is_content]
    has_content_mask = any(not r.is_content for r in records)
    content_argmax = (
        _safe_mean([1.0 if r.gold_id == r.top1_id else 0.0 for r in content])
        if has_content_mask
        else None
    )

    mean_lp = _safe_mean(gold_lps)
    # bits per token = -(1/N) sum log2 p = -mean_lp / ln(2)
    bpc = (-mean_lp / math.log(2)) if gold_lps else float("nan")

    return TFAResult(
        n=len(records),
        tfa_argmax=_safe_mean(argmax_hits),
        tfa_logprob=mean_lp,
        bpc_bits=bpc,
        tfa_argmax_content=content_argmax,
        n_content=len(content),
    )


def top1_from_topk(topk: dict[int, float]) -> int:
    """Return the argmax token id from a {token_id: logprob} top-k map.

    vLLM `prompt_logprobs` ranks over the full vocab, so the max-logprob entry in
    the returned top-k is the true argmax at that position.
    """
    if not topk:
        raise ValueError("empty top-k map; cannot determine argmax")
    return max(topk.items(), key=lambda kv: kv[1])[0]
