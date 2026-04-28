# Intellect-3 Logic Failure Breakdown: qwen35_4b_intellect3_logic_hybrid_25

Source: `C:\projects\trm_observability_harness\data\qwen35_4b_intellect3_logic_hybrid_25\predictions.jsonl`

## Arm Summary

| Arm | Rows | Exact Match | Failed Rows | Avg Cell Acc | Avg Wrong Cells On Failed | Top Failure Tags |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `generic_skill` | 25 | 0.0000 | 25 | 0.6856 | 5.2800 | camp_count_mismatch:23, camp_signature_mismatch:23, cell_mismatch:23, tent_count_mismatch:3, tent_signature_mismatch:3 |
| `logic_skill` | 25 | 0.0000 | 25 | 0.5121 | 4.6800 | camp_signature_mismatch:18, cell_mismatch:18, camp_count_mismatch:17, prediction_parse_failure:7, tent_count_mismatch:2 |
| `logic_skill_trm` | 25 | 1.0000 | 0 | 1.0000 | 0.0000 | - |
| `vanilla` | 25 | 0.0000 | 25 | 0.7411 | 5.8400 | camp_signature_mismatch:25, cell_mismatch:25, camp_count_mismatch:24, tent_signature_mismatch:5, tent_count_mismatch:4 |

## Baseline Vs Compare

Baseline arm: `vanilla`. Compare arm: `logic_skill_trm`.

| Status | Count |
| --- | ---: |
| `fixed_by_compare` | 25 |

## Failed Or Changed Problems

| Row | Status | Baseline Exact | Compare Exact | Acc Delta | Compare Wrong Cells | Compare Failure Tags | Compare Confusions |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| `intellect_3_logic_0` | `fixed_by_compare` | False | True | 0.3200 | 0 | - | - |
| `intellect_3_logic_1` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_10` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_11` | `fixed_by_compare` | False | True | 0.2400 | 0 | - | - |
| `intellect_3_logic_12` | `fixed_by_compare` | False | True | 0.2800 | 0 | - | - |
| `intellect_3_logic_13` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_14` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_15` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_16` | `fixed_by_compare` | False | True | 0.3500 | 0 | - | - |
| `intellect_3_logic_17` | `fixed_by_compare` | False | True | 0.2500 | 0 | - | - |
| `intellect_3_logic_18` | `fixed_by_compare` | False | True | 0.3200 | 0 | - | - |
| `intellect_3_logic_19` | `fixed_by_compare` | False | True | 0.2400 | 0 | - | - |
| `intellect_3_logic_2` | `fixed_by_compare` | False | True | 0.3600 | 0 | - | - |
| `intellect_3_logic_20` | `fixed_by_compare` | False | True | 0.1000 | 0 | - | - |
| `intellect_3_logic_21` | `fixed_by_compare` | False | True | 0.2400 | 0 | - | - |
| `intellect_3_logic_22` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_23` | `fixed_by_compare` | False | True | 0.2800 | 0 | - | - |
| `intellect_3_logic_24` | `fixed_by_compare` | False | True | 0.3125 | 0 | - | - |
| `intellect_3_logic_3` | `fixed_by_compare` | False | True | 0.3000 | 0 | - | - |
| `intellect_3_logic_4` | `fixed_by_compare` | False | True | 0.3200 | 0 | - | - |
| `intellect_3_logic_5` | `fixed_by_compare` | False | True | 0.2400 | 0 | - | - |
| `intellect_3_logic_6` | `fixed_by_compare` | False | True | 0.2400 | 0 | - | - |
| `intellect_3_logic_7` | `fixed_by_compare` | False | True | 0.2800 | 0 | - | - |
| `intellect_3_logic_8` | `fixed_by_compare` | False | True | 0.3000 | 0 | - | - |
| `intellect_3_logic_9` | `fixed_by_compare` | False | True | 0.3000 | 0 | - | - |
