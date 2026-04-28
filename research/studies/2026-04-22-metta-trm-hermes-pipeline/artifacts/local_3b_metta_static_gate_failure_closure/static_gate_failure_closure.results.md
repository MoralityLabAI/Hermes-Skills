# Static-Gate Failure Closure

Generated: `2026-04-28T12:24:27.742171+00:00`

This replay analyzes the remaining failures from the OOM-safe `metta_static_gate_rudder` run without launching the local 3B again.

## Summary

| Policy | Rows | Target-action acc | Repair-action acc | Joint acc |
| --- | ---: | ---: | ---: | ---: |
| `metta_static_gate_rudder_oom_safe` | 88 | 0.9432 | 1.0000 | 0.9432 |
| `metta_static_gate_v2_replay` | 88 | 0.9545 | 1.0000 | 0.9545 |

## Remaining V2 Misses

| Split | Case | Failure | Target | V2 pred | Closure class |
| --- | --- | --- | --- | --- | --- |
| `val_seen` | `intellect_3_logic_0:logic_trm_c_repair_if_c_fail` | `c_signature_fail` | `reject_or_abstain` | `commit` | `requires_post_repair_verifier` |
| `val_seen` | `intellect_3_logic_0:logic_trm_dual_repair_if_any_sig_fail` | `c_signature_fail` | `reject_or_abstain` | `commit` | `requires_post_repair_verifier` |
| `holdout_seen` | `intellect_3_logic_88:logic_trm_c_repair_if_c_fail` | `c_signature_fail` | `reject_or_abstain` | `commit` | `requires_post_repair_verifier` |
| `holdout_seen` | `intellect_3_logic_88:logic_trm_dual_repair_if_any_sig_fail` | `c_signature_fail` | `reject_or_abstain` | `commit` | `requires_post_repair_verifier` |

## Interpretation

- V2 adds one high-precision static gate: `safety_abstain_router + json_value_mismatch -> commit`, fixing the literal-union output miss without another model call.
- The only remaining misses are `c_signature_fail` no-gain rows where the repair action is correct but the commit decision needs post-repair validation.
- This defines the next TRM target: a verifier/commit TRM trained to distinguish `c_signature_fail` repair-success from no-gain after the proposed projection is applied.
