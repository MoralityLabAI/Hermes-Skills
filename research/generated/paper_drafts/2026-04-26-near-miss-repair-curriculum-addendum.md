# Addendum: Near-Miss Repair Curriculum For TRM Training

Status: draft addendum  
Date: April 26, 2026

## Thesis

The largest MeTTa/TRM lifts in the current Hermes skill work come from repair, verification, and commit-control behavior over semi-failed outputs. The training methodology should therefore prioritize a near-miss repair curriculum rather than only exact-positive imitation.

The generated curriculum is [near_miss_repair_curriculum.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\near_miss_repair_curriculum\near_miss_repair_curriculum.md>). The Pure-TRM export is [near_miss_repair_pure_trm_rows.jsonl](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\near_miss_repair_curriculum\near_miss_repair_pure_trm_rows.jsonl>).

## Corpus Shape

The current curriculum has `244` rows:

| Bucket | Rows | Use |
| --- | ---: | --- |
| `repair_success` | `91` | Train repair and verifier TRMs on successful transformations. |
| `partial_repair_improvement` | `20` | Train ranked repair and commit policies. |
| `exact_positive` | `71` | Preserve clean examples and non-repair commit cases. |
| `repair_failure_or_no_gain` | `62` | Train veto/abstain and hard-negative commit behavior. |

Role distribution:

| Role | Rows | Read |
| --- | ---: | --- |
| `hard_reasoning_logic` | `222` | Main current opportunity, dominated by Intellect-3 C-signature repair rows. |
| `structured_map` | `10` | Schema/tree/tool-shape repair examples. |
| `choice_contract` | `6` | Label/wrapper/literal-count repair examples. |
| `hard_reasoning_numeric` | `4` | Boundary rows; use for candidate auditing, not solver training. |
| `abstain_guard` | `2` | Safety route and refusal-format examples. |

## Methodology

For each env family, collect:

- raw candidate output,
- verifier failure label,
- repair action,
- repaired output,
- post-repair verifier result,
- whether repair changed semantics or only structure,
- commit/veto decision.

The ideal sample set is balanced across:

- successes where repair makes the output exact,
- partial improvements where repair helps but does not solve,
- exact positives where repair should not fire,
- hard negatives where repair should abstain.

## Training Claim

This reframes MeTTa as a data-curation and supervision-shaping layer. It makes the semi-failed state explicit and turns a single failed benchmark row into typed TRM training examples: `validate_failure`, `repair_success`, `repair_failure`, `signature_pass_cell_fail`, `commit_error`, and `reject_or_repair`.

The near-term bet is that repair/verifier TRMs can squeeze more lift by learning when a near-miss is repairable and when a commit gate should abstain. This should be evaluated by held-out failure family, not by random held-out rows.

## Train/Eval Split

The curriculum now has a leakage-aware split package: [near_miss_repair_splits.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\near_miss_repair_curriculum\splits\near_miss_repair_splits.md>).

Current split: `156` train rows, `34` seen-family validation rows, `36` seen-family holdout rows, and `18` unseen-family holdout rows. The primary ready lane is `repair_verifier_logic_c_signature`; structured-contract, numeric, and abstain rows should remain seed/transfer probes until more examples are collected.
