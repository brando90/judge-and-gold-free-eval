# TLDR: No-GPU/no-API fakes so the FULL orchestration (data -> TFA scoring ->
# correctness -> judge -> JSONL -> crux report) is smoke-testable on CPU/CI.
# Plants a known signal (TFA and judge both track a latent quality, independent
# of boxed-correct) so `analyze_crux.py` should return GREEN -- i.e. the pipeline
# can actually detect a real partial correlation. Real code paths exercised:
# score_tfa, is_correct, JSONL schema, analyze_crux aggregation + verdict.
from __future__ import annotations

import random

from tfa.core import PosRecord
from tfa.data import Problem


def fake_problems(n: int, seed: int = 0) -> list[Problem]:
    rng = random.Random(seed)
    out = []
    for i in range(n):
        latent = rng.gauss(0, 1)  # hidden "reasoning quality" for this problem
        out.append(Problem(
            id=f"toy-{i}", question=f"toy problem {i}", gold_solution="x " * 30,
            gold_answer=str(i), dataset="toydry", meta={"latent": latent},
        ))
    return out


def fake_tfa_records(latent: float, capability: float, seed: int) -> list[PosRecord]:
    """Build gold-token records whose argmax-hit-rate reflects latent quality +
    model capability, so score_tfa() sees real variance."""
    rng = random.Random(seed)
    n = 30
    hit_p = 1 / (1 + pow(2.718, -(latent + capability)))  # sigmoid in (0,1)
    recs = []
    for _ in range(n):
        hit = rng.random() < hit_p
        recs.append(PosRecord(gold_id=1, top1_id=1 if hit else 2,
                              gold_logprob=-abs(rng.gauss(0, 1)), is_content=True))
    return recs


def fake_free_and_judge(latent: float, capability: float, gold_answer: str, seed: int):
    """Return (free_text, boxed_correct, judge_score).

    judge tracks latent quality (+noise); correctness is a SEPARATE coin so the
    planted partial(TFA, judge | correct) is nonzero.
    """
    rng = random.Random(seed + 7)
    correct = 1 if rng.random() < 1 / (1 + pow(2.718, -capability)) else 0
    boxed = gold_answer if correct else str(int(gold_answer) + 1)
    free = f"...reasoning... \\boxed{{{boxed}}}"
    judge = max(0.0, min(10.0, 5 + 2.5 * (latent + capability) + rng.gauss(0, 1)))
    return free, correct, judge
