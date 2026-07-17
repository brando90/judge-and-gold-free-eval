# Weekend research brief — judge-free evaluation of reasoning (for an autonomous agent)

> This is a complete prompt for a capable research agent (e.g. Fable) to run judge-free-eval research
> autonomously over a weekend. Read it fully, then read the repo docs it references, then execute.

---

## 0. Mission (the goal, stated plainly)
**Determine when a *judge-free, reference-grounded* signal can evaluate mathematical reasoning — at the
model level and, the hard part, at the item (per-response) level — across natural-language math and formal
(Lean) math; identify the best such signal and its limits; and produce a rigorous, honestly-reported
measurement with a clear recommendation.**

"Judge-free" = no LLM-as-judge and no human labels *in the metric itself*; the metric may use an **objective
oracle** (a symbolic answer-checker for NL math, or the **Lean kernel** for formal math) and the model's own
computation. The north-star use cases are cheap leaderboards, RL reward, and candidate re-ranking without a judge.

You are continuing a live project. **Do not restart from zero and do not repeat known dead-ends.** Build on
what's established, and hold yourself to the rigor rules below (they were learned the hard way).

---

## 1. Required reading (in the repo, before you touch anything)
- `experiments/tfa-vs-judge/RESULTS.md` — final conclusions.
- `experiments/tfa-vs-judge/JOURNAL.md` — detailed narrative: every TFA variant tried, why each failed, the
  correctness bug, and the current rollout process-value results.
- `experiments/tfa-vs-judge/RESULTS_LOG.md` — raw chronological log (for provenance).
- `docs/fixing-tfa-item-level.md` — critique + literature survey (Math-Shepherd/OmegaPRM, PRMs, ROSCOE, etc.).
- `docs/plan-A-tfa-with-ground-truth.md`, `docs/plan-B-agentic-sparse-feedback.md`,
  `docs/tfa_judge_free_evaluation_proposal_google_doc_ready.docx.md` — the original vision. Continue it **in
  spirit** (judge-free reasoning eval; tiered design; "beyond final answers"), not to the letter.
- The **harness** you will reuse/extend: `experiments/tfa-vs-judge/tfa/` (metric core, backends, boxed
  correctness, judge, corruption, analysis) and `experiments/tfa-vs-judge/scripts/`.

---

