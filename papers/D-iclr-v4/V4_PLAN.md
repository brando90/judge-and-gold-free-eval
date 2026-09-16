# v4 plan: MathRefBench, and what `experiment_1.md` adds to v3

Status: draft for review. Nothing here is registered yet. v3 is frozen at `4907d40`
(tag `paper-d-iclr-v3`); this directory is a copy and v3 is not touched.

---

## 1. What is new in the inputs

### 1.1 The benchmark

`datasets/final_mathrefbench.jsonl` — 324 items, built from two sources:

| Source | Items | Labels | Answer style |
|---|---|---|---|
| `math_constraint` | 257 | `SAT` | constructions: permutations, graphs, grids, sequences |
| `mathconstruct` | 67 | `Find Any` (51), `Find Infinitely Many` (16) | competition answers, often huge integers |

Each item stores `problem`, `formatting_instructions`, `original_parameters`, and a
`solutions` bank. Each solution carries `answer`, `normalized_answer_id` (the canonical
answer class), `rendered_answer`, `worked_solution`, and `origin`.

Distinct answer classes per item: 7 for 306 items, 2–6 for the other 18.

**The bank is a sample, not the full answer set.** 1,874 of 2,198 solutions have
`origin: generated`, and 306 of 324 items carry exactly 7 — a cap, not a count. Scoring a
candidate by bank membership would therefore mark a correct-but-unbanked answer wrong, which
is precisely the error this paper is about. This is the single most important design fact.

### 1.2 The programmatic checker (new, and what makes v4 cleaner than v3)

`experiments/tfa-vs-judge/scripts/v4_checkers.py` decides validity from each problem's own
definition plus `original_parameters`, with no bank and no judge.

* **Coverage:** 189 of 324 items, across 16 families — n-queens, all-interval series, Langford,
  Costas, Golomb, knight's tour, De Bruijn, quasigroup, orthogonal Latin squares, Legendre
  pairs, antimagic squares, Ramsey colourings, social golfers, number partitioning, BIBD, and
  `pysms` graph-property constructions (95 items: degree, edge count, clique, independent set,
  chromatic number, girth, connectivity).
* **Validation:** all 1,279 checkable bank solutions verify, zero failures. Two checkers were
  wrong on first writing (`number` required equal sums of squares; `hadamard` used the wrong
  correlation constant) and were fixed against the problem statements.
* **Not checkable (135 items):** all 67 `mathconstruct` items, plus `math_constraint` families
  whose generated instance is not in `original_parameters` (`magic`, `max_clique`, `graph`
  colouring, `latin` completion, `graceful`, `low` autocorrelation, `non`-transitive dice).
  These stay bank-scored and must carry the sampling caveat.

**Consequence for the design.** Restrict the primary analysis to the 189 checkable items. That
restores the property v3's constructed pools had and v3's MACE questions lacked: "correct but
different from every reference shown" is decidable in code. Report the other 135 separately.

---

## 2. What `experiment_1.md` shares with v3, and what it adds

### 2.1 Already established in v3 (so not a new claim)

| `experiment_1.md` element | v3 equivalent | v3 result |
|---|---|---|
| C1 vs C0, one reference vs none | referenced vs blind | the core of P1–P3 |
| reference rotation, preference reversal | the swap test (P1) | identical text moves 3–5 of 10 points |
| grading valid-vs-invalid separation | grading AUROC (P2) | falls 0.06–0.16 factual, 0.17–0.27 arithmetic |
| solve-then-grade (M3) | R25/R26 solve-first prompt | smallest grading loss of the correctness prompts |
| structured verification (M2) | R25 verify-first | shortfall 0.5–6 points |
| best-of-n selection | best-of-64 accuracy | selection less exposed than grading |
| "multiple valid answers" instruction | the full-credit sentence | cuts Sonnet 5's false rejections 36 → 18 points |

### 2.2 Genuinely new

1. **C2, the two-reference dose.** v3 only ever showed one reference or a full list. C2 asks
   whether two references anchor on both classes, teach multiplicity, or confuse the judge —
   with a matched comparison `C2(a,b) − [C1(a)+C1(b)]/2` that holds reference identity fixed
   and changes only the count. v3 has nothing equivalent; the closest is the min(3,k) arm of the
   k-pool mitigations, which was never analysed this way.
2. **A 0–3 ordinal rubric** instead of v3's 0–10 score. Cheaper to defend, and it makes ties
   explicit rather than hiding them in a continuous score.
3. **Full best-of-n curves** at n ∈ {1,2,4,8,16,32,64} from one judging pass, rather than v3's
   single best-of-64 endpoint.
4. **A 4 × 4 judge grid** (four methods × four models) reported cell by cell, where v3 reported
   a handful of judge–prompt pairs.
5. **An explicit NA abstention level**, reported separately rather than folded into a low score.
6. **Frozen reference assignments** (seed `20260902`, item-level draws, saved manifest) reused
   across every generator, model, method and retry.

