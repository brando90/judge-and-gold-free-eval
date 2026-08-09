# Human labeling set: reasoning-trace quality

Purpose: get an external, human ground truth for **reasoning quality** (the axis the deterministic
answer-checker cannot see) on the traces where it matters most. The deterministic benchmark tells us
only whether the final answer is correct. It cannot tell a soundly-reasoned correct answer from a
luckily-correct one, and it is exactly the variable we condition out in the item-level analysis. So the
LLM judge is currently our only source of reasoning-quality scores, and this set validates that judge
against people.

## What is in the sample

242 traces (`traces_to_label.jsonl` / `.csv`), in two strata:

**Stratum D (diagnostic, 42 traces, items 1-42).** Over-samples the cells where a human tiebreak is
decisive (table below). Use it to adjudicate who is right when TFA and the judge disagree. Because it is
selected ON disagreement, do not estimate correlations from it alone.

**Stratum R (random, 200 traces, items 43-242).** Drawn uniformly from the MATH-500 pool with no
selection on TFA, judge, or correctness. This is the stratum for the validity numbers: rho(TFA, human)
and rho(judge, human), unbiased. The first 40 R-items are the **shared block**: every labeler grades
these, which gives inter-rater agreement and the human-human ceiling the judge should be compared against.

**Rollout process value coverage.** All 200 random-stratum traces now have rollout-PV scores computed
with the uniform 14B completer (`runs/prm_labelset/`), so human grades on these items anchor TFA, the LLM
judge, AND the +0.43 process-value claim on the same traces. Analysis: `scripts/analyze_human_labels.py`.

**Labeling protocol.** Every labeler: (1) grade the 40 shared-block items (marked on the card), then
(2) grade whatever slice of the rest you were assigned. Partial returns are fine; labels key on the trace
`id`, so files from multiple people and multiple sessions merge cleanly.

**Reuse.** The original 42 diagnostic traces kept their exact `id`s and order positions, and both label
pages kept their storage keys, so labels already collected (in-browser progress or returned CSVs) remain
valid as-is.

The diagnostic cells:

| cell | selection | why it is informative |
|---|---|---|
| A | correct, high TFA, **low judge** | TFA says good, judge flags the reasoning: who is right? |
| B | correct, **low TFA**, high judge | TFA penalizes a valid but different-style solution |
| C | correct, low judge | lucky-correct? right answer, weak reasoning per the judge |
| D | correct, high TFA, high judge | both agree it is good (calibration anchor) |
| E | wrong, high judge | near-miss: wrong result, coherent reasoning |
| F | wrong, low judge | incoherent: wrong and unsound |

Cells A, B, C are the within-correct / disagreement region and make up 30 of the 42 items.

## How to label

Open `label.html` in any browser (double-click, no server needed). Math in the problem, reference, and
trace is rendered with MathJax; if you are offline the LaTeX shows as source, which is still readable.
For each trace you see the problem, the reference solution, and the model trace to grade, then answer a
short rubric (step validity, completeness, overall quality 0 to 10, lucky-correct). Labels autosave to
the browser and you can `Download CSV` or `Download JSON` at any time.

Each card shows its **cell** (for example, "lucky-correct? correct answer, low judge") along with the TFA
and judge scores, so you know what kind of case you are looking at. If you prefer to label without that
context, tick **blind mode** in the header to hide the cell and scores.

## Fields

`traces_to_label.csv` columns: `order, id, dataset, model, cell, cell_desc, correct` (deterministic
final-answer correctness), `tfa` (teacher-forced accuracy), `judge` (gpt-5.2 reasoning score 0 to 10),
`gold_answer, question, gold_solution, trace`. Regenerate the diagnostic stratum with `scripts/make_labeling_set.py`; extend/refresh the random stratum with `scripts/extend_labeling_set.py` (append-only, never touches existing ids).

## Shareable version (no repo needed)

Two self-contained, CDN-free copies are published as Artifacts:

- Original 42-trace diagnostic set (`label_artifact.html`):
  https://claude.ai/code/artifact/b50024f9-6198-4e9c-8520-0d13cb14faca
- Full 242-trace set with the random validity stratum (`label_artifact_v2.html`), use this one for
  new labeling:
  https://claude.ai/code/artifact/7e601e93-b797-470f-94dc-884621476437

Math is pre-rendered to native MathML, so it renders with no external libraries (works under the Artifact
content-security policy). It is private until you share it from the page's share menu. Rebuild it with
`scripts/build_label_artifact.py` after regenerating the sample.

## How the labels come back to you

Artifacts cannot post to a server, so collection is by file, not by submission:

1. Each labeler opens the link, enters their name/initials in the header, and grades the traces. Progress
   autosaves in their own browser.
2. When done (or partway), they click **Download CSV** (or JSON) and send you the file.
3. You concatenate the returned CSVs. Every row carries `labeler` and the trace `id`, so multiple people
   and multiple passes deduplicate cleanly. The `machine_correct`, `tfa`, and `judge` columns are carried
   through for the analysis below.

If you would rather collect automatically, the alternative is to give labelers the CSV file and have them
fill it in a shared spreadsheet, but the download-and-send flow above needs no setup.

## Analysis after labeling

With human labels `h`, the questions are: does the LLM judge agree with humans (`ρ(judge, h)`), and does
TFA track human quality (`ρ(TFA, h)`), especially within the correct stratum. If the judge is faithful,
every judge-based number in the paper inherits external validity. If not, the judge-free framing gets
stronger and the item-level ground truth must be rebuilt on humans.


## Active labeling (phase 2, blind, soundness+style rubric)

Two per-author artifacts on the random MATH-500 stratum (blind by default; grade soundness and style on
independent 0-10 scales):
- Author 1 (20 shared items): https://claude.ai/code/artifact/433e4f1f-3a34-4f9e-a70f-e07c054a7ba6
- Author 2 (80 items, first 20 shared with author 1): https://claude.ai/code/artifact/ad2372eb-d9d4-451b-a05a-90365165d086

The 20 shared items give the inter-rater ceiling and let us disattenuate; author 2's extra 60 grow the
validity n to ~80. Rebuild subsets with BLIND_DEFAULT=1 and an order-range filter over traces_to_label.jsonl.
