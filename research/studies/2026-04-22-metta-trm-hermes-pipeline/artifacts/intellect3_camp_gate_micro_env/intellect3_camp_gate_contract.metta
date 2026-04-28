;; Intellect-3 Campsite camp-gate micro-env contract.
;; The LLM/TRM proposes a grid; MeTTa gates score and repair the proposal.

(: env_id Symbol)
(= env_id intellect3_camp_gate_micro_env)

(: symbols (List Symbol))
(= symbols (T C X))

(: stage_order (List Symbol))
(= stage_order (parse candidate verify_c_signature verify_t_signature repair commit))

(: metric_exact_match Symbol)
(= metric_exact_match grid_exact_match)
(: metric_cell_accuracy Symbol)
(= metric_cell_accuracy grid_cell_accuracy)
(: metric_c_signature_pass Symbol)
(= metric_c_signature_pass row_col_c_signature_pass)
(: metric_t_signature_pass Symbol)
(= metric_t_signature_pass row_col_t_signature_pass)

(: gate_parse Symbol)
(= gate_parse TRM_PARSE_GRID)
(: gate_c_signature Symbol)
(= gate_c_signature TRM_CAMP_ROW_COL_SIGNATURE)
(: gate_dual_signature Symbol)
(= gate_dual_signature TRM_TENT_CAMP_ROW_COL_SIGNATURE)
(: gate_commit Symbol)
(= gate_commit TRM_COMMIT_GRID)

(: repair_c_only Symbol)
(= repair_c_only MIN_EDIT_PROJECT_C_SIGNATURE_PRESERVE_T)
(: repair_dual Symbol)
(= repair_dual MIN_EDIT_PROJECT_T_AND_C_SIGNATURES)

(: failure_taxonomy (List Symbol))
(= failure_taxonomy (candidate_parse_failure shape_mismatch t_signature_fail c_signature_fail cell_commit_fail))
