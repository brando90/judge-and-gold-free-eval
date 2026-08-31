# Exemplar-vs-specification experiment on code.
# INTERNAL REGISTRATION: this header pins the design, population, estimator and predictions, and
# the file is git-committed BEFORE any exemplar score exists. No OSF post (registration hold).
#
# The question, and why it may restate the paper's central rule. Every reference this paper has
# shown a judge is an EXEMPLAR: one valid answer out of several. Companion A's code condition is
# different in kind, showing the judge the TEST ASSERTIONS, which are a SPECIFICATION: not an
# answer at all, but the criteria an answer must satisfy. That difference reconciles an apparent
# contradiction between the two papers, since A reports a reference HELPING on code (which has
# many valid implementations) while this paper reports references HARMING under multiplicity.
# A specification cannot be anchored on, because there is nothing to match; consulting it IS
# verification. The hypothesis, recorded pre-data in registration.md, is that anchoring is caused
# by being shown one valid exemplar and that answer multiplicity governs only its cost.
#
# Code is additionally the untested THIRD REGIME. In our math pools the model emits a derivation
# ending in a separable boxed answer, and the judge anchors on that answer token; holding it fixed
# and varying the derivation moves scores 20-400x less (H-METHOD). In code there IS no separable
# answer: the artifact IS the answer, and many artifacts are valid. Whether anchoring collapses
# without an answer token to match, or transfers to structural resemblance, is unknown.
#
# Design. Frozen MBPP pool (378 items x 64 Qwen2.5-7B samples, oracle labels already computed by
# the EvalPlus-augmented test suite). Three conditions on the SAME samples and judges:
#   blind        - no reference                              [ALREADY RUN, companion A: noref]
#   specification- the example_test assertions                [ALREADY RUN, companion A: ref]
#   exemplar     - the MBPP canonical solution                [NEW: this experiment]
# Judges: Qwen2.5-7B and Qwen2.5-14B (both already have blind and specification arms), rubrics a/b.
#
# POPULATION RESTRICTION, verified not assumed. MBPP's canonical solutions were executed against
# our own test field: 60 of 378 FAIL it, because MBPP's reference code was written against the
# weaker original assertions while our oracle uses the EvalPlus-augmented suite (a serial recheck
# at 30s confirmed 60 of 61 flagged, so the count is execution-stable). Showing the judge a
# reference our own oracle scores INVALID would be a different and confounded manipulation, so
# the exemplar arm runs only on the 318 items whose canonical solution passes. The blind and
# specification arms are re-read on the same 318 items so all three conditions are paired.
#
# REGISTERED PREDICTIONS:
#   P-EX1 (the discriminating test): the exemplar condition's inflation over blind is POSITIVE
#     with a 95% item-bootstrap CI excluding zero, while the specification condition's is not.
#     Confirmation would establish that the harm attaches to the reference's TYPE rather than to
#     the task's answer structure, and the paper's boundary rule should be restated accordingly.
#   P-EX2 (anchoring readout): under the exemplar condition, valid samples textually closer to
#     the canonical solution score higher than equally valid samples that are far from it
#     (item-level correlation between similarity-to-reference and judge score, positive, CI
#     excluding zero). Under blind, that correlation's CI contains zero.
#   P-EX3 (regime check, directional): the exemplar effect on code is SMALLER than the answer
#     anchoring measured on the math pools (margin +4.06 to +5.32), because no separable answer
#     token exists for the judge to match on.
#   A null on P-EX1 is fully informative and must be reported as prominently as a confirmation:
#     it would mean exemplar references are safe where the artifact is the answer, confining this
#     paper's warning to tasks with a separable answer.
#
# Run from experiments/tfa-vs-judge:  python3 scripts/build_code_exemplar.py
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

from datasets import load_dataset

TASKS = "runs/bon_mbpp_tasks.jsonl"
OUT = "runs/mbpp_exemplar_tasks.jsonl"

ours = [json.loads(l) for l in open(TASKS)]
canon = {}
for cfg in ("full", "sanitized"):
    d = load_dataset("mbpp", cfg)
    for sp in d:
        for r in d[sp]:
            if r.get("code"):
                canon[str(r["task_id"])] = r["code"]


def run_src(src, timeout=30.0):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(src)
        p = f.name
    try:
        return subprocess.run([sys.executable, p], capture_output=True, timeout=timeout).returncode == 0
    except Exception:
        return False
    finally:
        os.unlink(p)


def check(o):
    tid = re.sub(r"\D", "", str(o["problem_id"]))
    code = canon.get(tid)
    if not code:
        return None
    t = o["test"] if isinstance(o["test"], str) else "\n".join(o["test"])
    return (o, code, run_src(code + "\n" + t + "\n"))


with ThreadPoolExecutor(8) as ex:
    res = [r for r in ex.map(check, ours) if r]

kept = [(o, c) for o, c, ok in res if ok]
dropped = [o["problem_id"] for o, _, ok in res if not ok]
with open(OUT, "w") as f:
    for o, c in kept:
        row = dict(o)
        row["canonical_solution"] = c
        f.write(json.dumps(row) + "\n")

print(f"[code-exemplar] {len(kept)}/{len(ours)} items kept (canonical passes our oracle)")
print(f"  dropped {len(dropped)} whose canonical solution fails the EvalPlus-augmented suite")
print(f"  wrote {OUT}")
assert len(kept) >= 300, "unexpectedly few usable items"
