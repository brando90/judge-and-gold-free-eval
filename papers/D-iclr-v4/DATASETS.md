# Datasets for Paper D v4

Two datasets built from one benchmark, kept separate on purpose. Every number below is measured,
not estimated. Paths are relative to the repository root.

The central property of both: **correctness is decided programmatically, never by matching a stored
answer list.** A candidate is valid if a checker says the constructed object satisfies the problem's
constraints. That matters because the benchmark stores at most 7 reference answers per item while
these problems admit thousands, so "not in the reference list" carries no information about
correctness — and scoring by list-matching would reproduce the exact error the paper studies.

---

## Where the data lives

| file | items | size | sha256 (first 16) |
|---|---|---|---|
| `papers/D-iclr-v4/datasets/dataset1.jsonl` | 156 | 1.8M | `c2567d5733676384` |
| `papers/D-iclr-v4/datasets/dataset2.jsonl` | 110 | 1.6M | `2a1ba9fc975787e2` |

Source benchmark: `datasets/final_mathrefbench.jsonl` (324 items, built from MathConstruct and
Math-Constraint).

### Raw candidate pools

The pools are **not** in git — 157MB and 2.4MB, against a 132MB repo, for data that is not part of
the paper. They are attached to the private release
**[`paper-d-iclr-v4`](https://github.com/brando90/judge-free-eval/releases/tag/paper-d-iclr-v4)**,
readable by anyone with access to this repository:

| asset | rows | gzipped |
|---|---|---|
| `dataset1_pool_scored.jsonl.gz` | 20,288 | 42.7M |
| `dataset2_pool_scored.jsonl.gz` | 1,288 | 0.5M |
| `MANIFEST.txt` | — | sha256 checksums |

```bash
gh release download paper-d-iclr-v4 --repo brando90/judge-free-eval --dir pools
shasum -a 256 -c <(awk '/sha256/{print $2"  "f} /\.gz$/{f=$1}' pools/MANIFEST.txt)
```

Only the **scored** pools are published. The unscored ones
(`gpt-4.1-mini-2025-04-14.jsonl`, `gpt-5.6-sol.jsonl`) are redundant: the scored files have the same
rows and the same full reply text, plus the verdict fields, so shipping both would duplicate ~300MB
of model output for nothing. Locally they all sit under the gitignored
`experiments/tfa-vs-judge/runs/v4_pool/`.

Every row keeps the model's full reply, so scoring can be redone after any checker change without
regenerating — which is what makes `v4_rescore.py` cheap.

### Record format

One JSON object per item:

```
question_id, problem_name, problem, formatting_instructions,
generator,                 # model that produced the candidates
draws,                     # samples drawn for this item
references: [ {answer, normalized_answer_id, origin, canonical} ],
candidates: [ {answer, valid, sample, case, generator} ]
```

`case` is **A** (valid, coincides with a stored reference), **B** (valid, absent from the reference
list — the population the paper is about), or **C** (invalid). Every candidate records its
`generator`, so the Dataset 2 case-C provenance difference described below is visible in the data
rather than only in prose.

---

## Dataset 1 — the main pool

| | |
|---|---|
| Items | **156** |
| Generator | `gpt-4.1-mini-2025-04-14`, temperature 1.0 (explicit) |
| Draws per item | 64 |
| Candidates | 238 case A, 2,036 case B, **2,112 case C** |
| Distinct valid answers per item | median 10, mean 14.6, min 2, max 64 |
| Case C per item | median 5, mean 13.5, **min 0**, max 62 |
| References per item | median 7, min 2, max 7 (156 canonical, 911 generated) |

**Generation pool:** 20,288 draws across 317 items, 7,331 valid (36%), 0 errors, **$92.20**.
Selected from that pool are the 156 items with ≥2 distinct valid candidates.

**Generator choice** was measured on 12 checkable items against four alternatives. gpt-4.1-mini was
both the cheapest and no less accurate than models 4× dearer (6/12 valid vs 5/12 for gpt-4.1,
GPT-5-mini and Haiku 4.5), with the best parse rate (12/12). Sonnet 5 solved more (10/12) at **90×
the cost**, and would have produced a pool too uniformly correct to study.

**Caveat:** case C per item has a **minimum of 0** — some items have no invalid candidates at all,
so false-acceptance cannot be measured on them. Filter on case-C availability before that analysis.

---

## Dataset 2 — the hard pool

Dataset 1 leaves 161 of 317 items unusable: 140 where gpt-4.1-mini never produced a valid answer in
64 attempts, and 21 yielding only one distinct answer. Those are the **hard** items, and they are
where the effect should be strongest: a judge that cannot solve the problem itself has no choice but
to lean on the reference it was shown. Dataset 2 recovers 110 of them.

| | |
|---|---|
| Items | **110** |
| Generator (cases A, B) | `gpt-5.6-sol`, temperature 1.0 (explicit) |
| Generator (case C) | `gpt-4.1-mini-2025-04-14` — see below |
| Draws per item | 8 |
| Candidates | 44 case A, 461 case B, **3,966 case C** |
| Distinct valid answers per item | median 5, mean 4.6, min 2, max 8 |
| Case C per item | median 38, mean 36.1, min 3, max 64 |
| References per item | median 7, min 2, max 7 (110 canonical, 635 generated) |

**Generation pool:** 1,288 draws across 161 items, 901 valid (70%), 0 errors, **$220.97**.

**Generator choice** was measured, not assumed: nine models on the same 25 hard items.

| model | valid/draw | items ≥1 valid | $/draw |
|---|---|---|---|
| **gpt-5.6-sol** | **90%** | 13/15 | $0.149 |
| gpt-5.6-terra | 62% | 16/24 | $0.072 |
| claude-opus-5 | 51% | 14/24 | $0.971 |
| gpt-5.6-luna | 25% | 7/25 | $0.007 |
| claude-sonnet-5 | 23% | 9/25 | $0.212 |
| gpt-5-mini | 10% | 11/25 | $0.020 |
| claude-haiku-4-5 | 2% | 2/25 | $0.007 |
| gpt-4.1 | 1% | 1/25 | $0.015 |
| gpt-5.4-nano | 0% | 0/25 | $0.0003 |

sol is both the strongest and cheaper per draw than Sonnet 5; Opus 5 is dominated outright (terra
beats it on coverage at 1/14th the cost). Probing cost ~$50 and overturned an earlier recommendation
of Sonnet 5 made before the gpt-5.6 family had enough draws to judge.

**Draw depth** was also measured. A bootstrap over observed draws put the knee at 3–4 draws per
item; going 4 → 16 costs 4× for +13 items. We ran 8.

### Case C comes from a different generator — a declared confound

gpt-5.6-sol is 70% valid on these items, so it produces too few wrong answers to measure false
acceptance (11 across 46 items at one point). Dataset 1 already holds 5,570 distinct invalid answers
covering **158 of these 161 items** — genuine failures on exactly these problems, already paid for.
The remaining 3 items have no distinct invalid answer available, so false acceptance is undefined
there and they must be filtered out of that analysis.

The alternative, perturbing valid answers into wrong ones, was rejected. Corruption has failed a
prospective manipulation check **twice** in this project (Registration 6: 5 of 7 corrupt prompts
never moved their judge; Registration 7: 2 of 9 cells passed, one moved the *wrong* way). And a
perturbed correct answer sits minimally distant from a correct answer — which is the very axis this
paper measures, making it the one bias that would flatter our own claim.

**Consequence for analysis:** the confound is confined to false acceptance. The **A-vs-B comparison
that carries the main claim is unaffected**, since both come from one generator. Report false
acceptance separately per dataset, never pooled. Dataset 1 additionally supports a confound-free
within-generator check, as gpt-4.1-mini produced both valid and invalid candidates there.

---

## Combined coverage

| | items |
|---|---|
| Benchmark total | 324 |
| Gradeable without the answer key | 317 |
| Dataset 1 | 156 |
| Dataset 2 | 110 |
| Overlap | **0** |
| **Combined** | **266 (82%)** |

The two datasets are **analysed separately and never pooled**: they differ in generator and in draw
depth, so a cross-dataset comparison would confound item difficulty with generator identity.

**The 58 items in neither dataset:** 7 excluded because their verifier is untrustworthy (see below),
and 51 that no generator we tried could solve twice.

---

## How correctness is decided

Three checkers, each validated against the benchmark's own stored answers before being trusted.
A checker that rejects known-good answers would manufacture this paper's effect, so each had to
clear the same bar first.

| checker | items | validation |
|---|---|---|
| `scripts/v4_checkers.py` — our predicates | 189 | **1,279/1,279** stored answers accepted |
| `scripts/v4_mc_checkers.py` — upstream MathConstruct `check()` | 67 | **459/459** |
| `scripts/v4_csp_checkers.py` — upstream Math-Constraint `verify()` | 61 | **411/411** |

Upstream code is vendored and pinned: MathConstruct at `3e51d847`, Math-Constraint at `687a6d55`
(see `experiments/tfa-vs-judge/vendor/PROVENANCE.md`).

Per-dataset breakdown by checker family:

| | our predicates | CSP verify | upstream MathConstruct |
|---|---|---|---|
| Dataset 1 (156) | 116 | 8 | 32 |
| Dataset 2 (110) | 46 | 33 | 31 |

### Two findings from building the checkers

**`low_autocorrelation` (7 items) is excluded.** Its upstream verifier rejects Math-Constraint's
*own* stored solution, not merely ours, so it cannot be trusted to score candidates.

**`graph_k_coloring` needed a symmetry fix.** The verifier rejected 52 of 126 stored answers. All 52
are proper colourings within k — confirmed directly against the edge list parsed from each problem
statement, independently of the solver — and all 52 are accepted once colours are relabelled into
order of first appearance. The pycsp3 model carries value-precedence constraints, so `[2,0,1,3,…]`
is refused where `[0,1,2,3,…]` is accepted: same partition, different names.

That is this paper's thesis appearing in a published benchmark's own tooling — a correct answer
confidently rejected as "Solution violates constraints (UNSAT)" for differing *presentationally*
from the reference form. The relabel retry is restricted to types where value identity is a genuine
symmetry, and is gated on a negative control: valid answers still accepted 6/6, adjacent-vertex
colour clashes rejected 6/6, over-k colourings rejected 6/6. Relabelling preserves the partition, so
it cannot launder a wrong answer into a right one.

---

## A property that shapes the experiment design

**Canonical answers are rediscovered ~2× more often than chance.** Every item's reference bank holds
one canonical answer (`origin: "original"`, always index 0) plus machine-generated ones. Measured on
Dataset 1: canonical answers are 14.7% of available reference slots but **31%** of candidate matches
(22 of 71 vs 10.1 expected, sd 2.95, **z = 4.02, p = 5.8e-05**).

So under uniform sampling, *which* reference we show correlates with *whether* the candidate matches
it. If judges then score matching answers higher, "judges favour the answer they were shown" becomes
indistinguishable from "canonical answers are easier to rediscover" — a property of the generator,
not of judging.

`scripts/v4_reference_sampler.py` removes this by balancing reference `origin` 50/50 by construction
(uniform sampling would give 14.3%) and balancing position within swap pairs, so origin is not
confounded with presentation order either.

---

## Reproducing

```bash
cd experiments/tfa-vs-judge

# 1. generate candidates (Dataset 1 shown; Dataset 2 uses gpt-5.6-sol, 8 draws, poolb_items.txt)
python3 scripts/v4_generate.py --model gpt-4.1-mini-2025-04-14 --provider openai \
    --price-in 0.4 --price-out 1.6 --n-samples 64 --workers 64 --cap-usd 140

# 2. re-score every row under one checker version
python3 scripts/v4_rescore.py --in runs/v4_pool/<pool>.jsonl --out runs/v4_pool/<pool>_scored.jsonl

# 3. assemble a dataset
python3 scripts/v4_build_dataset2.py --pool runs/v4_pool/<pool>_scored.jsonl \
    --case-c-pool runs/v4_pool/<case-c-source>.jsonl --out <dataset>.jsonl
```

Scoring is a pure function of each row's stored reply, so step 2 can be rerun after any checker
change without regenerating. `--case-c-pool` defaults to the Dataset 1 pool, which is correct for
Dataset 2; when rebuilding Dataset 1, point it at Dataset 1's own pool.

Total generation spend across both datasets and all probes: **$398.55**.
