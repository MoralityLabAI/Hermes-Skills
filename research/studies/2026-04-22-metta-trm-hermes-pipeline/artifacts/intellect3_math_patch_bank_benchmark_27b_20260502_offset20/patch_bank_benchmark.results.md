# Intellect-3-Math Patch-Bank Benchmark

Generated: `2026-05-03T00:52:52.787236+00:00`
Base URL: `http://snacksack-ms-7d32.tail3156cd.ts.net:8081/v1`
Rows requested: `10`
Completed calls: `70`

## Patch Scores

| Patch | Rows | Exact | Exact Rate | Errors | Avg Latency | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `raw_baseline_no_skill` | 10 | 0 | 0.0000 | 0 | 1.47s | `comparison_only` |
| `incumbent_current_skill` | 10 | 2 | 0.2000 | 0 | 1.57s | `incumbent` |
| `qwen27b_auditor_patch` | 10 | 0 | 0.0000 | 0 | 1.72s | `reject_patch` |
| `codex_domain_router_v1` | 10 | 0 | 0.0000 | 0 | 1.77s | `reject_patch` |
| `codex_answer_shape_verifier_v1` | 10 | 0 | 0.0000 | 0 | 1.58s | `reject_patch` |
| `codex_slow_path_trigger_v1` | 10 | 1 | 0.1000 | 0 | 1.56s | `reject_patch` |
| `codex_patch_commit_controller_v1` | 10 | 0 | 0.0000 | 1 | 1.46s | `reject_patch` |

## Read

Patch-bank benchmark over held-out rows; adoption is gated against the incumbent, not raw exact alone.

Best raw exact patch: `incumbent_current_skill`.

Adoption gates compare each patch against `incumbent_current_skill`; a patch with equal or lower exact is rejected even if it looks plausible.