### 2.3 Where I would push back

* **`M_q = min(3, k_q)` with k_q = 7 for 306 items** means 3 of 7 classes are shown and 4 are
  never exposed. Good for the unexposed-class analysis, but it means "the full answer list" —
  v3's strongest fix — is not tested here. I would add a C_all arm on the checkable items, since
  the checker makes it cheap and it is the one intervention v3 showed actually works.
* **Judge models.** `judge_methodology.md` names Qwen3-32B, Llama-3.3-70B, Mistral-Small-3.1-24B
  and DeepSeek-V3.1. None runs locally on this machine (v3's open judges were ≤14B on a 16 GB
  Mac), so these need cluster GPUs or a hosted API. That is a scheduling question, not a design
  one, but it gates the whole grid.
* **Candidate generators.** `judge_methodology.md` lists Qwen3-14B, Ministral-3-14B and Sonnet-4.
  See §3: Anthropic is currently unavailable.

---

## 3. Generator choice (in progress)

Llama-3.1-8B, v3's generator, will not solve these problems. Pilot on 10 stratified items with
the supplied prompt:

| Model | Same 12 checkable items | Cost/item | Median |
|---|---|---|---|
| GPT-4.1-mini | **6/12 checker-valid**, 12/12 parseable, 0 truncated | **$0.0032** | 16s |
| GPT-4.1 | 5/12 checker-valid, 12/12 parseable, 0 truncated | $0.0119 | 14s |
| GPT-5-mini | running (141s median in round 1: slow) | ~$0.018 | 141s |
| Haiku 4.5, Sonnet 5 | **blocked** — Anthropic workspace limit, resets 2026-10-01 | — | — |

**Leading choice: GPT-4.1-mini** — same solve rate as GPT-4.1 at about a quarter of the cost and
comparable latency. Confirm once GPT-5-mini reports; if it is much stronger it may still lose on
latency, since 64 candidates x 189 items is 12,096 calls.

Two scoring bugs were found and fixed while piloting, both mine:
* Bank comparison stripped only whitespace, so `0,4,1,3,2` and `[0, 4, 1, 3, 2]` counted as
  different answers; it was scoring formatting, not correctness.
* The first sample drew from all 324 items, so only 3 of 10 were checkable. Sampling is now
  restricted to the 189 checkable items (`--checkable-only`), which is what makes the table above
  decisive where the first round was not.

The first round also measured the harness rather than the models: 4,096 tokens truncated 2 of 10
replies and three answers came back as LaTeX arrays or `\ldots`. The cap is now 16k and the prompt
demands a literal flat list. After that fix, parseable answers went from 8/10 to 12/12.

**Blocker:** the Anthropic key is out of budget until **2026-10-01**, after the ICLR deadline.
Until that limit is raised, Anthropic models cannot be candidate generators *or* judges.

The first pilot measured the harness as much as the models, so it was fixed before re-running:
16k token cap, an explicit instruction that the boxed answer be a literal flat list (no LaTeX
environments, no ellipses), and a `truncated` flag so a capped reply is never scored as wrong.

**Selection rule:** pick the cheapest model that produces parseable answers and clears a solve
floor on the checkable items, measured by the checker rather than by bank match. Report the
chosen model's solve rate per source, since `mathconstruct` is much harder than `math_constraint`.

---

## 4. Proposed experiment set for v4

Numbers to be fixed at registration; this is the shape, not the commitment.

* **E1 — C0/C1 rotation on checkable items.** 189 items × 64 candidates, judged blind and under
  each of 3 rotated references. Primary endpoint: change in the share of *checker-valid* winners
  at best-of-n, plus the paired grade change split by candidate class (matches the shown
  reference / matches another valid class / invalid). This is v3's P1+P2+P3 on a clean oracle.
* **E2 — C2 two-reference dose.** The matched comparison above, on items with k ≥ 3 so at least
  one class stays unexposed.
* **E3 — C_all.** The full answer bank as the reference block, the v3 fix, now measurable against
  a checker rather than against the list that defines correctness. This addresses the AC's
  "partly by construction" objection to v3 §7 directly.
* **E4 — Judge grid.** Methods M0–M3 × available models, every cell reported.
* **E5 — Unbanked-answer audit.** The checker's unique contribution: how often does a judge
  reject a candidate the checker says is valid but that appears in no reference and in no bank
  entry? v3 could not ask this question.

## 5. Open questions for you

1. **Anthropic limit** — can the workspace cap be raised before the deadline? It decides whether
   Claude models appear in v4 at all.
2. **Judge models** — the four named open models need GPUs or a hosted endpoint. Cluster, or
   substitute hosted models?
3. **Scope** — is v4 a new paper, or v3 plus a MathRefBench section? The experiment set above is
   a paper's worth of work; a section would be E1 and E3 only.
