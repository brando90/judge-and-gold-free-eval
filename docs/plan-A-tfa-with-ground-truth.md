# Plan A — TFA as a judge-free metric *where gold references exist*

**Priority plan. This is the paper.** High-leverage, low-risk: remove the LLM judge, keep the gold reference. Reducing/removing the gold reference is explicitly future work (→ [Plan B](plan-B-agentic-sparse-feedback.md)).

Grounded in [`../research/`](../research/README.md). Read [`research-brief.md`](../research/research-brief.md) §1–§7 alongside this.

---

## 0. TL;DR

Teacher-Forced Accuracy (TFA) is a cheap, deterministic, judge-free metric: feed a model the gold solution under teacher forcing and score the fraction of gold tokens it predicts by argmax ([Putnam-AXIOM, Gulati et al., ICML 2025, arXiv:2508.08292](https://arxiv.org/abs/2508.08292)). It was shown to correlate **0.66 ± 0.02** with boxed final-answer accuracy on MATH — but **it has never been validated against the thing it is meant to replace: an LLM judge or a human rating of reasoning quality.** Plan A closes exactly that gap, across GSM8K, MATH, and Putnam-AXIOM, with two mandatory robustness pillars (a shortcut/exposure-bias control and a multi-reference variant), plus a formal-spec track on VeriBench graded by *semantic* equivalence rather than token match.

**Headline claim we want to earn:** *"On reasoning tasks with a gold reference, a single-forward-pass, judge-free metric tracks human/judge assessments of reasoning quality as well as — or better than — an LLM judge, at a fraction of the cost and with perfect reproducibility."*

---

## 1. Research questions

- **RQ1 (the crux).** Does TFA correlate with an **LLM judge** and with **human ratings of reasoning quality**, not merely with boxed final-answer accuracy? On which benchmarks, and how strongly?
- **RQ2 (robustness / validity).** How much of TFA is a *teacher-forcing shortcut* (copying gold tokens already in context) rather than a reasoning signal? Does the correlation survive a shortcut control?
- **RQ3 (multi-path).** How much does the single-canonical-path penalty cost TFA, and does a **multi-reference / equivalence-aware** variant recover it?
- **RQ4 (new territory).** Can TFA now be **run on Putnam-AXIOM** with open reasoning models (it never was — proprietary-logprob limitation), and does it detect contamination on functional Variations the way boxed accuracy does (~46.8% relative drop for o1-preview)?
- **RQ5 (design).** Argmax-match vs. gold-token logprob/perplexity — which better predicts judged quality? How should TFA be normalized across tokenizers and reference lengths?
- **RQ6 (formal specs).** For VeriBench-style theorem-spec prediction, does token-level TFA add anything over semantic-equivalence grading (BEq/SMT), or is it dominated by it?

**Primary hypothesis (H1):** TFA's correlation with judge/human reasoning-quality ratings is *positive and competitive with an LLM judge's agreement with humans*, and **survives the shortcut control** — establishing TFA as a valid judge replacement in the gold-reference regime.

**What would falsify H1:** TFA correlates with final-answer accuracy but **not** with judge/human reasoning-quality ratings once shortcut-controlled — i.e., TFA is "just a cheaper SymPy exact-match." That is itself a publishable negative result and a precise scoping of TFA's limits.

---

## 2. Contribution & positioning

**The gap we close.** Putnam-AXIOM validated TFA against *boxed final-answer accuracy* only. Nobody has shown TFA tracks a *judge* or *humans* on reasoning quality — the exact claim needed to "replace the judge." We provide that evidence (or bound it).

**The niche TFA uniquely fills** (see [scalable-oversight.md §6](../research/scalable-oversight.md)): a metric that is simultaneously **judge-free, execution-free, annotation-free, single-forward-pass, and process-level**, for reasoning tasks where a gold reference exists but no executable oracle does (natural-language proofs/derivations) and where final-answer accuracy is uninformative or gameable (proofs, binary/MCQ). No existing family covers all of these at once:
- pass@k / SWE-bench / Math-Verify need an executable or symbolic oracle;
- exact-match / n-gram / embedding metrics need a canonical string and give *no* process signal;
- ROSCOE / ReCEval give a process signal but are model-backboned (not strictly judge-free) and reference-free-but-uncalibrated.

**Durable selling points to lead with:** bias-freedom, reference-groundedness, and *no generate-then-parse step* (sidesteps the extraction/format fragility that makes deterministic metrics swing 2.2%→80.3% across harnesses — xFinder [arXiv:2405.11874](https://arxiv.org/abs/2405.11874); FormatSpread [arXiv:2310.11324](https://arxiv.org/abs/2310.11324)). Do **not** lead with determinism alone — batch-invariant kernels ([arXiv:2601.06118](https://arxiv.org/abs/2601.06118)) may erode that edge.

**Nearest neighbors to differentiate from:**
- **OmniScore** ([arXiv:2604.05083](https://arxiv.org/abs/2604.05083)) — deterministic but a *separately trained encoder regressor* distilled on GPT-4.1 labels (inherits its biases). TFA uses the evaluated model's *own* logprobs; no auxiliary model, no distillation bias.
- **LAS / SCOTT** ([arXiv:2305.01879](https://arxiv.org/pdf/2305.01879)) — teacher-anchored *simulatability*, but simulation-based, not single-forward-pass token matching.
- **BPC / perplexity** — the closest logprob cousin (~0.54 on MATH); the key ablation partner.
- **ROSCOE** ([arXiv:2212.07919](https://arxiv.org/abs/2212.07919)) — the headline process-metric baseline TFA already beats (≤0.53).

## 3. Scope & non-goals

**In scope:** benchmarks where a gold reference exists (GSM8K, MATH/MATH-500, Putnam-AXIOM; VeriBench for the formal track). Open-weights models only (logprob access).

**Explicit non-goals (state in the paper):**
- Removing/reducing the gold-reference requirement → future work / Plan B.
- Scoring proprietary/closed models via their APIs (no arbitrary-continuation logprobs). A *surrogate open scorer* is a flagged optional extension, not a claim.
- Agentic / multi-step / sparse-feedback settings → Plan B.

One novel contribution, owned cleanly. (See [`../docs/project-context.md`](../docs/project-context.md) for the team's scoping rationale: "in research we don't get partial credit.")

---

## 4. Formalization: TFA spec + variants to test

**Canonical TFA (fix and document up front — the paper leaves this underspecified):**
```
TFA(model, prompt, gold) = (1/N) * Σ_{i=1..N} 1[ argmax_v p_model(v | prompt, gold_{<i}) == gold_i ]
```
- Tokenize `gold` with **each model's own tokenizer**; concatenate after `prompt`; **mask prompt positions** so only the N gold-solution tokens are scored.
- Single forward pass; gather gold-token logprob on the fly (never materialize `[B,N,|V|]` logits).

**Variants to evaluate (each answers a specific RQ):**
| Variant | Definition | Answers |
|---|---|---|
| `TFA-argmax` (canonical) | 0/1 argmax match rate | baseline |
| `TFA-logprob` / `BPC` | mean gold-token logprob (bits-per-token/char) | RQ5 (argmax vs. soft) |
| `TFA-topk` | credit if gold token ∈ top-k | RQ5 (thresholding) |
| `TFA-len-norm` | normalized by reference length / token-type | RQ5 (cross-model comparability) |
| `TFA-multiref` | max TFA over K gold references per problem | RQ3 (multi-path penalty) |
| `TFA-content` | score only *content* tokens (mask stopwords/connectives/formatting) | RQ2 (shortcut control) |

---

## 5. Experimental design

### 5.1 Datasets (HF paths; verify counts/licences before harness — see brief §3)
| Benchmark | Gold reference | HF path | Role |
|---|---|---|---|
| **GSM8K** | full NL rationale + `####` answer | `openai/gsm8k` (`main`) | NL-rationale transfer test (RQ1). Use `madrylab/gsm8k-platinum` to control label noise. |
| **Hendrycks MATH** | full LaTeX solution + `\boxed{}` | `EleutherAI/hendrycks_math` or `nlile/hendrycks-MATH-benchmark` | **Reproduction anchor** — only dataset TFA was validated on. |
| **MATH-500** | step-by-step + answer | `HuggingFaceH4/MATH-500` | cheap comparable hard subset. |
| **Putnam-AXIOM** | full LaTeX solution + boxed answer; functional Variations | `Putnam-AXIOM/putnam-axiom-dataset-v1` | **New territory (RQ4)** — TFA never run here; contamination test. |
| **VeriBench (Lean 4)** | gold Lean formalization (compiler-checked) | OpenReview `rWkGFmnSNl` — pin the exact artifact | Formal spec track (RQ6), separate methodology. |

### 5.2 Models (≥15 open-weights, logprob-exposing; span size & family)
Llama-3.x (8B/70B), Qwen2.5 / Qwen3 (7B/14B/32B/72B), Mistral/Mixtral, Gemma-2, Phi-3/4, OLMo, DeepSeek (incl. a distilled reasoning model). Span 7B→70B+ and base vs. instruct vs. reasoning-tuned to probe the weak-model next-token limit and tool-use disadvantage noted in the brief.

### 5.3 The comparison matrix (core of RQ1)
For each (model × benchmark × problem): compute **TFA (+ variants)**, **BPC**, **all 18 ROSCOE** scores, **BLEU/ROUGE/BERTScore**, and **SymPy/Math-Verify exact-match** (the *anchor correlate*, via [huggingface/Math-Verify](https://github.com/huggingface/Math-Verify) / `lm-eval-harness` `minerva_math`). Then collect the two **targets**:

- **(T1) LLM-judge score of reasoning quality.** A controlled rubric-based judge (grade the *reasoning trace*, not just the answer). Control for the documented biases: randomize position, fix temperature, run ≥3 seeds and report variance, use ≥2 judge families to bound self-preference (Zheng et al. [arXiv:2306.05685](https://arxiv.org/abs/2306.05685); Self-Preference [arXiv:2410.21819](https://arxiv.org/abs/2410.21819)). The judge's *own* instability is part of the story (motivates going judge-free).
- **(T2) Human ratings of reasoning quality.** A held-out expert-graded subset (target ~300–500 traces stratified by benchmark/difficulty/correctness). This is the ground-truth target and the scarce resource — budget for it early.

**Analysis:** correlate every metric against (a) final-answer accuracy and (b) T1/T2. Report Spearman + bootstrap CIs, per-benchmark and pooled. Key comparisons: `corr(TFA, T2)` vs. `corr(LLM-judge, T2)` (does judge-free match the judge?), and `corr(TFA, T2)` vs. `corr(SymPy-EM, T2)` (does TFA beat the free final-answer signal — i.e., is the *process* granularity real?).

### 5.4 Shortcut / exposure-bias control (MANDATORY — RQ2)
Directly answers the two killer critiques (Bachmann & Nagarajan [arXiv:2403.06963](https://arxiv.org/abs/2403.06963); Readout Shortcut [arXiv:2605.22870](https://arxiv.org/abs/2605.22870)):
1. **Answer-swap / corruption test:** perturb the trailing answer token(s) in the gold trace; if TFA barely moves, it's a copy shortcut. Report Δ.
2. **Content-token TFA (`TFA-content`):** recompute over load-bearing reasoning tokens only (mask formatting/connectives/numerals-in-context). Compare correlation with T2.
3. **Free-run cross-check:** report TFA alongside a free-generation accuracy number; frame TFA explicitly as a *screening/proxy* metric, not a deployment-behavior metric.
A reviewer who has read 2605.22870 will look for exactly this. Passing it is the paper's credibility anchor.

### 5.5 Multi-reference / equivalence-aware variant (MANDATORY — RQ3)
Generate/collect **K gold references per problem** (multiple human solutions where available; otherwise synthetic verified alternatives — verified by SymPy answer-equivalence, *not* by a judge). Report `TFA-multiref` and the shrinkage of the alternative-path penalty. Also report TFA split by correct-answer vs. wrong-answer traces to show TFA isn't merely re-deriving answer correctness (pre-empt R2).

### 5.6 Formal-spec track — VeriBench (RQ6, separate methodology)
**Do not** use naive token-TFA as the primary signal — exact-match/BLEU are documented as inadequate for formal statements (alpha-equivalence, definitional equality, hypothesis reordering; [arXiv:2406.07222](https://arxiv.org/abs/2406.07222)). Two clean framings:
- **(a) TFA-as-diagnostic vs. semantic equivalence:** grade predicted specs by BEq / bidirectional provability or SMT-based equivalence (VeriEquivBench [arXiv:2510.06296](https://arxiv.org/abs/2510.06296)); ask whether token-TFA adds anything.
- **(b) TFA-on-proof-tokens → compile/verify:** treat VeriBench's native Lean-kernel pass@1 as ground truth and test whether TFA over the *proof* tokens predicts it.
Consider swapping in **VERINA / Verus-SpecGym / ProofNet** for a cleaner isolated spec-prediction story. Pin the exact VeriBench artifact first (113 vs 140 tasks; not VerifierBench/VeriSoftBench/VeriEquivBench — see R7).

> **Brando's "first experiment"** was "reproduce Putnam-AXIOM TFA for VeriBench theorem-spec prediction." The research says: keep the spirit (spec prediction), but grade by *semantic equivalence*, not token match. E1 below reproduces TFA; E4 executes the VeriBench spec track with the corrected methodology.

---

## 6. Phased milestones

| Phase | Goal | Exit criterion |
|---|---|---|
| **E0 — Harness** | vLLM `prompt_logprobs` (+`--no-enable-prefix-caching`) / HF teacher-forcing harness; per-token masking; `TFA-argmax`+`TFA-logprob`; unit-tested on a toy example. | TFA reproducible bit-for-bit on a fixed (model, gold) pair; tokenizer masking verified. |
| **E1 — Reproduce** | Reproduce Putnam-AXIOM's TFA↔final-answer-accuracy ~0.66 on MATH across ≥10 open models. | Correlation within CI of the paper's, or a documented discrepancy. |
| **E2 — The crux (RQ1)** | Build the T1 judge + T2 human-rating pipeline; compute the full metric matrix; correlate all metrics vs. accuracy and vs. T1/T2. | `corr(TFA, T2)` estimated with CIs on ≥3 benchmarks; head-to-head vs. LLM-judge and vs. SymPy-EM. |
| **E3 — Robustness (RQ2,RQ3,RQ5)** | Shortcut control; multi-reference variant; argmax-vs-logprob & normalization ablations. | Shortcut-controlled correlation reported; multi-ref penalty quantified. |
| **E4 — New territory + formal (RQ4,RQ6)** | Run TFA on Putnam-AXIOM (+Variations contamination test); VeriBench spec track with semantic equivalence. | First-ever TFA numbers on Putnam-AXIOM; VeriBench diagnostic result. |
| **E5 — Write-up** | Paper: lead with judge-reliability motivation, close the validation gap, disarm exposure-bias & multi-path critiques head-on. | Draft with all claims traceable to E1–E4 and no overclaiming beyond the data. |

**First concrete step:** E0 + E1 (harness + MATH reproduction). Everything downstream depends on a trustworthy TFA implementation and a confirmed reproduction.

---

## 7. Success criteria

- **Strong success:** `corr(TFA, T2)` is positive, survives the shortcut control, and is statistically **≥** `corr(LLM-judge, T2)` on ≥2 benchmarks, at ≫ lower cost and perfect reproducibility. → TFA is a validated judge replacement in-regime.
- **Useful success:** TFA beats final-answer-EM's correlation with T2 (process granularity is real) even if it doesn't beat the judge → TFA is a strong cheap first-pass metric.
- **Informative negative:** TFA tracks accuracy but not T2 after shortcut control → precise, publishable characterization of what TFA *cannot* do; motivates Plan B and reference-improvement work.

---

## 8. Risks & pre-emptions (from brief §6)
| # | Risk | Pre-emption (baked into design) |
|---|---|---|
| R1 | TFA never validated vs a judge | E2 *is* this validation — the whole contribution. Don't overclaim before E2 data. |
| R2 | Gold-reference / single-path dependence | Scope to reference-exists; multi-ref variant (5.5); correct-vs-wrong split. |
| R3 | Logprobs block proprietary models | Position for open-weights; surrogate-scorer only as flagged extension. |
| R4 | Alpha-equivalence kills token-match for specs | Formal track uses semantic equivalence, not token-TFA (5.6). |
| R5 | Tokenizer/length dependence | Fix argmax-vs-logprob up front; own-tokenizer; length-norm ablation (5.3/5.6). |
| R6 | Determinism edge eroding | Lead with bias-freedom + no-parse, not determinism. |
| R7 | VeriBench identity ambiguity | Pin exact OpenReview artifact before building harness. |
| R8 | **Exposure-bias/shortcut** (added from radar) | Mandatory shortcut control (5.4) — the single most important robustness check. |

---

## 9. Compute & tooling
- **Inference:** vLLM (`SamplingParams(prompt_logprobs=…, max_tokens=1)`) for throughput; HF Transformers as ground-truth reference implementation. GPU: 70B needs multi-GPU / quantization; most work fits on a single 8×A100/H100 node.
- **Metrics:** `lm-eval-harness` (`minerva_math`), `huggingface/Math-Verify`, ROSCOE (Meta AI release), `bert-score`, `sacrebleu`.
- **Judge/human pipeline:** rubric templates, ≥2 judge families, annotation UI for T2; log seeds and full configs for reproducibility.
- Repo lives under [`../experiments/`](../experiments); pin dataset revisions and model commits.

## 10. Deliverables
1. Open TFA harness (vLLM + HF), with the shortcut control and multi-ref variant.
2. The metric-vs-judge-vs-human correlation study across ≥15 models × 3–4 benchmarks.
3. First TFA results on Putnam-AXIOM (+ contamination-Variation analysis).
4. VeriBench spec-prediction diagnostic (semantic-equivalence graded).
5. Paper + released ratings/annotations (T2) as a reusable resource.

## 11. Working with the team
- **Aryan / Eric** (Putnam-AXIOM authors): sanity-check the TFA reproduction (E1) and the exact metric definition; they hit the proprietary-logprob wall, so E4 (TFA on Putnam-AXIOM) is new ground they'll care about.
- **Brando:** direction, the spec-prediction framing, and the "certification of judges" angle (a possible bridge for the formal track).
- **Sanmi / reviewers:** final arbiter on scope; keep the one-contribution discipline.
- Keep a running "claims ledger": every number in the paper maps to an experiment ID and a verified source (many literature figures are flagged `[UNCERTAIN]` — re-check against PDFs).
