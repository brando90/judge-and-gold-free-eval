# Watching the watchers: when do AI judges actually fail?

*A study of scalable oversight with planted errors, a ladder of judges, and an
audit trail. Companion deck with all figures: paper/oversight_slides.html.
Method diagram: paper/figs_oversight/f0_method.png. Full experiment log:
docs/oversight-log.md.*

## The question

Modern AI produces work faster than anyone can check it. The standard answer is
to have another AI act as a judge, which only moves the problem: who checks the
judge? The field calls this scalable oversight, and its working assumption is
that judges become unreliable as the systems they grade grow stronger.

We set out to measure exactly when and why AI judges fail. Two design choices
did most of the work. First, a ladder of judges, from a 0.5B model up through
1.5B, 3B, 7B, and 14B to GPT-5.2 and Claude Opus, all grading the same solutions
under the same instructions, later replicated across six model families.
Second, planted errors: rather than trusting any benchmark's answer key, we took
solutions known to be correct and broke them ourselves, then verified every
break mechanically. In math, a hidden error carries a wrong value consistently
through every later step, so the solution reads smoothly and ends wrong; a
checker confirms every stated equation is arithmetically true and the final
answer is not the real one. In code, we mutated correct programs and kept only
mutants that run cleanly but fail the official tests. When you plant the error
yourself, "did the judge catch it" has a definite answer.

## Part 1. Most measured judge failure is not judge failure

Three times, our own data produced an exciting oversight law, and three times it
dissolved when we checked every underlying case.

The most seductive example: count how many small judges a wrong solution fools,
and you appear to predict frontier-judge failure almost perfectly, from 1% (no
small judges fooled) to 94% (all three fooled). A cheap early-warning system for
frontier mistakes. Except that when we adjudicated all 55 top-bucket cases with
two frontier models under a solve-first protocol (they agreed 55 out of 55), 71%
of the "fooling" solutions were correct answers that the benchmark had marked
wrong. Among the genuinely wrong ones, the frontier judge failed 6%, barely
above its 2% baseline. The same autopsy killed an "attractor errors fool
judges" effect (83% scorer bugs) and a capability-gap degradation trend (a
difficulty confound).

Two conclusions, both verified beyond our own pipeline:

1. In our GSM8K scoring, 4.1% of correctness labels were simply wrong, and
   fixing them raised the measured quality of a frontier judge from 0.66 to
   0.75. Benchmarks measure the oracle as much as the judge.
2. The wreckage contains a tool. When several cheap open models unanimously
   produce the same "wrong" answer, the grading oracle is usually what is
   broken. Checked against GSM8K-Platinum, a human-curated re-annotation, with
   no frontier model involved: 66 of 74 flags (89%) were genuine grading
   problems, and the breakdown matters: 60 were our own scorer misparsing
   correct answers (the dataset key was fine), 4 were items Platinum removed as
   broken, and 2 were keys Platinum re-labeled to the models' answer. An
   unsupervised grading-pipeline debugger that costs pennies, and a reminder
   that the oracle a judge is scored against is the key AND the scorer.

With labels cleaned, judge skill on natural errors is a smooth curve:
discrimination AUC 0.78, 0.90, 0.92, 0.96, 0.96, 0.97, 0.99 up the ladder. No
cliff, no magic size. One more self-caught artifact belongs here: at a score
cutoff of 7, the 7B judge looked identical to the frontier; at a cutoff of 5 the
gap was 74% versus 10%. Thresholds can manufacture equivalences.

## Part 2. Judges read stories; they do not check lines

Planting a single false equation in an otherwise correct solution reveals what
judges actually do. Between 40 and 50 percent of explicit false statements
produce no meaningful score change, and 69 to 85 percent of such solutions still
clear a typical deployment bar. Where the typo sits matters, and it matters
differently by scale: mid-size judges punish blatant, early corruptions most
(local salience), while frontier judges forgive obvious typos and punish quiet,
late corruptions that touch the conclusion (global consequence). Frontier
judges are outcome graders, not proofreaders. Anyone using raw judge scores as
step-level process rewards should treat this as a warning.

## Part 3. The reference mechanism

