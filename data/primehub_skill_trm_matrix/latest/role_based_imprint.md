# Primehub Role-Based TRM Imprint

- Role split: action-bearing TRM support currently lives mainly in internal_action, choice_contract, structured_map.
- Keep hard reasoning and guarded safety roles critic-first until their exact-positive banks grow: abstain_guard, hard_reasoning_numeric, hard_reasoning_logic.

## abstain_guard
- role_name: guarded_critic
- support_tier: critic_guard
- goal: separate true negatives from high-confidence guarded overrides
- rows: 17
- exact_positive_rows: 2
- target_action_coverage: 0.1176
- critic_bucket_accuracy: 1.0000
- retriever_exact_match_rate: 0.0000
- route_abstain_rate: 1.0000
- trainer_policy: exact_positive_weight=3.00, near_miss_weight=1.15, weak_positive_weight=0.75, negative_weight=0.25, min_supervision_weight=0.25, top_k=3, routing_strength=guarded
- signal_weights: contract_family_match=0.70, contract_validity=1.00, critic_verdict_agreement=1.55, failure_localization=1.20, profile_selection_correctness=0.65, repair_success=0.90, retrieval_selection_correctness=0.65, task_success=0.95, transport_no_fallback=0.60, transport_visible_output=0.60
- skill_prompt_lines:
  - This TRM role is critic-first and abstention-heavy: default conservative and require explicit contract evidence before any override.
  - Use retrieved support as a veto signal, not as permission to comply; if exact verification fails, keep the abstention path.
- trainer_lines:
  - Preserve a hard critic gate for this role; do not relax abstention defaults until the override bank grows beyond a couple of exact positives.

## choice_contract
- role_name: contract_formatter
- support_tier: action_support
- goal: repair exact small-answer wrappers without changing semantics
- rows: 81
- exact_positive_rows: 35
- target_action_coverage: 0.4321
- critic_bucket_accuracy: 0.3077
- retriever_exact_match_rate: 0.0000
- route_abstain_rate: 0.3077
- trainer_policy: exact_positive_weight=2.25, near_miss_weight=1.50, weak_positive_weight=1.25, negative_weight=0.20, min_supervision_weight=0.45, top_k=5, routing_strength=moderate
- signal_weights: contract_family_match=1.10, contract_validity=1.45, critic_verdict_agreement=1.00, failure_localization=1.00, profile_selection_correctness=1.25, repair_success=1.25, retrieval_selection_correctness=1.25, task_success=1.30, transport_no_fallback=0.75, transport_visible_output=0.75
- skill_prompt_lines:
  - This TRM role is strongest as a contract formatter: recover semantics first, then use support to repair wrappers, choice tokens, and exact answer shells.
  - Treat retrieved support as a formatting prior, not as authority on semantics; if the solved answer conflicts with the template, keep the answer and repair only the wrapper.
- trainer_lines:
  - Invest additional collection into answer-wrapper and exact token repair; this is the only broad cluster with meaningful action-bearing coverage.
  - Keep semantics-vs-format labels separate so the formatter role can improve without pretending to solve the task from scratch.

## hard_reasoning_logic
- role_name: critic_verify_logic
- support_tier: critic_verify_sparse
- goal: improve branch elimination and exact answer emission on logic-heavy envs
- rows: 20
- exact_positive_rows: 3
- target_action_coverage: 0.1500
- critic_bucket_accuracy: 0.5714
- retriever_exact_match_rate: 0.0000
- route_abstain_rate: 0.5714
- trainer_policy: exact_positive_weight=2.75, near_miss_weight=1.80, weak_positive_weight=1.00, negative_weight=0.20, min_supervision_weight=0.60, top_k=2, routing_strength=conservative
- signal_weights: contract_family_match=0.85, contract_validity=1.15, critic_verdict_agreement=1.30, failure_localization=1.15, profile_selection_correctness=0.80, repair_success=1.00, retrieval_selection_correctness=0.80, task_success=1.00, transport_no_fallback=0.60, transport_visible_output=0.60
- skill_prompt_lines:
  - This TRM role is a branch eliminator and verifier: use it to rule out unsupported candidates and confirm the surviving answer, not to improvise a new reasoning trace.
  - Current support is critic-weighted rather than retrieval-weighted, so stay on the base reasoning path unless the candidate set is already narrow.
