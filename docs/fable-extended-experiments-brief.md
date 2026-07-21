# Extended experiments and Putnam-AXIOM reconciliation: an executable research brief

> Autonomous research brief for a capable agent (for example Fable), to run offline or remotely across
> several sessions. Read it fully, read the referenced repo docs, then execute the workstreams in order.
> Do not run everything at once. Finish one workstream, commit its results, update `paper/PAPER.md` and
> `JOURNAL.md`, then start the next, and keep going until all are done. Be critical: for every claimed
> effect, control the confounds named in that workstream and validate the finding before you believe it.
> A well-scoped negative is a real result here. Write in plain prose without em-dashes.

---

## 0. Mission

Extend the judge-free Teacher-Forced Accuracy (TFA) study along five axes the PI asked for, and first
reconcile our numbers with the original Putnam-AXIOM paper (arXiv:2508.08292). The five axes:

1. Report correlations with **boxed accuracy** everywhere, alongside the judge correlation.
2. Report correlation metrics **beyond Spearman** (Pearson, Kendall), with confidence intervals.
3. Add an **IMO-hard olympiad dataset** (Omni-MATH or OlympiadBench).
4. Add **non-Qwen model families**, including math-specialized models, and map exactly **where TFA fails**.
5. Test **non-math and agentic datasets**, especially top agentic benchmarks, to see whether TFA gives any
   signal (even model-level correlation is a useful result).

The north star is unchanged: understand when a judge-free, reference-grounded signal can evaluate reasoning,
at the model level and the item level, and report it honestly.

---

## 1. Current state and required reading

- `experiments/tfa-vs-judge/paper/PAPER.md`: the current result. Model-level TFA ranks within a family and
  across families on hard data, but collapses on saturated GSM8K; item-level is a saturation and family
  effect (zero on MATH, small on GSM8K, up to +0.22 on Putnam); a rollout process value grades solutions at
  a cost; judge-invariance (D1) and cross-family (D2) sections; an appendix of failed cheap variants; and a
  section explaining the GSM8K collapse as stylistic distance from a short reference.
- `experiments/tfa-vs-judge/JOURNAL.md` sections 1 to 4c: full detail and bug post-mortems.
- `docs/fable-plan-A-derisking-brief.md`: the de-risking plan (D1 to D6) this brief continues.
- `docs/fixing-tfa-item-level.md`: literature on why cheap item-level fixes fail; rollout PRM rationale.
- Harness to reuse: `tfa/` (metric core, `boxed.py` fixed scorer, `judge.py` litellm judge, `analyze.py`
  bootstrap and partial correlation, `corrupt.py`) and `scripts/` (`run_all.py`, `run_judge.py`,
  `run_variants.py`, `run_rollout_prm.py`, `analyze_workstream_a2.py`, `analyze_d2.py`, `make_figures.py`).
  Local analysis venv is `experiments/tfa-vs-judge/.venv-local` (numpy, scipy, matplotlib, math-verify,
  latex2mathml). Cluster venv is on `/lfs`; raw artifacts go to `/dfs/scratch0/<user>/jfe_raw/`.

---

## 2. Reconciliation with Putnam-AXIOM (do this first, it frames the rest)

### 2.1 What Putnam-AXIOM (Gulati et al., arXiv:2508.08292) actually claims about TFA

- TFA correlates with boxed accuracy at **0.66 plus or minus 0.02 on MATH** across **15 open-source models
  from 7B to 70B**, and beats every ROSCOE metric (best 0.53) and BPC (0.54) on every MATH category.
- On Putnam-AXIOM Original, TFA to accuracy correlation is **0.52**, and **0.62 without two outliers**.
- TFA is defined as the fraction of reference-solution tokens the model predicts by **argmax** while
  teacher-forced on the ground truth. All tokens counted. Prompt masking is not described. No log-prob variant.
- Proprietary models (GPT-4o, o1-preview, Claude) are excluded from TFA because it needs log-probabilities.
- TFA is claimed to give "step-level insight without additional annotation", to "expose reasoning errors
  invisible to final-answer checks", and to "penalize solutions that get the right box via spurious reasoning".
