STAIR mini-proposal · Judge-free evaluation with TFA

# **Can Teacher-Forced Accuracy Reduce the Need for LLM Judges?**

*A short STAIR proposal for validating TFA as a judge-free metric for open-ended reasoning*

**Proposed lead: Brando Miranda  |  Context: Putnam-AXIOM / Teacher-Forced Accuracy**

# **TL;DR**

LLM judges are useful but often prompt-sensitive, unstable, and expensive to validate. Putnam-AXIOM suggests a complementary route: when a benchmark has a gold solution trace, score a model by how well it predicts the next token of that gold trace under teacher forcing.

**Central question:** When gold reasoning traces exist, does TFA correlate with human judgments, strong LLM judgments, and task correctness well enough to serve as a deterministic, judge-free evaluation signal?

# **Motivation**

Open-ended evaluation is becoming harder in the agentic era. A model can produce a proof, plan, tool trajectory, code patch, or free-form explanation; exact-match metrics are too brittle, while LLM judges add another model whose reliability must itself be validated. This creates an evaluation regress: to trust an LLM judge, we need human labels or an oracle. TFA asks whether a simpler deterministic signal can do part of the job when references exist.

Given a problem and a reference solution string, TFA conditions the evaluated model on the gold prefix and asks whether it predicts each next token correctly. Intuitively, it measures local agreement with a trusted reasoning path. It requires no judge prompt, no rubric-tuned evaluator model, and, with log probabilities, only a forward pass over the reference trace.

# **Core hypothesis**

H1: On tasks where a gold reasoning trace is meaningful, TFA is a stable, low-cost proxy for reasoning quality and will correlate with human judgments at least as well as commonly used automatic judge baselines.

This is not assumed true. TFA may penalize valid alternate proofs, favor reference-matching style, or under-score tool-using and compressed solutions. The project is interesting because these failure modes are measurable.

# **Research questions**

* Human alignment: How strongly do TFA, teacher-forced cross entropy, and bits-per-character correlate with expert judgments of solution quality?  
* Judge comparison: On easier tasks where strong LLM judges are likely reliable, does TFA agree with those judges? On harder tasks, does it avoid LLM-judge instability?  
* Beyond final answers: Does TFA distinguish lucky-boxed-correct outputs from genuinely valid reasoning traces?  
* Robustness: How sensitive is TFA to reference style, paraphrases, alternate proofs, model family, response length, and tokenization?  
* Practicality: When does TFA beat LLM judges on the cost/reliability frontier, and when should it be used only as one signal in a hybrid stack?

# **Experimental design**

Use a tiered design so the project can produce a credible result before expensive expert grading is complete.

* Tier 0 — controlled/easy reasoning: short algebra, arithmetic, and symbolic manipulation problems where correctness is nearly unambiguous; use this to calibrate against strong LLM judges.  
* Tier 1 — Putnam-AXIOM and MATH-style reasoning: problems with boxed answers and reference solutions; compute boxed accuracy and TFA-family metrics for models with log probabilities.  
* Tier 2 — human-graded proof traces: sample 200–500 generated solutions from Putnam-AXIOM-Grading or a similar subset; expert raters grade final answer, local validity, gap severity, and overall proof quality.  
* Tier 3 — reference multiplicity stress test: create 2–4 references per problem: original, paraphrased, compressed, and structurally different proofs.

# **Metrics and baselines**

* Reference-conditioned metrics: TFA, teacher-forced cross entropy, bits-per-character, step-normalized TFA, and multi-reference max/mean TFA.  
* Outcome metrics: boxed accuracy, expert rubric scores, and pairwise human preferences.  
* Judge baselines: single-pass rubric judge, comparative judge against a reference, structured chain-of-thought judge, and repeated-sampling judge variance.  
* Controls: lexical overlap, embedding similarity, and solution length, to test whether TFA adds signal beyond surface similarity.

# **Analysis and success criteria**

Report Pearson, Spearman, Kendall, pairwise ranking accuracy, and bootstrapped confidence intervals. For human labels, report inter-rater reliability and compare each automatic metric to the human aggregate. Analyze both across all models and within model families, controlling for length, reference style, final-answer correctness, and model family.

A positive result shows that TFA-family metrics correlate with expert proof-quality scores, identify incorrect reasoning even when the final boxed answer is correct, are more stable than LLM judges under prompt/seed/rubric perturbations, retain signal with paraphrased or multi-reference gold traces, and are cheap enough for routine benchmark pipelines.

# **Risks and de-risking plan**

* Alternate-proof penalty: use multi-reference scoring and paraphrased references; analyze max-vs-mean TFA.  
* Style confounding: include model-family controls and references in multiple styles.  
* Closed-source limitation: treat log-probability access as a scope condition; run slow incremental scoring only on small closed-model samples.  
* TFA is not correctness: frame contribution as reference-conditioned reasoning fidelity, not universal verification.  
* Human grading cost: start with a small expert-labeled pilot and scale only if the pilot shows nontrivial signal.

# **Deliverables and lab ask**

1. Measurement paper on when TFA tracks human and judge-based reasoning quality.  
2. Reusable TFA-family metric code integrated with Putnam-AXIOM / lm-eval-harness workflows.  
3. Small human-graded calibration set of reasoning traces with expert rubric labels.  
4. Practitioner guidance: when to use TFA, when to use LLM judges, and when to combine them.

Lab feedback requested: Is the central claim interesting enough? Which first target is best—Putnam-AXIOM-Grading, MATH-style solutions, code/Lean traces, or controlled easy tasks? Who is interested in human grading, judge baselines, or metric implementation?

# **References**

* Gulati, Miranda, Chen, Xia, Fronsdal, Dumont, Obbad, and Koyejo. Putnam-AXIOM: A Functional and Static Benchmark. arXiv:2508.08292. https://arxiv.org/abs/2508.08292  
* Chen, Gulati, Miranda, Tang, and Koyejo. Rethinking LLM Judges: Chain-of-Thought and Multi-Step Pipelines for Math Grading. ICLR 2026 Workshop on Logical Reasoning of Large Language Models. https://openreview.net/forum?id=vdXPorr099