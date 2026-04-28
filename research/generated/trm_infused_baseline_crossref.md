# TRM-Infused Hermes Benchmark Cross-Ref

## Source Chat

- session: `C:\Users\patri\.codex\sessions\2026\04\19\rollout-2026-04-19T22-45-11-019da8c7-1000-7920-8a73-f020962d546d.jsonl`
- timestamp: `2026-04-22T20:29:34.748Z`
- extracted links: `11`
- missing-env rerun source: `chat_message_fallback`

## Artifact Spine

| Artifact | Type | Key Read | Path |
| --- | --- | --- | --- |
| BlueBeam handoff | benchmark handoff | 90/90; positives `20`; TRM rows `195` | [README.md](<C:\projects\Hermes-Skills\Hermes Skills\data\handoffs\bluebeam_mechinterp_2026-04-16\README.md>) |
| Missing-env rerun | coverage rerun | task_complete `32`; success `32`; envs `16` | [summary.json](<C:\projects\Hermes-Skills\Hermes Skills\data\job_limited_runs\primehub-missing-envs-rerun-20260420.summary.json>) |
| Final gapfill | gapfill audit | tasks `4`; `passthrough` bridge failures, `verbatim_copy` success | [overnight_primehub_benchmark.stout.jsonl](<C:\projects\Hermes-Skills\Hermes Skills\data\primehub_final_eligible_gapfill_20260420\overnight_primehub_benchmark.stout.jsonl>) |
| Role imprint | TRM role cards | clusters `6`; strongest action-bearing support in `choice_contract` / `structured_map` / `internal_action` | [role_based_imprint.json](<C:\projects\Hermes-Skills\Hermes Skills\data\primehub_skill_trm_matrix\latest\role_based_imprint.json>) |
| Baseline vs mining | trainer-policy rerun pair | overlapping rows `26`; positive deltas `2` | [baseline ledger](<C:\projects\Hermes-Skills\Hermes Skills\data\primehub_trainer_policy_baseline_rerun_20260421\ledger.jsonl>) |
| Pressure slice | wider `choice_contract` check | comparisons `22`; contract>baseline `1` | [pressure ledger](<C:\projects\Hermes-Skills\Hermes Skills\data\primehub_choice_contract_pressure_20260421\ledger.jsonl>) |
| SimpleQA verified proof | transport proof | tasks `4`; visible output true `4`; model fallbacks `0` | [ledger.jsonl](<C:\projects\Hermes-Skills\Hermes Skills\data\primehub_simpleqa_verified_proof_20260422\ledger.jsonl>) |

## Key Deltas

- `boolq` / `qwen35_27b` / `two-model-contract-repair-v1`: baseline `0.0` -> mining `1.0` (delta `+1.0000`)
- `antislop` / `qwen35_27b` / `two-model-contract-repair-v1`: baseline `12.0` -> mining `12.0` (delta `+0.0000`)
- pressure slice `winogrande`: baseline `1.0` / contract `1.0` / abstain `1.0`

## Role Cards

| Cluster | Support Tier | Rows | Exact+ | Coverage | Critic Acc | Route Abstain |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| abstain_guard | critic_guard | 17 | 2 | 0.1176 | 1.0000 | 1.0000 |
| choice_contract | action_support | 81 | 35 | 0.4321 | 0.3077 | 0.3077 |
| hard_reasoning_logic | critic_verify_sparse | 20 | 3 | 0.1500 | 0.5714 | 0.5714 |
| hard_reasoning_numeric | critic_verify_sparse | 35 | 3 | 0.0857 | 0.6000 | 0.6000 |
| internal_action | narrow_action_support | 2 | 2 | 1.0000 | 1.0000 | 0.0000 |
| structured_map | format_support | 16 | 4 | 0.2500 | 0.0000 | 0.0000 |

## Gapfill Status

- `qwen35_9b` / `passthrough` / `single-model-baseline`: `execution_failure`
- `qwen35_9b` / `verbatim_copy` / `single-model-baseline`: `success`
- `qwen35_27b` / `passthrough` / `single-model-baseline`: `execution_failure`
- `qwen35_27b` / `verbatim_copy` / `single-model-baseline`: `success`

## SimpleQA Proof

