# C-Signature Post-Repair Verifier Sweep

Generated: `2026-04-28T14:03:18.178724+00:00`

This no-model sweep tests whether the remaining C-signature false commits are solved by exposing richer post-repair verifier state to the commit TRM.

Selected policy: `postrepair_exact_or_gain_gt_0`

## Selected Policy Metrics

| Split | Rows | Accuracy | False commit rate | False reject rate | Expected committed delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `train` | 86 | 1.0000 | 0.0000 | 0.0000 | 8.7983 |
| `val_seen` | 16 | 1.0000 | 0.0000 | 0.0000 | 1.9117 |
| `holdout_seen` | 20 | 1.0000 | 0.0000 | 0.0000 | 1.7600 |

## Policy Comparison

| Policy | Signal class | Val acc | Val false commit | Val false reject | Holdout acc | Holdout false commit | Holdout false reject |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `postrepair_exact_or_gain_gt_0` | `post_evaluator_multi_signal` | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 |
| `postrepair_gain_ge_0p02` | `post_evaluator_delta` | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 |
| `postrepair_gain_ge_0p05` | `post_evaluator_delta` | 1.0000 | 0.0000 | 0.0000 | 0.8000 | 0.0000 | 0.2222 |
| `postrepair_gain_gt_0` | `post_evaluator_delta` | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 |
| `postrepair_signature_and_gain_gt_0` | `post_symbolic_plus_delta` | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 |
| `after_exact_only` | `post_evaluator_exact` | 0.8750 | 0.0000 | 0.1429 | 0.7000 | 0.0000 | 0.3333 |
| `after_signature_and_exact` | `post_symbolic_plus_exact` | 0.8750 | 0.0000 | 0.1429 | 0.7000 | 0.0000 | 0.3333 |
| `after_signature_complete_only` | `post_symbolic` | 0.8750 | 1.0000 | 0.0000 | 0.9000 | 1.0000 | 0.0000 |
| `always_commit` | `control` | 0.8750 | 1.0000 | 0.0000 | 0.9000 | 1.0000 | 0.0000 |
| `postrepair_non_regression` | `post_evaluator_delta` | 0.8750 | 1.0000 | 0.0000 | 0.9000 | 1.0000 | 0.0000 |

## Interpretation

- Signature-complete state alone is not enough: the repaired C-signature candidates all pass signatures, including no-gain repairs.
- Exact-only validation is safe but rejects partial improvements, so it is too conservative for a repair curriculum.
- The useful training signal is multi-signal post-repair state: exactness plus positive reward delta. This closes false commits while preserving non-exact improvements.
- This should be reported as an evaluator-backed verifier/commit ceiling and a TRM training target, not as evidence that the 3B prompt solved the case.

## MeTTa Contract

```scheme
; C-signature post-repair verifier sketch.
; This is an evaluator-backed training target, not a prompt-only LLM result.

(= (signature-complete $state)
   (and (after-t-signature-pass $state) (after-c-signature-pass $state)))

(= (positive-repair-delta $state)
   (> (reward-delta $state) 0.0))

(= (c-signature-commit-action $state)
   (if (or (after-exact $state) (positive-repair-delta $state))
       commit
       reject_or_abstain))

(= (c-signature-training-signals $state)
   (list (after-exact $state)
         (signature-complete $state)
         (reward-delta $state)
         (c-signature-commit-action $state)))
```
