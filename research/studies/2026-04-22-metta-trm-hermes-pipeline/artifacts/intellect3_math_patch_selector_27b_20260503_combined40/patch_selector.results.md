# Intellect-3-Math Row-Level Patch Selector

Generated: `2026-05-03T00:57:52.301243+00:00`
Rows: `40`
Calls: `280`

## Selector Scores

| Selector | Split | Rows | Exact | Exact Rate |
| --- | --- | ---: | ---: | ---: |
| `incumbent_all` | `all` | 40 | 7 | 0.1750 |
| `oracle_any_exact_all` | `all` | 40 | 8 | 0.2000 |
| `plurality_answer_all` | `all` | 40 | 4 | 0.1000 |
| `prior_selector_train` | `train` | 20 | 4 | 0.2000 |
| `prior_selector_test` | `test` | 20 | 4 | 0.2000 |
| `incumbent_test` | `test` | 20 | 4 | 0.2000 |
| `oracle_any_exact_test` | `test` | 20 | 4 | 0.2000 |

## Read

The current patch bank has a small oracle headroom over the incumbent (8/40 vs 7/40), but the simple learned prior selector does not yet extract reliable held-out lift. Next useful work is to train a selector TRM on richer features, not to adopt a global prompt patch.

## Row-Level Upper Bound

{
  "rows": 40,
  "exact": 8,
  "exact_rate": 0.2,
  "missing_selected_rows": 0,
  "selected_patch_counts": {
    "raw_baseline_no_skill": 3,
    "incumbent_current_skill": 37
  }
}
