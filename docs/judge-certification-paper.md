# Certify Your Judge: A Cheap Protocol That Tells Whether an LLM Judge Grades Substance or Style

*Two-page draft. [pending] marks numbers from experiments currently running; everything else is final.*

## The problem

LLM judges now sit inside leaderboards, data filters, and reward pipelines, and the standing objection
to all of them is the same: agreement between judges is reliability, not validity, and a judge can be
reliable while grading the wrong thing. The style-over-substance literature has documented that judges
in general preference pools reward fluency and length. But "judges score surface" is usually asserted
about judges in general, and never measured for the particular judge, task, and prompt someone is about
to deploy. There is no accepted procedure for answering the only question that matters in practice:
*does my judge, on my task, measure what I think it measures?*

We propose and validate such a procedure. It costs a few hundred dollars of annotator time, produces a
pass/fail verdict with confidence intervals, and — the part that surprised us — the first judge we ran
it on passed.

## The protocol

Four components, all necessary.

**1. Two blind axes, not one.** Humans grade each solution on two deliberately separated 0-10 scales:
*soundness* (is every step valid; does the argument establish the answer; ignore the writing) and
*style* (is it clear and well-organized; ignore correctness). Annotators see no model names and no
scores. The two-axis design is the instrument's core: with a single "quality" number, style-loading is
unmeasurable in principle.

**2. A divergence stratum, because random data cannot power the test.** On a uniformly random sample of
MATH-500 solutions, human soundness and style correlate at +0.82 and near-ceiling scores leave the
judge's grades 96% identical — no variance, no test. We therefore also grade a small set selected where
cheap signals disagree with the judge; on those items soundness and style decouple (correlation +0.31)
and the test has power. Selection inflates magnitudes, so this stratum answers only the *which-axis*
question, never population effect sizes; the random stratum provides those.

**3. Partial correlations as the verdict.** The judge's score is correlated with human soundness
holding style fixed, and with human style holding soundness fixed. A substance-reading judge shows the
first high and the second near zero. A style-loaded judge shows the reverse. We also require the
within-correct check: among solutions whose final answer is right, does the judge still separate sound
from lucky reasoning? This distinguishes a judge that reads the work from one that merely re-derives
the answer and matches endpoints.

**4. A shared block and a positive control.** Two annotators grade the same items, giving the
human-human ceiling that bounds any claim about the judge (ours: soundness 0.79, style 0.55 — the style
axis is noisier, so style-nulls are bounded by measurement precision and we report them as such, with
attenuation stated). And because a protocol that can only acquit is not a protocol, we certified a
deliberately sabotaged judge: the same frontier model, instructed to prioritize presentation over
correctness. The instrument convicted it — its style partial jumped to +0.56 (honest judge: +0.05 to
+0.12) while its soundness partial fell to +0.18 (honest: +0.47 to +0.56), on the same 60 human-labeled
items. The protocol detects style-loading when it is present and finds none when it is not.

## What certification found

**The frontier judge passed, decisively.** GPT-5.2 judging MATH-500 solutions: correlation with human
soundness +0.59 [+0.32, +0.77] on the random stratum (n=60); on the divergence stratum with two-rater
consensus, partial correlation with soundness holding style fixed **+0.86**, with style holding
soundness fixed **−0.06**. Both annotators independently show the pattern (+0.87 and +0.77). Within
correct-answer solutions only, where an endpoint-matcher would flatline, the judge still tracks
soundness at **+0.81**. A second frontier family (Claude Opus) grading the same items under the same
rubric agrees with human soundness at +0.53. This judge reads the work.

**The context that makes this worth reporting:** on the very same solutions, every reference-matching
metric we could construct — teacher-forced accuracy, gold-token probabilities, TF-IDF, word overlap,
sentence embeddings — correlates with human soundness between −0.24 and +0.14. The judge is not merely
"agreeing with itself"; it is the only cheap signal in the comparison that measures reasoning quality
at all, and the certification is what licenses saying so.

**The ladder discriminates, and the reference flips the verdict.** We ran the protocol down a ladder
of open-weights judges (Qwen 1.5B to 14B), each in two deployment conditions, with predictions
registered in an earlier draft before the results landed. Both held. Without a reference in context,
every judge on the ladder fails certification: the 1.5B judge is actively style-loaded (style partial
+0.33, soundness -0.05), and the 3B-14B judges are too weak to certify (rho +0.24 to +0.28 against
human soundness). With the gold reference in context, every judge from 1.5B up passes: the 1.5B flips
from style-loaded to valid (+0.40, style partial +0.08), and the 14B reaches +0.53 with partials
+0.50 / +0.07, within noise of the frontier judge. The reference does not merely raise detection
rates, as our earlier work showed; it changes what the judge measures, from style to substance. A
1.5B judge with a reference is a certifiable grader. A 14B judge without one is not.

**What certification does not claim.** One judge family passed on one math benchmark. That is the
point: validity is a property of a (judge, task, prompt) triple, not of "LLM judges." The protocol is
the contribution; our verdicts are worked examples.

## Why this matters beyond the verdict

Three uses fall out immediately. *Deployment gating:* certify before wiring a judge into a leaderboard
or filter; the cost is roughly 5-8 annotator-hours per triple. *Debugging the measurement stack:* in
our hands the protocol's failures were informative — apparent judge failures traced to benchmark
answer-key bugs (71-83% of flagged cases in a prior audit) and to range restriction on saturated data,
where 96% of judge scores are identical and no validity question can even be asked. A benchmark that
cannot power certification cannot power evaluation either, which converts "use harder items" from
advice into a measurable requirement. *A target for judge improvement:* once validity is a number,
interventions (references, forced solve-first, ensembling) can be evaluated on whether they raise it,
not just on agreement rates.

## Limitations

Current annotators include paper authors (an external annotator is in progress); the random-stratum
n is 60 toward a pre-stated 80; one domain has human grades (code certification uses executed tests
for soundness and pending human grades for style). The style axis is the noisier instrument
(inter-rater 0.55) and all style-nulls carry that bound. All registered predictions (sabotage, ladder, reference flip) are now confirmed; remaining pendings are the human-label completions above.

---
*Data, labeling instruments, and scripts: experiments/tfa-vs-judge (human_eval/, runs/cert_out/,
scripts/critic_panel.py, scripts/style_judge_control.py).*
