; Camp-gate noisy constraint extraction graph.
; This contract is a readable MeTTa-style specification for the Python gates.

(= (camp-gate-router $prompt)
   (commit-json
     (dimension-gate $prompt)
     (anchor-gate $prompt)
     (row-quota-gate $prompt)
     (column-quota-gate $prompt)))

(= (dimension-gate $prompt) (script-parse height width))
(= (anchor-gate $prompt) (script-parse fixed_tents_1_indexed))
(= (row-quota-gate $prompt) (script-parse row_c_counts_top_to_bottom))
(= (column-quota-gate $prompt) (script-parse col_c_counts_left_to_right))
(= (solver-gate $packet) (public-constraint-solver $packet))

(claim-boundary target-grid-unused)
(claim-boundary prompt-visible-constraints-only)
(claim-boundary no-llm-solve-step)
