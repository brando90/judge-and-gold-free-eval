# Human labeling set: reasoning-trace quality

Purpose: get an external, human ground truth for **reasoning quality** (the axis the deterministic
answer-checker cannot see) on the traces where it matters most. The deterministic benchmark tells us
only whether the final answer is correct. It cannot tell a soundly-reasoned correct answer from a
luckily-correct one, and it is exactly the variable we condition out in the item-level analysis. So the
LLM judge is currently our only source of reasoning-quality scores, and this set validates that judge
against people.

## What is in the sample

42 traces (`traces_to_label.jsonl` / `.csv`), over-sampling the cells where a human tiebreak is decisive:

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

Open `label.html` in any browser (double-click, no server needed). For each trace you see the problem,
the reference solution, and the model trace to grade, then answer a short rubric (step validity,
completeness, overall quality 0 to 10, lucky-correct). Labels autosave to the browser and you can
`Download CSV` at any time.

Label **blind**: the TFA and judge scores and the cell label are hidden by default so they do not anchor
you. Toggle `reveal metric scores` only after you have formed a view, or for a researcher review pass.

## Fields

`traces_to_label.csv` columns: `order, id, dataset, model, cell, cell_desc, correct` (deterministic
final-answer correctness), `tfa` (teacher-forced accuracy), `judge` (gpt-5.2 reasoning score 0 to 10),
`gold_answer, question, gold_solution, trace`. Regenerate with `scripts/make_labeling_set.py`.

## Analysis after labeling

With human labels `h`, the questions are: does the LLM judge agree with humans (`ρ(judge, h)`), and does
TFA track human quality (`ρ(TFA, h)`), especially within the correct stratum. If the judge is faithful,
every judge-based number in the paper inherits external validity. If not, the judge-free framing gets
stronger and the item-level ground truth must be rebuilt on humans.