- trainer_lines:
  - Collect more exact-positive rows before treating this role as retrieval-capable; right now it is primarily a verifier/control-plane specialist.
  - Keep routing conservative and prefer better row quality over more aggressive router behavior.

## hard_reasoning_numeric
- role_name: critic_verify_numeric
- support_tier: critic_verify_sparse
- goal: improve exact numeric recovery and verification on hard reasoning envs
- rows: 35
- exact_positive_rows: 3
- target_action_coverage: 0.0857
- critic_bucket_accuracy: 0.6000
- retriever_exact_match_rate: 0.0000
- route_abstain_rate: 0.6000
- trainer_policy: exact_positive_weight=3.00, near_miss_weight=1.80, weak_positive_weight=1.00, negative_weight=0.20, min_supervision_weight=0.60, top_k=2, routing_strength=conservative
- signal_weights: contract_family_match=0.85, contract_validity=1.15, critic_verdict_agreement=1.30, failure_localization=1.15, profile_selection_correctness=0.80, repair_success=1.00, retrieval_selection_correctness=0.80, task_success=1.00, transport_no_fallback=0.60, transport_visible_output=0.60
- skill_prompt_lines:
  - This TRM role is a numeric verifier, not a generic solver: solve locally, then use TRM to catch arithmetic drift, sign errors, and invalid final forms.
  - Do not lean on retrieval-led derivations here; current support is too sparse, so use TRM mainly to veto contradictions or confirm the final exact value.
- trainer_lines:
  - Collect more exact-positive rows before treating this role as retrieval-capable; right now it is primarily a verifier/control-plane specialist.
  - Keep routing conservative and prefer better row quality over more aggressive router behavior.

## internal_action
- role_name: latent_action_retriever
- support_tier: narrow_action_support
- goal: recover exact hidden-action tokens such as inspect_and_continue
- rows: 2
- exact_positive_rows: 2
- target_action_coverage: 1.0000
- critic_bucket_accuracy: 1.0000
- retriever_exact_match_rate: 0.0000
- route_abstain_rate: 0.0000
- trainer_policy: exact_positive_weight=3.00, near_miss_weight=2.00, weak_positive_weight=1.50, negative_weight=0.20, min_supervision_weight=0.85, top_k=1, routing_strength=focused
- signal_weights: contract_family_match=1.20, contract_validity=1.40, critic_verdict_agreement=1.00, failure_localization=1.00, profile_selection_correctness=1.60, repair_success=1.25, retrieval_selection_correctness=1.70, task_success=1.40, transport_no_fallback=0.85, transport_visible_output=0.85
- skill_prompt_lines:
  - This TRM role is a narrow latent-action specialist: when the contract implies deferred internal continuation, emit only `inspect_and_continue` and no visible draft.
  - Do not generalize this support into normal visible-answer tasks; it is a tiny but clean exact-token niche.
- trainer_lines:
  - Add more hidden-action environments before widening this role; the current signal is clean but too narrow to claim generality.

## structured_map
- role_name: schema_formatter
- support_tier: format_support
- goal: preserve strict line schemas and structured answer maps
- rows: 16
- exact_positive_rows: 4
- target_action_coverage: 0.2500
- critic_bucket_accuracy: 0.0000
- retriever_exact_match_rate: 0.0000
- route_abstain_rate: 0.0000
- trainer_policy: exact_positive_weight=2.20, near_miss_weight=1.75, weak_positive_weight=1.00, negative_weight=0.15, min_supervision_weight=0.35, top_k=4, routing_strength=moderate
- signal_weights: contract_family_match=1.25, contract_validity=1.50, critic_verdict_agreement=1.00, failure_localization=1.10, profile_selection_correctness=1.35, repair_success=1.55, retrieval_selection_correctness=1.35, task_success=1.15, transport_no_fallback=0.80, transport_visible_output=0.80
- skill_prompt_lines:
  - This TRM role is formatter-friendly: use it to preserve strict line shape, field order, and schema compliance, then reject malformed structure before final output.
  - When structure and semantics disagree, prioritize structurally valid output that still preserves the intended answer content.
- trainer_lines:
  - Grow schema-preserving rows and malformed-output negatives together; the useful gain here is structural reliability, not open-ended reasoning.
