# Combined Intellect-3-Math Patch-Bank Benchmark

Generated: `2026-05-03T00:25:54.042430+00:00`
Unique rows: `20`
Calls: `140`

## Aggregate Patch Scores

| Patch | Rows | Exact | Exact Rate | Errors | Gate |
| --- | ---: | ---: | ---: | ---: | --- |
| `raw_baseline_no_skill` | 20 | 2 | 0.1000 | 0 | `comparison_only` |
| `incumbent_current_skill` | 20 | 4 | 0.2000 | 0 | `incumbent` |
| `qwen27b_auditor_patch` | 20 | 3 | 0.1500 | 0 | `reject_patch` |
| `codex_domain_router_v1` | 20 | 2 | 0.1000 | 0 | `reject_patch` |
| `codex_answer_shape_verifier_v1` | 20 | 1 | 0.0500 | 0 | `reject_patch` |
| `codex_slow_path_trigger_v1` | 20 | 2 | 0.1000 | 1 | `reject_patch` |
| `codex_patch_commit_controller_v1` | 20 | 2 | 0.1000 | 0 | `reject_patch` |

## Row-Level Winners

{
  "row_count": 20,
  "exclusive_wins": {
    "multi_patch_exact": 4,
    "no_patch_exact": 15,
    "incumbent_current_skill": 1
  },
  "exact_rows_by_patch": {
    "raw_baseline_no_skill": 2,
    "qwen27b_auditor_patch": 3,
    "incumbent_current_skill": 4,
    "codex_domain_router_v1": 2,
    "codex_answer_shape_verifier_v1": 1,
    "codex_slow_path_trigger_v1": 2,
    "codex_patch_commit_controller_v1": 2
  }
}

## Read

Patch-bank benchmark over held-out rows; adoption is gated against the incumbent, not raw exact alone.

Best raw exact patch: `incumbent_current_skill`.
No candidate patch clears the adoption gate on the combined 20-row smoke.
