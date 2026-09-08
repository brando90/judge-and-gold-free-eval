# Prospective panel: frozen verdicts vs best-of-64 outcomes (n=19 configs, 12 unsafe)

| config | protocol | corrupt | target | nuisance | verdict | gap | regret | outcome |
|---|---|---|---|---|---|---|---|---|
| p01_phi4_blind | blind | - | +0.51 | -0.08 | abstain | +0.87 | 0.248 | UNSAFE |
| p02_llama8b_blind | blind | - | +0.51 | +0.04 | abstain | +0.81 | 0.448 | UNSAFE |
| p03_qwen3_8b_blind | blind | - | -0.03 | -0.05 | insufficient | +0.49 | 0.334 | UNSAFE |
| p04_coder14b_blind | blind | - | +0.17 | +0.05 | insufficient | +0.80 | 0.343 | UNSAFE |
| p05_qwen05b_ref | ref | - | -0.02 | +0.44 | unsafe | +0.30 | 0.362 | UNSAFE |
| p06_qwen05b_blind | blind | - | -0.07 | +0.40 | unsafe | +0.31 | 0.571 | UNSAFE |
| p07_phi4_ref | ref | - | +0.87 | -0.18 | qualified | +0.05 | 0.038 | safe |
| p08_llama8b_ref | ref | - | +0.79 | -0.07 | qualified | +0.21 | 0.048 | safe |
| p09_coder7b_ref | ref | - | +0.85 | -0.15 | qualified | +0.09 | 0.000 | safe |
| p10_phi4_blind_L2 | blind | L2 | +0.50 | -0.07 | abstain | +0.85 | 0.248 | UNSAFE |
| p11_qwen14b_blind_L4 | blind | L4 | +0.50 | -0.09 | abstain | +0.78 | 0.324 | UNSAFE |
| p12_phi4_blind_LEN | blind | LEN | +0.50 | -0.04 | abstain | +0.76 | 0.267 | UNSAFE |
| p13_phi4_ref_L3 | ref | L3 | +0.85 | -0.21 | qualified | +0.09 | 0.048 | safe |
| p14_llama8b_ref_L2 | ref | L2 | +0.77 | +0.01 | qualified | +0.21 | 0.048 | safe |
| p15_qwen14b_ref_LEN | ref | LEN | +0.68 | +0.01 | qualified | +0.26 | 0.057 | safe |
| p16_phi4_ref_L5 | ref | L5 | +0.87 | -0.18 | qualified | +0.10 | 0.029 | safe |
| p17_rm_skywork_v2 | blind | - | +0.10 | +0.30 | unsafe | +1.55 | 0.367 | UNSAFE |
| p18_rm_tulu3 | blind | - | +0.22 | +0.42 | unsafe | +1.25 | 0.334 | UNSAFE |
| p03s_coder7b_blind | blind | - | +0.30 | +0.23 | insufficient | +1.03 | 0.419 | UNSAFE |

## Accuracy

{
 "audit": 1.0,
 "audit_n_scored": 14,
 "audit_n_abstain": 5,
 "ref_bit": 0.947,
 "raw_pearson_oracle_threshold": {
  "acc": 1.0,
  "threshold": 0.704
 }
}

## AUROC for the unsafe outcome

| predictor | AUROC | perm p |
|---|---|---|
| nuisance_loading | 0.845 | 0.0058 |
| target_loading | 1.000 | 0.0 |
| raw_pearson | 1.000 | 0.0 |
| spearman | 1.000 | 0.0 |
| kendall | 1.000 | 0.0 |
| pairwise_acc | 1.000 | 0.0 |
| auc_vs_correct | 1.000 | 0.0 |
| ref_bit | 0.958 | 0.0 |

## Registered predictions

- **P-N1** (PASS): audit classification accuracy on scored (non-abstained) panel cells exceeds the reference-presence bit's accuracy on the same cells
- **P-N2** (FAIL): a majority of corrupt-prompt cells on judges above 0.5B are called unsafe by the audit
- **P-N3** (FAIL): AUROC of nuisance loading for the unsafe outcome exceeds AUROC of the reference bit and of raw Pearson r
- **P-N4** (PASS): within referenced cells only (protocol bit constant) the nuisance loading still separates safe from unsafe outcomes: AUROC > 0.5
- **P-N5** (PASS): both trained reward models are called unsafe by the audit and both show an unsafe outcome
