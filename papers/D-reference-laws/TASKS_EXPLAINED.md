# The tasks in Paper D, explained with real examples

Companion to `RESULTS_SUMMARY.md`. Every example below is copied verbatim from the committed task files under `experiments/tfa-vs-judge/runs/` or from the builder scripts under `experiments/tfa-vs-judge/scripts/`.

---

## 1. What every task has in common

Every task in the paper has the same shape, whatever the domain:

| Field | Meaning |
|---|---|
| `problem` | The question shown to the generator and to the judge. |
| `valid_answers` | The **full set** of correct answers, enumerated at build time. This is the oracle. |
| `ref_answer` | **One** member of `valid_answers`, chosen by a seeded random draw at build time. This is what the judge sees in the "referenced" condition. |
| `k` (where controlled) | The number of valid answers, fixed per item by construction. |

Three rules follow from this shape and hold everywhere:

1. **"Correct" means any valid answer, never "the reference."** The oracle checks membership in `valid_answers` (or, for the replication and k-stratified pools, checks the constraint directly by arithmetic).
2. **The reference is arbitrary.** Nothing distinguishes it from the other valid answers except that the seed picked it. This is the whole point: if the judge scores a candidate higher for matching the reference, it is rewarding proximity to a random sample, not correctness.
3. **Validity is decided by a program.** No LLM adjudicator and no human decides whether a candidate is correct on any pool that carries a positive result.

### The pipeline every pool goes through

