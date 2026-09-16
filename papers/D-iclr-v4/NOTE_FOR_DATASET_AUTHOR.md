# MathRefBench: one request, and a validation result you may want

We wrote independent validity checkers for `final_mathrefbench.jsonl`. They **verify 1,279 of 1,279
stored solutions, with zero failures**, across 189 of the 324 items. Your answers and our checkers
agree everywhere they meet.

**The ask: the MathConstraint instance generator.** 68 `math_constraint` items give a seed and a
density in `original_parameters` but not the instance itself, so we cannot reconstruct the
constraint a candidate answer is supposed to satisfy:

| item | `original_parameters` | what's missing |
|---|---|---|
| `magic_square_density15_n6_seed92063` | `{density: 15, n: 6}` | which cells are pre-filled, with what |
| `max_clique_density52_k7_n48_seed4904` | `{density: 52, k: 7, n: 48}` | the 48-vertex graph |
| `graph_coloring_density…_k3_n32…` | `{density, k, n}` | the graph to colour |
| `low_autocorrelation_n12` | `{n}` | the threshold that counts as a solution |

The generator script is ideal (seed + parameters should reproduce the instance). Failing that, an
`instance` field per item, or a one-line spec per family, would do.

The MathConstraint paper (arXiv 2605.08498) says the generator and evaluation harness are released,
but we could not find the repository — a pointer would be enough.

## Why we need checkers rather than the answer bank

Our paper studies a failure mode of LLM judges: when a question has several correct answers, a judge
shown one of them tends to reject the others. Testing that requires deciding whether an arbitrary
candidate is *actually correct*, not whether it appears in a stored list. Scoring against the bank
would reproduce the very error we are measuring.

This matters because **the bank is capped at 7 answers per item** (you confirmed this; every item has
at least 2, and 306 of 324 hold exactly 7, with 1,874 of 2,198 solutions marked
`origin: "generated"`). So an item may well have valid answers that are not in the bank, and a
candidate can be correct yet unlisted. That is exactly the case our paper is about, and exactly why
a checker rather than a lookup is required.

## Two notes

**MathConstruct's checkers are public** (`github.com/eth-sri/mathconstruct`, per-problem `check`
methods). We plan to use those for the 67 `mathconstruct` items rather than trusting the bank. If
the copies in MathRefBench have diverged from upstream, tell us.

**Two of our checkers were wrong when first written and your data caught them** — `number` (we
required equal sums of squares) and `hadamard` (wrong cyclic-autocorrelation constant). Fixed.

## What we'll send back

If we get the generator, we'll share the extended checkers and the verification result across all
~257 `math_constraint` items — an independent audit of the bank. Any stored answer that fails, we
send you the item and the reason rather than dropping it silently.
