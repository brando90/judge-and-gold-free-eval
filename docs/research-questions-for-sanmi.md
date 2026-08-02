# Judge-free evaluation: which question is worth going after?

Our study is essentially done. A cheap, automatic way of scoring answers ranks
whole models well but cannot grade an individual answer, and we can prove why:
89 to 96 percent of the per-answer score reflects how predictable the reference
text is, not how good the answer is. The signal tracks resemblance to the
reference's style, not reasoning quality.

Five questions follow from that. Each is a different bet on what the finding
generalizes to. Listed in no particular order. Under each is the closest prior
work and where it stops short, checked in a literature pass.

### As AI gets more capable than the methods we use to check it, does our ability to catch its mistakes break down in a predictable way?

If we can plot that breakdown as a curve, we can tell which checking methods will
still hold up as models keep improving, instead of only comparing them on the
models we have now.

*Closest prior work.* Engels et al. 2025 (arXiv:2504.18530) already plots
oversight success against the capability gap, but on game Elo; Agent Score
Difference (arXiv:2504.03731) is a single score at parity, not a curve. Our edge:
the optimization-pressure-over-time axis, and real math, code, and agentic
capability rather than games.

### When we grade AI answers cheaply and automatically, are we measuring whether the answer looks right, or whether it is right?

Our result suggests cheap graders, including using one AI to judge another,
mostly reward answers that resemble the reference, not answers that are actually
better.

*Closest prior work.* JudgeBench (arXiv:2410.12784) shows judges failing at
objective correctness; ODIN (arXiv:2402.07319) and Length-Controlled AlpacaEval
(arXiv:2404.04475) each remove one bias. None reports the surface-nuisance
fraction of the score as the headline, which our decomposition does.

### Is telling a good answer from a bad one really easier than producing a good answer in the first place?

We found that judging plain correctness is easy but judging quality is not, so
the common assumption that checking is easier than doing may only hold for
right-or-wrong tasks.

*Closest prior work.* Weaver (arXiv:2506.18203), Generator-Validator Consistency
(arXiv:2310.01846), and "Can LLMs Judge Better Than They Generate?"
(arXiv:2606.28050) all study the gap for correctness only. Restricting it to
quality among already-correct answers appears open.

### If we train an AI to score well on a cheap evaluator, does that evaluator stop being trustworthy, and can we tell in advance which ones will break?

An evaluator that looks accurate can fall apart once a model is optimized to
satisfy it (reward hacking). The open question is which signals survive that
pressure.

*Closest prior work.* Scaling Laws for Reward Model Overoptimization
(arXiv:2210.10760) predicts hacking magnitude from optimization, not from a
static property; Skalse et al. (arXiv:2209.13085) prove unhackability is
near-impossible. Predicting hackability in advance from a measurable surface
property appears unclaimed.

### For open-ended work with no clear right answer, can anything cheap judge quality, or do we always need a human?

Essays, research, and long agent tasks have no gold answer to compare against, so
it is unknown whether any low-cost signal tracks quality at all.

*Closest prior work.* BARTScore (arXiv:2106.11520), CCS (arXiv:2212.03827), and
Self-Consistency (arXiv:2203.11171) give label-free signals, but for constrained
or convergent tasks. Whether any survives into open-ended, answer-free work, or
whether human judgment is the floor, is unposed.

---

### The spine (why the program hangs together)

Across all five, one measurable quantity keeps recurring: how much of an
evaluator's score is surface nuisance rather than model-invariant quality. No
prior work defines that fraction and shows it predicts both out-of-distribution
collapse and hackability. Closest are Inside the Unfair Judge (arXiv:2607.11871),
Singhal et al. on length correlations (arXiv:2310.03716), and Eisenstein et al.
Helping or Herding (arXiv:2312.09244), each of which foreshadows one leg. That
unifying predictor is the open gap, and it is a mechanism rather than a trained
metric, which makes it hard to game.
