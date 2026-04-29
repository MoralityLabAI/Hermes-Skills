# Study Plan

## Hypothesis

MeTTa/TRM signature projection can amplify hard logic only when a small model emits enough verifier-visible grid state. The gain should appear in `metta_signature_projection`, not necessarily in raw `metta_runtime`.

## Arms

- `baseline`: direct grid answer.
- `pure_trm`: TRM-style contract parsing prompt.
- `metta_runtime`: MeTTa/TRM gate prompt without deterministic projection.
- `metta_signature_projection`: deterministic min-edit projection from the `metta_runtime` candidate to public prompt constraints.

## Metrics

- `exact_success`: grid matches the unique solver-derived target.
- `contract_valid`: grid satisfies public constraints.
- `avg_cell_accuracy`: cell-level agreement with the held-out target.
- `proposal_tier`: `none`, `weak_surface`, `partial_semantic`, or `full_candidate`.

## Promotion Rule

Promote as hard-env evidence only if projection improves exactness/cell accuracy and the audit shows `target_grid_in_prompt=false`, `projection_uses_target_grid=false`, and `unique_solution_from_prompt_constraints=true`.

## Stop Rule

If raw 3B outputs are mostly `none`, this lane needs a stronger model or a public-trace scaffold before projection can be meaningfully tested.
