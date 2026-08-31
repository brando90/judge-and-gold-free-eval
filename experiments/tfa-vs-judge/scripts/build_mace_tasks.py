# MACE task-pool builder for the domain-diversity extension.
# INTERNAL REGISTRATION: this header pins the population, the oracle, the sampling seed, and the
# predictions, and the file is git-committed BEFORE any MACE generation exists. No OSF post.
#
# Why MACE, and why these domains. Every constructive result in this paper so far rests on task
# pools we built ourselves (the 120-task replication pool, the 75-task k-stratified pool, the
# synthetic grid); the one third-party substrate, RewardBench-2 Ties, was shown to carry ~90%
# unreliable invalid-labels. MACE (arXiv:2602.07842) supplies third-party questions with
# third-party ground truth and answer cardinality fixed by construction at k in {1,2,4,6}.
# Two audits, both run before this file was written, determine which domains enter:
#   - Math: 2000/2000 questions have exactly correct AND exactly complete answer sets, verified
#     by direct computation over the five computable kinds. Exact oracle, but arithmetic.
#   - Entity domains: an independent enumeration audit (12 multi-valid questions per domain)
#     gives absent-from-list rates of River 2.3%, Language 8.1%, Region 30.8%, Office 33.3%,
#     Award 43.5%. River and Language pass; the other three are EXCLUDED, not patched.
# The extension therefore runs NON-MATHEMATICAL first (River, Language), with Math as a
# label-noise control, so any divergence is attributable to substrate rather than oracle quality.
#
# Population (pinned): River and Language, all four cardinalities k in {1,2,4,6}, 25 items per
# (domain, k) cell = 200 non-math items; plus Math, 25 per k = 100 items as the control.
# Sampling seed random.Random(20260901), fixed here before any item is drawn.
# Reference: one valid answer per item, drawn by the same seeded RNG, mirroring every other pool.
#
# Oracle. Entity domains: loose-normalized membership in the shipped valid set (the Ties-style
# checker), whose incompleteness is bounded by the audit above and whose errors fall on the
# NON-matching side, shrinking measured margins rather than inflating them. Math: exact
# computation over the stated kind and range, no list needed.
#
# REGISTERED PREDICTIONS (committed before any MACE generation):
#   P-MC1 (the k-step, non-math): on River+Language, the per-item paired referenced-minus-blind
#     inflation delta is larger at k>1 than at k=1, with a 95% item-bootstrap CI on the step
#     excluding zero, for both judges (Qwen2.5-7B, phi-4). This is the paper's central claim
#     tested on third-party, non-mathematical tasks for the first time.
#   P-MC2 (anchoring margin, non-math): the referenced anchoring margin at k>1 is positive with
#     a CI excluding zero, and the blind margin's CI contains zero.
#   P-MC3 (substrate control): the k-step on MACE-Math has the same sign as on River+Language.
#     A divergence would indicate the entity oracle's residual noise is material and would be
#     reported as such.
#   A null on P-MC1 is the most consequential outcome available: it would confine every
#   constructive result in this paper to task pools of our own construction, and must be
#   reported as prominently as a confirmation.
#
# Run from experiments/tfa-vs-judge:  python3 scripts/build_mace_tasks.py
import ast
import json
import math
import random
import re

from datasets import load_dataset
from sympy import isprime

SEED = 20260901
PER_CELL = 25
KS = [1, 2, 4, 6]
NONMATH = ["River", "Language"]
rng = random.Random(SEED)


def parse_ref(ref):
    if isinstance(ref, (list, tuple)):
        return [str(x) for x in ref]
    try:
        v = ast.literal_eval(ref)
        return [str(x) for x in v] if isinstance(v, (list, tuple)) else [str(v)]
    except Exception:
        return [str(ref)]


def is_square(n):
    r = math.isqrt(n)
    return r * r == n


def is_cube(n):
    r = round(n ** (1 / 3))
    return any((r + d) ** 3 == n for d in (-1, 0, 1))


_F = set()
_a, _b = 0, 1
while _a < 10 ** 13:
    _F.add(_a)
    _a, _b = _b, _a + _b


def is_tri(n):
    m = math.isqrt(8 * n + 1)
    return m * m == 8 * n + 1


MATH_KIND = {"prime": isprime, "square": is_square, "cube": is_cube,
             "fibonacci": lambda n: n in _F, "triangular": is_tri}

rows = []
for dom in NONMATH + ["Math"]:
    d = load_dataset("fzzh/MACE", dom)["train"]
    by_k = {k: [] for k in KS}
    for r in d:
        a = parse_ref(r["Reference"])
        if len(a) in by_k:
            by_k[len(a)].append((r["Question"], a))
    for k in KS:
        pool = by_k[k]
        take = rng.sample(pool, min(PER_CELL, len(pool)))
        for i, (q, ans) in enumerate(take):
            params = {"fam": f"mace_{dom.lower()}", "domain": dom}
            if dom == "Math":
                m = re.search(r"Name a (\w+) number between (\d+) and (\d+)", q)
                if not m:
                    continue
                kind, lo, hi = m.group(1), int(m.group(2)), int(m.group(3))
                # exactness assertion: the shipped set must equal the computed truth
                truth = {str(n) for n in range(lo, hi + 1) if MATH_KIND[kind](n)}
                assert truth == set(ans), f"MACE-Math mismatch on {q!r}"
                params.update(kind=kind, lo=lo, hi=hi)
            rows.append(dict(problem_id=f"mace/{dom.lower()}-k{k}-{i}",
                             problem=q, question=q, params=params, k=k,
                             ref_answer=rng.choice(ans), valid_answers=ans))

with open("runs/mace_tasks.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")

import collections
cnt = collections.Counter((r["params"]["domain"], r["k"]) for r in rows)
print(f"[mace] wrote {len(rows)} items -> runs/mace_tasks.jsonl")
for dom in NONMATH + ["Math"]:
    print(f"  {dom:9s} " + str({k: cnt[(dom, k)] for k in KS}))
nm = sum(v for (d, _), v in cnt.items() if d in NONMATH)
print(f"  non-math items: {nm}; math control items: {len(rows) - nm}")
print(f"  all Math items passed the exactness assertion (shipped set == computed truth)")
