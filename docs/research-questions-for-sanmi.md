# Next research directions: which one should we take?

Our TFA study is essentially done. A cheap, reference-anchored signal **ranks
models well but cannot grade an individual solution**, and we can prove why: 89
to 96 percent of the per-item score is reference nuisance, not competence.

Five directions open from there, listed in no particular order. My own read is
at the very bottom, kept separate on purpose.

---

### The map: finish the reference-anchored picture, or prove the no-go

We ruled out single-reference TFA at the item level, but multi-reference,
outcome-gated, and per-step variants are untested. We still do not know whether
*any* reference-anchored signal can grade within the set of correct answers.

**First test:** outcome-gated multi-reference TFA on the datasets where
single-reference failed. Either we recover a signal or we close the door
formally. Reuses the existing TFA pipeline, so this is days, not weeks.

### Certification: check an evaluator before we deploy it, without full ground truth

Today we find out a judge is hackable only after it fails (a stray colon flips
GPT-4o up to 35 percent of the time). There is no cheap pre-flight check.

**First test:** run our nuisance decomposition on an LLM judge (quality vs
length, style, position) from a small human-graded anchor set, and see whether
the resulting nuisance fraction predicts where the judge gets gamed on
JudgeBench. The decomposition machinery already exists.

### Process value: a reference-free signal that grades agents and survives being optimized against

Our rollout process value grades solutions, but it needs a gold trace and costs
roughly 100x TFA. Agentic tasks rarely have gold traces, and any reward signal
gets gamed once you train against it.

**First test:** rollout value grounded in an environment's own success oracle on
SWE-bench-style tasks, then optimize an agent against it and measure how much
reward hacking shows up.

### Robustness curves: do oversight signals degrade predictably as the solver gets stronger?

Benchmarks score overseers at parity. Nobody measures how reliability bends as
the capability gap and the optimization pressure grow, which is the thing that
actually decides whether a method scales.

**First test:** fix a task, sweep solver scale, plot judge and TFA reliability
against the capability gap, and check whether the style-offset we already
measured predicts the slope.

### No oracle: is there any cheap signal where there is no checkable answer at all?

Everything above has a checkable answer. Open-ended work (writing, research
proposals, open agentic goals) may have no cheap floor beneath human grading or
debate, and we have not tested it.

**First test:** apply the nuisance decomposition to a subjective-grading dataset
with human labels, and see whether quality separates from surface at all.

---

### My read (last, on purpose)

If it were my call I would open with **certification**. It is the cheapest, it
reuses the decomposition we already built, and it becomes a concrete result in a
couple of weeks, which then feeds the bigger swing in **robustness curves**.
Robustness curves is the higher-ceiling paper but the larger commitment. **The
map** is the safe finisher for the current work. I would treat **process value**
and **no oracle** as follow-ons once one of the first two lands.
