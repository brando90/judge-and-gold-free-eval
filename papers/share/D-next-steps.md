# Paper D — Next Steps: answer-anchoring vs method-anchoring, and new benchmarks

*Drafted 2026-08-25. Everything here is pre-data planning; per house rules, any confirmatory
arm gets its predictions registered (`papers/registrations/osf_drafts.md` → OSF) and its
pipeline committed before generation.*

## The central hypothesis to test next (Sri, 2026-08-25)

Paper D established **answer-multiplicity** anchoring: when several *final answers* are
valid, the judge rewards the one matching the shown reference. The next question is what
the judge actually anchors **on**:

> **Hypothesis (H-METHOD):** multiple valid *methods* reaching the *same* final answer will
> NOT reproduce the inversion. If anchoring keys on the final answer, a candidate that
> matches the reference's answer via a different derivation still "matches," so
> method-variation is forgiven and no inflation appears.

Why this is a real, falsifiable fork:
- **Supports H-METHOD:** our rotation experiment defined matching by the *extracted boxed
  answer* only; the +9.5-point flips followed the answer string, and our tasks' "methods"
  were too short to carry independent signal. Nothing in our data shows method anchoring.
- **Against H-METHOD:** the solution-fixation literature (fixation bias) reports judges
  penalizing valid solutions that *differ in approach* from a worked reference. If that
  holds dynamically, method-multiplicity alone would inflate — which would extend paper D's
  warning to **unique-answer tasks with worked-solution references** (a much bigger blast
  radius than the current claim).

Either outcome is publishable: a confirmed null cleanly localizes anchoring to the answer
token(s) and certifies worked references safe at k=1; a falsification widens the boundary.

## Ranked experiment queue

| # | Experiment | Tests | New code needed | Cost |
|---|---|---|---|---|
| **P0** | **Run pipeline17** (judge-coverage extension, Registration 5 — **already registered externally**, committed pre-data in `e75e465`; running it needs no new OSF action) | The fix's judge-generality: re-judges the frozen k-stratified pool with gemma-2-9b-it, Mistral-7B-Instruct-v0.3, Qwen2.5-14B (backup Yi-1.5-9B), turning M1's evidence base from 2 judges into 5 across 4 families — the paper's most-cited limitation | None — `bash pipeline17.sh <GPU> <JUDGE>`, three invocations | Cheapest of all: judging only, frozen pool and samples reused |
| E1 | **Worked-reference arm** on the existing 120-task / k-stratified pools: new condition `refsol` where the reference is a synthesized worked solution ("x must be odd and ≡2 mod 5; candidates are …; take 37") instead of the bare answer | Does a *longer* reference (more matching surface) anchor more or less than a bare answer at k>1? Closes the paper's stated "long reference untested" limitation | Per-family solution-text generator (~100 lines); one new `bon_judge.py` cond | Cheapest: reuses frozen pools + samples, judging only |
| E2 | **Same-answer, different-method** on unique-answer math (MATH subset): worked gold reference (method A); candidates curated/generated to reach the same answer by method B; margin = method-matching vs non-matching *correct* candidates; plus best-of-64 inflation vs blind | **H-METHOD directly** — the discriminating control between answer-anchoring and method-anchoring | Method-diversity curation (generate n samples, cluster by approach — LLM-label the method, human-audit a subset) | Medium: needs candidate curation |
| E3 | **Code rotation** (HumanEval → CodeContests): rotate the reference among genuinely different correct implementations; oracle = unit tests. Two sub-arms: (a) same-behavior different-implementation = pure method multiplicity; (b) CodeContests problems that accept multiple correct *outputs* (~25% of them) = answer multiplicity, the code analog of the k-step | H-METHOD in its purest form (implementations differ maximally, behavior identical), plus cross-domain replication of the k-step | Harness mostly exists (`--domain code/mbpp`, code oracle); CodeContests loader + accepted-solutions reference picker | Medium |
| E4 | **MACE replication** (arXiv 2602.07842): natural-language factual k-grid, k∈{1,2,4,6} controlled by design, Wikidata-enumerated answer sets, 500 questions per cell across 6 domains | External validity of the k-step beyond arithmetic constraint families — the strongest realism upgrade available off-the-shelf | MACE task-file builder (same schema as `runs/bon_synthk_tasks.jsonl`); enumeration-completeness audit (reuse the checker-adjudication machinery) | Medium |
| E5 | **ARC-DA** (arXiv 2102.03315): 2,985 direct-answer science questions, 8,436 valid answers (~2.8/question) | Realism extension to crowd-enumerated science QA | Needs the label-correction machinery up front (answer lists are known-incomplete; no exact oracle — evaluation there uses F1/ROUGE) | Higher: adjudication-heavy |

Suggested order: **P0 immediately** (free, registered, hardens the fix), then **E1 → E2 →
E4** as the next registered block, with E3 in parallel on the cluster (it shares no pools
with the others). E5 only if E4's enumeration audit comes back clean enough to trust the
approach on crowd-sourced sets. Once P0 lands, paper D's Table 7 and its N=2 caveats get
updated and the paper is realistically submission-ready — that decision point is Sri's.

## Registered-style predictions to commit before running (draft)

- **P-N1 (E1):** at k>1, the worked-solution reference's inflation delta vs blind is at
  least as large as the bare-answer reference's (more matching surface ⇒ ≥ anchoring).
