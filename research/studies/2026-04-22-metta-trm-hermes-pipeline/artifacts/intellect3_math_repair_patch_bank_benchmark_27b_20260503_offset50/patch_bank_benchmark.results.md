# Intellect-3-Math Patch-Bank Benchmark

Generated: `2026-05-03T01:35:35.335943+00:00`
Base URL: `http://snacksack-ms-7d32.tail3156cd.ts.net:8081/v1`
Rows requested: `10`
Completed calls: `30`

## Patch Scores

| Patch | Rows | Exact | Exact Rate | Errors | Avg Latency | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `raw_baseline_no_skill` | 10 | 0 | 0.0000 | 0 | 1.70s | `comparison_only` |
| `incumbent_current_skill` | 10 | 2 | 0.2000 | 0 | 1.72s | `incumbent` |
| `codex_near_miss_repair_v3` | 10 | 0 | 0.0000 | 0 | 1.80s | `reject_patch` |

## Read

Patch-bank benchmark over held-out rows; adoption is gated against the incumbent, not raw exact alone.

Best raw exact patch: `incumbent_current_skill`.

Adoption gates compare each patch against `incumbent_current_skill`; a patch with equal or lower exact is rejected even if it looks plausible.
