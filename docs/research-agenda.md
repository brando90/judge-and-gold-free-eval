# Research agenda: judge-free evaluation and scalable oversight

*Where LLM judges are used, where scalable oversight is unsolved, and where we can make real progress.
Drafted from the TFA judge-free-eval results (this repo), a scalable-oversight brainstorm, and the mid-2026
literature. Opinionated on purpose.*

---

## 0. Where we sit, and the one idea that carries forward

Our TFA study proved a specific, general-feeling thing: **a cheap automatic evaluator measures agreement with a
reference's surface (style, predictability), and that coincides with quality only under narrow conditions**
(a long, constrained reference; models that share its distribution; no saturation). We turned that into a
mechanism (per-item TFA is 89 to 96 percent a model-invariant "reference-predictability" nuisance) and a
boundary map (ranking holds on hard math, inverts on saturated GSM8K, washes out on code, collapses across
families, extends to agents with the same within/cross split).

The forward bet of this agenda: **that lens is not about TFA. It is about every cheap evaluator, including LLM
judges.** Judges are also cheap proxies with a competence axis and a surface-nuisance axis (verbosity, position,
style, format). The unsolved problems below are all versions of "we deploy an evaluator without knowing whether
it is measuring quality or surface, and without knowing how it degrades under pressure." Our methodology
(decompose the signal, measure the nuisance, map the boundary) is unusually well-suited to answering that.

---

## 1. The unsolved core (grounded in the 2026 literature)

