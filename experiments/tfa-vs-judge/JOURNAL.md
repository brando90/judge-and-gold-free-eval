# Experimental Journal — judge-free evaluation via TFA and successors

A detailed running narrative of what we've tried, what failed, and what we're testing now.
For the crisp final conclusions see [RESULTS.md](RESULTS.md); for the raw chronological log see [RESULTS_LOG.md](RESULTS_LOG.md).

---

## 0. The question
Can a **cheap, deterministic, judge-free** signal replace an LLM judge for evaluating reasoning? Two regimes:
- **Model level** — rank models (leaderboard) without a judge.
- **Item level** — grade a *single response*'s reasoning quality without a judge. **This is the hard one and the whole fight.**

**Decision metric (used everywhere):** the **partial Spearman correlation** `ρ(signal, judge | correct)` — does the
signal track a frontier LLM judge's reasoning-quality score *beyond* the free boxed-answer-correctness bit? A judge
earns its keep beyond correctness, so this partial is the right bar. ≈ 0 means "no item-level signal."

**Fixed setup.** Qwen2.5-Instruct ladder {0.5B, 1.5B, 3B, 7B, 14B, 32B} × MATH-500 (500 problems → 3000 items).
Per (model, problem): **TFA** (teacher-forced argmax-match on the gold solution, vLLM), **boxed-correctness** of the
model's free-gen (Math-Verify), **judge** = gpt-5.2 (0–10 rubric on the free-gen). Skampere1 A100s.

---

## 1. Core result — TFA works at the model level, fails at the item level
- **E0 (metric correctness):** vLLM TFA == HF ground-truth teacher-forcing, exact. TFA is computed correctly.
- **E1 (model level):** ρ(mean-TFA, accuracy) = **+0.94**; ρ(mean-TFA, mean-judge) = **+0.94** (n=6). TFA ranks models
  like accuracy and like the judge. Reproduces & exceeds Putnam-AXIOM's ~0.66.
- **E2 (item level):** partial ρ(TFA, judge | correct) = **−0.02** (raw −0.03; within-correct −0.06). **No per-response signal.**

**Why item-level fails (mechanism).** Gold-trace length is an *adversarial confound*: longer/formulaic gold is more
predictable → **higher TFA (+0.34)** but marks harder problems the judge rates lower → **lower judge (−0.33)**. The two
effects run through gold-length in opposite directions, so TFA and the judge are pushed apart. Fundamentally **TFA
measures predictability of the *reference*, not quality of the model's *own* reasoning.**

---

## 2. TFA variations tried to recover item-level signal — and their outcomes

| Variation | Idea | Item-level `partial \| correct` | Verdict |
|---|---|---|---|
| **content-token TFA** | mask formatting/LaTeX glue (shortcut control) | ~0 | ❌ null persists (not a formatting artifact) |
| **TFA-logprob / BPC** | soft gold-token logprob instead of argmax | ~0 (−0.11 within-correct) | ❌ soft variant no better |
| **surprisal-weighted TFA** | down-weight low-surprisal (formulaic) gold tokens | **−0.16** | ❌ *worse* than baseline |
| **IDF-weighted TFA** | down-weight corpus-frequent gold tokens | −0.01 | ❌ ≈ baseline |
| **contrastive TFA (answer-swap)** | TFA(gold) − TFA(answer-corrupted gold) | apparent **+0.18** → **−0.02** | ❌ **ARTIFACT (retracted)** |
| **contrastive TFA (step-shuffle)** | TFA(gold) − TFA(step-shuffled gold) | −0.13 | ❌ fails |
| **multi-reference TFA** | max TFA over K verified gold solutions | not run | (expected: fixes only the alternate-path half) |

### What each variation actually is (mechanics + why it failed)

Baseline **TFA** = teacher-force the model on the gold solution and score the fraction of gold tokens where the
model's argmax next-token equals the gold token. All variations below modify *how* or *what* we score.

