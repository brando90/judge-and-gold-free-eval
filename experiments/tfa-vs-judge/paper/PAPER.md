# When can a judge-free signal grade math reasoning?

*A study of Teacher-Forced Accuracy across GSM8K, MATH, and Putnam-AXIOM.*

**TL;DR.** Teacher-Forced Accuracy (TFA) — the fraction of a reference solution's tokens a model would have predicted greedily — is often floated as a cheap, judge-free way to score reasoning. We test it against a strong LLM judge on six math datasets and five models. TFA ranks *models* almost perfectly everywhere, but it barely grades *individual solutions*: the per-item signal is statistically zero on MATH, small on GSM8K, and reaches only ρ≈0.22 on the hardest data (Putnam). That exception is real — it survives label-noise and contamination controls — but it is driven entirely by TFA having room to vary on hard problems, and it is far too weak to replace a judge. Code and data: [`experiments/tfa-vs-judge`](https://github.com/brando90/judge-free-eval/tree/main/experiments/tfa-vs-judge).

## The problem

Evaluating mathematical reasoning at scale is expensive. Checking a final answer is cheap but blind to the reasoning that produced it; grading the reasoning itself means paying a frontier LLM judge on every solution. A judge-free signal that tracks solution quality would make large evaluation loops — reranking, filtering, reward modeling — dramatically cheaper.

Teacher-Forced Accuracy is the most natural candidate. Given a problem and a *gold* reference solution, we feed the reference to the model under teacher forcing and measure how often the model's greedy next-token prediction matches the reference token. A model that "would have written the gold solution" is presumably a strong reasoner. TFA needs no judge, no sampling, and one forward pass. Prior work has shown it ranks models well. The open question — and the one that decides whether TFA is useful as a grader rather than a leaderboard tool — is whether it can tell a *good* solution from a *bad* one on a *per-item* basis. That is what a judge does, and that is what we test.

## Setup

We evaluate the Qwen2.5 instruct ladder (0.5B, 1.5B, 3B, 7B, 14B) on six datasets spanning three difficulty regimes: grade-school word problems (**GSM8K**, and its relabeled **GSM8K-Platinum**), competition-style problems (**MATH-500** and a larger **MATH-full** algebra sample), and olympiad problems (**Putnam-AXIOM**, plus its **functional Variations** designed to defeat memorization). For each solution we record TFA and a ground-truth quality score from a gpt-5.2 judge (0–10), alongside final-answer correctness from Math-Verify.

Our central question is whether TFA tracks judged quality *beyond* simply being correct. Correct answers score higher on both TFA and the judge, so a raw correlation is confounded. We therefore report the **partial Spearman correlation ρ(TFA, judge) controlling for correctness** — within the correct and incorrect solutions separately, does higher TFA mean a better-judged solution? — with 95% bootstrap confidence intervals, and we repeat every analysis controlling for solution length.

| dataset | n | accuracy | TFA range | model-level ρ(TFA, judge) | item-level ρ(TFA, judge \| correct) |
|---|---:|---:|:---:|:---:|:---:|
| MATH-500 | 2500 | 0.60 | 0.76–0.82 | +0.90 | −0.01 [−0.05, +0.04] |
| MATH-full | 2999 | 0.77 | 0.75–0.80 | +0.60 | +0.02 [−0.02, +0.05] |
| GSM8K | 2500 | 0.75 | 0.81–0.84 | +0.90 | +0.12 [+0.08, +0.16] |
| GSM8K-Platinum | 2500 | 0.78 | 0.81–0.84 | +0.70 | +0.06 [+0.02, +0.10] |
| Putnam-AXIOM | 1180 | 0.10 | 0.70–0.77 | +1.00 | **+0.22 [+0.16, +0.27]** |
| Putnam-Variations | 1325 | 0.12 | 0.68–0.76 | +1.00 | +0.15 [+0.09, +0.20] |

*All rows use the same five-model ladder. A 32B model was also run on MATH-500 and dropped here so the TFA ranges and model-level correlations are comparable across datasets.*

## What we found

**TFA is an excellent model ranker.** Averaged over a dataset, TFA orders the five models the same way accuracy and the judge do, with correlations from +0.60 to +1.00 (Figure 1). The correlation is strongest on the hardest data: on Putnam, mean TFA and mean judge score agree perfectly (ρ = +1.00). This inverts a natural worry — that TFA would be useless once models are weak — because weak models on hard problems are exactly where TFA has the most room to separate them. Where TFA weakens (down to +0.60) is the opposite regime: easy, near-saturated data where all five models look alike.

![Model-level: mean TFA tracks accuracy across the ladder on every dataset.](figs/fig2_model_level.png)

