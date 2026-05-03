# Intellect-3-Math Patch-Bank Benchmark

Generated: `2026-05-03T01:30:59.581482+00:00`
Base URL: `http://snacksack-ms-7d32.tail3156cd.ts.net:8081/v1`
Rows requested: `10`
Completed calls: `130`

## Patch Scores

| Patch | Rows | Exact | Exact Rate | Errors | Avg Latency | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `raw_baseline_no_skill` | 10 | 0 | 0.0000 | 1 | 1.38s | `comparison_only` |
| `incumbent_current_skill` | 10 | 1 | 0.1000 | 0 | 1.53s | `incumbent` |
| `qwen27b_auditor_patch` | 10 | 1 | 0.1000 | 0 | 1.90s | `reject_patch` |
| `codex_domain_router_v1` | 10 | 1 | 0.1000 | 0 | 1.88s | `reject_patch` |
| `codex_answer_shape_verifier_v1` | 10 | 1 | 0.1000 | 0 | 1.81s | `reject_patch` |
| `codex_slow_path_trigger_v1` | 10 | 1 | 0.1000 | 1 | 1.63s | `reject_patch` |
| `codex_patch_commit_controller_v1` | 10 | 1 | 0.1000 | 0 | 1.68s | `reject_patch` |
| `codex_metta_theorem_router_v2` | 10 | 1 | 0.1000 | 0 | 1.83s | `reject_patch` |
| `codex_finite_table_builder_v2` | 10 | 1 | 0.1000 | 0 | 2.30s | `reject_patch` |
| `codex_backward_constraint_solver_v2` | 10 | 1 | 0.1000 | 0 | 2.00s | `reject_patch` |
| `codex_modular_valuation_solver_v2` | 10 | 0 | 0.0000 | 0 | 1.72s | `reject_patch` |
| `codex_coordinate_geometry_solver_v2` | 10 | 1 | 0.1000 | 0 | 1.65s | `reject_patch` |
| `codex_extremal_construction_solver_v2` | 10 | 1 | 0.1000 | 2 | 1.29s | `reject_patch` |

## Read

Patch-bank benchmark over held-out rows; adoption is gated against the incumbent, not raw exact alone.

Best raw exact patch: `qwen27b_auditor_patch`.

Adoption gates compare each patch against `incumbent_current_skill`; a patch with equal or lower exact is rejected even if it looks plausible.
