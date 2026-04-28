# Intellect-3 Logic Failure Breakdown: qwen27b_intellect3_logic_hybrid_200

Source: `C:\projects\trm_observability_harness\data\qwen27b_intellect3_logic_hybrid_200\predictions.jsonl`

## Arm Summary

| Arm | Rows | Exact Match | Failed Rows | Avg Cell Acc | Avg Wrong Cells On Failed | Top Failure Tags |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `generic_skill` | 109 | 0.0092 | 108 | 0.8079 | 4.1574 | camp_count_mismatch:108, camp_signature_mismatch:108, cell_mismatch:108, tent_count_mismatch:1, tent_signature_mismatch:1 |
| `logic_skill` | 109 | 0.0000 | 109 | 0.8076 | 4.1284 | camp_count_mismatch:109, camp_signature_mismatch:109, cell_mismatch:109, tent_count_mismatch:3, tent_signature_mismatch:3 |
| `logic_skill_trm` | 109 | 0.3028 | 76 | 0.8787 | 3.6184 | cell_mismatch:76, camp_signature_mismatch:61, camp_count_mismatch:39 |
| `vanilla` | 109 | 0.0000 | 109 | 0.8061 | 4.1560 | camp_count_mismatch:109, camp_signature_mismatch:109, cell_mismatch:109 |

## Baseline Vs Compare

Baseline arm: `vanilla`. Compare arm: `logic_skill_trm`.

| Status | Count |
| --- | ---: |
| `fixed_by_compare` | 33 |
| `partial_improvement` | 40 |
| `partial_regression` | 25 |
| `unfixed` | 11 |

## Failed Or Changed Problems