- There is **no human evaluation and no LLM-judge comparison**. The paper names this as future work:
  "A systematic comparison between TFA and expert grading of proof traces will quantify how faithfully
  automatic scores reflect human judgment."
- Contamination: functional Variations drop accuracy sharply (o1-preview 19.6 points, 46.8 percent relative;
  GPT-4o 36 points; DeepSeek-R1-Qwen-32B 37.5 points). TFA was **not** computed on the Variations.

### 2.2 What we found, and how it lines up

Model-level TFA to accuracy is **essentially the same result they report**, and the gap in the headline
number is explained, not contradicted. Measured on our data (five-model Qwen ladder plus Mistral, Phi-4,
OLMo-2), model-level TFA to accuracy on MATH-500:

| set | Spearman | Pearson | Kendall |
|---|---:|---:|---:|
| within-Qwen (clean single family) | +0.90 | +0.94 | +0.80 |
| pooled cross-family (4 families) | +0.86 | +0.77 | **+0.64** |

Their reported 0.66 sits right on our **cross-family Kendall (+0.64)**. Two methodological choices move our
Spearman +0.90 down to their 0.66, and both are things we can demonstrate:

1. **Correlation metric.** Kendall tau is the honest choice for ranking a handful of models and is far less
   forgiving than Spearman. Pooled cross-family, Spearman +0.86 becomes Kendall +0.64.
2. **Model-set composition.** Their 15-model set mixes families and, critically, includes **math-specialized
   models** (Qwen2-Math, DeepSeek-Math, NuminaMath). These are trained on MATH-style solutions, so their TFA
   is inflated relative to their problem-solving ability, and they fall off the accuracy line. That is exactly
   the family and training-style offset we found in D2 and used to explain the GSM8K collapse. Their own
   "without two outliers 0.62" on Putnam is the same phenomenon.

So there is no real discrepancy in the model-level claim. TFA to accuracy is positive and beats ROSCOE and BPC
in both studies. Our BPC ablation (BPC tracks accuracy about as well as TFA on MATH and Putnam) is consistent
with their BPC 0.54 being below TFA 0.66.

The one place our work goes past theirs is the item level. Putnam-AXIOM asserts TFA gives step-level insight
and penalizes right-answer-wrong-reasoning, but provides no evidence, and names expert grading as future work.
We ran that test (partial Spearman of TFA against a frontier judge, controlling for correctness) and find the
reasoning-quality claim does **not** hold on MATH (item-level partial rho about zero), is small on GSM8K, and
reaches only +0.22 on Putnam. We complete their stated future work and report the honest answer.

### 2.3 Reproduction and debug plan (do this to close the loop)

Goal: reproduce their 0.66 on MATH from their setup, and show the gap is metric plus model-set, not a bug.

1. Match their TFA definition as a variant: **all tokens, no prompt masking, argmax**. We currently mask the
   prompt and can also mask to content tokens. Add an `--all-tokens --no-prompt-mask` reproduction mode to the
   metric (or compute it in analysis from saved per-token records) and confirm it does not change the
   qualitative picture. Expect a small absolute TFA shift and little correlation change.
2. Assemble a **15-ish model cross-family set at 7B to 70B that includes math-specialized models**: for
   example Qwen2.5-Math-7B, deepseek-math-7b-instruct, NuminaMath-7B, Mathstral-7B, plus general models from
   Llama, Gemma, Mistral, Phi, OLMo, Yi or GLM. Verify HF paths and log-prob access first.
3. Compute model-level TFA to accuracy with Spearman, Pearson, and Kendall, both pooled and within family.
   Prediction: the pooled cross-family number, especially Kendall or Pearson, lands near 0.6 to 0.7, matching
   their 0.66, and the math-specialized models are the visible outliers (high TFA for their accuracy).
4. Report the reconciliation in the paper: same direction, magnitude explained by metric and by the
   training-style offset, and the item-level claim tested for the first time.

Confounds to keep in mind here: capability range of the model set (a wider accuracy spread inflates rank
correlation), per-category averaging versus pooled (they average across MATH categories), and tokenizer and
length effects on absolute TFA.