1. **content-token TFA (shortcut control).** Same as TFA but **mask out "glue" tokens** — whitespace, LaTeX
   delimiters (`{ } $ \frac …`), punctuation — and score argmax-match only over "content" tokens. *Rationale:* maybe
   raw TFA is inflated by trivially-predictable boilerplate that drowns the real signal. *Result:* item-level null
   persists (~0) → the failure is **not** a formatting artifact; the content tokens carry no per-item signal either.

2. **TFA-logprob / BPC.** Replace the hard 0/1 argmax-match with the **soft gold-token log-probability** (how much
   probability mass the model puts on each gold token), averaged over the trace (equivalently bits-per-token).
   *Rationale:* argmax is coarse; a soft confidence might carry more. *Result:* ~0 (−0.11 within-correct) → the
   coarseness of argmax was not the problem; the soft version is no better (slightly worse).

3. **surprisal-weighted TFA.** Weight each gold token's match by its **surprisal** (self-information `−log p` under the
   model), so *predictable/formulaic* tokens (low surprisal) count little and *surprising* tokens count more.
   *Rationale:* down-weight boilerplate to isolate load-bearing reasoning tokens. *Result:* **−0.16 (worse).** The
   high-surprisal tokens are exactly the hard reasoning tokens even good models miss, so up-weighting them adds noise.

4. **IDF-weighted TFA.** Like (3) but weight by **corpus inverse-frequency** — gold tokens that are rare across the
   whole gold-solution corpus weigh more; frequent ones less. A *model-independent* notion of informativeness.
   *Rationale:* same "down-weight the boilerplate" idea, without depending on the model's own probabilities.
   *Result:* ≈ baseline (−0.01) → reweighting frequent tokens doesn't create signal.

5. **contrastive TFA (answer-swap).** `TFA(gold) − TFA(answer-corrupted gold)`, where the corrupted gold is identical
   except its final `\boxed{}` answer is changed to a wrong value. *Rationale:* a good reasoner should predict the
   *correct*-answer gold better than a wrong-answer one, and differencing cancels the length/formulaic baseline.
   *Result:* looked positive (+0.18) but was an **artifact** (retracted; see the cautionary tale below).

6. **contrastive TFA (step-shuffle).** `TFA(gold) − TFA(step-shuffled gold)`, where the corrupted gold has its
   reasoning lines/sentences **reordered** (length exactly preserved, so no `1/N` artifact). *Rationale:* a coherent
   reasoner should predict the correctly-ordered gold better than a scrambled one. *Result:* **−0.13.** Shuffling
   destroys *global* coherence, but next-token prediction is *local* — the model doesn't track global step-order
   through local logprobs, so the contrast is uninformative.

7. **multi-reference TFA (not run).** Use **K diverse, answer-verified gold solutions** per problem and take
   `max_k TFA(gold_k)`. *Rationale:* single-gold TFA penalizes valid *alternate* reasoning paths (the
   low-TFA/high-judge failure mode); crediting the best-matching reference removes that penalty. *Expected:* fixes
   only **half** the null — the alternate-path (short/clever gold) side — but not the length/formulaic (long gold)
   side, which is bidirectional. So insufficient alone; not prioritized.

### The `contrast_answer` cautionary tale (why we now stress-test everything)
`contrast_answer` first looked like a win (+0.35). On scrutiny it was a **`1/gold_length` artifact**: because the
corruption changes only the answer token, `contrast_answer ≈ [predicts correct answer]/N`, dominated by inverse gold
length (Spearman +0.67), which re-imports the length confound with a favorable sign. Stripping the `1/N` magnitude
(length-independent bit) gave partial +0.01; controlling for correctness **and** length gave **−0.02**. Retracted.
**Lesson baked into the process:** any positive item-level result must survive controlling for its plausible confound
(length, difficulty) before we believe it.

### Weighting can't manufacture absent signal
Ideas that *reweight* the same gold-prediction (surprisal, IDF, content-mask) all fail, consistent with the deep
analysis: the item-level signal is *absent* under gold-prediction, not hidden under the confound — residualizing the
confound leaves nothing. **The fix has to change *what is measured*, not reweight it.**

---

