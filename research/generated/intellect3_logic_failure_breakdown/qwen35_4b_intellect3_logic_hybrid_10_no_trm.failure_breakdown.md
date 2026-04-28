# Intellect-3 Logic Failure Breakdown: qwen35_4b_intellect3_logic_hybrid_10_no_trm

Source: `C:\projects\Hermes-Skills\Hermes Skills\data\qwen35_4b_intellect3_logic_hybrid_10_no_trm\predictions.jsonl`

## Arm Summary

| Arm | Rows | Exact Match | Failed Rows | Avg Cell Acc | Avg Wrong Cells On Failed | Top Failure Tags |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `logic_skill` | 10 | 0.0000 | 10 | 0.7810 | 5.0000 | camp_count_mismatch:10, camp_signature_mismatch:10, cell_mismatch:10, tent_count_mismatch:1, tent_signature_mismatch:1 |
| `vanilla` | 10 | 0.0000 | 10 | 0.7880 | 4.9000 | camp_count_mismatch:10, camp_signature_mismatch:10, cell_mismatch:10 |

## Baseline Vs Compare

Baseline arm: `vanilla`. Compare arm: `vanilla`.

| Status | Count |
| --- | ---: |
| `unfixed` | 10 |

## Failed Or Changed Problems

| Row | Status | Baseline Exact | Compare Exact | Acc Delta | Compare Wrong Cells | Compare Failure Tags | Compare Confusions |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| `intellect_3_logic_0` | `unfixed` | False | False | 0.0000 | 7 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:5, X->C:2 |
| `intellect_3_logic_1` | `unfixed` | False | False | 0.0000 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:4, X->C:1 |
| `intellect_3_logic_2` | `unfixed` | False | False | 0.0000 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:5 |
| `intellect_3_logic_3` | `unfixed` | False | False | 0.0000 | 4 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:4 |
| `intellect_3_logic_4` | `unfixed` | False | False | 0.0000 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:5 |
| `intellect_3_logic_5` | `unfixed` | False | False | 0.0000 | 6 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:4, X->C:2 |
| `intellect_3_logic_6` | `unfixed` | False | False | 0.0000 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:5 |
| `intellect_3_logic_7` | `unfixed` | False | False | 0.0000 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:5 |
| `intellect_3_logic_8` | `unfixed` | False | False | 0.0000 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:3 |
| `intellect_3_logic_9` | `unfixed` | False | False | 0.0000 | 4 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:4 |
