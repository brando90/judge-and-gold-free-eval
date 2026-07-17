# Results — TFA vs. the LLM judge (first run, MATH-500)

**Setup.** Qwen2.5-Instruct capability ladder (0.5B, 1.5B, 3B, 7B, 14B, 32B) on MATH-500 (500 problems).
Per (model, problem) we compute: **TFA** (teacher-forced argmax-match on the gold solution, vLLM),
**boxed correctness** of the model's free-generated solution (Math-Verify), and a **frontier LLM-judge**
reasoning-quality score (`gpt-5.2`, 0–10 rubric on the free-gen trace). Run on skampere1 (A100s).

## E0 — metric correctness (PASS)
vLLM TFA matches the HF ground-truth teacher-forcing **exactly** on argmax and to ~1e-3 on logprob
(`scripts/verify_backends.py`). The TFA implementation is trustworthy.

## E1 — reproduction: TFA ↔ boxed accuracy (CONFIRMED)

| Model | mean-TFA | accuracy | mean-judge (0–10) |
|---|---|---|---|
| 0.5B | 0.762 | 0.266 | 3.35 |
| 1.5B | 0.796 | 0.462 | 5.45 |
| 3B | 0.795 | 0.594 | 6.92 |
| 7B | 0.801 | 0.632 | 7.65 |
| 14B | 0.815 | 0.690 | 8.00 |
| 32B | 0.819 | 0.730 | 8.32 |

- **Model-level ρ(mean-TFA, accuracy) = +0.94** (Pearson 0.96) — reproduces and exceeds the paper's ~0.66.

## E2 — the crux: does TFA track the judge, per response? (NEGATIVE at item level)

**Two levels, opposite answers:**

- **Model level (positive):** ρ(mean-TFA, mean-judge) = **+0.94** (n=6, CI [0.52, 1.00]).
  TFA ranks models the same way a frontier judge does.
- **Item level (negative):** pooled ρ(TFA, judge) = **−0.03**; the decisive
  **partial ρ(TFA, judge | correct) = −0.035, 95% CI [−0.071, +0.001]** — indistinguishable from zero
  (slightly negative). Among correctly-solved problems it is −0.10 (CI [−0.15, −0.05]).
  Sanity: the judge itself is meaningful — ρ(judge, correct) = +0.72.

**Verdict: NEGATIVE.** TFA carries **no per-response reasoning-quality signal** beyond the free boxed-correctness bit.

### Supporting diagnostics (E1 data)
- Item-level ρ(TFA, correct) ≈ 0 (−0.01) both pooled and within every model (−0.02 to −0.12).
- Per-item TFA is confounded by **gold-trace length** (ρ ≈ +0.37): longer, more formulaic gold scores
  higher. Gold length anti-correlates with correctness (ρ ≈ −0.31), so the two effects cancel.
- The **content-token variant** (masking formatting/LaTeX glue — the shortcut control) halves the
  gold-length confound (+0.37 → ~+0.2) but still shows **no** item-level correlation with correctness.
  So the null is not a formatting artifact.

## Takeaway
On MATH, **TFA is a valid judge-free *model-ranking* signal** (ranks models like accuracy and like a
frontier judge, cheaply and deterministically) but **is not a per-response judge replacement** — it has
no item-level correlation with judged reasoning quality. This is the "precise negative" the plan flagged
as a legitimate outcome, and it sharply scopes the contribution: *judge-free leaderboarding, yes;
per-response grading, no.*

## Caveats / next
- Model-level n=6 (wide CI); add more families (Llama, Mistral) and sizes to firm it up.
- TFA is compressed/saturated on MATH (0.76–0.82); harder sets (Putnam-AXIOM) may give more range —
  but the collaborator's weak-model floor concern applies.
- Single judge (`gpt-5.2`); a second family bounds self-preference (the Anthropic key in the provided
  `.env` was rejected as invalid, so cross-family judge is TODO).
- Prompting is raw completion-style (not chat-templated); accuracies are sane but a chat-template pass
  is a cheap robustness check.

---

# Appendix: what the metrics mean, and how they were computed

