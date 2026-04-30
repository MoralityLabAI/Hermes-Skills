# Primehub External Abstraction Comparison

## Trainer Plan

- `training_task_id`: `metta-primehub-external-abstraction-comparison-20260423`
- `chunk_strategy`: `variant_per_run`
- `checkpoint_interval`: `variant_complete`
- `holdout_ratio`: `0.2`
- `top_k`: `5`
- `min_supervision_weight`: `0.4`

## Original External Primehub Holdout

| Variant | Rows | Critic bucket acc | Retriever exact | Gated router exact | Gated abstain |
| --- | ---: | ---: | ---: | ---: | ---: |
| control | 32 | 0.7500 | 0.0625 | 0.0000 | 0.9062 |
| control_plus_external_abstraction | 32 | 0.5938 | 0.1562 | 0.0000 | 0.7500 |
| control_plus_external_abstraction_and_critic_support | 32 | 0.7500 | 0.1562 | 0.1562 | 0.5938 |
| control_plus_external_and_all_transfer | 32 | 0.5938 | 0.1562 | 0.0000 | 0.7500 |
| control_plus_external_critic_and_all_transfer | 32 | 0.7500 | 0.1562 | 0.1562 | 0.5938 |
| control_plus_external_abstraction_and_critic_support_and_ifeval_abstraction | 32 | 0.6562 | 0.1562 | 0.1562 | 0.5000 |
| control_plus_external_abstraction_and_critic_support_and_ifeval_stack | 32 | 0.6562 | 0.1562 | 0.1562 | 0.5000 |
| control_plus_external_abstraction_and_critic_support_and_aime_abstraction | 32 | 0.5625 | 0.1562 | 0.1562 | 0.4062 |
| control_plus_external_abstraction_and_critic_support_and_aime_stack | 32 | 0.5625 | 0.1562 | 0.1562 | 0.4062 |

## Focus Env Holdout

Focus envs: `aime2026`, `allenai_ifeval`, `ascii_tree`, `if_summarize_judge`, `math_env`, `psycho_bench`, `pydantic_adherence`, `truthfulqa`

| Variant | Rows | Critic bucket acc | Retriever exact | Gated router exact | Gated abstain |
| --- | ---: | ---: | ---: | ---: | ---: |
| control | 17 | 0.5294 | 0.1176 | 0.0000 | 0.8235 |
| control_plus_external_abstraction | 17 | 0.5294 | 0.2941 | 0.0000 | 0.8235 |
| control_plus_external_abstraction_and_critic_support | 17 | 0.8235 | 0.2941 | 0.2941 | 0.5294 |
| control_plus_external_and_all_transfer | 17 | 0.5294 | 0.2941 | 0.0000 | 0.8235 |
| control_plus_external_critic_and_all_transfer | 17 | 0.8235 | 0.2941 | 0.2941 | 0.5294 |
| control_plus_external_abstraction_and_critic_support_and_ifeval_abstraction | 17 | 0.6471 | 0.2941 | 0.2941 | 0.3529 |
| control_plus_external_abstraction_and_critic_support_and_ifeval_stack | 17 | 0.6471 | 0.2941 | 0.2941 | 0.3529 |
| control_plus_external_abstraction_and_critic_support_and_aime_abstraction | 17 | 0.4706 | 0.2941 | 0.2941 | 0.1765 |
| control_plus_external_abstraction_and_critic_support_and_aime_stack | 17 | 0.4706 | 0.2941 | 0.2941 | 0.1765 |

## AllenAI IFEval Contract Holdout

| Variant | Rows | Retrieval contract | Gated contract | Gated postscript | Gated semantic | Gated nonempty |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| control | 3 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_external_abstraction | 3 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_external_abstraction_and_critic_support | 3 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_external_and_all_transfer | 3 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_external_critic_and_all_transfer | 3 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_external_abstraction_and_critic_support_and_ifeval_abstraction | 3 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| control_plus_external_abstraction_and_critic_support_and_ifeval_stack | 3 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| control_plus_external_abstraction_and_critic_support_and_aime_abstraction | 3 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_external_abstraction_and_critic_support_and_aime_stack | 3 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

## AIME2026 Numeric Holdout

