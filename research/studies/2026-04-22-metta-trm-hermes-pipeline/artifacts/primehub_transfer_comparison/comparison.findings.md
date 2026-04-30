# Primehub Transfer Comparison

## Trainer Plan

- `training_task_id`: `metta-primehub-transfer-comparison-20260423`
- `chunk_strategy`: `variant_per_run`
- `checkpoint_interval`: `variant_complete`
- `holdout_ratio`: `0.2`
- `top_k`: `5`
- `min_supervision_weight`: `0.4`

## Original External Primehub Holdout

| Variant | Rows | Critic bucket acc | Retriever exact | Gated router exact | Gated abstain |
| --- | ---: | ---: | ---: | ---: | ---: |
| control | 32 | 0.7500 | 0.0625 | 0.0000 | 0.9062 |
| control_plus_structured_transfer | 32 | 0.7500 | 0.0625 | 0.0000 | 0.9062 |
| control_plus_structured_and_if_transfer | 32 | 0.7500 | 0.0625 | 0.0000 | 0.9062 |

## Focus Env Holdout

Focus envs: `ascii_tree`, `if_summarize_judge`, `psycho_bench`, `pydantic_adherence`

| Variant | Rows | Critic bucket acc | Retriever exact | Gated router exact | Gated abstain |
| --- | ---: | ---: | ---: | ---: | ---: |
| control | 3 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_structured_transfer | 3 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_structured_and_if_transfer | 3 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

## Delta Vs Control On Original External Holdout

| Variant | Critic bucket acc | Retriever exact | Gated router exact | Gated abstain |
| --- | ---: | ---: | ---: | ---: |
| control_plus_structured_transfer | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| control_plus_structured_and_if_transfer | +0.0000 | +0.0000 | +0.0000 | +0.0000 |

## Readout

- Original external primehub holdout rows: `32`.
- No original external lift was observed on the untouched primehub holdout.
- Original external env counts: `{'aime2026': 6, 'misguided_attn': 5, 'psycho_bench': 3, 'math_env': 3, 'allenai_ifeval': 3, 'colf': 3, 'jailbreak_bench': 3, 'uq': 4, 'truthfulqa': 2}`.
- Focus-env overlap in the original holdout: `{'psycho_bench': 3}`.
