# Build the answer-separability continuum tasks (P-SC1..P-SC4, registered in
# papers/analysis/sep_continuum_analysis.py, committed together with this file BEFORE any
# generation, oracle, or judging runs).
#
# The prospective test of the separability hypothesis the code falsification produced.
# 25 base constraint instances (single congruence x = a mod m on [lo, hi], exactly K base
# solutions, K in 6..10), each asked at FOUR answer-structure strata:
#   scalar : one such integer, boxed.                      (short separable token)
#   pair   : two distinct such integers, boxed "x,y".      (short separable token, composite)
#   json   : three distinct such integers as a JSON object (structured but still a short
#            canonicalizable string)
#   program: a Python function f() returning three such    (the artifact IS the answer;
#            integers                                       no separable token)
# All strata are multi-valid by construction (k >= 6, C(K,2) >= 15, C(K,3) >= 20), so the
# k > 1 step is saturated everywhere and answer STRUCTURE is the only axis that moves.
# The separability hypothesis predicts a CLIFF at the artifact boundary, not a gradient:
# that discrimination (cliff vs the review's assumed gradient) is what the registered
# predictions encode.
#
# References (pinned, seeded rng(7)): scalar = one sampled base solution; pair = two,
# sorted, "x,y"; json = {"values": [three sorted], "count": 3}; program = the canonical
#   def f():
#       return [x for x in range(lo, hi + 1) if x % m == a][:3]
# Each task stores ref_canon (the canonical form used for matching) and the full base
# solution set. Output: runs/sep_tasks.jsonl (100 rows).
import json
import random

rng = random.Random(7)
N_ITEMS = 25

instances = []
seen = set()
while len(instances) < N_ITEMS:
    m = rng.choice([3, 4, 5, 6, 7])
    a = rng.randrange(m)
    lo = rng.randrange(20, 200)
    K = rng.choice([6, 7, 8, 9, 10])
    # find hi giving exactly K solutions
    sols = []
    x = lo
    while len(sols) < K:
        if x % m == a:
            sols.append(x)
        x += 1
    hi = sols[-1] + rng.randrange(0, m)  # next solution is sols[-1] + m, so K is preserved
    sols = [x for x in range(lo, hi + 1) if x % m == a]
    if len(sols) != K:
        continue
    key = (m, a, lo, hi)
    if key in seen:
        continue
    seen.add(key)
    instances.append(dict(m=m, a=a, lo=lo, hi=hi, sols=sols))

BOX = ("You MUST end your response with the final answer inside \\boxed{...}, with nothing "
       "after it.")
rows = []
for i, ins in enumerate(instances):
    m, a, lo, hi, sols = ins["m"], ins["a"], ins["lo"], ins["hi"], ins["sols"]
    base = (f"{lo} <= x <= {hi} and x leaves remainder {a} when divided by {m}")
    r1 = rng.choice(sols)
    r2 = sorted(rng.sample(sols, 2))
    r3 = sorted(rng.sample(sols, 3))
    prog_ref = (f"def f():\n    return [x for x in range({lo}, {hi + 1}) "
                f"if x % {m} == {a}][:3]")
    prog_canon = ",".join(str(x) for x in sols[:3])
    strata = dict(
        scalar=dict(
            problem=(f"Give one integer x such that {base}. {BOX} "
                     f"Example ending: The answer is \\boxed{{42}}"),
            ref_answer=str(r1), ref_canon=str(r1)),
        pair=dict(
            problem=(f"Give two DISTINCT integers x, each satisfying: {base}. Write them "
                     f"comma-separated. {BOX} Example ending: The answer is \\boxed{{41,52}}"),
            ref_answer=f"{r2[0]},{r2[1]}", ref_canon=f"{r2[0]},{r2[1]}"),
        json=dict(
            problem=(f"Give three distinct integers x, each satisfying: {base}. Answer "
                     f"with a JSON object of exactly the form {{\"values\": [v1, v2, v3], "
                     f"\"count\": 3}}. End your response with that JSON object on its own "
                     f"line, nothing after it."),
            ref_answer=json.dumps({"values": r3, "count": 3}),
            ref_canon=",".join(str(x) for x in r3)),
        program=dict(
            problem=(f"Write a Python function f() taking no arguments that returns a list "
                     f"of three distinct integers x, each satisfying: {base}. Output the "
                     f"complete function in a ```python code block."),
            ref_answer=prog_ref, ref_canon=prog_canon))
    for sname, s in strata.items():
        rows.append(dict(problem_id=f"sep/{sname}-{i}", stratum=sname, inst=i,
                         problem=s["problem"], ref_answer=s["ref_answer"],
                         ref_canon=s["ref_canon"], params=dict(m=m, a=a, lo=lo, hi=hi),
                         base_solutions=sols, k_base=len(sols)))

with open("runs/sep_tasks.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(f"[build_sep_tasks] {len(rows)} tasks ({N_ITEMS} instances x 4 strata); "
      f"K range {min(x['k_base'] for x in rows)}..{max(x['k_base'] for x in rows)}")