## The three raw per-(model, problem) measurements
Note *what each is measured on* — this asymmetry drives everything.

| Quantity | Measured on | How | Range |
|---|---|---|---|
| **TFA** (`tfa_argmax`) | the **gold** solution (teacher-forced) | feed the model the gold tokens; at each position check if the model's argmax next-token equals the gold token; TFA = fraction matching (`tfa/core.py`) | [0,1] |
| **boxed-correct** | the model's **own** free generation | free-solve, extract `\boxed{}`, check equality with gold answer via Math-Verify (`tfa/boxed.py`) | {0,1} |
| **judge** | the model's **own** free generation | show gpt-5.2 the problem + gold + the model's solution, rate the *reasoning* 0–10 (`tfa/judge.py`) | [0,10] |

TFA never sees the model's own output — it only measures how *predictable the gold trace* is to the model. The premise is that predicting an expert proxies for one's own reasoning quality.

## Spearman ρ, and item-level vs. model-level
Spearman ρ is a rank correlation (+1 monotone-up, 0 none, −1 monotone-down); used over Pearson because relationships are nonlinear and the judge scale is skewed. Two distinct questions:
- **Item-level:** each (model, problem) is a point → 3000 points. "Across responses, does higher TFA go with a higher judge score?" (Can TFA grade a response?)
- **Model-level:** average each model's 500 items → 6 points. "Across models, does higher mean-TFA go with higher mean-judge?" (Can TFA rank models?)

## The decisive metric: partial correlation ρ(TFA, judge | correct)
The judge is largely driven by correctness (item-level r(judge, correct) = **+0.72**). So a raw r(TFA, judge) could be "real" only via correctness, which is free (Math-Verify). The partial correlation removes the rank-association explained by correctness from *both* TFA and judge, then correlates the residuals (`tfa/analyze.py`):
```
partial = (Rxy − Rxz·Ryz)/√((1−Rxz²)(1−Ryz²))
        = (−0.032 − (−0.011)(0.723))/√(...) = −0.035   (95% CI [−0.071, +0.001])
```
Equivalently, stratified: among correct answers r(TFA, judge) = −0.10; among wrong, +0.03. Both ≈ 0. **This is the right test** because a judge earns its keep beyond the free correctness bit; partial ≈ 0 means TFA adds nothing there.

## Why item-level TFA ≈ 0: the confounds (mechanistic)
```
r(TFA, gold_length)     = +0.38   longer/formulaic gold → higher TFA
r(correct, gold_length) = −0.28   longer gold → harder → less correct
```
The two opposing paths through gold-length cancel → r(TFA, correct) ≈ 0. Per-item TFA variance is dominated by a *reference* property (length/formulaicness), not the model's competence. The **content-token control** (mask formatting/LaTeX glue) halves the length confound (+0.38→~+0.2) but the item-level null persists — so it is not a formatting artifact. Neither does the soft `tfa_logprob` help (−0.11 among correct).

## The two failure modes, from real 14B correct-answer examples
**HIGH TFA / LOW judge — long, formulaic gold; model predicts it but its own route is worse.**
- `precalculus/826` (TFA=0.96, judge=2.0, gold_len=478): hard product-of-cosines; gold is a long standard double-angle chain (predictable), but the model's own free solution took a weaker "roots of unity" route.
- `precalculus/989` (TFA=0.94, judge=2.0, gold_len=918): very long formulaic gold → high TFA; own reasoning judged poor.

**LOW TFA / HIGH judge — short, clever gold; model solves it correctly via a *different* valid path.**
- `algebra/893` (TFA=0.62, judge=10, gold_len=105): gold uses a slick "constant term = product of constants" shortcut; the model does a full rigorous expansion (judged 10) — valid but different, so it doesn't match the gold tokens. The **alternate-path penalty**.
- `number_theory/612` (TFA=0.62, judge=10, gold_len=37): terse clever gold; the model's longer explicit derivation is judged perfect.

Both modes are driven by properties of the *reference* (length, path-uniqueness), not by the quality of the model's own reasoning — exactly why item-level TFA is decoupled from the judge.

