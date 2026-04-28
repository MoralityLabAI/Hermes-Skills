# Near-Miss Repair Curriculum

Generated: `2026-04-26T16:08:44.858285+00:00`

This curriculum collects semi-failed outputs where MeTTa/TRM repair, verifier, or commit gates can learn useful control behavior. It is a curation artifact, not a model-training result.

## Summary

- Rows: `244`
- Average positive delta per row: `0.0832`

## Buckets

| Bucket | Rows |
| --- | ---: |
| `repair_success` | 91 |
| `exact_positive` | 71 |
| `repair_failure_or_no_gain` | 62 |
| `partial_repair_improvement` | 20 |

## Roles

| TRM role | Rows | Bucket mix |
| --- | ---: | --- |
| `hard_reasoning_logic` | 222 | `exact_positive`:67, `partial_repair_improvement`:20, `repair_failure_or_no_gain`:53, `repair_success`:82 |
| `structured_map` | 10 | `exact_positive`:2, `repair_failure_or_no_gain`:4, `repair_success`:4 |
| `choice_contract` | 6 | `exact_positive`:1, `repair_failure_or_no_gain`:2, `repair_success`:3 |
| `hard_reasoning_numeric` | 4 | `exact_positive`:1, `repair_failure_or_no_gain`:3 |
| `abstain_guard` | 2 | `repair_success`:2 |

## Sources

| Source | Rows |
| --- | ---: |
| `intellect3_logic_flow_policy_sweep` | 218 |
| `symbolic_closure_threshold_suite` | 20 |
| `scale_transfer_probe_suite_qwen25_3b_q4km` | 6 |

## High-Value Rows

