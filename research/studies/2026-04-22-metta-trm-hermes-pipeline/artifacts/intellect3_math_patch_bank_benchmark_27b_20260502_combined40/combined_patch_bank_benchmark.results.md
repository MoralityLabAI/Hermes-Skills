# Combined Intellect-3-Math Patch-Bank Benchmark

Generated: `2026-05-03T00:57:45.708357+00:00`
Unique rows: `40`
Calls: `280`

## Aggregate Patch Scores

| Patch | Rows | Exact | Exact Rate | Errors | Gate |
| --- | ---: | ---: | ---: | ---: | --- |
| `raw_baseline_no_skill` | 40 | 3 | 0.0750 | 0 | `comparison_only` |
| `incumbent_current_skill` | 40 | 7 | 0.1750 | 0 | `incumbent` |
| `qwen27b_auditor_patch` | 40 | 4 | 0.1000 | 0 | `reject_patch` |
| `codex_domain_router_v1` | 40 | 3 | 0.0750 | 0 | `reject_patch` |
| `codex_answer_shape_verifier_v1` | 40 | 2 | 0.0500 | 0 | `reject_patch` |
| `codex_slow_path_trigger_v1` | 40 | 4 | 0.1000 | 1 | `reject_patch` |
| `codex_patch_commit_controller_v1` | 40 | 3 | 0.0750 | 1 | `reject_patch` |

## Row-Level Winners

{
  "row_count": 40,
  "exclusive_wins": {
    "multi_patch_exact": 6,
    "no_patch_exact": 32,
    "incumbent_current_skill": 2
  },
  "exact_rows_by_patch": {
    "raw_baseline_no_skill": 3,
    "qwen27b_auditor_patch": 4,
    "incumbent_current_skill": 7,
    "codex_domain_router_v1": 3,
    "codex_answer_shape_verifier_v1": 2,
    "codex_slow_path_trigger_v1": 4,
    "codex_patch_commit_controller_v1": 3
  }
}

## Read

Patch-bank benchmark over held-out rows; adoption is gated against the incumbent, not raw exact alone.

Best raw exact patch: `incumbent_current_skill`.
No candidate patch clears the adoption gate on the combined 40-row smoke.
