# Real Tool-Contract Router Study Plan

## Hypothesis

MeTTa/TRM scaffolding should improve real tool-call reliability when the tool schema, argument types, and safety policy are verifier-visible.

## Arms

- `baseline`: direct tool-call JSON prompt.
- `pure_trm`: TRM contract prompt with the selected tool schemas.
- `metta_runtime`: MeTTa schema-memory and route-gate prompt.
- `metta_runtime_repair`: public-validator feedback repair prompt.

## Metrics

- valid JSON rate
- valid schema rate
- exact tool route rate
- exact argument rate
- safe-to-execute correctness
- unsafe commit rate

## Stop Rule

If MeTTa only fixes JSON syntax while selecting the wrong tool family, split the lane into router TRM and argument-repair TRM before adding more rows.

## Current Status

- Live local 3B result exists.
- The strongest signal is schema/tool-route improvement, not exact tool-call success.
- Public repair reduced unsafe commits from 2 to 1 but did not improve exact success beyond MeTTa runtime.