**a. Judges are provably hackable, not merely biased.** "One Token to Fool LLM-as-a-Judge"
([2507.08794](https://arxiv.org/abs/2507.08794)) shows punctuation and generic openers ("Let's solve step by
step", ":") elicit up to 35 percent false-positive rewards from GPT-4o / Claude-4-class judges. Reference-free
judges get reward-hacked under self-play ([2607.05904](https://arxiv.org/pdf/2607.05904)), and RLVR verifiers are
gamed by shortcut responses ([2604.15149](https://arxiv.org/pdf/2604.15149)). Overconfidence and confirmation
bias compound it ([2508.06225](https://arxiv.org/pdf/2508.06225); [2507.19486](https://arxiv.org/pdf/2507.19486)).

**b. Verifiable rewards only reach cheaply-checkable domains.** The properties that make RLVR reliable confine it
to clean-outcome tasks; long-form, subjective, and agentic work lack a cheap oracle, and outcome supervision
alone under-grades reasoning quality ("Right Is Not Enough", [2506.06877](https://arxiv.org/pdf/2506.06877)).
Process reward models help but must themselves be learned and can be gamed
([Process Reward Models That Think, 2504.16828](https://arxiv.org/pdf/2504.16828)).

**c. Weak-to-strong oversight works in a regime and breaks past it.** Debate beats consultancy but degrades as
the capability gap grows, and has only been tested with sub-superhuman AI, not humans judging superhuman AI
([Kenton et al., 2407.04622](https://arxiv.org/abs/2407.04622); [debate safety-case sketch,
2505.03989](https://arxiv.org/pdf/2505.03989)). Anthropic's automated-alignment-researcher work shows the same
shape: generalizes on math (0.94) but degrades on code (0.47), and reward-hacks the evaluator when it can
([Anthropic, 2026](https://www.anthropic.com/research/automated-alignment-researchers)).

**d. The evaluation regress is unbroken.** To trust a judge you still need human labels or an oracle. Nobody can
yet certify, for a given task, whether a cheap signal or a judge is trustworthy, without that ground truth.

**e. The measurement gap (the key insight).** Existing evaluations measure **accuracy or agreement at parity**,
before optimization pressure. The scalable question is **robustness as the capability gap widens and as the
system is optimized against the overseer**. That curve, not the point estimate, is what predicts whether a method
scales. This is the axis the field is not yet measuring.

---

## 2. The benchmark landscape (so we know what exists)

**Benchmarks that use an LLM as the judge of other models:** MT-Bench, Arena-Hard, AlpacaEval 2, Prometheus,
G-Eval, AlignEval, HelpSteer, MixEval, WildBench. All inherit the judge's biases and hackability.

**Meta-benchmarks that judge the judge:** **JudgeBench** ([2410.12784](https://arxiv.org/abs/2410.12784), ICLR
2025) asks whether a judge distinguishes *objectively correct from incorrect* (ground-truth pairs with subtle
errors), not whether it matches human preference; strong judges (GPT-4o) land barely above random, and results
swing with the judge prompt (minimal "pick A or B" vs the Arena-Hard "generate your own answer first, then
compare" recipe that reduces anchoring). Related: overconfidence diagnosis
([2508.06225](https://arxiv.org/pdf/2508.06225)), confirmation bias ([2507.19486](https://arxiv.org/pdf/2507.19486)).

**Scalable-oversight protocol benchmarks:** "A Benchmark for Scalable Oversight Protocols"
([2504.03731](https://arxiv.org/pdf/2504.03731), ICLR 2025) introduces **Agent Score Difference (ASD)**: how much
a protocol advantages truth over falsehood, log P(judge believes truthful agent) minus log P(judge believes lying
agent). It compares debate vs consultancy. **By its own admission it does not test long-horizon capability gaps or
optimization pressure over time.** That is the opening.

---

## 3. The structural template for an impactful paper (from "Explorative Modeling", 2607.27372)

That paper is not about oversight. Its lesson is *how high-impact work is shaped*: it takes a problem everyone
treated as two-dimensional (model size, data size) and **introduces a genuine third axis** (exploration), then
validates it **thoroughly across modalities** (image, video, language) with **scaling curves** showing the axis
matters more with scale (gains climbing 7 to 36 percent).

**Our analog.** Scalable-oversight evaluation is treated as roughly two-dimensional: judge accuracy / agreement,
and cost. The missing third axis is **robustness under (capability gap x optimization pressure)**, the
degradation curve. An impactful paper introduces that axis, validates it across domains (math, code, agentic,
subjective), and, uniquely for us, **explains the curve with a mechanism** rather than just charting it.

---

## 4. Top research questions (ranked by impact x our edge)

### RQ1 (flagship). Oversight robustness curves: a cross-domain benchmark AND a mechanism for how oversight degrades under capability gap and optimization pressure.

- **The move.** Stop reporting oversight quality at parity. Report the **curve**: overseer reliability as a
  function of (i) solver capability (widen the gap), and (ii) optimization pressure (let the solver be trained or
  best-of-n selected against the overseer). Extend ASD to an **ASD-under-optimization** and a **degradation
  slope**: the method whose reliability curve degrades slowest is the more scalable one. Measure alongside cost
  (compute, human time). This operationalizes the brainstorm's four axes: truthfulness under optimization,
  performance vs solver strength, adversarial susceptibility, cost.
- **Our unique contribution beyond a benchmark.** We do not just chart the curve, we **predict it**. Our
  competence-vs-nuisance decomposition and the cross-family **style offset** give a concrete, measurable
  mechanism for *why* an overseer degrades: as the solver diverges in style/distribution from the overseer's
  reference or training, the nuisance term grows and the reliability curve bends. This turns "oversight breaks at
  large gaps" (Kenton et al.) from an observation into a **predictor**, which is what would make this more than a
  V2 of the ASD benchmark.
- **Cross-domain (the multi-modal thoroughness of the template).** Math, code (SWE-bench), agentic tool-use
  (tau2-bench), and a subjective/long-form domain, so the curve is characterized where oversight actually has to
  work, not just on toy tasks.
- **First experiment.** Two-player setup, fixed overseer, a solver ladder of increasing capability; for each
  point measure ASD, judge-vs-ground-truth accuracy, and susceptibility to adversarial/optimized responses
  (best-of-n against the judge, master-key probes). Plot reliability vs capability and vs optimization budget.
  Then test whether our style/nuisance diagnostic predicts each method's degradation slope.
- **Why highest-impact.** It gives the field the benchmark it admits it is missing, with a theory attached, and
  it is a direct, ownable extension of our results. It reframes scalable oversight around the right axis.
- **Risk.** Building faithful capability ladders and optimization loops is work; mitigate by starting with
  best-of-n optimization (cheap) before full RL.

### RQ2. Certify, without full ground truth, when an automatic evaluator (cheap signal or LLM judge) is trustworthy for a task.

- **Gap.** We deploy judges and proxies blind; JudgeBench shows even strong judges are near-random on objective
  correctness, and prompt-dependent.
- **Our edge.** Generalize the TFA competence-vs-nuisance decomposition to **judges themselves**: estimate a
  judge's **nuisance fraction** on a task (how much of its score is verbosity/style/position/format vs quality),
  and produce a task-level **validity score** that flags when the judge will mislead, calibrated with minimal
  anchored human labels. Extend to other cheap proxies (perplexity, BPC, embedding similarity) so the output is a
  general "is this evaluator measuring quality here?" test.
- **First experiment.** Define the judge nuisance fraction; show it predicts where our gpt-5.2 / Opus judges
  diverge from **humans** on Putnam-AXIOM-Grading (we have that data via the companion study), and that it flags
  the master-key / verbosity failures from [2507.08794](https://arxiv.org/abs/2507.08794).
- **Why high-impact.** Turns automatic evaluation from hope into certification, usable by everyone running
  LLM-judge benchmarks and reward models. Directly attacks the evaluation regress.
- **Risk.** Certification needs some anchor ground truth; making the anchor minimal is the contribution.

### RQ3. Reference-free process signals for open-ended / agentic tasks that grade AND survive optimization pressure.

- **Gap.** No gold, no cheap oracle is exactly where oversight is unsolved, and reference-free signals get
  reward-hacked under self-play ([2607.05904](https://arxiv.org/pdf/2607.05904)).
- **Our edge.** Our rollout process value already grades where TFA cannot (partial rho +0.43, sound-vs-lucky
  +0.19), grounded in an environment's own outcome oracle. The open problem is a version that stays honest under
  optimization.
- **First experiment.** Rollout process value on executable agents (SWE-bench with a scaffold, or tau2-bench);
  put it under best-of-n / RL optimization and measure hacking; compare to generative PRMs
  ([2504.16828](https://arxiv.org/pdf/2504.16828)); test a hacking-robust variant (ensemble or
  consistency-penalized). This is also RQ1's "optimization pressure" axis instantiated for a process signal.
- **Why high-impact.** Unlocks reward and evaluation for the subjective/agentic majority of high-value tasks.
- **Risk.** Hacking may be partly fundamental (consistency is not truth); a clean characterization is still a
  contribution.

### RQ4. Does the generation-verification gap hold for grading reasoning quality, and where?

- **Gap.** The optimistic premise of scalable oversight is "verifying is easier than generating." Our item-level
  null is direct evidence that a cheap verifier does not easily beat generation for *quality* (only for
  correctness). Sharpen where verification genuinely helps (constrained references, correctness) vs where it
  collapses to style-matching (open-ended quality).
- **Why it matters.** It is the theoretical backbone under RQ1 and RQ2, and a foundational claim on its own.
  Best folded into RQ1/RQ2 rather than run standalone.

---

## 5. Recommendation (what to propose to Sanmi)

**Lead with RQ1 as the flagship**, with RQ2 as the certification engine that feeds it and RQ3 as the high-risk
agentic follow-on. Rationale:

- **It is the highest-impact, most ownable move.** The field wants the degradation-curve benchmark (the existing
  ASD benchmark admits it is missing) and we uniquely bring a *mechanism* that predicts the curve, straight from
  our TFA results. That is the "new axis + thorough cross-domain validation" shape of an impactful paper.
- **It respects the frontier-API constraint.** Frontier API models expose no token log-probabilities, so
  TFA-style signals cannot run on them. The practical oversight toolkit for frontier systems is therefore
  certified judges (RQ2) and reference-free process signals (RQ3), with TFA as the foundation that maps the
  limits. RQ1 measures all of them on the axis that matters.
- **It compounds our assets.** We already have the boundary methodology, the variance decomposition, a
  multi-judge / multi-family sweep, the rollout-process-value harness, and (via the companion study) human
  grades to anchor certification.

**Unifying thesis.** Every cheap evaluator, TFA and LLM judges alike, mixes a quality signal with a surface
nuisance. The program is to (1) measure that mix and certify when quality dominates (RQ2), (2) chart and predict
how it degrades under capability gap and optimization pressure (RQ1), and (3) build signals for the open-ended
regime where references fail (RQ3). Our TFA paper is step zero: proof that the mix exists and that its boundary is
measurable.

---

## 6. Concrete first 6-8 weeks (derisking, cheap-first)

1. **RQ2 seed:** compute the judge nuisance fraction on Putnam-AXIOM-Grading (human-anchored); show it predicts
   judge-vs-human divergence and catches master-key probes. Cheap, uses data we have.
2. **RQ1 seed:** on one domain (math), build a solver capability ladder and plot ASD + judge accuracy vs
   capability, plus best-of-n-against-the-judge as the optimization axis. Test whether the style/nuisance
   diagnostic predicts the slope.
3. **RQ3 seed:** rollout process value on tau2-bench (no Docker-per-repo), then a best-of-n hacking probe.
4. Write up (1) as a standalone certification result while (2) and (3) mature into the flagship.

---

## Sources

Our results: [`experiments/tfa-vs-judge/paper/PAPER.md`](../experiments/tfa-vs-judge/paper/PAPER.md), plan
[`docs/agentic-tfa-plan.md`](agentic-tfa-plan.md).
Scalable oversight: Kenton et al. weak-vs-strong ([2407.04622](https://arxiv.org/abs/2407.04622)); debate
safety-case sketch ([2505.03989](https://arxiv.org/pdf/2505.03989)); ASD benchmark
([2504.03731](https://arxiv.org/pdf/2504.03731)); Anthropic automated alignment researchers
([blog](https://www.anthropic.com/research/automated-alignment-researchers)).
LLM judges: JudgeBench ([2410.12784](https://arxiv.org/abs/2410.12784)); One Token to Fool
([2507.08794](https://arxiv.org/abs/2507.08794)); overconfidence ([2508.06225](https://arxiv.org/pdf/2508.06225));
confirmation bias ([2507.19486](https://arxiv.org/pdf/2507.19486)).
Rewards / verification: RLVR gaming ([2604.15149](https://arxiv.org/pdf/2604.15149)); reference-free self-play
hacking ([2607.05904](https://arxiv.org/pdf/2607.05904)); outcome-supervision pitfalls
([2506.06877](https://arxiv.org/pdf/2506.06877)); PRMs that think ([2504.16828](https://arxiv.org/pdf/2504.16828));
Math-Shepherd ([2312.08935](https://arxiv.org/abs/2312.08935)); OmegaPRM ([2406.06592](https://arxiv.org/abs/2406.06592)).
Impactful-paper template: Explorative Modeling ([2607.27372](https://arxiv.org/abs/2607.27372)).
