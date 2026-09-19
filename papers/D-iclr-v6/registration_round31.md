# Round 31 registration — the counter-instructed swap

Registered before any model call. Committed at the timestamp of this commit; no R31 call had been made when
it was written, and the harness change it depends on (`scripts/r26_judges.py`, template `counter`) is in the
same commit.

## Why this experiment

Every headline swap number in the paper comes from a prompt that tells the judge to use or compare with the
reference. Round 30 narrowed that objection but did not close it: its `direct` prompt *names* the reference
and gives no instruction about it, which shows the effect does not need an instruction to compare. It does
not show what happens when the judge is instructed **against** using the reference. That is the remaining
form of the instruction-following reading, and it is the one a reviewer will raise.

## Design

The R22-B swap again, under a prompt that explicitly forbids using the reference. Identical candidate text;
only which correct answer is named as the reference changes between the two arms.

**Prompt.** New template `counter` in `scripts/r26_judges.py`, byte-identical to `("direct", "ref")` except
for one inserted sentence:

> The reference answer is only one of several correct answers. Do not compare the response to it, and do not
> treat agreeing or disagreeing with it as evidence; judge only whether the response is itself a correct
> answer to the question.

Everything else — question/reference/response layout, "Do not explain", the `correct: yes|no` tail, 1,024 max
tokens, OpenAI temperature 0, Anthropic thinking disabled — is unchanged from R26/R30. Any difference from
the direct arm is therefore attributable to the instruction rather than to rewording.

**Pools.** Both arms are new; unlike R30-A there is no existing run to reuse, because this template has never
been run.
- draw 1: `runs/r20/mace_gen/pool.jsonl` (149 questions, 596 answers; its `ref` is draw 1).
- draw 2: `runs/r22/redraw_pool.jsonl` (the same 149 questions and answers; its `ref` is draw 2, and it
  carries the match groups `group_draw1` and `group` for both draws).

Confirmed before registering that the two pools agree on draw identity: for `mace/language-k2-0` the draw-1
pool's `ref` is `Brazil` and the redraw pool's `ref_draw1` is `Brazil`, with `ref` = `Indonesia`.

**Judges.** GPT-4.1 (`gpt-4.1-2025-04-14`) and Claude Sonnet 5, `--conds ref`, at the R26 settings.

**Runs.** Four cells of 596 calls: `runs/r31/{draw1,draw2}_{gpt41,sonnet}`. Cost basis from the R30 cells of
the same size and template: USD 0.153 (GPT-4.1) and 0.382 (Sonnet 5) per 596 calls, so about USD 1.10 in
total. `--cap-usd 2` per cell. Record actual spend per cell in `runs/r31/*/spend.json`.

**Scoring.** `papers/analysis/r30_analysis.py --part a`, unchanged, joining the arms on `(problem_id, idx)`
and taking the match-change classes from the redraw pool's own `group_draw1`/`group`, restricted to correct
answers: `stop` (match under draw 1, not draw 2), `start` (not under draw 1, match under draw 2), `neither`
(nonmatch under both, the placebo). Credited = score ≥ 7. Question bootstrap, 2,000 resamples, seed 0.

## Endpoints

Among the answers whose match group changes between draws, for each judge: the credited share of each class
under each draw, and the shift, with intervals. Reported without a prediction: each judge's accuracy against
the answer lists under each draw, the count in each class, and the number of replies with no parseable grade.

## Predictions

For each judge:

- **P-R31A1.** Answers that stop matching when the reference moves are credited less under draw 2 than under
  draw 1 (interval excludes zero).
- **P-R31A2.** Answers that start matching are credited more under draw 2 than under draw 1 (interval
  excludes zero).
- **P-R31A3.** The counter-instructed shift is smaller in magnitude than that judge's own shift under the
  `direct` prompt, measured on the same answers and the same two draws (point prediction, each direction).
  Per judge, from R30-A: below 26.4 points for `stop` and below 24.7 for `start` for GPT-4.1; below 13.2 and
  below 17.8 for Sonnet 5. Stated per judge because a shared bound would be vacuous for Sonnet 5.
- **P-R31A4.** Answers that match neither reference change credit by at most 5 points between draws (point).

## Verdict rule

The project rule, unchanged. *Confirmed*: the 95% interval excludes zero in the predicted direction, or a
registered point prediction holds. *Not confirmed*: the interval includes zero. *Falsified*: the interval
excludes zero in the opposite direction, or a point prediction fails.

## What it settles, in both directions

If P-R31A1 and P-R31A2 hold, the anchoring survives an explicit instruction not to use the reference, and the
instruction-following reading is dead in every form we can test: the paper can say so in Section 3 rather
than bounding the objection.

If they fail — if the swap largely disappears under counter-instruction — then the effect is substantially a
response to what the prompt asks, and Section 3's claim that it "is not an artifact of our own wording" is
too strong. In that case the paper must say so plainly in the main text, narrow the claim to prompts that do
not forbid reference use, and report this cell as a falsification alongside the others in the ledger. That
outcome is registered here as an expected possibility, not a reason to withhold the result.

