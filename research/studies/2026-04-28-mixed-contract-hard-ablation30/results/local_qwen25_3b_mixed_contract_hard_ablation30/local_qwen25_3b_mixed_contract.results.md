# Local Qwen2.5-3B Mixed Contract Hard Ablation30

Generated: `2026-04-28T17:25:50.668988+00:00`

Evidence class: `live_model_local_3b`

Model: `D:\Research_Engine\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf`
llama.cpp completion: `D:\Research_Engine\tools\llama.cpp-b8922-cuda12.4\llama-completion.exe`
Peak child RSS: `2370.91 MB`

Full 30-row hard local 3B run against frozen mixed-contract validators. Includes blind repair to separate generic second-pass repair from public-validator feedback repair. This is live_model_local_3b evidence, not trained TRM lift.

## Arm Summary

| Arm | Rows | Contract valid | Semantic valid | Exact success | Exact rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 30 | 20 | 15 | 12 | 0.4000 |
| `metta_runtime` | 30 | 20 | 12 | 9 | 0.3000 |
| `metta_runtime_blind_repair` | 30 | 20 | 15 | 12 | 0.4000 |
| `metta_runtime_repair` | 30 | 20 | 16 | 13 | 0.4333 |
| `pure_trm` | 30 | 21 | 14 | 11 | 0.3667 |

## Repair Opportunity Summary

Rows where `metta_runtime` failed exactly: `21`

| Repair arm | Rows | Contract valid | Semantic valid | Exact success | Exact rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `metta_runtime_blind_repair` | 21 | 11 | 6 | 3 | 0.1429 |
| `metta_runtime_repair` | 21 | 11 | 7 | 4 | 0.1905 |

## Case Detail