- `qwen35_27b` / `simpleqa_verified_2` / `single-model-baseline`: reward `0.0`, visible_output_true `1`, model_client_fallbacks `0`
- `qwen35_27b` / `simpleqa_verified_2` / `two-model-contract-repair-v1`: reward `0.0`, visible_output_true `1`, model_client_fallbacks `0`
- `qwen35_27b` / `simpleqa_verified` / `single-model-baseline`: reward `0.0`, visible_output_true `1`, model_client_fallbacks `0`
- `qwen35_27b` / `simpleqa_verified` / `two-model-contract-repair-v1`: reward `0.0`, visible_output_true `1`, model_client_fallbacks `0`

## Linked Studies

- [README.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-primehub-structured-map-retrieval\README.md>)
- [README.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\README.md>)
- [2026-04-22-hermes-trm-weekly-draft.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\paper_drafts\2026-04-22-hermes-trm-weekly-draft.md>)
- [2026-04-26-symbolic-closure-threshold-addendum.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\paper_drafts\2026-04-26-symbolic-closure-threshold-addendum.md>)
- [symbolic_closure_threshold.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\symbolic_closure_threshold_suite\symbolic_closure_threshold.results.md>)
- [2026-04-26-metta-eval-meta-skills-addendum.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\paper_drafts\2026-04-26-metta-eval-meta-skills-addendum.md>)
- [metta_eval_meta_skill_fork_plan.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\metta_eval_meta_skill_fork_plan.md>)
- [2026-04-26-metta-composition-skill-addendum.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\paper_drafts\2026-04-26-metta-composition-skill-addendum.md>)
- [metta_composition_plan.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\metta_composition_plan.md>)
- [2026-04-26-intellect3-logic-flow-policy-addendum.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\paper_drafts\2026-04-26-intellect3-logic-flow-policy-addendum.md>)
- [intellect3_logic_flow_policy_sweep.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\intellect3_logic_flow_policy_sweep\intellect3_logic_flow_policy_sweep.results.md>)
- [2026-04-26-near-miss-repair-curriculum-addendum.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\paper_drafts\2026-04-26-near-miss-repair-curriculum-addendum.md>)
- [near_miss_repair_curriculum.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\near_miss_repair_curriculum\near_miss_repair_curriculum.md>)
- [2026-04-26-near-miss-repair-split-methodology-addendum.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\paper_drafts\2026-04-26-near-miss-repair-split-methodology-addendum.md>)
- [near_miss_repair_splits.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\near_miss_repair_curriculum\splits\near_miss_repair_splits.md>)
- [2026-04-26-local-3b-repair-training-rudder-addendum.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\paper_drafts\2026-04-26-local-3b-repair-training-rudder-addendum.md>)
- [local_3b_repair_training_rudder.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\local_3b_repair_training_rudder_benchmark\local_3b_repair_training_rudder.results.md>)
- [2026-04-28-local-3b-metta-action-space-rudder-addendum.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\paper_drafts\2026-04-28-local-3b-metta-action-space-rudder-addendum.md>)
- [local_3b_metta_action_space_rudder results](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\local_3b_metta_action_space_rudder_benchmark\local_3b_repair_training_rudder.results.md>)
- [static_gate_failure_closure.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\local_3b_metta_static_gate_failure_closure\static_gate_failure_closure.results.md>)
- [c_signature_commit_trm_pack.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\c_signature_commit_trm_pack\c_signature_commit_trm_pack.md>)
- [c_signature_commit_trm_training_plan.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\c_signature_commit_trm_pack\c_signature_commit_trm_training_plan.md>)
- [run_c_signature_commit_trm_jobcap.ps1](<C:\projects\Hermes-Skills\Hermes Skills\research\scripts\run_c_signature_commit_trm_jobcap.ps1>)
- [c_signature_commit_policy_sweep.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\c_signature_commit_policy_sweep\c_signature_commit_policy_sweep.results.md>)
- [c_signature_postrepair_verifier.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\c_signature_postrepair_verifier_sweep\c_signature_postrepair_verifier.results.md>)
- [c_signature_postrepair_verifier_contract.metta](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\c_signature_postrepair_verifier_sweep\c_signature_postrepair_verifier_contract.metta>)
- [methodology_lift.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\metta_trm_methodology_lift_matrix\methodology_lift.results.md>)
- [methodology_lift_contracts.metta](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\metta_trm_methodology_lift_matrix\methodology_lift_contracts.metta>)
- [2026-04-28-metta-trm-methodology-lift-matrix-addendum.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\paper_drafts\2026-04-28-metta-trm-methodology-lift-matrix-addendum.md>)
- [main.tex](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\paper_latex\metta_trm_repair_addendum\main.tex>)
- [data_campaign_plan.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\paper_latex\metta_trm_repair_addendum\data_campaign_plan.md>)
