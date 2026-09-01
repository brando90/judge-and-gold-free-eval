# How the best papers are written — practices for this project's drafts

Distilled from studying recent NeurIPS award winners: *Are Emergent Abilities a Mirage?*
(Outstanding Paper 2023 — Schaeffer, Miranda, Koyejo), *Deep RL at the Edge of the Statistical
Precipice* (Outstanding 2021), *MAUVE* (Outstanding 2021), *DPO: Your Language Model is Secretly
a Reward Model* (runner-up 2023), *Privacy Auditing with One (1) Training Run* (Outstanding
2023), plus the 2022 and 2024 slates. These are the standards our story.tex drafts are held to.

## What actually wins

1. **One reframing, statable in a sentence — often in the title.** Winners do not have five
   contributions; they have one insight that reorganizes how the reader sees a familiar thing.
   *"Emergence is a metric artifact." "Your LM is secretly a reward model." "One training run
   suffices."* Ours: *"The reference is not an answer key; it is one sample from the valid set."*
   / *"Raw agreement cannot see what a judge scores; partial correlations can."* / *"Matching
   measures the reference, not the solution."*

2. **Indict or repair a field-wide PRACTICE, not a model.** Precipice went after how everyone
   evaluates deep RL; Mirage went after how everyone measures emergence. The subject is the
   reader's own workflow — that is what makes committees call a paper important. Our papers all
   qualify: reference-guided judging, judge validation by agreement, similarity grading are all
   standard practice.

3. **Prove the conceptual claim with one decisive empirical demonstration, early.** Precipice's
   Atari-100k case study; Mirage's arithmetic curves. The reader must hit a figure or table they
   cannot argue with by page 2. Everything after it is elaboration and defense.

4. **Ship something a practitioner uses tomorrow.** Precipice shipped rliable and the IQM
   recipe; DPO shipped an algorithm; Privacy Auditing shipped a one-run auditor. A diagnosis
   without a usable remedy reads as a workshop paper. Ours ship: the blind-then-reveal ordering
   and the separable-answer boundary (D); the 4–8 hour audit recipe (A); the answer-correct-bit
   rule and reference-perplexity reporting (B). These deserve prominence, not appendices.

5. **Make uncertainty and honesty part of the CONTENT.** Precipice's entire subject is
   statistical honesty; Mirage's force comes from testing its own predictions. Our registered-
   before-data discipline, falsified predictions, and retracted readings are not confessions to
   bury — they are the same virtue the committees rewarded, and belong in the text where they
   bite, stated plainly.

6. **Titles do work.** Every winner's title either states the result, names the reframing, or
   installs the paper's metaphor. Two-part titles where the subtitle restates the title are
   filler. Prefer the half that carries the insight.

7. **The demonstration generalizes, and the paper shows where it stops.** Winners bound their
   claims (Mirage: "we do not claim emergence cannot exist"). A mechanism shown to predict where
   the effect appears AND where it disappears (our code-exemplar result) is the strongest form
   of this and should close the argument, not hide mid-paper.

## Craft rules (apply to every draft)

- Abstract: 5–8 sentences, arc of practice → reframing → evidence → remedy → implication. At
  most three numbers. No CIs, no jargon coined later in the paper.
- Introduction ends with contributions a reader can quote; each maps to a section.
- One number per claim in prose; every CI lives in a table or caption. Tables carry the rigor.
- Figure captions: bold one-sentence takeaway first, mechanics after. A reader flipping through
  figures alone should reconstruct the argument.
- Active voice for results ("The score follows the reference"), no hedged verbs where the CI
  already does the hedging, no "note that", no "interestingly".
- Every section earns its place; if a section only catalogues, give it one organizing sentence
  and compress. Repetition of a claim is a bug, including between abstract, intro and results.
- Limitations preempt the reviewer: name the objection sharply, answer what can be answered,
  concede what cannot. A conceded limitation stated crisply reads as strength.
- Related work positions, never lists: each cited line says what it established and what this
  paper adds to it.
- 14–16 pages compiled including references; main argument complete by ~page 10.

## Project-specific rules

- Numbers verbatim from main.tex / registration.md / papers/analysis — never retyped from
  memory; run the scripted fidelity check before committing.
- Registered-and-falsified predictions reported inline where they bite, with registration
  provenance (external OSF vs internal git) stated once in the intro.
- story.tex never modifies main.tex; a footnote names main.tex as the technical report.
- All three drafts share register and caption conventions so they read as a series.
