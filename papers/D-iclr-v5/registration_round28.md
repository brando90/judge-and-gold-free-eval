# Round 28 registration DRAFT: agentic judges — does indirection remove the pull? (R28)

**STATUS: DRAFT. NOT REGISTERED. NO DATA GENERATED.**

This document is a specification only. It carries no registration weight and no prediction in it may be
cited in the paper. To register it: fix the arms, prompts, pools, and caps below, commit it together with
the harness and producer scripts and a timestamp, and only then make the first model call. Any estimate
produced before that commit is post hoc and must be marked `†`.

## Motivation

The masking suite (`app:mechanism`) already shows the effect largely vanishes when the reference is not
surface-comparable — written as an expression, or hidden inside a worked solution. That suggests the
mechanism is addressable by design rather than only by prompt wording. R28 asks whether giving the judge
*access* to the reference, without putting the string in its context, keeps the reference's benefit while
removing the pull. It also answers the standing reviewer question that v5's Limitations concedes: whether a
judge with tools anchors the way a single-call judge does.

Two things the "just use an agent" proposal conflates, which arms 1 and 2 separate:
* **Indirection** — the reference stops being a string available for surface comparison.
* **Verification ability** — the judge gains the means to check the answer itself.

## Arms

Same candidate answers throughout, same judges, so cells are directly comparable to the existing
single-call results.

| Arm | Reference exposure | Tools | Pools |
|---|---|---|---|
| 0 | Reference in prompt (existing baseline; no new calls) | none | replication, MACE subsample |
| 1 | Pointer only — retrievable by tool call, never pre-loaded into context | `get_reference()` | replication, MACE subsample |
| 2 | Membership oracle — may ask whether a candidate answer is on the list; never sees the list | `is_listed(answer) -> bool` | replication, MACE subsample |
| 3 | No reference at all; task constraint plus a Python tool | `run_python(code)` | replication (arithmetic only) |
| 4 | Differential testing (below) | `run_tests`, `get_gold_impl()` | new code pool |

**Arm 3** operationalizes the paper's own recipe item ("a checker exists — grade with it").

**Arm 4, differential testing.** Candidate implementation in context; gold implementation behind a pointer,
never shown as text. The agent generates inputs, runs both, and grades on behavioural equivalence only.
* *Swap analogue:* hold the candidate fixed, swap the gold to a semantically equivalent implementation
  using a different algorithm. A judge grading behaviour scores identically; a judge anchoring on style or
  route moves. This is the solution-route rotation with an executable reference.
* *Wrong-answer pool:* mutants of correct solutions (off-by-one, flipped comparison, dropped edge case),
  which give a real false-acceptance curve.
* *Required control — the underspecification trap:* reference-derived tests inherit the reference's
  behaviour on inputs the spec never pinned down, so a correct implementation that differs on an
  unspecified edge case will be failed. A spec-only arm (tests generated from the problem statement, no
  gold access) measures how much of arm 4's rejection is spec-legitimate. Without this arm, arm 4's
  false-rejection number is uninterpretable and must not be reported.

## Endpoints

**Primary.** The swap test, unchanged in form: candidate text byte-identical, move which correct answer the
pointer resolves to, measure the change in score. The single-call baseline moves 3 to 5 points for the
judges already reported (`sec:p1`).

**Required secondary endpoints. The swap must not be reported alone.**
1. False-rejection rate on correct answers that differ from the reference.
2. Grading AUROC of differing correct answers against wrong answers.
3. **False acceptances — non-negotiable.** Solve-first prompting already credited 17.3% and 25.9% of
   label-wrong answers on hard HLE questions for GPT-4.1 (`app:r27`), so any arm that reduces anchoring is
   scored on wrong answers too. Use the 40-task MACE subsample, which is wrong-answer rich.
4. Tool-call logs: how often the agent actually retrieved the reference, per arm and pool. An arm in which
   the agent rarely calls `get_reference()` is not a test of indirection but of blind judging.

## Predictions (to be fixed before the first call)

For each judge and pool, against that judge's own arm-0 cell:

* **P-R28-1.** Arm 1 (pointer) reduces the absolute swap change to at most 1.5 points.
* **P-R28-2.** Arm 1 does not reduce grading AUROC relative to arm 0.
* **P-R28-3.** Arm 1 does not raise false acceptance on the MACE subsample by more than 5 points over arm 0.
* **P-R28-4.** Arm 2 (membership oracle) reduces the absolute swap change at least as much as arm 1
  (indirection alone suffices; if arm 2 fails while arm 1 holds, the benefit came from verification ability,
  not indirection).
* **P-R28-5.** Arm 4's swap analogue moves the score by at most 1 point once the spec-only control is
  subtracted.

Reported without a prediction: per-arm tool-call counts, latency, and cost per judged answer.

## Verdict rule

The rule already in force (`app:ledger`): *confirmed* = 95% interval excludes zero in the predicted
direction, or a registered point prediction holds; *not confirmed* = interval includes zero; *falsified* =
interval excludes zero in the opposite direction, or a point prediction fails.

## Scoping and cost

Restrict to the 120 replication tasks, the 40-task MACE subsample, and a small code pool. Multi-turn tool
use on 64 candidates per task across all pools is not affordable; sample candidates per task as the API
judges already do. Set a USD cap per judge–arm cell before the first call and record spend per cell.

## Standing constraints

* Anthropic workspace limit — check availability before scheduling (it blocked generator work through
  2026-10-01 in another track).
* Run local models sequentially; two concurrent local HF models triggered a low-memory kill on the 16 GB Mac.
* Log every tool call to disk at call time, not at the end of the run.
