# Round 29 registration DRAFT: human validation of the labels (R29)

**STATUS: DRAFT. NOT REGISTERED. NO DATA GENERATED.**

Specification only; no registration weight. Register by committing the final protocol with a timestamp
before any annotation begins.

## Why this is the most important open item

No label anywhere in the paper was checked by a human. Specifically:

* Prevalence labels come from LLM annotators with $\kappa \le 0.35$ on the several-versus-other label
  (`app:prevalence`).
* The registered any-format label audit **failed its own bound**: Opus 5 confirmed 86.2% of the replies the
  rule credits, against 90% predicted (`app:grid`; recorded as falsified in the ledger).
* A GPT-5-mini relabel of the first audit disagreed enough that the paper concedes its rates are likely low.
* HLE labels come from HLE's own judge — the same judge whose behaviour is under study, which makes the
  "HLE judge credits 0%" row near-tautological and is already flagged as such.

Prevalence carries much of the "who should care" argument, so soft rates make the reuse case soft.

**Scope note, to keep the priority honest.** The reuse argument has three legs and only one is
LLM-labeled: (a) prevalence in reuse datasets — soft, this proposal; (b) the 35-of-43 grader survey — a
document survey, solid; (c) the benchmark study, in which shipped graders and two RL verifiers score 30 to
67 points below answer-list accuracy using **MACE's own shipped answer lists**, not our labels. Leg (c) does
not depend on any label produced by this project. If R29 is not run, the reuse *magnitude* claim softens;
the demonstration does not collapse.

## Minimum viable version

Human-label a sample from the two datasets that carry the reuse argument: **NQ-open** and the
**WebInstruct-verified** RL training set.

* **Annotators.** Two or three, independent, using the paper's existing label definitions verbatim
  (`app:prevalence`). Annotators see the question only, never the LLM label.
* **Sample.** A few hundred items per dataset, drawn with a recorded seed from the same pools the LLM
  annotators labeled, so the comparison is paired.
* **Report.** Inter-annotator $\kappa$; $\kappa$ against the LLM labels; and whether the LLM rates sit
  inside the human confidence intervals.
* **Also human-check a subsample of the any-format labels**, since that audit already failed its bound.
  Stratify by any-format label as the Opus 5 audit did.

## Predictions (to be fixed before annotation)

* **P-R29-1.** Inter-annotator $\kappa$ on the several-versus-other label exceeds the LLM annotators'
  $\kappa \le 0.35$.
* **P-R29-2.** The human several-answer rate for the WebInstruct-verified set falls inside the reported
  interval around 5.5%.
* **P-R29-3.** The human several-answer rate for NQ-open falls inside the reported 30% to 44% band.
* **P-R29-4.** Human reading confirms at least 86.2% of the replies the any-format rule credits (the rate
  Opus 5 reached), on the same strata.

A failure of P-R29-2 or P-R29-3 is reportable and must be reported: it bounds the reuse claim, which is
exactly what the exercise is for.

## Fallback if human annotation is out of reach

State the exposure plainly in the abstract, not only in Limitations. The prevalence figures are currently
carried with more confidence in the main text than `app:prevalence` supports. This is a text change, not an
experiment, and does not need registration.

## Consequence for the AI use statement

The AI use statement currently ends "no label was checked by human annotators." If R29 runs, that sentence
must be rewritten to state who annotated, how many items, and that the annotators were authors (if they
were). Author annotation is acceptable practice and must be disclosed as such, including that annotators
were not blind to the hypothesis.

## Lower priority, no new runs needed

Three graders grade their own models' answers in the benchmark study. Self-preference appears in the paper's
own data (GPT-4.1 credited 20.7% of GPT-4.1-mini's wrong answers under the direct prompt against 13.9% of
Haiku 4.5's; `registration_round27.md` post hoc). Limitations mentions the self-grading; adding the forward
reference would show a reviewer it is measured rather than merely acknowledged.