---

## 3. Workstreams

Run in this order. Each names its hypothesis, method, the confounds you must control, the literature to check,
the validity bar (what makes a positive believable and what a clean negative would mean), and the deliverable.

### WS1. Boxed-accuracy correlations everywhere (cheap, do alongside WS2)

**Why.** Every model-level and cross-family table currently reports the judge correlation. Add the boxed
accuracy correlation next to it, so results are directly comparable to Putnam-AXIOM and so a reader can see
where accuracy and judge agree or diverge.

**Method.** Extend `analyze_workstream_a2.py` and `analyze_d2.py` to emit, for every dataset and model set,
both `rho(mean-TFA, mean-accuracy)` and `rho(mean-TFA, mean-judge)`. Use recomputed correctness `cc` from the
fixed scorer, never the stale stored `boxed_correct`. At the item level, report the within-correct and
within-wrong TFA means and the point-biserial of TFA with correctness, since item-level accuracy is binary.

**Confounds.** Stale `boxed_correct` in old Qwen files (recompute `cc`). Math-Verify false positives on
complex answers (spot-check). Accuracy and judge are tightly coupled at the model level (about equal in our
data), so do not present them as independent confirmations, present agreement or divergence.

**Validity.** This is descriptive, both outcomes are informative. If TFA tracks accuracy but not judge
anywhere, that localizes what TFA measures.

**Deliverable.** Every results table gains an accuracy column beside the judge column.

### WS2. Correlation metrics beyond Spearman (cheap, do with WS1)

**Why.** The Putnam-AXIOM reconciliation shows conclusions move with the metric. Small model counts (5 to 15)
make Pearson outlier-sensitive and Spearman optimistic. Report all three and say which to trust.

**Method.** Report **at least three of these four**: Pearson, Spearman, Kendall tau-b, and ICC. Use each where
it is meaningful:
- For TFA against a target on different scales (TFA about 0.7 to 0.85 versus judge 0 to 10 or accuracy 0 to 1),
  report **Pearson, Spearman, Kendall tau-b**, each with a bootstrap 95 percent CI (resample models with
  replacement). These three are the meaningful cross-scale metrics; that is already three of the four.
- Add **ICC (intraclass correlation, two-way, ICC(2,1) or ICC(A,1))** for **same-scale agreement** analyses,
  where it is the standard tool: inter-judge agreement (gpt-5.2 versus Claude, both 0 to 10, the D1 check) and
  judge versus human (the D5 calibration, both on the same rubric). For a cross-scale TFA-to-target ICC, first
  z-score each series; note that standardized ICC then approaches Pearson and is reported only for completeness.
- Add one nonlinear dependence measure (distance correlation or mutual information) at the model level, because
  TFA saturates and the TFA-to-quality relation is nonlinear, so a low Pearson with a high distance correlation
  would itself be a finding.
Implement ICC in the analyzer (a small variance-components function, or `pingouin.intraclass_corr` in
`.venv-local`), and report the ICC form used (single-rater, absolute-agreement vs consistency).
For item-level, keep partial Spearman as the primary decision metric, and add partial Pearson and a rank-based check.

**Confounds.** Ties in TFA (use tau-b, which corrects for ties). Tiny n (report the CI, do not over-read a
point estimate). Nonlinearity and saturation (this is why Pearson can understate the association).

**Literature.** The metric-dependence of emergent-ability conclusions (arXiv:2304.15004) is the cautionary
reference: the choice of metric can manufacture or hide an effect. Kendall tau is the standard for ranking
few systems.

**Validity.** Prefer Kendall tau-b for the headline model-level claim, report the others for transparency.
A conclusion that survives all three metrics is robust; one that only holds under Spearman is fragile.

**Deliverable.** A metric-comparison table, and a one-line rule in the paper on which metric the claims rest on.

### WS3. IMO-hard olympiad dataset (GPU, medium)