## 2. What is already established (do not re-derive)
Setup so far: Qwen2.5-Instruct ladder {0.5B…32B} × MATH-500, judge = `gpt-5.2` (0–10 reasoning rubric on the
model's free-gen), correctness via `$`-delimited Math-Verify. Decision metric = **partial Spearman
`ρ(signal, judge | correct)`** (does the signal track the judge *beyond* the free correctness bit).

- **TFA works at the MODEL level, fails at the ITEM level.** ρ(mean-TFA, accuracy) = ρ(mean-TFA, mean-judge)
  = **+0.94** (n=6). Item-level partial ρ(TFA, judge | correct) = **≈ 0** (−0.02).
- **Mechanism of the item-level failure:** gold-trace length is an *adversarial confound* (ρ(TFA, len)=+0.34,
  ρ(judge, len)=−0.33). TFA measures *reference predictability*, not the model's *own* reasoning.
- **Every cheap TFA variant failed** (see JOURNAL table): content-token, logprob/BPC, surprisal-weighted,
  IDF-weighted, contrastive answer-swap (**a `1/length` artifact — retracted**), contrastive step-shuffle.
  Reweighting a gold-prediction cannot create absent signal.
- **A correctness-scoring bug was found and fixed**: `answers_equivalent` must wrap answers in `$…$` before
  Math-Verify (else 247 false-neg + 25 false-pos on non-scalar answers). Always use the fixed version.
- **Rollout process value (Math-Shepherd style) partially works.** With a *fixed* completer, truncate a
  response at cut-points, let the completer continue K times, `V(f)=P(reach correct answer)`. On 450 responses:
  `partial ρ(value, judge | correct)` = **+0.37 (32B completer) / +0.44 (14B)**, CIs exclude 0, survives
  difficulty control. **Mid-strength (14B) beats strong (32B)** (a near-oracle completer washes out). And the
  hard case flips positive: **within-correct = +0.19 [0.09, 0.29]** with the 14B completer. This is a
  process-reward / soft-verifier (judge-free, oracle-grounded) — **not TFA and not cheap** (~K·T× cost).

**Standing takeaway:** judge-free *model-ranking* is solid (TFA). Judge-free *item-level grading* is only
*partially* solved, and only by the expensive rollout value — not by any cheap gold-prediction metric.

---

## 3. Rigor rules (non-negotiable — these were learned from a retraction)
1. **Decision metric is always `partial ρ(signal, judge | correct)` with a bootstrap 95% CI**, plus the
   `within-correct` and `within-wrong` strata reported separately.
2. **Stress-test EVERY positive before believing it.** For any signal that looks positive, (a) control
   additionally for the plausible confound (trace **length** and problem **difficulty**, e.g. the completer
   base-rate V(0)); (b) construct a confound-*independent* version and check it survives. If the signal dies
   under control, it is an artifact — say so and drop it. (This is exactly how `contrast_answer` was caught.)
3. **Correctness = `$`-delimited Math-Verify** for NL math; the **Lean kernel** for FL math. Never the raw
   string fallback for headline numbers.
4. **Report negatives honestly and precisely.** A well-scoped negative is a real result. Do not overclaim; do
   not bury caveats. Keep a **claims ledger**: every number → the script/run that produced it.
5. **Pin dataset revisions and model commits.** Fixed seeds. Save per-item outputs so analyses are re-runnable
   without GPUs.

---

## 4. Workstreams (prioritized). Run baselines first, then push the frontier.

### A. NL-math TFA baselines — breadth (do this first)
Reproduce and extend the model-level + item-level TFA picture beyond MATH-500.
- **Datasets:** GSM8K (`openai/gsm8k` main; also `madrylab/gsm8k-platinum` for label noise), MATH
  (`HuggingFaceH4/MATH-500`, and full `EleutherAI/hendrycks_math` if time), Putnam-AXIOM
  (`Putnam-AXIOM/putnam-axiom-dataset-v1`, incl. the functional Variations). Verify exact paths/revisions.
- **Per dataset:** compute TFA (argmax + logprob) across the Qwen2.5 ladder; free-gen accuracy; the gpt-5.2
  judge on free-gen. Report **model-level** ρ(mean-TFA, accuracy) and ρ(mean-TFA, judge), and **item-level**
  partial ρ(TFA, judge | correct) with CIs.
- **Specifically test:** (i) does the model-level result hold on GSM8K (short NL rationales) and Putnam-AXIOM
  (where TFA is riskiest — weak models floor on next-token prediction; document the floor); (ii) does the
  item-level null hold everywhere. Expected: model-level yes, item-level ≈0 — confirm or find the exception.

### B. Formal-math (FL) track — the prover is a *free* judge (high value)
Formal math is the cleanest judge-free setting: **the Lean kernel is an objective oracle**, so "correctness"
needs no judge. Token-TFA on Lean is known-inadequate (alpha-equivalence, definitional equality, hypothesis
reordering — arXiv:2406.07222), so **do not use naive token-TFA as the primary signal.**
- **Datasets:** VeriBench (the lab's own Python→Lean benchmark; see `~/veribench` and its SCSC metric / TC1
  prover-entailment mode), VERINA, MiniF2F (Lean 4), PutnamBench (`github.com/trishullab/PutnamBench`). Verify
  and pin.
- **Signals to compare (all judge-free):**
  1. **Prover/compiler pass** = ground-truth item outcome (kernel-verified, no `sorry`). This is the oracle.
  2. **Semantic-equivalence coverage** of predicted vs. gold statements via **bidirectional prover entailment
     (BEq)** / SMT — the FL analog of "does the spec match" (cf. VeriBench TC1 mode-1, VeriEquivBench
     arXiv:2510.06296). Test whether this correlates with a human/LLM quality rating of the formalization.
  3. **TFA-on-proof-tokens** — only as a *diagnostic*: does it predict kernel pass@1? (Not as the primary metric.)
  4. **Rollout value, FL version (high value):** truncate a proof attempt, let a completer finish it K times,
     `V = P(the kernel accepts a completion)`. This is a judge-free process value with the kernel as oracle —
     the natural FL counterpart of the NL rollout-PRM, and it directly connects to VeriBench's prover-entailment TC1.
- **Question:** which judge-free FL signal best tracks formalization *quality* (spec faithfulness), and does the
  rollout-value item-level result transfer to FL?

### C. Rollout process value — depth (the promising direction)
- **Completer-strength curve (requested):** run the rollout value with **7B, 14B, 32B** completers on the same
  NL responses. We have 14B/32B (14B > 32B). **Add 7B** — does an even-weaker completer sharpen the
  within-correct signal (less wash-out) or get too noisy? Find the Goldilocks completer. Report V(0) base-rate,
  meanV/lastV features, partial|correct, and within-correct/wrong for each completer.
- **Scale + step-level:** replace the 4 fixed cut-points with true per-step values on more problems/models to
  tighten CIs and get power in the correct stratum. Use OmegaPRM's efficiency (binary-search for the first
  error on monotonic trajectories; tree/rollout reuse) once the signal is confirmed — not before.
