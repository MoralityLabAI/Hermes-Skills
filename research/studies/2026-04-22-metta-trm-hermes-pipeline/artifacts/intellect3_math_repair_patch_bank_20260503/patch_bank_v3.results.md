# Intellect-3-Math Repair Patch Bank

Generated: `2026-05-03T01:32:27.060666+00:00`
Source bank: `C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\intellect3_math_diverse_patch_bank_20260503\patch_bank_v2.json`
Total patches: `16`

## Added Repair Patches

| Patch | Failure Modes |
| --- | --- |
| `codex_near_miss_repair_v3` | off_by_one_attractor, copied_power_of_two, strict_cycle_wraparound |
| `codex_trm_repair_gate_v3` | prompt_constant_copy, boundary_neighbor_error, valuation_mismatch |
| `codex_pattern_micro_solver_v3` | wrong_named_algorithm, area_quotient_trap, valuation_window_error |

## Read

These patches test the paper's repair-curriculum claim directly: use observed semi-failed outputs to generate pattern-level veto and adjacent-value checks.
