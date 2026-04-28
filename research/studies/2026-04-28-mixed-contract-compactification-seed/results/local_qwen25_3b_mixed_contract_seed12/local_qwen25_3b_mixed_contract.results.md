# Local Qwen2.5-3B Mixed Contract Smoke

Generated: `2026-04-28T16:27:13.255858+00:00`

Evidence class: `live_model_local_3b`

Model: `D:\Research_Engine\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf`
llama.cpp completion: `D:\Research_Engine\tools\llama.cpp-b8922-cuda12.4\llama-completion.exe`
Peak child RSS: `2371.06 MB`

This run replaces deterministic seed candidates with local 3B completions for the same row IDs and validators. It is a smoke, not the full 50-row held-out suite.

## Arm Summary

| Arm | Rows | Contract valid | Semantic valid | Exact success | Exact rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 12 | 7 | 6 | 5 | 0.4167 |
| `metta_runtime` | 12 | 8 | 8 | 6 | 0.5000 |
| `metta_runtime_repair` | 12 | 9 | 10 | 8 | 0.6667 |
| `pure_trm` | 12 | 9 | 8 | 6 | 0.5000 |

## Case Detail

| Row | Family | Arm | Exact | Contract | Semantic | Output |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `ifsum_lakebed_001` | `if_summarize_judge` | `baseline` | 0 | 0 | 0 | <code>Ancient lakebed found on Mars</code> |
| `ifsum_lakebed_001` | `if_summarize_judge` | `pure_trm` | 0 | 1 | 0 | <code>Ancient lakebed found in rover samples</code> |
| `ifsum_lakebed_001` | `if_summarize_judge` | `metta_runtime` | 0 | 1 | 0 | <code>Ancient lakebed found in Martian samples</code> |
| `ifsum_lakebed_001` | `if_summarize_judge` | `metta_runtime_repair` | 0 | 1 | 0 | <code>Ancient lakebed found in Martian samples</code> |
| `ifsum_gate_question_002` | `if_summarize_judge` | `baseline` | 0 | 0 | 1 | <code>Do symbolic gates reduce invalid contract commits?</code> |
| `ifsum_gate_question_002` | `if_summarize_judge` | `pure_trm` | 1 | 1 | 1 | <code>How do symbolic gates reduce invalid contract commits?</code> |
| `ifsum_gate_question_002` | `if_summarize_judge` | `metta_runtime` | 1 | 1 | 1 | <code>How do symbolic gates reduce invalid contract commits?</code> |
| `ifsum_gate_question_002` | `if_summarize_judge` | `metta_runtime_repair` | 1 | 1 | 1 | <code>How do symbolic gates reduce invalid contract commits?</code> |
| `pyd_task_003` | `pydantic_adherence` | `baseline` | 0 | 0 | 0 | <code>{&quot;rows&quot;: [{&quot;priority&quot;: &quot;high&quot;, &quot;due_date&quot;: &quot;2026-05-02&quot;, &quot;blocked&quot;: false}]}</code> |
| `pyd_task_003` | `pydantic_adherence` | `pure_trm` | 0 | 1 | 0 | <code>{\n  &quot;task&quot;: &quot;str&quot;,\n  &quot;blocked&quot;: true,\n  &quot;due_date&quot;: &quot;2026-05-02&quot;,\n  &quot;priority&quot;: &quot;high&quot;\n}</code> |
| `pyd_task_003` | `pydantic_adherence` | `metta_runtime` | 1 | 1 | 1 | <code>{&quot;task&quot;: &quot;collect rows&quot;, &quot;priority&quot;: &quot;high&quot;, &quot;due_date&quot;: &quot;2026-05-02&quot;, &quot;blocked&quot;: false}</code> |
| `pyd_task_003` | `pydantic_adherence` | `metta_runtime_repair` | 1 | 1 | 1 | <code>{&quot;task&quot;: &quot;collect rows&quot;, &quot;priority&quot;: &quot;high&quot;, &quot;due_date&quot;: &quot;2026-05-02&quot;, &quot;blocked&quot;: false}</code> |
| `pyd_verifier_004` | `pydantic_adherence` | `baseline` | 1 | 1 | 1 | <code>{&quot;name&quot;:&quot;verifier&quot;,&quot;retries&quot;:2,&quot;safe&quot;:true}</code> |
| `pyd_verifier_004` | `pydantic_adherence` | `pure_trm` | 1 | 1 | 1 | <code>{&quot;name&quot;: &quot;verifier&quot;, &quot;retries&quot;: 2, &quot;safe&quot;: true}</code> |
| `pyd_verifier_004` | `pydantic_adherence` | `metta_runtime` | 0 | 0 | 0 | <code>{&quot;env_family&quot;: &quot;pydantic_adherence&quot;, &quot;failure_labels&quot;: [&quot;json_parse&quot;, &quot;type_error&quot;], &quot;validator&quot;: {&quot;required&quot;: {&quot;name&quot;: &quot;str&quot;, &qu</code> |
| `pyd_verifier_004` | `pydantic_adherence` | `metta_runtime_repair` | 0 | 0 | 0 | <code>{&quot;env_family&quot;: &quot;pydantic_adherence&quot;, &quot;failure_labels&quot;: [&quot;json_parse&quot;, &quot;type_error&quot;], &quot;validator&quot;: {&quot;required&quot;: {&quot;name&quot;: &quot;str&quot;, &qu</code> |
| `ascii_flat_005` | `ascii_tree` | `baseline` | 0 | 0 | 0 | <code>1\n     / \\n    2   3\n   / \ / \\n  4  5 6  7</code> |
| `ascii_flat_005` | `ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>{\n  &quot;root&quot;: {\n    &quot;rows&quot;: {\n      &quot;validators&quot;: {\n        &quot;results&quot;: &quot;&quot;\n      }\n    }\n  }\n}</code> |
| `ascii_flat_005` | `ascii_tree` | `metta_runtime` | 0 | 0 | 1 | <code>{\n  &quot;root&quot;: {\n    &quot;rows&quot;: {\n      &quot;0&quot;: {\n        &quot;validators&quot;: {\n          &quot;0&quot;: &quot;v0&quot;,\n          &quot;1&quot;: &quot;v1&quot;,\n          &quot;2&quot;: &</code> |
| `ascii_flat_005` | `ascii_tree` | `metta_runtime_repair` | 0 | 0 | 1 | <code>{\n  &quot;root&quot;: {\n    &quot;rows&quot;: {\n      &quot;0&quot;: {\n        &quot;validators&quot;: {\n          &quot;0&quot;: &quot;v0&quot;,\n          &quot;1&quot;: &quot;v1&quot;,\n          &quot;2&quot;: &</code> |
| `ascii_nested_006` | `ascii_tree` | `baseline` | 0 | 0 | 0 | <code>commit\n     /    \\nparse    classify</code> |
| `ascii_nested_006` | `ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>```\npipeline\n\|-- parse\n\|   `-- classify\n`-- commit\n```</code> |
| `ascii_nested_006` | `ascii_tree` | `metta_runtime` | 0 | 0 | 1 | <code>pipeline\n\|-- parse\n   \|-- classify\n   `-- commit</code> |
| `ascii_nested_006` | `ascii_tree` | `metta_runtime_repair` | 0 | 0 | 1 | <code>pipeline\n\|-- parse\n   \|-- classify\n   `-- commit</code> |
| `ifeval_bullets_007` | `ifeval_contract_family` | `baseline` | 1 | 1 | 1 | <code>- Parse input data\n- Validate input data\n- Commit validated data</code> |
| `ifeval_bullets_007` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>- Parse the contract.\n- Validate the parsed contract.\n- Commit the validated contract.</code> |
| `ifeval_bullets_007` | `ifeval_contract_family` | `metta_runtime` | 0 | 0 | 0 | <code>- line_count: 1\n- extra_text: 2</code> |
| `ifeval_bullets_007` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>- parse\n- validate\n- commit</code> |
| `ifeval_json_array_008` | `ifeval_contract_family` | `baseline` | 0 | 1 | 0 | <code>[&quot;commit&quot;, &quot;repair&quot;, &quot;route&quot;]</code> |
| `ifeval_json_array_008` | `ifeval_contract_family` | `pure_trm` | 1 | 1 | 1 | <code>[&quot;route&quot;, &quot;repair&quot;, &quot;commit&quot;]</code> |
| `ifeval_json_array_008` | `ifeval_contract_family` | `metta_runtime` | 1 | 1 | 1 | <code>[&quot;route&quot;, &quot;repair&quot;, &quot;commit&quot;]</code> |
| `ifeval_json_array_008` | `ifeval_contract_family` | `metta_runtime_repair` | 1 | 1 | 1 | <code>[&quot;route&quot;, &quot;repair&quot;, &quot;commit&quot;]</code> |
| `boolq_nile_009` | `boolq_choice_contract` | `baseline` | 1 | 1 | 1 | <code>true</code> |
| `boolq_nile_009` | `boolq_choice_contract` | `pure_trm` | 1 | 1 | 1 | <code>true</code> |
| `boolq_nile_009` | `boolq_choice_contract` | `metta_runtime` | 1 | 1 | 1 | <code>true</code> |
| `boolq_nile_009` | `boolq_choice_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>true</code> |
| `boolq_sky_010` | `boolq_choice_contract` | `baseline` | 1 | 1 | 1 | <code>false</code> |
| `boolq_sky_010` | `boolq_choice_contract` | `pure_trm` | 1 | 1 | 1 | <code>false</code> |
| `boolq_sky_010` | `boolq_choice_contract` | `metta_runtime` | 1 | 1 | 1 | <code>false</code> |
| `boolq_sky_010` | `boolq_choice_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>false</code> |
| `choice_letter_011` | `choice_contract` | `baseline` | 0 | 1 | 0 | <code>C</code> |
| `choice_letter_011` | `choice_contract` | `pure_trm` | 0 | 1 | 0 | <code>C</code> |
| `choice_letter_011` | `choice_contract` | `metta_runtime` | 0 | 1 | 0 | <code>A</code> |
| `choice_letter_011` | `choice_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>B</code> |
| `pipe_triplet_012` | `structured_contract` | `baseline` | 1 | 1 | 1 | <code>2026-04-28\|trm\|ready</code> |
| `pipe_triplet_012` | `structured_contract` | `pure_trm` | 0 | 0 | 0 | <code>date\|owner\|status\n2026-04-28\|trm\|ready</code> |
| `pipe_triplet_012` | `structured_contract` | `metta_runtime` | 1 | 1 | 1 | <code>2026-04-28\|trm\|ready</code> |
| `pipe_triplet_012` | `structured_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>2026-04-28\|trm\|ready</code> |

## Claim Audit

- Allowed: this is a live local 3B smoke against frozen validators.
- Not allowed: do not report this as the final mixed-contract benchmark; the row count is intentionally small.
- Not allowed: do not call `metta_runtime_repair` learned TRM lift; it is a repair-prompt arm using the same 3B model plus public validator feedback.
