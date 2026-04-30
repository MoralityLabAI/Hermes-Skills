# Primehub Rollup Comparison

## Trainer Plan

- `training_task_id`: `metta-primehub-rollup-comparison-20260423`
- `chunk_strategy`: `variant_per_run`
- `checkpoint_interval`: `variant_complete`
- `holdout_ratio`: `0.2`
- `top_k`: `5`
- `min_supervision_weight`: `0.4`

## Variant Results

| Variant | Rows | Exact+ | Global retriever | Global gated router | Primehub retriever | Primehub gated router | Primehub abstain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| control | 195 | 24 | 0.0625 | 0.0000 | 0.0625 | 0.0000 | 0.9062 |
| control_plus_structured_map | 219 | 42 | 0.0571 | 0.0000 | 0.0625 | 0.0000 | 0.9062 |
| control_plus_structured_map_and_if_summarize | 380 | 167 | 0.1667 | 0.1364 | 0.0625 | 0.0000 | 0.9062 |

## Delta Vs Control

| Variant | Global retriever | Global gated router | Primehub retriever | Primehub gated router | Primehub abstain |
| --- | ---: | ---: | ---: | ---: | ---: |
| control_plus_structured_map | -0.0054 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| control_plus_structured_map_and_if_summarize | +0.1042 | +0.1364 | +0.0000 | +0.0000 | +0.0000 |

## Official Cycle 12 Reference

- Official router gated exact match: `0.0000`
- Official retriever exact match: `0.0625`
- Official critic bucket accuracy: `0.7500`

## Live Baseline vs Mining Cross-Ref

| Model | Env | Variant | Baseline reward | Mining reward | Delta | Baseline tokens | Mining tokens | Delta |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen35_27b | boolq | single-model-baseline | 0.0000 | 0.0000 | +0.0000 | 512 | 704 | +192 |
| qwen35_27b | boolq | two-model-abstain-guard-v1 | 0.0000 | 1.0000 | +1.0000 | 703 | 895 | +192 |
| qwen35_27b | boolq | two-model-contract-repair-v1 | 0.0000 | 1.0000 | +1.0000 | 703 | 893 | +190 |
| qwen35_27b | psycho_bench | single-model-baseline | 0.0000 | 0.0000 | +0.0000 | 912 | 1104 | +192 |
| qwen35_27b | psycho_bench | two-model-contract-repair-v1 | 0.0000 | 0.0000 | +0.0000 | 1077 | 1269 | +192 |
| qwen35_9b | boolq | single-model-baseline | 0.0000 | 0.0000 | +0.0000 | 511 | 703 | +192 |
| qwen35_9b | boolq | two-model-abstain-guard-v1 | 0.0000 | 0.0000 | +0.0000 | 702 | 894 | +192 |
| qwen35_9b | boolq | two-model-contract-repair-v1 | 0.0000 | 0.0000 | +0.0000 | 702 | 894 | +192 |
| qwen35_9b | psycho_bench | single-model-baseline | 0.0000 | 0.0000 | +0.0000 | 911 | 1103 | +192 |
| qwen35_9b | psycho_bench | two-model-contract-repair-v1 | 0.0000 | 0.0000 | +0.0000 | 1076 | 1268 | +192 |

## Readout

- Control rerun global retriever exact match is `0.0625` on `195` rows.
- Best global lift is `control_plus_structured_map_and_if_summarize` with delta `+0.1042` retriever exact match.
- No primehub transfer lift was observed; all three variants stayed at `0.0625` retriever exact match and `0.0000` gated router exact match on the base `primehub` holdout.
- Live mining rerun still shows the only reward delta in this slice on `boolq` for `qwen35_27b`.
- No live baseline/mining rows exist yet for: `ascii_tree`, `if_summarize_judge`, `pydantic_adherence`.