- **The hard open question (make real progress):** *can any judge-free signal robustly grade among CORRECT
  answers?* Push within-correct: better completer choice, step-level dips (a step that lowers P(correct) then
  recovers = "lucky"), and multi-sample self-consistency of the response itself. Report the ceiling honestly.

### D. Robustness / validity (do as budget allows)
- **Cross-family judge:** re-run the judge with a second frontier family (e.g. Claude Opus / Gemini) to bound
  self-preference; check the item-level conclusions are judge-invariant. (The provided Anthropic key was
  invalid earlier — obtain a working one.)
- **Small human-rated calibration set (proposal Tier 2):** 100–200 traces, expert-graded for local validity /
  gap severity / overall quality, to confirm the LLM judge is a faithful stand-in for humans. This is the
  proposal's primary ground truth and the biggest external-validity gap.
- **Multi-reference TFA** (max over K verified golds) — expected to fix only the alternate-path half of the
  null; run it to confirm and quantify.

---

## 5. Analysis protocol (apply uniformly)
For each (signal, dataset): report Spearman **and** the partial ρ(·, judge | correct) with bootstrap CI; the
within-correct and within-wrong strata; and, for any positive, the confound-controlled version (length +
difficulty). Model-level: ρ(mean-signal, accuracy) and ρ(mean-signal, mean-judge), n and CI. Aggregate a single
comparison table across all datasets and signals. Prefer plots of the value/feature vs. judge, colored by correctness.

---

## 6. Infrastructure & how to run
- **Compute:** SNAP cluster (`skampere1`/`skampere2`, direct SSH, `/lfs` local scratch — put HF cache and venv
  on `/lfs` for speed, not `/dfs`/NFS which is slow). Check free GPUs via the SNAP GPU-stats wiki; use
  `CUDA_VISIBLE_DEVICES`, `--tp 2` for ≥32B. vLLM 0.25.x + torch cu13x already work.
- **Harness:** extend `experiments/tfa-vs-judge/` — `scripts/run_all.py` (TFA + free-gen + judge),
  `scripts/run_rollout_prm.py` (rollout value), `scripts/run_judge.py` (GPU-free re-judge of saved traces),
  and the `scripts/analyze_*` + `tfa/analyze.py` (partial correlation + bootstrap). Reuse `tfa/boxed.py`
  (fixed Math-Verify), `tfa/backends/` (vLLM/HF, verified equal). Save per-item JSONL; keep raw traces
  gitignored, commit slim scores + summaries.
- **Models:** open-weights with logprob access. Current best mid-2026 open models for math: Qwen3
  {8B,14B,32B}, Qwen2.5-Instruct ladder, DeepSeek-R1 distills, Llama-3.x (gated). Web-search current SOTA
  before pinning — do not hardcode from memory. Completers for the rollout curve: 7B/14B/32B.

---

## 7. Deliverables (by end of weekend)
1. **A single results table** across {GSM8K, MATH, Putnam-AXIOM} × {model-level, item-level} for TFA, plus the
   FL track summary, committed to `RESULTS.md`, with the full narrative appended to `JOURNAL.md`.
2. **The completer-strength curve** (7B/14B/32B) with the within-correct number for each, and the recommended
   completer.
3. **A clear recommendation:** the best judge-free signal for (a) model ranking, (b) NL item-level, (c) FL —
   with where each works and its cost/limits.
4. **Honest scoping:** what remains unsolved (esp. grading among correct answers), and whether the human-
   calibration and cross-family-judge checks changed anything.
5. A running **claims ledger** (number → run → verified source). Commit incrementally to `main`.

---

## 8. Explicit non-goals / do-not-do
- Do **not** chase more cheap gold-token TFA patches (weighting/masking/contrastive) — ruled out; the null is
  absence of signal under gold-prediction, not a hidden confound.
- Do **not** report a positive without the confound-control + CI (the retraction lesson).
- Do **not** conflate "judge-free model ranking" (solved) with "judge-free per-response grading" (mostly not).
- Plan B (agentic / sparse-feedback / no-gold) is future work — stay in the reference-exists regime.

## 9. Definition of done
You've succeeded if there is (a) a clean cross-dataset baseline table for TFA (NL + FL) with model- and
item-level numbers and CIs, (b) a completer-strength curve pinning the best rollout-value configuration and its
within-correct signal, (c) at least one solid FL result using the kernel as the free oracle, and (d) an honest,
well-scoped recommendation — all committed with reproducible scripts and a claims ledger.
