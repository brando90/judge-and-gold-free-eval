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
