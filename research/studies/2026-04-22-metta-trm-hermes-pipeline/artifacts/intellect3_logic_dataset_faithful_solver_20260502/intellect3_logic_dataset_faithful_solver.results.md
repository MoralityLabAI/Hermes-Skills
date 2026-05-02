# Intellect-3 Logic Dataset-Faithful Solver Replay

Generated: `2026-05-02T22:04:46.046473+00:00`
Source: `C:\projects\Tesseract\Tesseract\data\normalized_trajectories\intellect_3_logic.jsonl`
Predictions: `C:\projects\trm_observability_harness\data\qwen27b_intellect3_logic_hybrid_200\predictions.jsonl`

## Result

| Arm | Exact | Exact Rate | Avg Cell Acc | Ambiguous Exact | Abstain | Evidence |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `public_unique_solver` | 92/109 | 0.8440 | 0.8440 | 0/17 | 17 | public/candidate no-target |
| `public_first_solver` | 96/109 | 0.8807 | 0.9764 | 4/17 | 0 | public/candidate no-target |
| `candidate_project_logic_skill` | 98/109 | 0.8991 | 0.9801 | 6/17 | 0 | public/candidate no-target |
| `candidate_project_logic_skill_trm` | 97/109 | 0.8899 | 0.9776 | 5/17 | 0 | public/candidate no-target |
| `candidate_project_generic_skill` | 96/109 | 0.8807 | 0.9764 | 4/17 | 0 | public/candidate no-target |
| `candidate_project_vanilla` | 96/109 | 0.8807 | 0.9764 | 4/17 | 0 | public/candidate no-target |
| `metta_unique_else_logic_skill_projection` | 98/109 | 0.8991 | 0.9801 | 6/17 | 0 | public/candidate no-target |
| `canonical_oracle_upper_bound` | 109/109 | 1.0000 | 1.0000 | 17/17 | 0 | target upper bound |

## Read

Dataset-faithful public constraints produce at least one valid solution for all rows. They uniquely determine 92/109 benchmark targets; 17 rows have multiple public-valid grids. Candidate-conditioned projection improves benchmark-canonical agreement but cannot fairly recover hidden canonical choices for every ambiguous row without an extra tie-break signal.

Public-valid solver closure: `109/109` rows have at least one valid grid under the dataset-faithful rule contract.

The important correction is semantic: the source benchmark solutions are valid under the stated camp-centric rule,
but usually invalid under the stricter tree-centric Campsite rule.  A MeTTa/TRM gate should therefore learn a
`rule_contract` state before applying a solver.

## Ambiguous Rows

`intellect_3_logic_19`, `intellect_3_logic_34`, `intellect_3_logic_40`, `intellect_3_logic_41`, `intellect_3_logic_44`, `intellect_3_logic_47`, `intellect_3_logic_52`, `intellect_3_logic_56`, `intellect_3_logic_68`, `intellect_3_logic_69`, `intellect_3_logic_73`, `intellect_3_logic_85`, `intellect_3_logic_86`, `intellect_3_logic_90`, `intellect_3_logic_91`, `intellect_3_logic_94`, `intellect_3_logic_107`

These rows are solved as logic puzzles but not uniquely benchmark-canonical from public constraints alone.
