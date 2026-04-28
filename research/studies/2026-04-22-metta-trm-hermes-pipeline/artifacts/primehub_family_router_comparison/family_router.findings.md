# Primehub Family Router Comparison

## Variants

| Variant | Whole critic | Whole gated | Unrelated critic | Unrelated gated | IFEval gated contract | AIME gated exact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| control | 0.7500 | 0.0000 | 0.6522 | 0.0000 | 0.0000 | 0.0000 |
| global_common | 0.7500 | 0.1562 | 0.6522 | 0.2174 | 0.0000 | 0.0000 |
| global_all_abstractions | 0.4688 | 0.1562 | 0.6522 | 0.2174 | 1.0000 | 1.0000 |
| global_all_stacks | 0.4688 | 0.1562 | 0.6522 | 0.2174 | 1.0000 | 1.0000 |
| routed_abstractions | 0.4688 | 0.1562 | 0.6522 | 0.2174 | 1.0000 | 1.0000 |
| routed_stacks | 0.4688 | 0.1562 | 0.6522 | 0.2174 | 1.0000 | 1.0000 |

## Interference Vs Global Common

| Variant | Target lift | Unrelated critic drift | Unrelated gated regression | Whole critic drift | Net score |
| --- | ---: | ---: | ---: | ---: | ---: |
| control | 0.0000 | 0.0000 | 0.2174 | 0.0000 | -0.2174 |
| global_all_abstractions | 2.0000 | 0.0000 | 0.0000 | 0.2812 | 2.0000 |
| global_all_stacks | 2.0000 | 0.0000 | 0.0000 | 0.2812 | 2.0000 |
| routed_abstractions | 2.0000 | 0.0000 | 0.0000 | 0.2812 | 2.0000 |
| routed_stacks | 2.0000 | 0.0000 | 0.0000 | 0.2812 | 2.0000 |

## Readout

- Routed envs: `['allenai_ifeval', 'aime2026']`.
- Best net interference variant: `global_all_abstractions`.
- Best target lift variant: `global_all_abstractions`.
