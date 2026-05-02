;; 27B-drafted MeTTa self-improvement contract for Intellect-3-Math.
(= env_id intellect3_math_metta_self_improve_27b)
(= skill_name "Intellect-3-Math-Auditor")
(= (metta_rule 1) "(rule math-audit-magnitude (if (and (is-problem-type ?p small-scale) (> ?answer 1000)) (reject-answer ?answer)))")
(= (metta_rule 2) "(rule math-audit-consistency (if (not (satisfies-constraints ?problem ?answer)) (reject-answer ?answer)))")
(= (metta_rule 3) "(rule math-route-decision (if (contains-keyword ?prompt \"find a+b+c\") (use-strict-integer-mode)))")
(= (heldout_exact baseline) 0/10)
(= (heldout_exact current_skill) 3/10)
(= (heldout_exact metta_self_improved) 2/10)
