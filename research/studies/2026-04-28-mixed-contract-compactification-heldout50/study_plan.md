# Heldout50 Study Plan

## Hypothesis

MeTTa-scaffolded repair gating should improve exact mixed-contract validity over baseline and prompt-only TRM on held-out rows, but gains must be separated from learned TRM lift.

## Arms

- `baseline`: direct final answer prompt.
- `pure_trm`: TRM contract prompt.
- `metta_runtime`: MeTTa/TRM gate prompt.
- `metta_runtime_repair`: repair-prompt gate using public validator feedback.

## Metrics

- `exact_success`
- `contract_valid`
- `semantic_valid`
- per-family exact rate
- child RSS and job-cap outcome

## Promotion Rule

Promote this to paper material as held-out local 3B evidence because `metta_runtime_repair` remains positive and the result table explicitly separates prompt-only, repair-prompt, and no-model evidence.

## Stop Rule

If the lift is concentrated in easy choice or delimiter rows, expand harder schema/tree rows before making a general compactification claim.

## Result Snapshot

The full local Qwen2.5-3B Q4 run scored `baseline` 23/50 exact, `pure_trm` 27/50, `metta_runtime` 32/50, and `metta_runtime_repair` 37/50. The paper-safe claim is methodology lift from structured MeTTa/TRM framing and public-validator repair, not trained TRM capability.
