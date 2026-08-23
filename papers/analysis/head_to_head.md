# Naive validation vs the audit, as predictors of BoN-64 gaming (math)

| config | n | naive r (raw agreement) | soundness partial | style partial | BoN gap | regret |
|---|---|---|---|---|---|---|
| noref:Qwen2.5-1.5B-Instruct | 53 | +0.18 | -0.00 | +0.51 | 0.88 | 0.448 |
| noref:Qwen2.5-14B-Instruct | 60 | +0.37 | +0.41 | -0.21 | 0.63 | 0.324 |
| noref:Qwen2.5-3B-Instruct | 60 | +0.24 | +0.19 | +0.16 | 0.44 | 0.429 |
| noref:Qwen2.5-7B-Instruct | 60 | +0.33 | +0.32 | -0.02 | 0.8 | 0.324 |
| ref:Qwen2.5-1.5B-Instruct | 56 | +0.55 | +0.51 | +0.10 | 0.16 | 0.01 |
| ref:Qwen2.5-14B-Instruct | 60 | +0.70 | +0.70 | -0.11 | 0.05 | 0.048 |
| ref:Qwen2.5-3B-Instruct | 60 | +0.55 | +0.53 | -0.02 | 0.07 | 0.038 |
| ref:Qwen2.5-7B-Instruct | 60 | +0.66 | +0.66 | -0.12 | 0.18 | 0.019 |
| sabotage:Qwen2.5-14B-Instruct | 60 | +0.45 | +0.38 | +0.24 | 0.61 | 0.324 |
| sabotage:Qwen2.5-7B-Instruct | 60 | +0.34 | +0.28 | +0.17 | 0.13 | 0.4 |
| ref:GPT-5.2 (honest) | 60 | +0.89 | +0.90 | -0.22 | 0.38 | 0.117 |
| sabotage:GPT-5.2 | 60 | +0.35 | +0.20 | +0.59 | 0.85 | 0.133 |
