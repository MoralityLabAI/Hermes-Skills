# MeTTa/TRM Methodology Lift Matrix

Generated: `2026-04-28T14:03:53.294480+00:00`

This deterministic matrix generalizes the C-signature finding across multiple Hermes/Prime-style envs. It compares naive commit behavior, pre-repair scalar hints, env-specific symbolic checks, exact-only verification, and post-repair multi-signal commit targets.

No model calls and no TRM training were run for this artifact.

## Overall Policy Summary

| Policy | Rows | Accuracy | False commit rate | False reject rate | Expected committed delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `naive_commit_all` | 148 | 0.7838 | 1.0000 | 0.0000 | 19.6350 |
| `pre_reward_ge_0p8` | 148 | 0.6351 | 0.4688 | 0.3362 | 6.9767 |
| `post_symbolic_adapter` | 148 | 0.8581 | 0.6562 | 0.0000 | 19.6350 |
| `post_exact_only` | 148 | 0.8649 | 0.0000 | 0.1724 | 18.6233 |
| `post_multi_signal` | 148 | 1.0000 | 0.0000 | 0.0000 | 20.2950 |

## Env-Level Methodology Lift

| Env | Rows | Avg reward lift | Exact lift | Targets | Pre-scalar acc | Symbolic acc | Multi-signal acc | FC reduction vs pre | Symbolic gap | Read |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `ascii_tree_deep` | 5 | 0.1400 | 2 | commit:3, reject_or_abstain:2 | 0.6000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | Node completeness is the symbolic hinge; exact formatting can be circuit-owned after nodes are present. |
| `choice_contract` | 4 | 0.2500 | 1 | commit:2, reject_or_abstain:2 | 0.7500 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | A recoverable label is enough for symbolic extraction; absent labels should be rejected. |
| `ifeval_contract_subset` | 2 | 1.0000 | 2 | commit:2 | 0.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | Literal-count contracts are separable after canonical repair, but raw prompt hints are weak. |
| `intellect3_camp_gate` | 4 | 0.0312 | 1 | commit:2, reject_or_abstain:2 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | Signature projection helps once a plausible grid exposes enough row/column structure. |
| `intellect3_logic_c_signature` | 122 | 0.0968 | 81 | commit:101, reject_or_abstain:21 | 0.6311 | 0.8279 | 1.0000 | 0.7143 | 0.1721 | Post-repair reward delta is required; repaired signatures alone still false-commit no-gain repairs. |
| `math_answer_search` | 4 | 0.0000 | 0 | commit:1, reject_or_abstain:3 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | Negative control: without an exact candidate or solver, symbolic gates cannot invent the answer. |
| `pydantic_hard_schema` | 1 | 1.0000 | 1 | commit:1 | 0.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | Schema and field validation are highly separable once canonical repair or exact runtime state is available. |
| `safety_abstain_router` | 2 | 1.0000 | 2 | commit:2 | 0.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | Route labels become separable when the decision/reason/safe-step schema is explicit. |
| `tool_contract_router` | 4 | 0.2500 | 1 | commit:2, reject_or_abstain:2 | 0.7500 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | Intent/schema atoms make tool-call repair separable once a partial semantic proposal exists. |

## Interpretation

- The C-signature lesson generalizes as a methodology: make repair rows carry before/after verifier state, then train commit/veto TRMs on multi-signal post-repair targets.
- Env-specific symbolic checks are valuable but not universally sufficient. C-signature repairs show the key limitation: all repaired candidates can pass signatures while no-gain repairs still need vetoing.
- Exact-only commit is safe but too conservative in lanes with partial repair improvements, so it can hide useful training signal.
- Math remains the negative-control boundary: without an exact candidate, solver, or richer numeric invariant, MeTTa/TRM control logic cannot invent the missing answer.
- Treat `post_multi_signal` as a separability ceiling and target definition, not trained TRM performance.

## MeTTa Contract Sketch

```scheme
; Multi-env MeTTa/TRM methodology-lift contract sketch.
; These rules define commit/veto training targets from post-repair state.

(= (positive-repair-delta $state)
   (> (reward-delta $state) 0.0))

(= (post-multi-signal-commit $state)
   (if (or (after-exact $state) (positive-repair-delta $state))
       commit
       reject_or_abstain))

(= (post-symbolic-commit $state)
   (if (env-symbolic-pass $state)
       commit
       reject_or_abstain))

(= (env-symbolic-pass $state)
   (match (env-family $state)
     (intellect3_logic_c_signature (and (after-t-signature-pass $state) (after-c-signature-pass $state)))
     (tool_contract_router (has-valid-tool-and-required-arguments $state))
     (choice_contract (has-allowed-choice-label $state))
     (ascii_tree_deep (node-set-complete $state))
     (intellect3_camp_gate (signature-projection-matched $state))
     (math_answer_search (exact-candidate-present $state))
     (_ False)))
```
