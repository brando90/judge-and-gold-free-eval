# TLDR: Corrupted references for contrastive TFA (idea 3). Contrastive TFA =
# TFA(correct gold) - TFA(corrupted gold): a good reasoner should predict the
# correct gold MORE than a length-matched corrupted one, and the difference
# cancels the gold-length/formulaicness baseline that confounds raw TFA.
from __future__ import annotations

import random
import re

from tfa.boxed import extract_boxed


def corrupt_answer(gold: str) -> str:
    """Swap the final \\boxed{...} to a wrong (but plausible) value. Length ~preserved.

    Tests whether the model prefers the correct conclusion; nearly identical text
    except the answer region, so length/formulaic baseline is held fixed.
    """
    ans = extract_boxed(gold)
    if ans is None:
        return gold
    m = re.fullmatch(r"\s*(-?\d+)\s*", ans)
    if m:
        wrong = str(int(m.group(1)) + 1)
    else:
        mf = re.fullmatch(r"\s*(-?\d+)/(\d+)\s*", ans)  # simple fraction a/b -> (a+1)/b
        wrong = f"{int(mf.group(1)) + 1}/{mf.group(2)}" if mf else (ans + " + 1")
    # replace only the last boxed occurrence's content
    idx = gold.rfind(ans)
    return gold[:idx] + wrong + gold[idx + len(ans):] if idx != -1 else gold


def corrupt_shuffle(gold: str, seed: int = 0) -> str:
    """Shuffle the middle reasoning lines, keeping the first/last line fixed. Length
    is exactly preserved; only step ordering (logical coherence) is destroyed.
    A coherent reasoner should predict the correctly-ordered gold better."""
    lines = [ln for ln in gold.split("\n")]
    if len(lines) < 4:
        # fall back to sentence-level shuffle for single-block solutions
        parts = re.split(r"(?<=[.])\s+", gold.strip())
        if len(parts) < 4:
            return gold
        mid = parts[1:-1]
        random.Random(seed).shuffle(mid)
        return " ".join([parts[0], *mid, parts[-1]])
    mid = lines[1:-1]
    random.Random(seed).shuffle(mid)
    return "\n".join([lines[0], *mid, lines[-1]])
