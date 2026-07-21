# Does the judge-free signal extend to agents? A plan grounded in the boundary we found

*Planning doc, July 2026. Companion to the TFA-vs-judge paper. This supersedes the scoping in
[`plan-B-agentic-sparse-feedback.md`](plan-B-agentic-sparse-feedback.md) with concrete, current
benchmarks and a falsifiable design. Drafted with Opus and to be critiqued by an Opus reviewer before
any compute is spent.*

## 1. The thesis, inherited from the math result

The paper's one-line finding is that **TFA measures agreement with a reference's style, and that coincides
with quality only when two conditions hold: the reference is tightly constrained (low solution multiplicity),
and the models being ranked share its style.** We watched this play out as a clean boundary: TFA ranks models
on competition and olympiad math (Putnam +0.60, Omni-MATH +0.86), collapses on saturated grade-school math
(GSM8K −0.37, a style axis dominating a dead quality axis), and washes out on code (HumanEval +0.24, where one
gold program cannot stand in for many valid ones).

Agentic tasks are not a new question for TFA. They are the **far end of the same axis**: solution multiplicity
is maximal (many action sequences reach a goal), horizons are long (errors compound), and the "style" that TFA
keys on is now an entire agent scaffold (ReAct prose vs JSON tool-calls vs code). So the honest prior is not
"will TFA work on agents" but "**the boundary predicts exactly where on the agentic spectrum a reference-anchored
signal can still rank, and where you must switch to a reference-free one.**" That prediction is testable, and the
benchmarks to test it now exist with real gold traces. This is the contribution: not "TFA for agents," but
*mapping the judge-free frontier one regime further and handing off to the right tool at the boundary.*

## 2. Where gold traces actually come from (the landscape, mid-2026)

The blocker Sri flagged, "golden traces are hard to get for multi-step executions," is now only partly true.
The current benchmarks split cleanly into two kinds, and the split is exactly our constraint axis.

| Benchmark | Gold reference available | Constraint on the reference | Success oracle | Fit for TFA |
|---|---|---|---|---|
| **Mind2Web** (offline web) | Yes: human demo, one gold `(snapshot → target element+op)` per step | **High** (single correct DOM element + operation) | Exact match to gold action (element acc, op F1, step-success) | **Best fit.** It *is* teacher-forced by construction |
| **TRAJECT-Bench** (tool use, Aug 2025) | Yes: reference tool-call trajectory, fine-grained (selection / arguments / order) | Medium-high (correct tool + args + dependency order) | Executable APIs + trajectory match | **Strong fit** for a graded TFA |
| **tau2-bench** (customer service) | Partial: ground-truth task spec + canonical action set | Medium (policy-constrained, but paraphrasable) | Programmatic final-DB-state reward | Rollout process value |
| **SWE-bench Verified** (repo bugfix) | Yes: the merged gold PR diff | Low (many valid patches) | Hidden test suite (pass@1) | Rollout process value; TFA-on-patch as a boundary check |
| **WebArena / OSWorld** (live web/OS) | Rare (few human demos) | Low (many valid paths) | Final-state functional check | Reference-free only |
| **GAIA / BrowseComp** (assistant) | No trajectory gold, answer only | n/a | Final-answer match | Out of scope for TFA |

Two facts make this tractable now. First, **Mind2Web is already a teacher-forced benchmark**: it is offline, it
scores each predicted next action against a fixed gold trajectory, and its headline metric (step-success rate)
is precisely "did the model's greedy next action match the gold." That is TFA, in a different modality, with a
constrained single-token-like target. Second, **SWE-bench Verified ships the gold patch** for every task, so the
reference exists even though solution multiplicity is high, which is exactly the case we need to probe the boundary.

## 3. The plan: two arms, split at the boundary

### Arm 1 — Does a reference-anchored signal still rank agents where the reference is constrained?

**Benchmarks:** Mind2Web (primary, cheapest), then TRAJECT-Bench (tool-call graded matching).

