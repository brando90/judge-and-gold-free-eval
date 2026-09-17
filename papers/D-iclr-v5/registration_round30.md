# Round 30 registration: the swap under a neutral prompt (R30-A) and a canonical reference (R30-B)

**REGISTERED 2026-09-16, before any R30 model call.**

The arms, pools, prompts, endpoints, predictions and caps below are fixed as written. The builder
(`experiments/tfa-vs-judge/scripts/r30_build_canonical_pools.py`) and the producer
(`papers/analysis/r30_analysis.py`) were committed at `2a9ad6a`, before this registration and before any
call. Both were checked against stored data only, in a temporary workspace that wrote nothing into the
repository, and the design facts that check revealed are disclosed under R30-B below. No outcome of any R30
model call has been computed at the time of this commit. Any estimate not specified here is post hoc and
carries a `†`.

Credentials were checked before registering, with a one-token call per key that used no R30 pool: the
project's original `ANTHROPIC_API_KEY` is out of budget until 2026-10-01, while `ANTHROPIC_API_KEY_1` and
`_2` work, and the runs below use `_1` at the authors' direction.

## Why these two

Two independent area-chair reviews of v5 name the same two evidence gaps, and both are answerable with
existing harnesses and existing pools.

1. **Every headline effect comes from a prompt that instructs comparison.** Our referenced rubric says to use
   the reference to check the candidate; the MT-Bench template asks for a comparison; the chain-of-thought,
   verify-first and solve-first prompts all tell the judge to use the reference. Only the direct prompt names
   the reference without saying what to do with it, and the swap has never been run under it. The paper
   currently concedes this in \S3 and \S5 without answering it. A reviewer can therefore still say the
   effect is prompt-following.
2. **The headline magnitude comes from a reference drawn at random.** Benchmark authors pick the salient or
   canonical answer, which models also tend to produce, so 30 to 67 points is nearer a worst case than a
   typical one. The paper never tests a canonical reference.

## Context disclosed before R30

All results through R27 are known. Relevant to these designs:

- Under the referenced rubric, the swap moves identical text by about 3 to 5 points (\S3).
- R22-B, the second reference draw under the rubric, moved credit with the reference for the three API
  graders: answers that stop matching go from 100%, 99.3% and 99.3% credited to 61.8%, 72.1% and 74.3%
  (Sonnet 5, Opus 5, Haiku 4.5), and answers that start matching from 64.4%, 76.2% and 68.4% to 99.4%, 99.4%
  and 97.7%, while pooled accuracy moved at most 3 points (`registration_round22.md`; `tab:r22-redraw`).
  318 of the 596 answers change match group between the two draws (verified against
  `runs/r22/redraw_pool.jsonl`).
- The same redraw under our rubric with **GPT-4.1** moves credit much less: answers that stop matching go
  from 100% to 87.5% (144 answers) and those that start matching from 80.5% to 99.4% (174), that is 12.5 and
  18.9 points against Sonnet 5's 38.2 and 35.0 (`tab:r24-gpt41`). The two judges of R30-A therefore have
  very different rubric baselines, and the prediction below is set per judge rather than on a shared bound.
- R23-A showed that credit shift is a draw effect, not call-to-call variation: under a same-reference
  regrade, match-changing answers keep their credit to within about 3 points.
- Under the direct prompt with the reference, credit for differing correct answers falls from 91.4% to 73.2%
  (GPT-4.1) and 96.5% to 83.3% (Sonnet 5) against blind (R26-A).
- R27-A: among correct answers credited blind, 22.4% (GPT-4.1) and 14.1% (Sonnet 5) lose credit once the
  reference is shown under the direct prompt, against 0.0% of matching answers.

Neither part changes an existing number; both add conditions to stored pools.

---

## R30-A: does the swap survive a prompt that never instructs comparison?

**Design.** The R22-B swap, re-run under the direct prompt instead of the rubric. Identical candidate text;
only which correct answer is named as the reference changes.

