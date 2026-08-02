# Step 1 result: the yardstick certifies an evaluator without trusting it

**The step.** Reliable judges without ground truth needs a gate: with little
ground truth, how do you tell a good judge from a bad one? The proposed answer is
a nuisance fraction, computed as a mechanism, not a trained metric. This is the
first run of it, on real LLM judges.

**Method.** For each dataset and judge we take every item-level score and split
its variance into two parts: how much is explained by ground-truth correctness
(the quality signal we want a judge to track), and how much is explained by
surface features of the response (length, line count, LaTeX density, presence of
a boxed answer) that a good judge should ignore. The sharpest number is measured
among already-correct answers, where correctness is constant, so any remaining
spread is quality or surface. We run it on two LLM judges (GPT-5.2, Opus 4.8) and
on TFA for comparison, on the Qwen ladder over MATH-500, GSM8K, and Putnam.
Correctness is the authoritative `cc` field, joined by (model, problem_id) from
the scores files; every judged record matched an anchor.

Code: `scripts/judge_nuisance.py` (numbers, `runs/judge_nuisance.json`) and
`scripts/make_step1_fig.py` (`paper/figs/fig_step1_yardstick.png`).

## What it found

The certificate has two axes: quality signal (variance explained by correctness,
higher is better) and surface nuisance among correct answers (lower is better). A
trustworthy evaluator sits high-quality and low-surface.

| dataset | evaluator | quality signal | surface nuisance (within correct) |
|---|---|---:|---:|
| MATH-500 | judge GPT-5.2 | 86% | 1.8% |
| MATH-500 | judge Opus | 85% | 4.5% |
| MATH-500 | TFA | 0% | 11.2% |
| GSM8K | judge GPT-5.2 | 73% | 0.3% |
| GSM8K | judge Opus | 74% | 11.3% (9.9% is length) |
| GSM8K | TFA | 1% | 1.8% |
| Putnam | judge GPT-5.2 | 36% | 7.7% |
| Putnam | judge Opus | 29% | 4.9% |
| Putnam | TFA | 1% | 13.3% |

Reading:

- **The yardstick separates a real evaluator from a surface one.** The LLM judges
  track correctness (29 to 86%); TFA tracks it essentially not at all (0 to 1.4%),
  and the variance TFA does have is surface. So the certificate correctly places
  the judges as trustworthy and TFA as not, using only the correctness anchor plus
  surface features. Note that a low surface number alone is not a pass: TFA on
  GSM8K has low surface (1.8%) only because it has almost no signal to begin with.
  The certificate is the pair, quality high and surface low.

- **It flags a specific, actionable judge failure.** Among correct GSM8K answers,
  the Opus judge's score is 11.3% surface and almost all of that is length (9.9%):
  Opus over-rewards longer correct answers. GPT-5.2 on the same data is length-free
  (0.0%). That is exactly the pre-deployment warning Step 1 promises, and it is
  invisible to headline accuracy.

- **It tracks difficulty.** On hard Putnam the judges' quality signal drops to 29
  to 36% and their surface nuisance rises, so the yardstick says a cheap judge is
  less trustworthy there, before any downstream use.

## What this validates, and what it does not

- It validates the **gate** of the program: a mechanism-based nuisance fraction is
  computable on real judges and it ranks evaluators and flags concrete failures.
- We measured it where we **have** ground truth so we could check it. The point is
  that it needs only a small correctness anchor, so it should transfer to
  low-ground-truth domains; showing it is stable under subsampling to a small
  anchor is the immediate next check.
- Scope of this run: the within-family Qwen ladder and two judges. Cross-family
  judges, more surface features (position, self-preference), and the
  small-n Putnam within-correct cell (about 120 answers) are open.
- This is Step 1 only. It does not yet test survival under a widening capability
  gap (Step 2) or under optimization (Step 3); the nuisance fraction measured here
  is the quantity those steps predict from.