- **P-N2 (E2, H-METHOD):** on unique-answer math with a worked reference, the
  method-matching margin among *correct* candidates has a CI containing zero, and
  referenced best-of-64 inflation is not above blind. (Sri's hypothesis: the null holds.)
- **P-N3 (E3a):** same prediction as P-N2 for same-behavior different-implementation code.
- **P-N4 (E3b/E4):** the k=1-to-k>1 step replicates on CodeContests multi-output problems
  and on MACE (both judges, step CI excluding zero).

## Benchmark catalog (why each fits or doesn't)

The requirement is always the pair: **real multiplicity + a validity oracle that isn't the
reference.**

**Found by Sri (2026-08-25):**
- **MACE** (arXiv 2602.07842, *Evaluating and Calibrating LLM Confidence on Questions with
  Multiple Correct Answers*): 12,000 factual questions, six domains, answer cardinality
  fixed by construction at 1/2/4/6 — a natural-language twin of our synthetic k-grid, with
  Wikidata-grounded enumerated answer sets (κ=0.94 expert verification). Best off-the-shelf
  fit found so far. Caveat to audit: enumeration completeness (the Ties failure mode).
- **ARC-DA** (arXiv 2102.03315): multi-valid by construction (~2.8 valid answers/question)
  but no exact oracle — valid sets are crowd-sourced and open-textured. Usable only with
  adjudication + label correction; treat as a realism stress test, not a clean measurement.

**Coding (harness nearly ready):** HumanEval / MBPP / EvalPlus (unit-test oracle, canonical
solution as reference); **CodeContests** (100+ accepted human solutions per problem — real
reference diversity for rotation; ~25% of problems accept multiple outputs); LiveCodeBench
(contamination-controlled); SWE-bench (gold patch = one of many valid patches, test-harness
oracle — highest practical impact).

**Security:** Cybench, NYU CTF Bench, CTFTiny, SEC-bench/CyberGym — flag unique (k=1) but
the exploit/patch is massively multi-valid with an execution oracle; LLM-as-judge is
already being used on agent write-ups there, which is exactly where the anchoring warning
applies. (Authorized-benchmark settings only.)

**Structured:** Text-to-SQL (Spider, BIRD): many equivalent queries, execution-accuracy
oracle, gold SQL shipped — reference-guided SQL grading is common practice. IFEval-style
constraint following: infinite valid outputs, programmatic checkers.

**Formal math:** Lean (miniF2F, PutnamBench): many distinct proofs per theorem, the kernel
as a perfect oracle, reference proof shipped — the cleanest possible method-multiplicity
domain (every proof of a theorem reaches the "same answer"), and a bridge to VeriBench.

**Surveyed and rejected earlier** (for the record): JudgeBench, LLMBar, RM-Bench — pairwise
one-right-one-wrong, no multiplicity; MT-Bench / Arena / AlpacaEval / HelpSteer2 —
preference labels, no validity oracle; MixEval — objective but single-answer.

## How the queue links to related work

- **P0** answers the judge-generality demand standard in the judge-bias literature (biases
  are judge-specific), converting "consistent with capability but not isolated from it"
  into an actual cross-family claim about the fix.
- **E1/E2** engage the **solution-fixation** line most directly: that work showed judges
  statically penalize valid solutions differing from a worked reference, but never isolated
  the *same-answer-different-method* cell from the *different-answer* cell. E2 is exactly
  that isolation, run dynamically. It also bears on the "judge writes its own reference
  first" practice: if method-anchoring is real, self-generated references are
  contraindicated even on unique-answer tasks.
- **E4 (MACE)** creates a complementarity worth a related-work paragraph in both papers:
  MACE shows *confidence calibration* breaks as the number of correct answers grows; we
  would show *reference-guided judging* breaks along the same axis — answer-multiplicity
  as a general failure dimension for LLM evaluation, a framing neither paper claims alone.
- **E3** imports the pass@k/CodeBLEU tradition (multiplicity defeats match metrics —
  companion B's territory) into the judging-under-selection setting.
- The whole program sits inside the **overoptimization** framework (Gao et al.): our
  contribution there is mapping which evaluator-side "safeguards" reduce exploitability
  and which *increase* it.

## Novelty ledger (honest)

**Not novel, and the paper says so:** the static fixation bias (judges penalize
non-matching valid answers), reference-guided degradation on open-ended tasks, the
documented benefits of references on unique-answer grading, RewardBench-2's Ties
construction, and the overoptimization setting itself.

**Genuinely novel — four claims with no prior claimant found:**
1. **The dynamic inversion**: first measurement of a reference making best-of-n inflation
   *worse than blind*, externally preregistered, twice. Prior work measured static verdict
   accuracy; the safeguard claim rests on the dynamic quantity, and the two can disagree.
2. **The causal mechanism**: anchoring shown by *intervention* (rotate the reference,
   identical text swings ±9.5 of 10), not inferred from error rates — nobody else has the
   within-sample causal design.
3. **The controlled boundary**: harm switching on at exactly k=2 with k fixed per item by
   construction, the step universal across six judges — the literature had direction, not
   a dose-response with a located threshold.
4. **The fix**: blind-then-reveal, preregistered, removing the measured inflation for both
   judges where prompting is a placebo — no prior work offers a protocol-level mitigation
   validated under selection pressure. P0 is what hardens this, the paper's most
   practically valuable claim.

**Where the moat is thinnest:** realism (arithmetic families — E4 fixes), judge count on
the fix (P0 fixes), and the risk of being misread as "fixation bias again" — which is why
the intro leads with the dynamic/static distinction, and why E2, whichever way it lands,
adds a second mechanism-level result nobody else has touched.

## Pipeline reuse map

Everything runs on the existing machinery (see `papers/D-reference-laws/README.md`):
`bon_generate.py` (add `mace`, `codecontests` domains), `bon_oracle.py` / code sandbox /
new MACE membership check, `bon_judge.py` (add `refsol` cond), frozen estimator in
`bon_analysis.py` unchanged, analysis producers follow the `papers/analysis/` +
`MANIFEST.md` convention. Register first, commit pipelines pre-data, deviations by public
amendment.
