# Local 3B Repair-Training Rudder Benchmark

Generated: `2026-04-26T16:49:31.660412+00:00`

This is a pre-training benchmark: the local 3B model chooses repair/commit/veto actions over Pure-TRM rows. It does not claim trained repair-TRM weights exist yet.

## Summary

| Arm | Rows | Target-action acc | Repair-action acc | Joint acc | JSON parse | Max child RSS MB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `raw_3b_rudder` | 88 | 0.7159 | 0.4091 | 0.3636 | 1.0000 | 2360.80 |
| `repair_training_rudder` | 88 | 0.7955 | 0.3409 | 0.3182 | 1.0000 | 2375.40 |

## Claim Boundary

- `raw_3b_rudder` measures whether the small model can infer gate actions from state alone.
- `repair_training_rudder` measures whether retrieved near-miss training rows help the small model choose the right gate actions.
- This should be followed by an actual trained repair/verifier TRM run using the same splits.

## Failure Breakdown

| Slice | Raw target | Repair-context target | Raw repair | Repair-context repair | Read |
| --- | ---: | ---: | ---: | ---: | --- |
| `holdout_unseen_family` | 0.5000 | 0.8889 | 0.0000 | 0.0000 | Retrieval helps commit/veto transfer, but not unseen repair-action naming. |
| `repair_failure_or_no_gain` | 0.0000 | 0.1818 | 0.1818 | 0.0909 | Main weakness: the 3B over-commits repairs that should be rejected. |
| `c_signature_fail` | 0.8889 | 0.8889 | 1.0000 | 0.8333 | Logic C-signature repair is already learnable by prompt-level 3B. |
| `signature_pass_cell_fail` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | Needs a verifier/commit TRM; prompt context alone does not identify no-gain cases. |
| `structured_map` | 0.4000 | 1.0000 | 0.0000 | 0.0000 | Commit/veto transfers; repair action should be narrowed by env-specific action schemas. |

Interpretation: this benchmark supports using the 3B as a commit/veto rudder with repair-training context, but not as the final repair-action selector. The next experiment should split the decision into two stages: deterministic role/action-space narrowing first, then 3B or TRM commit selection.
