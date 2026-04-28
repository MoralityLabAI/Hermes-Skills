# Addendum: Multi-Env MeTTa/TRM Methodology Lift Matrix

Status: draft addendum  
Date: April 28, 2026

## Thesis

The C-signature verifier result generalizes as a methodology, not as a single-env trick. The reusable move is to convert each repair attempt into a before/after verifier-state row, then compare:

- naive commit behavior,
- pre-repair scalar hints,
- env-specific symbolic checks,
- exact-only post-repair verification,
- post-repair multi-signal commit targets.

Artifact: [methodology_lift.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\metta_trm_methodology_lift_matrix\methodology_lift.results.md>).

## Scope

Rows: `148` deterministic no-model rows.

Sources:

- `122` C-signature commit rows,
- `20` symbolic closure threshold rows,
- `6` local 3B scale-transfer repair rows.

Covered envs:

- `intellect3_logic_c_signature`
- `tool_contract_router`
- `choice_contract`
- `ascii_tree_deep`
- `intellect3_camp_gate`
- `math_answer_search`
- `pydantic_hard_schema`
- `ifeval_contract_subset`
- `safety_abstain_router`

## Overall Result

| Policy | Rows | Accuracy | False commit | False reject | Expected committed delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `naive_commit_all` | `148` | `0.7838` | `1.0000` | `0.0000` | `19.6350` |
| `pre_reward_ge_0p8` | `148` | `0.6351` | `0.4688` | `0.3362` | `6.9767` |
| `post_symbolic_adapter` | `148` | `0.8581` | `0.6562` | `0.0000` | `19.6350` |
| `post_exact_only` | `148` | `0.8649` | `0.0000` | `0.1724` | `18.6233` |
| `post_multi_signal` | `148` | `1.0000` | `0.0000` | `0.0000` | `20.2950` |

## Read

The strongest generalization is not "symbolic checks always solve it." They do not. `post_symbolic_adapter` still false-commits C-signature no-gain repairs because those repaired candidates pass signatures. The stronger methodology is multi-signal post-repair state: exactness, reward delta, and env-specific structural checks.

`post_exact_only` is safe but too conservative; it drops partial repair improvements. That matters because a repair curriculum should not throw away useful non-exact improvements when training verifier and commit/veto TRMs.

Math remains the boundary condition. `math_answer_search` has `0.0000` average reward lift and `0` exact-count lift in the threshold suite. The commit/veto target can reject non-improving proposals, but MeTTa/TRM control logic still needs an exact candidate, solver, or stronger numeric invariant to create capability there.

## Claim Boundary

This is a separability and methodology artifact. It does not claim trained TRM-weight performance. The next publishable step is to train compact verifier/commit TRMs on these multi-env rows under the capped HRM/TRM wrapper, then report whether the learned gate holds on held-out rows without using evaluator labels at inference time.
