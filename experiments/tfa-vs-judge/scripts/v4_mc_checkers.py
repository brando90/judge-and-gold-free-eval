# Upstream MathConstruct checkers, wrapped to match the v4_checkers.py interface.
#
# Covers the 67 `mathconstruct` items in final_mathrefbench.jsonl, which our own checkers do not
# touch (they handle `math_constraint` only). Together: 256 of 324 items decidable without the
# answer bank.
#
# Validated against the bank exactly as our own checkers were: 459/459 stored answers accepted,
# 67/67 items, zero failures. See vendor/PROVENANCE.md for the pinned commit.
#
# The one trap, which cost a full wrong run: do NOT pass the stored `answer` field. It carries JSON
# artifacts -- big integers serialized as strings inside lists, fractions as "a/b". Pass the model's
# raw reply or the `rendered_answer` LaTeX; upstream's parser wants \boxed{} text.
import functools
import importlib
import inspect
import os
import sys
import warnings

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "..", "vendor", "mathconstruct", "src")

_ready = False


def _boot():
    """Import upstream lazily: it pulls sympy/scipy, and callers that only touch math_constraint
    items should not pay for that."""
    global _ready, _Problem
    if _ready:
        return
    sys.path.insert(0, os.path.abspath(VENDOR))
    from loguru import logger
    logger.remove()  # upstream logs a warning per rejected answer; we record verdicts ourselves
    from math_construct.problems.problem import Problem
    _Problem = Problem
    _ready = True


@functools.lru_cache(maxsize=1)
def _dirs():
    root = os.path.abspath(os.path.join(VENDOR, "math_construct", "problems"))
    ds = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)) and not d.startswith("__")]
    return sorted(ds, key=len, reverse=True)  # longest first: 'imo_shortlist' before 'imo'


def module_for(problem_name):
    """'bmo-shortlist-2008-n1' -> 'math_construct.problems.bmo_shortlist.problem_2008_n1'.
    Longest-prefix match against the real directory names, so 'imo_shortlist' is not read as 'imo'."""
    n = problem_name.replace("-", "_")
    for d in _dirs():
        if n.startswith(d + "_"):
            return f"math_construct.problems.{d}.problem_{n[len(d) + 1:]}"
    return None


@functools.lru_cache(maxsize=512)
def _cls(mod):
    m = importlib.import_module(mod)
    for _, o in inspect.getmembers(m, inspect.isclass):
        if issubclass(o, _Problem) and o is not _Problem and o.__module__ == mod:
            return o
    return None


def covers(row):
    """True if this row is a mathconstruct item we can check."""
    if not row["question_id"].startswith("mathconstruct"):
        return False
    _boot()
    mod = module_for(row["problem_name"])
    if mod is None:
        return False
    try:
        return _cls(mod) is not None
    except Exception:
        return False


def check(row, answer, raw_text=None):
    """True / False / None for a candidate answer to this item.

    Prefer `raw_text` (the model's full reply) -- upstream pulls the LAST \\boxed{} out of it,
    which is what its parser and list-depth matching expect. `answer` is re-wrapped as a fallback.
    None means 'cannot decide' (not our item, import failed, or the answer would not parse) and is
    never to be read as 'incorrect'.
    """
    if not covers(row):
        return None
    try:
        cls = _cls(module_for(row["problem_name"]))
        # Every benchmark item is an /original. get_original() also sidesteps stored parameters
        # that arrive as strings, e.g. {'n': '10000000000000000000'}.
        prob = (cls.get_original() if row["question_id"].endswith("/original")
                else cls(**row["original_parameters"]))
        text = raw_text if raw_text else str(answer)
        if "\\boxed{" not in text:
            text = "\\boxed{" + str(answer) + "}"
        parsed = prob.parse(text)
        if parsed is None:
            return None
        out = prob.check(parsed)
        return bool(out[0]) if isinstance(out, tuple) else bool(out)
    except Exception:
        return None
