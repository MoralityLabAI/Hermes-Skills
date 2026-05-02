# Repair Rudder Scale Comparison: 3B, 9B, 27B

Date: 2026-05-02

This table compares matched repair-rudder arms over the 88-row non-train
Pure-TRM split where available. The 3B row comes from the local Qwen2.5-3B Q4
run recorded in
`research/generated/paper_drafts/2026-04-28-local-3b-metta-action-space-rudder-addendum.md`.
The 9B and 27B rows come from the snacksack CUDA runs recorded in this artifact
folder.

| model | arm | n | target action | repair action | joint | JSON parse |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 3B | `raw_3b_rudder` | 88 | 0.7159 | 0.4091 | 0.3636 | 1.0000 |
| 3B | `repair_training_rudder` | 88 | 0.7955 | 0.3409 | 0.3182 | 1.0000 |
| 3B | `metta_action_space_rudder` | 88 | 0.7500 | 1.0000 | 0.7500 | 1.0000 |
| 3B | `metta_static_gate_rudder` | 88 | 0.9545 | 1.0000 | 0.9545 | 1.0000 |
| 9B | `raw_3b_rudder` | 88 | 0.7273 | 0.4091 | 0.3636 | 1.0000 |
| 9B | `repair_training_rudder` | 88 | 0.9659 | 0.7955 | 0.7955 | 1.0000 |
| 9B | `metta_action_space_rudder` | 88 | 0.7500 | 1.0000 | 0.7500 | 1.0000 |
| 9B | `metta_static_gate_rudder` | 88 | 0.9545 | 1.0000 | 0.9545 | 1.0000 |
| 27B | `raw_3b_rudder` | 88 | 0.7614 | 0.5341 | 0.4886 | 1.0000 |
| 27B | `repair_training_rudder` | 88 | 0.9318 | 0.7955 | 0.7955 | 1.0000 |
| 27B | `metta_action_space_rudder` | 88 | 0.8068 | 1.0000 | 0.8068 | 1.0000 |
| 27B | `metta_static_gate_rudder` | 88 | 0.9432 | 1.0000 | 0.9432 | 1.0000 |

## Interpretation

The scale effect is not monotonic across every arm. The raw model-rudder improves
from 3B/9B to 27B, but the strongest lift still comes from the control-plane
structure:

- 9B repair-training context improves joint accuracy from 0.3636 to 0.7955.
- 27B repair-training context improves joint accuracy from 0.4886 to 0.7955.
- MeTTa static gating reaches roughly 0.95 joint accuracy at all three scales.

This supports the paper's compactification claim: for typed near-miss repair
decisions, symbolic control-plane structure and curated repair signals can
dominate raw LLM scale over this benchmark slice.
