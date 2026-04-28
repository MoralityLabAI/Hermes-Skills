# Local 3B Repair-Training Rudder Benchmark

Generated: `2026-04-28T11:50:45.091072+00:00`

This is a pre-training benchmark: the local 3B model chooses repair/commit/veto actions over Pure-TRM rows. It does not claim trained repair-TRM weights exist yet.

## Summary

| Arm | Rows | Target-action acc | Repair-action acc | Joint acc | JSON parse | Max child RSS MB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `metta_action_space_rudder` | 88 | 0.7500 | 1.0000 | 0.7500 | 1.0000 | 2361.24 |
| `metta_action_space_training_rudder` | 88 | 0.6932 | 1.0000 | 0.6932 | 1.0000 | 2381.04 |
| `metta_static_gate_rudder` | 88 | 0.9545 | 1.0000 | 0.9545 | 1.0000 | 2361.29 |
| `metta_validator_gate` | 88 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 |

## Claim Boundary

- `raw_3b_rudder` measures whether the small model can infer gate actions from state alone.
- `repair_training_rudder` measures whether retrieved near-miss training rows help the small model choose the right gate actions.
- `metta_action_space_rudder` fixes the repair action with a MeTTa action-space gate and uses 3B only for commit/veto.
- `metta_static_gate_rudder` additionally lets MeTTa commit or veto obvious exact/no-gain states before falling back to 3B.
- `metta_validator_gate` is a post-repair validator ceiling, not a prompt-level 3B result.
- This should be followed by an actual trained repair/verifier TRM run using the same splits.
