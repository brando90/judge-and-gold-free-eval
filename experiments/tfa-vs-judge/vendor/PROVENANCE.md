# Vendored upstream checkers

`mathconstruct/` is a copy of https://github.com/eth-sri/mathconstruct
pinned at commit `3e51d847547a6586237ae55b83131b0e31b8476d` (fetched 2026-09-16), with `.git/` removed.

Used for the 67 `mathconstruct` items in `datasets/final_mathrefbench.jsonl`: each problem class
exposes `check()`, and `Problem.parse()` handles \boxed{} extraction and list-depth matching.
Verified against the benchmark's own answer bank: **459/459 stored answers accepted, 67/67 items**.

Calling convention (see scripts/v4_mc_checkers.py):
    prob = cls.get_original()          # every benchmark item is an /original
    parsed = prob.parse(latex_text)    # takes the \boxed{...} string
    ok = prob.check(parsed)            # bool | (bool, reason, CheckerTag)

Do NOT feed the stored `answer` field in directly -- it carries JSON artifacts (big integers
serialized as strings inside lists, fractions as "a/b"). Use `rendered_answer`, or the model's
raw reply, both of which are \boxed{} LaTeX.

Checker deps only: pydantic, numpy, sympy, scipy, loguru, antlr4-python3-runtime==4.11.
(torch / transformers / openai in their pyproject are for their eval harness, not the checkers.)

---

## math-constraint/

Copy of https://github.com/vireshpati/Math-Constraint pinned at commit `687a6d5510f96afdfa7229fc04b230e434e0c792`
(fetched 2026-09-16). Only `src/`, `mathconstraint/` and `mathconstraint_easy/` are kept;
`results/` and `.git/` are not needed by the verifier.

Covers the `math_constraint` items our own checkers cannot reach, via
`math_constraint.eval.validate_answer(problem_row, True, answer)`, which normalises the answer and
calls `verify()` -- re-solving the pycsp3 model with the candidate fixed as equality constraints.

Requirements: a JVM (pycsp3 solvers are Java; brew openjdk works) and `pycsp3`. `stubs/pysms` is a
deliberate stand-in: `problems.py` imports `sms_solver` at module scope, which needs the real pysms
(a C++/Boost build), but every pysms_* family in our benchmark is already covered by v4_checkers.py,
so the stub satisfies the import and raises if anything actually tries to use it.

Measured: **0.47s mean, 0.6s max per verify**, uniform across all 9 problem types, with refutation
as fast as confirmation. An earlier claim that this was a prohibitive "different cost class" was
wrong -- it came from reading the 60s solver *timeout* as if it were a measurement.

**`low_autocorrelation` is excluded (7 items).** Its verifier rejects the repo's OWN stored
solution, not merely ours, so it cannot be trusted to score candidates.
