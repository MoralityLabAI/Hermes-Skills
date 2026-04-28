# Mixed Contract Validator Smoke

Evidence class: `no_model_validator_smoke`

This run tests frozen rows and exact validators for the mixed-contract compactification study. It does not use model calls and should not be reported as benchmark lift.

## Arm Summary

| Arm | Rows | Contract valid | Semantic valid | Exact success | Exact rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `canonical_target` | 50 | 50 | 50 | 50 | 1.0000 |

## Failure Rows

No failures.

## Interpretation

- The validator surface catches format-only, schema-only, and semantic-label failures separately.
- The `metta_runtime_repair` arm is canonical deterministic repair, not a learned or live model result.
- The next valid benchmark step is to replace deterministic candidates with local 3B completions while preserving these row IDs and validators.
