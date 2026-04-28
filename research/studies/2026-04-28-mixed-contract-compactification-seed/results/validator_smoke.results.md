# Mixed Contract Validator Smoke

Evidence class: `no_model_validator_smoke`

This run tests frozen rows and exact validators for the mixed-contract compactification study. It does not use model calls and should not be reported as benchmark lift.

## Arm Summary

| Arm | Rows | Contract valid | Semantic valid | Exact success | Exact rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 12 | 2 | 7 | 2 | 0.1667 |
| `metta_runtime` | 12 | 11 | 11 | 11 | 0.9167 |
| `metta_runtime_repair` | 12 | 12 | 12 | 12 | 1.0000 |
| `pure_trm` | 12 | 8 | 10 | 8 | 0.6667 |

## Failure Rows

| Arm | Row | Family | Contract | Semantic | Output |
| --- | --- | --- | ---: | ---: | --- |
| `baseline` | `ifsum_lakebed_001` | `if_summarize_judge` | 0 | 1 | <code>Mars rover samples show ancient lakebed.</code> |
| `baseline` | `ifsum_gate_question_002` | `if_summarize_judge` | 0 | 1 | <code>Symbolic gates reduce invalid contract commits.</code> |
| `pure_trm` | `ifsum_gate_question_002` | `if_summarize_judge` | 0 | 1 | <code>Can symbolic gates reduce invalid contract commits?</code> |
| `metta_runtime` | `ifsum_gate_question_002` | `if_summarize_judge` | 0 | 0 | <code>Could symbolic gates reduce invalid commits today?</code> |
| `baseline` | `pyd_task_003` | `pydantic_adherence` | 0 | 0 | <code>{task: collect rows, priority: urgent, due_date: May 2, blocked: no}</code> |
| `pure_trm` | `pyd_task_003` | `pydantic_adherence` | 0 | 0 | <code>{&quot;task&quot;:&quot;collect rows&quot;,&quot;priority&quot;:&quot;high&quot;,&quot;due_date&quot;:&quot;2026-05-02&quot;}</code> |
| `baseline` | `pyd_verifier_004` | `pydantic_adherence` | 0 | 0 | <code>{&quot;name&quot;:&quot;verifier&quot;,&quot;retries&quot;:&quot;two&quot;,&quot;safe&quot;:&quot;yes&quot;}</code> |
| `baseline` | `ascii_flat_005` | `ascii_tree` | 0 | 1 | <code>root: rows, validators, results</code> |
| `baseline` | `ascii_nested_006` | `ascii_tree` | 0 | 1 | <code>pipeline\n- parse\n- classify\n- commit</code> |
| `pure_trm` | `ascii_nested_006` | `ascii_tree` | 0 | 1 | <code>pipeline\n\|-- parse\n\|-- classify\n`-- commit</code> |
| `baseline` | `ifeval_bullets_007` | `ifeval_contract_family` | 0 | 1 | <code>The steps are parse, validate, and commit.</code> |
| `baseline` | `ifeval_json_array_008` | `ifeval_contract_family` | 0 | 0 | <code>Route, Repair, Commit</code> |
| `baseline` | `boolq_nile_009` | `boolq_choice_contract` | 0 | 0 | <code>Yes, true.</code> |
| `pure_trm` | `choice_letter_011` | `choice_contract` | 0 | 0 | <code>Commit: B</code> |
| `baseline` | `pipe_triplet_012` | `structured_contract` | 0 | 0 | <code>2026/04/28 \| trm \| ready</code> |

## Interpretation

- The validator surface catches format-only, schema-only, and semantic-label failures separately.
- The `metta_runtime_repair` arm is canonical deterministic repair, not a learned or live model result.
- The next valid benchmark step is to replace deterministic candidates with local 3B completions while preserving these row IDs and validators.
