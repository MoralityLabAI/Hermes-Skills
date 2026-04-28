# Intellect-3 Logic Flow Policy Sweep

Source: `C:\projects\trm_observability_harness\data\qwen27b_intellect3_logic_hybrid_200\predictions.jsonl`
Generated: `2026-04-26T15:51:16.166715+00:00`

This replay tests commit policies over existing candidate arms. It measures whether MeTTa/TRM flow control should commit original grids, C-only projections, dual-signature projections, or abstain.

Evidence class: `post_hoc_projection`.

## Policy Summary

| Policy | Selection | Exact | Cell Acc | T Sig | C Sig | Transforms | Source Arms |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `logic_trm_c_repair_if_c_fail` | 1.0000 | 0.6789 | 0.9340 | 1.0000 | 1.0000 | `c_repair`:61, `original`:48 | `logic_skill_trm`:109 |
| `logic_trm_dual_repair_if_any_sig_fail` | 1.0000 | 0.6697 | 0.9318 | 1.0000 | 1.0000 | `dual_repair`:61, `original`:48 | `logic_skill_trm`:109 |
| `multi_arm_min_edit_c_repair` | 1.0000 | 0.6605 | 0.9318 | 0.9908 | 1.0000 | `c_repair`:109 | `logic_skill_trm`:96, `logic_skill`:9, `generic_skill`:4 |
| `multi_arm_min_edit_dual_repair` | 1.0000 | 0.6605 | 0.9299 | 1.0000 | 1.0000 | `dual_repair`:109 | `logic_skill_trm`:96, `logic_skill`:9, `generic_skill`:4 |
| `signature_first_then_dual` | 1.0000 | 0.6605 | 0.9299 | 1.0000 | 1.0000 | `dual_repair`:60, `original`:49 | `logic_skill_trm`:96, `logic_skill`:9, `generic_skill`:4 |
| `multi_arm_original_signature_pass` | 0.4495 | 0.3119 | 0.4213 | 0.4495 | 0.4495 | `abstain`:60, `original`:49 | `logic_skill_trm`:48, `generic_skill`:1 |
| `logic_trm_original` | 1.0000 | 0.3028 | 0.8787 | 1.0000 | 0.4404 | `original`:109 | `logic_skill_trm`:109 |

## Read

- `logic_trm_original` is the current single-arm TRM baseline.
- `logic_trm_c_repair_if_c_fail` tests the narrow camp-placement repair gate.
- `logic_trm_dual_repair_if_any_sig_fail` tests the coupled tent/camp signature gate.
- `multi_arm_*` policies test whether parallel skill candidates can improve commit selection without another model call.
- If multi-arm policies win, the next live benchmark should spend extra calls on candidate diversity and let MeTTa/TRM own the commit gate.
