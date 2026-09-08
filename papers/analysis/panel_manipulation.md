# Manipulation check for the panel's corrupt-prompt cells (post hoc)

A cell counts as manipulated only if its anchor scores correlate with its honest twin's at r < 0.95.

| cell | honest twin | corrupt | n | r with twin | mean shift | nuisance honest -> corrupt | target honest -> corrupt | manipulated |
|---|---|---|---|---|---|---|---|---|
| p10_phi4_blind_L2 | p01_phi4_blind | L2 | 237 | 0.997 | -0.011 | -0.08 -> -0.07 | +0.51 -> +0.50 | NO |
| p11_qwen14b_blind_L4 | t11_qwen14b_blind_honest | L4 | 242 | 0.933 | +0.152 | +0.01 -> -0.09 | +0.34 -> +0.50 | yes |
| p12_phi4_blind_LEN | p01_phi4_blind | LEN | 237 | 0.986 | -0.038 | -0.08 -> -0.04 | +0.51 -> +0.50 | NO |
| p13_phi4_ref_L3 | p07_phi4_ref | L3 | 237 | 0.997 | +0.016 | -0.18 -> -0.21 | +0.87 -> +0.85 | NO |
| p14_llama8b_ref_L2 | p08_llama8b_ref | L2 | 242 | 0.994 | +0.048 | -0.07 -> +0.01 | +0.79 -> +0.77 | NO |
| p15_qwen14b_ref_LEN | t15_qwen14b_ref_honest | LEN | 242 | 0.922 | -0.537 | -0.17 -> +0.01 | +0.78 -> +0.68 | yes |
| p16_phi4_ref_L5 | p07_phi4_ref | L5 | 237 | 0.996 | -0.040 | -0.18 -> -0.18 | +0.87 -> +0.87 | NO |

**2 of 7 corrupt cells moved their judge** (2/7 cells).
