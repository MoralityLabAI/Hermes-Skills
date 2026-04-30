# Primehub Role-Based TRM Imprint

- Role split: action-bearing TRM support currently lives mainly in internal_action.

## internal_action
- role_name: latent_action_retriever
- support_tier: narrow_action_support
- goal: recover exact hidden-action tokens such as inspect_and_continue
- rows: 2
- exact_positive_rows: 2
- target_action_coverage: 1.0000
- trainer_policy: exact_positive_weight=3.00, weak_positive_weight=1.50, negative_weight=0.20, min_supervision_weight=0.85, top_k=1, routing_strength=focused
- skill_prompt_lines:
  - This TRM role is a narrow latent-action specialist: when the contract implies deferred internal continuation, emit only `inspect_and_continue` and no visible draft.
  - Do not generalize this support into normal visible-answer tasks; it is a tiny but clean exact-token niche.
- trainer_lines:
  - Add more hidden-action environments before widening this role; the current signal is clean but too narrow to claim generality.
