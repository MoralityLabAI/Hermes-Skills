# Qwen2.5-3B CPU replication hard30

Generated: `2026-10-08T14:10:59.237856+00:00`

Evidence class: `live_model_local_3b`

Model: `C:\Users\patri\Documents\Codex\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf`
llama.cpp completion: `C:\Users\patri\Documents\Codex\BitAgent-gym\llama-prism\bin\llama-completion.exe`
Peak child RSS: `2269.26 MB`

This run replaces deterministic candidates with local 3B completions for the supplied row IDs and validators. Interpret it according to the study claim audit.

## Arm Summary

| Arm | Rows | Contract valid | Semantic valid | Exact success | Exact rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 30 | 20 | 11 | 9 | 0.3000 |
| `metta_runtime` | 30 | 20 | 11 | 8 | 0.2667 |
| `metta_runtime_blind_repair` | 30 | 20 | 16 | 13 | 0.4333 |
| `metta_runtime_repair` | 30 | 20 | 16 | 13 | 0.4333 |
| `pure_trm` | 30 | 20 | 14 | 11 | 0.3667 |

## Repair Opportunity Summary

Rows where `metta_runtime` failed exactly: `22`

| Repair arm | Rows | Contract valid | Semantic valid | Exact success | Exact rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `metta_runtime_blind_repair` | 22 | 12 | 8 | 5 | 0.2273 |
| `metta_runtime_repair` | 22 | 12 | 8 | 5 | 0.2273 |

## Case Detail

