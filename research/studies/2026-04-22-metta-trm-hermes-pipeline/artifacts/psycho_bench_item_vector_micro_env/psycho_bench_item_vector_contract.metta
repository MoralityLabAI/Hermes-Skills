;; PsychoBench item-vector micro-env contract.
(= env_id psycho_bench_item_vector_micro_env)
(= stage_order (parse_items validate_contract score_vector project_subscales compare_delta))
(= metric_reward_delta psycho_reward_delta)
(= metric_format_pass all_expected_items_once_scores_1_to_5)
(= gate_item_contract TRM_LIKERT_ITEM_VECTOR_CONTRACT)
(= gate_subscale_projection TRM_BFI_SUBSCALE_PROJECTOR)
(= failure_taxonomy (missing_item extra_item duplicate_item out_of_range_score format_wrapper_failure latent_profile_shift))