# Appendix: how might we improve TFA?
Grounded in the two failure modes. Key honesty check: **pure length-normalization/detrending will not create item-level signal** — the partial correlation (which already residualizes out correctness) is ≈ 0, so the signal isn't hidden under a confound; it's absent under the current measurement. The promising ideas therefore *change what is measured*, not just normalize.

1. **Multi-reference TFA** (fixes the alternate-path failure, low-TFA/high-judge). Score against K diverse gold solutions (answer-equivalence-verified) and take the max/soft-max, so a model that reasons well via *any* valid path is credited. Directly repairs algebra/893-type cases.
2. **Surprisal/informativeness-weighted TFA** (fixes the length/formulaic confound, high-TFA/low-judge). Weight each gold token by how load-bearing it is (e.g., inverse token frequency or surprisal under a base LM); formulaic boilerplate counts little, decisive reasoning tokens count most. A principled generalization of the content-token mask.
3. **Contrastive TFA: TFA(correct gold) − TFA(corrupted gold).** Corrupt the gold (wrong final step / distractor derivation) of matched length; a model that reasons well should predict the correct gold *more* than the corrupted one. Differencing cancels the length/formulaic baseline and could surface reasoning discrimination — cheap to run.
4. **Score the model's own trace, not the gold.** The deepest fix: item-level quality is about the model's *own* output. Judge-free proxies: self-consistency across samples, confidence/perplexity of its own derivation, or step-wise entailment to the answer. Departs from teacher-forcing-on-gold but serves the per-response goal (and honestly may be necessary — predicting an expert is structurally different from reasoning well).
5. **Step/bottleneck aggregation.** Replace mean-TFA with the *minimum* over reasoning steps (a single broken step gates quality) or the fraction of steps above a threshold — still gold-anchored, but less length-dominated.

Recommended first probes (cheap, on the existing traces or one extra pass): (2) surprisal-weighting and (3) contrastive TFA, since both attack the identified confounds without new human labels; then (1) multi-reference for the alternate-path failure.

# Appendix: deeper analysis — *why* item-level TFA fails (3000 items)

The item-level null is not random decoupling; it is a **structured, adversarial confound**.

## Gold length is a common cause that moves TFA and the judge in opposite directions
Within the correct stratum (n=1687), Spearman of each property against TFA and against the judge:
```
                  r(·, TFA)   r(·, judge)
 gold_length       +0.34        −0.33     (equal and OPPOSITE)
 free_gen_length   +0.17        −0.17
 free/gold sim     +0.12        +0.02
```
Longer, more formulaic gold is more predictable → higher TFA; but longer gold means a harder problem
with more room for reasoning gaps even when the answer is right → lower judge. Length quintiles:
```
 gold_len bin     mean-TFA   mean-judge
 [ 18,  77]         0.764       9.87
 [ 77, 109]         0.780       9.73
 [109, 164]         0.801       9.69
 [164, 242]         0.808       9.59
 [242,1389]         0.839       8.52
```
TFA rises monotonically with gold length while the judge falls — the shared driver pushes them apart,
which is why r(TFA, judge) is slightly *negative* (−0.10), not merely zero.

## Corroborating cuts
- **Per-subject** r(TFA, judge | correct): positive where gold is short (algebra +0.11, prealgebra +0.06;
  ~130 gold tok), negative where gold is long (geometry −0.25, intermediate-algebra −0.09; ~210–250 tok).
- **Path adherence:** splitting by free-gen↔gold word-overlap, the correlation rises from −0.17 (diverged
  path) to −0.03 (followed gold) — less negative but still not positive. Even on-path, TFA has no signal.
- **Variance:** gold-length explains ~12% of TFA's rank variance and ~11% of the judge's, in opposite signs.

## Interpretation
TFA measures **reference predictability**, dominated by the reference's length/formulaicness — an axis that
is itself weakly *anti*-correlated with judged reasoning quality. This is the mechanistic root of the
item-level failure and the direct motivation for surprisal-weighting (idea 2, strip the length axis) and
contrastive TFA (idea 3, difference out the length baseline).