| Source | Role | Case | Bucket | Before | After | Delta | Failure | Repair |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| `scale_transfer_probe_suite_qwen25_3b_q4km` | `abstain_guard` | `battery_storage` | `repair_success` | 0.0000 | 1.0000 | 1.0000 | `json_value_mismatch` | `canonical_commit` |
| `scale_transfer_probe_suite_qwen25_3b_q4km` | `choice_contract` | `hashtags_exact_four` | `repair_success` | 0.0000 | 1.0000 | 1.0000 | `hashtag_contract_failure` | `['ifeval_contract_subset_canonical_commit']` |
| `scale_transfer_probe_suite_qwen25_3b_q4km` | `structured_map` | `library_policy_nested` | `repair_success` | 0.0000 | 1.0000 | 1.0000 | `json_parse_failure` | `canonical_commit` |
| `scale_transfer_probe_suite_qwen25_3b_q4km` | `choice_contract` | `two_bullets_five_words` | `repair_success` | 0.0000 | 1.0000 | 1.0000 | `bullet_word_count_failure` | `['ifeval_contract_subset_canonical_commit']` |
| `scale_transfer_probe_suite_qwen25_3b_q4km` | `abstain_guard` | `unknown_pills` | `repair_success` | 0.0000 | 1.0000 | 1.0000 | `json_value_mismatch` | `canonical_commit` |
| `symbolic_closure_threshold_suite` | `choice_contract` | `boxed_letter_extract:partial_semantic` | `repair_success` | 0.0000 | 1.0000 | 1.0000 | `mismatch` | `boxed_choice_extract` |
| `symbolic_closure_threshold_suite` | `structured_map` | `weather_sf_unit:partial_semantic` | `repair_success` | 0.0000 | 1.0000 | 1.0000 | `json_value_mismatch` | `intent_schema_arg_repair` |
| `scale_transfer_probe_suite_qwen25_3b_q4km` | `structured_map` | `package_tree_deep` | `repair_success` | 0.6000 | 1.0000 | 0.4000 | `partial_tree` | `['ascii_tree_deep_canonical_commit']` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_71:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.6667 | 1.0000 | 0.3333 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_71:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.6667 | 1.0000 | 0.3333 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_104:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.7000 | 1.0000 | 0.3000 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_104:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.7000 | 1.0000 | 0.3000 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_16:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.7000 | 1.0000 | 0.3000 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_16:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.7000 | 1.0000 | 0.3000 | `c_signature_fail` | `dual_repair` |
| `symbolic_closure_threshold_suite` | `structured_map` | `package_tree_from_nodes:partial_semantic` | `repair_success` | 0.7000 | 1.0000 | 0.3000 | `partial_tree` | `node_list_to_canonical_tree` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_102:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.7500 | 1.0000 | 0.2500 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_102:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.7500 | 1.0000 | 0.2500 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_51:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.7500 | 1.0000 | 0.2500 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_51:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.7500 | 1.0000 | 0.2500 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_54:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.7500 | 1.0000 | 0.2500 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_54:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.7500 | 1.0000 | 0.2500 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_37:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8000 | 1.0000 | 0.2000 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_37:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8000 | 1.0000 | 0.2000 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_97:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8000 | 1.0000 | 0.2000 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_97:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8000 | 1.0000 | 0.2000 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_99:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8000 | 1.0000 | 0.2000 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_99:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8000 | 1.0000 | 0.2000 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_65:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8125 | 1.0000 | 0.1875 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_65:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8125 | 1.0000 | 0.1875 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_45:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8400 | 1.0000 | 0.1600 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_106:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8500 | 1.0000 | 0.1500 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_106:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8500 | 1.0000 | 0.1500 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_20:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8500 | 1.0000 | 0.1500 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_20:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8500 | 1.0000 | 0.1500 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_48:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8500 | 1.0000 | 0.1500 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_48:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8500 | 1.0000 | 0.1500 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_83:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8500 | 1.0000 | 0.1500 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_83:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8500 | 1.0000 | 0.1500 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_9:logic_trm_c_repair_if_c_fail` | `partial_repair_improvement` | 0.6500 | 0.8000 | 0.1500 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_9:logic_trm_dual_repair_if_any_sig_fail` | `partial_repair_improvement` | 0.6500 | 0.8000 | 0.1500 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_29:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8667 | 1.0000 | 0.1333 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_29:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8667 | 1.0000 | 0.1333 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_56:logic_trm_c_repair_if_c_fail` | `partial_repair_improvement` | 0.6000 | 0.7333 | 0.1333 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_56:logic_trm_dual_repair_if_any_sig_fail` | `partial_repair_improvement` | 0.6000 | 0.7333 | 0.1333 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_80:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8667 | 1.0000 | 0.1333 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_80:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8667 | 1.0000 | 0.1333 | `c_signature_fail` | `dual_repair` |
| `symbolic_closure_threshold_suite` | `hard_reasoning_logic` | `row_signature_projection:partial_semantic` | `repair_success` | 0.8750 | 1.0000 | 0.1250 | `partial_grid` | `camp_signature_min_edit_projection` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_11:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8800 | 1.0000 | 0.1200 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_11:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8800 | 1.0000 | 0.1200 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_18:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8800 | 1.0000 | 0.1200 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_18:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8800 | 1.0000 | 0.1200 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_36:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8800 | 1.0000 | 0.1200 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_36:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8800 | 1.0000 | 0.1200 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_59:logic_trm_c_repair_if_c_fail` | `partial_repair_improvement` | 0.7200 | 0.8400 | 0.1200 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_59:logic_trm_dual_repair_if_any_sig_fail` | `partial_repair_improvement` | 0.7200 | 0.8400 | 0.1200 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_5:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8800 | 1.0000 | 0.1200 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_5:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8800 | 1.0000 | 0.1200 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_72:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8800 | 1.0000 | 0.1200 | `c_signature_fail` | `c_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_72:logic_trm_dual_repair_if_any_sig_fail` | `repair_success` | 0.8800 | 1.0000 | 0.1200 | `c_signature_fail` | `dual_repair` |
| `intellect3_logic_flow_policy_sweep` | `hard_reasoning_logic` | `intellect_3_logic_96:logic_trm_c_repair_if_c_fail` | `repair_success` | 0.8800 | 1.0000 | 0.1200 | `c_signature_fail` | `c_repair` |

## Methodology Use

- Train repair/verifier TRMs on `repair_success` and `partial_repair_improvement` rows.
- Keep `repair_failure_or_no_gain` rows as hard negatives for commit/veto TRMs.
- Do not merge `hard_reasoning_numeric` rows into solver training unless teacher candidates or invariants exist.
- Evaluate by held-out failure family, not just held-out examples.
