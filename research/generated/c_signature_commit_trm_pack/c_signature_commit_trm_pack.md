# C-Signature Commit TRM Pack

Generated: `2026-04-28T14:01:59.131092+00:00`

This pack isolates the remaining Intellect-3 logic failure mode after MeTTa action-space narrowing: deciding whether a proposed C-signature repair should be committed or rejected.

## Summary

- Rows: `122`
- Purpose: Train a post-repair verifier/commit TRM for c_signature_fail rows where MeTTa can select the repair action but pre-repair 3B over-commits no-gain repairs.

## Companion Artifacts

- Training plan: `research/generated/c_signature_commit_trm_pack/c_signature_commit_trm_training_plan.md`
- Capped Windows wrapper: `research/scripts/run_c_signature_commit_trm_jobcap.ps1`
- Post-repair verifier sweep: `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/c_signature_postrepair_verifier_sweep/c_signature_postrepair_verifier.results.md`

| Split | Rows | Target mix |
| --- | ---: | --- |
| `holdout_seen` | 20 | `commit`:18, `reject_or_abstain`:2 |
| `train` | 86 | `commit`:69, `reject_or_abstain`:17 |
| `val_seen` | 16 | `commit`:14, `reject_or_abstain`:2 |

## Bucket Mix

| Bucket | Rows |
| --- | ---: |
| `partial_repair_improvement` | 20 |
| `repair_failure_or_no_gain` | 21 |
| `repair_success` | 81 |

## Training Interpretation

- `commit` rows are successful or partially improving C-signature repairs.
- `reject_or_abstain` rows are no-gain repairs that the 3B static-gate rudder still tends to over-commit.
- The target TRM should run after MeTTa proposes the C-signature repair, not before repair-action selection.
- The pack preserves post-repair signals (`after_exact`, reward delta, and signature pass state) so verifier TRMs can learn from multiple success metrics instead of a single scalar reward.
- Report false-commit rate as the primary safety metric; exact/joint accuracy alone hides no-gain over-commit.

## High-Risk Reject Rows

| Split | Case | Before reward | After reward | Edit distance | After exact | Target |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `train` | `intellect_3_logic_1:logic_trm_c_repair_if_c_fail` | 0.8500 | 0.8000 | 1 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_1:logic_trm_dual_repair_if_any_sig_fail` | 0.8500 | 0.8000 | 1 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_14:logic_trm_c_repair_if_c_fail` | 0.8400 | 0.8400 | 4 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_14:logic_trm_dual_repair_if_any_sig_fail` | 0.8400 | 0.8400 | 4 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_21:logic_trm_c_repair_if_c_fail` | 0.8400 | 0.8400 | 2 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_21:logic_trm_dual_repair_if_any_sig_fail` | 0.8400 | 0.8400 | 2 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_45:logic_trm_dual_repair_if_any_sig_fail` | 0.8400 | 0.7600 | 4 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_49:logic_trm_c_repair_if_c_fail` | 0.7600 | 0.7600 | 2 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_49:logic_trm_dual_repair_if_any_sig_fail` | 0.7600 | 0.7600 | 2 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_55:logic_trm_c_repair_if_c_fail` | 0.8500 | 0.8000 | 1 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_55:logic_trm_dual_repair_if_any_sig_fail` | 0.8500 | 0.8000 | 1 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_84:logic_trm_c_repair_if_c_fail` | 0.8800 | 0.8400 | 1 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_84:logic_trm_dual_repair_if_any_sig_fail` | 0.8800 | 0.8400 | 1 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_92:logic_trm_c_repair_if_c_fail` | 0.7600 | 0.7600 | 4 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_92:logic_trm_dual_repair_if_any_sig_fail` | 0.7600 | 0.7600 | 4 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_94:logic_trm_c_repair_if_c_fail` | 0.8500 | 0.7000 | 3 | `False` | `reject_or_abstain` |
| `train` | `intellect_3_logic_94:logic_trm_dual_repair_if_any_sig_fail` | 0.8500 | 0.7000 | 3 | `False` | `reject_or_abstain` |
| `val_seen` | `intellect_3_logic_0:logic_trm_c_repair_if_c_fail` | 0.8400 | 0.8400 | 2 | `False` | `reject_or_abstain` |
| `val_seen` | `intellect_3_logic_0:logic_trm_dual_repair_if_any_sig_fail` | 0.8400 | 0.8400 | 2 | `False` | `reject_or_abstain` |
| `holdout_seen` | `intellect_3_logic_88:logic_trm_c_repair_if_c_fail` | 0.7000 | 0.7000 | 4 | `False` | `reject_or_abstain` |
| `holdout_seen` | `intellect_3_logic_88:logic_trm_dual_repair_if_any_sig_fail` | 0.7000 | 0.7000 | 4 | `False` | `reject_or_abstain` |
