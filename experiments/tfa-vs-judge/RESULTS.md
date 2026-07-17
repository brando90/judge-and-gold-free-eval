# Results — TFA vs. the LLM judge (first run, MATH-500)

**Setup.** Qwen2.5-Instruct capability ladder (0.5B, 1.5B, 3B, 7B, 14B, 32B) on MATH-500 (500 problems).
Per (model, problem) we compute: **TFA** (teacher-forced argmax-match on the gold solution, vLLM),
**boxed correctness** of the model's free-generated solution (Math-Verify), and a **frontier LLM-judge**
reasoning-quality score (`gpt-5.2`, 0–10 rubric on the free-gen trace). Run on skampere1 (A100s).

## E0 — metric correctness (PASS)
vLLM TFA matches the HF ground-truth teacher-forcing **exactly** on argmax and to ~1e-3 on logprob
(`scripts/verify_backends.py`). The TFA implementation is trustworthy.

## E1 — reproduction: TFA ↔ boxed accuracy (CONFIRMED)

| Model | mean-TFA | accuracy | mean-judge (0–10) |
|---|---|---|---|
| 0.5B | 0.762 | 0.266 | 3.35 |
| 1.5B | 0.796 | 0.462 | 5.45 |
| 3B | 0.795 | 0.594 | 6.92 |
| 7B | 0.801 | 0.632 | 7.65 |
| 14B | 0.815 | 0.690 | 8.00 |
| 32B | 0.819 | 0.730 | 8.32 |

- **Model-level ρ(mean-TFA, accuracy) = +0.94** (Pearson 0.96) — reproduces and exceeds the paper's ~0.66.

## E2 — the crux: does TFA track the judge, per response? (NEGATIVE at item level)

**Two levels, opposite answers:**

- **Model level (positive):** ρ(mean-TFA, mean-judge) = **+0.94** (n=6, CI [0.52, 1.00]).
  TFA ranks models the same way a frontier judge does.
- **Item level (negative):** pooled ρ(TFA, judge) = **−0.03**; the decisive
  **partial ρ(TFA, judge | correct) = −0.035, 95% CI [−0.071, +0.001]** — indistinguishable from zero
  (slightly negative). Among correctly-solved problems it is −0.10 (CI [−0.15, −0.05]).
  Sanity: the judge itself is meaningful — ρ(judge, correct) = +0.72.

**Verdict: NEGATIVE.** TFA carries **no per-response reasoning-quality signal** beyond the free boxed-correctness bit.

### Supporting diagnostics (E1 data)
- Item-level ρ(TFA, correct) ≈ 0 (−0.01) both pooled and within every model (−0.02 to −0.12).
- Per-item TFA is confounded by **gold-trace length** (ρ ≈ +0.37): longer, more formulaic gold scores
  higher. Gold length anti-correlates with correctness (ρ ≈ −0.31), so the two effects cancel.
- The **content-token variant** (masking formatting/LaTeX glue — the shortcut control) halves the
  gold-length confound (+0.37 → ~+0.2) but still shows **no** item-level correlation with correctness.
  So the null is not a formatting artifact.

## Takeaway
On MATH, **TFA is a valid judge-free *model-ranking* signal** (ranks models like accuracy and like a
frontier judge, cheaply and deterministically) but **is not a per-response judge replacement** — it has
no item-level correlation with judged reasoning quality. This is the "precise negative" the plan flagged
as a legitimate outcome, and it sharply scopes the contribution: *judge-free leaderboarding, yes;
per-response grading, no.*

## Caveats / next
- Model-level n=6 (wide CI); add more families (Llama, Mistral) and sizes to firm it up.
- TFA is compressed/saturated on MATH (0.76–0.82); harder sets (Putnam-AXIOM) may give more range —
  but the collaborator's weak-model floor concern applies.
- Single judge (`gpt-5.2`); a second family bounds self-preference (the Anthropic key in the provided
  `.env` was rejected as invalid, so cross-family judge is TODO).
- Prompting is raw completion-style (not chat-templated); accuracies are sane but a chat-template pass
  is a cheap robustness check.
