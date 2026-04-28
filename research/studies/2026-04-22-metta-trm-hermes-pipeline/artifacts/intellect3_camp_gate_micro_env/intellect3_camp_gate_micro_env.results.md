# Intellect-3 Campsite Camp-Gate Micro-Env

Source: `C:\projects\trm_observability_harness\data\qwen27b_intellect3_logic_hybrid_200\predictions.jsonl`
Generated: `2026-04-26T00:52:48.878329+00:00`

MeTTa contract: [`intellect3_camp_gate_contract.metta`](<intellect3_camp_gate_contract.metta>)

C-only repair isolates camp placement failures; dual T+C projection measures whether a coupled signature gate can convert candidate grids into exact answers.

## Arm Summary

| Arm | Rows | Original Exact | Original Cell Acc | T Sig Pass | C Sig Pass | C Repair Exact | Dual Repair Exact | Fixed By Dual | Unresolved Dual |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `generic_skill` | 109 | 0.0092 | 0.8079 | 0.9908 | 0.0092 | 0.4954 | 0.4954 | 53 | 55 |
| `logic_skill` | 109 | 0.0000 | 0.8076 | 0.9725 | 0.0000 | 0.4587 | 0.4771 | 52 | 57 |
| `logic_skill_trm` | 109 | 0.3028 | 0.8787 | 1.0000 | 0.4404 | 0.6789 | 0.6697 | 40 | 36 |
| `vanilla` | 109 | 0.0000 | 0.8061 | 1.0000 | 0.0000 | 0.4862 | 0.4862 | 53 | 56 |

## Failure Tags

| Arm | Original Tags | Original Confusions | Dual-Unresolved Tags | Dual-Unresolved Confusions |
| --- | --- | --- | --- | --- |
| `generic_skill` | c_signature_fail:108, cell_commit_fail:108, t_signature_fail:1 | C->X:437, X->C:11, T->C:1 | cell_commit_fail:55 | C->X:123, X->C:123 |
| `logic_skill` | c_signature_fail:109, cell_commit_fail:109, t_signature_fail:3 | C->X:431, X->C:14, T->C:4, C->T:1 | cell_commit_fail:57 | C->X:124, X->C:124, C->T:2, T->C:2 |
| `logic_skill_trm` | cell_commit_fail:76, c_signature_fail:61 | C->X:157, X->C:118 | cell_commit_fail:36 | C->X:77, X->C:77, C->T:1, T->C:1, T->X:1 |
| `vanilla` | c_signature_fail:109, cell_commit_fail:109 | C->X:452, X->C:1 | cell_commit_fail:56 | C->X:125, X->C:125 |

## Failed Problem Rows