## 3. Instrumentation bug found & fixed (didn't change conclusions)
`answers_equivalent` parsed answers without `$…$`, so Math-Verify mis-parsed non-scalar answers → **247 false
negatives + 25 false positives** (9.1% of labels; accuracy underestimated ~7 pts). **Fixed** (`tfa/boxed.py`).
Re-scoring under corrected labels: item-level partial −0.035 → −0.019 (still ≈0); model-level ρ +0.94 (unchanged).
Verified with instrumentation that Math-Verify actually decided the labels (0 exceptions, 0 string-fallbacks).

---

## 4. Current direction — rollout process value (Math-Shepherd style, fixed strong completer)

**Rationale.** Every gold-anchored TFA variant failed because it measures the *reference*, not the model's own
reasoning, and the literature says per-step *quality* needs rollouts or process labels (Math-Shepherd, OmegaPRM;
see [`../../docs/fixing-tfa-item-level.md`](../../docs/fixing-tfa-item-level.md)). So we changed the object entirely.

**Design.** For each stored response, truncate the model's *own* free-gen at cut-points `f ∈ {0, .25, .5, .75}`, let a
**fixed strong completer (Qwen2.5-32B)** *continue* the prefix K=8 times, and check answers with Math-Verify →
`V(f) = P(reach correct answer | prefix)`. Using a *fixed* completer decouples the value from the evaluated model's
capability (kills weak-completer noise, makes scores comparable). `V(0)` = completer's base solve-rate = a wash-out /
difficulty diagnostic. Features: `meanV`, `lastV = V(.75)`, `lift = meanV − V(0)`.

**First result (150 responses: 1.5B/7B/14B × 50 problems, 110 correct / 40 wrong):**

| feature | `r(·,judge)` | `partial \| correct` (95% CI) | `partial \| correct & V(0)` | within-correct | within-wrong |
|---|---|---|---|---|---|
| meanV | +0.45 | **+0.36 [0.19, 0.51]** | +0.38 | +0.12 (CI incl. 0) | +0.69 (n=40) |
| lastV | +0.52 | **+0.46 [0.29, 0.61]** | +0.62 | −0.06 | +0.79 |
| lift  | +0.42 | **+0.33 [0.17, 0.47]** | +0.51 | +0.15 | +0.65 |

**Reading the table.** The value is `V(f) = P(the fixed 32B completer reaches the correct answer | problem + first
f-fraction of the model's own response)`, estimated from K=8 rollouts. The rows are three summaries of the value
*trajectory* `V(0), V(.25), V(.5), V(.75)`; the columns are increasingly strict tests against the judge.

