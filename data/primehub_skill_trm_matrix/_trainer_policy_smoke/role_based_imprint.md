# Primehub Role-Based TRM Imprint

- Role split: action-bearing TRM support currently lives mainly in internal_action, choice_contract.
- Keep hard reasoning and guarded safety roles critic-first until their exact-positive banks grow: abstain_guard, hard_reasoning_numeric.

## hard_reasoning_numeric
- role_name: critic_verify_numeric
- support_tier: critic_verify_sparse
- goal: improve exact numeric recovery and verification on hard reasoning envs
- rows: 35
- exact_positive_rows: 3
- target_action_coverage: 0.0857
- trainer_policy: exact_positive_weight=3.00, weak_positive_weight=1.00, negative_weight=0.20, min_supervision_weight=0.60, top_k=2, routing_strength=conservative
- skill_prompt_lines:
  - This TRM role is a numeric verifier, not a generic solver: solve locally, then use TRM to catch arithmetic drift, sign errors, and invalid final forms.
  - Do not lean on retrieval-led derivations here; current support is too sparse, so use TRM mainly to veto contradictions or confirm the final exact value.
- trainer_lines:
  - Collect more exact-positive rows before treating this role as retrieval-capable; right now it is primarily a verifier/control-plane specialist.
  - Keep routing conservative and prefer better row quality over more aggressive router behavior.

## choice_contract
- role_name: contract_formatter
- support_tier: action_support
- goal: repair exact small-answer wrappers without changing semantics
- rows: 48
- exact_positive_rows: 15
- target_action_coverage: 0.3125
- trainer_policy: exact_positive_weight=2.25, weak_positive_weight=1.25, negative_weight=0.20, min_supervision_weight=0.45, top_k=5, routing_strength=moderate
- skill_prompt_lines:
  - This TRM role is strongest as a contract formatter: recover semantics first, then use support to repair wrappers, choice tokens, and exact answer shells.
  - Treat retrieved support as a formatting prior, not as authority on semantics; if the solved answer conflicts with the template, keep the answer and repair only the wrapper.
- trainer_lines:
  - Invest additional collection into answer-wrapper and exact token repair; this is the only broad cluster with meaningful action-bearing coverage.
  - Keep semantics-vs-format labels separate so the formatter role can improve without pretending to solve the task from scratch.

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

## abstain_guard
- role_name: guarded_critic
- support_tier: critic_verify_sparse
- goal: separate true negatives from high-confidence guarded overrides
- rows: 21
- exact_positive_rows: 2
- target_action_coverage: 0.0952
- trainer_policy: exact_positive_weight=3.00, weak_positive_weight=1.00, negative_weight=0.25, min_supervision_weight=0.60, top_k=2, routing_strength=guarded
- skill_prompt_lines:
  - This TRM role is critic-first and abstention-heavy: default conservative and require explicit contract evidence before any override.
- trainer_lines:
  - Preserve a hard critic gate for this role; do not relax abstention defaults until the override bank grows beyond a couple of exact positives.