**But TFA barely grades individual solutions, and only on hard data.** The per-item picture (Figure 2) is a story of three dataset families, not a smooth trend. On MATH — both the standard 500-problem set and the larger algebra sample — the partial correlation is statistically indistinguishable from zero; TFA carries no information about which correct solution the judge prefers. On GSM8K it is small but real (+0.12). Only on Putnam does it become substantial (+0.22), and it stays positive under length control throughout. Even the best case is a weak correlate, not a grader: a ρ of 0.22 explains under 5% of the variance in judged quality.

![The per-item TFA signal is a dataset-family effect: zero on MATH, small on GSM8K, largest on Putnam.](figs/fig1_difficulty_gradient.png)

**The pattern is explained by saturation, not accuracy.** Notice that GSM8K (75% accuracy) has a larger item-level signal than MATH-full (77% accuracy): difficulty as measured by accuracy is not what matters. What matters is how much room TFA has to move. On easy data all five models reproduce most gold tokens, so their mean TFA sits in a narrow 0.03-wide band (Figure 3); the metric is pinned near its ceiling and cannot discriminate. On Putnam the band widens to 0.07, and the per-item signal appears alongside it. TFA grades reasoning only where it is not saturated.

![TFA saturates on easy data (narrow range) and spreads out on hard data (wide range).](figs/fig3_saturation.png)

**The signal that does exist is genuine.** A skeptic could attribute the Putnam and GSM8K signal to memorized solutions or noisy gold labels rather than real reasoning quality. Two controls argue otherwise (Figure 4). Swapping Putnam for its functional variations — same structure, different numbers, contamination-proof — attenuates the signal from +0.22 to +0.15 but leaves it clearly above zero. Cleaning GSM8K's label noise with the Platinum relabeling halves it from +0.12 to +0.06, again staying positive. Both controls chip at the effect without erasing it, so what TFA measures on these datasets is competence, not an artifact.

![The item signal survives contamination and label-noise controls, attenuated but above zero.](figs/fig4_robustness.png)

## A judge-free signal that *does* grade solutions — at a cost

If token agreement with a fixed reference cannot grade a solution, what can? We changed the object being measured. Rather than asking how well the model reproduces a gold trace, we ask whether the model's *own* partial reasoning stays on track toward a correct answer. Concretely, we truncate a response at several points (after 0%, 25%, 50%, and 75% of its tokens), hand each prefix to a fixed *completer* model, let it continue eight times, and record V(f) — the fraction of continuations that reach the correct final answer, checked by the same symbolic oracle, still with no judge in the loop. A response whose prefixes keep the problem solvable was reasoning well; one that derails the completer was not. We summarize each response's value trajectory by its mean and its late value V(75%). This is Math-Shepherd-style *process value*, and it is deliberately not cheap: it costs many sampled completions per response rather than one teacher-forcing pass.

This signal clears the bar TFA never did. Controlling for correctness, the rollout value correlates with the judge at ρ = +0.33 to +0.43 across completers on 450 MATH-500 responses (150 problems × 3 models) — the same MATH setting where TFA's own per-item signal was zero — with confidence intervals that exclude zero and that *strengthen* when we additionally control for problem difficulty — the opposite behavior of an artifact. And at the right completer it produces the first positive signal we found in the hardest regime of all: among *correct* answers, where every TFA variant sat at zero, the value separates genuinely-sound solutions from lucky ones at ρ = +0.19 [0.09, 0.29].

The completer's strength follows an inverted-U (Figure 5). Too weak (7B) and it fails to finish even good prefixes, adding noise; too strong (32B) and it re-solves the problem regardless of the prefix — it already solves 91% from scratch — washing the signal out. A mid-strength 14B completer is the sweet spot on both the overall correlation and the decisive within-correct test, and it is the only setting where the within-correct signal becomes significant.

![Rollout value vs. the judge across completers: a mid-strength 14B completer is best, and only it makes the grade-among-correct signal significant.](figs/fig5_rollout_completer_curve.png)

| completer | base solve-rate V(0) | overall (partial ρ \| correct) | within-correct | within-wrong |
|---|:---:|:---:|:---:|:---:|
| 7B (too weak) | 0.82 | +0.33 [0.24, 0.41] | +0.09 [−0.02, 0.20] *(n.s.)* | +0.73 |
| **14B (sweet spot)** | 0.88 | **+0.43 [0.35, 0.51]** | **+0.19 [0.09, 0.29]** | +0.73 |
| 32B (too strong) | 0.91 | +0.37 [0.27, 0.45] | +0.08 [−0.02, 0.19] *(n.s.)* | +0.67 |

Two honest caveats. First, this is not TFA and not cheap: it costs eight completions at each of four cut-points — hundreds of times the cost of a single teacher-forcing pass — and it is stochastic. It is a process-reward model or soft verifier, not a drop-in judge replacement. Second, most of its signal lives in the *wrong* stratum (within-wrong ρ ≈ +0.7): it is very good at telling a near-miss from incoherent nonsense, which for math is a legitimate but largely *correctness-graded* notion of quality. The within-correct signal — the one that would truly rival a judge — is real but weak and fragile, appearing only at the sweet-spot completer.