| Row | Status | Baseline Exact | Compare Exact | Acc Delta | Compare Wrong Cells | Compare Failure Tags | Compare Confusions |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| `intellect_3_logic_0` | `partial_improvement` | False | False | 0.0400 | 4 | camp_signature_mismatch, cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_1` | `partial_improvement` | False | False | 0.0500 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_10` | `partial_improvement` | False | False | 0.1500 | 1 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:1 |
| `intellect_3_logic_100` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_101` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_102` | `partial_regression` | False | False | -0.0500 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:3, X->C:2 |
| `intellect_3_logic_103` | `partial_regression` | False | False | -0.0667 | 4 | cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_104` | `partial_regression` | False | False | -0.1000 | 6 | camp_signature_mismatch, cell_mismatch | C->X:3, X->C:3 |
| `intellect_3_logic_105` | `fixed_by_compare` | False | True | 0.1875 | 0 | - | - |
| `intellect_3_logic_106` | `partial_regression` | False | False | -0.1000 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_107` | `partial_improvement` | False | False | 0.0400 | 4 | cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_108` | `partial_improvement` | False | False | 0.0400 | 4 | cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_11` | `partial_improvement` | False | False | 0.0800 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_12` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_13` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_14` | `partial_improvement` | False | False | 0.0400 | 4 | camp_signature_mismatch, cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_15` | `partial_improvement` | False | False | 0.1333 | 1 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:1 |
| `intellect_3_logic_16` | `partial_regression` | False | False | -0.1000 | 6 | camp_signature_mismatch, cell_mismatch | C->X:3, X->C:3 |
| `intellect_3_logic_17` | `partial_regression` | False | False | -0.0500 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:3, X->C:2 |
| `intellect_3_logic_18` | `partial_improvement` | False | False | 0.0800 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_19` | `partial_improvement` | False | False | 0.0400 | 4 | cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_2` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_20` | `partial_improvement` | False | False | 0.0500 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_21` | `partial_improvement` | False | False | 0.0400 | 4 | camp_signature_mismatch, cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_22` | `partial_improvement` | False | False | 0.1600 | 1 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:1 |
| `intellect_3_logic_23` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_24` | `partial_regression` | False | False | -0.1250 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:3, X->C:2 |
| `intellect_3_logic_25` | `partial_improvement` | False | False | 0.1600 | 1 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:1 |
| `intellect_3_logic_26` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_27` | `partial_improvement` | False | False | 0.0625 | 1 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:1 |
| `intellect_3_logic_28` | `partial_improvement` | False | False | 0.1200 | 2 | camp_signature_mismatch, cell_mismatch | C->X:1, X->C:1 |
| `intellect_3_logic_29` | `partial_improvement` | False | False | 0.0667 | 2 | camp_signature_mismatch, cell_mismatch | C->X:1, X->C:1 |
| `intellect_3_logic_3` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_30` | `partial_improvement` | False | False | 0.1200 | 2 | camp_signature_mismatch, cell_mismatch | C->X:1, X->C:1 |
| `intellect_3_logic_31` | `unfixed` | False | False | 0.0000 | 4 | cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_32` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_33` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_34` | `partial_regression` | False | False | -0.0667 | 4 | cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_35` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_36` | `partial_improvement` | False | False | 0.0800 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_37` | `unfixed` | False | False | 0.0000 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:3, X->C:2 |
| `intellect_3_logic_38` | `unfixed` | False | False | 0.0000 | 1 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:1 |
| `intellect_3_logic_39` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_4` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_40` | `partial_regression` | False | False | -0.0667 | 4 | cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_41` | `unfixed` | False | False | 0.0000 | 4 | cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_42` | `unfixed` | False | False | 0.0000 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:3, X->C:2 |
| `intellect_3_logic_43` | `partial_improvement` | False | False | 0.1600 | 1 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:1 |
| `intellect_3_logic_44` | `partial_regression` | False | False | -0.1000 | 6 | camp_signature_mismatch, cell_mismatch | C->X:3, X->C:3 |
| `intellect_3_logic_45` | `partial_improvement` | False | False | 0.0400 | 4 | camp_signature_mismatch, cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_46` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_47` | `unfixed` | False | False | 0.0000 | 4 | cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_48` | `partial_improvement` | False | False | 0.0500 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_49` | `partial_regression` | False | False | -0.0400 | 6 | camp_signature_mismatch, cell_mismatch | C->X:3, X->C:3 |
| `intellect_3_logic_5` | `partial_improvement` | False | False | 0.0400 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_50` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_51` | `partial_regression` | False | False | -0.0500 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:3, X->C:2 |
| `intellect_3_logic_52` | `partial_improvement` | False | False | 0.0400 | 4 | cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_53` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_54` | `partial_regression` | False | False | -0.0500 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:3, X->C:2 |
| `intellect_3_logic_55` | `partial_improvement` | False | False | 0.0500 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_56` | `partial_regression` | False | False | -0.2000 | 6 | camp_signature_mismatch, cell_mismatch | C->X:3, X->C:3 |
| `intellect_3_logic_57` | `partial_regression` | False | False | -0.1000 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:3, X->C:2 |
| `intellect_3_logic_58` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_59` | `partial_regression` | False | False | -0.0800 | 7 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:4, X->C:3 |
| `intellect_3_logic_6` | `partial_improvement` | False | False | 0.1200 | 2 | camp_signature_mismatch, cell_mismatch | C->X:1, X->C:1 |
| `intellect_3_logic_60` | `partial_improvement` | False | False | 0.1000 | 2 | camp_signature_mismatch, cell_mismatch | C->X:1, X->C:1 |
| `intellect_3_logic_61` | `partial_improvement` | False | False | 0.1200 | 2 | camp_signature_mismatch, cell_mismatch | C->X:1, X->C:1 |
| `intellect_3_logic_62` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_63` | `partial_regression` | False | False | -0.0400 | 6 | camp_signature_mismatch, cell_mismatch | C->X:3, X->C:3 |
| `intellect_3_logic_64` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_65` | `unfixed` | False | False | 0.0000 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_66` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_67` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_68` | `unfixed` | False | False | 0.0000 | 4 | cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_69` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_7` | `partial_regression` | False | False | -0.0400 | 6 | cell_mismatch | C->X:3, X->C:3 |
| `intellect_3_logic_70` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_71` | `partial_regression` | False | False | -0.1333 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:3, X->C:2 |
| `intellect_3_logic_72` | `partial_improvement` | False | False | 0.0400 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_73` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_74` | `partial_improvement` | False | False | 0.1000 | 2 | camp_signature_mismatch, cell_mismatch | C->X:1, X->C:1 |
| `intellect_3_logic_75` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_76` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_77` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_78` | `partial_improvement` | False | False | 0.1200 | 2 | camp_signature_mismatch, cell_mismatch | C->X:1, X->C:1 |
| `intellect_3_logic_79` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_8` | `unfixed` | False | False | 0.0000 | 4 | cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_80` | `partial_regression` | False | False | -0.0667 | 2 | camp_signature_mismatch, cell_mismatch | C->X:1, X->C:1 |
| `intellect_3_logic_81` | `partial_improvement` | False | False | 0.1600 | 1 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:1 |
| `intellect_3_logic_82` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_83` | `partial_improvement` | False | False | 0.0500 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_84` | `partial_improvement` | False | False | 0.0800 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_85` | `partial_improvement` | False | False | 0.0400 | 4 | cell_mismatch | C->X:2, X->C:2 |
| `intellect_3_logic_86` | `partial_regression` | False | False | -0.0500 | 5 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:3, X->C:2 |
| `intellect_3_logic_87` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_88` | `partial_regression` | False | False | -0.1000 | 6 | camp_signature_mismatch, cell_mismatch | C->X:3, X->C:3 |
| `intellect_3_logic_89` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_9` | `partial_regression` | False | False | -0.1500 | 7 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:4, X->C:3 |
| `intellect_3_logic_90` | `partial_regression` | False | False | -0.0400 | 6 | cell_mismatch | C->X:3, X->C:3 |
| `intellect_3_logic_91` | `fixed_by_compare` | False | True | 0.2000 | 0 | - | - |
| `intellect_3_logic_92` | `partial_regression` | False | False | -0.0400 | 6 | camp_signature_mismatch, cell_mismatch | C->X:3, X->C:3 |
| `intellect_3_logic_93` | `partial_improvement` | False | False | 0.1000 | 2 | camp_signature_mismatch, cell_mismatch | C->X:1, X->C:1 |
| `intellect_3_logic_94` | `partial_improvement` | False | False | 0.0500 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_95` | `partial_improvement` | False | False | 0.1600 | 1 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:1 |
| `intellect_3_logic_96` | `partial_improvement` | False | False | 0.0800 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_97` | `unfixed` | False | False | 0.0000 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_98` | `partial_improvement` | False | False | 0.0800 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
| `intellect_3_logic_99` | `unfixed` | False | False | 0.0000 | 3 | camp_count_mismatch, camp_signature_mismatch, cell_mismatch | C->X:2, X->C:1 |
