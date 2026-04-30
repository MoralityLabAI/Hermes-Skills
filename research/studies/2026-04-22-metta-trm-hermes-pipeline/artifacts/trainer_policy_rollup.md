# MeTTa Trainer-Policy Rollup

## Structured Map Bundle

Bundle:

- `artifacts/primehub_structured_map_trainer_policy/metta_trainer_policy_bundle.summary.json`

Rollup:

- `artifacts/primehub_structured_map_trainer_policy/rollup/metta_trainer_policy_rollup.manifest.json`

Observed trainer-policy bridge:

- cluster: `structured_map`
- support tier: `format_support`
- rows: `63`
- average supervision weight: `1.5195`

Local harness receipts:

- critic bucket accuracy: `0.8462`
- retriever exact match: `0.6154`
- critic-gated router exact match: `0.6154`

Read:

- the MeTTa scorecard is now a real TRM training bundle, not just a diagnostic artifact
- the strongest structured-map trainer lanes are transport, selection, and failure-localization
- `task_success` and `contract_validity` remain the weak families inside this synthetic trainer slice

## Constraint Summarization Bundle

Bundle:

- `artifacts/if_summarize_judge_trainer_policy/metta_trainer_policy_bundle.summary.json`

Rollup:

- `artifacts/if_summarize_judge_trainer_policy/rollup/metta_trainer_policy_rollup.manifest.json`

Observed trainer-policy bridge:

- cluster: `constraint_summarize`
- support tier: `format_support`
- rows: `446`
- average supervision weight: `1.6062`

Local harness receipts:

- critic bucket accuracy: `0.8605`
- retriever exact match: `0.6628`
- critic-gated router exact match: `0.6628`
- critic-gated router abstain rate: `0.0116`

Read:

- `if_summarize_judge` is now the clearest proof that MeTTa can enrich TRM training, not just runtime prompting
- the trainer surface is broad enough to support separate profile-selection, contract-validity, repair, and transport targets
- the weakest retrieval families in this slice are still the most specific symbolic targets, especially `repair_success` and profile-specific selection labels

## Current Take

The practical win from MeTTa is now two-stage:

- it expands one symbolic package into `5-6x` denser supervision
- it compiles that supervision into a normal TRM trainer bundle that the local critic/retriever/router harness can train on immediately