| Row | Family | Arm | Exact | Contract | Semantic | Output |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `hard_math_001_mod` | `math_numeric_contract` | `baseline` | 0 | 1 | 0 | <code>14</code> |
| `hard_math_001_mod` | `math_numeric_contract` | `pure_trm` | 0 | 1 | 0 | <code>10</code> |
| `hard_math_001_mod` | `math_numeric_contract` | `metta_runtime` | 0 | 1 | 0 | <code>28</code> |
| `hard_math_001_mod` | `math_numeric_contract` | `metta_runtime_blind_repair` | 0 | 1 | 0 | <code>3</code> |
| `hard_math_001_mod` | `math_numeric_contract` | `metta_runtime_repair` | 0 | 1 | 0 | <code>4</code> |
| `hard_math_002_polynomial` | `math_numeric_contract` | `baseline` | 0 | 1 | 0 | <code>47</code> |
| `hard_math_002_polynomial` | `math_numeric_contract` | `pure_trm` | 0 | 1 | 0 | <code>145</code> |
| `hard_math_002_polynomial` | `math_numeric_contract` | `metta_runtime` | 0 | 1 | 0 | <code>41</code> |
| `hard_math_002_polynomial` | `math_numeric_contract` | `metta_runtime_blind_repair` | 0 | 1 | 0 | <code>41</code> |
| `hard_math_002_polynomial` | `math_numeric_contract` | `metta_runtime_repair` | 0 | 1 | 0 | <code>41</code> |
| `hard_math_003_filter` | `math_numeric_contract` | `baseline` | 1 | 1 | 1 | <code>6</code> |
| `hard_math_003_filter` | `math_numeric_contract` | `pure_trm` | 0 | 1 | 0 | <code>4</code> |
| `hard_math_003_filter` | `math_numeric_contract` | `metta_runtime` | 0 | 1 | 0 | <code>4</code> |
| `hard_math_003_filter` | `math_numeric_contract` | `metta_runtime_blind_repair` | 0 | 1 | 0 | <code>3</code> |
| `hard_math_003_filter` | `math_numeric_contract` | `metta_runtime_repair` | 0 | 1 | 0 | <code>3</code> |
| `hard_math_004_boolean_sum` | `math_numeric_contract` | `baseline` | 1 | 1 | 1 | <code>2</code> |
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
| `hard_math_007_majority` | `math_numeric_contract` | `pure_trm` | 0 | 1 | 0 | <code>2</code> |
| `hard_math_007_majority` | `math_numeric_contract` | `metta_runtime` | 0 | 1 | 0 | <code>3</code> |
| `hard_math_007_majority` | `math_numeric_contract` | `metta_runtime_blind_repair` | 0 | 1 | 0 | <code>2</code> |
| `hard_math_007_majority` | `math_numeric_contract` | `metta_runtime_repair` | 0 | 1 | 0 | <code>2</code> |
| `hard_math_008_prime_count` | `math_numeric_contract` | `baseline` | 1 | 1 | 1 | <code>3</code> |
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
| `hard_logic_003_xor` | `logic_label_contract` | `metta_runtime` | 1 | 1 | 1 | <code>B</code> |
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
| `hard_schema_004_window` | `computed_json_schema` | `pure_trm` | 1 | 1 | 1 | <code>{\n  &quot;batch_id&quot;: &quot;batch-7&quot;,\n  &quot;failed&quot;: 5,\n  &quot;passed&quot;: 7,\n  &quot;start_date&quot;: &quot;2026-05-11&quot;\n}</code> |
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
| `hard_state_001_repair` | `state_sequence_array` | `metta_runtime_blind_repair` | 0 | 0 | 0 | <code>[&quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_VALIDATE_VALIDATION_FAILED&quot;]</code> |
| `hard_state_001_repair` | `state_sequence_array` | `metta_runtime_repair` | 0 | 0 | 0 | <code>[&quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;]</code> |
| `hard_state_002_reject` | `state_sequence_array` | `baseline` | 0 | 0 | 0 | <code>[&quot;parse-failure&quot;]</code> |
| `hard_state_002_reject` | `state_sequence_array` | `pure_trm` | 0 | 1 | 0 | <code>[&quot;json_parse&quot;, &quot;array_length&quot;, &quot;state_order&quot;]</code> |
| `hard_state_002_reject` | `state_sequence_array` | `metta_runtime` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;]</code> |
| `hard_state_002_reject` | `state_sequence_array` | `metta_runtime_blind_repair` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;TRM_DRAFT&quot;]</code> |
| `hard_state_002_reject` | `state_sequence_array` | `metta_runtime_repair` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;]</code> |
| `hard_state_003_retry` | `state_sequence_array` | `baseline` | 0 | 1 | 0 | <code>[&quot;collect&quot;, &quot;score fails&quot;, &quot;retry&quot;, &quot;score succeeds&quot;, &quot;commit&quot;]</code> |
| `hard_state_003_retry` | `state_sequence_array` | `pure_trm` | 0 | 0 | 0 | <code>[&quot;json_parse&quot;, &quot;array_length&quot;, &quot;state_order&quot;]</code> |
| `hard_state_003_retry` | `state_sequence_array` | `metta_runtime` | 0 | 0 | 0 | <code>[&quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_VALIDATE_OBSER</code> |
| `hard_state_003_retry` | `state_sequence_array` | `metta_runtime_blind_repair` | 0 | 0 | 0 | <code>[&quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_VALIDATE_OBSER</code> |
| `hard_state_003_retry` | `state_sequence_array` | `metta_runtime_repair` | 0 | 0 | 0 | <code>[&quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_VALIDATE_OBSER</code> |
| `hard_state_004_branch` | `state_sequence_array` | `baseline` | 0 | 0 | 0 | <code>[&quot;route&quot;, &quot;tool&quot;, &quot;returns&quot;, &quot;validation&quot;, &quot;passes&quot;, &quot;commit&quot;]</code> |
| `hard_state_004_branch` | `state_sequence_array` | `pure_trm` | 0 | 0 | 0 | <code>[&quot;json_parse&quot;, &quot;array_length&quot;, &quot;state_order&quot;]</code> |
| `hard_state_004_branch` | `state_sequence_array` | `metta_runtime` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;TRM_COMMIT&quot;]</code> |
| `hard_state_004_branch` | `state_sequence_array` | `metta_runtime_blind_repair` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;TRM_COMMIT&quot;]</code> |
| `hard_state_004_branch` | `state_sequence_array` | `metta_runtime_repair` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;TRM_COMMIT&quot;]</code> |
| `hard_state_005_abort` | `state_sequence_array` | `baseline` | 1 | 1 | 1 | <code>[&quot;load&quot;, &quot;check&quot;, &quot;abort&quot;]</code> |
| `hard_state_005_abort` | `state_sequence_array` | `pure_trm` | 0 | 1 | 0 | <code>[&quot;json_parse&quot;, &quot;array_length&quot;, &quot;state_order&quot;]</code> |
| `hard_state_005_abort` | `state_sequence_array` | `metta_runtime` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;]</code> |
| `hard_state_005_abort` | `state_sequence_array` | `metta_runtime_blind_repair` | 0 | 0 | 0 | <code>[&quot;TRM_PARSE_CONTRACT&quot;, &quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;TRM_DRAFT&quot;]</code> |
| `hard_state_005_abort` | `state_sequence_array` | `metta_runtime_repair` | 0 | 0 | 0 | <code>[&quot;METTA_VALIDATE_OBSERVABLE_STATE&quot;, &quot;METTA_SELECT_CONTRACT&quot;, &quot;TRM_DRAFT&quot;]</code> |
| `hard_tree_001_skill` | `deep_ascii_tree` | `baseline` | 0 | 0 | 1 | <code>root\n \|\n \|__ skill\n \|    \|\n \|    \|__ parse\n \|    \|__ schema\n \|    \|__ prompt\n \|    \|__ commit</code> |
| `hard_tree_001_skill` | `deep_ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>\|-- root\n\|   \|-- skill\n\|   \|-- parse\n\|   \|-- schema\n\|   \|-- prompt\n\|   `-- commit</code> |
| `hard_tree_001_skill` | `deep_ascii_tree` | `metta_runtime` | 0 | 0 | 1 | <code>skill\n\|-- parse\n\|-- schema\n\|-- prompt\n`-- commit</code> |
| `hard_tree_001_skill` | `deep_ascii_tree` | `metta_runtime_blind_repair` | 0 | 0 | 1 | <code>skill\n\|-- parse\n\|   \|-- schema\n\|   \|-- prompt\n`-- commit</code> |
| `hard_tree_001_skill` | `deep_ascii_tree` | `metta_runtime_repair` | 0 | 0 | 1 | <code>skill\n\|-- parse\n\|   \|-- schema\n\|   \|-- prompt\n`-- commit</code> |
| `hard_tree_002_eval` | `deep_ascii_tree` | `baseline` | 0 | 0 | 0 | <code>root\n     /   \\n  eval    holdout\n     \     /\n     claim</code> |
| `hard_tree_002_eval` | `deep_ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>```\neval\n\|-- rows\n\|   \|-- hard\n\|   `-- holdout\n`-- claims\n```</code> |
| `hard_tree_002_eval` | `deep_ascii_tree` | `metta_runtime` | 0 | 0 | 1 | <code>```\neval\n\|-- rows\n\|   \|-- hard\n\|   `-- holdout\n`-- claims\n```</code> |
| `hard_tree_002_eval` | `deep_ascii_tree` | `metta_runtime_blind_repair` | 0 | 0 | 1 | <code>```\neval\n\|-- rows\n\|   \|-- hard\n\|   `-- holdout\n`-- claims\n```</code> |
| `hard_tree_002_eval` | `deep_ascii_tree` | `metta_runtime_repair` | 0 | 0 | 1 | <code>```\neval\n\|-- rows\n\|   \|-- hard\n\|   `-- holdout\n`-- claims\n```</code> |
| `hard_tree_003_gate` | `deep_ascii_tree` | `baseline` | 0 | 0 | 1 | <code>```markdown\n      root\n       \|\n    gate\n       \|\n     metta\n       \|\n    select\n       \|\n     trm\n       \|\n   repair\n```</code> |
| `hard_tree_003_gate` | `deep_ascii_tree` | `pure_trm` | 0 | 0 | 1 | <code>```\ngate\n\|-- metta\n\|   `-- select\n\|-- trm\n`-- repair\n```</code> |
| `hard_tree_003_gate` | `deep_ascii_tree` | `metta_runtime` | 1 | 1 | 1 | <code>gate\n\|-- metta\n\|   `-- select\n\|-- trm\n`-- repair</code> |
| `hard_tree_003_gate` | `deep_ascii_tree` | `metta_runtime_blind_repair` | 1 | 1 | 1 | <code>gate\n\|-- metta\n\|   `-- select\n\|-- trm\n`-- repair</code> |
| `hard_tree_003_gate` | `deep_ascii_tree` | `metta_runtime_repair` | 1 | 1 | 1 | <code>gate\n\|-- metta\n\|   `-- select\n\|-- trm\n`-- repair</code> |
| `hard_tree_004_data` | `deep_ascii_tree` | `baseline` | 0 | 0 | 0 | <code>root\n  /   \\n fail  raw\n\|      \|\naudit  label</code> |
| `hard_tree_004_data` | `deep_ascii_tree` | `pure_trm` | 0 | 0 | 0 | <code>\|-- data\n\|   \|-- raw\n\|   \|   `-- raw node content\n\|   \|-- labels\n\|   \|   `-- label1\n\|   \|   `-- label2\n\|   `-- failures\n\|   \|   `-- failure1\n\|   \|   `-- failure</code> |
| `hard_tree_004_data` | `deep_ascii_tree` | `metta_runtime` | 0 | 0 | 1 | <code>```\ndata\n\|-- raw\n\|-- labels\n\|   `-- failures\n`-- audit\n```</code> |
| `hard_tree_004_data` | `deep_ascii_tree` | `metta_runtime_blind_repair` | 0 | 0 | 1 | <code>```\ndata\n\|-- raw\n\|-- labels\n\|   `-- failures\n`-- audit\n```\n\nThe previous output was already correct. No changes were needed.</code> |
| `hard_tree_004_data` | `deep_ascii_tree` | `metta_runtime_repair` | 0 | 0 | 1 | <code>```\ndata\n\|-- raw\n\|-- labels\n\|   `-- failures\n`-- audit\n```</code> |

## Claim Audit

- Allowed: this is a live local 3B result against frozen validators.
- Not allowed: do not call this trained TRM lift; interpret benchmark status according to the study claim audit and row-suite scope.
- Not allowed: do not call `metta_runtime_repair` learned TRM lift; it is a repair-prompt arm using the same 3B model plus public validator feedback.
- Not allowed: do not conflate `metta_runtime_blind_repair` with validator-feedback repair; blind repair receives no validator verdict details.
