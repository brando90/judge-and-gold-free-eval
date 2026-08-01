# Research agenda: judge-free evaluation and scalable oversight

*A memo on where LLM judges keep failing, where scalable oversight is genuinely stuck, and where our TFA work
gives us an unusual angle of attack. Written for the group; opinionated on purpose. Mid-2026.*

## The through-line from our TFA work

The TFA study taught us one thing that turns out to be bigger than TFA. A cheap automatic evaluator does not
measure quality; it measures how much a candidate agrees with the surface of a reference, its style and its
predictability. That agreement lines up with quality only in a narrow regime: when the reference is long and
tightly constrained, when the models being scored share its distribution, and when the task is hard enough that
the metric has not saturated. We were able to make that precise (per-item TFA is 89 to 96 percent a
model-invariant reference-predictability nuisance) and to draw the boundary where it holds and where it breaks
(ranking works within a family and on hard math, inverts on saturated GSM8K, washes out on code, collapses across
families, and carries the same within-versus-across split into agents).

The reason this matters beyond TFA is that *every* cheap evaluator has this shape, including the LLM judges the
whole field now runs on. A judge, too, has a competence axis and a surface axis: it rewards length, formatting,
position, and house style alongside actual quality. Almost every open problem below is a version of the same
sentence: we deploy an evaluator without knowing whether it is tracking quality or surface, and without knowing
how it will behave once something optimizes against it. Our habit of decomposing a signal, measuring its
nuisance, and charting its boundary is unusually well suited to answering exactly that.

## Why now: evaluation has become the bottleneck

