# Continuous prediction of BoN-64 outcomes from static audit statistics (post hoc; n=13 configs, 8 unsafe)

## LOO linear prediction (RMSE / R^2)

| predictor set | gap RMSE | gap R2 | regret RMSE | regret R2 |
|---|---|---|---|---|
| mean only | 0.398 | 0 | 0.159 | 0 |
| raw_pearson | 0.388 | +0.05 | 0.131 | +0.32 |
| spearman | 0.366 | +0.15 | 0.110 | +0.53 |
| kendall | 0.346 | +0.24 | 0.108 | +0.54 |
| pairwise_acc | 0.351 | +0.22 | 0.101 | +0.60 |
| auc_vs_correct | 0.321 | +0.35 | 0.113 | +0.49 |
| ref_bit | 0.336 | +0.29 | 0.088 | +0.69 |
| raw+ref | 0.391 | +0.04 | 0.099 | +0.61 |
| sound_partial | 0.357 | +0.20 | 0.134 | +0.29 |
| style_partial | 0.363 | +0.17 | 0.175 | -0.21 |
| both_partials | 0.373 | +0.12 | 0.125 | +0.38 |
| both_partials+ref | 0.375 | +0.11 | 0.116 | +0.47 |

## AUROC for UNSAFE (regret >= 0.25 or excess_gap >= 0.50)

| predictor | AUROC | perm p |
|---|---|---|
| raw | 1.000 | 0.0004 |
| spearman | 1.000 | 0.0012 |
| kendall | 1.000 | 0.0012 |
| pairwise | 0.975 | 0.0004 |
| auc_correct | 1.000 | 0.0006 |
| ref | 1.000 | 0.0006 |
| sound | 1.000 | 0.0002 |
| style | 0.863 | 0.0178 |
| both_partials_loo_linear | 1.000 |  |
| raw+ref_loo_linear | 1.000 |  |

## Spearman with outcomes

| predictor | rho(gap) | p | rho(regret) | p |
|---|---|---|---|---|
| raw | -0.71 | 0.0096 | -0.75 | 0.004 |
| spearman | -0.67 | 0.013 | -0.78 | 0.0024 |
| kendall | -0.70 | 0.011 | -0.74 | 0.0046 |
| pairwise | -0.68 | 0.0134 | -0.76 | 0.0042 |
| auc_correct | -0.77 | 0.002 | -0.72 | 0.0098 |
| ref | -0.72 | 0.0092 | -0.85 | 0.0008 |
| sound | -0.72 | 0.0076 | -0.70 | 0.0098 |
| style | +0.52 | 0.0776 | +0.39 | 0.191 |

## In-sample two-partial fits

{"both_partials_insample_gap": {"intercept": 0.804, "b_sound": -0.844, "b_style": 0.292, "r2": 0.519}, "both_partials_insample_regret": {"intercept": 0.58, "b_sound": -0.785, "b_style": -0.405, "r2": 0.641}}
