; Multi-env MeTTa/TRM methodology-lift contract sketch.
; These rules define commit/veto training targets from post-repair state.

(= (positive-repair-delta $state)
   (> (reward-delta $state) 0.0))

(= (post-multi-signal-commit $state)
   (if (or (after-exact $state) (positive-repair-delta $state))
       commit
       reject_or_abstain))

(= (post-symbolic-commit $state)
   (if (env-symbolic-pass $state)
       commit
       reject_or_abstain))

(= (env-symbolic-pass $state)
   (match (env-family $state)
     (intellect3_logic_c_signature (and (after-t-signature-pass $state) (after-c-signature-pass $state)))
     (tool_contract_router (has-valid-tool-and-required-arguments $state))
     (choice_contract (has-allowed-choice-label $state))
     (ascii_tree_deep (node-set-complete $state))
     (intellect3_camp_gate (signature-projection-matched $state))
     (math_answer_search (exact-candidate-present $state))
     (_ False)))
