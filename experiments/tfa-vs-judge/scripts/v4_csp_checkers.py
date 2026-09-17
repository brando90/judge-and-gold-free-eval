# Math-Constraint's solver-based verifier, wrapped to match the v4_checkers.py interface.
#
# Third and last checker in the stack:
#   v4_checkers.py     189 math_constraint items, pure-Python predicates
#   v4_mc_checkers.py   67 mathconstruct items,  upstream MathConstruct check()
#   v4_csp_checkers.py  the remainder,           upstream Math-Constraint verify()  <- this file
#
# Unlike the other two, this one does not check a predicate: it re-solves the pycsp3 model with the
# candidate fixed as equality constraints, in a subprocess, and asks whether the result is SAT. That
# needs a JVM. Measured cost is 0.47s mean / 0.6s max per call, uniform across problem types, with
# refutation as fast as confirmation -- an earlier claim that this was prohibitively expensive came
# from mistaking the 60s solver TIMEOUT for a measurement.
#
# EXCLUDED: low_autocorrelation. Its verifier rejects Math-Constraint's OWN stored solution, not just
# ours -- the objective bound appears to be encoded as an optimisation rather than a constraint, so
# re-solving with the sequence fixed returns UNSAT even for a known-good answer. A checker that
# rejects correct answers is the exact failure this paper studies, so those 7 items stay unscored
# rather than being scored wrongly.
import ast
import functools
import json
import os
import sys
import warnings

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.abspath(os.path.join(HERE, "..", "vendor", "math-constraint"))

# Types this file must not score, and why.
EXCLUDE = {"low_autocorrelation"}

# Types where permuting the value labels is a genuine symmetry, so a rejected answer deserves a
# second try in canonical form (see the symmetry retry in check()).
CANON_TYPES = {"graph_k_coloring"}


def _canonical(seq):
    """Relabel values by order of first appearance: [2,0,1,3,2] -> [0,1,2,3,0]."""
    m, out = {}, []
    for v in seq:
        if v not in m:
            m[v] = len(m)
        out.append(m[v])
    return out

_ready = False
_validate = None
_repo = None


def _java_home():
    """pycsp3's solvers are Java. macOS ships a stub `java` that errors unless a JDK is installed,
    so point at a real one rather than trusting PATH."""
    if os.environ.get("JAVA_HOME"):
        return os.environ["JAVA_HOME"]
    import glob
    for pat in ("/opt/homebrew/Cellar/openjdk/*", "/usr/local/Cellar/openjdk/*",
                "/Library/Java/JavaVirtualMachines/*/Contents/Home"):
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


def _boot():
    """Import lazily: this pulls pycsp3 and needs a JVM, and callers that only touch the other two
    checkers should not pay for it or fail without it."""
    global _ready, _validate, _repo
    if _ready:
        return
    jh = _java_home()
    if jh:
        os.environ.setdefault("JAVA_HOME", jh)
        os.environ["PATH"] = os.path.join(jh, "bin") + os.pathsep + os.environ.get("PATH", "")
    sys.path.insert(0, os.path.join(VENDOR, "src"))
    sys.path.insert(0, os.path.join(VENDOR, "stubs"))   # satisfies problems.py's pysms import
    from loguru import logger
    logger.remove()
    from math_constraint.eval import validate_answer
    _validate = validate_answer
    _repo = {}
    for split in ("mathconstraint", "mathconstraint_easy"):
        p = os.path.join(VENDOR, split, "problems.jsonl")
        if os.path.exists(p):
            for line in open(p):
                d = json.loads(line)
                _repo.setdefault(d["name"], d)
    _ready = True


@functools.lru_cache(maxsize=1024)
def _row_for(problem_name):
    _boot()
    return _repo.get(problem_name)


def covers(row):
    """True if this is a math_constraint item we can verify and are willing to trust."""
    if not row["question_id"].startswith("math_constraint"):
        return False
    try:
        d = _row_for(row["problem_name"])
    except Exception:
        return False
    return bool(d) and d.get("problem_type") not in EXCLUDE


def _parse(answer):
    """Our generator stores the extracted \\boxed{} content as a string; the verifier wants a list.
    '[1, 2, 3]' and '1,2,3' must both work -- comparing formatting rather than content is how a
    correct answer gets scored wrong."""
    if not isinstance(answer, str):
        return answer
    s = answer.strip()
    try:
        return json.loads(s)
    except Exception:
        pass
    for cand in (s, "[" + s + "]"):
        try:
            return ast.literal_eval(cand)
        except Exception:
            continue
    return s


def check(row, answer, raw_text=None, with_reason=False):
    """True / False / None for a candidate answer to this item.

    None means ONLY that no verifier covers this item (or the stack failed to load). An answer that
    will not parse, or that the solver refutes, is False -- consistent with v4_checkers.py and
    v4_mc_checkers.py, so that wrong answers stay in the pool as wrong rather than vanishing as
    'undecidable' and inflating the apparent valid rate.
    """
    def out(v, why):
        return (v, why) if with_reason else v

    if not covers(row):
        return out(None, "no_checker")
    try:
        _boot()
        d = _row_for(row["problem_name"])
    except Exception as e:
        return out(None, f"infra:{type(e).__name__}")

    # A model may answer "UNSATISFIABLE" -- the candidate prompt explicitly permits it. Every item
    # in this benchmark carries satisfiable: True, so that is a WRONG answer, not an unverifiable
    # one. Handled here rather than passed to the solver, which reports it as "solver returned
    # UNKNOWN": the same verdict, but a label that reads like verifier failure. 1,006 of the 1,010
    # UNKNOWN verdicts in the pool were exactly this, and the wording cost real time chasing a
    # phantom reversal of the CSP solve-rate result.
    if "unsat" in str(answer).lower().replace(" ", ""):
        return out(False, "claimed_unsat_but_item_is_sat")

    parsed = _parse(answer)
    if parsed is None or parsed == "":
        return out(False, "noparse")
    try:
        # every item in this benchmark is satisfiable, so the claimed-SAT flag is always True;
        # validate_answer normalises the shape and then calls verify()
        res = _validate(d, True, parsed)
    except Exception as e:
        return out(False, f"raised:{type(e).__name__}")
    if res.get("solution_correct"):
        return out(True, "ok")

    # Symmetry retry. The pycsp3 colouring model carries value-precedence (symmetry-breaking)
    # constraints, so it rejects a PROPER colouring whose colour labels are permuted: [2,0,1,3,...]
    # is refused where [0,1,2,3,...] is accepted. Verified on this benchmark: all 52 rejected
    # graph_k_coloring answers are proper colourings within k when checked directly against the
    # edge list, and all 52 are accepted after relabelling.
    #
    # Safe because relabelling only renames colour classes -- it preserves the partition, so an
    # improper colouring stays improper and a wrong answer cannot be laundered into a right one.
    # Restricted to types where colour identity genuinely is a symmetry.
    if d.get("problem_type") in CANON_TYPES and isinstance(parsed, list) and parsed:
        try:
            if _validate(d, True, _canonical(parsed)).get("solution_correct"):
                return out(True, "ok:canonical-relabel")
        except Exception:
            pass
    return out(False, f"rejected:{str(res.get('details'))[:60]}")
