# Paper D artifact manifest

Every number quoted in Paper D ("When the Answer Key Backfires") traces to one of the
artifacts below, each regenerated end to end by its named committed producer. Producers
marked **frozen pre-run** were committed before the data they analyze existed; those marked
**post hoc** were written after a review round, from score files already on disk.
Run producers from `experiments/tfa-vs-judge/`.

## Registered analyses (frozen pre-run)

| Artifact | Producer | Registration | Feeds |
|---|---|---|---|
| `repl_results.json` | `repl_analysis.py` | external, osf.io/ym5x9, pre-generation | replication table (paper Table 2), abstract E1, P-R1/P-R2/P-R3 |
| `mitigation_results.json` | `mitigation_analysis.py` | external, osf.io/qugbd, pre-generation | k-stratified mitigation table (Table 7), P-M1/P-M2/P-M3 levels |
| `synthk_results.json` | `synthk_analysis.py` | git-committed pre-generation | synthetic grid (Tables 4-5 region), P-S1..P-S5 scoring |
| `ties_fullset.json`, `ties_inband.json`, `ties_paired.json`, `ties_pooled_delta.json`, `ties_regret_cis.json`, `ties_collapse_conditional.json` | `ties_dynamics.py` | git-committed (P-T1/P-T3); population + pooled estimator post hoc, disclosed | exploratory Ties section (Table 8 region) |
| `ties_rot_controls.json` | `ties_rot_controls.py` | rotation addendum (P-T2r), pre-re-judging | rotation table (Table 3), anchoring figure |
| `ties_p2_margin.json` | `ties_p2_margin.py` | git-committed (P-T2) | original-arm margins |

## Registered analyses, internal-only registration (git commit precedes the run; no external post — registration hold)

| Artifact | Producer | Registered | Feeds |
|---|---|---|---|
| `exploit_dose.json` | `exploit_dose.py` | commit `36efc6b`, 2026-08-26, pre-analysis | composition dose-response (paper Section on pool composition, Table on doses); P-E1 falsified in reverse, P-E2 confirmed |
| `distance_gradient.json` | `distance_gradient.py` | commit `160e638`, 2026-08-26, pre-analysis | distance-gradient paragraph; P-D1/P-D2 formal, estimator disclosed fragile; P-D3 falsified |
| `anchor_vs_weakness.json` | `anchor_vs_weakness.py` | pre-analysis commit, 2026-08-26 | blind-validation filter paragraph in the mechanism section; P-AW1/P-AW2 confirmed |
| (pending) | `simcorr_analysis.py` | commit `f41e358`, pre-data | similarity-vs-correctness 2x2; judging BLOCKED by the failed naturalness audit (see registration.md) |
| `p17_coverage_results.json` | `p17_coverage_analysis.py` | external (Registration 5), harness pre-data | judge-coverage table (tab:coverage); P-X1 not confirmed, P-X2 confirmed |

## Post-hoc analyses (committed producers, written after review rounds)

| Artifact | Producer | Feeds |
|---|---|---|
| `synthk_paired.json` | `synthk_paired.py` | paired step/level/trend re-analysis (post-hoc table), rotation-arm exact McNemar |
| `mitigation_registered_contrasts.json` | `round6_disclosures.py` | registered P-M contrasts computed directly; M2 validity-multiplier audit |
| `repl_disclosures.json` | `round6_disclosures.py` | boxed compliance, pass-rate attribution, pilot-overlap sensitivity, eligible vs in-band counts |
| `repl_pressure_curve.json` | `round6_disclosures.py` | replication selection-pressure curve |
| `round7_linkage.json` | `round7_linkage.py` | band-matched comparison; per-item margin-to-inflation linkage |
| `round8_followups.json` | `round8_followups.py` | matched-population recompute (n=83); M1 under rising selection pressure; attenuation sweep (its `linkage_sim` is **superseded** by `round9_provenance.json`'s `linkage_power`, which estimates the measurement noise the sweep treated as unidentifiable) |
| `round9_provenance.json` | `round9_provenance.py` | linkage power analysis at data-implied noise (split-half); band-match multiplicity composition; boxed-compliance decomposition; worked example of the inflation estimator |
| `checker_audit.json`, `checker_adjudication.json`, `ties_corrected_delta.json` | committed alongside score files (adjudication via GPT-5.2, reference not shown) | checker audits and label-corrected recompute in the exploratory section |
| `exploit_dose_diag.json` | `exploit_dose_diag.py` | valid-pick/judge-gain/true-gain decomposition behind the lure reading (written after P-E1's falsification) |
| (prints only) | `exploit_dose_attract.py` | fraction of selected invalid samples containing the reference answer text |
| (prints only) | `distance_gradient_robust.py` | median/trimmed/Spearman robustness behind the distance verdict |
| `panel2_mitigation_results.json` | `panel2_mitigation_analysis.py` | the second-panel mitigation grid, `tab:panel2-mitig` (6 judges on MACE, 4 on the replication pool, 5 prompt arms), and `fig_grid_candidate` |

## Notes

- The rotation-arm McNemar collapse tests are produced by `synthk_paired.py` despite that
  script's synthetic-grid name.
- Monte Carlo seeds are fixed in every producer; regenerated bootstrap bounds can move by
  up to about 0.02 relative to frozen registered runs.
- Raw score files live under `experiments/tfa-vs-judge/runs/`; task pools under
  `experiments/tfa-vs-judge/runs/*_tasks.jsonl`.
