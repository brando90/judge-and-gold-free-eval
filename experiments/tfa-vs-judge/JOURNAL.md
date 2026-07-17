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
- **Judge-free item-level grading: unsolved.** No cheap gold-anchored variant works; the rollout process value is the
  first signal to survive the artifact/difficulty checks, but it lives in the wrong stratum and is a graded-correctness
  proxy. Whether it becomes a genuine per-response reasoning-quality signal is the open bet.