P-R31A3 is the quantitative middle: a shift that survives but shrinks is itself the reportable finding, and
its size bounds how much of the effect the instruction contributes.

## Outcome

Run 2026-09-17 after this document was committed (`b72dc8a`, 10:10:00 −07:00). Four cells, 596 calls each,
**0 errors and 0 ungraded replies**. Spend USD 1.43 (Sonnet 5 0.507 + 0.503; GPT-4.1 0.208 + 0.208), inside
the USD 2 per-cell cap. Class counts match R30-A exactly: stop 144, start 174, neither 222, invalid 56.
Scored with `papers/analysis/r30_analysis.py --part a`, unchanged; outputs `papers/analysis/r31a_*.json`.
Every share was re-derived independently of the producer, without the bootstrap, and agrees to four decimals.

**The swap essentially disappears under counter-instruction.**

| Judge | class | draw 1 | draw 2 | shift (95% CI) | same class, `direct` prompt (R30-A) |
|---|---|---|---|---|---|
| Sonnet 5 | stop | 0.986 | 0.979 | $-0.007$ [$-0.031$, $+0.015$] | $-0.132$ |
| Sonnet 5 | start | 0.977 | 0.989 | $+0.012$ [$-0.011$, $+0.034$] | $+0.178$ |
| Sonnet 5 | neither | 0.968 | 0.946 | $-0.023$ [$-0.050$, $+0.004$] | $-0.059$ |
| GPT-4.1 | stop | 0.993 | 0.972 | $-0.021$ [$-0.051$, $+0.007$] | $-0.264$ |
| GPT-4.1 | start | 0.977 | 0.977 | $+0.000$ [$-0.016$, $+0.018$] | $+0.247$ |
| GPT-4.1 | neither | 0.968 | 0.968 | $+0.000$ [$-0.012$, $+0.013$] | $-0.032$ |

**Verdicts (8 predictions: 4 confirmed, 4 not confirmed, 0 falsified).**

- **P-R31A1** (stop-matching credited less under draw 2): **not confirmed** for both judges. Both intervals
  include zero ($-0.007$ [$-0.031$, $+0.015$] and $-0.021$ [$-0.051$, $+0.007$]).
- **P-R31A2** (start-matching credited more under draw 2): **not confirmed** for both judges. Both intervals
  include zero ($+0.012$ [$-0.011$, $+0.034$] and $+0.000$ [$-0.016$, $+0.018$]).
- **P-R31A3** (counter shift smaller than that judge's own `direct` shift): **confirmed** for both judges in
  both directions, by a wide margin. GPT-4.1 2.1 and 0.0 points against bounds of 26.4 and 24.7; Sonnet 5
  0.7 and 1.2 against 13.2 and 17.8.
- **P-R31A4** (placebo moves at most 5 points): **confirmed** for both judges (2.3 and 0.0 points).

**The judges did not simply become permissive, which is the reading this result had to survive.** Wrong
answers are still rejected, and correct-answer credit rises sharply against the `direct` prompt on the same
pool:

| Judge | prompt | correct credited | wrong credited |
|---|---|---|---|
| Sonnet 5 | direct | 0.878 | 0.107 |
| Sonnet 5 | counter (draw 1 / 2) | 0.976 / 0.969 | 0.107 / 0.125 |
| GPT-4.1 | direct | 0.800 | 0.071 |
| GPT-4.1 | counter (draw 1 / 2) | 0.978 / 0.972 | 0.196 / 0.214 |

Reported without a prediction: accuracy against the answer lists is within **0.2 to 1.7 points** under every
cell (Sonnet 5 $-0.012$/$-0.017$, GPT-4.1 $-0.002$/$-0.005$), against the 30 to 67 points by which the
shipped benchmark graders fall short.

**What this settles, read against what was registered.**

The registered failure branch applies in part and must be stated plainly: the swap *is* removable by an
instruction, so the anchoring is sensitive to what the prompt asks. But it does not make the effect an
artifact of our wording, and Section 3's claim is not withdrawn, because R30-A already showed the swap is
large under a prompt that names the reference and gives **no** instruction about it ($-0.264$/$+0.247$ for
GPT-4.1). The two results are complementary and the pair is a stronger statement than either alone:

- the effect does **not require** an instruction to compare (R30-A), so it is not manufactured by our rubric;
- it **is eliminated** by an explicit instruction not to compare (R31), so it is not an immovable property of
  the judge either.

The practical finding belongs in Section 7. Telling the judge that the reference is one of several correct
answers and not to compare against it closes almost the whole accuracy gap, at a cost that differs by judge:
nearly free for Sonnet 5 (wrong-answer acceptance 0.107 → 0.107/0.125) and real for GPT-4.1 (0.071 →
0.196/0.214). That mirrors, and strengthens, the existing correctness-prompt result, which already warns that
one of two judges then accepts wrong answers.

Ledger: 321 → 329 registered predictions.
