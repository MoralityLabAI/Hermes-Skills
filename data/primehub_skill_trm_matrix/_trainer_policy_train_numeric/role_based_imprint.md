# Primehub Role-Based TRM Imprint

- Keep hard reasoning and guarded safety roles critic-first until their exact-positive banks grow: hard_reasoning_numeric.

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