The central experiment of the study shows three curves (deck, figure "the
mechanism"). Detection of fully propagated hidden errors:

| judge | no reference | correct reference shown | own answer as reference |
|---|---:|---:|---:|
| 1.5B | 3% | 21% | 59% |
| 3B | 17% | 85% | 60% |
| 7B | 49% | 85% | 85% |
| 14B | 75% | 90% | 95% |
| frontier | 98-100% | 100% | not needed |

Without a reference, small judges are nearly blind and skill climbs slowly.
With a correct reference, a 3B judge catches 85% of hidden errors. The
reference is worth +68 points at 3B and +2 at the frontier. Verification
decomposes into two parts: obtaining a reference, which is capability-bound,
and comparing against it, which is cheap enough for very small models.

Three details earned their place the hard way:

- Simply prompting a small judge to "solve it first, then judge" makes things
  worse (7B: 28% versus 49% direct). Generation dumps show why: the model
  silently skips the solving step. Small models fail instructions quietly.
- Forcing the two stages mechanically, generate an answer in one pass, then
  judge with it shown as a reference, produces the third column above.
- At 1.5B the judge does better with its own scruffy answer (59%) than with the
  official gold solution (21%). A reference in the judge's own style beats a
  polished one in someone else's. Reference style, not just
  reference correctness, is a first-order variable.

We must also report our own failure. The first version of the third column came
out exactly equal to the second, 100% recovery everywhere. It was a silent
dispatch bug: the "solve first" arm had run the with-reference condition twice,
and 128 of 128 scores were identical. We retracted the claim in the log, fixed
and verified the pipeline, and reran everything. Six of our own results died by
our own checks during this campaign.

Generality: the reference boost appears in all six families tried (Qwen,
Microsoft phi-4 at +26 points, Mistral +15, AI2 OLMo +60, Meta Llama +14,
Google Gemma +24), with family mattering more than parameter count. On
ProcessBench, a public benchmark with human-annotated first-error labels, the
same capability story appears (F1 of 0, 0, 37, 30, 63 up the ladder, 88 for
Opus; the dip at 7B is its documented credulity mode, answering "no error"
almost everywhere, which solve-first partially repairs), and the forced
solve-first protocol adds 7 to 8 F1 points once the judge is large enough to
comply.

## Part 4. Hard-to-verify domains, where the lever flips

Everything above had a safety net: math has answers, code has tests. Scalable
oversight is hardest where the net is gone. Using RewardBench-2, whose subsets
range from fully checkable math to questions with many valid answers, we ran
the ladder over 460 prompts, every better-versus-worse pair judged in both
presentation orders, under three conditions: no reference, the judge's own
generated answer as reference, and, as the decisive control, another model's
answer as reference.

Two free observations first. The rate at which a verdict flips when you swap
the order of the two candidates is a ground-truth-free stress meter: it falls
from near coin-flip at 0.5B (71 to 95%) to 2 to 24% at 14B, except on precise
instruction-checking, where every judge on the ladder stays near chance (46 to
60% flips), the pairwise version of the proofreading blind spot. No reference
of any kind fixes that subset.

Then the finding (judge: 14B; McNemar tests on paired items):

| condition | Math accuracy | many-valid-answers accuracy |
|---|---:|---:|
| no reference | 75% | 99% |
| own answer as reference | 84% (p=.006) | 91% (p<.0001) |
| weak model's answer | 73% | 92% (p=.0005) |
| decent model's answer | 82% | 92% (p=.0002) |

On single-answer content, references help in proportion to their quality, and a
bad one is merely useless. On these plural items, which are hard for every judge
on our ladder to verify independently, every reference hurts, by about the same
amount regardless of source or quality, and order-instability jumps (2% to
9-17% flips); the replication below shows this harm requires the
hard-to-verify condition, not plurality alone. The control settles the mechanism: this is not the
judge preferring its own words, since other models' references hurt equally. A
single reference anchors the judge on one valid answer and makes it punish
other perfectly valid ones. We audited the closest prior work
(arXiv:2509.19880, which proposed generate-then-judge and reports only
gains) page by page: it tests only single-answer tasks, pointwise, with no
other-model control and no order metrics. The sign flip is new.

The dividing line for oversight is therefore not objective versus subjective.
It is one right answer versus many valid answers that the judge cannot
independently verify. The next section shows both conditions are necessary.

## A minimal model of why the lever flips

The dissociation follows from one assumption backed by our data: a judge given a
reference acts substantially as a similarity comparator (it favors the candidate
closer to the reference), while a judge without one verifies independently with
some success probability that grows with capability.

Let a task have a set V of valid answers, |V| = k. The judge sees candidates c1
(valid) and c2 (invalid), and, in the reference condition, a reference r that is
itself a valid answer. Suppose that with probability q the judge verifies
independently (and then judges correctly), and otherwise falls back on
similarity to r, picking whichever candidate matches r more closely. Assume
distinct valid answers are mutually dissimilar, which holds by construction in
our plurality tasks and approximately in RewardBench-2 Ties.

Single answer (k = 1): any valid reference agrees with the valid candidate, so
the similarity fallback also answers correctly. Accuracy with reference is
q + (1 - q) * P(r is valid), which increases with reference quality and never
falls below the no-reference accuracy q0 when P(r is valid) is high. This is
the Math column: help proportional to reference quality, a useless reference
approximately neutral.

Many answers (k > 1): a valid reference r now differs from the valid candidate
in roughly (k-1)/k of pairings, and in those cases the similarity fallback finds
the valid candidate no closer to r than the invalid one, so it adds noise or
actively prefers a near-miss that mimics r. Accuracy with reference is at most
q + (1 - q)/k + epsilon, and the reference HURTS whenever the judge's
independent accuracy without the distraction, q0, exceeds that quantity, i.e.
whenever q0 - q > (1 - q)/k. Since providing a reference also suppresses
independent verification (the judge defers to the comparator, our order-flip
rates rise when the reference is added), q < q0 in practice, and the harm grows
with k. This is the Ties column, and it predicts the harm is independent of
reference quality and source, which is what the other-model controls found.

The model makes a further testable prediction: on plurality tasks whose
validity is trivially checkable, judges strong enough to keep verifying should
show no harm from a valid-but-different reference, while judges below the
verification floor should still be hurt. We built exactly that instrument
(synthetic many-valid-answer questions, validity checked by code, reference a
different valid answer, single-answer twins as controls) and the prediction
held on all five judges tested: no harm at 3B and above on the easy plural
checks (deltas 0 to +3, not significant) with the single-answer side showing
the full reference benefit (+32 to +39 points, p < 1e-4), and the harm
reappearing at 1.5B (-13 to -14, order-flips rising to 95%), a single rung on
one instrument, consistent with, though not by itself proof of, a verification
floor. The final form of the law is therefore
two-conditional: a reference degrades judging when valid answers are plural AND
verification is hard relative to the judge. RewardBench-2's factuality-flavored
plural items sit in that regime for every judge on our ladder, which is why all
of them were hurt there; and the hard cases of scalable oversight sit in that
regime by definition.

## The rules this buys

For measurement: audit the answer key before the judge (cheap-model consensus
finds oracle bugs at 89% precision against an external human-curated check,
unsupervised); never trust a single
score threshold; and ask every pairwise question twice with the order swapped,
since the flip rate is a free reliability meter that needs no labels.

For deployment: where a task has one right answer, provide a reference, and if
none exists, have the judge generate one in a separate forced step, never via a
single "solve first" prompt. Where a task has many valid answers AND the judge
cannot cheaply verify validity itself, withhold references; in that regime any
single reference, of any quality, biases the judge against valid alternatives
(when validity is easy for the judge to check, references are safe). And where the task is precise constraint-checking,
do not use a judge at all; use a programmatic checker, because no judge on our
ladder does this reliably, references or not.

These rules compose into a simple adaptive protocol: classify each prompt
(one right answer or many valid ones) with a cheap pass, then attach a
reference only in the single-answer case. On RewardBench-2 with a 14B judge
this router captures the math reference gain and most of the plurality harm
avoidance at once. Its pooled edge over the best fixed policy (78 versus 77
percent) is within our noise band and is not claimed as a gain; the point is
that a single policy no longer has to sacrifice one regime for the other, and
oracle routing shows six points of headroom. Its known failure is that answer
multiplicity is the wrong routing key for open-ended instruction tasks (it
misroutes the Focus subset), where the better key, per the boundary condition
above, is whether the judge can verify the content itself.

## Methods notes for the skeptical reader

Four choices deserve explicit defense. The 0-10 rubric was held fixed across
every judge and arm so no comparison mixes rubrics; score cutoffs (5 and 7)
appear only in threshold-sensitivity checks, and every headline claim uses
threshold-free statistics (AUC, paired McNemar), precisely because we caught a
cutoff manufacturing a fake equivalence. Each table cell is a single
deterministic run (temperature 0); paired designs and item-level tests carry
the inference, and effects below about six points are treated as noise
throughout. Prompt sensitivity was probed only where it became load-bearing
(the solve-first compliance failure); a systematic prompt ablation is future
work. Finally, RewardBench-2 Ties earns the label "many valid answers" by
construction: each Ties prompt admits an enumerated set of equally correct
answers, and the judged pair shows one valid against one invalid; validity is
factual, which is exactly why it is hard for mid-size judges to verify and why
it sits in the harmful regime of the two-condition law.

## Honest limits

The adjudications rest on two frontier families plus one human-curated external
check, not on fresh human labels. The verification-generation coupling at the
item level remains open (weak positive coupling, small bins). The
many-valid-answer result is one benchmark and should be replicated on a second
plurality-style dataset and with frontier judges. Agent-trajectory oversight was
deliberately deferred to existing safety benchmarks. Effect sizes below about
six points in the pairwise tables are within noise and are not claimed.

## Provenance

Thirteen findings, four independent critic passes (two design, two
adversarial), one public retraction with a verified correction, all headline
numbers re-derived from raw files by fresh code, planted code errors re-executed
against official tests, and a complete chronological audit trail in
docs/oversight-log.md. Roughly one day of five cluster GPUs, two frontier
judges, and $28 of API spend.
