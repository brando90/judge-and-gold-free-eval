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

Llama-3.1-8B, v3's generator, will not solve these problems. Pilot with the supplied prompt,
scored by the checker rather than by bank membership:

| Model | Checker-valid | Parsed | Median | $/item | 12,096-call generation |
|---|---|---|---|---|---|
| **GPT-4.1-mini** | **6/12** | **12/12** | 16s | **$0.0032** | **$39** |
| GPT-5-mini | 6/10 | 10/12 | 30s | $0.0127 | $153 |
| GPT-4.1 | 5/12 | 12/12 | 14s | $0.0119 | $144 |
| Haiku 4.5 | 5/11 | 11/12 | 9s | $0.0124 | $150 |
| Sonnet 5 | 10/11 | 11/12 (1 truncated at 32k) | 35s | $0.2049 | $2,478 |

**Decision: GPT-4.1-mini as the bulk generator.** Highest checker-valid rate of the cheap models,
the only one tied for fully parseable output, and a quarter to a thirtieth of the cost of every
alternative. Generation for the full pool is about $39 against Sonnet 5's ~$1,451.

**Sonnet 5 is the most accurate and the most expensive.** At a 32k cap (and with streaming, which
the SDK requires for long requests) it reaches 10/11 valid, failing only the Ramsey colouring and
still truncating one item. But at $0.2049/item the full pool costs about $2,478 against the mini's
$39 — 64x — because it narrates every constraint check before answering.

**A design reason not to pick the strongest generator.** The analyses need candidate pools that mix
valid and invalid answers: best-of-n selection and valid-versus-invalid discrimination are both
undefined if every candidate is correct. A generator near 50% is more useful here than one near
100%. Sonnet 5 is still worth a *second*, smaller pool, since `experiment_1.md` analyses generators
separately, and a strong-generator pool tests whether the reference effect survives when most
candidates are right.

**Anthropic access is restored.** `ANTHROPIC_API_KEY_1` and `_2` work; `_3` is invalid; the original
`ANTHROPIC_API_KEY` is the one capped until 2026-10-01. The harness now prefers the numbered keys.
Claude models are therefore available as judges as well, which matters because Sonnet 5 and Opus 5
carry v3's strongest P3 evidence (the 2-of-843 second-blind-call control).

**Three harness bugs found and fixed while piloting, all mine:**
* A 4,096-token cap truncated replies mid-answer; now 16k by default, and `truncated` is recorded so
  a capped reply is never scored as a wrong answer.
* The answer extractor required `\boxed{}` *inside* `<FINAL_ANSWER>`; Haiku omits the box on every
  reply, so 12 of 12 correct answers scored as unparseable. The box is now optional.
* Only the last 400 characters of each reply were stored, so long constructions pushed the answer
  tag out of the saved text and could not be recovered on re-score. Now 4,000.

Scoring is by `v4_checkers.py`, not bank membership: a valid-but-unbanked answer would otherwise
count as wrong, which is the very error this paper is about.

**Blocker:** the Anthropic key is out of budget until **2026-10-01**, after the ICLR deadline.
Until that limit is raised, Anthropic models cannot be candidate generators *or* judges.

**Selection rule:** pick the cheapest model that produces parseable answers and clears a solve
floor on the checkable items, measured by the checker rather than by bank match. Report the
chosen model's solve rate per source, since `mathconstruct` is much harder than `math_constraint`.

---

## 3b. Cluster status (skampere), checked 2026-09-16

All three hosts are reachable as `srivatsavad@` (the CSID, per the lab cluster guide — the earlier
`Permission denied` on skampere3 was just the default username). vLLM 0.19.0 with torch 2.10 is
already installed in `~/miniconda3/envs/rrv` on skampere1 and skampere2.

| Host | GPUs | Idle now | `rrv` env | `/lfs` free |
|---|---|---|---|---|
| skampere1 | 8x A100-80GB | #1, #3, #6 | yes (vLLM 0.19.0, torch 2.10, transformers 4.57.6) | 1.1T (98% used) |
| skampere2 | 8x H200-143GB | #4, #5 | yes (vLLM 0.19.0, torch 2.10, transformers 4.57.2) | 689G (99% used) |
| skampere3 | 8x B200-183GB | #4, #5, #6 | **no** — needs creating | 141G (100% used) |

**Weights go on DFS, not LFS.** `/lfs` is 98-100% full on all three hosts, but
`/dfs/scratch0/srivatsavad` has **11T free** and is shared across nodes, so a model downloaded once
is visible everywhere. The lab guide calls DFS slower than LFS, so the pattern is: download to DFS,
and if serving throughput suffers, copy the active model to that host's `/lfs`.

This removes the disk blocker. Feasible now: Qwen3-32B (~65G), Mistral-Small-3.1-24B (~48G),
Llama-3.3-70B (~140G). **DeepSeek-V3.1 (600B+ MoE, ~700G) is still impractical** and needs
substituting — suggested: DeepSeek-R1-Distill-Qwen-32B, or the already-cached Qwen3-14B.

**In flight:** Qwen3-32B downloading to `/dfs/scratch0/srivatsavad/hf` on skampere1 (pid 3777158,
log at `/dfs/scratch0/srivatsavad/logs/qwen3_32b_dl.log`).

**Long runs need Kerberos care.** The ticket expires the same day it is issued, so judging runs go
through `/afs/cs/software/bin/krbtmux` plus `reauth`, per the lab guide. Max 3 GPUs concurrently.

**Scope confirmed: narrow first, expand with time and confidence.** Start with E1 (C0/C1 rotation)
and E3 (full answer list) on the 189 checkable items, two judge models, two methods (M0 brief
justification and M3 solve-then-grade — the pair that differs most mechanically). Expand only once
the effect is shown to reproduce here.

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