| Row | Arm | Original Acc | Original Tags | Original Confusions | C Repair Acc | Dual Repair Acc | Dual Tags | Dual Confusions |
| --- | --- | ---: | --- | --- | ---: | ---: | --- | --- |
| `intellect_3_logic_0` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_0` | `generic_skill` | 0.8800 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_0` | `logic_skill` | 0.7600 | t_signature_fail, c_signature_fail, cell_commit_fail | C->X:3, T->C:2, C->T:1 | 0.0000 | 1.0000 | - | - |
| `intellect_3_logic_0` | `logic_skill_trm` | 0.8400 | c_signature_fail, cell_commit_fail | C->X:2, X->C:2 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_1` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_1` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_1` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_1` | `logic_skill_trm` | 0.8500 | c_signature_fail, cell_commit_fail | C->X:2, X->C:1 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_2` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.7600 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_2` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.7600 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_2` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.7600 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_3` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_3` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_3` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_4` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_4` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_4` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_5` | `vanilla` | 0.8400 | c_signature_fail, cell_commit_fail | C->X:3, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_5` | `generic_skill` | 0.7600 | c_signature_fail, cell_commit_fail | C->X:4, X->C:2 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_5` | `logic_skill` | 0.7600 | c_signature_fail, cell_commit_fail | C->X:4, X->C:2 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_5` | `logic_skill_trm` | 0.8800 | c_signature_fail, cell_commit_fail | C->X:2, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_6` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_6` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_6` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_6` | `logic_skill_trm` | 0.9200 | c_signature_fail, cell_commit_fail | C->X:1, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_7` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_7` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_7` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_7` | `logic_skill_trm` | 0.7600 | cell_commit_fail | C->X:3, X->C:3 | 0.7600 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_8` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 1.0000 | - | - |
| `intellect_3_logic_8` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 1.0000 | - | - |
| `intellect_3_logic_8` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 1.0000 | - | - |
| `intellect_3_logic_8` | `logic_skill_trm` | 0.8000 | cell_commit_fail | C->X:2, X->C:2 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_9` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_9` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_9` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_9` | `logic_skill_trm` | 0.6500 | c_signature_fail, cell_commit_fail | C->X:4, X->C:3 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_10` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_10` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_10` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_10` | `logic_skill_trm` | 0.9500 | c_signature_fail, cell_commit_fail | C->X:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_11` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_11` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3, X->C:2 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_11` | `logic_skill` | 0.8400 | c_signature_fail, cell_commit_fail | C->X:3, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_11` | `logic_skill_trm` | 0.8800 | c_signature_fail, cell_commit_fail | C->X:2, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_12` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_12` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_12` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_13` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_13` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_13` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_14` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_14` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_14` | `logic_skill` | 0.7600 | c_signature_fail, cell_commit_fail | C->X:5, X->C:1 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_14` | `logic_skill_trm` | 0.8400 | c_signature_fail, cell_commit_fail | C->X:2, X->C:2 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_15` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_15` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_15` | `logic_skill` | 0.8667 | c_signature_fail, cell_commit_fail | C->X:2 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_15` | `logic_skill_trm` | 0.9333 | c_signature_fail, cell_commit_fail | C->X:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_16` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_16` | `generic_skill` | 0.8500 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_16` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_16` | `logic_skill_trm` | 0.7000 | c_signature_fail, cell_commit_fail | C->X:3, X->C:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_17` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_17` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_17` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_17` | `logic_skill_trm` | 0.7500 | c_signature_fail, cell_commit_fail | C->X:3, X->C:2 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_18` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_18` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_18` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_18` | `logic_skill_trm` | 0.8800 | c_signature_fail, cell_commit_fail | C->X:2, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_19` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_19` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_19` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_19` | `logic_skill_trm` | 0.8400 | cell_commit_fail | C->X:2, X->C:2 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_20` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_20` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_20` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_20` | `logic_skill_trm` | 0.8500 | c_signature_fail, cell_commit_fail | C->X:2, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_21` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_21` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_21` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_21` | `logic_skill_trm` | 0.8400 | c_signature_fail, cell_commit_fail | C->X:2, X->C:2 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_22` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_22` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_22` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_22` | `logic_skill_trm` | 0.9600 | c_signature_fail, cell_commit_fail | C->X:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_23` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_23` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_23` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_24` | `vanilla` | 0.8125 | c_signature_fail, cell_commit_fail | C->X:3 | 0.7500 | 0.7500 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_24` | `generic_skill` | 0.8125 | c_signature_fail, cell_commit_fail | C->X:3 | 0.7500 | 0.7500 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_24` | `logic_skill` | 0.8125 | c_signature_fail, cell_commit_fail | C->X:3 | 0.7500 | 0.7500 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_24` | `logic_skill_trm` | 0.6875 | c_signature_fail, cell_commit_fail | C->X:3, X->C:2 | 0.7500 | 0.7500 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_25` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_25` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_25` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_25` | `logic_skill_trm` | 0.9600 | c_signature_fail, cell_commit_fail | C->X:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_26` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_26` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_26` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_27` | `vanilla` | 0.8750 | c_signature_fail, cell_commit_fail | C->X:2 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_27` | `generic_skill` | 0.8750 | c_signature_fail, cell_commit_fail | C->X:2 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_27` | `logic_skill` | 0.8125 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_27` | `logic_skill_trm` | 0.9375 | c_signature_fail, cell_commit_fail | C->X:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_28` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_28` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_28` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_28` | `logic_skill_trm` | 0.9200 | c_signature_fail, cell_commit_fail | C->X:1, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_29` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_29` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_29` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_29` | `logic_skill_trm` | 0.8667 | c_signature_fail, cell_commit_fail | C->X:1, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_30` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.7600 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_30` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.7600 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_30` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.7600 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_30` | `logic_skill_trm` | 0.9200 | c_signature_fail, cell_commit_fail | C->X:1, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_31` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_31` | `generic_skill` | 0.8500 | c_signature_fail, cell_commit_fail | C->X:2, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_31` | `logic_skill` | 0.8500 | c_signature_fail, cell_commit_fail | C->X:2, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_31` | `logic_skill_trm` | 0.8000 | cell_commit_fail | C->X:2, X->C:2 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_32` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_32` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_32` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_33` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_33` | `generic_skill` | 0.8500 | c_signature_fail, cell_commit_fail | C->X:2, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_33` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_34` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 0.7333 | 0.7333 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_34` | `generic_skill` | 0.7333 | c_signature_fail, cell_commit_fail | C->X:3, X->C:1 | 0.7333 | 0.7333 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_34` | `logic_skill` | 0.7333 | c_signature_fail, cell_commit_fail | C->X:3, X->C:1 | 0.7333 | 0.7333 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_34` | `logic_skill_trm` | 0.7333 | cell_commit_fail | C->X:2, X->C:2 | 0.7333 | 0.7333 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_35` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_35` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_35` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_36` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_36` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_36` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_36` | `logic_skill_trm` | 0.8800 | c_signature_fail, cell_commit_fail | C->X:2, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_37` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_37` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_37` | `logic_skill` | 0.8400 | t_signature_fail, c_signature_fail, cell_commit_fail | C->X:3, T->C:1 | 0.9600 | 0.8400 | cell_commit_fail | C->T:2, T->C:2 |
| `intellect_3_logic_37` | `logic_skill_trm` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3, X->C:2 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_38` | `vanilla` | 0.9375 | c_signature_fail, cell_commit_fail | C->X:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_38` | `logic_skill` | 0.9375 | c_signature_fail, cell_commit_fail | C->X:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_38` | `logic_skill_trm` | 0.9375 | c_signature_fail, cell_commit_fail | C->X:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_39` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_39` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_39` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_40` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 0.7333 | 0.7333 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_40` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 0.7333 | 0.7333 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_40` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 0.7333 | 0.7333 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_40` | `logic_skill_trm` | 0.7333 | cell_commit_fail | C->X:2, X->C:2 | 0.7333 | 0.7333 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_41` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_41` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_41` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_41` | `logic_skill_trm` | 0.8000 | cell_commit_fail | C->X:2, X->C:2 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_42` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_42` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_42` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_42` | `logic_skill_trm` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3, X->C:2 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_43` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_43` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_43` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_43` | `logic_skill_trm` | 0.9600 | c_signature_fail, cell_commit_fail | C->X:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_44` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_44` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_44` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_44` | `logic_skill_trm` | 0.7000 | c_signature_fail, cell_commit_fail | C->X:3, X->C:3 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_45` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_45` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_45` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_45` | `logic_skill_trm` | 0.8400 | c_signature_fail, cell_commit_fail | C->X:2, X->C:2 | 1.0000 | 0.7600 | cell_commit_fail | C->T:1, C->X:1, T->C:1, T->X:1, X->C:1 |
| `intellect_3_logic_46` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_46` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_46` | `logic_skill` | 0.8400 | c_signature_fail, cell_commit_fail | C->X:3, X->C:1 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_47` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_47` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_47` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_47` | `logic_skill_trm` | 0.8000 | cell_commit_fail | C->X:2, X->C:2 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_48` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_48` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_48` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_48` | `logic_skill_trm` | 0.8500 | c_signature_fail, cell_commit_fail | C->X:2, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_49` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.7600 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_49` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.7600 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_49` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.7600 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_49` | `logic_skill_trm` | 0.7600 | c_signature_fail, cell_commit_fail | C->X:3, X->C:3 | 0.7600 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_50` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_50` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_50` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_51` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_51` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_51` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_51` | `logic_skill_trm` | 0.7500 | c_signature_fail, cell_commit_fail | C->X:3, X->C:2 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_52` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_52` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_52` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_52` | `logic_skill_trm` | 0.8400 | cell_commit_fail | C->X:2, X->C:2 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_53` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_53` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_53` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_54` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_54` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_54` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_54` | `logic_skill_trm` | 0.7500 | c_signature_fail, cell_commit_fail | C->X:3, X->C:2 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_55` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_55` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_55` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3, X->C:1 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_55` | `logic_skill_trm` | 0.8500 | c_signature_fail, cell_commit_fail | C->X:2, X->C:1 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_56` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 0.7333 | 0.7333 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_56` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 0.7333 | 0.7333 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_56` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 0.7333 | 0.7333 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_56` | `logic_skill_trm` | 0.6000 | c_signature_fail, cell_commit_fail | C->X:3, X->C:3 | 0.7333 | 0.7333 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_57` | `vanilla` | 0.8500 | c_signature_fail, cell_commit_fail | C->X:3 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_57` | `generic_skill` | 0.8000 | t_signature_fail, c_signature_fail, cell_commit_fail | C->X:3, T->C:1 | 0.7500 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_57` | `logic_skill` | 0.8000 | t_signature_fail, c_signature_fail, cell_commit_fail | C->X:3, T->C:1 | 0.7500 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_57` | `logic_skill_trm` | 0.7500 | c_signature_fail, cell_commit_fail | C->X:3, X->C:2 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_58` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_58` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_58` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_59` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 1.0000 | - | - |
| `intellect_3_logic_59` | `generic_skill` | 0.8400 | c_signature_fail, cell_commit_fail | C->X:3, X->C:1 | 0.8400 | 1.0000 | - | - |
| `intellect_3_logic_59` | `logic_skill` | 0.8400 | c_signature_fail, cell_commit_fail | C->X:3, X->C:1 | 0.8400 | 1.0000 | - | - |
| `intellect_3_logic_59` | `logic_skill_trm` | 0.7200 | c_signature_fail, cell_commit_fail | C->X:4, X->C:3 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_60` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.7000 | 0.7000 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_60` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.7000 | 0.7000 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_60` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.7000 | 0.7000 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_60` | `logic_skill_trm` | 0.9000 | c_signature_fail, cell_commit_fail | C->X:1, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_61` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_61` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_61` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.7600 | cell_commit_fail | C->X:3, X->C:3 |
| `intellect_3_logic_61` | `logic_skill_trm` | 0.9200 | c_signature_fail, cell_commit_fail | C->X:1, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_62` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_62` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_62` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_63` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 1.0000 | - | - |
| `intellect_3_logic_63` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 1.0000 | - | - |
| `intellect_3_logic_63` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 1.0000 | - | - |
| `intellect_3_logic_63` | `logic_skill_trm` | 0.7600 | c_signature_fail, cell_commit_fail | C->X:3, X->C:3 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_64` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_64` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_64` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_65` | `vanilla` | 0.8125 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_65` | `generic_skill` | 0.8125 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_65` | `logic_skill` | 0.8125 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_65` | `logic_skill_trm` | 0.8125 | c_signature_fail, cell_commit_fail | C->X:2, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_66` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_66` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_66` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_67` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_67` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_67` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_68` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_68` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_68` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3, X->C:1 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_68` | `logic_skill_trm` | 0.8000 | cell_commit_fail | C->X:2, X->C:2 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_69` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.6800 | cell_commit_fail | C->X:4, X->C:4 |
| `intellect_3_logic_69` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.6800 | cell_commit_fail | C->X:4, X->C:4 |
| `intellect_3_logic_69` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.6800 | cell_commit_fail | C->X:4, X->C:4 |
| `intellect_3_logic_70` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_70` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_70` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_71` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_71` | `generic_skill` | 0.9333 | c_signature_fail, cell_commit_fail | C->X:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_71` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_71` | `logic_skill_trm` | 0.6667 | c_signature_fail, cell_commit_fail | C->X:3, X->C:2 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_72` | `vanilla` | 0.8400 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_72` | `generic_skill` | 0.8400 | c_signature_fail, cell_commit_fail | C->X:3, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_72` | `logic_skill` | 0.8400 | c_signature_fail, cell_commit_fail | C->X:3, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_72` | `logic_skill_trm` | 0.8800 | c_signature_fail, cell_commit_fail | C->X:2, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_73` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_73` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_73` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_74` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_74` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_74` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_74` | `logic_skill_trm` | 0.9000 | c_signature_fail, cell_commit_fail | C->X:1, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_75` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_75` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_75` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:3 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_76` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_76` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_76` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_77` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_77` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_77` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_78` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_78` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_78` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_78` | `logic_skill_trm` | 0.9200 | c_signature_fail, cell_commit_fail | C->X:1, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_79` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_79` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_79` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:4 | 0.8000 | 0.8000 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_80` | `vanilla` | 0.9333 | c_signature_fail, cell_commit_fail | C->X:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_80` | `generic_skill` | 0.8667 | c_signature_fail, cell_commit_fail | C->X:2 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_80` | `logic_skill` | 0.9333 | c_signature_fail, cell_commit_fail | C->X:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_80` | `logic_skill_trm` | 0.8667 | c_signature_fail, cell_commit_fail | C->X:1, X->C:1 | 1.0000 | 1.0000 | - | - |
| `intellect_3_logic_81` | `vanilla` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_81` | `generic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
| `intellect_3_logic_81` | `logic_skill` | 0.8000 | c_signature_fail, cell_commit_fail | C->X:5 | 0.8400 | 0.8400 | cell_commit_fail | C->X:2, X->C:2 |
