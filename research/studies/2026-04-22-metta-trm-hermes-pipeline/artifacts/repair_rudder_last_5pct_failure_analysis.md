# Repair Rudder Last-5% Failure Analysis

Date: 2026-05-02

This note analyzes the residual errors after the snacksack 9B/27B repair-rudder
runs over the 88-row non-train Pure-TRM split.

## Main Finding

The best arm is not primarily limited by LLM scale. The 9B and 27B raw rudders
improve slightly with scale, but the high-performing MeTTa static gate fails on
a small number of typed veto cases:

| model | best arm | joint accuracy | misses |
| --- | --- | ---: | ---: |
| 9B | `metta_static_gate_rudder` | 0.9545 | 4 / 88 |
| 27B | `metta_static_gate_rudder` | 0.9432 | 5 / 88 |

For 9B, all four misses are Intellect-3-Logic cases where the repair action is
correct but the commit/veto decision is wrong:

| split | case | target | predicted |
| --- | --- | --- | --- |
| val_seen | `intellect_3_logic_0:logic_trm_c_repair_if_c_fail` | `c_repair / reject_or_abstain` | `c_repair / commit` |
| val_seen | `intellect_3_logic_0:logic_trm_dual_repair_if_any_sig_fail` | `dual_repair / reject_or_abstain` | `dual_repair / commit` |
| holdout_seen | `intellect_3_logic_88:logic_trm_c_repair_if_c_fail` | `c_repair / reject_or_abstain` | `c_repair / commit` |
| holdout_seen | `intellect_3_logic_88:logic_trm_dual_repair_if_any_sig_fail` | `dual_repair / reject_or_abstain` | `dual_repair / commit` |

For 27B, the same four Intellect-3-Logic cases remain, plus one cross-family
case:

| split | case | target | predicted |
| --- | --- | --- | --- |
| holdout_unseen_family | `battery_storage` | `canonical_commit / commit` | `canonical_commit / reject_or_abstain` |

## Diagnosis

The current static gate has deterministic target-action rules for:

- exact positives: commit
- `signature_pass_cell_fail`: reject
- obvious null/weak-surface cases: reject

It does not deterministically handle `c_signature_fail` rows where the repair
action is known but the post-repair verifier says the repair failed or produced
no gain. Those rows fall back to the LLM commit/veto rudder, and both 9B and 27B
over-commit the repair.

The missing signal is not "more intelligence in the rudder." It is a typed
post-repair verifier/control signal:

```text
if failure_label == c_signature_fail
and bucket == repair_failure_or_no_gain:
    choose repair action c_repair or dual_repair as appropriate
    but veto commit
```

That rule would close the 9B static-gate residual on this benchmark slice. The
27B extra miss is the complementary problem: a valid canonical repair was
over-vetoed on a JSON-value mismatch case, so the curriculum also needs positive
post-repair proof traces, not only negative veto traces.

## What The Last 5% Is

The last 5% is a commit/veto calibration layer around semi-failed alternatives:

- "repair chosen correctly, but post-repair evidence says do not commit"
- "repair chosen correctly, and post-repair evidence says commit despite surface uncertainty"

This is exactly where synthetic chain-of-thought can help, but it should not be
generic natural-language CoT. The useful synthetic trace is verifier-grounded:

1. Identify typed failure label.
2. Select candidate repair operator.
3. Apply repair or simulate repaired artifact.
4. Run verifier/signature checks.
5. Record delta against one or more success metrics.
6. Commit only if the repaired artifact crosses the configured threshold.

The LLM should be orchestrated to write or call this trace, not to freehand the
decision. In the paper language, this is the `TRM-infused-skill skill`: a skill
that designs the TRM/verifier/MeTTa loop for a new benchmark family.

## Next Curriculum

For each hard problem family, generate synthetic rows with these fields:

- `failure_label`
- `repair_operator`
- `pre_verifier_signature`
- `post_verifier_signature`
- `metric_delta`
- `commit_threshold`
- `target_action`
- `counterfactual_reason`: why the nearest wrong action fails

Prioritize paired rows:

- same problem, same repair operator, post-repair pass versus post-repair no-gain
- same failure label, different repair operator, one valid and one invalid
- same surface text, different verifier outcome, to break lexical shortcuts

This should train a small commit/veto TRM to learn the missing boundary. The
LLM then becomes a planner and trace drafter, while the TRM/MeTTa/verifier stack
owns the execution-quality decision.

## Generalization Hypothesis

To evolve toward 100% on a challenging problem set, the system should iterate:

1. Mine residual failures from the benchmark.
2. Cluster failures by typed verifier defect, not by prompt wording.
3. Generate synthetic paired traces for the missing boundary.
4. Train or update the relevant repair/verifier/commit TRM.
5. Re-run the skill with MeTTa rules updated only when a verifier-visible
   invariant has been found.

The larger LLM can help discover candidate traces and propose repairs, but the
observed data says the durable lift comes from turning those traces into typed
control-plane signals.
