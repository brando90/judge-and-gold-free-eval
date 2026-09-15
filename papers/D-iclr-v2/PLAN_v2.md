# Version 2 plan: "The Reference Is Not an Answer Key"

Started 2026-09-14 from v1 (tag `paper-d-iclr-v1`, commit 9816adf; frozen PDF in `papers/D-iclr/`).
v2 lives in `papers/D-iclr-v2/`; v1 is not edited again.

## What v2 must add (user request, 2026-09-14)

1. **Why it matters: is reference-guided judging the standard?** Show which benchmarks, evaluation libraries, and RL reward
   pipelines grade answers with an LLM judge given one reference, what their prompts say, and how common multi-answer
   questions are in the data they grade.
2. **How to fix it.** A section that tells practitioners what to do, backed by experiments rather than advice.
3. Carry over the v1 abstract change ("does not reliably mean the answer is wrong").

## Workstreams

### W1. Practice survey (web research, verified against primary sources)
- Benchmarks whose official scorer is a reference-guided LLM judge (SimpleQA, BrowseComp, HLE, MT-Bench, FreshQA, CRAG, MixEval,
  Omni-MATH, ...); evaluation libraries and platforms (Inspect AI, OpenAI Evals, LangChain, LlamaIndex, RAGAS, DeepEval, MLflow,
  promptfoo, Phoenix, Vertex, Azure, Bedrock, OpenAI graders/RFT); RL verifiers (DeepSeek-R1, Kimi k1.5, General-Reasoner,
  xVerify, CompassVerifier, Seed1.5-Thinking, ...); surveys that quantify LLM-judge use.
- Per entry: source URL, default judge, what the reference is called, verbatim lines on answers that differ from it, whether
  the prompt allows several valid answers.
- Output: `survey/practice_survey.{md,json}`, `survey/prompts/*.txt`, `survey/new_refs.bib`. A second agent re-verifies quotes.
- Already verified by hand: the SimpleQA grader ("A factual statement in the answer contradicts the gold target" -> INCORRECT)
  and the HLE / BrowseComp judge ("based on the precise and unambiguous [correct_answer] ... do not argue for any answer
  different than [correct_answer], focus only on whether the answers match"; HLE's official judge is o3-mini-2025-01-31).

### W2. Prevalence of multi-answer questions in data graded this way
- Extend the v1 audit (MATH-500, GSM8K, DeepScaleR, NQ-open) to benchmarks that ship a reference-guided grader and to RL data
  graded by an LLM verifier: SimpleQA, BrowseComp, HLE (exact-answer, text-only), TriviaQA, WebInstruct-verified.
- Fix v1's limitation (one model family): two annotators from different developers (Claude Sonnet 5, GPT-5-mini), Opus 5
  adjudicates disagreements; report both-annotator and either-annotator bounds; relabel the v1 items with the second family.
- Protocol committed before labeling. Output: `papers/analysis/prevalence_v2/`.

### W3. Registered experiments (round 24)
- **R24-A, standard benchmark graders.** The verbatim SimpleQA grader and HLE/BrowseComp judge, each with its official judge
  model (GPT-4.1 for SimpleQA as configured in simple-evals; o3-mini for HLE) and with Claude Sonnet 5, grade the 596
  benchmark answers (149 MACE questions, four models). Gold target = one drawn reference, or the full answer list stated as
  "any one of these". Prediction: one reference under-counts; the full list closes the gap without accepting more wrong answers.
- **R24-B, a non-Anthropic grader with the paper's rubric.** GPT-4.1 grades the benchmark pool blind, with the first draw,
  and with the second draw (shortfall; credit shift for answers whose match changes).
- **R24-C, the answer-key fix on grading.** Sonnet 5, Opus 5, and GPT-4.1 grade the R8-A MACE subsample (correct and wrong
  answers) with the full answer list; grading AUROC and false rejections against blind and single-reference grading.
- **R24-D, prompt-only fix when the set cannot be listed.** Sonnet 5 with adaptive thinking plus the full-credit sentence on
  the same subsample, against thinking alone and the sentence alone.
- Registration, harness and producers committed before any call. Spend caps: Anthropic USD 25, OpenAI USD 25.

### W4. Writing
- **Intro:** a motivation paragraph with counts from W1 and W2 and one quoted benchmark prompt.
- **New Section "How standard graders fail and how to fix it"** (replaces "What helps"): R24-A/B/C/D results, then a short
  recipe:
  (i) grade against the full answer set when it can be listed;
  (ii) otherwise tell the judge that other answers can be correct and use a thinking judge, and expect only partial relief on
  factual questions;
  (iii) for verifiable tasks use a programmatic checker;
  (iv) when none applies, score blind and referenced separately and audit disagreements (max rule stays exploratory).
- **Page budget (9 pages):** move Figure 3b (thinking) and the P3 binned text to the appendix; compress Related work; merge
  Table 2 into the fix section's table.
- Carry the abstract sentence change; add one abstract sentence on standard graders and the fix.

### W5. QA and review
- Number check against the new producer JSONs; one independent QA reviewer (correctness and structure); a harsh AC critic
  round; apply blockers only.

### W6. Release
- Build and render check (Figure 1 on page 1, main text within 9 pages); commit on `papers`; fast-forward `main`; supplement
  refresh with round-24 data (new tokens); anonymity scan. No push, no OSF posting.

## Status log
- 2026-09-14: v2 directory created; W1 survey agent launched; OpenAI key verified (GPT-4.1, o3-mini, GPT-5.x available).