| Row | Family | Arm | Exact | Contract | Semantic | Output |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `hard_math_001_mod` | `math_numeric_contract` | `baseline` | 0 | 1 | 0 | <code>14</code> |
| `hard_math_001_mod` | `math_numeric_contract` | `pure_trm` | 0 | 1 | 0 | <code>10</code> |
| `hard_math_001_mod` | `math_numeric_contract` | `metta_runtime` | 0 | 1 | 0 | <code>28</code> |
| `hard_math_001_mod` | `math_numeric_contract` | `metta_runtime_blind_repair` | 0 | 1 | 0 | <code>3</code> |
| `hard_math_001_mod` | `math_numeric_contract` | `metta_runtime_repair` | 0 | 1 | 0 | <code>4</code> |
| `hard_math_002_polynomial` | `math_numeric_contract` | `baseline` | 0 | 1 | 0 | <code>47</code> |
| `hard_math_002_polynomial` | `math_numeric_contract` | `pure_trm` | 0 | 0 | 0 | <code>To solve the problem, we follow the given equation with the provided values for x and y:\n\n1. Substitute x = 4 and y = 7 into the equation: \n   3*x*x - 2*y + 5\n\n2. Compute step by step:\n   3*4*4 -</code> |
| `hard_math_002_polynomial` | `math_numeric_contract` | `metta_runtime` | 0 | 1 | 0 | <code>41</code> |
| `hard_math_002_polynomial` | `math_numeric_contract` | `metta_runtime_blind_repair` | 0 | 1 | 0 | <code>41</code> |
| `hard_math_002_polynomial` | `math_numeric_contract` | `metta_runtime_repair` | 0 | 1 | 0 | <code>41</code> |
| `hard_math_003_filter` | `math_numeric_contract` | `baseline` | 0 | 1 | 0 | <code>5</code> |
| `hard_math_003_filter` | `math_numeric_contract` | `pure_trm` | 0 | 1 | 0 | <code>5</code> |
| `hard_math_003_filter` | `math_numeric_contract` | `metta_runtime` | 0 | 1 | 0 | <code>4</code> |
| `hard_math_003_filter` | `math_numeric_contract` | `metta_runtime_blind_repair` | 0 | 1 | 0 | <code>3</code> |
| `hard_math_003_filter` | `math_numeric_contract` | `metta_runtime_repair` | 0 | 1 | 0 | <code>3</code> |
| `hard_math_004_boolean_sum` | `math_numeric_contract` | `baseline` | 0 | 1 | 0 | <code>1</code> |
| `hard_math_004_boolean_sum` | `math_numeric_contract` | `pure_trm` | 0 | 1 | 0 | <code>1</code> |
| `hard_math_004_boolean_sum` | `math_numeric_contract` | `metta_runtime` | 0 | 1 | 0 | <code>1</code> |
| `hard_math_004_boolean_sum` | `math_numeric_contract` | `metta_runtime_blind_repair` | 0 | 1 | 0 | <code>1</code> |
| `hard_math_004_boolean_sum` | `math_numeric_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>2</code> |
| `hard_math_005_day` | `math_numeric_contract` | `baseline` | 0 | 1 | 0 | <code>04</code> |
| `hard_math_005_day` | `math_numeric_contract` | `pure_trm` | 1 | 1 | 1 | <code>13</code> |
| `hard_math_005_day` | `math_numeric_contract` | `metta_runtime` | 0 | 1 | 0 | <code>20260513</code> |
| `hard_math_005_day` | `math_numeric_contract` | `metta_runtime_blind_repair` | 0 | 1 | 0 | <code>20260514</code> |
| `hard_math_005_day` | `math_numeric_contract` | `metta_runtime_repair` | 0 | 1 | 0 | <code>20260513</code> |
| `hard_math_006_grid` | `math_numeric_contract` | `baseline` | 0 | 1 | 0 | <code>24</code> |
| `hard_math_006_grid` | `math_numeric_contract` | `pure_trm` | 0 | 1 | 0 | <code>14</code> |
| `hard_math_006_grid` | `math_numeric_contract` | `metta_runtime` | 0 | 1 | 0 | <code>14</code> |
| `hard_math_006_grid` | `math_numeric_contract` | `metta_runtime_blind_repair` | 0 | 1 | 0 | <code>14</code> |
| `hard_math_006_grid` | `math_numeric_contract` | `metta_runtime_repair` | 0 | 1 | 0 | <code>16</code> |
| `hard_math_007_majority` | `math_numeric_contract` | `baseline` | 1 | 1 | 1 | <code>1</code> |
| `hard_math_007_majority` | `math_numeric_contract` | `pure_trm` | 0 | 1 | 0 | <code>3</code> |
| `hard_math_007_majority` | `math_numeric_contract` | `metta_runtime` | 0 | 1 | 0 | <code>2</code> |
| `hard_math_007_majority` | `math_numeric_contract` | `metta_runtime_blind_repair` | 1 | 1 | 1 | <code>1</code> |
| `hard_math_007_majority` | `math_numeric_contract` | `metta_runtime_repair` | 0 | 1 | 0 | <code>3</code> |
| `hard_math_008_prime_count` | `math_numeric_contract` | `baseline` | 0 | 1 | 0 | <code>4</code> |
| `hard_math_008_prime_count` | `math_numeric_contract` | `pure_trm` | 0 | 1 | 0 | <code>2</code> |
| `hard_math_008_prime_count` | `math_numeric_contract` | `metta_runtime` | 0 | 1 | 0 | <code>2</code> |
| `hard_math_008_prime_count` | `math_numeric_contract` | `metta_runtime_blind_repair` | 1 | 1 | 1 | <code>3</code> |
| `hard_math_008_prime_count` | `math_numeric_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>3</code> |
| `hard_logic_001_router_schema` | `logic_label_contract` | `baseline` | 0 | 0 | 0 | <code>B=no</code> |
| `hard_logic_001_router_schema` | `logic_label_contract` | `pure_trm` | 0 | 0 | 0 | <code>B=no</code> |
| `hard_logic_001_router_schema` | `logic_label_contract` | `metta_runtime` | 0 | 0 | 0 | <code>B=unknown</code> |
| `hard_logic_001_router_schema` | `logic_label_contract` | `metta_runtime_blind_repair` | 0 | 0 | 0 | <code>B=no</code> |
| `hard_logic_001_router_schema` | `logic_label_contract` | `metta_runtime_repair` | 0 | 0 | 0 | <code>B=no</code> |
| `hard_logic_002_commit_gate` | `logic_label_contract` | `baseline` | 0 | 1 | 0 | <code>C</code> |
| `hard_logic_002_commit_gate` | `logic_label_contract` | `pure_trm` | 0 | 1 | 0 | <code>C</code> |
| `hard_logic_002_commit_gate` | `logic_label_contract` | `metta_runtime` | 0 | 1 | 0 | <code>C</code> |
| `hard_logic_002_commit_gate` | `logic_label_contract` | `metta_runtime_blind_repair` | 0 | 1 | 0 | <code>D</code> |
| `hard_logic_002_commit_gate` | `logic_label_contract` | `metta_runtime_repair` | 0 | 1 | 0 | <code>D</code> |
| `hard_logic_003_xor` | `logic_label_contract` | `baseline` | 0 | 1 | 0 | <code>A</code> |
| `hard_logic_003_xor` | `logic_label_contract` | `pure_trm` | 1 | 1 | 1 | <code>B</code> |
| `hard_logic_003_xor` | `logic_label_contract` | `metta_runtime` | 0 | 1 | 0 | <code>A</code> |
| `hard_logic_003_xor` | `logic_label_contract` | `metta_runtime_blind_repair` | 1 | 1 | 1 | <code>B</code> |
| `hard_logic_003_xor` | `logic_label_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>B</code> |
| `hard_logic_004_failed_parse` | `logic_label_contract` | `baseline` | 1 | 1 | 1 | <code>B</code> |
| `hard_logic_004_failed_parse` | `logic_label_contract` | `pure_trm` | 1 | 1 | 1 | <code>B</code> |
| `hard_logic_004_failed_parse` | `logic_label_contract` | `metta_runtime` | 0 | 1 | 0 | <code>C</code> |
| `hard_logic_004_failed_parse` | `logic_label_contract` | `metta_runtime_blind_repair` | 1 | 1 | 1 | <code>B</code> |
| `hard_logic_004_failed_parse` | `logic_label_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>B</code> |
| `hard_logic_005_transitive` | `logic_label_contract` | `baseline` | 1 | 1 | 1 | <code>true</code> |
| `hard_logic_005_transitive` | `logic_label_contract` | `pure_trm` | 1 | 1 | 1 | <code>true</code> |
| `hard_logic_005_transitive` | `logic_label_contract` | `metta_runtime` | 1 | 1 | 1 | <code>true</code> |
| `hard_logic_005_transitive` | `logic_label_contract` | `metta_runtime_blind_repair` | 1 | 1 | 1 | <code>true</code> |
| `hard_logic_005_transitive` | `logic_label_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>true</code> |
| `hard_logic_006_pass2` | `logic_label_contract` | `baseline` | 1 | 1 | 1 | <code>PASS2</code> |
| `hard_logic_006_pass2` | `logic_label_contract` | `pure_trm` | 1 | 1 | 1 | <code>PASS2</code> |
| `hard_logic_006_pass2` | `logic_label_contract` | `metta_runtime` | 0 | 1 | 0 | <code>OTHER</code> |
| `hard_logic_006_pass2` | `logic_label_contract` | `metta_runtime_blind_repair` | 1 | 1 | 1 | <code>PASS2</code> |
| `hard_logic_006_pass2` | `logic_label_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>PASS2</code> |
| `hard_logic_007_cycle` | `logic_label_contract` | `baseline` | 1 | 1 | 1 | <code>false</code> |
| `hard_logic_007_cycle` | `logic_label_contract` | `pure_trm` | 1 | 1 | 1 | <code>false</code> |
| `hard_logic_007_cycle` | `logic_label_contract` | `metta_runtime` | 1 | 1 | 1 | <code>false</code> |
| `hard_logic_007_cycle` | `logic_label_contract` | `metta_runtime_blind_repair` | 1 | 1 | 1 | <code>false</code> |
| `hard_logic_007_cycle` | `logic_label_contract` | `metta_runtime_repair` | 1 | 1 | 1 | <code>false</code> |
| `hard_schema_001_repair_route` | `computed_json_schema` | `baseline` | 1 | 1 | 1 | <code>{&quot;route&quot;:&quot;repair&quot;,&quot;priority&quot;:&quot;high&quot;,&quot;retry_count&quot;:2,&quot;safe&quot;:true}</code> |
| `hard_schema_001_repair_route` | `computed_json_schema` | `pure_trm` | 0 | 0 | 0 | <code>{&quot;route&quot;: &quot;repair&quot;, &quot;priority&quot;: &quot;high&quot;, &quot;retry_count&quot;: previous_attempts+1, &quot;safe&quot;: true}</code> |
| `hard_schema_001_repair_route` | `computed_json_schema` | `metta_runtime` | 0 | 0 | 0 | <code>{&quot;route&quot;: &quot;repair&quot;, &quot;priority&quot;: &quot;high&quot;, &quot;retry_count&quot;: &quot;2&quot;, &quot;safe&quot;: &quot;true&quot;}</code> |
| `hard_schema_001_repair_route` | `computed_json_schema` | `metta_runtime_blind_repair` | 0 | 0 | 0 | <code>{&quot;route&quot;: &quot;repair&quot;, &quot;priority&quot;: &quot;high&quot;, &quot;retry_count&quot;: &quot;3&quot;, &quot;safe&quot;: &quot;true&quot;}</code> |
| `hard_schema_001_repair_route` | `computed_json_schema` | `metta_runtime_repair` | 0 | 0 | 0 | <code>{&quot;route&quot;: &quot;repair&quot;, &quot;priority&quot;: &quot;high&quot;, &quot;retry_count&quot;: &quot;3&quot;, &quot;safe&quot;: &quot;true&quot;}</code> |
| `hard_schema_002_commit_route` | `computed_json_schema` | `baseline` | 0 | 0 | 1 | <code>{&quot;route&quot;:&quot;commit&quot;,&quot;priority&quot;:&quot;low&quot;,&quot;retry_count&quot;:0,&quot;safe&quot;:true,&quot;contract_valid&quot;:true,&quot;semantic_valid&quot;:true,&quot;previous_attempts&quot;:0}</code> |
| `hard_schema_002_commit_route` | `computed_json_schema` | `pure_trm` | 1 | 1 | 1 | <code>{&quot;route&quot;: &quot;commit&quot;, &quot;priority&quot;: &quot;low&quot;, &quot;retry_count&quot;: 0, &quot;safe&quot;: true}</code> |
| `hard_schema_002_commit_route` | `computed_json_schema` | `metta_runtime` | 1 | 1 | 1 | <code>{&quot;route&quot;: &quot;commit&quot;, &quot;priority&quot;: &quot;low&quot;, &quot;retry_count&quot;: 0, &quot;safe&quot;: true}</code> |
| `hard_schema_002_commit_route` | `computed_json_schema` | `metta_runtime_blind_repair` | 1 | 1 | 1 | <code>{&quot;route&quot;: &quot;commit&quot;, &quot;priority&quot;: &quot;low&quot;, &quot;retry_count&quot;: 0, &quot;safe&quot;: true}</code> |
| `hard_schema_002_commit_route` | `computed_json_schema` | `metta_runtime_repair` | 1 | 1 | 1 | <code>{&quot;route&quot;: &quot;commit&quot;, &quot;priority&quot;: &quot;low&quot;, &quot;retry_count&quot;: 0, &quot;safe&quot;: true}</code> |
| `hard_schema_003_reject_route` | `computed_json_schema` | `baseline` | 1 | 1 | 1 | <code>{&quot;route&quot;:&quot;reject&quot;,&quot;priority&quot;:&quot;high&quot;,&quot;retry_count&quot;:0,&quot;safe&quot;:false}</code> |
| `hard_schema_003_reject_route` | `computed_json_schema` | `pure_trm` | 1 | 1 | 1 | <code>{&quot;route&quot;: &quot;reject&quot;, &quot;priority&quot;: &quot;high&quot;, &quot;retry_count&quot;: 0, &quot;safe&quot;: false}</code> |
| `hard_schema_003_reject_route` | `computed_json_schema` | `metta_runtime` | 1 | 1 | 1 | <code>{&quot;priority&quot;: &quot;high&quot;, &quot;route&quot;: &quot;reject&quot;, &quot;retry_count&quot;: 0, &quot;safe&quot;: false, &quot;priority&quot;: &quot;high&quot;, &quot;retry_count&quot;: 0, &quot;route&quot;: </code> |
| `hard_schema_003_reject_route` | `computed_json_schema` | `metta_runtime_blind_repair` | 1 | 1 | 1 | <code>{&quot;priority&quot;: &quot;high&quot;, &quot;route&quot;: &quot;reject&quot;, &quot;retry_count&quot;: 0, &quot;safe&quot;: false, &quot;priority&quot;: &quot;high&quot;, &quot;retry_count&quot;: 0, &quot;route&quot;: </code> |
| `hard_schema_003_reject_route` | `computed_json_schema` | `metta_runtime_repair` | 1 | 1 | 1 | <code>{&quot;priority&quot;: &quot;high&quot;, &quot;route&quot;: &quot;reject&quot;, &quot;retry_count&quot;: 0, &quot;safe&quot;: false, &quot;priority&quot;: &quot;high&quot;, &quot;retry_count&quot;: 0, &quot;route&quot;: </code> |
| `hard_schema_004_window` | `computed_json_schema` | `baseline` | 1 | 1 | 1 | <code>{&quot;batch_id&quot;:&quot;batch-7&quot;,&quot;passed&quot;:7,&quot;failed&quot;:5,&quot;start_date&quot;:&quot;2026-05-11&quot;}</code> |
| `hard_schema_004_window` | `computed_json_schema` | `pure_trm` | 1 | 1 | 1 | <code>{&quot;batch_id&quot;: &quot;batch-7&quot;, &quot;failed&quot;: 5, &quot;passed&quot;: 7, &quot;start_date&quot;: &quot;2026-05-11&quot;}</code> |
| `hard_schema_004_window` | `computed_json_schema` | `metta_runtime` | 1 | 1 | 1 | <code>{&quot;batch_id&quot;: &quot;batch-7&quot;, &quot;failed&quot;: 5, &quot;passed&quot;: 7, &quot;start_date&quot;: &quot;2026-05-11&quot;}</code> |
| `hard_schema_004_window` | `computed_json_schema` | `metta_runtime_blind_repair` | 1 | 1 | 1 | <code>{&quot;batch_id&quot;: &quot;batch-7&quot;, &quot;failed&quot;: 5, &quot;passed&quot;: 7, &quot;start_date&quot;: &quot;2026-05-11&quot;}</code> |
| `hard_schema_004_window` | `computed_json_schema` | `metta_runtime_repair` | 1 | 1 | 1 | <code>{&quot;batch_id&quot;: &quot;batch-7&quot;, &quot;failed&quot;: 5, &quot;passed&quot;: 7, &quot;start_date&quot;: &quot;2026-05-11&quot;}</code> |
| `hard_schema_005_skill` | `computed_json_schema` | `baseline` | 0 | 0 | 0 | <code>{&quot;name&quot;:&quot;metta_router&quot;,&quot;version&quot;:&quot;3&quot;,&quot;active&quot;:true}</code> |
| `hard_schema_005_skill` | `computed_json_schema` | `pure_trm` | 1 | 1 | 1 | <code>{&quot;name&quot;: &quot;metta_router&quot;, &quot;version&quot;: 3, &quot;active&quot;: true}</code> |
| `hard_schema_005_skill` | `computed_json_schema` | `metta_runtime` | 1 | 1 | 1 | <code>{&quot;name&quot;: &quot;metta_router&quot;, &quot;version&quot;: 3, &quot;active&quot;: true}</code> |
| `hard_schema_005_skill` | `computed_json_schema` | `metta_runtime_blind_repair` | 1 | 1 | 1 | <code>{&quot;name&quot;: &quot;metta_router&quot;, &quot;version&quot;: 3, &quot;active&quot;: true}</code> |
| `hard_schema_005_skill` | `computed_json_schema` | `metta_runtime_repair` | 1 | 1 | 1 | <code>{&quot;name&quot;: &quot;metta_router&quot;, &quot;version&quot;: 3, &quot;active&quot;: true}</code> |
| `hard_schema_006_score` | `computed_json_schema` | `baseline` | 0 | 0 | 0 | <code>{&quot;contract&quot;:2,&quot;semantic&quot;:3,&quot;total&quot;:5,&quot;exact&quot;:&quot;true&quot;}</code> |
| `hard_schema_006_score` | `computed_json_schema` | `pure_trm` | 1 | 1 | 1 | <code>{&quot;contract&quot;: 2, &quot;semantic&quot;: 3, &quot;total&quot;: 5, &quot;exact&quot;: true}</code> |
| `hard_schema_006_score` | `computed_json_schema` | `metta_runtime` | 1 | 1 | 1 | <code>{&quot;contract&quot;: 2, &quot;exact&quot;: true, &quot;semantic&quot;: 3, &quot;total&quot;: 5}</code> |
| `hard_schema_006_score` | `computed_json_schema` | `metta_runtime_blind_repair` | 1 | 1 | 1 | <code>{&quot;contract&quot;: 2, &quot;exact&quot;: true, &quot;semantic&quot;: 3, &quot;total&quot;: 5}</code> |
| `hard_schema_006_score` | `computed_json_schema` | `metta_runtime_repair` | 1 | 1 | 1 | <code>{&quot;contract&quot;: 2, &quot;exact&quot;: true, &quot;semantic&quot;: 3, &quot;total&quot;: 5}</code> |
| `hard_state_001_repair` | `state_sequence_array` | `baseline` | 0 | 1 | 0 | <code>[&quot;parse-fails&quot;,&quot;validation-fails&quot;,&quot;repair-succeeds&quot;,&quot;commit&quot;]</code> |
| `hard_state_001_repair` | `state_sequence_array` | `pure_trm` | 0 | 0 | 0 | <code>[&quot;json_parse&quot;, &quot;array_length&quot;, &quot;state_order&quot;]</code> |
| `hard_state_001_repair` | `state_sequence_array` | `metta_runtime` | 0 | 0 | 0 | <code>[&quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;]</code> |
| `hard_state_001_repair` | `state_sequence_array` | `metta_runtime_blind_repair` | 0 | 0 | 0 | <code>[&quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_VALIDATE_FAILURE&quot;]</code> |
| `hard_state_001_repair` | `state_sequence_array` | `metta_runtime_repair` | 0 | 0 | 0 | <code>[&quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;]</code> |
| `hard_state_002_reject` | `state_sequence_array` | `baseline` | 0 | 0 | 0 | <code>[&quot;parse&quot;]</code> |
| `hard_state_002_reject` | `state_sequence_array` | `pure_trm` | 0 | 1 | 0 | <code>[&quot;json_parse&quot;, &quot;array_length&quot;, &quot;state_order&quot;]</code> |
| `hard_state_002_reject` | `state_sequence_array` | `metta_runtime` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;]</code> |
| `hard_state_002_reject` | `state_sequence_array` | `metta_runtime_blind_repair` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;TRM_DRAFT&quot;]</code> |
| `hard_state_002_reject` | `state_sequence_array` | `metta_runtime_repair` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;]</code> |
| `hard_state_003_retry` | `state_sequence_array` | `baseline` | 0 | 1 | 0 | <code>[&quot;collect&quot;, &quot;score fails&quot;, &quot;retry&quot;, &quot;score succeeds&quot;, &quot;commit&quot;]</code> |
| `hard_state_003_retry` | `state_sequence_array` | `pure_trm` | 0 | 0 | 0 | <code>[\n    &quot;json_parse&quot;,\n    &quot;array_length&quot;,\n    &quot;state_order&quot;\n]</code> |
| `hard_state_003_retry` | `state_sequence_array` | `metta_runtime` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;TRM_COMMIT&quot;]</code> |
| `hard_state_003_retry` | `state_sequence_array` | `metta_runtime_blind_repair` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_COMMIT&quot;]</code> |
| `hard_state_003_retry` | `state_sequence_array` | `metta_runtime_repair` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;]</code> |
| `hard_state_004_branch` | `state_sequence_array` | `baseline` | 0 | 0 | 0 | <code>[&quot;route&quot;, &quot;selects&quot;, &quot;tool&quot;, &quot;tool&quot;, &quot;returns&quot;, &quot;validation&quot;, &quot;passes&quot;, &quot;commit&quot;]</code> |
| `hard_state_004_branch` | `state_sequence_array` | `pure_trm` | 0 | 0 | 0 | <code>[&quot;json_parse&quot;, &quot;array_length&quot;, &quot;state_order&quot;]</code> |
| `hard_state_004_branch` | `state_sequence_array` | `metta_runtime` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;TRM_COMMIT&quot;]</code> |
| `hard_state_004_branch` | `state_sequence_array` | `metta_runtime_blind_repair` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;TRM_DRAFT&quot;, &quot;TRM_COMMIT&quot;]</code> |
| `hard_state_004_branch` | `state_sequence_array` | `metta_runtime_repair` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;TRM_COMMIT&quot;]</code> |
| `hard_state_005_abort` | `state_sequence_array` | `baseline` | 1 | 1 | 1 | <code>[&quot;load&quot;, &quot;check&quot;, &quot;abort&quot;]</code> |
| `hard_state_005_abort` | `state_sequence_array` | `pure_trm` | 0 | 1 | 0 | <code>[&quot;json_parse&quot;, &quot;array_length&quot;, &quot;state_order&quot;]</code> |
| `hard_state_005_abort` | `state_sequence_array` | `metta_runtime` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;]</code> |
| `hard_state_005_abort` | `state_sequence_array` | `metta_runtime_blind_repair` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;TRM_DRAFT&quot;]</code> |
| `hard_state_005_abort` | `state_sequence_array` | `metta_runtime_repair` | 0 | 0 | 0 | <code>[&quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;]</code> |
| `hard_tree_001_skill` | `deep_ascii_tree` | `baseline` | 0 | 0 | 1 | <code>root\n \|\n \|__ skill\n \|    \|\n \|    \|__ parse\n \|    \|__ schema\n \|    \|__ prompt\n \|    \|__ commit</code> |
| `hard_tree_001_skill` | `deep_ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>\| root\n\|   \|-- skill\n\|   \|-- parse\n\|   \|-- schema\n\|   \|-- prompt\n\|   `-- commit</code> |
| `hard_tree_001_skill` | `deep_ascii_tree` | `metta_runtime` | 0 | 0 | 1 | <code>skill\n\|-- parse\n\|-- schema\n\|-- prompt\n`-- commit</code> |
| `hard_tree_001_skill` | `deep_ascii_tree` | `metta_runtime_blind_repair` | 0 | 0 | 1 | <code>skill\n\|-- parse\n\|   \|-- schema\n\|   \|-- prompt\n`-- commit</code> |
| `hard_tree_001_skill` | `deep_ascii_tree` | `metta_runtime_repair` | 0 | 0 | 1 | <code>skill\n\|-- parse\n\|   \|-- schema\n\|   \|-- prompt\n`-- commit</code> |
| `hard_tree_002_eval` | `deep_ascii_tree` | `baseline` | 0 | 0 | 0 | <code>root\n     /   \\n  eval   holdout\n     \     \\n    root   claims</code> |
| `hard_tree_002_eval` | `deep_ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>```\nroot\n\|-- eval\n\|   \|-- rows\n\|   \|   \|-- hard\n\|   \|   `-- holdout\n\|   `-- claims\n```</code> |
| `hard_tree_002_eval` | `deep_ascii_tree` | `metta_runtime` | 0 | 0 | 1 | <code>```\neval\n\|-- rows\n\|   \|-- hard\n\|   `-- holdout\n`-- claims\n```</code> |
| `hard_tree_002_eval` | `deep_ascii_tree` | `metta_runtime_blind_repair` | 0 | 0 | 1 | <code>```\neval\n\|-- rows\n\|   \|-- hard\n\|   `-- holdout\n`-- claims\n```</code> |
| `hard_tree_002_eval` | `deep_ascii_tree` | `metta_runtime_repair` | 0 | 0 | 1 | <code>```\neval\n\|-- rows\n\|   \|-- hard\n\|   `-- holdout\n`-- claims\n```</code> |
| `hard_tree_003_gate` | `deep_ascii_tree` | `baseline` | 0 | 0 | 0 | <code>root\n  \\n   \\n    \\n     \\n      \\n       \\n        \\n         \\n          \\n           \\n            \\n             \\n              \\n               \\n                \\n                 \\n              </code> |
| `hard_tree_003_gate` | `deep_ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>\| root\n\| \|-- gate\n\| \| \|-- metta\n\| \| \| \|-- select\n\| \| \| \| \|-- trm\n\| \| \| `-- repair\n\| `-- repair</code> |
| `hard_tree_003_gate` | `deep_ascii_tree` | `metta_runtime` | 1 | 1 | 1 | <code>gate\n\|-- metta\n\|   `-- select\n\|-- trm\n`-- repair</code> |
| `hard_tree_003_gate` | `deep_ascii_tree` | `metta_runtime_blind_repair` | 1 | 1 | 1 | <code>gate\n\|-- metta\n\|   `-- select\n\|-- trm\n`-- repair</code> |
| `hard_tree_003_gate` | `deep_ascii_tree` | `metta_runtime_repair` | 1 | 1 | 1 | <code>gate\n\|-- metta\n\|   `-- select\n\|-- trm\n`-- repair</code> |
| `hard_tree_004_data` | `deep_ascii_tree` | `baseline` | 0 | 0 | 0 | <code>raw\n  /  \\n failures  audit\n \    /\n  raw\n / \\nraw raw</code> |
| `hard_tree_004_data` | `deep_ascii_tree` | `pure_trm` | 0 | 0 | 0 | <code>\|-- data\n\|   \|-- raw\n\|   \|   `-- raw node 1\n\|   \|       \|-- labels\n\|   \|       \|   `-- label 1\n\|   \|       \|       `-- failures\n\|   \|       \|           `-- failure 1\n\|   \|</code> |
| `hard_tree_004_data` | `deep_ascii_tree` | `metta_runtime` | 0 | 0 | 1 | <code>```\ndata\n\|-- raw\n\|-- labels\n\|   `-- failures\n`-- audit\n```</code> |
| `hard_tree_004_data` | `deep_ascii_tree` | `metta_runtime_blind_repair` | 0 | 0 | 1 | <code>```\ndata\n\|-- raw\n\|-- labels\n\|   `-- failures\n`-- audit\n```\n\nThe previous output was already correct. No changes were needed.</code> |
| `hard_tree_004_data` | `deep_ascii_tree` | `metta_runtime_repair` | 0 | 0 | 1 | <code>```\ndata\n\|-- raw\n\|-- labels\n\|   `-- failures\n`-- audit\n```</code> |

## Claim Audit

- Allowed: this is a live local 3B result against frozen validators.
- Not allowed: do not call this trained TRM lift; interpret benchmark status according to the study claim audit and row-suite scope.
- Not allowed: do not call `metta_runtime_repair` learned TRM lift; it is a repair-prompt arm using the same 3B model plus public validator feedback.
- Not allowed: do not conflate `metta_runtime_blind_repair` with validator-feedback repair; blind repair receives no validator verdict details.
