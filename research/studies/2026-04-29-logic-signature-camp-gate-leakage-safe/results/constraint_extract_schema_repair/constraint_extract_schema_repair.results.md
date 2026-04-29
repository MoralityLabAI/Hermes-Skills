# Local Qwen2.5-3B Constraint Extraction Camp-Gate Run

Generated: `2026-04-29T18:36:29.532353+00:00`

Evidence class: `live_model_local_3b_constraint_extract`

Model: `D:\Research_Engine\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf`
Peak child RSS: `0.00 MB`

## Arm Summary

| Arm | Rows | JSON Parse | Strict Packet Exact | Strict Solve Exact | Repair Packet Exact | Repair Solve Exact | Repair Solve Rate | Avg Strict Cell Acc |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline_extract` | 12 | 0 | 0 | 0 | 0 | 0 | 0.0000 | 0.0000 |
| `canonical_packet_solver` | 12 | 12 | 12 | 12 | 12 | 12 | 1.0000 | 1.0000 |
| `metta_schema_extract` | 12 | 12 | 0 | 0 | 12 | 12 | 1.0000 | 0.0000 |

## Repair-Failed Extractions

| Row | Arm | JSON | Strict Packet Exact | Repair Packet Exact | Repair Solve Exact | Output |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `camp_gate_001_5x4_4c` | `baseline_extract` | 0 | 0 | 0 | 0 | <code>T C X X\nC T C C\nX C X C\nT X T C\nX C C X</code> |
| `camp_gate_002_4x4_3c` | `baseline_extract` | 0 | 0 | 0 | 0 | <code>X C X X\nC T C X\nX C X C\nX X C T</code> |
| `camp_gate_003_4x5_4c` | `baseline_extract` | 0 | 0 | 0 | 0 | <code>T C X\nX C X\nT C X\nX C X</code> |
| `camp_gate_004_5x4_4c` | `baseline_extract` | 0 | 0 | 0 | 0 | <code>T C X X\nC T C X\nX C C T\nX X C T\nX C C X</code> |
| `camp_gate_005_5x5_5c` | `baseline_extract` | 0 | 0 | 0 | 0 | <code>T C X\nX C X\nT C X\nX C X\nT C X</code> |
| `camp_gate_006_4x4_3c` | `baseline_extract` | 0 | 0 | 0 | 0 | <code>T C X X\nX C T T\nT X C X\nX X T C</code> |
| `camp_gate_007_5x4_4c` | `baseline_extract` | 0 | 0 | 0 | 0 | <code>T C X X\nC T C X\nT C C X\nX C C T\nX X C T</code> |
| `camp_gate_008_4x4_3c` | `baseline_extract` | 0 | 0 | 0 | 0 | <code>T C X X\nC T C X\nX C X T\nX X T C</code> |
| `camp_gate_009_4x5_4c` | `baseline_extract` | 0 | 0 | 0 | 0 | <code>T C X\nX C X\nT C X\nX C X</code> |
| `camp_gate_010_5x4_4c` | `baseline_extract` | 0 | 0 | 0 | 0 | <code>T C X X\nC T C T\nX C C X\nT X T C\nX C T X</code> |
| `camp_gate_011_5x5_5c` | `baseline_extract` | 0 | 0 | 0 | 0 | <code>X C X C X\nC T C T C\nX C X C X\nT C T C T\nX C X C X</code> |
| `camp_gate_012_4x4_3c` | `baseline_extract` | 0 | 0 | 0 | 0 | <code>T C X X\nX C T X\nT X C T\nX X C X</code> |

## Interpretation

- This is the extraction-side follow-up to the public-constraint solver ablation.
- If extraction succeeds, the skill can shift the LLM from solver to constraint transcriber.
- If extraction fails on less-structured prompts, the next TRM target is constraint extraction rather than grid execution.