*Rows (features of a response's value trajectory):*
- **meanV** — average value over the non-zero cut-points (.25/.5/.75). "On average, how solvable does this response's
  reasoning keep the problem?" A level summary.
- **lastV = V(.75)** — the value after ~75% of the response. "Does the reasoning end *on-track*?" Empirically the
  strongest single feature — the state near the end of the derivation best summarizes whether it stayed valid.
- **lift = meanV − V(0)** — the value *net of the problem's base difficulty*. `V(0)` is the completer solving from the
  problem alone (no prefix); `lift` isolates how much *this response's reasoning* raises (helps) or lowers (misleads)
  the completer's odds versus starting from scratch. This is the "prefix-specific" effect with base difficulty removed.

*Columns (tests of increasing strictness):*
- **r(·, judge)** — raw Spearman with the judge over all 150 responses. Inflated: both the feature and the judge
  partly track correctness, so this over-states the real signal.
- **partial | correct (95% CI)** — the decisive metric: Spearman controlling for the binary boxed-correct bit, with a
  bootstrap CI. "Does the feature track the judge *beyond* free correctness?" CI excluding 0 = genuine item-level signal.
- **partial | correct & V(0)** — additionally control for `V(0)` (the completer's base solve-rate ≈ problem difficulty).
  This is the **artifact check**: if the signal is really just problem difficulty driving both V and the judge, it dies
  here. It *strengthens* instead — the opposite of `contrast_answer`, which collapsed under its length control.
- **within-correct / within-wrong** — Spearman among *only* correct answers (n=110) / *only* wrong answers (n=40).
  These localize *where* the signal lives: separating good-from-bad reasoning among already-correct answers
  (within-correct) vs. separating near-miss from incoherent wrong answers (within-wrong).

**What the numbers say.** `lastV` is the best feature (partial +0.46, and +0.62 once difficulty is removed) — being
*on-track near the end* matters most. The signal is almost entirely in the **wrong stratum** (within-wrong +0.65…+0.79):
a wrong answer whose prefix a strong completer can still finish correctly (high V) had *coherent* reasoning and the
judge scores it higher; a wrong answer that derails the completer (low V) was *incoherent* and the judge scores it low.
Among **correct** answers the value **saturates** (they reach the answer, so V stays high) → within-correct ≈ +0.12
with a CI that includes 0 → no reliable signal in the hard, valuable case. And `V(0)=0.946` means the 32B nearly always
solves these problems anyway, so `lift` is mostly slightly negative (a weaker model's prefix marginally *hurts* a
near-oracle) and it is the *variance* in that lift — not its level — that carries the information.

**This is the first item-level signal that survives scrutiny.**
- CIs exclude 0.
- **Survives controlling for problem difficulty** (V(0)) — it *strengthens*, the opposite of `contrast_answer`, which
  died under its confound control. So it is **not** a difficulty artifact.

**But — honest caveats (this is a lead, not a solved problem):**
- **Concentrated in the *wrong* stratum** (within-wrong +0.69; within-correct +0.12 with CI including 0). It separates
  *near-miss* wrong answers (coherent reasoning the 32B can still complete → high V, judge scores higher) from
  *incoherent* wrong answers (low V, judge low). It does **not** yet separate good-from-bad reasoning among *correct*
  answers — the harder, more valuable case, where V saturates.
- **Partly a graded-correctness signal.** `V = P(reach correct answer)`, so within the wrong stratum "higher V" ≈ "closer
  to correct." For math that *is* a legitimate reasoning-quality proxy (a near-miss reasons better than nonsense) and
  the judge agrees — but it's a *soft/graded correctness* signal more than reasoning-quality-independent-of-correctness.
- **Partial wash-out:** the 32B solves 94.6% from scratch (V(0)=0.946), so the base rate is near-saturated; the *lift*
  over base rate is what carries information. A mid-strength completer might reduce this.
- **Small subset:** 50 problems, 40 wrong items. Needs scale-up.

---

### Scaled result (450 responses) + completer comparison
Repeated on **150 problems × 3 models = 450 responses** (323 correct / 127 wrong), with **two completers** (mid-strength
14B and strong 32B) to test wash-out sensitivity:

Completer-strength curve (meanV feature; n=323 correct / 127 wrong):

| completer | V(0) base | `partial \| correct` (95% CI) | **within-correct** (n=323) | within-wrong |
|---|---|---|---|---|
| 7B (too weak) | 0.823 | +0.33 [0.24, 0.41] | +0.09 [−0.02, 0.20] (n.s.) | +0.73 |
| **14B (sweet spot)** | 0.878 | **+0.43 [0.35, 0.51]** | **+0.19 [0.09, 0.29]** ✓ | +0.73 |
| 32B (too strong) | 0.906 | +0.37 [0.27, 0.45] | +0.08 [−0.02, 0.19] (n.s.) | +0.67 |

**Findings.**
1. **Signal holds at scale and replicates across completers** (partial +0.33→+0.44, tight CIs, survives difficulty
   control). This is a robust, non-artifact, judge-free item-level signal — the first in the whole investigation.
2. **Completer strength is an inverted-U (Goldilocks); 14B is the sweet spot.** Both *too weak* (7B: fails to finish
   even good prefixes → noisy V) and *too strong* (32B: re-solves regardless of the prefix → V(0)=0.91 wash-out) are
   worse than 14B on both overall partial and within-correct. **Design rule: use a *mid-strength* completer — capable
   enough that success reflects the prefix, not so capable the prefix is irrelevant.**
3. **The decisive within-correct test flips positive only at the sweet-spot completer: 14B gives +0.19 [0.09, 0.29]
   (CI excludes 0); 7B and 32B are ≈+0.08 (n.s.).** The grade-among-correct signal is *real but fragile* — it exists,
   but only at the right completer strength, and even then it is weak (+0.19).
   So the rollout value *does* weakly-but-significantly separate *valid-correct from lucky-correct* — the marquee case
   TFA and every variant failed at (≈0). It is far weaker than the wrong-stratum (+0.73, near-miss vs. incoherent), so
   most of the signal is still graded-correctness, but there **is** real signal in the hard case.

**Updated verdict.** The rollout process value *partially solves the underlying "judge-free per-response reasoning
signal" problem* — robust, difficulty-controlled, replicated, and it even cracks (weakly) the grade-among-correct
case. It is **not** TFA and **not** cheap (~K·T× cost, sampled), so it's a **process-reward / soft-verifier**, not the
proposal's cheap deterministic judge-replacement. But as a judge-free signal grounded in an objective answer-oracle, it
works where every gold-prediction variant failed.

## 4b. Workstream A — TFA baselines across NL-math datasets (MATH, GSM8K, Putnam-AXIOM)
Extended the TFA picture to **6 datasets** × the Qwen2.5 {0.5B,1.5B,3B,7B,14B} ladder (identical 5-model ladder
everywhere; 32B also run on MATH-500 but dropped from this table for apples-to-apples). Judge = gpt-5.2; correctness via
`$`-delimited Math-Verify (boxed-first extraction). Human-facing summary + figures in `paper/` (`PAPER.md`, `figs/`,
`summary.json`); regenerate with `scripts/make_figures.py` + `scripts/analyze_workstream_a2.py`.

| dataset | n | acc | TFA range | ML ρ(TFA,acc) | ML ρ(TFA,judge) | item `partial\|corr` (CI) | `\|corr&len` | w-corr | w-wrong |
|---|---:|---:|---|---|---|---|---|---|---|
| MATH-500          | 2500 | 0.60 | 0.76–0.82 | +0.90 | +0.90 | **−0.01** [−0.05,+0.04] | +0.08 | −0.05 | +0.06 |
| MATH-full (alg.)  | 2999 | 0.77 | 0.75–0.80 | +0.60 | +0.60 | **+0.02** [−0.02,+0.05] | +0.04 | +0.02 | +0.08 |
| GSM8K             | 2500 | 0.75 | 0.81–0.84 | +0.70 | +0.90 | **+0.115** [0.08,0.16] | +0.11 | +0.04 | +0.29 |
| GSM8K-Platinum    | 2500 | 0.78 | 0.81–0.84 | +0.60 | +0.70 | **+0.063** [0.02,0.10] | +0.09 | +0.03 | +0.22 |
| Putnam            | 1180 | 0.10 | 0.70–0.77 | +1.00 | +1.00 | **+0.218** [0.16,0.27] | +0.24 | +0.28 | +0.21 |
| Putnam-Variations | 1325 | 0.12 | 0.68–0.76 | +0.90 | +1.00 | **+0.145** [0.09,0.20] | +0.17 | +0.16 | +0.13 |

**Findings.**
1. **Model-level TFA holds everywhere** (ρ(mean-TFA, judge) = +0.60→+1.00). Strongest on the *hardest* data (Putnam
   ρ=+1.0, range 0.70–0.77) — **the "weak-model floor" fear is inverted.** It can *degrade to +0.60* on saturated
   single-subject data (MATH-full algebra, GSM8K-Platinum), where the 5 models sit in a ~0.03–0.05 TFA band. Still always
   positive and usable for ranking.
2. **Item-level is a FAMILY effect, not a smooth accuracy gradient:** MATH ≈0 (both subsets, CI straddles 0) → GSM8K
   +0.06…+0.12 → **Putnam +0.15…+0.22**, all length-robust (they *strengthen* under length control). Mechanism =
   **TFA de-saturation**: range widens 0.03 (easy) → 0.07 (hard), so predicting the gold starts to reflect genuine
   competence the judge rewards. Note GSM8K (acc 0.75) ≫ MATH-full (acc 0.77) in item-signal despite equal accuracy — so
   it's dataset family, not accuracy per se. Still **modest (≤+0.22)** — not judge-replacing.
3. **Label-noise (GSM8K → Platinum):** item signal roughly **halves** (+0.115 → +0.063), CI still >0. Part of GSM8K's
   per-item signal was coupled to label noise; the rest is real. *Caveat: overlapping-but-not-identical item sets, so
   directional not a paired ablation.*
4. **Contamination (Putnam → functional Variations):** item signal attenuates ~⅓ (+0.218 → +0.145) but stays robustly
   >0 (CI [0.09,0.20]) → **not a memorization/contamination artifact**; genuine competence signal survives functional
   variation. Model-level stays +1.0.
5. **Scale (MATH-500 → MATH-full, n≈3000):** the MATH item-null **confirmed at scale** (both ≈0).

**Critic / bugs caught this batch.**
- **Judge crash on content filter:** one MATH-full prompt tripped OpenAI `ContentPolicyViolationError`; unhandled, it
  killed the whole 3000-item judge run (0 rows written). Fixed `scripts/run_judge.py` to catch per-item exceptions → `None`
  (skipped, already filtered downstream). Re-judged: 0.5B 599/600 (1 flagged item skipped), rest 600/600.
- **Data-completeness caught by moving analysis local (per user):** the SNAP MATH-500 re-run globbed only 3 of 6 model
  files (n=1500 → wrong ML/IL); the local copy has the full ladder. Also `math_verify` missing in the fresh local venv
  silently degraded `answers_equivalent` to string-match (MATH-500 acc 0.64→0.57) until installed. **Lesson: verify
  `math_verify` present and the full file set before trusting numbers.** Local venv = `.venv-local` (numpy/scipy/
  matplotlib/math-verify).
- **Consistency:** 32B only run on MATH-500 → dropped from the cross-dataset table/figures (5-model ladder everywhere).
- (Earlier, still relevant) GSM8K/Putnam acc-0.000 extractor bugs and env-file OpenAI-key corruption — all fixed; see git.

**Caveats.** Single judge (gpt-5.2); Qwen-only responses; MATH-full = algebra subject only; Putnam correct-stratum small
(acc≈0.10, so the robust Putnam part is within-wrong +0.21); Math-Verify FP-prone on complex Putnam answers.
**Workstream A (breadth) is complete** — all planned NL-math datasets run, judged, analyzed, and figured.

## 4c. Workstream D2 — cross-family / cross-tokenizer generalization (is it Qwen-specific?)
Added three instruction-tuned families with **distinct tokenizers** — `mistralai/Mistral-7B-Instruct-v0.3`,
`microsoft/phi-4` (14B), `allenai/OLMo-2-1124-13B-Instruct` — on the three anchor datasets (MATH-500, GSM8K,
Putnam-AXIOM original), same harness, judge = gpt-5.2. Analysis: `scripts/analyze_d2.py` (pooled + family-stratified),
figure `paper/figs/fig6_cross_family.png` (`scripts/make_d2_fig.py`), slim scores `runs/scores_d2.jsonl`.
Llama/Gemma are HF-gated (403 on the current token) → deferred; Qwen3 deferred (default *thinking* mode is not
comparable to the non-thinking Instruct baseline).

**Model-level ρ(mean-TFA, judge): cross-family ranking is saturation-limited.**

| dataset | within-Qwen | pooled cross-family (4 families) |
|---|---|---|
| MATH-500 | +0.94 | **+0.90** |
| Putnam   | +1.00 | **+0.88** |
| GSM8K    | +0.90 | **−0.07** (collapse) |

On hard/unsaturated data cross-family ranking survives; on **saturated GSM8K it collapses** — all models pin into a
narrow TFA band (0.79–0.84) with a **family-specific offset**. Mistral is the poster child: TFA 0.80 (Qwen-like) but
judge 6.6 / acc 0.56, vs Phi-4 TFA 0.79 but judge 9.7 / acc 0.94. TFA measures reference-predictability-under-the-model,
which carries a family baseline that only stays negligible when the data de-saturates the models. **This qualifies the
"judge-free model ranking is solved" claim → solved *within a family*, or across families only on unsaturated data.**

**Item-level partial ρ(TFA, judge | correct), family-stratified.**

| family (n per dataset) | MATH-500 | GSM8K | Putnam |
|---|---|---|---|
| Qwen2.5 | −0.02 | +0.115 | +0.218 |
| Mistral | −0.01 | **+0.103** [0.03,0.18] | +0.118 [−0.00,0.24] |
| OLMo    | −0.14 | +0.03 (n.s.) | +0.04 (n.s.) |
| Phi-4   | −0.13 | −0.05 (n.s.) | +0.03 (n.s.) |

- **The MATH null is family-robust** (every family ≈0 to slightly negative; none positive). ✓
- **The GSM8K positive reproduces in Qwen (+0.115) and Mistral (+0.103)** but **vanishes in Phi-4/OLMo**, which are
  accuracy-*saturated* on GSM8K (0.94/0.91) → no within-correct spread to grade.
- **The Putnam +0.22 is essentially a Qwen result**; new families have tiny correct strata (acc 0.03–0.19) → wide CIs,
  cannot confirm. So the difficulty-gradient positives need *both* an unsaturated dataset *and* enough correct-varied
  solutions — conditions Qwen meets best.

**Critic / bug caught (double-check mandate again).** The first pooled ρ read −0.87 on GSM8K — an **artifact**: the old
Qwen `.judged.jsonl` files store the pre-fix buggy `boxed_correct=0` (the ####-extraction bug) for GSM8K/Putnam.
Recomputing correctness with the fixed scorer (`answers_equivalent`/`extract_final_answer`) for **every** model gives the
clean numbers above; the qualitative collapse (GSM8K) and survival (MATH/Putnam) are unchanged. Also verified the
non-Qwen TFA is mechanically sound (healthy 0.44–0.96 ranges; Mistral's low acc is real, not an extraction failure —
spot-checked wrong items). MATH-500 finalized on the **complete local** ladder (cluster had only 3 of 6 Qwen files).

**Deferred D2 extensions:** gated Llama-3.x / Gemma-2 (need license acceptance), non-thinking Qwen3, and a second size
per new family (to test *within-new-family* model-level ρ, impossible with one model each).

## 5. Where we are / next steps
1. **Scale the rollout-PRM** — more problems and models, and step-level cut-points (not just 4 fractions), to tighten
   CIs and get power in the correct stratum.
2. **Mid-strength completer** (e.g. 14B) to cut the 94.6% base-rate wash-out and test whether the signal holds.
3. **The open hard question:** can *any* judge-free signal separate good-from-bad reasoning among *correct* answers?
   So far every signal (TFA and rollout-PRM alike) is ≈0 there. That may be the true limit.
4. **Framing:** even in the best case, the rollout-PRM is a costly (~K·T× TFA) soft-correctness signal, not a cheap
   drop-in judge. TFA's validated niche remains model-level ranking.

## Standing conclusions
- **Judge-free model-level ranking: solid** (TFA, ρ ≈ 0.94).
- **Judge-free item-level grading: partially solved (by a costly process signal, not by TFA).** No cheap gold-anchored
  TFA variant works (all ≈0 or artifacts). The **rollout process value** with a mid-strength (14B) completer gives a
  robust, replicated, difficulty-controlled item-level signal: `partial ρ(·, judge | correct) = +0.44` [0.35, 0.51],
  and — crucially — a **weak but significant within-correct signal (+0.19 [0.09, 0.29])**, cracking the grade-among-correct
  case that TFA totally failed. It is a **process-reward / soft-verifier** (judge-free, oracle-grounded), not a cheap
  deterministic judge-replacement; the bulk of its signal is still near-miss detection in the wrong stratum (+0.73).
