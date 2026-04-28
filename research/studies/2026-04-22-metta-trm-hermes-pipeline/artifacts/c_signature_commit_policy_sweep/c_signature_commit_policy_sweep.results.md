# C-Signature Commit Policy Sweep

Generated: `2026-04-28T14:02:37.334046+00:00`

This deterministic sweep tests whether simple MeTTa-visible features can solve the remaining C-signature false-commit problem before training a neural commit TRM.

Selected policy: `knn_k3_reject_ge_0p34`

## Selected Policy Metrics

| Split | Rows | Accuracy | False commit rate | False reject rate | Expected committed delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `train` | 86 | 0.8953 | 0.4118 | 0.0290 | 8.3983 |
| `val_seen` | 16 | 1.0000 | 0.0000 | 0.0000 | 1.9117 |
| `holdout_seen` | 20 | 0.8000 | 1.0000 | 0.1111 | 1.6600 |

## Top Validation Policies

| Policy | Val acc | Val false commit | Val false reject | Holdout acc | Holdout false commit |
| --- | ---: | ---: | ---: | ---: | ---: |
| `knn_k3_reject_ge_0p34` | 1.0000 | 0.0000 | 0.0000 | 0.8000 | 1.0000 |
| `knn_k3_reject_ge_0p5` | 1.0000 | 0.0000 | 0.0000 | 0.8000 | 1.0000 |
| `knn_k1_reject_ge_0p25` | 0.8750 | 0.0000 | 0.1429 | 0.9000 | 1.0000 |
| `knn_k1_reject_ge_0p34` | 0.8750 | 0.0000 | 0.1429 | 0.9000 | 1.0000 |
| `knn_k1_reject_ge_0p5` | 0.8750 | 0.0000 | 0.1429 | 0.9000 | 1.0000 |
| `knn_k1_reject_ge_0p67` | 0.8750 | 0.0000 | 0.1429 | 0.9000 | 1.0000 |
| `knn_k1_reject_ge_0p75` | 0.8750 | 0.0000 | 0.1429 | 0.9000 | 1.0000 |
| `knn_k5_reject_ge_0p25` | 0.8750 | 0.0000 | 0.1429 | 0.7500 | 1.0000 |
| `knn_k5_reject_ge_0p34` | 0.8750 | 0.0000 | 0.1429 | 0.7500 | 1.0000 |
| `knn_k7_reject_ge_0p25` | 0.8750 | 0.0000 | 0.1429 | 0.7000 | 1.0000 |
| `knn_k7_reject_ge_0p34` | 0.8750 | 0.0000 | 0.1429 | 0.8500 | 1.0000 |
| `train_feature_memory` | 0.8750 | 0.0000 | 0.1429 | 0.8000 | 1.0000 |
| `knn_k3_reject_ge_0p25` | 0.7500 | 0.0000 | 0.2857 | 0.9000 | 0.0000 |
| `band_0p80_0p88_edit_1_4` | 0.7500 | 0.0000 | 0.2857 | 0.6000 | 1.0000 |
| `reward_band_0p80_0p88` | 0.7500 | 0.0000 | 0.2857 | 0.5000 | 1.0000 |
| `band_0p76_0p88_edit_1_4` | 0.6250 | 0.0000 | 0.4286 | 0.6000 | 1.0000 |
| `reward_band_0p76_0p88` | 0.6250 | 0.0000 | 0.4286 | 0.5000 | 1.0000 |
| `edit_2_4_reject` | 0.5000 | 0.0000 | 0.5714 | 0.9000 | 0.0000 |
| `edit_1_2_3_4_reject` | 0.2500 | 0.0000 | 0.8571 | 0.3000 | 0.0000 |
| `always_commit` | 0.8750 | 1.0000 | 0.0000 | 0.9000 | 1.0000 |

## Holdout Safety Frontier

| Policy | Holdout acc | Holdout false commit | Holdout false reject | Val acc | Val false commit |
| --- | ---: | ---: | ---: | ---: | ---: |
| `edit_2_4_reject` | 0.9000 | 0.0000 | 0.1111 | 0.5000 | 0.0000 |
| `knn_k3_reject_ge_0p25` | 0.9000 | 0.0000 | 0.1111 | 0.7500 | 0.0000 |
| `edit_1_2_3_4_reject` | 0.3000 | 0.0000 | 0.7778 | 0.2500 | 0.0000 |
| `knn_k1_reject_ge_0p25` | 0.9000 | 1.0000 | 0.0000 | 0.8750 | 0.0000 |
| `knn_k1_reject_ge_0p34` | 0.9000 | 1.0000 | 0.0000 | 0.8750 | 0.0000 |
| `knn_k1_reject_ge_0p5` | 0.9000 | 1.0000 | 0.0000 | 0.8750 | 0.0000 |
| `knn_k1_reject_ge_0p67` | 0.9000 | 1.0000 | 0.0000 | 0.8750 | 0.0000 |
| `knn_k1_reject_ge_0p75` | 0.9000 | 1.0000 | 0.0000 | 0.8750 | 0.0000 |
| `always_commit` | 0.9000 | 1.0000 | 0.0000 | 0.8750 | 1.0000 |
| `knn_k3_reject_ge_0p67` | 0.9000 | 1.0000 | 0.0000 | 0.8750 | 1.0000 |
| `knn_k3_reject_ge_0p75` | 0.9000 | 1.0000 | 0.0000 | 0.8750 | 1.0000 |
| `knn_k5_reject_ge_0p5` | 0.9000 | 1.0000 | 0.0000 | 0.8750 | 1.0000 |
| `knn_k5_reject_ge_0p67` | 0.9000 | 1.0000 | 0.0000 | 0.8750 | 1.0000 |
| `knn_k5_reject_ge_0p75` | 0.9000 | 1.0000 | 0.0000 | 0.8750 | 1.0000 |
| `knn_k7_reject_ge_0p5` | 0.9000 | 1.0000 | 0.0000 | 0.8750 | 1.0000 |

## Interpretation

- Validation-selected simple policies can eliminate validation false commits while still missing all holdout no-gain C repairs.
- Holdout-safe visible-feature rules exist, but they are lossy guards with high false-reject rates on validation or training.
- This supports training a post-repair verifier/commit TRM with richer post-repair state instead of relying on scalar pre-repair features.
