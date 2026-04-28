; C-signature post-repair verifier sketch.
; This is an evaluator-backed training target, not a prompt-only LLM result.

(= (signature-complete $state)
   (and (after-t-signature-pass $state) (after-c-signature-pass $state)))

(= (positive-repair-delta $state)
   (> (reward-delta $state) 0.0))

(= (c-signature-commit-action $state)
   (if (or (after-exact $state) (positive-repair-delta $state))
       commit
       reject_or_abstain))

(= (c-signature-training-signals $state)
   (list (after-exact $state)
         (signature-complete $state)
         (reward-delta $state)
         (c-signature-commit-action $state)))