**Pool.** `runs/r22/redraw_pool.jsonl` (149 questions, 4 answers each, 596 answers). It already carries `ref`
(draw 2), `ref_draw1` (draw 1), and the match groups `group` and `group_draw1` for both.

**Builder.** None is needed, and the one an earlier draft of this document named is dropped. The draw-1
referenced arm already exists: `runs/r26/bench_direct_<judge>/scores.jsonl` was run on
`runs/r20/mace_gen/pool.jsonl`, whose `ref` is draw 1, and the redraw pool kept all 149 questions (no
question was dropped for want of an alternative answer), so the two arms cover the same questions and
answers and the producer joins them on `(problem_id, idx)`. Writing a draw-1 pool and re-running it would
spend money to reproduce rows we already hold, and would risk the two arms diverging.

**Judges and prompt.** GPT-4.1 (`gpt-4.1-2025-04-14`) and Claude Sonnet 5, with
`scripts/r26_judges.py --template direct --conds ref` at the R26 settings (no reasoning requested, 1,024
max tokens, OpenAI temperature 0, Anthropic thinking disabled). The direct prompt names the reference and
gives no instruction to use or compare with it; this is the only prompt we have with that property.

**What is already run, and what is new.** `runs/r26/bench_direct_<judge>/scores.jsonl` holds 596 `noref` and
596 `ref` rows per judge, and its `ref` rows were made on the draw-1 pool. They are the draw-1 arm and are
reused; the blind rows are reused as the baseline. Only the draw-2 arm is new: 596 calls per judge.

**Endpoints.** Among the 318 answers whose match group changes between draws:
- credit rate for answers that match under draw 1 but not draw 2, under each draw;
- credit rate for answers that match only under draw 2, under each draw;
- as a placebo, the same for answers matching neither reference.
Question-level bootstrap for each difference.

**Predictions.** For each judge:

- **P-R30A1.** Answers that stop matching when the reference moves are credited less under draw 2 than under
  draw 1 (interval excludes zero).
- **P-R30A2.** Answers that start matching are credited more under draw 2 than under draw 1 (interval
  excludes zero).
- **P-R30A3.** The credit shift under the direct prompt is smaller than that judge's own shift under our
  rubric, measured on the same answers and the same two draws (point prediction, each direction):
  below 38.2 points for answers that stop matching and below 35.0 for answers that start matching for
  Sonnet 5; below 12.5 and below 18.9 for GPT-4.1. A shared bound would be vacuous, since GPT-4.1's rubric
  shift is already smaller than Sonnet 5's by a factor of about three.
- **P-R30A4.** Answers that match neither reference change credit by at most 5 points between draws (point).

Reported without a prediction: each judge's accuracy against the answer lists under each draw, and the count
of answers in each match-change group.

**What it settles.** If P-R30A1 and P-R30A2 hold, the effect is not an artifact of telling the judge to
compare, and the paper can say so in the main text instead of conceding the objection. If they fail, the
instruction-following reading is largely right for this prompt and the paper must say that plainly and
narrow its claims to instructed graders. P-R30A3 separates the two readings quantitatively rather than
qualitatively: a large shrink is itself a reportable result.

---

## R30-B: how much of the shortfall is the random draw?

**Design.** The benchmark study re-run with the reference chosen rather than drawn.

**Pool and answer lists.** The 149-question benchmark pool (`runs/r20/mace_gen/pool.jsonl`), with the answer
lists in `runs/mace_tasks.jsonl` (`valid_answers`).

**Builder.** `scripts/r30_build_canonical_pools.py` writes two pools, recomputing match groups with the
MACE normalized-containment rule of `r20_build_leaderboard_pool.py`:

No blind calls are seeded, and an earlier draft of this document was wrong to say they would be. The shipped
SimpleQA and BrowseComp/HLE graders have no blind condition at all: `runs/r24/std_*/pool.jsonl` hold only
`ref` and `reflist` rows, and the HLE template is reference-only by construction. Blind rows exist only for
our own rubric. Nothing is lost, because this part's baseline is answer-list accuracy, which is the `oracle`
field of the pool rather than a blind grader run.

