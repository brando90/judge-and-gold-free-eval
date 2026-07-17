# TLDR: Correlation analysis that produces the go/no-go number for the crux
# experiment. The decisive quantity is the PARTIAL correlation rho(TFA, judge |
# boxed-correct): does TFA carry reasoning-quality signal beyond the free
# final-answer-correctness bit? Also provides raw Spearman/Pearson, per-stratum
# (correct vs wrong) correlations, and bootstrap CIs.
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
from scipy import stats


@dataclass
class CorrCI:
    rho: float
    lo: float
    hi: float
    n: int
    method: str


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3 or np.all(x == x[0]) or np.all(y == y[0]):
        return float("nan")
    return float(stats.spearmanr(x, y).statistic)


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3 or np.all(x == x[0]) or np.all(y == y[0]):
        return float("nan")
    return float(stats.pearsonr(x, y).statistic)


def bootstrap_corr(
    x: np.ndarray, y: np.ndarray, method: str = "spearman",
    n_boot: int = 10_000, seed: int = 0, ci: float = 0.95,
) -> CorrCI:
    """Bootstrap CI for a correlation by resampling paired items with replacement."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    f = _spearman if method == "spearman" else _pearson
    point = f(x, y)
    rng = np.random.default_rng(seed)
    n = len(x)
    boots = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        boots[b] = f(x[idx], y[idx])
    boots = boots[~np.isnan(boots)]
    lo, hi = np.quantile(boots, [(1 - ci) / 2, 1 - (1 - ci) / 2]) if len(boots) else (float("nan"), float("nan"))
    return CorrCI(rho=point, lo=float(lo), hi=float(hi), n=n, method=method)


def partial_spearman(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    """Spearman partial correlation of x,y controlling for z.

    Rank-transform, then apply the standard first-order partial-correlation
    formula. For binary z (e.g., boxed-correct in {0,1}) this equals the
    covariance-adjusted within-strata association.
    """
    x = stats.rankdata(x); y = stats.rankdata(y); z = stats.rankdata(z)
    rxy = np.corrcoef(x, y)[0, 1]
    rxz = np.corrcoef(x, z)[0, 1]
    ryz = np.corrcoef(y, z)[0, 1]
    denom = np.sqrt((1 - rxz**2) * (1 - ryz**2))
    if denom == 0 or np.isnan(denom):
        return float("nan")
    return float((rxy - rxz * ryz) / denom)


def bootstrap_partial(
    x: np.ndarray, y: np.ndarray, z: np.ndarray,
    n_boot: int = 10_000, seed: int = 0, ci: float = 0.95,
) -> CorrCI:
    x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
    point = partial_spearman(x, y, z)
    rng = np.random.default_rng(seed)
    n = len(x)
    boots = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        boots[b] = partial_spearman(x[idx], y[idx], z[idx])
    boots = boots[~np.isnan(boots)]
    lo, hi = np.quantile(boots, [(1 - ci) / 2, 1 - (1 - ci) / 2]) if len(boots) else (float("nan"), float("nan"))
    return CorrCI(rho=point, lo=float(lo), hi=float(hi), n=n, method="partial_spearman")


@dataclass
class CruxReport:
    """The one-screen answer to 'does TFA track the judge beyond correctness?'"""
    tfa_vs_judge: CorrCI            # item-level rho(TFA, judge)
    tfa_vs_correct: CorrCI         # item-level rho(TFA, boxed-correct)  [the free signal]
    judge_vs_correct: CorrCI       # how much the judge itself is just re-reading correctness
    tfa_vs_judge_partial: CorrCI   # DECISIVE: rho(TFA, judge | correct)
    tfa_vs_judge_within_correct: CorrCI   # rho on correct-only items
    tfa_vs_judge_within_wrong: CorrCI     # rho on wrong-only items
    verdict: str

    def to_dict(self) -> dict:
        d = {k: (asdict(v) if isinstance(v, CorrCI) else v) for k, v in self.__dict__.items()}
        return d


def crux_report(
    tfa: np.ndarray, judge: np.ndarray, correct: np.ndarray,
    n_boot: int = 10_000, seed: int = 0,
) -> CruxReport:
    """Compute the decision-grade correlations for the fast crux experiment.

    tfa:     per-item TFA-argmax (teacher-forced on gold).
    judge:   per-item frontier-judge reasoning-quality score (on the model's free-gen trace).
    correct: per-item boxed-answer correctness in {0,1} (the free anchor correlate).
    """
    tfa = np.asarray(tfa, float); judge = np.asarray(judge, float); correct = np.asarray(correct, float)
    cmask = correct == 1
    wmask = correct == 0

    partial = bootstrap_partial(tfa, judge, correct, n_boot=n_boot, seed=seed)

    def _sub(mask):
        if mask.sum() >= 5:
            return bootstrap_corr(tfa[mask], judge[mask], n_boot=n_boot, seed=seed)
        return CorrCI(float("nan"), float("nan"), float("nan"), int(mask.sum()), "spearman")

    # Decision rule (objective, stated up front in the plan):
    #  - GREEN  : partial rho CI excludes ~0 on the positive side  -> TFA adds process signal.
    #  - NEGATIVE: partial rho CI includes 0                        -> TFA ~ cheaper exact-match.
    if not np.isnan(partial.lo) and partial.lo > 0.05:
        verdict = "GREEN: TFA carries reasoning-quality signal beyond boxed correctness."
    elif not np.isnan(partial.hi) and partial.hi < 0.05:
        verdict = "NEGATIVE: TFA does not add signal beyond boxed correctness (cheaper exact-match)."
    else:
        verdict = "INCONCLUSIVE: partial-correlation CI straddles 0; need more items/models."

    return CruxReport(
        tfa_vs_judge=bootstrap_corr(tfa, judge, n_boot=n_boot, seed=seed),
        tfa_vs_correct=bootstrap_corr(tfa, correct, n_boot=n_boot, seed=seed),
        judge_vs_correct=bootstrap_corr(judge, correct, n_boot=n_boot, seed=seed),
        tfa_vs_judge_partial=partial,
        tfa_vs_judge_within_correct=_sub(cmask),
        tfa_vs_judge_within_wrong=_sub(wmask),
        verdict=verdict,
    )
