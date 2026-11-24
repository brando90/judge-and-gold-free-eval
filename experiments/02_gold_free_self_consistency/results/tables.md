## E1 within-problem AUROC vs the gold bit (176-problem judge subset, 95% CI over problems)

| scorer | needs gold | needs judge | AUROC | 95% CI | pooled AUROC |
|---|---|---|---|---|---|
| SC (M) | no | no | 0.956 | [0.937, 0.973] | 0.947 |
| Qwen-1.5B noref | no | yes | 0.713 | [0.692, 0.734] | 0.710 |
| Qwen-1.5B ref | yes | yes | 0.938 | [0.923, 0.951] | 0.934 |
| Qwen-3B noref | no | yes | 0.682 | [0.657, 0.708] | 0.685 |
| Qwen-3B ref | yes | yes | 0.920 | [0.906, 0.934] | 0.903 |
| Qwen-7B noref | no | yes | 0.754 | [0.733, 0.775] | 0.754 |
| Qwen-7B ref | yes | yes | 0.921 | [0.905, 0.935] | 0.914 |
| Qwen-14B noref | no | yes | 0.767 | [0.747, 0.787] | 0.773 |
| Qwen-14B ref | yes | yes | 0.915 | [0.897, 0.930] | 0.913 |

## E2 selection accuracy (argmax score; 176 problems)

| scorer | accuracy | 95% CI |
|---|---|---|
| SC (M) | 0.949 | [0.915, 0.977] |
| Qwen-1.5B noref | 0.619 | [0.545, 0.688] |
| Qwen-1.5B ref | 0.932 | [0.892, 0.966] |
| Qwen-3B noref | 0.631 | [0.562, 0.699] |
| Qwen-3B ref | 0.938 | [0.898, 0.972] |
| Qwen-7B noref | 0.750 | [0.682, 0.812] |
| Qwen-7B ref | 0.869 | [0.812, 0.920] |
| Qwen-14B noref | 0.761 | [0.699, 0.824] |
| Qwen-14B ref | 0.869 | [0.818, 0.915] |
| mean pass@1 (random sample) | 0.495 | |
| pass@4 / pass@16 / pass@64 (oracle) | 0.888 / 0.998 / 1.000 | |
