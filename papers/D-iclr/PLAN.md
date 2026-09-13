# Presentation plan for the ICLR version (from The_Reference_Is_Not_An_Answer_Key, 2026-09-13)

Model paper: Schaeffer, Miranda & Koyejo, "Are Emergent Abilities of LLMs a Mirage?" (NeurIPS 2023 outstanding paper).
What we copy from it: one alternative explanation stated on page 1; a schematic figure that makes the explanation
visual before any data; numbered predictions derived from the explanation; each results section opens with the
prediction in bold and closes with whether it held; few, large figures with one colour grammar; a short
discussion that says what the paper does *not* claim.

## The one idea
A reference on a question with several correct answers is not an answer key; it is one sample from the set of
correct answers, and judges grade agreement with that sample.

## Predictions (and where each is tested)
- **P1 The score follows the reference.** Rotation test on byte-identical text (registered, 12/12 cells); survives
  restricting to answers the judge accepted blind; mechanism: the reference must state its answer (masking suite 6/6).
- **P2 The damage appears exactly when a second correct answer exists.** k = 1 vs k > 1 step (6 judges, synthetic grid;
  OSF k-pool; MACE inversion: reference helps at k = 1, hurts at k > 1); unique-answer MATH-500: reference helps
  (+29 to +31 points). Grading: correct answers that differ from the reference become hard to tell from wrong ones
  (AUROC and false rejections), robust to how answers are read.
- **P3 It survives what would cure ignorance.** Answers the judge certified blind; a frontier judge (Sonnet 5 rotation,
  grading with wrong answers); reasoning judges (arithmetic effect removed, factual effect persists); instructions
  (capability-gated, partial at the frontier).

## What it costs and what helps (Section 6)
- Selection: the OSF endpoint (+1.19 SD inflation) holds; accuracy losses are smaller once answers written outside
  \boxed{} are credited (clear only for Qwen2.5-7B); MACE shows no loss.
- Scope: a canonical program does not anchor (MBPP, falsified registered prediction); answer-structure continuum
  attenuates scalar -> pair -> JSON -> program.
- Mitigations: blind-then-reveal removes inflation (OSF) and its active ingredient is the displayed blind score;
  the max(blind, referenced) rule protects accuracy at the same cost; validity gate backfires for one judge.

## Reliability corrections relative to the source draft (keep these; reviewers found each)
1. The "82.5% vs 19.6%" frontier result came from an excluded command-line run whose context included commit
   messages naming the hypothesis. Not used; replaced by the clean Sonnet 5 API/CLI results.
2. "+9.5 points" is from the exploratory Ties pool (incomplete checker, saturating 1.5B judge). Headline rotation
   numbers come from the registered exact-oracle replication, exact scorer.
3. Selection-accuracy and "selection collapses onto the key" readouts depend on a checker that counts unboxed
   answers wrong; report them with format-lenient labels.
4. Training (DPO wedge): protected and blind arms failed their gates and the reference arm did not copy the key;
   report as a limitation, not a headline.
5. Legacy "10"-token scorer: use exact-scorer values for Qwen/gemma where they exist.

## Layout (9 pages)
- p1: title, abstract, **Figure 1 concept + method diagram** (question with two correct answers; rotation test;
  what the answer-key reading predicts vs. what judges do, with measured bars).
- p2: introduction; contributions; **Table 1 predictions -> tests -> results** (all main results at a glance).
- p3: setup (tasks, judges, three measurements) and **Figure 2 main results** (rotation + grading + k boundary).
- p4-7: P1, P2, P3 sections; reasoning figure; cost and mitigations.
- p8-9: related work, limitations, conclusion. Everything else in the appendix with the full ledger.
