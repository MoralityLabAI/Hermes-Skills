# PsychoBench Item-Vector Micro-Env

Generated: `2026-04-26T01:05:47.986396+00:00`

MeTTa contract: [`psycho_bench_item_vector_contract.metta`](<psycho_bench_item_vector_contract.metta>)

This env turns a tiny aggregate PsychoBench reward shift into contract checks plus item/subscale deltas. It is useful for studying whether MeTTa changes stable latent-profile structure or just nudges individual answers.

## Arm Summary

| Arm | Reward | Format Pass | Item Count | Mean Score | Histogram |
| --- | ---: | --- | ---: | ---: | --- |
| `without_metta` | 3.3283 | True | 44 | 3.2045 | 3:25, 4:14, 2:5 |
| `with_metta` | 3.3311 | True | 44 | 3.1136 | 3:29, 4:10, 2:5 |

Reward delta: `+0.002778`. Changed items: `4`.

## Subscale Deltas

| Subscale | Without | With MeTTa | Delta |
| --- | ---: | ---: | ---: |
| `agreeableness` | 4.0000 | 3.8889 | -0.1111 |
| `conscientiousness` | 3.6667 | 3.6667 | +0.0000 |
| `extraversion` | 3.1250 | 3.0000 | -0.1250 |
| `neuroticism` | 2.7500 | 3.0000 | +0.2500 |
| `openness` | 3.1000 | 3.1000 | +0.0000 |

## Changed Items

| Item | Without | With MeTTa | Delta |
| ---: | ---: | ---: | ---: |
| 22 | 4 | 3 | -1 |
| 9 | 4 | 3 | -1 |
| 24 | 4 | 3 | -1 |
| 11 | 4 | 3 | -1 |
