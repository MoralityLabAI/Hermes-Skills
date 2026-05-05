# MeTTa TRM Meta-Skill Contract

This contract defines the minimum viable orchestration layer for MeTTa-assisted TRM compactification.

## Package Inputs

Accept one or more of:

- Natural-language task or benchmark failure.
- Existing Hermes skill name.
- Target env or env family.
- Prior trace, play diary, MCP lookup receipt, or benchmark scorecard.

## Package Outputs

A package should contain:

- `package.manifest.json`
- `package.metta`
- `contracts.metta`
- `retrieval_policy.metta`
- `failure_modes.metta`
- `examples/minimal_valid.json`

Use only atom heads already supported by `metta-trm-hermes-pipeline` unless a compiler extension is deliberately planned.

## Verification Scores

The verifier emits five scores from `0.0` to `1.0`:

- `syntax`: all non-comment MeTTa lines parse as single top-level atoms with supported heads.
- `contract`: goals, answer shapes, constraints, forbids, examples, and validation paths are present.
- `retrieval`: query cues and retrieval priorities are present.
- `repair`: failure modes, repair hints, and trace labels are present.
- `trainer_export`: enough typed material exists to produce role-specific TRM rows.

The overall score is the arithmetic mean. A package may be used for training rows at `0.70+`; require `0.85+` before using it as a runtime packet without human review.

## Benchmark Arms

Use the same arm names across studies:

- `baseline`
- `pure_trm`
- `metta_runtime`
- `metta_runtime_repair`
- `teacher_candidate_metta`

## Skill Patch Categories

Allowed patch categories:

- `runtime_packet_injection`
- `retrieval_policy_update`
- `repair_gate_update`
- `validator_update`
- `commit_veto_update`
- `training_corpus_expansion`
- `no_patch_more_data`

Every proposed patch must include evidence, expected metric movement, rollback condition, and claim label.

