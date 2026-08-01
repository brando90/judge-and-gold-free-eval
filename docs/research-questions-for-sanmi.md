# Judge-free evaluation: which question is worth going after?

Our TFA study is essentially done. A cheap, reference-anchored signal ranks
models well but cannot grade an individual solution, and we can prove why: 89 to
96 percent of the per-item score is reference nuisance, not competence. The
signal tracks agreement with the reference's style, not reasoning quality.

Five questions follow from that. Each is a different bet on what the finding
generalizes to. Listed in no particular order.

### Is scalable oversight bounded by a scaling law?

Chart oversight reliability against solver capability, not accuracy at parity. In
a solver-versus-overseer setup, whose method degrades slowest as the solver
outgrows the overseer and is optimized against it? The output is a curve, not a
single score.

### Do all cheap evaluators measure surface agreement, not quality?

Is the competence-versus-nuisance decomposition we found for TFA a universal
property of automatic evaluation, LLM judges and similarity metrics included?

### Is verifying quality fundamentally easier than generating it?

Or does the generation-versus-verification gap hold only for correctness, not
for quality, as our item-level null already suggests?

### Can an evaluator be trusted under optimization pressure?

Which evaluation signals survive being trained against, and can we predict in
advance which ones get gamed?

### Can quality be measured with no reference at all?

Where no gold answer exists (open-ended writing, research, agents), is there any
cheap signal that tracks quality, or is human judgment the irreducible floor?
