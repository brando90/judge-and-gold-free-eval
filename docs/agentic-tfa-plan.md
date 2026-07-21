# Does the judge-free signal extend to agents? A plan grounded in the boundary we found

*Planning doc, July 2026. Companion to the TFA-vs-judge paper. Supersedes the scoping in
[`plan-B-agentic-sparse-feedback.md`](plan-B-agentic-sparse-feedback.md). Revised after two Opus critiques
that killed an earlier Mind2Web-first version; the reasoning for the change is in section 3.*

## 1. The thesis, inherited from the math result

The paper's finding is that **TFA measures agreement with a reference's style, and that coincides with quality
only when two conditions hold: the reference is a long token sequence pinned by the task's own logic (so
predicting it requires competence, not memorized formatting), and the models being ranked share its style.**
We watched this as a clean boundary: TFA ranks models on hard, constrained math (Putnam +0.60, Omni-MATH +0.86),
fades as accuracy saturates (MATH-500 +0.35), is only weakly positive on code where one gold program cannot stand
in for many valid ones (HumanEval cross-family +0.24, within-Qwen +0.80), and turns negative on saturated
grade-school math (GSM8K −0.37), where a short, stylized reference lets a family-specific style offset bury the
quality signal.

Agentic tasks are the far end of the same axis. The contribution is not "TFA for agents." It is to **map the
judge-free frontier one regime further, and to hand off to the right tool at the boundary.** Two facts about TFA
constrain the whole plan and were the undoing of the first draft:

