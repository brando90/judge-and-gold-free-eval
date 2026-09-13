# External NeurIPS-AC review, round 2, of `A-certificate/Agreement_Is_Not_A_Certificate.tex` (2026-09-12)

Score: **6/10, weak accept / borderline accept** (up from 5). Sub-scores: technical quality 3.5/4,
significance 3.5/4, novelty 3.5/4, empirical strength 3/4, clarity 3.5-4/4. Path to 7: one
successful preregistered corruption panel plus the already-built split-rater annotation.

## Judged fixed
Marginal-agreement baselines (five metrics); thresholds and boundary false pass (continuous
loadings separated from rule, CI abstention); power/sample-size (calibrated simulation); DPO
overclaim; companion work doing conceptual lifting (Figure 1 labeled); central claim reframed as
construct validity. The +0.82 -> +0.32 correction "actually makes me trust the paper more."
Judged partially fixed: collinearity (prospective panel added); rater halo (cross-rater swap
reassuring, full split-rater still "awaiting annotators").

## Central remaining issue
The prospective panel failed its manipulation: 5 of 7 corrupt instructions did nothing, and the 2
that moved did not move toward style. The panel therefore tests weakness, not the distinctive
capable-but-corrupt regime; raw correlation AUC 1.000 > reference bit 0.958 > nuisance 0.845.

## Requested
1. Prospective panel whose corruption must pass a frozen manipulation check on data disjoint from
   audit and pressure sets, conditioned only on "did the treatment change the judge in the
   intended direction" plus evidence it loads on presentation rather than noise; use 3-4
   frontier judges, honest and corrupt twins, behaviorally verifiable mechanisms (style,
   confidence, reference-similarity, verbosity). 4-6 genuinely style-loaded new judges that then
   inflate would outweigh twenty more weak judges.
2. Run the fully split-rater annotation (pool A soundness only, pool B style only).
3. Keep Section 5; sharpen that it validated "target-validity measurement prevents false
   certification of weak judges," not "nuisance loading separates capable-corrupt from
   capable-honest."
4. Split the panel table into A predeclared deployment decisions (qualified->safe 7/7,
   unsafe/insufficient->unsafe 7/7, abstain->unsafe 5/5) and B exploratory ranking (target 1.00,
   raw 1.00, ref .958, nuisance .845), explaining P-N3 was falsified because the manipulation failed.
5. Conclusion: replace "where substance and style travel together" with "raw agreement measures
   performance on the observed unoptimized distribution and does not identify which correlated
   attributes drive the score"; replace "the one property that decides a judge's fate" with
   risk depending on both target and nuisance validity (weak: target~0; capable-corrupt: target>0,
   nuisance>>0; good: target>>0, nuisance~0).
6. Promote the simulation: the false pass reveals that finite-sample point thresholds cannot
   support certification near a boundary, so uncertainty-aware abstention is structurally necessary.
