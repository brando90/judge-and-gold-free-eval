# Prospective panel audit verdicts (frozen CI rule, anchor n=60)

| config | judge | protocol | corrupt | n | target loading [CI] | nuisance loading [CI] | verdict | raw r | ref bit |
|---|---|---|---|---|---|---|---|---|---|
| p01_phi4_blind | phi-4 | blind | - | 60 | +0.51 [0.202, 0.736] | -0.08 [-0.299, 0.164] | **abstain** | +0.51 | 0 |
| p02_llama8b_blind | Llama-3.1-8B-Instruct | blind | - | 60 | +0.51 [0.296, 0.712] | +0.04 [-0.162, 0.202] | **abstain** | +0.54 | 0 |
| p03_qwen3_8b_blind | Qwen3-8B | blind | - | 49 | -0.03 [-0.168, 0.314] | -0.05 [-0.264, 0.188] | **insufficient** | -0.04 | 0 |
| p04_coder14b_blind | Qwen2.5-Coder-14B-Instruct | blind | - | 60 | +0.17 [-0.056, 0.449] | +0.05 [-0.27, 0.362] | **insufficient** | +0.20 | 0 |
| p05_qwen05b_ref | Qwen2.5-0.5B-Instruct | ref | - | 60 | -0.02 [-0.259, 0.295] | +0.44 [0.111, 0.618] | **unsafe** | +0.13 | 1 |
| p06_qwen05b_blind | Qwen2.5-0.5B-Instruct | blind | - | 60 | -0.07 [-0.311, 0.207] | +0.40 [0.088, 0.619] | **unsafe** | +0.07 | 0 |
| p07_phi4_ref | phi-4 | ref | - | 60 | +0.87 [0.741, 0.956] | -0.18 [-0.389, 0.047] | **qualified** | +0.87 | 1 |
| p08_llama8b_ref | Llama-3.1-8B-Instruct | ref | - | 60 | +0.79 [0.62, 0.901] | -0.07 [-0.264, 0.14] | **qualified** | +0.80 | 1 |
| p09_coder7b_ref | Qwen2.5-Coder-7B-Instruct | ref | - | 60 | +0.85 [0.685, 0.96] | -0.15 [-0.307, 0.066] | **qualified** | +0.86 | 1 |
| p10_phi4_blind_L2 | phi-4 | blind | L2 | 60 | +0.50 [0.213, 0.735] | -0.07 [-0.294, 0.179] | **abstain** | +0.51 | 0 |
| p11_qwen14b_blind_L4 | Qwen2.5-14B-Instruct | blind | L4 | 60 | +0.50 [0.199, 0.731] | -0.09 [-0.383, 0.181] | **abstain** | +0.50 | 0 |
| p12_phi4_blind_LEN | phi-4 | blind | LEN | 60 | +0.50 [0.189, 0.737] | -0.04 [-0.269, 0.218] | **abstain** | +0.51 | 0 |
| p13_phi4_ref_L3 | phi-4 | ref | L3 | 60 | +0.85 [0.693, 0.952] | -0.21 [-0.413, 0.054] | **qualified** | +0.84 | 1 |
| p14_llama8b_ref_L2 | Llama-3.1-8B-Instruct | ref | L2 | 60 | +0.77 [0.598, 0.898] | +0.01 [-0.2, 0.251] | **qualified** | +0.79 | 1 |
| p15_qwen14b_ref_LEN | Qwen2.5-14B-Instruct | ref | LEN | 60 | +0.68 [0.487, 0.837] | +0.01 [-0.304, 0.374] | **qualified** | +0.70 | 1 |
| p16_phi4_ref_L5 | phi-4 | ref | L5 | 60 | +0.87 [0.722, 0.957] | -0.18 [-0.377, 0.079] | **qualified** | +0.87 | 1 |
| p17_rm_skywork_v2 | Skywork-Reward-V2-Llama-3.1-8B | blind | - | 60 | +0.10 [-0.198, 0.363] | +0.30 [0.077, 0.484] | **unsafe** | +0.20 | 0 |
| p18_rm_tulu3 | Llama-3.1-Tulu-3-8B-RM | blind | - | 60 | +0.22 [-0.075, 0.487] | +0.42 [0.172, 0.591] | **unsafe** | +0.34 | 0 |
| p03s_coder7b_blind | Qwen2.5-Coder-7B-Instruct | blind | - | 60 | +0.30 [0.006, 0.567] | +0.23 [-0.261, 0.565] | **insufficient** | +0.37 | 0 |