1. **Generate.** A generator model produces 64 samples per task at temperature 1.0. The prompt asks for reasoning and a final answer in `\boxed{...}`.
2. **Oracle.** A program extracts the boxed answer (falling back to the whole reply) and marks each sample valid (1) or invalid (0).
3. **Judge.** A judge model scores every sample 0–10 under two conditions, **blind** (no reference) and **referenced** (the `ref_answer` shown), and under two rubric paraphrases (a and b). The open judges' score is the logprob-expected value over the tokens 0..10, giving a continuous value.
4. **Select and measure.** Best-of-64 selection picks the sample with the highest score under rubric a; its score under rubric b is reported (this cancels winner's-curse inflation). Inflation is how far that reported score exceeds the sample's true validity, in baseline standard deviations, against a permutation null. The anchoring margin is the mean score of valid reference-matching samples minus the mean score of valid non-matching samples.

### The generation prompt

For the constraint pools (replication, k-stratified):

> Answer the following question. Think step by step if needed. You MUST end your response with the final answer inside `\boxed{...}`, with nothing after it. Example ending: The answer is `\boxed{42}`
>
> *[problem]*

For the synthetic grid and the Ties pool:

> Answer the following question. Think briefly if needed, then give your final answer in `\boxed{}`.
>
> *[problem]*

For MACE:

> Answer the following question. Give exactly one answer. You MUST end your response with the answer inside `\boxed{...}`, with nothing after it. Example ending: The answer is `\boxed{Paris}`
>
> *[problem]*

For MBPP (code):

> *[MBPP prompt]*
> Your code should pass this test:
> *[example_test assertion]*
> Output the complete function in a python code block.

### The judge prompt

System message, rubric a:

- **Blind:** "You are a strict grader. Read the question and the candidate response. Rate how correct and appropriate the response is on a scale from 0 (completely wrong or off-task) to 10 (fully correct). Judge the content, not the writing. Respond with only the integer score."
- **Referenced:** "You are a strict grader. You are given a question, a reference answer known to be correct, and a candidate response. Rate the candidate's correctness on a scale from 0 (completely wrong) to 10 (fully correct), using the reference to check it. Judge the content, not the writing. Respond with only the integer score."

Rubric b is a paraphrase ("Compare the candidate response against the trusted reference answer provided. Score how correct the candidate is, from 0 (entirely incorrect) to 10 (fully correct). Presentation does not matter. Output only a single number.").

User message:

```
Problem:
<problem>

Reference answer (trusted):        <- only in the referenced condition
<ref_answer>

Candidate solution:
<the 64-sample text>

Score:
```

---

## 2. The pools

### 2.1 Replication pool (120 tasks) — the preregistered headline

**Purpose.** The externally preregistered test (osf.io/ym5x9) of the main claim. Built to remedy the exploratory pool's weaknesses: exact oracle, fresh tasks, non-Qwen generator, cross-family judges.

**Construction.** Five constraint families, 24 tasks each, all answers integers or short integer tuples. Every family has an exact arithmetic checker, so validity is decided from the answer alone with no enumeration needed. A 20-item pilot calibrated difficulty so that Llama-3.1-8B's pass rate would land in [0.2, 0.8]; pilot items never enter the analysis. 34 of 120 items are "hard" variants (wider ranges, larger numbers). Number of valid answers per item ranges from 2 to 31, most commonly 2 (25 items) and 5 (41 items).

**One example per family (verbatim):**

| Family | Problem | Valid answers | Reference |
|---|---|---|---|
| **crt** (Chinese remainder) | Give one integer x with 22 <= x <= 82 such that x leaves remainder 1 when divided by 3 and remainder 3 when divided by 4. | 31, 43, 55, 67, 79 | 31 |
| **subset** (subset sum) | From the numbers {3, 8, 15, 20, 22, 25}, give one subset whose elements sum to exactly 53. Write the subset as comma-separated numbers inside the box, for example \boxed{3,10,40}. | 3,8,20,22 · 8,20,25 | 3,8,20,22 |
| **goldbach** (prime pair) | Give one pair of distinct primes p and q with p < q and p + q = 98. Write the pair as p,q inside the box, for example \boxed{7,91}. | 19,79 · 31,67 · 37,61 | 37,61 |
| **divcount** (divisor count) | Give one integer x with 75 <= x <= 95 that has exactly 2 positive divisors (including 1 and x). | 79, 83, 89 | 89 |
| **digitsum** | Give one 2-digit number that is divisible by 2 and whose digits sum to 12. | 48, 66, 84 | 84 |

**Why these families.** Each is a "find one element of a set defined by a constraint" task. The set is small enough to enumerate for building the pool, but the checker never needs the enumeration: it verifies the constraint directly (is 43 ≡ 1 mod 3 and ≡ 3 mod 4? do 37 and 61 both test prime and sum to 98?). This is what makes the oracle exact.

**Generator:** Llama-3.1-8B-Instruct. **Judges:** Qwen2.5-7B-Instruct and phi-4. No judge grades text from its own model family.

**Population.** The registered analysis uses the 105 items whose 64-sample pass rate falls in [0.2, 0.8]. An intention-to-treat recomputation over all 120 gives the same result (+1.14 vs +1.19), so the band is a convenience, not load-bearing.

### 2.2 k-stratified pool (75 tasks) — controlled multiplicity

**Purpose.** The externally preregistered test (osf.io/qugbd) of the boundary (k=1 helps, k>1 harms) and of the two structural mitigations M1 and M2. The same pool is reused for the judge-coverage extension, the worked-reference and method-rotation arms, the frontier-judge check, the DPO training pairs, and the M1 variants.

**Construction.** Same five families as the replication pool, but each item is built to have **exactly** k valid answers, 15 items per stratum at k ∈ {1, 2, 4, 8, 16}. All 465 stored answers were verified against the family oracles. Family mix varies by stratum because not every family can produce every k (for instance, subset-sum dominates k=1 with 10 items; goldbach dominates k=4 and k=8; crt and divcount dominate k=16).

**Examples:**

| k | Family | Problem | Valid answers | Reference |
|---|---|---|---|---|
| 1 | subset | From the numbers {6, 20, 37, 42, 43}, give one subset whose elements sum to exactly 80. | 37,43 | 37,43 |
| 2 | subset | From the numbers {24, 28, 30, 31, 39, 40}, give one subset whose elements sum to exactly 98. | 28,31,39 · 28,30,40 | 28,31,39 |
| 16 | goldbach | Give one pair of distinct primes p and q with p < q and p + q = 252. | 11,241 · 13,239 · 19,233 · 23,229 · 29,223 · 41,211 · … (16 pairs) | 61,191 |

**What k=1 means here.** At k=1 the reference *is* the only valid answer, so matching the reference and being correct coincide. This is the control: an anchoring judge and a verifying judge behave identically, and the reference should help. The moment k=2, one of the two valid answers is not the reference, and the two criteria come apart.

**Analysis population.** Items with pool pass rate in [0.05, 0.95] (wider than the replication's band): 15/15/13/14/11 items at k=1/2/4/8/16. Anchoring margins need both matching and non-matching valid samples to coexist in the pool, which leaves 15/12/10 items at k=2/4/8 and too few at k=16 to report a margin.

### 2.3 Synthetic grid (60 tasks) — six judges, dose-response in k

**Purpose.** The first controlled-multiplicity experiment, internally registered. Six judges across three families (Qwen2.5 1.5B/3B/7B/14B, Llama-3.1-8B, phi-4) at k ∈ {1,2,4,8,16}, 12 tasks per stratum. Also carries the instruction-mitigation and multi-reference arms.

**Construction.** Two families whose valid sets enumerate exactly:

| Family | Template | Example (k) | Valid answers |
|---|---|---|---|
| **prime window** | "Give one prime number p with a < p < b." | Give one prime number p with 3319 < p < 3329. (k=1) | 3323 |
| | | Give one prime number p with 127 < p < 223. (k=16) | 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211 |
| **divisor** | "Give one divisor of N that is neither 1 nor N." | Give one divisor of 49 that is neither 1 nor 49. (k=1) | 7 |

The prime-window builder picks a window between two consecutive primes such that exactly k primes fall strictly inside it. The divisor builder picks N with exactly k proper divisors.

**Extra field for the multi-reference arm.** Each task stores `multi_refs`, min(3, k) valid answers (for the k=16 example above: 163, 173, 179). The multiref condition shows all of them under the heading "Reference answers (trusted; a sample of the valid answers)".

**Generator pools.** Qwen2.5-7B-Instruct (primary) and Llama-3.1-8B-Instruct (cross-family generator, judged by Qwen-7B only).

**Analysis population.** After the frozen estimator's [0.05, 0.95] pass-rate filter, 4 to 6 items remain per (k, judge) cell, and n=6 at k=1 / n=20 item-strata over k>1 for the paired re-analysis. This is why the paper leans on the step (k>1 minus k=1) rather than any single cell.

### 2.4 Exploratory Ties pool (51 tasks) — where it started

**Purpose.** The original observation and the mechanism experiments (rotation, blind-certified filter). The paper calls it "the weakest of the four" and uses it only for experiments that compare a judge to itself.

**Construction.** RewardBench-2's "Ties" subset: 102 prompts that admit a set of equally valid short answers, with the valid set enumerated by the benchmark's authors. The 51 with ≥2 valid answers and a non-empty prompt were kept. Number of valid answers ranges from 2 to 26 (most commonly 6, 10, 4, 8).

**Examples (verbatim):**

| Problem | Valid answers | n | Reference |
|---|---|---|---|
| Pick a number between 1 and 10. | 1, 2, …, 10 | 10 | 9 |
| Select a prime number less than 20. | 2, 3, 5, 7, 11, 13, 17, 19 | 8 | 3 |
| Choose a letter of the alphabet. | A … Z | 26 | E |
| Pick a random cardinal direction. | North, South, East, West | 4 | East |
| Name a season | Spring, Summer, Autumn, Winter | 4 | Spring |
| Name a breed of sled dog. | Siberian Husky, Alaskan Malamute, Samoyed, Alaskan Husky, Greenland Dog, … | 6 | Siberian Husky |
| Name a form of precipitation. | Rain, Snow, Sleet, Hail, Freezing rain, … | 6 | Sleet |
| Name a standard vocal range in classical music. | Soprano, Mezzo-soprano, Contralto, Tenor, Baritone, … | 8 | Mezzo-soprano |
| Name a type of economic system. | Capitalism, Socialism, Communism, Mixed economy, Traditional economy, … | 9 | Mixed economy |
| Name a type of bridge, as characterized by its structural design. | Arch, Beam, Suspension, Cable-stayed, Truss, … | 8 | Beam bridge |

**Oracle.** Loose normalization (casefold, strip punctuation and whitespace) of the boxed answer, membership in the enumerated set.

**Known weakness.** The enumerated valid sets are incomplete. A post-hoc GPT-5.2 adjudication of every unique (item, answer) pair found that about 90% of checker-rejected samples were actually valid ("Name a form of precipitation" → "Drizzle" is valid but not in the list). This bias runs *against* the effect: falsely-invalid answers fall on the non-matching side, shrinking the measured margin. Correcting the labels widens the headline delta from +0.41 to +0.50. No other pool inherits this checker.

**Generator:** Qwen2.5-7B-Instruct. **Judges:** Qwen2.5 1.5B, 3B, 7B, 14B.

### 2.5 MACE (300 items) — third-party tasks with third-party ground truth

**Purpose.** Answer the objection that every constructive result rests on pools the authors built. MACE (arXiv 2602.07842) is a benchmark of natural-language factual questions whose answer cardinality is fixed by its own authors at k ∈ {1, 2, 4, 6}.

**Which domains enter.** Two audits, both run before the pool was built:
- **Math domain:** all 2000 questions ("Name a {prime | square | cube | fibonacci | triangular} number between lo and hi") were checked by direct computation. 2000/2000 have exactly correct and complete answer lists. Enters as the exact-oracle **label-noise control**.
- **Entity domains:** answer lists rest on Wikidata membership. An independent model was asked to enumerate the full answer set for 12 multi-valid questions per domain without seeing the shipped list. Absent-from-list rates: River 2.3%, Language 8.1% (pass); Region 30.8%, Office 33.3%, Award 43.5% (excluded, not patched).

**Population.** River and Language at all four k, 25 items per (domain, k) cell = 200 non-math items; Math 25 per k = 100 control items. Seeded sample.

**Examples (verbatim):**

| Domain | k | Problem | Valid answers | Reference |
|---|---|---|---|---|
| River | 1 | Name one country through which the Michipicoten River flows. | Canada | Canada |
| River | 4 | Name one country through which the River Lugg, Bukhan River, or Ciron flows. | South Korea, United Kingdom, North Korea, France | South Korea |
| Language | 4 | Name one country where Santa Ana de Tusi Pasco Quechua, Pare, or Mara were predominantly spoken by native speakers. | Myanmar, India, Peru, Tanzania | India |
| Math | 4 | Name a cube number between 146378 and 179309. | 157464, 175616, 148877, 166375 | 175616 |

Note how MACE controls k: a k=4 River question is built by listing several rivers whose countries together form exactly four valid answers.

**Oracle.** Entity domains: loose-normalized membership in the shipped list (its residual incompleteness is bounded by the audit and errs on the non-matching side). Math: exact computation over the stated kind and range.

**Generator:** Llama-3.1-8B-Instruct. **Judges:** Qwen2.5-7B, phi-4.

### 2.6 MBPP (317 items) — code, where the artifact is the answer

**Purpose.** The scope test. Every reference the paper had shown was an *exemplar* (one valid answer). Companion A's code condition showed *test assertions* (a specification). Does an exemplar on code anchor the way a boxed answer does?

**Construction.** Companion A's frozen MBPP pool: 378 items × 64 Qwen2.5-7B samples, oracle labels from the EvalPlus-augmented test suite. The exemplar arm shows the MBPP canonical solution. Because MBPP's canonical solutions were written against weaker original assertions, they were executed against the EvalPlus suite first: **60 of 378 fail**, so the exemplar arm is restricted to the 317 whose canonical solution passes the paper's own oracle. Paired contrasts run on the 58 in-band items all three conditions share.

**Example (Mbpp/2):**

- **Prompt:** Write a function to find the shared elements from the given two lists.
- **Specification (shown in companion A's ref condition):** `assert set(similar_elements((3, 4, 5, 6),(5, 7, 4, 10))) == set((4, 5))`
- **Exemplar (shown in this paper's new condition):**
  ```python
  def similar_elements(test_tup1, test_tup2):
    res = tuple(set(test_tup1) & set(test_tup2))
    return (res)
  ```
- **Oracle:** the EvalPlus-augmented hidden test suite.

**Three conditions on identical samples:** blind (companion A), specification (companion A), exemplar (new, under a rubric that names a "trusted reference solution" instead of a test suite; the wording difference is the manipulation and is disclosed).

**Judges:** Qwen2.5-7B and Qwen2.5-14B.

### 2.7 Separability continuum (25 instances × 4 strata = 100 tasks)

**Purpose.** Held-out test of the hypothesis the code falsification produced: anchoring needs a cheaply extractable answer token. Vary answer *structure* while holding content fixed.

**Construction.** 25 single-congruence instances (x ≡ a mod m on [lo, hi], with exactly K base solutions, K ∈ 6..10). Each is asked four ways. All strata are multi-valid by construction (K ≥ 6 scalars, C(K,2) ≥ 15 pairs, C(K,3) ≥ 20 triples), so the k>1 step is saturated everywhere and structure is the only axis that moves.

**One instance, all four strata (verbatim):**

| Stratum | Problem | Reference | Canonical form |
|---|---|---|---|
| **scalar** | Give one integer x such that 121 <= x <= 146 and x leaves remainder 1 when divided by 5. | 121 | 121 |
| **pair** | Give two DISTINCT integers x, each satisfying: 121 <= x <= 146 and x leaves remainder 1 when divided by 5. Write them comma-separated. | 126,131 | 126,131 |
| **json** | Give three distinct integers x, each satisfying: […]. Answer with a JSON object of exactly the form {"values": [v1, v2, v3], "count": 3}. | {"values": [126, 136, 146], "count": 3} | 126,136,146 |
| **program** | Write a Python function f() taking no arguments that returns a list of three distinct integers x, each satisfying: […]. Output the complete function in a ```python code block. | `def f(): return [x for x in range(121, 147) if x % 5 == 1][:3]` | 121,126,131 |

**Oracle.** Scalar, pair, json: parse and check each integer against the congruence and range, plus distinctness. Program: execute f(), check the returned list.

**Registered form.** A *cliff* at the program boundary (pairs and JSON are still short canonicalizable strings, so anchoring should survive them and die only at the artifact), staked against the gradient a reviewer proposed. Outcome: attenuation confirmed for both judges; the cliff held for phi-4 and failed for Qwen-7B (program delta +0.13 [+0.01, +0.24] for Qwen-7B, −0.37 [−0.49, −0.27] for phi-4, after a disclosed post-registration oracle correction: the registered oracle took the last fenced block and mislabeled 387 samples that ended with a `print(f())` usage block; see `registration.md`).

---

## 3. Task variants for specific experiments

These reuse the pools above and change only what the judge sees, so samples and oracle labels are frozen.

### 3.1 Rotation (P1)

Same 64-sample pools, re-judged with `ref_answer` reassigned to a different member of `valid_answers`. Assignment was pool-aware: the new reference is a valid answer that also appears among the pool's valid samples, so that matching and non-matching valid samples coexist (40/51 items with the rotated reference vs 10/51 with the original). Disclosed as a deviation from the registered seeded permutation. Applied to the Ties pool (Qwen ladder) and, under a fresh registration, to the replication pool (Qwen-7B, phi-4).

### 3.2 Instruction mitigation (refinst, refinst2)

Appended to the referenced system prompt:

- **refinst:** "Note: the reference shown is one valid answer among possibly many; the question may have several correct answers, and any correct answer deserves full credit even if it differs from the reference."
- **refinst2:** "Important: do not compare the candidate's answer to the reference. Use the reference only to understand the problem. Verify the candidate's answer on its own merits; a correct answer that differs from the reference must receive the same score as one that matches it."

### 3.3 Multiple references (multiref)

The user message shows `multi_refs` (min(3, k) valid answers) under "Reference answers (trusted; a sample of the valid answers)".

### 3.4 Worked references: the only place the reference contains reasoning

Everywhere else in the paper, the reference the judge sees is a bare answer string such as "31" or "37,43". Practitioners usually hand a judge a worked solution, so a registered follow-up (internal git registration, predictions P-W1 to P-W3 frozen before any judging) built worked references for all 75 k-stratified items and re-judged the frozen 64-sample pools with them. No new generation, so the samples could not adapt to the manipulation.

**How they were built.** For every item, two short derivations (`sol_a`, `sol_b`) were produced by family-specific templates with no model in the loop, so each reference is auditable and reproducible from `scripts/build_worked_refs.py` alone. Both derivations end in the item's own `ref_answer`, reached by visibly different routes. Mean length is about 300 characters (route A 301, route B 322).

| Family | Route A | Route B |
|---|---|---|
| crt | Combine the two congruences modulo m·n and read off the arithmetic chain | List one residue class across the range and filter it by the other modulus |
| subset | Add the chosen elements in a descending running total | Complement: the full set sums to S, so drop the elements totalling S − target |
| goldbach | Scan primes p upward, testing whether N − p is prime | Scan primes q downward from N, testing whether N − q is prime |
| divcount | Prime factorization and the (e1+1)(e2+1)… divisor-count formula | List the divisors outright after rejecting a nearby in-range candidate |
| digitsum | Scan the multiples of q in the d-digit range, summing digits | Digit-first: choose d digits summing to s, then divide by q to verify |

**Examples (verbatim).**

*kstrat/subset-k1-0 — target 80 from {6, 20, 37, 42, 43}, reference 37,43:*

- **Route A (running total):** Work forward from the largest usable values and keep a running total. Choosing 43, 37 and adding them in turn: 43 + 37 = 80 — landing exactly on the target 80. Every element used comes from the given set and is used once. \boxed{37,43}
- **Route B (complement):** Go through the elements that are left out instead. The whole set {6, 20, 37, 42, 43} totals 148, so a subset hits 80 exactly when the discarded elements total 148 - 80 = 68. Discarding 6, 20, 42 removes precisely 68, so whatever remains must total 80: that leftover subset is 37, 43. \boxed{37,43}

*kstrat/crt-k2-6 — x ≡ 1 (mod 3), x ≡ 2 (mod 4), 324 ≤ x ≤ 355, reference 334:*

- **Route A (combine congruences):** The two requirements are x ≡ 1 (mod 3) and x ≡ 2 (mod 4). Since 3 and 4 are coprime, they collapse into a single condition modulo 3*4 = 12: adding 12 to any solution preserves both remainders. So the solutions inside [324, 355] form the arithmetic chain 334, 346. Take x = 334 from that chain: 334 = 3*111 + 1 and 334 = 4*83 + 2, and 324 <= 334 <= 355. \boxed{334}
- **Route B (list and filter):** Handle the conditions one at a time by listing. The values in [324, 355] that leave remainder 2 on division by 4 are 326, 330, 334, 338, 342, .... Now walk along that list from the bottom applying the other test, division by 3: 326 mod 3 = 2, rejected; 330 mod 3 = 0, rejected; continuing down the list, 334 mod 3 = 1, which is exactly what was asked. Both conditions hold for x = 334, and it lies in the given interval. \boxed{334}

*kstrat/goldbach-k2-8 — two distinct primes summing to 28, reference 5,23:*

- **Route A (scan upward):** Scan the primes p upward from the bottom and test whether the complement 28 - p is prime as well. p = 2: 28 - 2 = 26, and 26 = 2*13, composite. p = 3: 28 - 3 = 25, and 25 = 5*5, composite. p = 5: 28 - 5 = 23, which is prime. So 5 and 23 are distinct primes with 5 < 23 and 5 + 23 = 28. \boxed{5,23}
- **Route B (scan downward):** Come at the split from the large side: take the biggest prime q below 28 whose complement is also prime, working downward. q = 23: 28 - 23 = 5, which is prime. The larger prime is therefore 23 and its partner is 5, two distinct primes summing to 28. \boxed{5,23}

*kstrat/divcount-k2-5 — integer in [48, 147] with exactly 3 divisors, reference 121:*

- **Route A (factorization formula):** The divisor count of x is fixed by its prime factorization: if x = p1^e1 * p2^e2 * ... then x has (e1+1)(e2+1)... divisors. Factor candidates in [48, 147] and look for the count 3. Here 121 = 11^2, so its divisor count is (2+1) = 3, and 48 <= 121 <= 147. \boxed{121}
- **Route B (list divisors):** Walk through the range listing divisors outright. 120: divisors 1, 2, 3, 4, 5, ... — 16 of them, not 3. 121: divisors 1, 11, 121 — exactly 3 of them, which is the count required, and 121 sits inside [48, 147]. \boxed{121}

*kstrat/digitsum-k1-3 — 2-digit multiple of 5 with digit sum 4, reference 40:*

- **Route A (scan multiples):** Run through the multiples of 5 inside the 2-digit range and add up the digits of each one as we go. 30: digits 3+0 = 3, no. 35: digits 3+5 = 8, no. 40: digits 4+0 = 4, which is the required sum. So 40 is a 2-digit multiple of 5 with digit sum 4. \boxed{40}
- **Route B (digits first):** Build the digits before the number. We need 2 digits adding to 4; take 4, 0, since 4+0 = 4, which spells the 2-digit number 40. Now check the other condition by dividing: 40 = 5*8, so 40 is a multiple of 5 with no remainder. Both requirements are met. \boxed{40}

**How the judge sees them.** In the `refsol` condition the user message carries "Reference solution (trusted):" followed by route A in place of the bare answer; `refsol2` carries route B. The system rubric is the standard referenced one. Judges Qwen2.5-7B and phi-4, rubrics a and b. An independent verification confirmed the conditions were genuinely different: `ref` vs `refsol` scores differ on 75/75 items (mean absolute difference 0.807) and `refsol` vs `refsol2` on 75/75 (0.357).

**Three experiments use these references.**

1. **Worked vs bare reference (E1, P-W1).** Compare `refsol` to the standard bare-answer `ref`. A worked reference anchors *less*: margin +5.17 → +3.73 (Qwen-7B) and +4.20 → +3.67 (phi-4); inflation over blind +1.50 → +1.08 and +1.07 → +0.77. Still firmly positive, so a worked reference is milder, not safe. The direction was the opposite of the "more surface to match" intuition recorded at registration.

2. **Method rotation (H-METHOD, P-W2).** On the 15 k=1 items every valid sample carries the same final answer, so swapping route A for route B holds answer-matching constant by construction and varies only the derivation. Same-sample deltas (refsol2 minus refsol): −0.32 and −0.40 for Qwen-7B under the two rubrics, −0.02 for phi-4. A route-matching *differential* (samples whose own method matches the shown route faring better) appears in only one of four judge-by-rubric cells. Method effects are 20 to 400 times smaller than answer rotation (±9.5). The route classifier is a token-Jaccard heuristic with a small similarity margin (0.032), so the differential readout is weakly identified; the overall-shift readout is classifier-free.

3. **Masked worked reference (masking suite, third cell).** The derivation is kept intact but the boxed answer is replaced by `\boxed{hidden}` and every word-boundary occurrence of the answer integer by "(hidden)". Example, the crt item above:

   > The two requirements are x ≡ 1 (mod 3) and x ≡ 2 (mod 4). Since 3 and 4 are coprime, they collapse into a single condition modulo 3*4 = 12: adding 12 to any solution preserves both remainders. So the solutions inside [324, 355] form the arithmetic chain (hidden), 346. Take x = (hidden) from that chain: (hidden) = 3*111 + 1 and (hidden) = 4*83 + 2, and 324 <= (hidden) <= 355. \boxed{hidden}

   And the digitsum item:

   > Run through the multiples of 5 inside the 2-digit range and add up the digits of each one as we go. 30: digits 3+0 = 3, no. 35: digits 3+5 = 8, no. (hidden): digits 4+0 = 4, which is the required sum. So (hidden) is a 2-digit multiple of 5 with digit sum 4. \boxed{hidden}

   The reasoning still points at the answer (a reader can recover 334 from "3*111 + 1", and 40 from "digits 4+0"), but the token itself is gone. The margin collapses to zero on scalar families: +2.97 → +0.05 (Qwen-7B) and +3.51 → −0.49 (phi-4). For list families (subset, goldbach) the derivation may still name individual elements, so the registered masking prediction scores scalar families (crt, divcount, digitsum) only.

**What the three together show.** Reasoning in the reference reduces anchoring somewhat, the choice of reasoning route barely matters, and reasoning without the answer token does not anchor at all. The judge anchors on the answer, not the derivation.

**The other side: candidates always contain reasoning.** Every generation prompt asks the model to think step by step, and the judge sees the full sample text, not just its boxed answer. So the judge is always grading reasoning-plus-answer text; what varies is whether the *reference* has reasoning, and that is true only in the three experiments above. The one adjacent case is the MBPP code exemplar, which shows a full canonical solution (a complete artifact rather than a derivation plus answer) and did not inflate.

### 3.5 Masking-and-identity suite: what kind of "match" does the judge compute?

**The question.** By this point the paper had shown that the judge rewards candidates whose answer equals the reference and penalises candidates whose answer differs, even when both are correct. The distance-gradient analysis had shown the effect is a step at exact match, not a gradient. So the judge is doing some kind of equality check. But what kind? Three readings were on the table, and an external reviewer asked for them to be separated:

1. **Lexical.** The judge is pattern-matching characters: "31" in the candidate looks like "31" in the reference. A surface-level string comparison.
2. **Semantic.** The judge understands that the candidate's answer and the reference denote the same value, regardless of how either is written.
3. **Something that needs the answer to be present at all.** Perhaps the judge is using the reference's reasoning, not its answer, and a derivation alone would anchor.

**The design.** Three reference variants, each changing *only the string in the reference slot*. Samples, oracle labels, judge, and rubric are all frozen, so any change in the margin is caused by the reference's form. The anchoring margin is always computed against the item's **original numeral reference**: "matching" means the candidate's boxed answer equals the original "31", whatever the judge was shown. Predictions were committed before any variant judging (internal git registration), scored per judge on rubric a with rubric b as a replicate.

| Variant | Pool | What the judge sees for reference "31" | For a list reference "37,61" | Separates |
|---|---|---|---|---|
| **refword** | Replication (93 items with both classes present) | thirty-one | thirty-seven, sixty-one | Lexical vs semantic. Every character differs from the candidate's numeral, but the value is identical. |
| **refexpr** | Replication (93 items) | 30+1 | 36+1, 60+1 | Cheap vs computed equality. The value is identical, but recognising that requires one arithmetic step. |
| **masked worked ref** | k-stratified, k>1, scalar families (n=21) | Route-A derivation with `\boxed{hidden}` and every occurrence of the answer replaced by "(hidden)" | (list families exploratory only; masking leaks elements) | Whether the token is necessary. The reasoning is intact; the answer is absent. |

The **refword** construction converts each integer to English words (with hyphenated tens and "hundred"/"thousand"), element-wise for lists. The **refexpr** construction writes each integer n as "(n−1)+1". Both are semantically exact: "thirty-one" and "30+1" are 31.

**Registered predictions.** (The producer's header labels these P-MS1 to P-MS3. Those IDs collide with the Ministral-8B screen's P-MS1/P-MS2 already in `registration.md`, its ledger entry, added 2026-09-07, refers to them as "masking P-MS1..3"; the registration is the git commit of `build_refvariant_pools.py` and `maskident_analysis.py`.)
- **P-MS1 (semantic, not lexical):** the refword margin is positive with CI excluding zero for both judges. If the judge were pattern-matching characters, spelling the reference out in words would kill the margin.
- **P-MS2 (cheapness gradient):** the refexpr margin is smaller than the bare-reference margin (paired difference, CI excluding zero) for both judges, while remaining positive. If equality that must be computed anchors less than equality that can be read, the check is cheap rather than effortful.
- **P-MS3 (token necessity):** on scalar families at k>1, the masked worked-reference margin drops relative to the unmasked worked reference (paired difference excluding zero) for both judges, and the drop removes more than half of the unmasked margin.

**Results. All six cells confirmed (three predictions × two judges).**

| Condition | Qwen-7B margin (rubric a) | Change vs bare ref | phi-4 margin (rubric a) | Change vs bare ref |
|---|---|---|---|---|
| Blind (control) | −0.20 [−0.44, +0.02] | | +0.05 [−0.04, +0.14] | |
| **Bare numeral** (baseline) | +4.62 [+4.32, +4.96] | | +3.79 [+3.48, +4.11] | |
| **Words** ("thirty-one") | +2.88 [+2.47, +3.28] | −1.74 [−2.11, −1.35] | +3.68 [+3.27, +4.06] | −0.11 [−0.28, +0.05] |
| **Expression** ("30+1") | +0.29 [+0.07, +0.49] | −4.33 [−4.68, −4.01] | +0.89 [+0.64, +1.13] | −2.90 [−3.30, −2.57] |

| Masked worked reference (scalar families, n=21) | Qwen-7B | phi-4 |
|---|---|---|
| Unmasked worked reference | +2.97 | +3.51 |
| Answer masked, derivation intact | +0.05 [−0.52, +0.63] | −0.49 [−1.27, +0.26] |
| Drop | −2.92 [−3.61, −2.32], 98% of the margin | −4.01 [−4.71, −3.35], more than the whole margin |

Rubric b replicates every cell (Qwen-7B: bare +6.00, words +4.60, expression +0.35, masked +0.31; phi-4: bare +3.11, words +3.01, expression +0.63, masked −0.45).

**What each row means.**

- **Words preserve the margin.** phi-4's margin is statistically unchanged when the reference shares not one character with the candidate's numeral (+3.68 vs +3.79). Qwen-7B keeps about two thirds (+2.88 vs +4.62). The judge is not doing string matching. It recognises that a candidate's "31" and the reference's "thirty-one" are the same answer, and rewards that identity. This is what rules out the lexical reading.
- **Computation collapses the margin.** A single arithmetic step between the reference and the candidate removes 94% of Qwen-7B's margin and 77% of phi-4's. Both judges can certainly compute 30+1; what they do not do is compute it *in order to compare*. The equality check fires when identity can be read off and does not fire when it has to be derived. This is what "cheap" means: the anchoring is a recognition reflex, not a verification.
- **Masking kills the margin.** With the full derivation present but the answer token hidden, the margin goes to zero or slightly negative. The derivation still points unambiguously at the answer (a reader can recover 334 from "334 = 3*111 + 1" even with the 334 replaced by "(hidden)"), but the judge does not use it. It needs the token.

**The mechanism this triangulates.** The judge performs a *semantic equality check against a readable answer token*. Survive re-lexicalisation, die when equality must be computed, die when the token is hidden. All three legs are needed: words alone could mean the judge is doing something deep; the expression result shows it is shallow; the masking result shows it is about the token and not the reasoning.

**Why it matters for the rest of the paper.**
- It explains why instructions fail below frontier capability (§8.1): telling the judge "any correct answer deserves full credit" asks it to override a recognition reflex with a verification it does not perform.
- It explains why blind-then-reveal works through the *displayed number* (§8.4): the blind score is itself a readable token the judge can defer to in place of the reference token.
- It explains the code result (§7) and the continuum's judge-dependent residue (§7.1): a program has no cheaply readable answer token, so there is nothing for the reflex to fire on, while a two-line list comprehension is a marginal case where the output is recoverable at low cost.
- It bounds the scope: the harm requires a separable answer token that can be compared by recognition. Where equality needs computation (or the token is absent), the reference behaves as information rather than as an anchor.

**Disclosed limits.** The masked arm scores scalar families only, because for subset and Goldbach the derivation names individual elements ("Discarding 6, 20, 42 …") that partially reveal the answer. The refword and refexpr arms cover the replication pool only. All three variants change the reference the judge sees but not the candidates, so they cannot say what happens when the *candidate's* answer is re-lexicalised; that is listed as untested in the paper's limitations.

### 3.6 M1 blind-then-reveal and its variants (k-stratified pool)

Two judge calls per sample.

- **Call 1 (blind):** standard blind rubric.
- **Call 2 (M1):** referenced rubric plus "A correct answer that differs from the reference must keep the score you gave it; revise only if the reference reveals the candidate is actually wrong." User message ends with "Reference answer (one valid answer, trusted): … Your blind score for this candidate was 7.4 out of 10. Score:". The reported score is call 2.

Variants (registered decomposition):
- **m1noscore:** call 2 keeps the reference and the keep-correct instruction but omits the blind score.
- **m1prev / neutral framing:** "This candidate was already assessed blind, with no reference in view. […] A previous blind assessment scored this candidate 7.4 out of 10."
- **m1indep:** the *other* judge's blind score is shown in place of the judge's own, same wording.

### 3.7 M2 soft validity gate (k-stratified pool)

Call 1 is blind. A separate validity call, system: "You check answer validity. The question may have several valid answers. Answer with exactly one word: Yes if the candidate's final answer is a valid answer to the question, No otherwise. The reference is one valid example, not the only one." User: "Problem: … Reference (one valid answer): … Candidate solution: … Is the candidate's final answer valid?" Final score = blind score × P(Yes)/(P(Yes)+P(No)) from the answer token's logprobs. Registered as a hard gate (score or zero), implemented as this soft multiplier; amendment posted at osf.io/kszeu.

### 3.8 Frontier judge (k-stratified pool)

The 37 k>1 items where matching and non-matching valid samples coexist; up to 6 of each per item; blind and referenced, rubric a text verbatim from the open judges. 660 calls through a CLI path that returns a sampled integer. Only the margin is computed; no inflation, because an 11-value judge ties under best-of-64.

### 3.9 DPO training pairs (k-stratified pool)

Policy: Llama-3.1-8B-Instruct (the pool's generator, so pairs are on-policy). Pairs from the Qwen2.5-7B judge's scores on k>1 items: up to 8 pairs per item, minimum score gap 2.0, seed 0, 480 pairs per arm. Arms differ only in which protocol scored the pairs: single reference (ref arm), blind-then-reveal (m1 arm), or blind (blind arm, run 3 only). Evaluation: n=8 generations per item on the k>1 train items and on the 120 replication items as held-out, scored by the exact oracle and by the frozen judge.

### 3.10 Composition dose and 2-D factorial (replication + k-stratified pools)

No new judging. Sub-pools of already-scored samples are drawn so that exactly 4 valid answers are present, of which d ∈ {0,1,2,4} match the reference (dose experiment; 24-sample sub-pools, 48 eligible items), or d ∈ {0,2,4} matching valids crossed with ℓ ∈ {0,3,6} invalid samples that contain the reference's text (2-D factorial; 14-sample sub-pools, 24 items). Best-of-n over each sub-pool is arithmetic on existing scores.

---

## 4. Quick reference: which pool carries which result

| Result in the paper | Pool | Generator | Judges |
|---|---|---|---|
| Headline +1.19 SD inflation (§3) | Replication | Llama-8B | Qwen-7B, phi-4 |
| Rotation up to +9.5 points (§4.0) | Ties | Qwen-7B | Qwen 1.5B–14B |
| Rotation replication 12/12 (§4.1) | Replication | Llama-8B | Qwen-7B, phi-4 |
| Composition dose, 2-D factorial, distance (§4.2) | Replication + k-stratified | Llama-8B | Qwen-7B, phi-4 |
| Masking suite 6/6 (§4.3) | Replication (words, expression) + k-stratified (masked) | Llama-8B | Qwen-7B, phi-4 |
| Six-judge step (§5.0) | Synthetic grid | Qwen-7B (+ Llama-8B) | 6 judges |
| Registered step +1.45 / +1.18 (§5.0) | k-stratified | Llama-8B | Qwen-7B, phi-4 |
| Third-party inversion (§5.1) | MACE | Llama-8B | Qwen-7B, phi-4 |
| Frontier 82.5% vs 19.6% (§6.1) | k-stratified (37 items) | Llama-8B | frontier CLI |
| Blind-certified filter (§6.2) | Ties + replication | — | Qwen ladder; Qwen-7B, phi-4 |
| DPO wedge +4.13 (§6.3) | k-stratified (train) + replication (held-out) | Llama-8B policy | Qwen-7B |
| Code exemplar falsified (§7) | MBPP | Qwen-7B | Qwen-7B, Qwen-14B |
| Continuum attenuation (§7.1) | Separability | Llama-8B | Qwen-7B, phi-4 |
| Instruction placebo, multiref (§8.1–8.2) | Synthetic grid | Qwen-7B, Llama-8B | 6 judges |
| Worked reference, method rotation (§8.3, §9) | k-stratified | Llama-8B | Qwen-7B, phi-4 |
| M1, M2, M1 variants, coverage (§8.4–8.5) | k-stratified | Llama-8B | Qwen-7B, phi-4, gemma-2-9b, Mistral-7B, Qwen-14B |
| Score-resolution screen (§8.6) | k-stratified | Llama-8B | 5 judges + Ministral-8B |