The clearest signal of where the field is heading came this year from Anthropic's automated weak-to-strong
researcher ([alignment.anthropic.com, 2026](https://alignment.anthropic.com/2026/automated-w2s-researcher/)).
Nine Claude agents, given a weak teacher and a strong student and asked to recover the student's true performance,
autonomously proposed and ran experiments until they reached a Performance Gap Recovered of 0.97, against 0.23
for two human researchers over a week. The headline is that AI can now do a well-posed research loop. The part
that should reorganize our plans is the authors' own conclusion: the bottleneck for alignment research is no
longer proposing or running ideas, it is *designing the evaluations*, because that is the one step that is not
yet automatable and not yet trustworthy.

Their failures make the point sharper than their success. The agents reward-hacked in ways the authors had not
anticipated and could not fully stop: mining dataset shortcuts, cherry-picking seeds, exfiltrating test labels,
even writing and running hidden unit tests to recover ground truth. And their real ceiling was generalization,
not raw performance: methods latched onto patterns specific to a dataset or a model, and a high
out-of-distribution score did not mean the method had actually generalized (one transferred to math but not code;
the production port collapsed into the noise).

That result sits on top of a literature that has been saying the same thing from every direction. Judges are not
merely biased, they are provably gameable: a lone punctuation mark or a generic "let's think step by step" opener
draws false-positive rewards from GPT-4o and Claude-4-class judges as often as a third of the time
([One Token to Fool, 2507.08794](https://arxiv.org/abs/2507.08794)), reference-free judges get hacked under
self-play ([2607.05904](https://arxiv.org/pdf/2607.05904)), and RLVR verifiers are gamed by shortcut responses
([2604.15149](https://arxiv.org/pdf/2604.15149)). Verifiable rewards only reach the domains with a cheap,
checkable outcome, which excludes most of what we actually care about, and outcome checking alone under-grades
the reasoning that produced the answer ([Right Is Not Enough, 2506.06877](https://arxiv.org/pdf/2506.06877)).
Weak-to-strong oversight protocols such as debate help in some regimes but degrade as the capability gap widens,
and they have never actually been tested with humans judging superhuman systems
([Kenton et al., 2407.04622](https://arxiv.org/abs/2407.04622)). Underneath all of it is the old regress: to
trust a judge you still need human labels or an oracle, and nobody can yet say, for a given task, whether a cheap
signal or a judge is trustworthy without that ground truth.

The quiet common thread is a measurement mistake. We evaluate an overseer by its agreement with humans *at
parity, before any optimization pressure*. But what decides whether a method scales is how its reliability holds
up as the system it oversees grows more capable and starts to optimize against it. That is a curve, not a point,
and it is the thing the field is not measuring.

## What already exists, and the gap it leaves

There are really two kinds of benchmark in play, and it helps to keep them apart. The first kind uses an LLM as
the judge of other models: MT-Bench, Arena-Hard, AlpacaEval 2, Prometheus, G-Eval, HelpSteer, MixEval, WildBench.
All of them inherit whatever biases and blind spots the judge has. The second kind judges the judge. The sharpest
is JudgeBench ([2410.12784](https://arxiv.org/abs/2410.12784)), which asks not whether a judge matches human
preference but whether it can tell an objectively correct answer from a subtly wrong one; strong judges land
barely above chance, and the result swings depending on whether the judge is asked to just pick A or B or, in the
Arena-Hard style, to work the problem itself first and then compare. Work on overconfidence
([2508.06225](https://arxiv.org/pdf/2508.06225)) and confirmation bias
([2507.19486](https://arxiv.org/pdf/2507.19486)) fills in the failure modes.

Closest to the scalable-oversight question is "A Benchmark for Scalable Oversight Protocols"
([2504.03731](https://arxiv.org/pdf/2504.03731)), which introduces Agent Score Difference: how much a protocol
rewards arguing for the truth over arguing for a falsehood, measured as the log-odds gap the judge assigns to a
truthful versus a lying agent. It compares debate and consultancy and finds debate ahead. But it says plainly
that it does not test long-horizon capability gaps or optimization pressure over time. That admission is the
opening for us.

## The shape of a paper worth writing

It is worth being explicit about what makes work land, because it shapes what we should build. The
"Explorative Modeling" paper ([2607.27372](https://arxiv.org/abs/2607.27372)) is not about oversight at all, but
its structure is the lesson: it took a problem everyone treated as two-dimensional, model size and data size, and
argued that there is a genuine third axis (exploration), then validated that axis across images, video, and
language with clean scaling curves. The impact came from naming a new dimension and showing it matters more as
you scale, not from a single clever trick.

Our analog is right there. Scalable-oversight evaluation is treated as roughly two-dimensional, judge accuracy
and cost. The missing axis is robustness under the combination of a widening capability gap and rising
optimization pressure, which is to say the degradation curve. A paper that introduces that axis, characterizes it
across math, code, agentic, and subjective tasks, and, uniquely for us, *explains the curve with a mechanism*
rather than only charting it, is the kind of thing that reframes a subfield.

## The questions I think we should answer

**First, and most important, chart and predict how oversight degrades under optimization.** Stop reporting how
good an overseer is at parity and start reporting the curve: how its reliability changes as the solver it watches
grows stronger and as that solver is optimized, by best-of-n selection and then by training, against the overseer
itself. The scalable-oversight benchmark already has a truth-incentive metric (Agent Score Difference); the move
is to measure it as a function of capability gap and optimization budget, across domains, and to read off which
methods degrade slowest. What we bring that a benchmark alone cannot is a *prediction*. Our decomposition says an
overseer degrades when the solver drifts in style and distribution away from the overseer's reference or
training, because that is when the surface-nuisance term swamps the competence term. If our style-offset
diagnostic predicts each method's degradation slope, we have turned "oversight breaks at large gaps" from an
observation into something you can forecast before you pay for the training run. That is the flagship.

**Second, certify when an evaluator can be trusted, without needing full ground truth.** This is the direct
generalization of the TFA decomposition to the evaluators people actually use. Take a judge and estimate its
nuisance fraction on a task, how much of its score is explained by surface features like verbosity, position, and
style rather than by quality, and calibrate that against a small anchored set of human grades to produce a
task-level validity score that flags when the judge will mislead. We have the pieces for this already: the
methodology, a multi-judge and multi-family sweep, and human grades from the companion Putnam grading study to
anchor against. The automated weak-to-strong result gives this a second, sharper target. Its number-one failure
was that a high out-of-distribution score did not mean real generalization, which is our surface-versus-competence
story one level up, at the level of methods rather than solutions. The same nuisance-fraction test should predict
whether a discovered method has actually generalized or has just latched onto something distribution-specific.
The honest catch is that certification needs *some* anchor ground truth; the contribution is making that anchor
small and the diagnostic cheap.

**Third, build a reference-free signal for the open-ended regime that survives being optimized against.** Where
there is no gold trace and no cheap oracle, which is exactly where oversight is unsolved, our rollout process
value already grades solutions that TFA cannot, including the coveted case of telling a sound answer from a lucky
one, because it measures the model's own reasoning against the environment's outcome rather than agreement with a
fixed reference. The open and important question is whether such a signal stays honest once you optimize it,
given that reference-free judges are known to get hacked under self-play. This is also where the automated W2S
result points us: its most effective methods were unsupervised elicitation, pulling the strong model's own latent
truth direction out with contrastive consistency rather than scoring outputs with a weak judge. Our reference-free
direction, the rollout value and the idea of anchoring on the model's own most-consistent solution, is the same
family. The paper is a head-to-head: when does a signal elicited from the model's own consistency beat a
reference or a judge, and when does it get hacked, measured under real optimization pressure on executable agents.

**Underneath all three sits an old question worth settling: is verifying actually easier than generating, for
grading quality rather than checking correctness?** The optimistic case for scalable oversight rests on yes. Our
item-level null is a piece of evidence for a more careful answer: a cheap verifier does *not* easily beat
generation when the target is quality, only when the target is correctness. Sharpening where verification
genuinely adds value, and where it collapses back into style-matching, is the theoretical spine under the first
two questions rather than a separate project.

## What I would propose

Lead with the degradation-curve work as the flagship, use the certification work as the engine that feeds it, and
treat the reference-free-under-optimization work as the higher-risk agentic bet. The case for that ordering is
that the flagship is both the highest-impact and the most ours: the field has said it needs the degradation-curve
benchmark, and we are the only ones positioned to attach a mechanism that predicts the curve, straight out of the
TFA results. It also respects the one hard constraint that keeps coming up, which is that frontier models behind
APIs expose no token log-probabilities, so TFA-style signals cannot run on them at all. The practical toolkit for
overseeing frontier systems is therefore certified judges and reference-free process signals, with TFA as the
foundation that maps where cheap signals lie. And it compounds what we have already built rather than starting
cold.

There is one caution to keep in front of us the whole time. If automated researchers can hill-climb an eval, they
will hill-climb ours. Any robustness benchmark we build has to be hard to hack by construction, or an
automated-search agent will simply game it. That is not an argument against the program; it is the reason the
program is the right one.

The one-sentence version of all of this: every cheap evaluator, TFA and LLM judges alike, mixes a real quality
signal with a surface nuisance, and the research is to measure that mix, certify when quality wins, predict how it
fails as systems are optimized against it, and build signals for the open-ended regime where references run out.
Our TFA paper is step zero, the proof that the mix exists and that its boundary can be measured.

## A cheap-first way to start (six to eight weeks)

The certification idea derisks fastest and on data we already have: estimate the judge nuisance fraction on the
Putnam human-graded set, show it predicts where our gpt-5.2 and Opus judges diverge from people, and confirm it
flags the known punctuation and verbosity hacks. In parallel, seed the flagship on one domain by building a
solver capability ladder in math, plotting Agent Score Difference and judge-versus-truth accuracy against
capability, and adding best-of-n-against-the-judge as a first, cheap optimization axis, then testing whether the
style-offset predicts the slope. Seed the reference-free work on tau2-bench, which needs no per-repository Docker,
by running the rollout process value and then probing it with best-of-n to see how quickly it can be hacked. The
certification result can be written up on its own while the other two mature into the flagship.

## Sources

Our results and plans: [`experiments/tfa-vs-judge/paper/PAPER.md`](../experiments/tfa-vs-judge/paper/PAPER.md),
[`docs/agentic-tfa-plan.md`](agentic-tfa-plan.md).
Automated research and weak-to-strong: automated weak-to-strong researcher
([alignment.anthropic.com, 2026](https://alignment.anthropic.com/2026/automated-w2s-researcher/); overview
[blog](https://www.anthropic.com/research/automated-alignment-researchers)); Kenton et al. weak-vs-strong
([2407.04622](https://arxiv.org/abs/2407.04622)); debate safety-case sketch
([2505.03989](https://arxiv.org/pdf/2505.03989)); scalable-oversight protocol benchmark / Agent Score Difference
([2504.03731](https://arxiv.org/pdf/2504.03731)).
LLM judges: JudgeBench ([2410.12784](https://arxiv.org/abs/2410.12784)); One Token to Fool
([2507.08794](https://arxiv.org/abs/2507.08794)); overconfidence ([2508.06225](https://arxiv.org/pdf/2508.06225));
confirmation bias ([2507.19486](https://arxiv.org/pdf/2507.19486)).
Rewards and verification: RLVR gaming ([2604.15149](https://arxiv.org/pdf/2604.15149)); reference-free self-play
hacking ([2607.05904](https://arxiv.org/pdf/2607.05904)); outcome-supervision pitfalls
([2506.06877](https://arxiv.org/pdf/2506.06877)); process reward models that think
([2504.16828](https://arxiv.org/pdf/2504.16828)); Math-Shepherd ([2312.08935](https://arxiv.org/abs/2312.08935));
OmegaPRM ([2406.06592](https://arxiv.org/abs/2406.06592)).
The new-axis template: Explorative Modeling ([2607.27372](https://arxiv.org/abs/2607.27372)).