**Why.** Our saturation account predicts that on extremely hard data TFA de-saturates further, so the
item-level signal should be at least as large as on Putnam, unless the weak-model floor hits (all models near
zero accuracy, TFA compressed low). Test which happens at the top of the difficulty range.

**Method.** Add **Omni-MATH** (about 4400 olympiad problems with full gold solutions and human difficulty
levels) or **OlympiadBench** (text-only math subset), whichever has clean full reference solutions. Verify the
HF path and that each item has a full solution, not just an answer. Run the existing pipeline: TFA and free
generation across the ladder, judge with gpt-5.2 and optionally Claude for judge-invariance, correctness by
Math-Verify. Report model-level correlations (WS1, WS2) and item-level partial rho with strata.

**Confounds.** At IMO difficulty, accuracy is very low, so the **correct stratum is tiny** and item-level
within-correct is underpowered, worse than Putnam. Treat the item-level positive as within-wrong-driven and
say so. Math-Verify is least reliable on olympiad answers (proofs, sets, tuples), so audit correctness and
consider judge-only correctness for headline item-level numbers. Contamination is a live risk on famous
olympiad problems, so note it and prefer the most recent or perturbed subset if available.

**Validity.** Model-level should stay strong (predicted near +0.9 to +1.0 within family, like Putnam). The
open question is whether item-level exceeds Putnam or collapses to a floor. Either is publishable and sharpens
the saturation account.

**Deliverable.** Omni-MATH or OlympiadBench added to `data.py` and to every table and figure.

### WS4. Non-Qwen families and a map of where TFA fails (GPU, the core of this batch)

**Why.** D2 showed cross-family ranking survives on hard data and collapses on saturated GSM8K, driven by a
family and style offset. Extend the family set, include the math-specialized models that reproduce the
Putnam-AXIOM 0.66, and turn "where TFA fails" into an explicit taxonomy.

**Method.** Add families and types, verifying HF paths and log-prob access first. **Priority order: finish the
current families before reaching for new gated ones.**
- **Math-specialized (do first, the WS-V reproduction):** Qwen2.5-Math-7B, deepseek-math-7b-instruct,
  Mathstral-7B, and NuminaMath-7B. All ungated. These test the training-style offset directly and reproduce
  the Putnam-AXIOM 0.66.
- **Reasoning-tuned:** DeepSeek-R1-Distill (Qwen and Llama variants), run in a comparable mode, to test whether
  long-CoT style diverges from concise gold references. Note Qwen3 defaults to thinking mode, which is not
  comparable to the non-thinking instruct baseline, so fix the mode explicitly. Ungated.
- **Second sizes for the current families** (Mistral, Phi, OLMo) so within-new-family ranking is possible.
- **Deferred, optional, only if a reviewer asks for the most popular families:** Llama-3.x and Gemma-2 or 3
  (gated). Do not add them just for breadth; the math-specialized and reasoning models already cover the
  failure taxonomy. Reach for these last, if at all.
Run the three anchors (MATH-500, GSM8K, Putnam) plus WS3 if ready. Compute pooled and per-family, per WS1/WS2.

**Hypothesized failure taxonomy (state it, then test each):**
1. **Saturation failure:** easy data (GSM8K), narrow TFA band, cross-family ranking collapses. Shown; confirm
   it holds with more families.
2. **Training-style-familiarity failure:** math-specialized or dataset-format-trained models have TFA inflated
   for their ability, so they sit off the accuracy line. Predict they are the outliers that pull cross-family
   correlation down toward the Putnam-AXIOM 0.66.
3. **Reasoning-style divergence failure:** long-CoT reasoning models predict a concise gold poorly despite
   high ability, the phi-4-on-GSM8K mechanism at family scale.

**Confounds.** Recompute `cc`. Simpson's paradox when pooling families at different TFA offsets, so always
report within-family alongside pooled. Gating and log-prob access (some gated or API-only models cannot be
scored). Thinking versus non-thinking mode for reasoning models. Tokenizer differences in the gold token count.

**Literature.** Exposure-bias and next-token pitfalls (Bachmann and Nagarajan arXiv:2403.06963), the readout
shortcut (arXiv:2605.22870), and the Putnam-AXIOM outlier note itself.