- **TFA needs a gold reference that is a long, task-pinned token sequence.** The entire mechanism (the
  reference-predictability nuisance is most of item variance; the gold is ~200 tokens on MATH) exists *because
  there are hundreds of tokens to average over*. A gold that is a short categorical choice (click element #7)
  has almost no token sequence to teacher-force, so token-TFA has nothing to bite on and degenerates into a
  grounding/classification accuracy that is not the statistic this paper is about.
- **TFA only works on open-weight models** (closed API models cannot be teacher-forced), and it is only
  interesting when it is a *cheap proxy distinct from the quality target* you validate it against. If the
  teacher-forced signal is literally the benchmark's own metric, correlating them tests nothing.

## 2. Ranking agentic benchmarks by whether TFA can even be defined

The right first question is not "which benchmark is cheapest" but "**where is the gold reference a long,
task-pinned token sequence with a free, independent success oracle**." That criterion, not GPU cost, orders the
field, and it demotes the benchmark the first draft picked.

| Benchmark | Gold reference | Is it a token-averageable sequence? | Independent success oracle | Fit for a faithful TFA |
|---|---|---|---|---|
| **SWE-bench Verified** | merged gold PR diff | **Yes** — a long code+prose diff | Hidden test suite, pass@1 (free, deterministic) | **Best.** Literal lift of the HumanEval result |
| **TRAJECT-Bench** (tool use, Oct 2025) | reference tool-call trajectory | **Mostly** — function names + JSON args + order, tens to hundreds of tokens | Executable APIs + trajectory match | **Strong**, longer target than a click |
| **tau2-bench** | canonical action set + task spec | Partial (paraphrasable policy text) | Programmatic final-DB-state reward | Arm 2 (rollout), not TFA |
| **Mind2Web** (offline web) | `(target element, op∈{CLICK,TYPE,SELECT}, value)` tuple per step | **No** — a categorical element choice; only the TYPE `value` string is token-like, usually a few tokens | Offline step-success floors; online needs the live env | Caveated modality probe only (section 3b) |
| **WebArena / OSWorld** | rare human demos | No | Final-state functional check | Reference-free only |
| **GAIA / BrowseComp / Mind2Web 2** | final answer, no trajectory gold | No | Answer/rubric match | Out of scope for TFA |

## 3. The plan: two arms, split at the multiplicity boundary

### Arm 1 (the derisk) — TFA on a gold token sequence: SWE-bench patch, then tool-call trajectory

This is the faithful, cleanly-runnable lift, and it is the derisk **because it is a genuine TFA, not because it is
cheapest**. Teacher-force the model on the gold token sequence and correlate with a free, independent oracle.

- **A0, SWE-bench Verified.** For each task, teacher-force the model on the **gold PR diff** given the issue and
  the oracle files the patch touches (oracle-file context keeps sequence length feasible and removes any retriever
  from the loop). Agentic-TFA = fraction of gold-diff tokens predicted by argmax, exactly the paper's estimator.
  Correlate mean Agentic-TFA with **free-generation pass@1** scored by the hidden tests, across a coder ladder.
  No live environment, no candidate generator, deterministic oracle.
- **A1, TRAJECT-Bench.** Same idea on a longer structured target: teacher-force the gold tool-call trajectory
  (serialized function name + JSON arguments + call order) and correlate with executable success. Report the
  token-TFA and, separately, the semantic components (tool-selection, argument, order accuracy) so we can see
  which part carries the ranking.

**Prediction (falsifiable, and distinct from the parent paper).** Because a patch and a tool trajectory are long
token sequences but code has high solution multiplicity, A0 should look like HumanEval one regime out:
**within-family positive (expected ≈ +0.6 to +0.8), cross-family washed out (expected ≈ 0 to +0.3)**. That
*confirms and extends* the code boundary at repo scale, cheaply. What would overturn our model: cross-family
ρ ≥ 0.6 on SWE-bench, which would mean a gold patch is a better cross-family ranker than a gold function, against
the multiplicity argument. The control that rules out the trivial explanation: check that patch-TFA adds ranking
information beyond raw diff length and beyond the fraction of unchanged context lines the model trivially copies.

### 3b. Modality probe (caveated, not the derisk) — Mind2Web

Mind2Web is kept only as an honest probe of a *different modality*, with three caveats that stop it from being the
derisk. First, its gold is a categorical `(element, op, value)` tuple, so there is no long token sequence; the only
token-TFA component is the TYPE `value` string, and it exists on a minority of steps. We therefore report three
**separate** numbers, never one conflated "Agentic-TFA": (a) element agreement (a grounding/classification score,
explicitly *not* TFA), (b) operation agreement (1-of-3), (c) value-string token-TFA (TYPE steps only). Second, by
the paper's own mechanism a short, near-categorical target with a large family-specific format offset is the
**GSM8K regime, not the Putnam regime**, so the honest prediction is that cross-family token-match tracks format and
training exposure, not competence, and can go *negative*, the first draft had this analogy backwards. Third,
Mind2Web is a common agent-SFT set, so per-family training contamination inflates token-agreement exactly like a
GSM8K style offset. **A0-gate for this probe:** if value-string token-TFA carries no ranking information beyond a
pure semantic element-accuracy, Mind2Web has no TFA content beyond its own leaderboard metric and we drop it. This
probe is **within-family only** for any token-match claim; the offline step-success target floors for small instruct
models, so if we use it at all the quality target is published Online-Mind2Web / Mind2Web 2 (2025) numbers for the
subset of open models that have them, computed by a *different* pipeline than the one producing TFA, to avoid
correlating a measurement with itself. Given all this, Mind2Web is scheduled after A0/A1, and may be cut.

### Arm 2 (the positive signal) — reference-free rollout process value on executable envs

Where the reference is open-ended, one gold trace cannot represent the solution set, so TFA-on-gold is expected to
be a poor cross-family ranker (A0 will confirm this as a boundary point). The positive signal is the paper's rollout
process value, lifted to agents: truncate a trajectory at breakpoints, hand each prefix to a fixed **completer
agent**, let it finish *K* times inside the real harness, and score V = P(the run passes the oracle). A prefix that
keeps the task solvable was progressing; one that derails the completer was not. This needs no judge and no gold
trace, only the executable oracle SWE-bench Verified and tau2-bench already provide, and it is the natural
credit-assignment signal for the RL loops agents are trained with. Compare V against the cheaper single-pass
progress-ratio surrogate (`log π_policy − log π_ref`) already scoped in plan-B.

## 4. Phasing, models, compute

| Phase | Goal | Concrete step | Exit criterion |
|---|---|---|---|
| **A0 — derisk** | Genuine TFA on a token-sequence gold | SWE-bench Verified: patch-TFA (oracle-file context) vs pass@1 across a coder ladder | Within-family ρ with bootstrap CI; cross-family near zero = boundary extended |
| **A1 — longer structured target** | Does a tool trajectory rank better than a patch | TRAJECT-Bench: tool-call TFA + semantic components vs executable success | Which component carries ranking; does multiplicity still wash cross-family |
| **A1b — modality probe** | Web actions, honestly caveated | Mind2Web 3-component decomposition, within-family, contamination-audited, with the A0-gate | Does value-string TFA beat semantic element-accuracy at all |
| **B1 — positive signal** | Rollout V where TFA fails | SWE-bench harness: truncate + fixed-completer rollouts, V = P(pass); vs progress-ratio | Does V grade trajectories where TFA cannot, at what cost |

**Models.** Open-weight only (teacher forcing is impossible otherwise). SWE-bench: a coder ladder,
Qwen2.5-Coder 1.5/7/14/32B plus DeepSeek-Coder and one non-Qwen coder family for a cross-family point. Reuse the
paper's general ladders where a benchmark's action format admits teacher forcing.

**Compute and power.** A0 is cheap and needs no environment: teacher forcing is one forward pass per gold sequence,
well within 2 to 3 GPUs; only the free-generation pass@1 eval runs the test harness. B1 is expensive (K rollouts x
breakpoints inside a Docker harness) and is deliberately last. Agent-capable open-weight models are *fewer* than the
math ladders and small ones floor, so effective n is small: prefer within-ladder Pearson with bootstrap CIs, and do
not over-interpret Kendall or ICC at n <= 5, the paper already shows those swing hard at small n.

## 5. Confounds and pitfalls (the senior-researcher checklist)

- **The gold must be a token sequence, or it is not TFA.** Report token-TFA only where a real token sequence
  exists (patch, tool trajectory, TYPE value); never conflate a categorical element choice into a "TFA" number.
- **Self-correlation.** The teacher-forced predictor must be distinct from the quality target. SWE-bench avoids this
  cleanly (TFA-on-patch vs an independent test oracle); Mind2Web does not (step-success is the benchmark score),
  which is why it is gated and demoted.
- **Retriever / grounding recall.** Any pipeline that first ranks DOM candidates injects a recall nuisance
  orthogonal to reasoning. A0 sidesteps it entirely (oracle-file context, no retriever); if Mind2Web is run, fix one
  ranker across all models so it is a constant, and list its recall as a confound.
- **Per-family training contamination.** Mind2Web and popular tool-use sets appear in agent-SFT mixes, so token
  agreement is inflated per family exactly like a GSM8K style offset. Audit provenance; treat cross-family token
  numbers on contaminated sets as format/exposure, not competence.
- **Format / scaffold dominance.** For structured actions, token-match is dominated by emitting the exact template
  (choice-letter convention, JSON punctuation). Declare Arm-1 token-match within-family unless the action schema is
  normalized across families, and report a format-matched control.
- **Gold provenance.** Use only human or executable-canonical references (SWE-bench merged PRs; verify TRAJECT-Bench
  traces are executable-canonical, not GPT-4-distilled, before trusting cross-family numbers).
- **Context length.** Whole-episode teacher forcing plus repo or page context can exceed context windows; use
  oracle-file context (SWE-bench) or per-step targets, not whole-episode.
- **Oracle gaming.** pass@1 and final-state checks can be passed by wrong trajectories; audit, and never present the
  rollout V as truth, only as calibrated progress.
- **The motivation is credit, not scoring.** Agent benchmarks already ship cheap oracles, so TFA's "avoid the judge"
  selling point is thin here; frame the contribution as dense per-step credit for RL, where a reference-free progress
  signal is the tool.

## 6. What would change our mind (each tied to a control)

- If SWE-bench patch-TFA ranks cross-family at ρ >= 0.6 (control: survives removing diff-length and copied-context
  confounds), then a long gold trace beats a gold function cross-family and the multiplicity argument is wrong.
  Strong, genuinely new result.
- If Mind2Web value-string TFA ranks models beyond semantic element-accuracy (control: the A0-gate above), then
  token agreement carries agentic signal even on a categorical target, sharpening the theory.
- If rollout process value on SWE-bench separates sound-from-lucky passes (as it did weakly on math), that is the
  reusable agentic verifier the RL people want, independent of TFA.

## 7. Recommendation

Make **SWE-bench Verified patch-TFA vs pass@1 (A0)** the derisk: it is a literal, faithful lift of the paper's code
result, it needs no live environment and no retriever, its oracle is free and independent of the TFA signal, and it
extends the math-to-code boundary to repo scale. Run **TRAJECT-Bench (A1)** next for a longer structured target.
Treat **Mind2Web** as a caveated, within-family modality probe that may be cut, not the derisk. Scope **rollout
process value (B1)** as the higher-cost positive follow-up. Treat WebArena, OSWorld, GAIA, and Mind2Web 2 as out of
scope for a reference-anchored signal, and say so in the paper, because that honesty is the contribution.

## Sources

- SWE-bench / SWE-bench Verified (gold PR patches + hidden-test oracle): https://www.swebench.com , https://arxiv.org/abs/2310.06770
- TRAJECT-Bench (trajectory-aware tool use, arXiv Oct 2025): https://arxiv.org/abs/2510.04550 , code https://github.com/PengfeiHePower/TRAJECT-Bench
- tau2-bench (tool-agent-user, programmatic reward): https://github.com/sierra-research/tau2-bench
- Mind2Web (offline web-action prediction; note the live variant Online-Mind2Web (2025) and Mind2Web 2 (2025)): https://arxiv.org/abs/2306.06070
- Agentic benchmark landscape 2026 (SWE-bench, WebArena, OSWorld, GAIA, tau2): survey at https://link.springer.com/article/10.1007/s10462-026-11571-0
- Progress-ratio credit signal (log-prob policy vs reference): see plan-B references.
