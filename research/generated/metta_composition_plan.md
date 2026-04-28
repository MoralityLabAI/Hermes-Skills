# MeTTa Composition Plan For TRM-Infused Hermes Skills

Generated: `2026-04-26T15:39:48.318889+00:00`

This plan composes Hermes skills into TRM-aware MeTTa circuits. It separates skill composition from eval execution and training.

## Sources

- Skill registry: [skill_registry.json](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\skill_registry.json>)
- TRM role imprint: [role_based_imprint.md](<C:\projects\Hermes-Skills\Hermes Skills\data\primehub_skill_trm_matrix\latest\role_based_imprint.md>)

## Composition Summary

| Circuit | Class | Status | Source skills | TRM roles | Claim boundary |
| --- | --- | --- | --- | --- | --- |
| `contract_compactification_circuit` | `compactifiable` | `ready` | `primehub-choice-contract-hermes`, `primehub-structured-map-hermes`, `primehub-constraint-summarize-hermes` | `choice_contract`, `structured_map` | Good compactification target; supports control-plane capability, not latent reasoning gain. |
| `tool_schema_composition_circuit` | `compactifiable` | `ready` | `trm-mcp`, `primehub-structured-map-hermes`, `primehub-choice-contract-hermes` | `structured_map`, `choice_contract` | Tool calls can compactify when schemas and arguments are verifier-visible. |
| `intellect3_logic_signature_circuit` | `symbolically_amplifiable` | `ready` | `intellect3-logic-hermes`, `primehub-hard-reasoning-logic-hermes`, `trm-public-rationale-chain` | `hard_reasoning_logic`, `structured_map` | Hard positive target; projection must use puzzle constraints rather than leaked target grids. |
| `intellect3_math_teacher_auditor_circuit` | `scale_sensitive` | `ready` | `intellect3-math-hermes`, `primehub-hard-reasoning-numeric-hermes` | `hard_reasoning_numeric` | Use as boundary case; MeTTa/TRM audits candidates but does not replace high-scale solving. |
| `safety_abstain_veto_circuit` | `compactifiable_with_domain_boundary` | `ready` | `primehub-abstain-guard-hermes`, `primehub-structured-map-hermes` | `abstain_guard`, `structured_map` | Can test routing and refusal format; not evidence of high-stakes advice quality. |
| `psycho_item_vector_composition_circuit` | `interpretability_only` | `ready` | `primehub-structured-map-hermes` | `structured_map` | Profile stability and interpretability lane; scalar gain alone is not enough. |

## Gate Details

### `contract_compactification_circuit`

- MeTTa gates: `route_gate`, `contract_select_gate`, `validate_gate`, `repair_gate`, `commit_gate`, `learning_gate`
- Pure-TRM exports: `constraint_error`, `repair_success`, `format_vs_semantics_split`, `commit_error`
- PrimeLab exports: `hard schema env variants`, `literal-count rubric traps`, `baseline eval receipts`
- Benchmark arms: `baseline`, `pure_trm`, `metta_runtime`, `metta_runtime_repair`

### `tool_schema_composition_circuit`

- MeTTa gates: `tool_route_gate`, `schema_memory_gate`, `argument_validate_gate`, `json_repair_gate`, `commit_gate`
- Pure-TRM exports: `route_error`, `retrieval_miss`, `json_repair_success`, `tool_commit_error`
- PrimeLab exports: `tool-use env receipt`, `argument rubric failure clusters`
- Benchmark arms: `baseline`, `pure_trm`, `metta_runtime`, `metta_runtime_repair`

### `intellect3_logic_signature_circuit`

- MeTTa gates: `proposal_gate`, `constraint_parse_gate`, `signature_validate_gate`, `min_edit_projection_gate`, `commit_gate`
- Pure-TRM exports: `grid_candidate`, `signature_mismatch`, `projection_success`, `critic_false_positive`
- PrimeLab exports: `logic rollout trace`, `cell-accuracy metric`, `signature rubric`
- Benchmark arms: `baseline`, `pure_trm`, `metta_runtime_repair`

### `intellect3_math_teacher_auditor_circuit`

- MeTTa gates: `candidate_parse_gate`, `invariant_validate_gate`, `numeric_error_gate`, `teacher_candidate_commit_gate`
- Pure-TRM exports: `numeric_error_archetype`, `candidate_selection`, `verifier_false_positive`, `abstain_correct`
- PrimeLab exports: `teacher candidate receipt`, `math hosted eval receipt`, `QLoRA candidate-auditor manifest`
- Benchmark arms: `baseline`, `pure_trm`, `teacher_candidate_metta`

### `safety_abstain_veto_circuit`

- MeTTa gates: `risk_route_gate`, `policy_validate_gate`, `abstain_or_answer_gate`, `safe_format_gate`, `commit_gate`
- Pure-TRM exports: `risk_route_error`, `critic_false_positive`, `critic_false_negative`, `safe_format_repair`
- PrimeLab exports: `borderline safety env receipt`, `advice-quality rubric split`
- Benchmark arms: `baseline`, `pure_trm`, `metta_runtime`

### `psycho_item_vector_composition_circuit`

- MeTTa gates: `item_vector_validate_gate`, `subscale_project_gate`, `profile_delta_audit_gate`, `stability_commit_gate`
- Pure-TRM exports: `item_changed`, `subscale_drift`, `stability_pass`, `profile_regression`
- PrimeLab exports: `repeated profile eval receipts`, `variance report`, `item-vector rollout table`
- Benchmark arms: `baseline`, `pure_trm`, `metta_runtime`
