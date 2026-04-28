# Hard Ablation30 Study Plan

## Hypothesis

If MeTTa/TRM scaffolding is doing more than output-format nudging, it should retain lift on numeric, logic, computed-schema, state-sequence, and deep-tree contracts. Public validator feedback should outperform blind repair on the subset where `metta_runtime` initially fails.

## Arms

- `baseline`: direct final answer prompt.
- `pure_trm`: TRM contract prompt.
- `metta_runtime`: MeTTa/TRM gate prompt.
- `metta_runtime_blind_repair`: second pass without validator feedback.
- `metta_runtime_repair`: second pass with public validator feedback.

## Metrics

- `exact_success`
- `contract_valid`
- `semantic_valid`
- per-family exact rate
- repair opportunity exact rate on rows where `metta_runtime` failed
- child RSS and job-cap outcome

## Claim Rule

Report this as a hard-suite ablation, not as trained TRM lift. The main comparison is `metta_runtime_blind_repair` versus `metta_runtime_repair` on failed MeTTa runtime rows.

## Current Status

- On this local 3B run, feedback repair scored 13/30 exact versus baseline 12/30, blind repair 12/30, and MeTTa runtime 9/30.
- On the 21 failed MeTTa-runtime opportunities, feedback repair fixed 4 rows versus 3 rows for blind repair.