**Validity.** A believable "TFA fails here" claim shows the model sits off the line and that neither
content-token TFA nor per-character BPC recovers it (the ablation we used for GSM8K), so it is not a formatting
or tokenizer artifact. The deliverable is a clean taxonomy with one figure per failure mode.

**Deliverable.** Expanded cross-family tables, the reproduced Putnam-AXIOM 0.66 with math-specialized models
flagged as outliers, and a "where TFA fails" figure and paragraph.

### WS5. Non-math and agentic datasets (medium to high, most novel and riskiest)

**Why.** TFA needs a gold reference trace. As solution multiplicity grows, from constrained math derivations,
to code with many valid forms, to agentic trajectories with vast valid spaces, the single-reference assumption
should weaken. The prediction is that TFA's correlation degrades along math, code, agentic, and mapping that
degradation is the contribution. Even a model-level correlation on code or SWE-bench is a useful result.

**Method, in increasing difficulty.**
1. **Code with an objective oracle (do first).** HumanEval, MBPP, or LiveCodeBench have a canonical gold
   solution and unit tests. Compute TFA on the gold solution and free-generation pass@1, then correlate mean
   TFA with pass@1 across models. This is the clean non-math extension with a deterministic oracle, no judge
   needed. Confound: **solution multiplicity**, since one gold penalizes valid different code, so predict TFA
   is a weaker model-level ranker on code than on math. Test the multi-reference variant here, since multiple
   gold solutions should help more on code than on math.
2. **SWE-bench Verified (agentic-adjacent, objective oracle).** The gold patch is the reference, tests are the
   oracle. Compute TFA on the gold patch (with the repository context in the prompt) and correlate mean TFA
   with resolve rate. This is the closest thing to an agentic task where a reference exists. Confounds: the
   gold patch is a final artifact, not the agent trajectory; the context is large and expensive; patch
   multiplicity is severe. Treat a positive model-level correlation as the win and do not overclaim item level.
3. **Reference-free agentic (tau-bench, WebArena, OSWorld): out of scope for TFA.** There is no canonical gold
   trajectory, so TFA does not apply. The correct analog is the policy-versus-reference log-probability ratio
   (Progress Advantage, arXiv:2606.26080), which is Plan B, not this brief. Note it and stop, rather than
   forcing TFA where its assumption fails.

**Literature.** SWE-bench (arXiv:2310.06770), EvalPlus on weak test oracles (arXiv:2305.01210), verifier
hackability and fuzzing RLVR verifiers (arXiv:2606.16062, arXiv:2606.01066), Progress Advantage
(arXiv:2606.26080), and the agentic benchmark landscape (SWE-bench Verified, tau-bench, WebArena, OSWorld,
BFCL, GAIA).

**Validity.** The honest thesis is a boundary map: TFA works as a model-level ranker where a reference exists
and solution multiplicity is low (math), degrades where multiplicity is high (code), and does not apply where
no canonical reference exists (open agentic). A clean degradation curve is a strong result. A surprise
positive on SWE-bench would be notable and must survive the multiplicity confound (does multi-reference change
it) before being believed.

**Deliverable.** A code result (TFA vs pass@1, with the multi-reference test), a SWE-bench model-level number
with caveats, and an explicit statement of where reference-anchored judge-free evaluation stops applying.

---

## 4. Rigor rules (carry over, non-negotiable)

1. Primary item-level metric is partial Spearman of the signal against the judge, conditioning on correctness,
   with a bootstrap 95 percent CI, plus within-correct and within-wrong strata. Add Pearson and Kendall per WS2.
2. Stress-test every positive. Additionally control for gold length and problem difficulty, and build a
   confound-independent version. If it dies under control it is an artifact, say so and drop it. This is how
   the answer-swap 1/length artifact was caught.
3. Correctness is dollar-delimited Math-Verify for natural-language math, unit tests for code, the Lean kernel
   for formal math. Never the raw string fallback for headline numbers. Verify `math_verify` imports before
   trusting any accuracy. Recompute `cc`, do not trust stored `boxed_correct` in old files.
