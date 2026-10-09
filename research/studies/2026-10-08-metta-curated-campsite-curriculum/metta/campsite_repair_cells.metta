;; Campsite repair-cell package: what a repair TRM's training rows carry per cell.
;; src/repair_cells.py compiles the cell atoms, in the order written here, into input channels; an atom the
;; code does not compute is an error. One top-level atom per line.

(repair-env campsite intellect3_camp_gate_micro_env)
(grid-pad 6 6)

;; Raw cell channels (shared by every framing).
(raw-channel cand_tree bool)
(raw-channel cand_empty bool)
(raw-channel cand_tent bool)
(raw-channel cand_missing bool)
(raw-channel puzzle_tree bool)
(raw-channel valid_cell bool)
(raw-channel row_target scaled3)
(raw-channel col_target scaled3)

;; Cell atoms: each public Campsite rule localised to the cell it constrains.
(cell-atom eligible bool)
(cell-atom row_deficit signed3)
(cell-atom col_deficit signed3)
(cell-atom row_slack signed3)
(cell-atom col_slack signed3)
(cell-atom touching_tent bool)
(cell-atom unmatched_tent bool)
(cell-atom tree_mismatch bool)

;; Rule symmetries: transformations that map valid solutions to valid solutions.
(symmetry flip_rows)
(symmetry flip_cols)
(symmetry flip_both)
(symmetry transpose)

;; Output and decoding.
(output-target nearest_valid_solution)
(decode tent_if_logit_positive copy_trees_from_puzzle)