**Design facts disclosed before registering.** The builder was run on the stored pool to check it; it makes
no model call and produces no outcome, but it does reveal how much the two rules move the reference, so we
disclose it here rather than after the fact. Over the 149 questions: the first-listed rule changes the
reference for 106 questions and the match group of 217 of the 596 answers; the modal rule changes 112
references and 357 groups. Match counts order as the design intends, with the modal rule most favourable to
the grader: 419 matching answers against 205 under first-listed and 174 under the random draw, out of 540
correct answers. No question needed the modal rule's no-match fallback, so that branch is defensive and
untested on this pool.

- `runs/r30/canon_first_pool.jsonl` — **first-listed rule**: `ref := valid_answers[0]`. Exogenous: it uses
  MACE's own ordering and nothing about our models. In the full MACE multi-answer set the stored draw equals
  the first-listed answer in 69 of 225 tasks, so this differs from the current reference for most questions;
  the builder reports the count for the 149-question pool.
- `runs/r30/canon_modal_pool.jsonl` — **modal rule**: `ref :=` the listed answer produced by the most of the
  four answering models, matched by the same containment rule. Ties are broken by first-listed order.
  Questions where no model produces a listed answer fall back to first-listed and are counted and reported
  separately. This arm is deliberately the best case for the grader, since it maximises the chance that a
  model's answer matches the reference.

**Graders.** As shipped, exactly as in R24, with `scripts/r24_grader_pool.py --conds ref`:
the SimpleQA grader with GPT-4.1 (`--template simpleqa`), the BrowseComp/HLE judge with o3-mini
(`--template hle`), and our score rubric with Sonnet 5 (`--template rubric`).

**Endpoints.** Pooled accuracy minus answer-list accuracy under each rule, against the random draw's 30 to 67
points; and the share of correct answers differing from the reference that each grader credits, which under
the random draw is 0% to 53%.

**Predictions.** For each grader:

- **P-R30B1.** Under both rules the shortfall against the answer lists is smaller than under the random draw
  (interval excludes zero, each arm).
- **P-R30B2.** Under the modal rule the shortfall is still below zero: even a best-case reference leaves the
  graders under their answer-list accuracy (interval excludes zero).
- **P-R30B3.** The share of differing correct answers credited moves less between reference rules, in
  percentage points, than the accuracy shortfall does. This is the claim that the credited share is the
  portable statistic and belongs in the abstract ahead of the accuracy gap.

Reported without a prediction: how many questions change reference under each rule, and the modal arm's
fallback count.

**What it settles.** It converts "30 to 67 points" from a number a reviewer can dismiss as a property of our
draw into a bounded range with a stated best case. If P-R30B2 fails for a grader — that is, a canonical
reference removes the shortfall entirely — that is a material limitation and the abstract must be rescoped
to randomly drawn references.

---

## Verdict rule, caps, amendments

**Verdict rule.** The standing one (`app:ledger`): *confirmed* means the 95% interval excludes zero in the
predicted direction, or a registered point prediction holds; *not confirmed* means the interval includes
zero; *falsified* means the interval excludes zero in the opposite direction, or a point prediction fails.

**Spend caps**, to be fixed before the first call. R30-A: USD 6 (GPT-4.1) and USD 10 (Sonnet 5) for 596
short-output calls each. R30-B, covering both arms: USD 10 (SimpleQA with GPT-4.1), USD 12 (HLE with
o3-mini, which reasons), USD 15 (rubric with Sonnet 5). Record actual spend per cell.

**Amendments.** Any change after the first call of a part is recorded here as a dated amendment before that
part's results are analysed, as in rounds 22 and 27.

**Analysis.** One producer, `papers/analysis/r30_analysis.py`, with `--part a|b`, writing
`papers/analysis/r30a_<judge>.json` and `papers/analysis/r30b_<grader>_<arm>.json`. It must be committed with
this registration, before any call.

**Count.** 8 predictions in R30-A (4 per judge) and 9 in R30-B (3 per grader).
