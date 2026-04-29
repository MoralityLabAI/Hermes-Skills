# Logic Signature Camp-Gate Projection Ablation

Generated: `2026-04-29T18:25:02.704781+00:00`

Evidence class: `live_log_replay_public_constraint_solver`

This replay fixes the prior parse/shape bottleneck by adding a public-constraint solver arm. It does not replace the candidate-conditioned projection metric.

## Arm Summary

| Arm | Rows | Exact | Exact Rate | Contract Valid | Avg Cell Acc | Tier Counts |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `baseline` | 12 | 0 | 0.0000 | 0 | 0.0781 | none:10, weak_surface:2 |
| `candidate_conditioned_projection` | 12 | 9 | 0.7500 | 9 | 0.7500 | full_candidate:9, none:3 |
| `metta_runtime` | 12 | 0 | 0.0000 | 0 | 0.2792 | none:3, weak_surface:9 |
| `metta_signature_projection` | 12 | 9 | 0.7500 | 9 | 0.7500 | full_candidate:9, none:3 |
| `public_constraint_solver` | 12 | 12 | 1.0000 | 12 | 1.0000 | full_candidate:12 |
| `pure_trm` | 12 | 0 | 0.0000 | 0 | 0.1562 | none:7, weak_surface:5 |

## Interpretation

- `candidate_conditioned_projection` is the fair measure of whether the 3B emitted a parseable verifier-visible grid state.
- `public_constraint_solver` shows the stronger closure threshold: once public constraints are machine-visible and unique, the LLM is no longer needed for grid execution.
- The next empirical bottleneck is constraint extraction from less-structured natural-language puzzle statements.
