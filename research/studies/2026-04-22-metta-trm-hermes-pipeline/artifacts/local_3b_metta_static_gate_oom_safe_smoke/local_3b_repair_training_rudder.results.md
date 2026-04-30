# Local 3B Repair-Training Rudder Benchmark

Generated: `2026-04-28T12:02:21.254239+00:00`

This is a pre-training benchmark: the local 3B model chooses repair/commit/veto actions over Pure-TRM rows. It does not claim trained repair-TRM weights exist yet.

## Summary

| Arm | Rows | Target-action acc | Repair-action acc | Joint acc | JSON parse | Max child RSS MB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `metta_static_gate_rudder` | 12 | 0.8333 | 1.0000 | 0.8333 | 1.0000 | 2369.86 |

## Claim Boundary

- `raw_3b_rudder` measures whether the small model can infer gate actions from state alone.
- `repair_training_rudder` measures whether retrieved near-miss training rows help the small model choose the right gate actions.
- `metta_action_space_rudder` fixes the repair action with a MeTTa action-space gate and uses 3B only for commit/veto.
- `metta_static_gate_rudder` additionally lets MeTTa commit or veto obvious exact/no-gain states before falling back to 3B.
- `metta_validator_gate` is a post-repair validator ceiling, not a prompt-level 3B result.
- This should be followed by an actual trained repair/verifier TRM run using the same splits.
