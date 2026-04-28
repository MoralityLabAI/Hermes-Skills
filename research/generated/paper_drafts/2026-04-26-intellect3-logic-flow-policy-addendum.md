# Addendum: Intellect-3 Logic Flow Policy Sweep

Status: draft addendum  
Date: April 26, 2026

## Thesis

The next Intellect-3 logic improvement should focus on a narrow MeTTa/TRM camp-placement repair gate, not a broad multi-arm ensemble. A deterministic replay over existing 27B Intellect-3 logic receipts shows that the current `logic_skill_trm` candidate plus C-signature repair is the best observed flow policy.

## Result

The replay artifact is [intellect3_logic_flow_policy_sweep.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\intellect3_logic_flow_policy_sweep\intellect3_logic_flow_policy_sweep.results.md>).

| Policy | Exact | Cell accuracy | Read |
| --- | ---: | ---: | --- |
| `logic_trm_original` | `0.3028` | `0.8787` | Current single-arm TRM baseline. |
| `logic_trm_c_repair_if_c_fail` | `0.6789` | `0.9340` | Best replay policy; repair only when C signature fails. |
| `logic_trm_dual_repair_if_any_sig_fail` | `0.6697` | `0.9318` | Slightly worse than C-only repair. |
| `multi_arm_min_edit_c_repair` | `0.6605` | `0.9318` | Candidate diversity did not beat the single TRM arm. |
| `signature_first_then_dual` | `0.6605` | `0.9299` | Multi-arm signature-first policy underperformed C-only repair. |

Evidence class: `post_hoc_projection`.

## Training Implication

The sweep emits Pure-TRM-style rows at [pure_trm_flow_policy_rows.jsonl](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\intellect3_logic_flow_policy_sweep\pure_trm_flow_policy_rows.jsonl>). The useful row types are:

- `signature_fail`
- `signature_pass_cell_fail`
- `commit_success`

These rows are better suited for a hard-reasoning-logic verifier/repairer than for a generic solver. The training target should be: detect C-signature failure, apply bounded repair, and reject over-broad dual projection unless it has stronger evidence.

## Next Live Eval

When Snacksack returns, the live benchmark should test:

`logic_skill_trm -> C-signature validate -> C-only min-edit repair if needed -> commit`

Do not spend extra calls on multi-arm candidate diversity first; the replay suggests the highest-return change is the narrow repair gate on the existing TRM arm.
