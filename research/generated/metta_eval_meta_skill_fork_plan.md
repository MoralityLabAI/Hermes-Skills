# MeTTa Eval Meta-Skill Fork Plan

Generated: `2026-04-26T15:32:10.601878+00:00`

This plan composes MeTTa gate circuits with Pure-TRM-Trainer and PrimeLab. MeTTa owns the gate grammar, Pure-TRM-Trainer owns controller/corpus training, and PrimeLab owns env/rubric/eval or QLoRA workflows.

## Source Infrastructure

- Pure-TRM-Trainer: [pure-trm-trainer](<C:\projects\Hermes-Skills\Hermes Skills\pure-trm-trainer>)
- PrimeLab Hermes: [primelab-hermes](<C:\projects\Hermes-Skills\Hermes Skills\primelab\primelab-hermes>)

## Forks

| Fork | Env families | Bottleneck | Pure-TRM export | PrimeLab export | Claim boundary |
| --- | --- | --- | --- | --- | --- |
| `metta-flow-trm-circuit-controller` | `all gate-circuit forks` | skill-flow routing and typed failure logging | `route_error`, `repair_success`, `repair_failure`, `commit_error` | `baseline rollout receipts`, `rubric brittleness notes` | Meta-controller infrastructure; proves eval discipline only after live env arms are run. |
| `metta-intellect3-logic-signature-gate` | `intellect3_logic`, `logic_env` | grid candidate plausibility plus row/column/object signature repair | `grid_candidate`, `signature_mismatch`, `projection_success`, `critic_false_positive` | `logic env baseline`, `rollout grid traces`, `rubric exactness and cell-accuracy metrics` | Hard-env positive target; valid only when puzzle-provided constraints, not leaked answers, drive projection. |
| `metta-intellect3-math-teacher-auditor` | `intellect3_math`, `math500`, `aime2024`, `aime2025`, `aime2026` | raw solve quality and candidate selection under 100B-class reasoning pressure | `numeric_error_archetype`, `candidate_selection`, `verifier_false_positive`, `abstain_correct` | `teacher candidate eval`, `hosted INTELLECT-3 or supported-model receipts`, `QLoRA candidate-auditor lane` | Negative/control boundary for small-model solving; gains must come from candidate auditing, not invented math. |
| `metta-structured-contract-repair-lane` | `pydantic_adherence`, `ascii_tree`, `ifeval_contract_family`, `boolq_choice_contract` | observable contract validity and deterministic repair | `constraint_error`, `repair_success`, `repair_failure`, `format_vs_semantics_split` | `harder schema env variants`, `rubric traps`, `baseline eval receipts` | Best compactification lane; does not imply latent reasoning gain. |
| `metta-psycho-item-vector-stability` | `psycho_bench` | aggregate reward hides item-level profile geometry | `item_changed`, `subscale_drift`, `stability_pass`, `profile_regression` | `repeated profile evals`, `rubric variance report`, `rollout item vectors` | Interpretability and stability lane, not conventional exact-answer correctness. |

## Gate Plans

### `metta-flow-trm-circuit-controller`

- Source skills: `metta-eval-optimizer-hermes`, `trm-observability-workflow`
- MeTTa gates: `route_gate`, `validate_gate`, `repair_gate`, `commit_gate`, `learning_gate`
- Benchmark arms: `baseline`, `pure_trm`, `metta_runtime`, `metta_runtime_repair`
- Next experiment: Use this controller plan to fork structured-map and Intellect-3 logic first.

### `metta-intellect3-logic-signature-gate`

- Source skills: `intellect3-logic-hermes`, `primehub-hard-reasoning-logic-hermes`
- MeTTa gates: `proposal_gate`, `signature_validate_gate`, `min_edit_projection_gate`, `commit_gate`
- Benchmark arms: `baseline`, `pure_trm`, `metta_runtime_repair`
- Next experiment: Run a small live local 3B grid-candidate probe and classify proposal tiers before projection.

### `metta-intellect3-math-teacher-auditor`

- Source skills: `intellect3-math-hermes`, `primehub-hard-reasoning-numeric-hermes`
- MeTTa gates: `candidate_parse_gate`, `invariant_validate_gate`, `numeric_error_gate`, `teacher_candidate_commit_gate`
- Benchmark arms: `baseline`, `pure_trm`, `teacher_candidate_metta`
- Next experiment: Generate or import teacher candidate sets, then test whether MeTTa/TRM selects better than keyword routing.

### `metta-structured-contract-repair-lane`

- Source skills: `primehub-structured-map-hermes`, `primehub-choice-contract-hermes`, `primehub-constraint-summarize-hermes`
- MeTTa gates: `contract_select_gate`, `field_validate_gate`, `canonical_repair_gate`, `commit_gate`
- Benchmark arms: `baseline`, `pure_trm`, `metta_runtime`, `metta_runtime_repair`
- Next experiment: Expand local 3B suite from six cases to a held-out 20-50 row mixed contract suite.

### `metta-psycho-item-vector-stability`

- Source skills: `primehub-structured-map-hermes`
- MeTTa gates: `item_vector_validate_gate`, `subscale_project_gate`, `profile_delta_audit_gate`, `stability_commit_gate`
- Benchmark arms: `baseline`, `pure_trm`, `metta_runtime`
- Next experiment: Run repeated local/profile probes and report variance before claiming scalar improvement.
