;; Intellect-3 math answer-manifold micro-env contract.
(= env_id intellect3_math_answer_manifold_micro_env)
(= stage_order (parse_answer classify_numeric_error route_select repair_or_commit))
(= metric_exact_match answer_exact_match)
(= metric_relative_distance abs_error_div_max_abs_expected)
(= gate_parse TRM_PARSE_INTEGER_ANSWER)
(= gate_error_taxonomy TRM_NUMERIC_ERROR_ARCHETYPE)
(= gate_route TRM_ROUTE_MATH_REPAIR)
(= failure_taxonomy (prediction_parse_failure off_by_one off_by_small double half negation sign_error_abs_match same_last_digit same_digit_multiset order_of_magnitude wrong_integer non_integer_wrapper))