**Signal.** Define **Agentic-TFA** as the teacher-forced next-action agreement: feed the model the gold history
(instruction + gold observations and gold actions up to step *t*) and measure whether its greedy next action
matches the gold action at *t*, averaged over steps and tasks. On Mind2Web this is the benchmark's own
step-success under teacher forcing; on TRAJECT-Bench it is graded over tool selection, arguments, and order.
This is a faithful lift of TFA: one forward pass per step, no sampling, no judge, no live environment.

**Measurement.** Across a model ladder (below), correlate mean Agentic-TFA with a *held-out* measure of true
agent quality: the benchmark's **online / free-run task-success** (Mind2Web-live, or executable pass on
TRAJECT-Bench), controlling for trajectory length and context length. Report Pearson, Spearman, Kendall, ICC,
within-family and cross-family, exactly as the paper does.

**Prediction (falsifiable).** Because the Mind2Web target is highly constrained (one right element), Agentic-TFA
should rank models *within a family* well (like our within-Qwen +0.8 to +1.0) and hold cross-family better than
code did, because the DOM target admits far less stylistic freedom than a free-form program. If instead it
collapses cross-family, the "constraint saves it" thesis is wrong for the action modality, and that is itself the
result. On TRAJECT-Bench, correlation should *degrade* as tasks require longer, more parallel tool chains (more
valid orderings = more multiplicity), tracing the same curve we saw from Putnam to code.

### Arm 2 — Where the reference is open-ended, use reference-free process value

**Benchmarks:** SWE-bench Verified (primary), tau2-bench (secondary).

Here one gold trace cannot represent the solution set, so TFA-on-gold is expected to be a poor ranker (we will
*confirm* this cheaply as a boundary point: TFA-on-gold-patch vs pass@1 across a code-model ladder; predicted
near-zero cross-family, echoing HumanEval). The **positive** signal is the paper's rollout process value, lifted
to agents: truncate a trajectory at breakpoints, hand each prefix to a fixed **completer agent**, let it finish
*K* times inside the real harness, and score V = P(the run passes the oracle). A prefix that keeps the task
solvable was progressing; one that derails the completer was not. This needs no judge and no gold trace, only the
executable oracle these benchmarks already provide, and it is the natural credit-assignment signal for the RL
loops that agents are trained with. tau2-bench and SWE-bench Verified both expose the programmatic reward that
makes V computable.

This arm also connects to the progress-ratio idea already scoped in plan-B (`log π_policy − log π_ref`) as a
cheaper, single-pass surrogate for the expensive rollout V, to be compared head to head.

## 4. Phasing, models, and compute

| Phase | Goal | Concrete step | Exit criterion |
|---|---|---|---|
| **A0 — derisk (days)** | Prove the pipeline on the cheapest constrained benchmark | Mind2Web offline: compute Agentic-TFA (teacher-forced step-success) for the Qwen2.5 ladder; correlate with reported task-success | A working TFA-on-actions number and a within-family correlation |
| **A1 — constrained arm** | Map constraint → correlation | Add Mistral / Phi / OLMo ladders and TRAJECT-Bench; stratify by trajectory length and tool-chain complexity | Cross-family curve of ρ vs multiplicity; does the math boundary replicate? |
| **B0 — boundary point** | Confirm TFA fails open-ended | SWE-bench Verified: TFA-on-gold-patch vs pass@1 across a coder ladder (Qwen2.5-Coder 1.5/7/14/32B, DeepSeek-Coder) | Predicted near-zero cross-family = boundary confirmed |
| **B1 — positive signal** | Rollout process value on agents | SWE-bench Verified harness: truncate + fixed-completer rollouts, V = P(pass); compare to progress-ratio surrogate | Does V grade trajectories where TFA cannot, at what cost |

**Models.** Reuse the paper's ladders where the scaffold allows teacher forcing: Qwen2.5 instruct 0.5–14B as the
spine, plus Mistral, Phi, OLMo for cross-family, and coder models on SWE-bench. All open-weight, so we can teacher-
force on the gold trace (closed models cannot be teacher-forced, a hard constraint that shapes the whole plan).

