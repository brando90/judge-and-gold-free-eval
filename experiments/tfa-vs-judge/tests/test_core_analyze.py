# TLDR: CPU-only unit tests for the correctness-critical pieces (TFA scoring +
# the partial-correlation decision logic). No GPU/torch/vLLM needed; run with
# `uv run --with numpy --with scipy --with pytest pytest`.
import math

import numpy as np

from tfa.core import PosRecord, score_tfa, top1_from_topk
from tfa.analyze import crux_report, partial_spearman


def test_tfa_argmax_and_logprob_hand_computed():
    recs = [
        PosRecord(gold_id=1, top1_id=1, gold_logprob=math.log(0.5), is_content=True),
        PosRecord(gold_id=2, top1_id=9, gold_logprob=math.log(0.25), is_content=False),
        PosRecord(gold_id=3, top1_id=3, gold_logprob=math.log(0.8), is_content=True),
        PosRecord(gold_id=4, top1_id=9, gold_logprob=math.log(0.1), is_content=True),
    ]
    r = score_tfa(recs)
    assert r.n == 4
    assert r.tfa_argmax == 0.5                      # hits [1,0,1,0]
    assert r.tfa_argmax_content == 2 / 3            # content hits [1,1,0]
    mean_lp = (math.log(0.5) + math.log(0.25) + math.log(0.8) + math.log(0.1)) / 4
    assert abs(r.tfa_logprob - mean_lp) < 1e-12
    assert abs(r.bpc_bits - (-mean_lp / math.log(2))) < 1e-12


def test_top1_from_topk_ranks_over_returned_map():
    assert top1_from_topk({7: -2.0, 3: -0.1, 9: -5.0}) == 3


def test_empty_records_are_nan_not_crash():
    r = score_tfa([])
    assert r.n == 0 and math.isnan(r.tfa_argmax)


def test_partial_correlation_zero_when_signal_is_pure_mediation():
    # tfa and judge each track correctness with INDEPENDENT residual noise, so
    # once we control for correctness their association vanishes: partial ~ 0.
    # With enough items the CI is tight enough to *conclusively* say NEGATIVE
    # (fewer items would correctly yield INCONCLUSIVE -- see docstring of crux_report).
    rng = np.random.default_rng(0)
    n = 3000
    correct = rng.integers(0, 2, n).astype(float)
    tfa = correct + rng.normal(0, 0.6, n)           # correlates with correct, not with judge's residual
    judge = correct + rng.normal(0, 0.6, n)
    rep = crux_report(tfa, judge, correct, n_boot=2000, seed=1)
    assert abs(rep.tfa_vs_judge_partial.rho) < 0.1
    assert rep.verdict.startswith("NEGATIVE")


def test_partial_correlation_positive_when_tfa_adds_process_signal():
    # judge tracks an underlying quality that TFA also reflects, independent of
    # whether the boxed answer is correct => partial > 0 => GREEN verdict.
    rng = np.random.default_rng(2)
    n = 600
    quality = rng.normal(0, 1, n)                    # latent reasoning quality
    correct = (rng.normal(0, 1, n) > 0).astype(float)  # correctness ~ independent of quality
    tfa = quality + rng.normal(0, 0.3, n)
    judge = quality + rng.normal(0, 0.3, n)
    rep = crux_report(tfa, judge, correct, n_boot=2000, seed=3)
    assert rep.tfa_vs_judge_partial.rho > 0.3
    assert rep.tfa_vs_judge_partial.lo > 0.05
    assert rep.verdict.startswith("GREEN")


def test_partial_spearman_matches_manual_formula():
    rng = np.random.default_rng(5)
    x = rng.normal(size=200); y = rng.normal(size=200); z = rng.normal(size=200)
    # sanity: partial of x with a y built to depend on x and z recovers positive assoc
    y2 = 0.7 * x + 0.7 * z + rng.normal(0, 0.1, size=200)
    assert partial_spearman(x, y2, z) > 0.5