4. Report negatives precisely. A boundary or a null is a result. Keep a claims ledger mapping every number to
   the script, run, and commit that produced it.
5. Save raw artifacts to `/dfs/scratch0/<user>/jfe_raw/` with fixed seeds and a manifest. Commit only slim
   per-item scores (`runs/scores_*.jsonl`), summaries, and figures. Regenerate numbers from the slim scores.
6. Web-search current model IDs before pinning. Right-size GPUs (baseline then scale, set
   `CUDA_VISIBLE_DEVICES`). Keep long jobs under nohup or setsid so they survive disconnects. Prefer running
   analysis locally in `.venv-local` on pulled judged files, which caught two data bugs before.

---

## 5. Analysis protocol (apply uniformly)

For each dataset and model set, report both accuracy and judge correlations, under Spearman, Pearson, and
Kendall, pooled and within family, with CIs. Item-level: partial rho against judge conditioning on
correctness, strata, and confound-controlled versions. Produce one comparison table spanning all datasets,
signals, and metrics, and figures per claim (reuse `make_figures.py` and `make_d2_fig.py`, add a
metric-comparison panel and a failure-taxonomy panel). Prefer plots of the signal versus the target colored by
correctness or by family.

---

## 6. Infrastructure and how to run

- Compute: SNAP cluster (skampere1 or skampere2, direct SSH, `/lfs` for HF cache and venv, `/dfs` for
  persistent raw artifacts). Check free GPUs, use `CUDA_VISIBLE_DEVICES`, tensor-parallel for 32B and larger.
- **GPU budget: use no more than 2 to 3 GPUs at a time** (shared cluster courtesy). Run workstreams and models
  sequentially through that budget rather than fanning out. The orchestrator must be a sequential queue that
  never holds more than three GPUs, not a wide parallel launch.
- Harness: extend `run_all.py` (TFA plus free-gen plus optional judge), `run_judge.py` (GPU-free re-judge of
  saved traces, resilient to per-item content-filter errors), `run_variants.py` (TFA variants, add the
  all-tokens no-mask reproduction mode and multi-reference), `run_rollout_prm.py` (rollout value), and the
  `analyze_*` scripts. Reuse `boxed.py` (fixed Math-Verify) and `backends/` (vLLM and HF verified equal).
- Data: add new datasets to `tfa/data.py` with pinned revisions. For code, add a unit-test oracle path. For
  SWE-bench, reuse the official harness for resolve-rate scoring rather than reimplementing it.
- Save per-item JSONL, keep heavy judged traces gitignored, commit slim scores and summaries and figures.

---

## 7. Deliverables and definition of done

1. A reconciliation section in the paper: our model-level TFA matches Putnam-AXIOM once metric and model set
   are matched, the 0.66 reproduced with math-specialized models flagged as outliers, and the item-level
   reasoning-quality claim tested for the first time.
2. Accuracy correlations beside judge correlations everywhere, under three metrics with CIs (WS1, WS2).
3. IMO-hard results (WS3) with an honest item-level power statement.
4. An expanded cross-family study and a "where TFA fails" taxonomy with figures (WS4).
5. A non-math and agentic boundary map: code result with the multi-reference test, a SWE-bench model-level
   number with caveats, and an explicit statement of where TFA stops applying (WS5).
6. A claims ledger and incremental commits to main, with `PAPER.md` and `JOURNAL.md` updated as each
   workstream lands.

Done means: the Putnam-AXIOM reconciliation is settled in writing, every table carries accuracy and judge
under three metrics, at least the code extension and one new hard dataset are complete, the failure taxonomy
has evidence for each mode, and every headline number is in the claims ledger with a reproducible script.

---

## 8. Non-goals

- Do not chase more cheap gold-token reweightings for item-level signal, they are ruled out.
- Do not report a positive without the confound control and a CI.
- Do not force TFA onto reference-free agentic tasks, where its assumption fails; note the progress-signal
  alternative and stop.
- Do not conflate judge-free model ranking, which works within family and on hard data, with judge-free
  per-response grading, which mostly does not.