**Compute.** Arm 1 is cheap: teacher forcing is one forward pass per step, no environment, well within 2–3 GPUs.
Arm 2 B1 is expensive (K rollouts × breakpoints inside a Docker/SWE harness) and is deliberately last.

## 5. Confounds and pitfalls (the senior-researcher checklist)

- **Scaffold/format dominates token match.** Teacher-forcing a tool trajectory only means something if the model
  is prompted in the *same* action format as the gold (ReAct vs JSON tool-call vs code). Format mismatch tanks TFA
  for reasons unrelated to competence and would masquerade as a family effect. Mitigation: normalize to a single
  action schema per benchmark, or restrict cross-family claims to models sharing a scaffold, and report a
  format-matched control. On Mind2Web this is baked in (fixed action space), which is another reason it goes first.
- **Gold provenance.** If "gold" traces are model-generated (many training sets distill GPT-4 trajectories), the
  style confound is fatal and self-fulfilling. Use only human or canonical references: Mind2Web human demos,
  SWE-bench merged PRs, tau2 task specs. Flag TRAJECT-Bench provenance before trusting it.
- **The motivation is weaker than in math.** Agent benchmarks already ship cheap programmatic oracles, so TFA's
  "avoid the expensive judge" selling point is thinner. The real need TFA/process-value serves here is *dense,
  per-step* credit for RL where only terminal reward is verifiable, so frame the contribution as shaping/credit,
  not leaderboard scoring.
- **Context length.** Whole-episode teacher forcing plus repo or DOM context can exceed context windows (this is
  the exact failure that dropped short-context models from our Omni-MATH cut). Mitigation: per-step TFA (Mind2Web),
  oracle-file context (SWE-bench), not whole-episode.
- **Success-oracle gaming.** Pass@1 and final-state checks can be passed by wrong trajectories (weak tests, lucky
  final state). Audit for it, and never present the rollout V as truth, only as calibrated progress, the same
  honesty ledger the paper keeps.
- **Multiplicity is the point, not a bug.** Expect Arm-2 TFA to be a poor ranker. That is a *predicted* boundary
  observation, not a failed experiment, and it is only interesting because Arm 1 is designed to succeed alongside it.

## 6. What would change our mind

- If Agentic-TFA ranks models cross-family on Mind2Web at ρ ≥ 0.6, the constrained-reference thesis extends to the
  action modality and TFA becomes a genuinely cheap agent-ranker for constrained-action benchmarks. Strong result.
- If it collapses even on Mind2Web's constrained targets, then the *action modality itself* (not just multiplicity)
  breaks reference anchoring, sharpening the theory.
- If rollout process value on SWE-bench separates sound-from-lucky passes (as it did weakly on math), that is the
  reusable agentic verifier the RL people want, independent of TFA.

## 7. Recommendation

Start with **Mind2Web A0/A1** this cycle: it is the cheapest, it is teacher-forced by construction, it needs no
environment, and it directly tests whether our boundary extends to actions. Scope **SWE-bench Verified** rollout
process value (B1) as the higher-cost positive follow-up. Treat WebArena/OSWorld/GAIA as out of scope for a
reference-anchored signal, and say so in the paper, because that honesty is the contribution.

## Sources

- Mind2Web (offline web-action prediction, gold trajectories): https://arxiv.org/abs/2306.06070 ; leaderboard notes https://benchmarkingagents.com/mind2web/
- TRAJECT-Bench (trajectory-aware tool use, Aug 2025): https://arxiv.org/abs/2510.04550 ; code https://github.com/PengfeiHePower/TRAJECT-Bench
- tau2-bench (tool-agent-user, programmatic reward): https://github.com/sierra-research/tau2-bench
- SWE-bench Verified (gold PR patches + test oracle): https://www.swebench.com
- Agentic benchmark landscape 2026 (SWE-bench, WebArena, OSWorld, GAIA, tau2, METR HCAST): https://decodethefuture.org/en/ai-agent-benchmarks-2026/
- Progress-ratio credit signal (log-prob policy vs reference): arXiv:2606.26080 (see plan-B)
