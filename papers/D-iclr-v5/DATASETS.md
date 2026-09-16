# Datasets used in "Reference Anchoring Biases LLM Judges Toward the Answer They Are Shown When Several Are Correct"

Every dataset the paper draws on, how it was built, where it lives, and what it was used for.
Paths are relative to the repository root. Pools we built ourselves come with a programmatic
oracle: the full set of correct answers is stored with the task, so "correct but different from
the reference" is decidable without a judge.

Third-party data is used under its own licence and is not redistributed here beyond what the
anonymized supplement contains. HLE and BrowseComp items carry their benchmarks' canary strings
and must not be used for training.

---

## 1. Constructed pools (ours)

### 1.1 Replication pool — 120 tasks

* **Builder:** `experiments/tfa-vs-judge/scripts/build_replication_pool.py`
* **Tasks:** `experiments/tfa-vs-judge/runs/repl_main_tasks.jsonl`
* **What it is:** arithmetic questions with several correct answers, drawn from five constraint
  families, each verifiable from the answer alone:

  | Family | Question | Answer |
  |---|---|---|
  | `crt` | an `x` in a range with `x = a mod m` and `x = b mod n` | integer |
  | `subset` | a subset of a multiset summing to a target | list of integers |
  | `goldbach` | an ordered pair of distinct primes summing to an even `N` | pair |
  | `divcount` | an integer in a range with exactly `k` divisors | integer |
  | `digitsum` | a `d`-digit multiple of `q` with digit sum `s` | integer |

* **How it was built:** the design was fixed before any model saw a task. Each item stores its
  full enumerated solution set; the reference is one valid answer sampled from that set. Difficulty
  was calibrated on a 20-item pilot, which does not enter any analysis, to put Llama-3.1-8B's
  best-of-64 pass rate in `[0.2, 0.8]` — hard enough that the judge's opinion matters.
* **Used for:** P1 (the swap), P2 (grading), P3 (acceptance), and the mitigation protocols.

### 1.2 Swapped-reference pool — the same 120 tasks, one field changed

* **Builder:** `experiments/tfa-vs-judge/scripts/build_replrot_pool.py`
* **What it is:** the replication pool with the reference moved to a *different* correct answer.
  The candidate texts are byte-identical to the originals; the only change is which valid answer
  sits in `ref_answer`. This is what makes P1 a within-text comparison.
* **Selection rule (pinned before judging, and disclosed as pool-aware):** among the valid answers
  other than the original reference, take the one that appears most often as a boxed answer among
  that item's oracle-valid samples, ties broken by sorted answer string. Items with no valid
  non-matching answer present in the pool keep the first alternative and are excluded from the
  gain/loss readouts by the analysis. Pool-awareness biases nothing *within* an item, because the
  readout compares the same sample under two references.
* **Used for:** P1.

### 1.3 k-pool — 75 tasks, k ∈ {1, 2, 4, 8, 16}

* **Builder:** `experiments/tfa-vs-judge/scripts/build_synth_multiplicity.py` (seed `20260824`)
* **What it is:** task families with *exactly* k correct answers, so answer multiplicity is a dose
  and the unique-answer control (k = 1) lives inside the same design rather than in a different
  dataset.
* **Used for:** the k = 1 control, the dose response, and the mitigations (the full-credit
  instruction, showing min(3, k) references, blind-then-reveal).

---

## 2. MACE — third-party factual questions

* **Source:** MACE (arXiv:2602.07842), questions whose number of correct answers is fixed by
  construction at k ∈ {1, 2, 4, 6}.
* **Builder:** `experiments/tfa-vs-judge/scripts/build_mace_tasks.py` (seed `20260901`)
* **Why it is here:** every constructed pool above is ours. MACE supplies third-party questions
  with third-party ground truth, so the central result does not rest only on tasks we wrote.
* **Domain audit, run before the pool was built.** We measured how often a model names a valid
  answer missing from the shipped answer list:

  | Domain | Missing-from-list rate | Decision |
  |---|---|---|
  | River | 2.3% | included |
  | Language | 8.1% | included |
  | Region | 30.8% | excluded |
  | Office | 33.3% | excluded |
  | Award | 43.5% | excluded |
  | Math | 0% (verified by direct computation on all 2,000) | included as a label-noise control |

  The excluded domains were dropped, not patched.
* **Population:** River and Language at all four cardinalities, 25 items per (domain, k) cell =
  200 items, plus 100 Math items as the control. The reference is one valid answer per item, drawn
  by the same seeded RNG.
* **Matching rule:** a candidate's answer is its last `\boxed{}` content, or its last 200
  characters if there is none, lowercased with non-alphanumeric characters removed. It is correct
  if it equals or contains a normalized list entry, and it matches the reference by the same test
  against the reference alone. Aliases missing from the list count as wrong, which *lowers*
  measured rejection of correct answers rather than inflating it.
* **Used for:** P2 and P3 on factual questions, and as the substrate for the benchmark-grader study.

---

## 3. Benchmark answer pool — 149 questions, 596 answers

* **Generation:** `experiments/tfa-vs-judge/scripts/r20_generate_mace.py`
* **Pool:** `experiments/tfa-vs-judge/runs/r20/mace_gen/pool.jsonl`
* **What it is:** the 149 MACE River and Language questions with several correct answers
  (49 at k=2, 50 at k=4, 50 at k=6), each answered once by four models — Llama-3.1-8B-Instruct (its first stored sample), Claude Haiku 4.5,
  Sonnet 5, and Opus 5 — giving 596 answers: 396 correct but differing from the reference, 144
  correct and matching, 56 wrong. Answer-list accuracy is 90.6%.
