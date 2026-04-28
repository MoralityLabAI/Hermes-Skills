# Near-Miss Repair Curriculum Splits

Generated: `2026-04-26T16:11:31.971109+00:00`

These files convert the near-miss repair curriculum into leakage-aware train/eval slices for repair, verifier, and commit/veto TRMs.

## Split Counts

| Split | Rows | Buckets | Roles |
| --- | ---: | --- | --- |
| `train` | 156 | `exact_positive`:46, `partial_repair_improvement`:12, `repair_failure_or_no_gain`:40, `repair_success`:58 | `choice_contract`:4, `hard_reasoning_logic`:148, `hard_reasoning_numeric`:4 |
| `val_seen` | 34 | `exact_positive`:14, `partial_repair_improvement`:2, `repair_failure_or_no_gain`:6, `repair_success`:12 | `hard_reasoning_logic`:34 |
| `holdout_seen` | 36 | `exact_positive`:8, `partial_repair_improvement`:6, `repair_failure_or_no_gain`:10, `repair_success`:12 | `hard_reasoning_logic`:36 |
| `holdout_unseen_family` | 18 | `exact_positive`:3, `repair_failure_or_no_gain`:6, `repair_success`:9 | `abstain_guard`:2, `choice_contract`:2, `hard_reasoning_logic`:4, `structured_map`:10 |

## Unseen-Family Holdout

`bullet_word_count_failure`, `grid_shape_failure`, `hashtag_contract_failure`, `json_parse_failure`, `json_value_mismatch`, `partial_tree`

## Candidate Trainer Specs

| Spec | Purpose | Train | Val seen | Holdout seen | Holdout unseen-family |
| --- | --- | ---: | ---: | ---: | ---: |
| `repair_verifier_logic_c_signature` | Train the logic repair/verifier circuit around C-signature failure, exact positives, and signature-pass cell failures. | 148 | 34 | 36 | 0 |
| `commit_veto_multirole` | Train commit/veto policy to accept repairs and positives while rejecting no-gain repairs. | 156 | 34 | 36 | 18 |
| `structured_contract_repair` | Train schema, tree, and choice-contract repair gates where symbolic closure is available. | 4 | 0 | 0 | 12 |
| `numeric_teacher_auditor` | Keep hard numeric rows as teacher-candidate audit and veto data, not standalone solver training. | 4 | 0 | 0 | 0 |
| `abstain_guard` | Train abstain/route guard rows where a malformed or unsafe candidate should be rejected. | 0 | 0 | 0 | 2 |

## Method Notes

- Treat `train` as replay/curriculum data, not benchmark evidence.
- Use `val_seen` to tune repair thresholds inside known failure families.
- Use `holdout_seen` to test case-level generalization without family shift.
- Use `holdout_unseen_family` to test whether MeTTa-framed gates transfer to new failure labels.
- Keep `hard_reasoning_numeric` under teacher-auditor or veto training until stronger candidate generators exist.
