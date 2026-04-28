# Mixed Contract Compactification Study Plan

## Hypothesis

Small LLMs can act as proposal engines when explicit MeTTa/TRM gates own observable output contracts such as word count, JSON schema, ASCII tree shape, choice labels, and delimiter formats.

## Arms

- `baseline`: intentionally loose plain-output candidate.
- `pure_trm`: typed but not fully repair-gated candidate.
- `metta_runtime`: gate-aware candidate without final canonical repair in every case.
- `metta_runtime_repair`: canonical deterministic repair target for validator smoke only.

## Metrics

- `contract_valid`: output satisfies the observable contract.
- `semantic_valid`: output preserves the row's minimal semantic target.
- `exact_success`: both contract and semantic checks pass.

## Promotion Rule

Promote to local 3B benchmarking only if the no-model validator catches the intended failures across all included env families and the row schema is stable.

## Stop Rule

If a positive result can be produced only by canonical postprocessing, report it as verifier-owned repair and do not call it trained TRM lift.