* **Prompt:** one answer per question, ending in `\boxed{...}`, the same prompt as the stored MACE
  candidate pool; 512 output tokens.
* **Used for:** the shipped-grader study (SimpleQA grader, BrowseComp/HLE judge), the two open
  RL-reward verifiers, the instruction ladder, and the full-answer-list fix.

---

## 4. Hard single-answer pool — 200 HLE questions, 400 answers

* **Builders:** `experiments/tfa-vs-judge/scripts/r27_generate.py`, then `r27_build_pool.py`
* **Pool:** `experiments/tfa-vs-judge/runs/r27/hle_pool.jsonl` (not tracked in git)
* **What it is:** the 200 text-only exact-answer HLE questions sampled for the second prevalence
  audit, answered once each by GPT-4.1-mini and Claude Haiku 4.5 under HLE's official system
  prompt (2,048 output tokens).
* **Labels:** HLE's own judge — its verbatim prompt with o3-mini and structured output — scored
  each answer against the HLE reference. Only 7 of 400 answers are labeled correct, which is why
  this pool measures false acceptance and not recall.
* **Used for:** the hard-question test of the "ask whether it is correct" fix.

---

## 5. MATH-500

* **Source:** Hendrycks et al. (2021), 500 competition problems with unique answers.
* **How it is used:** unchanged. Candidates come from Qwen2.5-7B; the reference is shown either as
  the full solution or as the final answer alone.
* **Used for:** the P2′ control — with one correct answer, the reference should help, and it does
  (best-of-64 accuracy rises about 30 points).

---

## 6. Prevalence audits

Two audits estimate how often questions in single-reference benchmarks actually admit several
correct answers. Neither was validated by human annotators; both are reported with that caveat.

### 6.1 First audit — four datasets, 800 items

* **Sample:** 200 questions per dataset (seed 0) from MATH-500, GSM8K, DeepScaleR, and NQ-open.
* **Labels:** each item labeled twice, independently, by Claude annotators that did not see each
  other's labels; disagreements adjudicated by re-reading. Every alternative answer offered for a
  math item was checked by computation. Equivalent forms of one answer (1/2 and 0.5) count as
  unique, and "find all" questions whose answer is one set count as unique.
* **Result:** curated math sets are almost entirely single-answer; NQ-open reaches 30.0%, or 18.5%
  after excluding questions whose answer changed over time.
* **Weakness:** both passes come from one model family, so agreement may overstate reliability.

### 6.2 Second audit — five graded-against-one-reference datasets, 1,000 items

* **Data:** `papers/analysis/prevalence_v2/` (protocol committed before any labeling call)
* **Sample:** 200 questions each (seed 0) from SimpleQA, BrowseComp, text-only exact-answer HLE,
  TriviaQA, and the WebInstruct-verified RL training set.
* **Labels:** two annotators from *different* developers — Claude Sonnet 5 and GPT-5-mini — labeled
  every item independently; Claude Opus 5 adjudicated disagreements until its spending cap, after
  which 135 remaining disagreements (106 on BrowseComp) kept the conservative label. That fallback
  can only lower the multi-answer count.
* **Result:** 0% to 4% for questions written for a single answer; 5.5% for the RL training set
  (18% by either annotator). Agreement is low (κ ≤ 0.35), so these rates are rough.
* **Files:** `items_<dataset>.jsonl`, `labels_passA_*.jsonl`, `labels_passB_*.jsonl`,
  `adjudicated_*.jsonl`, with `analyze.py` and `checks_*.py`.

---

## 7. Third-party datasets used in supporting roles

| Dataset | Role |
|---|---|
| RewardBench-2 Ties | the exploratory observation the replication pool was built to replicate; its own invalid-labels were found ~90% unreliable, which is why it is not a headline substrate |
| MathConstraint | pilot on solver-verified combinatorial puzzles (extended appendix only) |
| MBPP | the code experiments: canonical program as reference, test suite as checker (extended appendix only) |
| TriviaQA | second prevalence audit |
| WebInstruct-verified | second prevalence audit; the RL training set whose verifier sees one reference |
| SimpleQA, BrowseComp, HLE | second prevalence audit, and the source of the three shipped graders run verbatim |
| GSM8K, DeepScaleR, NQ-open | first prevalence audit |

---

## 8. Candidate generation, common to the constructed pools

* **Generator:** Llama-3.1-8B-Instruct, 64 samples per task at temperature 1 (Qwen2.5-7B for
  MATH-500).
* **Prompt:** the final answer inside `\boxed{...}`.
* **Labels:** the registered checkers read the answer from `\boxed{}`; 38% to 43% of replies ignore
  the format, so the constructed pools also carry *any-format labels* that accept a final answer
  stated in any form, plus labels read by Qwen2.5-14B. A registered audit by Claude Opus 5 confirms
  86% of the answers the any-format rule credits, short of the 90% we predicted. Grading results
  hold in direction under all four labelings; only their size moves.

---

## 9. What ships in the supplement

The anonymized supplement contains the task generators and checkers, the candidate pools, every
answer labeling, all judge score files, and the analysis scripts that produce every number, table
and figure. BrowseComp items, labels and adjudications are excluded. The R27 HLE pool and its
grader outputs are in the supplement but not tracked in git.
