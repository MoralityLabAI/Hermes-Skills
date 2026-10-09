;; Campsite near-miss curriculum package.
;; Declares what a curriculum row carries. src/metta_schema.py compiles the feature atoms, in the
;; order written here, into the typed state vector; an atom the compiler does not know is an error.
;; One top-level atom per line, as in the other Hermes-Skills MeTTa packages.

(curriculum-env campsite intellect3_camp_gate_micro_env)
(stage-order parse verify repair verify commit)

;; Verifier atoms: the official verifier's public gates (no gold grid is read).
(verifier-atom syntax_valid bool)
(verifier-atom shape_match bool)
(verifier-atom trees_unchanged bool)
(verifier-atom row_counts_match bool)
(verifier-atom col_counts_match bool)
(verifier-atom no_tent_touching bool)
(verifier-atom perfect_tree_matching bool)

;; Count atoms: how far the candidate is from each public constraint.
(count-atom rows_off fraction)
(count-atom cols_off fraction)
(count-atom tent_surplus signed3)
(count-atom moved_trees fraction)
(count-atom touching_pairs scaled3)
(count-atom unmatched_tents fraction)
(count-atom failed_gates fraction)

;; Shape atoms.
(shape-atom grid_rows scaled6)
(shape-atom grid_cols scaled6)

;; Repair operators (Hermes-Skills intellect3-logic projections) and their preconditions.
(repair-operator c_repair MIN_EDIT_PROJECT_C_SIGNATURE_PRESERVE_T (requires shape_match))
(repair-operator dual_repair MIN_EDIT_PROJECT_T_AND_C_SIGNATURES (requires shape_match))

;; Action menu, in the order the curriculum label uses (cheapest first).
(action-menu commit c_repair dual_repair reject)

;; Bucket rules for a row.
(bucket exact_positive (passes candidate))
(bucket repair_success (passes (first-passing-operator candidate)))
(bucket partial_improvement (lowers failed_gates (some-operator candidate)))
(bucket no_gain otherwise)

;; Commit rule after repair: the verifier owns it.
(commit-rule (passes (operator-output candidate)))
