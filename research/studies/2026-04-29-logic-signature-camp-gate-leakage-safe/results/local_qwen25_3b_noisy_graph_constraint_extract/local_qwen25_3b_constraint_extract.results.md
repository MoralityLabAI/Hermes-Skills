# Local Qwen2.5-3B Constraint Extraction Camp-Gate Run

Generated: `2026-04-29T19:01:48.411954+00:00`

Evidence class: `live_model_local_3b_constraint_extract`

Model: `D:\Research_Engine\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf`
Peak child RSS: `2356.22 MB`

## Arm Summary

| Arm | Rows | JSON Parse | Strict Packet Exact | Strict Solve Exact | Repair Packet Exact | Repair Solve Exact | Repair Solve Rate | Avg Strict Cell Acc |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline_extract` | 12 | 12 | 0 | 0 | 0 | 0 | 0.0000 | 0.0000 |
| `canonical_packet_solver` | 12 | 12 | 12 | 12 | 12 | 12 | 1.0000 | 1.0000 |
| `metta_graph_extract` | 12 | 12 | 7 | 7 | 9 | 9 | 0.7500 | 0.5833 |
| `metta_schema_extract` | 12 | 12 | 5 | 5 | 6 | 6 | 0.5000 | 0.4167 |

## Repair-Failed Extractions

| Row | Arm | JSON | Strict Packet Exact | Repair Packet Exact | Repair Solve Exact | Output |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `camp_gate_001_5x4_4c_noisy` | `baseline_extract` | 1 | 0 | 0 | 0 | <code>{\n  &quot;height&quot;: 5,\n  &quot;width&quot;: 4,\n  &quot;fixed_tents&quot;: [\n    {&quot;row&quot;: 1, &quot;col&quot;: 1},\n    {&quot;row&quot;: 1, &quot;col&quot;: 3},\n    {&quot;row&quot;: 4, &quot;col&quot;: 2},\n    {&quot;row&</code> |
| `camp_gate_001_5x4_4c_noisy` | `metta_graph_extract` | 1 | 0 | 0 | 0 | <code>{&quot;height&quot;: 5, &quot;width&quot;: 4, &quot;fixed_tents&quot;: [[&quot;1&quot;, &quot;1&quot;], [&quot;1&quot;, &quot;3&quot;], [&quot;4&quot;, &quot;2&quot;], [&quot;5&quot;, &quot;3&quot;]], &quot;row_c_counts&quot;: [2, 0, 0, 1, </code> |
| `camp_gate_002_4x4_3c_noisy` | `baseline_extract` | 1 | 0 | 0 | 0 | <code>{\n  &quot;height&quot;: 4,\n  &quot;width&quot;: 4,\n  &quot;fixed_tents&quot;: [\n    {\n      &quot;row&quot;: 2,\n      &quot;column&quot;: 3\n    },\n    {\n      &quot;row&quot;: 4,\n      &quot;column&quot;: 1\n    },\n    {\n      &</code> |
| `camp_gate_002_4x4_3c_noisy` | `metta_schema_extract` | 1 | 0 | 0 | 0 | <code>{&quot;col_c_counts&quot;: [1, 0, 0, 2], &quot;fixed_tents&quot;: [[2, 3], [4, 1], [4, 3]], &quot;height&quot;: 4, &quot;row_c_counts&quot;: [1, 0, 0, 2], &quot;width&quot;: 4}</code> |
| `camp_gate_002_4x4_3c_noisy` | `metta_graph_extract` | 1 | 0 | 0 | 0 | <code>{&quot;col_c_counts&quot;: [1, 0, 0, 2], &quot;fixed_tents&quot;: [[&quot;2&quot;, &quot;3&quot;], [&quot;4&quot;, &quot;1&quot;], [&quot;4&quot;, &quot;3&quot;]], &quot;height&quot;: 4, &quot;row_c_counts&quot;: [1, 0, 0, 2], &quot;width&q</code> |
| `camp_gate_003_4x5_4c_noisy` | `baseline_extract` | 1 | 0 | 0 | 0 | <code>{\n  &quot;height&quot;: 4,\n  &quot;width&quot;: 5,\n  &quot;fixed_tents&quot;: 10,\n  &quot;row_c_counts&quot;: [1, 1, 0, 2],\n  &quot;col_c_counts&quot;: [1, 0, 1, 0, 2]\n}</code> |
| `camp_gate_003_4x5_4c_noisy` | `metta_schema_extract` | 1 | 0 | 0 | 0 | <code>{&quot;col_c_counts&quot;: [1, 0, 1, 0, 2], &quot;fixed_tents&quot;: [[0, 0], [0, 4], [4, 2], [4, 4]], &quot;height&quot;: 4, &quot;row_c_counts&quot;: [1, 0, 1, 0, 2], &quot;width&quot;: 5}</code> |
| `camp_gate_003_4x5_4c_noisy` | `metta_graph_extract` | 1 | 0 | 0 | 0 | <code>{&quot;col_c_counts&quot;: [1, 0, 1, 0, 2], &quot;fixed_tents&quot;: [[&quot;1&quot;, &quot;1&quot;], [&quot;2&quot;, &quot;1&quot;], [&quot;4&quot;, &quot;2&quot;]], &quot;height&quot;: 4, &quot;row_c_counts&quot;: [1, 1, 0, 2], &quot;widt</code> |
| `camp_gate_004_5x4_4c_noisy` | `baseline_extract` | 1 | 0 | 0 | 0 | <code>{\n  &quot;height&quot;: 5,\n  &quot;width&quot;: 4,\n  &quot;fixed_tents&quot;: 4,\n  &quot;row_c_counts&quot;: [1, 0, 2, 0, 1],\n  &quot;col_c_counts&quot;: [1, 1, 1, 1]\n}</code> |
| `camp_gate_005_5x5_5c_noisy` | `baseline_extract` | 1 | 0 | 0 | 0 | <code>{\n  &quot;height&quot;: 5,\n  &quot;width&quot;: 5,\n  &quot;fixed_tents&quot;: 5,\n  &quot;row_c_counts&quot;: [1, 2, 0, 2, 0],\n  &quot;col_c_counts&quot;: [2, 0, 1, 0, 2]\n}</code> |
| `camp_gate_006_4x4_3c_noisy` | `baseline_extract` | 1 | 0 | 0 | 0 | <code>{\n  &quot;height&quot;: 4,\n  &quot;width&quot;: 4,\n  &quot;fixed_tents&quot;: [&quot;r1c1&quot;, &quot;r3c1&quot;, &quot;r3c4&quot;],\n  &quot;row_c_counts&quot;: [1, 1, 0, 1],\n  &quot;col_c_counts&quot;: [1, 1, 0, 1]\n}</code> |
| `camp_gate_007_5x4_4c_noisy` | `baseline_extract` | 1 | 0 | 0 | 0 | <code>{\n  &quot;height&quot;: 5,\n  &quot;width&quot;: 4,\n  &quot;fixed_tents&quot;: [\n    1, 3, 4, 5\n  ],\n  &quot;row_c_counts&quot;: [\n    1, 0, 1, 1, 1\n  ],\n  &quot;col_c_counts&quot;: [\n    1, 0, 2, 1\n  ]\n}</code> |
| `camp_gate_007_5x4_4c_noisy` | `metta_schema_extract` | 1 | 0 | 0 | 0 | <code>{&quot;col_c_counts&quot;: [1, 0, 2, 1], &quot;fixed_tents&quot;: [[0, 1], [1, 3], [2, 4], [3, 2]], &quot;height&quot;: 5, &quot;row_c_counts&quot;: [1, 0, 2, 1], &quot;width&quot;: 4}</code> |
| `camp_gate_008_4x4_3c_noisy` | `baseline_extract` | 1 | 0 | 0 | 0 | <code>{\n  &quot;height&quot;: 4,\n  &quot;width&quot;: 4,\n  &quot;fixed_tents&quot;: 3,\n  &quot;row_c_counts&quot;: [1, 1, 0, 1],\n  &quot;col_c_counts&quot;: [1, 1, 0, 1]\n}</code> |
| `camp_gate_009_4x5_4c_noisy` | `baseline_extract` | 1 | 0 | 0 | 0 | <code>{\n  &quot;height&quot;: 4,\n  &quot;width&quot;: 5,\n  &quot;fixed_tents&quot;: 4,\n  &quot;row_c_counts&quot;: {\n    &quot;1&quot;: 1,\n    &quot;2&quot;: 1,\n    &quot;3&quot;: 0,\n    &quot;4&quot;: 2\n  },\n  &quot;col_c_counts&quot;:</code> |
| `camp_gate_009_4x5_4c_noisy` | `metta_schema_extract` | 1 | 0 | 0 | 0 | <code>{&quot;col_c_counts&quot;: [2, 0, 1, 1, 0], &quot;fixed_tents&quot;: [[1, 3], [2, 1], [3, 4], [4, 2]], &quot;height&quot;: 4, &quot;row_c_counts&quot;: [2, 1, 1, 2], &quot;width&quot;: 5}</code> |
| `camp_gate_010_5x4_4c_noisy` | `baseline_extract` | 1 | 0 | 0 | 0 | <code>{\n  &quot;height&quot;: 5,\n  &quot;width&quot;: 4,\n  &quot;fixed_tents&quot;: 4,\n  &quot;row_c_counts&quot;: [1, 1, 0, 0, 2],\n  &quot;col_c_counts&quot;: [2, 0, 2, 0]\n}</code> |
| `camp_gate_010_5x4_4c_noisy` | `metta_schema_extract` | 1 | 0 | 0 | 0 | <code>{&quot;col_c_counts&quot;: [1, 0, 2, 0], &quot;fixed_tents&quot;: [[&quot;1&quot;, &quot;2&quot;], [&quot;1&quot;, &quot;3&quot;], [&quot;4&quot;, &quot;1&quot;], [&quot;5&quot;, &quot;4&quot;]], &quot;height&quot;: 5, &quot;row_c_counts&qu</code> |
| `camp_gate_011_5x5_5c_noisy` | `baseline_extract` | 1 | 0 | 0 | 0 | <code>{\n  &quot;height&quot;: 5,\n  &quot;width&quot;: 5,\n  &quot;fixed_tents&quot;: 15,\n  &quot;row_c_counts&quot;: [1, 0, 2, 0, 2],\n  &quot;col_c_counts&quot;: [2, 1, 0, 1, 1]\n}</code> |
| `camp_gate_011_5x5_5c_noisy` | `metta_schema_extract` | 1 | 0 | 0 | 0 | <code>{&quot;col_c_counts&quot;: [2, 1, 0, 1, 1], &quot;fixed_tents&quot;: [[0, 1], [2, 0], [3, 4], [5, 2], [5, 5]], &quot;height&quot;: 5, &quot;row_c_counts&quot;: [1, 0, 2, 0, 2], &quot;width&quot;: 5}</code> |
| `camp_gate_012_4x4_3c_noisy` | `baseline_extract` | 1 | 0 | 0 | 0 | <code>{\n  &quot;height&quot;: 4,\n  &quot;width&quot;: 4,\n  &quot;fixed_tents&quot;: 3,\n  &quot;row_c_counts&quot;: [1, 1, 0, 1],\n  &quot;col_c_counts&quot;: [1, 0, 1, 1]\n}</code> |

## Interpretation

- This is the extraction-side follow-up to the public-constraint solver ablation.
- If extraction succeeds, the skill can shift the LLM from solver to constraint transcriber.
- If extraction fails on less-structured prompts, the next TRM target is constraint extraction rather than grid execution.
