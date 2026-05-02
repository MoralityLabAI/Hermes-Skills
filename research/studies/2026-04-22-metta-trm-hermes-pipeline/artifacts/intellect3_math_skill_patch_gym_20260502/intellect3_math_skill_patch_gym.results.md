# Intellect-3-Math Skill-Patch Gym

Generated: `2026-05-02T23:12:59.964196+00:00`
Source smoke: `C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\intellect3_math_metta_self_improve_27b_20260502`

## Why This Gym

The 27B model can draft plausible MeTTa rules, but a single unverified prompt mutation underperformed the incumbent. The gym turns that into a search/control problem: generate patches, evaluate on held-out rows, train commit/veto TRMs, and only promote verified patches.

## Observed Seed Result

| Arm | Exact | Exact Rate | Common Actions |
| --- | ---: | ---: | --- |
| `baseline` | 0/10 | 0.0000 | 10:2, 2014:1, 12:1, 144:1, 15:1, 2018:1, 20:1, 4:1 |
| `current_skill` | 3/10 | 0.3000 | 10:2, 1023:1, 1:1, 17:1, 176:1, 2:1, 1009:1, 10201:1 |
| `metta_self_improved` | 2/10 | 0.2000 | 10:6, 1007:1, 108:1, 1009:1, 100:1 |

## Patch Bank

| Patch | Source | Status | Intended Failure Modes |
| --- | --- | --- | --- |
| `raw_baseline_no_skill` | `control` | `comparison_only` | no_skill_control |
| `incumbent_current_skill` | `codex_5_4_incumbent` | `incumbent` | none_baseline |
| `qwen27b_auditor_patch` | `live_qwen27b_drafted` | `observed_rejected` | magnitude_error, constraint_inconsistency |
| `codex_domain_router_v1` | `codex_gym_seed` | `candidate_pending_live_eval` | wrong_domain_tool, intermediate_answer_commit, magnitude_outlier |
| `codex_answer_shape_verifier_v1` | `codex_gym_seed` | `candidate_pending_live_eval` | answer_shape_mismatch, copied_constant, missing_bound_check |
| `codex_slow_path_trigger_v1` | `codex_gym_seed` | `candidate_pending_live_eval` | fast_guess, large_number_hallucination, unverified_extremal_answer |
| `codex_patch_commit_controller_v1` | `codex_gym_seed` | `controller_not_solver` | patch_overfit, regression_without_fix, candidate_selection_error |

## Adoption Gate

{
  "incumbent_patch_id": "incumbent_current_skill",
  "observed_candidate_patch_id": "qwen27b_auditor_patch",
  "decision": "reject_patch_keep_current_skill",
  "incumbent_exact": 3,
  "candidate_exact": 2,
  "rule": "adopt only if candidate held-out exact exceeds incumbent and fixed_by_candidate >= regressed_by_candidate"
}

## TRM Export

- Rows: `30`
- Labels: `commit_patch`, `reject_patch`, `incumbent`
- Target: train a patch commit/veto controller, not a math solver.

## Next Run

{
  "recommended_holdout_rows": 20,
  "recommended_patches": [
    "codex_domain_router_v1",
    "codex_answer_shape_verifier_v1",
    "codex_slow_path_trigger_v1",
    "codex_patch_commit_controller_v1"
  ],
  "execution": "evaluate each patch independently; checkpoint each row-arm result; promote only Pareto-improving patches",
  "resource_note": "snacksack 27B server reset during an uncapped 20-row expansion; keep live batches small and resumable."
}
