# Combined Intellect-3-Math Patch-Bank Benchmark

Generated: `2026-05-03T00:53:29.499521+00:00`
Unique rows: `30`
Calls: `210`

## Aggregate Patch Scores

| Patch | Rows | Exact | Exact Rate | Errors | Gate |
| --- | ---: | ---: | ---: | ---: | --- |
| `raw_baseline_no_skill` | 30 | 2 | 0.0667 | 0 | `comparison_only` |
| `incumbent_current_skill` | 30 | 6 | 0.2000 | 0 | `incumbent` |
| `qwen27b_auditor_patch` | 30 | 3 | 0.1000 | 0 | `reject_patch` |
| `codex_domain_router_v1` | 30 | 2 | 0.0667 | 0 | `reject_patch` |
| `codex_answer_shape_verifier_v1` | 30 | 1 | 0.0333 | 0 | `reject_patch` |
| `codex_slow_path_trigger_v1` | 30 | 3 | 0.1000 | 1 | `reject_patch` |
| `codex_patch_commit_controller_v1` | 30 | 2 | 0.0667 | 1 | `reject_patch` |

## Row-Level Winners

{
  "row_count": 30,
  "exclusive_wins": {
    "multi_patch_exact": 5,
    "no_patch_exact": 23,
    "incumbent_current_skill": 2
  },
  "exact_rows_by_patch": {
    "raw_baseline_no_skill": 2,
    "qwen27b_auditor_patch": 3,
    "incumbent_current_skill": 6,
    "codex_domain_router_v1": 2,
    "codex_answer_shape_verifier_v1": 1,
    "codex_slow_path_trigger_v1": 3,
    "codex_patch_commit_controller_v1": 2
  }
}

## Read

Patch-bank benchmark over held-out rows; adoption is gated against the incumbent, not raw exact alone.

Best raw exact patch: `incumbent_current_skill`.
No candidate patch clears the adoption gate on the combined 30-row smoke.
