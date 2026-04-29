# Real Tool-Contract Router Validator Smoke

Evidence class: `no_model_validator_smoke`

| Arm | Rows | Contract valid | Semantic valid | Exact success | Exact rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `canonical_target` | 32 | 32 | 32 | 32 | 1.0000 |

## Failure Rows

No failures.

## Interpretation

- The validator separates valid JSON/schema/tool-call shape from exact tool, argument, and safety semantics.
- This is a no-model canonical smoke. The next benchmark should compare baseline, pure TRM, MeTTa runtime, and repair arms on the same row IDs.
