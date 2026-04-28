# Mixed Contract Compactification Study Plan

## Hypothesis

Small LLMs can act as proposal engines when explicit MeTTa/TRM gates own observable output contracts such as word count, JSON schema, ASCII tree shape, choice labels, and delimiter formats.

## Arms

- `baseline`: intentionally loose plain-output candidate.
- `pure_trm`: typed but not fully repair-gated candidate.
- `metta_runtime`: gate-aware candidate without final canonical repair in every case.
- `metta_runtime_repair`: canonical deterministic repair target for validator smoke; repair-prompt gate for live local 3B runs.

## Metrics

- `contract_valid`: output satisfies the observable contract.
- `semantic_valid`: output preserves the row's minimal semantic target.
- `exact_success`: both contract and semantic checks pass.

## Promotion Rule

Promote to local 3B benchmarking only if the no-model validator catches the intended failures across all included env families and the row schema is stable.

## Stop Rule

If a positive result can be produced only by canonical postprocessing, report it as verifier-owned repair and do not call it trained TRM lift.

## Current Live Smoke

The first 12-row local 3B seed run is promising only for the repair-gated arm: `baseline` 5/12, `pure_trm` 6/12, `metta_runtime` 6/12, `metta_runtime_repair` 8/12. The next iteration should test whether the repair-gated lift survives the planned 50-row held-out suite.
