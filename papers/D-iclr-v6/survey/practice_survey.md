# Is reference-guided LLM judging standard practice? An evidence-backed survey

Survey for v2 of *The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown*.
All entries checked on **2026-09-14**. Structured records: `practice_survey.json`. Verbatim templates: `prompts/`. BibTeX: `new_refs.bib`.

**Method.** Every entry was checked against a primary source fetched on the check date:
- code: raw GitHub files pinned to a commit, or Hugging Face files pinned to a revision;
- official documentation pages;
- paper text: arXiv HTML.

Quotes are copied from the fetched text. Where the prompt text could not be fetched, the entry says so and no prompt is quoted.

- **Reference-guided LLM judge** means the official or built-in scorer shows an LLM, or a trained LLM verifier, a gold or reference answer.
- **Correct = match** means the prompt defines "correct" as agreeing with, matching, containing, or being equivalent to the reference.
- **Several valid** means the prompt says or implies that more than one answer can be correct.

---

## 1. Headline counts

| Group | Surveyed | Reference-guided LLM judge | Not | Notes |
|---|---|---|---|---|
| Benchmarks | 16 | **11** | 5 | The 5 are TruthfulQA (judge sees no reference), HealthBench (rubrics), GAIA (exact match), LiveBench (no judge), Arena-Hard (judge's own answer, no gold) |
| Evaluation libraries | 12 | **11** + 1 partially | 0 | Phoenix: reference QA template in evals v0.20.8; the current default correctness template is reference-free |
| Cloud platforms | 4 | **3** | 1 | Vertex AI: no reference-answer placeholder in its built-in model-based templates |
| RL reward pipelines | 11 | **10** + 1 partially | 0 | Rubrics as Rewards: references are used to write rubrics and in its Reference-Likert baseline |
| Research papers, 2023-2026 (Section 5) | 34 new + 4 already listed above | **34** (29 verified, 5 partially verified) | n/a | Areas: math/science 9, proof grading 4, code 2, QA and RAG 8, agents and deep research 11. 8 of them use the judge in training |
| Surveys / meta-analyses | 4 | n/a | n/a | Only one gives a prevalence count (Yang et al. 2026, see Section 4) |

**Judge prompts whose verbatim text was fetched and that contain a reference slot: 34.** The tally is per scorer entry: HLE and BrowseComp share one template but are counted separately, MLflow's two prompts count once, and LangChain's labeled-criteria prompt counts separately.

- **Define correctness as matching the reference:** 27 yes, 4 partially, 3 no.
  - Partially: FreshEval, DeepEval's GEval example, TinyV, OpenAI RFT.
  - No: LlamaIndex, openevals and LangChain labeled-criteria treat the reference as an optional aid.
- **Say several answers can be valid:** 2 yes, 3 partially, 29 no.
  - Yes: MixEval and FreshEval. Both give the judge a closed list of acceptable answers.
  - Partially: FRAMES ("look for equivalent information or correct answers"), Bedrock ("It is okay if the candidate answer diverges"), TinyV ("despite appearing different from the ground truth"). All three still require the reference's content.
- **None of the 34 prompts tells the judge that a correct answer not among the provided reference(s) should be credited.**
- **Five prompts state outright that the reference is correct or unique:**
  - CRAG: "always correct"
  - Omni-MATH: "ALWAYS correct"
  - CompassVerifier: "ALWAYS CORRECT ... NEVER QUESTION THEM"
  - OpenCompass: "definitely correct"
  - HLE / BrowseComp: "precise and unambiguous [correct_answer]" and "do not argue for any answer different than [correct_answer]"

**Research papers (Section 5).** 34 papers from 2023-2026 that are not already counted above evaluate or train with an LLM judge shown a single reference, or a closed list of references: 29 are verified and 5 partially verified. With Crossing the Reward Bridge, Qwen3, FRAMES and HLE from the tables below, the total is 38.

Can their tasks have several valid answers?
- **Yes, 7.** Several valid answers are acknowledged, but judging is still against one reference or a closed list.
- **Partially, 16.** Mostly equivalent forms of a single answer.
- **No, 11.**

A further 7 records argue for formal or programmatic verification or depend on it. 24 records say LLM judges are used because rule-based checking fails or no checker exists.

Prompt text could not be fetched for SimpleQA Verified (the prompt is in a Kaggle notebook), Kimi k1.5, Qwen3 and Seed1.5-Thinking (not published). These four are counted as reference-guided from their papers and dataset README, but they are excluded from the prompt tallies.

---

## 2. Summary table

Abbreviations: Y = yes, P = partially, N = no, n/a = not applicable or prompt not available.

### 2a. Benchmarks

| Benchmark | Ref-guided judge | Default judge | Reference is called | Correct = match | Several valid | Output |
|---|---|---|---|---|---|---|
| SimpleQA (simple-evals) | Y | gpt-4.1-2025-04-14 | "gold target" | Y | N | A/B/C |
| BrowseComp (simple-evals) | Y | gpt-4.1-2025-04-14 | "[correct_answer]" | Y | N | yes/no + confidence |
| simple-evals MATH equality checker | Y | gpt-4-turbo-preview | Expression 1 vs 2 | Y | N | Yes/No |
| SimpleQA Verified | Y | GPT-4.1 | "gold answer" | n/a (prompt unverified) | n/a | correct/incorrect/not attempted |
| Humanity's Last Exam | Y | o3-mini-2025-01-31 | "[correct_answer]" | Y | N | yes/no + confidence |
| MT-Bench (math, reasoning, coding) | Y | gpt-4 | "reference answer" (GPT-4-generated) | Y | N | 1-10 or [[A]]/[[B]]/[[C]] |
| FreshQA / FreshEval | Y | not verified | "correct_answers" list | P | Y (closed list) | correct/incorrect |
| Meta CRAG | Y | gpt-4-0125-preview | "Ground Truth" | Y | N | JSON score 0/1 |
| MixEval (free-form parser) | Y | GPT-3.5-Turbo-0125 | "golden answer(s)" | Y | Y (closed list) | 0.0-1.0 |
| Omni-MATH (GPT-4o / Omni-Judge) | Y | GPT-4o; Omni-Judge 8B | "reference answer" | Y | N | TRUE/FALSE |
| FRAMES | Y | Gemini-Pro-1.5-0514 | "Ground Truth Answer" | Y | P | TRUE/FALSE |
| TruthfulQA GPT-judge | N (no reference in judge input) | fine-tuned GPT-3 curie | none | n/a | n/a | yes/no |
| HealthBench | N (rubric items) | gpt-4.1-2025-04-14 | "rubric item" | n/a | n/a | criteria_met bool |
| GAIA | N (normalized exact match) | none | ground_truth | n/a | n/a | bool |
| LiveBench | N (no LLM judge) | none | ground truth | n/a | n/a | task scorers |
| Arena-Hard-Auto | N (reference: null; judge answers first) | gpt-4.1 (v2.0) | judge's own answer | n/a | n/a | [[A>>B]]...[[B>>A]] |

### 2b. Evaluation libraries

| Library | Ref-guided scorer | Default judge | Reference is called | Correct = match | Several valid | Output |
|---|---|---|---|---|---|---|
| Inspect AI `model_graded_fact` | Y | 'grader' role, else the evaluated model | "[Expert]" | Y | N | GRADE: C/I(/P) |
| OpenAI Evals `fact` / `closedqa` | Y | set per run | "[Expert]" / "[Criterion]" | Y | N | A-E / Y-N |
| LangChain `QAEvalChain` | Y | gpt-4 | "TRUE ANSWER" | Y | N | CORRECT/INCORRECT |
| LangChain `LabeledCriteriaEvalChain` | Y | gpt-4 | "[Reference]" | N | N | Y/N |
| openevals `CORRECTNESS_PROMPT` | Y | not set | "reference_outputs" | N | N | score |
| LlamaIndex `CorrectnessEvaluator` | Y | Settings.llm | "Reference Answer" | N | N | 1-5 |
| RAGAS `answer_correctness`, `factual_correctness` | Y | user LLM | "ground truth" / "reference" | Y | N | F-beta 0-1 |
| DeepEval `GEval` + `EXPECTED_OUTPUT` | Y (user-configured) | DeepEval default | "expected output" | P | N | score |
| MLflow `answer_correctness` / genai `Correctness` | Y | openai:/gpt-4 (v1); databricks or openai:/gpt-4.1-mini (genai) | "targets" / ground_truth as `<claim>` | Y | N | 1-5 / yes-no |
| promptfoo `factuality` | Y | gpt-5.6-sol | "expert_answer" | Y | N | A-E |
| Arize Phoenix QA | P (legacy v0.20.8 only) | user LLM | "[Reference]" | Y | N | correct/incorrect |
| TruLens GroundTruthAgreement | Y | user provider | "expected answer" | Y | N | 1-10 |
| OpenCompass GenericLLMEvaluator | Y | OC_JUDGE_MODEL | "Gold Target" / "standard answer" | Y | N | A/B |

The LangChain chains appear on two rows because they have separate prompts, but LangChain counts as one library in Section 1.

### 2c. Cloud platforms

| Platform | Ref-guided judge | Default judge | Reference is called | Correct = match | Several valid | Output |
|---|---|---|---|---|---|---|
| OpenAI platform graders (score_model) | Y | example: o4-mini-2025-04-16 | "item.reference_answer" | Y | N | 0-1 |
| Azure AI Foundry `builtin.similarity` | Y | user deployment | "ground_truth" / "correct answer" | Y | N | 1-5 (pass at 3) |
| Google Vertex AI model-based templates | N | n/a | none | n/a | n/a | n/a |
| AWS Bedrock "Correctness with ground truth" | Y | user-selected evaluator | "Ground Truth Response" | Y | P | correct / partially correct / incorrect |

### 2d. RL reward pipelines

| Pipeline | Ref-guided verifier | Verifier model | Reference is called | Correct = match | Several valid | Output |
|---|---|---|---|---|---|---|
| DeepSeek-R1 | Y | DeepSeek-V3 | "Reference Answer" / "ground-truth" | Y | N | correct/incorrect JSON |
| Kimi k1.5 | Y | trained Kimi CoT reward model | "reference answer" | n/a (prompt not published) | n/a | scalar / JSON |
| Qwen3 | Y | Qwen2.5-72B-Instruct | "reference answer" | n/a (prompt not published) | n/a | score |
| Seed1.5-Thinking | Y | Seed-Verifier / Seed-Thinking-Verifier | "reference answer" | n/a (described: "essentially equivalent") | n/a | YES/NO |
| General-Reasoner | Y | TIGER-Lab/general-verifier (1.5B) | "Ground Truth Answer" | Y | N | Final Decision: Yes/No |
| Crossing the Reward Bridge | Y | Qwen2.5-7B-Instruct-RLVR (distilled from a 72B teacher) | "Reference Answer" | Y | N | YES/NO (soft probability) |
| xVerify | Y | xVerify models | "Correct answer" | Y | N | [Correct]/[Incorrect] |
| CompassVerifier | Y | CompassVerifier models | "Standard Answer" | Y | N | A/B/C |
| TinyV | Y | configurable verifier | "ground_truth_answer" | P | P | True/False |
| Rubrics as Rewards | P | LLM judge (gpt-4o-mini for evaluation) | "reference response" | Y (Reference-Likert baseline) | N | 1-10 |
| OpenAI RFT graders | Y | user-set grader model | "Reference Answer" | P | N | 0-1 |

---

## 3. How the prompts treat an answer that differs from the reference

**Pattern A: the reference is declared correct, or the only acceptable answer.**
- HLE and BrowseComp: "Judge whether the following [response] to [question] is correct or not based on the precise and unambiguous [correct_answer] below." ... "do not argue for any answer different than [correct_answer], focus only on whether the answers match."
- CRAG: "1: Take it as granted that the Ground Truth is always correct." ... "4: If the Prediction does not exactly match the Ground Truth, go through the following steps and likely give a score as 0."
- Omni-MATH (GPT-4o template and the Omni-Judge chat template): "The reference answer is ALWAYS correct. You should carefully judge whether the student gives the same answer as reference answer."
- CompassVerifier: "THE STANDARD ANSWER IS ALWAYS CORRECT AND THE QUESTION IS PERFECTLY VALID. NEVER QUESTION THEM." Its CoT variant grades as INCORRECT "Any deviation from standard answer".
- OpenCompass: "You can assume that the standard answer is definitely correct."

**Pattern B: correctness is defined as matching, containing or being equivalent to the reference.**
- SimpleQA: "They fully contain the important information in the gold target." / "A factual statement in the answer contradicts the gold target."
- Inspect AI: "Does the submission contain the content in the expert answer?"
- OpenAI Evals and promptfoo factuality: "(D) There is a disagreement between the submitted answer and the expert answer."
- General-Reasoner: "please verify if the student's answer is equivalent to the ground truth answer."
- Crossing the Reward Bridge: "If they **match exactly**, output **YES**." / "If they **do not match**, output **NO**."
- DeepSeek-R1: "**correct**: The answer fully aligns with the reference answer in both reasoning process and final conclusion".
- xVerify: "the output must align with the correct answer in content and meaning to be considered [Correct]."
- Azure: "Equivalence, as a metric, measures the similarity between the predicted answer and the correct answer."
- TruLens: "how semantically similar the responses are to the expected answer."
- MLflow v1: "Score 1: The output is completely incorrect. It is completely different from or contradicts the provided targets."
- RAGAS: "FP (false positive): statements present in the answer but not directly supported by any statement in ground truth".
- OpenAI graders example: "If the reference and model answer are exact matches, output a score of 1. If they are somewhat similar in meaning, output a score in 0.5. Otherwise, give a score of 0."
- Rubrics as Rewards, Reference-Likert baseline: "The reference response represents a high-quality answer that you should use as a benchmark."

**Pattern C: several acceptable answers, but only from a closed list.**
- MixEval: "Note that each one of the golden answers is considered correct. Thus if the model's answer matches any one of the golden answers, it should be considered correct."
- FreshEval: the judge is given "a list of valid answers for the question" (paper). Its prompt adds: "approximate numbers are generally not accepted unless explicitly included in the ground-truth answers."

**Pattern D: allowances for surface form only.** Each prompt allows wording or format to differ but still requires the reference's content.
- FRAMES: "look for equivalent information or correct answers. Do not focus on exact wording unless the exact wording is crucial to the meaning."
- Bedrock: "It is okay if the candidate answer diverges; if the essential points are mentioned then the candidate answer is correct."
- TinyV: "identifying if the model's answer is correct compared to the ground truth answer despite appearing different from the ground truth."

**Pattern E: the reference is offered as an optional aid.**
- LlamaIndex: "You may also be given a reference answer to use for reference in your evaluation."
- openevals: "Use the reference outputs below to help you evaluate the correctness of the response".

Neither prompt says what to do when a correct answer differs from the reference.

**Closest acknowledgement found, not in a judge prompt.** The Rubrics as Rewards rubric-generation prompt says: "The reference answer is an ideal response but not necessarily exhaustive; use it only as guidance." This prompt writes rubrics; the reward judge never sees it.

Some documentation assumes unique answers. OpenAI RFT: "RFT works best with unambiguous tasks". The HLE paper: questions "have specific, unambiguous answers accepted by domain experts."

---

## 4. Prevalence counts from surveys and meta-analyses

- **Yang et al. 2026**, *What Are We Measuring in NLG?* (arXiv 2601.07648; corpus of 14,171 papers from four NLP conferences, 3,334 NLG papers):
  - Figure 1 caption: "LaaJ adoption surged from less than 1% before 2023 to 46% in 2025, surpassing human evaluation, which declined from 51% to 43%."
  - Section 5.3: "Only 254 of these (58.7%) explicitly validate LaaJ against human judgments, representing of the 679 NLG papers using LaaJ, under 8% of total 3,334 NLG papers." A symbol is missing from this sentence in the arXiv HTML rendering.
  - The count covers LLM-as-a-judge in general, not reference-guided judging specifically.
- **Gu et al. 2024**, *A Survey on LLM-as-a-Judge* (2411.15594): no prevalence count found in a full-text search.
- **Li et al. 2024**, *LLMs-as-Judges* (2412.05579): no count. Taxonomy quote: "Evaluation References are optional. Depending on the availability of evaluation reference, the evaluation process can be broadly divided into reference-based and reference-free scenarios." Also: "its effectiveness may be constrained by the quality and variety of the reference data."
- **Li et al. 2025**, *From Generation to Judgment* (EMNLP 2025, 2411.16594): no prevalence count found.
- **No published count of reference-guided judges was found.** The tallies in Section 1 are this survey's own.
- **Two related data points:**
  - Crossing the Reward Bridge (2503.23829) writes that prior RL studies such as "Zelikman et al., 2022; Gandhi et al., 2024; Zhang et al., 2024b; Lambert et al., 2024; Guo et al., 2025; Ma et al., 2025a; Yu et al., 2025" assign binary correctness given "access to the reference answer".
  - TinyV (2505.14625) reports that the rule-based Prime Verifier "mislabels 87K (38.5%) correct responses as incorrect".

---

## 5. Research papers that evaluate or train with a single-reference LLM judge

**Scope.** Papers from 2023-2026 in five areas:
- math and science reasoning (benchmarks and RL),
- proof grading,
- code evaluation,
- factual, open-domain QA and RAG evaluation,
- agents and deep research.

**Verification.** Every record was checked on 2026-09-14 against arXiv HTML (the Seed-Prover PDF) and, where noted, the official code. The records sit under `research_papers` in `practice_survey.json`, each with section location, judge model, reference wording, quotes and a several-valid-answers label. All 133 quote fragments were re-matched against the downloaded source text: 132 match exactly, and one WebDancer quote matches on 8-word windows because the HTML dropped a math symbol.

**Counts.**
- **Papers:** 34 papers not already counted in Section 2 use a single-reference LLM judge: 29 verified, 5 partially verified.
- **Totals by area:**

  | Area | Papers |
  |---|---|
  | math and science | 9 |
  | proof grading | 4 |
  | code | 2 |
  | QA and RAG | 8 |
  | agents and deep research | 11 |

- **Used in training:** 8 papers use the judge as an RL reward or data filter: Huang et al. 2025, MiniMax-M1, Guru, Llama-Nemotron, WebDancer, WebSailor, ASearcher, WebExplorer.
- **Tasks with several valid answers:**
  - **Yes, 7.** Kamalloo et al. 2023, EVOUNA, DeepResearcher, DeepResearch Bench, ICE-Score, CodeJudge, Proof or Bluff. In each, the judge still sees one reference, or a closed list of references.
  - **Partially, 16.** The papers accept equivalent forms of one answer.
  - **No, 11.**
- **Dropped after checking:** MultiHop-RAG, PEDANTS, Nemotron-CrossThink, Big-Math, Skywork-OR1, Magistral, Writing-Zero, Search-o1, WebShaper, Brains vs. Bytes. None uses a reference-based LLM judge, or the protocol was unstated.

### 5a. Papers

Use: E = evaluation, T = training (RL reward or data filter). Several valid: Y / P / N.

| # | Paper (arXiv) | bib key | Use | Where described | Judge | Reference wording | Several valid | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | From Accuracy to Robustness: rule- and model-based verifiers (2505.22203) | `huang2025pitfalls` (existing) | E+T | Sec. 3.1, Fig. 5; Sec. 3.3-6 | GPT-4o annotator; general-verifier, xVerify, R1-Distill-Verifier | "target answer" | P | verified (Fig. 5 prompt is an image) |
| 2 | U-MATH (2412.03205) | `chernyshev2024umath` | E | Sec. 3; App. C.2, Fig. 9 | o3-mini | "CORRECT ANSWER: {{golden_answer}}" | P | verified |
| 3 | Solving Inequality Proofs / IneqMath (2506.07927) | `lu2025ineqmath` | E | Sec. 4.1; App. B.1 | GPT-4o-mini | ground truth | N | verified |
| 4 | UGPhysics (2502.00334) | `xu2025ugphysics` | E | Sec. 3.3; App. B.4 | GPT-4o (after rule stage) | "ground-truth answers" | P | partially (prompt not in paper) |
| 5 | MiniMax-M1 (2506.13585) | `minimax2025m1` | T | Sec. 4.2, Tasks with Ground Truth | MiniMax GenRM | "ground-truth answers" | P | verified |
| 6 | Guru: RL for reasoning, cross-domain (2506.14965) | `cheng2025guru` | T | Model-Based Verification; Sec. 8 | TIGER-Lab general-verifier 1.5B | "reference answer" | P | verified |
| 7 | Llama-Nemotron (2505.00949) | `bercovich2025llamanemotron` | T | Accuracy rewards; math SFT filtering | Llama-3.3-70B-Instruct; Qwen2.5-32B-Instruct | "ground truth answer" | P | verified |
| 8 | OlympicArena (2406.12753) | `huang2024olympicarena` | E | Model-based Evaluation; Fig. 16 | GPT-4V | "the correct answer" | P | verified |
| 9 | MathOdyssey (2406.18321) | `fang2024mathodyssey` | E | Evaluation metric | GPT-4 | "the provided solution" | P | verified |
| 10 | Proof or Bluff? (2503.21934) | `petrov2025proofbluff` | E (grader test) | Sec. 3.3; App. A.2 | o3-mini, Claude 3.7 (the Table 2 caption instead names o3-mini and R1) | "a verified solution" + grading scheme | Y | verified |
| 11 | Towards Robust Mathematical Reasoning / IMO-ProofBench (2511.01846) | `luong2025imobench` | E | Sec. 3.2; App. B.5-B.6 | Gemini 2.5 Pro | "Ground Truth Solution" | P | verified |
| 12 | RefGrader (2510.09021) | `mahdavi2025refgrader` | E | Sec. 5.2; grading prompts | Gemini 2.5 Pro | "reference solution" | P | verified |
| 13 | MathArena (2505.23281) | `balunovic2025matharena` | E (final answers) | Sec. 3.3 | Gemini-2.5-Flash, cross-checked with a parser | "ground truth" | N | verified |
| 14 | ICE-Score (2304.14317) | `zhuo2024icescore` | E | Sec. 3; Tables 1-2 | GPT-3.5-turbo (and GPT-4) | "reference code" | Y | verified |
| 15 | CodeJudge (2410.02184) | `tong2024codejudge` | E | Sec. 4; App. tables "w/ ref" | GPT-3.5-Turbo, Llama-3-8B-Instruct and others | "reference code" | Y | verified |
| 16 | Answer Matching Outperforms Multiple Choice (2507.02856) | `chandak2025answermatching` | E | App. F.1 | Qwen3, DeepSeek, Llama matchers | "ground truth answer" | P | verified |
| 17 | Chinese SimpleQA (2411.07140) | `he2024chinesesimpleqa` | E | Sec. 2.2, 2.5 | not stated | "reference answer" | N | partially (grader prompt not in paper) |
| 18 | RAGChecker (2408.08067) | `ru2024ragchecker` | E | Sec. 3.1-3.3 | Llama3-70B-Instruct | "ground truth answer" | P | verified |
| 19 | BERGEN (2407.01102) | `rau2024bergen` | E | Sec. 5.1; App. G | SOLAR-10.7B-Instruct | "golden answer" | P | verified |
| 20 | Reference-Guided Verdict (2408.09235) | `refguided2024` (existing) | E | Sec. 3; App. D.2 | Mistral 7B, Llama-3.1 70B, GPT-3.5-turbo | "Reference Answer" | P | verified |
| 21 | Evaluating Open-Domain QA in the Era of LLMs (2305.06984) | `kamalloo2023evaluating` (existing) | E | Sec. 4.2; App. A | InstructGPT, GPT-4 | "Answer" (gold) | Y | verified |
| 22 | Judging the Judges (2406.12624) | `thakur2025judging` (existing) | E | Sec. 3; App. E, N | 13 judge models | "reference answers" | P | partially (prompt is a figure) |
| 23 | Evaluating Open-QA Evaluation / EVOUNA (2305.12421) | `wang2023evouna` | E | Sec. 3-4; App. E.5 | GPT-3.5 (text-davinci-003) | "a set of golden answers" | Y (closed list) | verified |
| 24 | WebWalker (2501.07572) | `wu2025webwalker` | E | Sec. 5.1; App. F.1; code | GPT-4 via LangChain cot_qa | "true answer" | N | verified |
| 25 | BrowseComp-ZH (2504.19314) | `zhou2025browsecompzh` | E | Sec. 4; App. A.2 | GPT-4o, BrowseComp prompt | [correct_answer] | N | verified |
| 26 | WebDancer (2505.22648) | `wu2025webdancer` | E+T | Sec. 4; reward design | GPT-4o; Qwen-72B-Instruct (reward) | "reference answer" | N | verified |
| 27 | WebSailor (2507.02592) | `li2025websailor` | E+T | Sec. 4-5; eval code | qwen2.5-72b-instruct | "[correct_answer]" / "labeled answer" | N | verified |
| 28 | ASearcher / Beyond Ten Turns (2508.07976) | `gao2025asearcher` | E+T | Sec. 4-5; eval code | Qwen2.5-72B-Instruct | "labeled answer" | P | verified |
| 29 | DeepResearcher (2504.03160) | `zheng2025deepresearcher` | E | Sec. 4; App. A.2 | GPT-4o-mini | "ground truth answer list" | Y (closed list) | verified |
| 30 | BrowseComp-Plus (2508.06600) | `chen2025browsecompplus` | E | Sec. 4; App. F | gpt-4.1 | "[correct_answer]" | N | verified |
| 31 | DeepResearch Bench, RACE (2506.11763) | `du2025deepresearchbench` | E | Sec. 3.1; RACE code | Gemini-2.5-pro | "reference report" | Y | verified |
| 32 | WebThinker (2504.21776) | `li2025webthinker` | E | App. C.3.1 | Qwen2.5-72B-Instruct | "Labeled Answer" | N | verified |
| 33 | WebExplorer (2509.06501) | `liu2025webexplorer` | E+T | RL reward; evaluation | DeepSeek-V3 | "ground truth answers" | N | partially (no prompt text) |
| 34 | Tongyi DeepResearch (2510.24701) | `tongyi2025deepresearch` | E | App. B | per benchmark: GPT-4o, o3-mini, Qwen2.5-72B, Gemini-2.0-Flash | "ground truth" | N | partially (reward mechanism unstated) |

### 5b. Quotes from the research papers

- **IMO-ProofBench** (2511.01846), proof autograder prompt and limitations appendix: "**Ground Truth Solution:** A reference solution. Assume this solution is correct. It demonstrates one valid approach." The appendix says the grader is "prone to be overly punitive for minor formatting issues or unconventional yet correct solutions." App. B.6 reports a "novel solution entirely different from the established ground truth" that got 6/7 from a human grader and was marked wrong by the autograder.
- **Answer Matching** (2507.02856), App. F.1 matcher prompt: "Your job is to ONLY check whether the given response matches the ground truth answer or not in the context of the question. You DO NOT NEED to assess the correctness of the response."
- **Kamalloo et al. 2023** (2305.06984): "lexical matching fails completely when a plausible candidate answer does not appear in the list of gold answers". Also: "Such failures largely stem from the incomplete list of gold answers that do not fully cover all plausible answers." The InstructGPT-eval example is "Answer: Peking Candidate: Jicheng Is candidate correct?"
- **CodeJudge** (2410.02184): "Surprisingly, providing reference code leads to worse performance for all three LLM-based methods in the CoNaLa dataset." The explanation: "the LLM evaluator focuses too much on the differences between the generated code and reference code rather than high-level semantic similarities."
- **RefGrader** (2510.09021): "The reference solution is guaranteed correct, but may differ in presentation." Also: "Contradictions imply the given solution is wrong at that step."
- **WebSailor** (2507.02592) and **BrowseComp-Plus** (2508.06600) reuse the HLE/BrowseComp line "do not argue for any answer different than [correct_answer], focus only on whether the answers match."
- **DeepResearch Bench** (2506.11763): "the target report's score is determined relative to the reference report's score". The reference is a single model-generated report for an open-ended research task.
- **DeepResearcher** (2504.03160), closed list: "the pred_answer should be semantically same to at least one of them."
- **Uniqueness is enforced rather than handled:**
  - Chinese SimpleQA: "the answer to each question must be unique, precluding the possibility of multiple correct responses."
  - BrowseComp-ZH: "there is only one correct and unambiguous answer that satisfies all the constraints of each question."
  - ASearcher: "we evaluate whether any of the mismatched answers generated during the Difficulty Measurement step could serve as alternative valid answers."
  - Big-Math (dropped; no judge): "problems with uniquely verifiable solutions".

### 5c. LLM judges appear where no programmatic checker exists

Twenty-four records say this directly. Representative quotes, all verified:
- **Crossing the Reward Bridge** (2503.23829): "only 60.3% of mathematical problems possess single-term numerical answers verifiable by rule-based methods, with the ratio dropping further to 45.4% for complex multi-domain queries."
- **Qwen3** (2505.09388): "avoiding false negatives that can occur with purely rule-based rewards."
- **MiniMax-M1** (2506.13585): "answers are objective but may have multiple valid expressions. Such diversity often renders rule-based answer checkers inaccurate."
- **Guru** (2506.14965): Science answers "are often open-ended and difficult to evaluate using deterministic rules".
- **OlympicArena** (2406.12753): "To deal with those problems with answer types that cannot be appropriately evaluated using rule-based matching, we employ model-based evaluation."
- **Huang et al. 2025** (2505.22203): "widely used rule-based verifiers fail to recognize equivalent answers in different formats". Also: "Model-based verifiers substantially improve static accuracy but are highly susceptible to reward hacking during RL".
- **WebDancer** (2505.22648): "the QA answers are inherently non-verifiable, cannot be reliably evaluated using rule-based F1/EM metrics".
- **DeepResearcher** (2504.03160): "Rule-based evaluation doesn't suit long-form responses, so we adopt a model-based evaluation (MBE) approach using LLM-as-a-Judge".
- **BERGEN** (2407.01102): "surface-matching metrics fail to capture whether the answer is correct."
- **CodeJudge** (2410.02184): "many tasks do not come with test cases or only have insufficient test cases that miss corner cases".
- **FRAMES** (2409.12941): "Since the gold answers to questions in the dataset are free-form tokens instead of choices from multiple-choice answers, we use an LLM to evaluate".
- **MT-Bench** (2306.05685): "devising a rule-based program to assess the outputs is extremely challenging."
- **VeriFree** (2505.21493): "Current practical workarounds use an additional LLM as a model-based verifier".

### 5d. Formal or programmatic verification as the alternative

Seven records, all verified:
- **MathConstruct** `balunovic2025mathconstruct`, existing key: "these benchmarks still rely on fixed-answer verification, often using an LLM as a judge for comparison." Its alternative: "verifying if a proposed construction satisfies the problem constraints is usually straightforward, enabling the use of automated verifiers to judge model responses." Each problem has a verifier function, so any valid construction is accepted.
- **Formal Mathematical Reasoning: A New Frontier in AI** `yang2024formalmath`: "solutions to many advanced problems are not numbers that can be evaluated by comparing them with the ground truth."
- **Proof or Bluff?** `petrov2025proofbluff`: "Current benchmarks that mitigate this issue either rely on formal verification tools like Lean ... or focus on the evaluation of constructive proofs". On LLM graders given a verified solution: "neither model accurately graded the solutions, consistently overestimating their quality."
- **Seed-Prover** `chen2025seedprover`: "Unlike natural language, formal languages such as Lean can provide a clear and automatic signal on the correctness of a formalized proof."
- **DeepSeek-Prover-V2** `ren2025deepseekproverv2`: proof assistants "operate on strict logical foundations, where every proof step must be explicitly constructed and formally verified."
- **PutnamBench** `tsoukalas2024putnambench`: evidence of practice, not an argument. "machine-verifiable proofs".
- **Kimina-Prover** `wang2025kimina`: proofs are checked by the Lean compiler, but formalization still has no checker. "there is no straightforward way to verify the correctness of a generated formal problem statement with respect to the natural language input." The paper uses an LLM judge there.
- **MathArena** (in 5a) chooses humans over LLM judges for proofs: "Automated grading is currently insufficient for proof-based problems, so we rely on expert human graders".

**Takeaway for the paper.** Programmatic and formal checkers appear where answers are machine-checkable: final numbers, Lean proofs, constructions with a verifier. LLM judges with a single reference fill the rest: free-form science answers, factual QA, agent answers, long reports, informal proofs and code without tests. These are the settings where several valid answers are most likely. Several papers keep checking workable by filtering tasks to unique answers (Big-Math, Chinese SimpleQA, BrowseComp-ZH, ASearcher) rather than by telling the judge that other answers may be correct.

## 6. Strongest examples to cite in the paper

1. **Humanity's Last Exam** `phan2025hle`, and the same template in **BrowseComp** `wei2025browsecomp`. Default judge o3-mini.
   > "do not argue for any answer different than [correct_answer], focus only on whether the answers match."
   > "Answer 'no' otherwise, i.e. if there if there is any inconsistency, ambiguity, non-equivalency, or if the extracted answer is incorrect."

   Sources: https://github.com/centerforaisafety/hle/blob/73ae974b1844/hle_eval/run_judge_results.py#L16-L33 and https://github.com/openai/simple-evals/blob/652c89d0ca9d/browsecomp_eval.py#L26-L45

2. **CompassVerifier** `liu2025compassverifier`, used for evaluation and as an outcome reward.
   > "THE STANDARD ANSWER IS ALWAYS CORRECT AND THE QUESTION IS PERFECTLY VALID. NEVER QUESTION THEM."

   Source: https://github.com/open-compass/CompassVerifier/blob/2d7cba6df0b2/src/prompts.py

3. **Meta CRAG** `yang2024crag`. Default judge gpt-4-0125-preview.
   > "1: Take it as granted that the Ground Truth is always correct."
   > "4: If the Prediction does not exactly match the Ground Truth, go through the following steps and likely give a score as 0."

   Source: https://github.com/facebookresearch/CRAG/blob/ad1518887dd4/prompts/templates.py#L7-L20

4. **Omni-MATH** `gao2024omnimath`, GPT-4o judge. The same line is in the Omni-Judge chat template.
   > "The reference answer is ALWAYS correct. You should carefully judge whether the student gives the same answer as reference answer."

   Source: https://github.com/KbsdJames/Omni-MATH/blob/23be225c8e26/GPT_eval/gpt_evaluation_template.txt

5. **RL rewards: DeepSeek-R1** `deepseek2025r1` and **Crossing the Reward Bridge** `su2025rewardbridge`.
   > DeepSeek-R1: "some of which uses a generative reward model by feeding the ground-truth and model predictions into DeepSeek-V3 for judgment" ... "**correct**: The answer fully aligns with the reference answer in both reasoning process and final conclusion"
   > Reward Bridge verifier: "If they **match exactly**, output **YES**." / "If they **do not match**, output **NO**."

   Sources: https://arxiv.org/html/2501.12948 (Listing 4) and https://huggingface.co/virtuoussy/Qwen2.5-7B-Instruct-RLVR/blob/1b9a9a093ba3/model_server.py#L17

   A useful companion is Qwen3 `yang2025qwen3`: "we provide a reference answer for each query and prompt Qwen2.5-72B-Instruct to score the model's response based on this reference."

6. **Default library scorers.** Inspect AI `inspectai`, OpenAI Evals `openaievals` and promptfoo `promptfoofactuality`.
   > Inspect AI: "You are comparing a submitted answer to an expert answer on a given question." ... "Does the submission contain the content in the expert answer?"
   > OpenAI Evals `fact`, reused verbatim by promptfoo: "(D) There is a disagreement between the submitted answer and the expert answer."

   Sources: https://github.com/UKGovernmentBEIS/inspect_ai/blob/3f63975a5d1c/src/inspect_ai/scorer/_model.py#L385-L403 and https://github.com/openai/evals/blob/8eac7a7de521/evals/registry/modelgraded/fact.yaml

Contrast worth citing, showing how multiple answers are handled today: **MixEval** `ni2024mixeval`, "Note that each one of the golden answers is considered correct. Thus if the model's answer matches any one of the golden answers, it should be considered correct." Correctness remains membership in a closed list.

---

## 7. Caveats and entries not fully verified

- **SimpleQA Verified.** The autorater prompt is in a Kaggle notebook that was not fetched. The paper and HF README were verified: GPT-4.1 grader, SimpleQA grading scheme, numeric gold answers rewritten with "acceptable range". No prompt is quoted.
- **Kimi k1.5, Qwen3 and Seed1.5-Thinking.** The verifier prompts are not published; only the papers' descriptions are quoted.
- **Google Vertex AI.** The docs page body did not render through the fetcher. The finding rests on the SDK template files `vertexai/evaluation/metrics/_default_templates.py` and the preview equivalent at commit a7e5c9c6cecd.
- **FreshEval.** The default judge model is not verified.
- **simple-evals.** Only `MathEval` calls the LLM equality checker; no AIME eval exists in `simple_evals.py` at commit 652c89d0ca9d.
- **DeepEval.** The GEval "Correctness" example was read through the WebFetch rendering of the docs page. GEval is a generic metric and uses the reference only when the user adds `EXPECTED_OUTPUT`.
- **Phoenix.** The reference-based QA template is from `arize-phoenix-evals-v0.20.8`. At HEAD (72daf48aaedf) the built-in correctness evaluator has no reference slot.
- **MT-Bench.** Per the paper, the "reference answer" is GPT-4's own answer, not a human gold answer. References are used only for the math, reasoning, coding and arena-hard-200 categories.
- **Arena-Hard.** Configs set `reference: null`. The original judge prompt makes the judge write its own answer first, which acts as an implicit reference.
- **Bedrock.** Prompts differ per evaluator model. The quote is from the Claude Sonnet 4.5 evaluator page.
- **Text extracted from arXiv HTML.** The DeepSeek-R1 Listing 4 and FRAMES Figure 6 files are HTML-to-text extractions. Math symbols can be dropped and typographic quotes are preserved as rendered.
- **Repository and default-model drift.** LangChain's evaluators now live in `langchain_classic`, and promptfoo's default grader is `gpt-5.6-sol` at commit 253e7aa83e70. Defaults change often; cite the commit.

- **Research papers (Section 5).**
  - Partially verified: UGPhysics and Chinese SimpleQA (prompt not in the paper), Judging the Judges (prompt is a figure), WebExplorer (no prompt text), Tongyi DeepResearch (reward mechanism not specified).
  - Proof or Bluff names o3-mini and Claude 3.7 as graders in its text, but its Table 2 caption says o3-mini and R1.
  - IMO-Bench's arXiv title is "Towards Robust Mathematical Reasoning".
  - The Huang et al. 2025 judge prompt and the BrowseComp-ZH grading prompt are images in the HTML; only their captions and surrounding text were checked.
  - Kimi-Researcher was not checked.

## 8. Files

- `practice_survey.json`:
  - 47 survey records;
  - `research_papers`: 47 records from the Section 5 search. 38 use a single-reference judge, 4 of which are also in the main survey; the rest are formal-verification or no-checker quote records. Dropped candidates are listed under `summary.research_papers.dropped_candidates`;
  - a computed summary.
- `prompts/`: 24 verbatim templates. Each file starts with a source URL, commit and retrieval-date header.
  - Benchmarks: simpleqa_grader, hle_browsecomp_judge, simple_evals_math_equality_checker, mtbench_reference_guided, crag_grader, omnimath_gpt4o_judge, mixeval_freeform_judge, frames_autorater, fresheval_strict_prefix_and_demos.
  - Libraries: inspect_model_graded_fact, openai_evals_fact.yaml, langchain_qa_eval, llamaindex_correctness, mlflow_correctness, promptfoo_factuality, phoenix_legacy_qa, opencompass_generic_llm_grader.
  - Platforms: azure_similarity.prompty, bedrock_correctness_with_ground_truth.
  - RL: deepseek_r1_v3_judge, general_verifier, reward_bridge_rlvr_verifier, xverify_judge, compassverifier_prompts.
- `new_refs.bib`: new entries only, 76 in total. 37 research-paper entries are between the `BEGIN/END research papers` markers. Reuse these existing keys from `../references.bib`: `zheng2023judging`, `liu2025compassverifier`, `chen2025xverify`, `ma2025generalreasoner`, `xu2025tinyv`, `yan2025verifybench`, `wei2024simpleqa`, `wei2025browsecomp` and `phan2025hle`. The last three were added to `references.bib` on 2026-09-14 while this survey was in progress.
