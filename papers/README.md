# The papers

Four papers grew out of this repo's experiments. Each lives in its own folder with a
self-contained LaTeX source; **every number in a paper traces to a JSON artifact in
[`analysis/`](analysis/) with a committed producer script** (see
[`analysis/MANIFEST.md`](analysis/MANIFEST.md) for paper D's full artifact-to-producer map).
Reviewers diff paper numbers against the JSONs to the digit — keep it that way.

| Folder | Paper | One-line thesis | Status |
|---|---|---|---|
| [`A-certificate/`](A-certificate/) | *Certify Before You Optimize* | A few dozen blind human labels, read through soundness/style partial correlations, predict which judges get gamed before any optimization runs. | Active draft |
| [`B-reference-matching/`](B-reference-matching/) | *Grading the Answer Key, Not the Student* | Reference-similarity metrics measure the reference's predictability, not the solution; nothing tested beats the free answer-correct bit. | Active draft ([4-page AAAI-27 workshop edition](../paper_latex_and_notes/AAAI_2027_EvalAIScientists_ReferenceMatching/README.md)) |
| [`C-benchmark-bug-miner/`](C-benchmark-bug-miner/) | (parked) | Judged unpublishable in review round 3; kept for the record. | Parked |
| [`D-reference-laws/`](D-reference-laws/) | *When the Answer Key Backfires* | On multi-valid-answer tasks a trusted reference **inflates** best-of-n scores (preregistered); anchoring is causal; blind-then-reveal fixes it. | Most mature — see its [README](D-reference-laws/README.md) for the full experiment runbook |

## Compiling a paper

Every paper compiles the same way (TeX Live; no shell-escape needed):

```bash
cd papers/D-reference-laws        # or A-certificate / B-reference-matching
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

A and B use `\input{sections/...}`; D is a single `main.tex`. D's previous draft (v19), with
the full v7–v19 change-history comment block, is preserved verbatim in
`D-reference-laws/main_v19_backup.tex`.

## Layout

```
papers/
  analysis/          canonical analysis layer: every paper number's JSON + committed producer
                     (MANIFEST.md maps artifact -> producer -> registration status for paper D)
  registrations/     external preregistration texts (osf_drafts.md; Registrations 1-5)
  reviews/           adversarial GPT-5.2 review rounds per paper (the review loop's record)
  share/             share-ready renamed PDFs, Discord blurbs, page-by-page reading guide for D
  A-certificate/  B-reference-matching/  C-benchmark-bug-miner/  D-reference-laws/
```

## House rules (these are load-bearing)

1. **Canonical producers.** Never hand-edit a number into a paper. Regenerate the JSON with
   its producer (run from `experiments/tfa-vs-judge/`), then update the paper from the JSON.
   Monte Carlo seeds are fixed; regenerated bootstrap bounds may drift by up to ~0.02 —
   if you regenerate, re-sync the paper.
2. **Registered vs post hoc.** Producers marked *frozen pre-run* in the manifest were
   committed before their data existed and score the registered predictions; do not modify
   them. New analyses go in new, clearly post-hoc producer scripts, and get a row in the
   paper's prediction ledger.
3. **Registrations first.** Any new confirmatory experiment gets its predictions written in
   `registrations/osf_drafts.md`, posted externally (OSF), and its pipeline script committed
   **before** any data is generated. Deviations are disclosed by public amendment, never
   silently (precedent: the M2 soft-gate amendment, osf.io/kszeu).
4. **Review loop.** Drafts are stress-tested by adversarial cold-reads (see `reviews/`);
   gating findings are fixed before any new claims are added.