| Variant | Rows | Retrieval nonempty | Retrieval boxed | Retrieval exact | Gated nonempty | Gated boxed | Gated exact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| control | 6 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_external_abstraction | 6 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_external_abstraction_and_critic_support | 6 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_external_and_all_transfer | 6 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_external_critic_and_all_transfer | 6 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_external_abstraction_and_critic_support_and_ifeval_abstraction | 6 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_external_abstraction_and_critic_support_and_ifeval_stack | 6 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| control_plus_external_abstraction_and_critic_support_and_aime_abstraction | 6 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| control_plus_external_abstraction_and_critic_support_and_aime_stack | 6 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Delta Vs Control On Original External Holdout

| Variant | Critic bucket acc | Retriever exact | Gated router exact | Gated abstain |
| --- | ---: | ---: | ---: | ---: |
| control_plus_external_abstraction | -0.1562 | +0.0937 | +0.0000 | -0.1562 |
| control_plus_external_abstraction_and_critic_support | +0.0000 | +0.0937 | +0.1562 | -0.3124 |
| control_plus_external_and_all_transfer | -0.1562 | +0.0937 | +0.0000 | -0.1562 |
| control_plus_external_critic_and_all_transfer | +0.0000 | +0.0937 | +0.1562 | -0.3124 |
| control_plus_external_abstraction_and_critic_support_and_ifeval_abstraction | -0.0938 | +0.0937 | +0.1562 | -0.4062 |
| control_plus_external_abstraction_and_critic_support_and_ifeval_stack | -0.0938 | +0.0937 | +0.1562 | -0.4062 |
| control_plus_external_abstraction_and_critic_support_and_aime_abstraction | -0.1875 | +0.0937 | +0.1562 | -0.5000 |
| control_plus_external_abstraction_and_critic_support_and_aime_stack | -0.1875 | +0.0937 | +0.1562 | -0.5000 |

## Delta Vs Control On AllenAI IFEval Contract Holdout

| Variant | Retrieval contract | Gated contract | Gated postscript | Gated semantic | Gated nonempty |
| --- | ---: | ---: | ---: | ---: | ---: |
| control_plus_external_abstraction | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| control_plus_external_abstraction_and_critic_support | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| control_plus_external_and_all_transfer | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| control_plus_external_critic_and_all_transfer | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| control_plus_external_abstraction_and_critic_support_and_ifeval_abstraction | +1.0000 | +1.0000 | +1.0000 | +1.0000 | +1.0000 |
| control_plus_external_abstraction_and_critic_support_and_ifeval_stack | +1.0000 | +1.0000 | +1.0000 | +1.0000 | +1.0000 |
| control_plus_external_abstraction_and_critic_support_and_aime_abstraction | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| control_plus_external_abstraction_and_critic_support_and_aime_stack | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |

## Delta Vs Control On AIME2026 Numeric Holdout

| Variant | Retrieval nonempty | Retrieval boxed | Retrieval exact | Gated nonempty | Gated boxed | Gated exact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| control_plus_external_abstraction | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| control_plus_external_abstraction_and_critic_support | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| control_plus_external_and_all_transfer | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| control_plus_external_critic_and_all_transfer | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| control_plus_external_abstraction_and_critic_support_and_ifeval_abstraction | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| control_plus_external_abstraction_and_critic_support_and_ifeval_stack | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| control_plus_external_abstraction_and_critic_support_and_aime_abstraction | +0.0000 | +0.0000 | +1.0000 | +1.0000 | +1.0000 | +1.0000 |
| control_plus_external_abstraction_and_critic_support_and_aime_stack | +0.0000 | +0.0000 | +1.0000 | +1.0000 | +1.0000 | +1.0000 |

## Readout

- Original external primehub holdout rows: `32`.
- Best original external lift variant: `control_plus_external_abstraction_and_critic_support_and_ifeval_abstraction`.
- Best allenai_ifeval contract variant: `control_plus_external_abstraction_and_critic_support_and_ifeval_abstraction`.
- Best aime2026 numeric variant: `control_plus_external_abstraction_and_critic_support_and_aime_abstraction`.
- Original external env counts: `{'aime2026': 6, 'misguided_attn': 5, 'psycho_bench': 3, 'math_env': 3, 'allenai_ifeval': 3, 'colf': 3, 'jailbreak_bench': 3, 'uq': 4, 'truthfulqa': 2}`.
- Focus-env overlap in the original holdout: `{'aime2026': 6, 'psycho_bench': 3, 'math_env': 3, 'allenai_ifeval': 3, 'truthfulqa': 2}`.
