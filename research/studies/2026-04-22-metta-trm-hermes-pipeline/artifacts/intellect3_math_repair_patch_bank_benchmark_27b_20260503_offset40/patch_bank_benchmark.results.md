# Intellect-3-Math Patch-Bank Benchmark

Generated: `2026-05-03T01:34:15.376441+00:00`
Base URL: `http://snacksack-ms-7d32.tail3156cd.ts.net:8081/v1`
Rows requested: `10`
Completed calls: `50`

## Patch Scores

| Patch | Rows | Exact | Exact Rate | Errors | Avg Latency | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `raw_baseline_no_skill` | 10 | 0 | 0.0000 | 0 | 1.73s | `comparison_only` |
| `incumbent_current_skill` | 10 | 1 | 0.1000 | 0 | 1.62s | `incumbent` |
| `codex_near_miss_repair_v3` | 10 | 2 | 0.2000 | 0 | 1.65s | `adopt_patch` |
| `codex_trm_repair_gate_v3` | 10 | 1 | 0.1000 | 0 | 1.98s | `reject_patch` |
| `codex_pattern_micro_solver_v3` | 10 | 1 | 0.1000 | 0 | 2.00s | `reject_patch` |

## Read

Patch-bank benchmark over held-out rows; adoption is gated against the incumbent, not raw exact alone.

Best raw exact patch: `codex_near_miss_repair_v3`.

Adoption gates compare each patch against `incumbent_current_skill`; a patch with equal or lower exact is rejected even if it looks plausible.
