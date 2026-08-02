# The program: reliable judges without ground truth

One mission: build judges that stay reliable when they are **optimized against**
and when the model they judge is **smarter than them**, in domains with little
ground truth, and measure that reliability.

This grows out of a finished result. A cheap, automatic way of scoring answers
ranks whole models well but cannot grade an individual answer, and we can prove
why: 89 to 96 percent of the per-answer score reflects how predictable the
reference text is, not how good the answer is. The signal tracks resemblance to
the reference's style, not reasoning quality.

Five steps, in dependency order. The first is a gate: nothing else is measurable
without it.

### 1. The yardstick: measuring a judge with little ground truth

With little ground truth, how do you tell a good judge from a bad one at all?
Split its score into a real-quality part and a surface-nuisance part (the
nuisance fraction) from a small anchor of labels. It must be a mechanism, not a
trained metric, so it cannot itself be gamed. Every step below needs this number.

### 2. Does it survive smarter models?

Does the judge's reliability fall predictably as the model it judges grows more
capable than it, and does the yardstick predict the fall? Plot reliability
against the capability gap across domains, and test whether the nuisance fraction
predicts the slope.

### 3. Does it survive reward hacking?

When a model is optimized against the judge, does the judge break, and can we
predict which judges break before we optimize, from the nuisance fraction alone?

### 4. How do we design one that survives both?

What construction holds up on both axes, especially where ground truth is scarce:
reference-free and process signals grounded in an environment's own success
oracle, ensembles, self-consistency, debate? Build candidates, score each with
step 1, and keep what lowers the nuisance fraction and flattens the curves.

### 5. Where is the floor?

Is there an open-ended regime, with no checkable answer, where no cheap judge
survives, so the honest design keeps a human or an environment oracle in the
loop? Find where the nuisance fraction cannot be driven down. That boundary is a
result in itself.

**The spine.** One static, mechanism-based quantity, the nuisance fraction,
predicts both capability-gap collapse (step 2) and hackability (step 3). That
single predictor is what makes this one program rather than five errands, and the
literature pass below finds it unclaimed.

---

## Appendix: the five as separate bets, with prior work

Before the program, these were the five as independent bets to choose between.
Each is a different generalization of our result; the program reorders them into
one dependency chain (yardstick = bet 2, survives smarter models = bet 1,
survives hacking = bet 4, design = bet 3, the floor = bet 5). Under each is the
closest prior work and where it stops short, checked in a literature pass.

### As AI gets more capable than the methods we use to check it, does our ability to catch its mistakes break down in a predictable way?

*Closest prior work.* Engels et al. 2025 (arXiv:2504.18530) already plots
oversight success against the capability gap, but on game Elo; Agent Score
Difference (arXiv:2504.03731) is a single score at parity, not a curve. Our edge:
the optimization-pressure-over-time axis, and real math, code, and agentic
capability rather than games.

### When we grade AI answers cheaply and automatically, are we measuring whether the answer looks right, or whether it is right?

*Closest prior work.* JudgeBench (arXiv:2410.12784) shows judges failing at
objective correctness; ODIN (arXiv:2402.07319) and Length-Controlled AlpacaEval
(arXiv:2404.04475) each remove one bias. None reports the surface-nuisance
fraction of the score as the headline, which our decomposition does.

### Is telling a good answer from a bad one really easier than producing a good answer in the first place?

*Closest prior work.* Weaver (arXiv:2506.18203), Generator-Validator Consistency
(arXiv:2310.01846), and "Can LLMs Judge Better Than They Generate?"
(arXiv:2606.28050) all study the gap for correctness only. Restricting it to
quality among already-correct answers appears open.

### If we train an AI to score well on a cheap evaluator, does that evaluator stop being trustworthy, and can we tell in advance which ones will break?

*Closest prior work.* Scaling Laws for Reward Model Overoptimization
(arXiv:2210.10760) predicts hacking magnitude from optimization, not from a
static property; Skalse et al. (arXiv:2209.13085) prove unhackability is
near-impossible. Predicting hackability in advance from a measurable surface
property appears unclaimed.

### For open-ended work with no clear right answer, can anything cheap judge quality, or do we always need a human?

*Closest prior work.* BARTScore (arXiv:2106.11520), CCS (arXiv:2212.03827), and
Self-Consistency (arXiv:2203.11171) give label-free signals, but for constrained
or convergent tasks. Whether any survives into open-ended, answer-free work, or
whether human judgment is the floor, is unposed.

### The spine (why the program hangs together)

No prior work defines a single surface-nuisance fraction and shows it predicts
both out-of-distribution collapse and hackability. Closest are Inside the Unfair
Judge (arXiv:2607.11871), Singhal et al. on length correlations
(arXiv:2310.03716), and Eisenstein et al. Helping or Herding (arXiv:2312.09244),
each of which foreshadows one leg. That unifying predictor is the open gap, and
it is a mechanism rather than a trained metric, which makes it hard to game.
