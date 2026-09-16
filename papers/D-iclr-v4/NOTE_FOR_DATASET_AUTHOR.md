# MathRefBench: request for the instance generators (and a validation result)

Short version: we wrote programmatic validity checkers for `final_mathrefbench.jsonl` and they
verify **1,279 of 1,279** checkable stored solutions with zero failures. They cover **189 of the
324 items**. We would like to cover ~68 more, and for that we need the code (or the raw instances)
that generated the `math_constraint` problems whose parameters do not fully determine the instance.

---

## Why we are writing checkers at all

Our paper studies a failure mode of LLM judges: when a question has several correct answers, a
judge shown one of them tends to reject the others. Testing that claim requires deciding, for an
arbitrary candidate answer, whether it is **actually correct** — not merely whether it appears in a
stored answer list. Otherwise a correct-but-unlisted answer is scored as wrong, and the
measurement reproduces the very error under study.

`final_mathrefbench.jsonl` is close to ideal for this, because most `math_constraint` problems are
self-verifying: "find an all-interval series of size 13", "place 7 non-attacking queens", "build a
graph on 10 vertices with minimum degree 6". Given the problem parameters, a short program decides
validity with no answer key.

## What we built

`v4_checkers.py` — one checker per family, taking `(answer, original_parameters)` and returning
valid / invalid. Families covered (189 items):

n-queens · all-interval series · Langford sequences · Costas arrays · Golomb rulers ·
knight's tours · De Bruijn sequences · quasigroups · orthogonal Latin squares · Legendre pairs ·
antimagic squares · Ramsey colourings · social golfers · number partitioning · BIBD ·
`pysms` graph-property constructions (degree bounds, edge counts, clique / independent-set /
chromatic-number bounds, girth, connectivity)

**Validation against your data:** every one of the 1,279 stored solutions in those families
verifies. Two checkers were wrong when first written and your data caught them — `number` (we
wrongly required equal sums of squares as well as equal sums) and `hadamard` (we used the wrong
cyclic-autocorrelation constant before reading the Legendre-pair definition). After fixing those,
zero failures. That is a good mutual sanity check: your answers and our independent checkers agree
everywhere they meet.

## What we cannot check, and the ask

**68 `math_constraint` items** whose `original_parameters` name a *seed and a density* but not the
generated instance itself. Examples:

| `question_id` fragment | `original_parameters` | what is missing |
|---|---|---|
| `magic_square_density15_n6_seed92063` | `{density: 15, n: 6}` | which cells are pre-filled, and with what |
| `max_clique_density52_k7_n48_seed4904` | `{density: 52, k: 7, n: 48}` | the actual 48-vertex graph |
| `graph_coloring_density…_k3_n32…` | `{density, k, n}` | the graph to be coloured |
| `latin_square_density…_n10` | `{density, n}` | the partially filled grid |
| `graceful_labeling_k…_p…` | `{k, p}` | the graph to label |
| `low_autocorrelation_n12` | `{n}` | the objective threshold that counts as a solution |
| `non_transitive_dice_m…_n…` | `{m, n}` | the exact dominance requirement |

For these, a candidate answer cannot be validated: we cannot reconstruct the constraint it is
supposed to satisfy. They currently fall back to answer-list matching, which is exactly the scoring
we are trying to avoid.

**What would help, in order of preference:**

1. **The generator script(s)** — if the seed plus parameters reproduce the instance deterministically,
   we can regenerate and check. This is the cleanest fix.
2. **The instances themselves**, added to each item, e.g. an `instance` field holding the graph edge
   list, the pre-filled grid, or the threshold.
3. **A short spec per family** — for `low_autocorrelation`, for example, just the objective value a
   valid answer must achieve.

## Two other things worth knowing

**The 67 `mathconstruct` items** (competition problems: "show that there exists n such that …") are
not checkable by any short program — validity needs the mathematics re-derived, and answers are
free-form (200-digit integers, coefficient lists). We plan to treat these separately and to state
the limitation, rather than pretend the answer bank settles correctness. No action needed, unless
you have validity checkers we have not seen.

**The answer bank looks like a sample rather than a complete set**: 1,874 of 2,198 solutions carry
`origin: "generated"`, and 306 of 324 items hold exactly 7 — which reads as a cap rather than the
true number of valid answers. We are treating it that way (a candidate may be valid yet absent from
the bank), which is precisely why the checkers matter to us. If instead the bank is intended to be
exhaustive for some families, that would be very useful to know, because it changes what an
unbanked-but-valid answer means.

## What we will report back

If we get the generators, we will share the extended checkers and the verification result across
all ~257 `math_constraint` items — a free, independent audit of the answer bank. If any stored
answer fails a checker we will send you the item and the reason rather than silently dropping it.

Contact: via the shared repository.