## What this means

For *ranking models* without a judge, TFA works and we recommend it: one forward pass per solution, correlations near 1.0 with a frontier judge, and best precisely where judging is hardest. For *grading individual solutions*, TFA is not a judge replacement. Its per-item signal is absent on the benchmarks people evaluate on most (MATH), and where it appears it is too weak to act on. The reason is structural: a gold-anchored teacher-forcing signal only informs when the gold is hard enough that models genuinely differ in reproducing it. The way forward is to measure the model's *own* reasoning rather than its agreement with a reference. The rollout process value does exactly that and does grade solutions — including, weakly, the coveted case of separating sound from lucky *correct* answers — but it buys that signal with hundreds of times the compute and remains a stochastic soft verifier, not a cheap deterministic judge. The open problem is closing the gap between TFA's price and the rollout value's signal: a per-item grader that is both cheap and informative under saturation. Anchoring on the model's own most-consistent solution instead of a fixed gold is one promising, still-untested route.

## Limitations

A single judge (gpt-5.2) defines ground truth, and all graded solutions come from one model family (Qwen2.5). MATH-full samples only the algebra subject. Putnam's correct-answer stratum is small (≈10% accuracy), so the robust part of its item-level signal comes from the incorrect solutions; final-answer correctness there relies on Math-Verify, which produces false positives on complex expressions. The GSM8K-versus-Platinum comparison uses overlapping but not identical items, so it is directional rather than a paired ablation.

## Reproducibility

Raw rollouts, per-token argmax/log-probability records, and seeds are saved under `/dfs/scratch0/srivatsavad/jfe_raw/`. All numbers regenerate from the committed per-item scores (`runs/scores_*.jsonl`) via `scripts/analyze_workstream_a2.py` and `scripts/make_figures.py`, which write `paper/summary.json` and the figures above. Full method notes and bug post-mortems are in [`JOURNAL.md`](../JOURNAL.md) §4b. Next directions we consider most promising — process-reward signals that survive saturation, cross-family judges, and self-reference (grading against the model's own solution rather than a fixed gold) — are laid out in the [research brief](../../../docs/fable-weekend-research-brief.md).

## Appendix: cheap TFA variants we tried to recover an item-level signal

Before adopting the expensive rollout value, we tried to squeeze a per-item signal out of gold-token agreement while keeping TFA's single-forward-pass cost — by reweighting which tokens count, or by contrasting the gold against a corrupted version. All seven failed. We record them here so others do not repeat them; the pattern is that reweighting the same gold-prediction cannot create a signal that is simply absent.

| variant | idea | item-level ρ (partial \| correct) | outcome |
|---|---|:---:|---|
| content-token TFA | mask formatting/LaTeX glue, score content tokens only | ~0 | null persists — not a formatting artifact |
| TFA-logprob / BPC | soft gold-token log-probability instead of argmax match | ~0 (−0.11 within-correct) | soft variant no better |
| surprisal-weighted TFA | up-weight surprising (non-formulaic) gold tokens | −0.16 | *worse* — surprising tokens are the hard ones good models also miss |
| IDF-weighted TFA | up-weight corpus-rare gold tokens | −0.01 | ≈ baseline — reweighting frequency adds nothing |
| contrastive TFA (answer-swap) | TFA(gold) − TFA(gold with a wrong final answer) | +0.18 → −0.02 | **artifact, retracted** (see below) |
| contrastive TFA (step-shuffle) | TFA(gold) − TFA(gold with reasoning lines reordered) | −0.13 | fails — next-token prediction is local, blind to global step order |
| multi-reference TFA | max TFA over K verified gold solutions | not run | expected to fix only the alternate-path half of the null |

**The cautionary tale that changed how we work.** The answer-swap contrast first looked like a genuine win at ρ ≈ +0.35. It was a `1/gold_length` artifact: because the corruption changes only the final answer token, the contrast reduces to roughly "predicts the correct answer, divided by solution length," and inverse gold-length (Spearman +0.67 with the contrast) re-imported the very length confound TFA already suffers from, this time with a flattering sign. Stripping the length magnitude dropped it to +0.01; controlling for correctness *and* length drove it to −0.02. We retracted it. The lesson is now a rule: **no positive item-level result is believed until it survives controlling for its plausible confounds — length and difficulty.** The rollout value in the main text passes that test (it strengthens under difficulty control); these TFA variants do not.

The deeper takeaway from this appendix is that the failure is not a hidden confound one can reweight away — the item-level signal is genuinely absent under gold-prediction. Recovering it requires changing *what is measured*, which is exactly what the rollout process value does.
