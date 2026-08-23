# Canonical validity numbers (anchor n=60, single annotator, blind)

| signal | n | Pearson r [95% CI] | Spearman rho | partial r (|style) | within-correct r (n) |
|---|---|---|---|---|---|
| tfa | 60 | -0.16 [-0.46,+0.13] | -0.12 | -0.14 | +0.21 (48) |
| logprob | 42 | -0.27 [-0.54,+0.04] | -0.18 | -0.27 | +0.15 (32) |
| tfidf | 60 | -0.08 [-0.33,+0.18] | -0.09 | -0.17 | +0.16 (48) |
| u1 | 60 | -0.33 [-0.58,-0.12] | -0.29 | -0.46 | +0.06 (48) |
| embed | 60 | +0.14 [-0.08,+0.40] | +0.13 | +0.15 | -0.01 (48) |
| pv_v0 | 60 | +0.54 [+0.24,+0.77] | +0.47 | +0.54 | +0.03 (48) |
| pv_v25 | 60 | +0.68 [+0.48,+0.85] | +0.32 | +0.67 | -0.02 (48) |
| pv_v5 | 60 | +0.76 [+0.56,+0.91] | +0.48 | +0.73 | +0.02 (48) |
| pv_v75 | 60 | +0.78 [+0.60,+0.91] | +0.46 | +0.76 | +0.19 (48) |
| pv_mean | 60 | +0.79 [+0.61,+0.92] | +0.41 | +0.76 | +0.07 (48) |
| judge_ref | 60 | +0.89 [+0.76,+0.97] | +0.43 | +0.90 | -0.14 (48) |
| critic_gpt | 60 | +0.91 [+0.77,+0.98] | +0.61 | +0.91 | +0.17 (48) |
| critic_opus | 60 | +0.88 [+0.74,+0.97] | +0.54 | +0.87 | +0.03 (48) |

All numbers vs human soundness. Style partials (judge signals): judge_ref=-0.22, critic_gpt=-0.10, critic_opus=-0.11

Difficulty-controlled partials (| pv_v0): pv_v25_partial_v0=+0.51, pv_v5_partial_v0=+0.64, pv_v75_partial_v0=+0.69, pv_mean_partial_v0=+0.69
