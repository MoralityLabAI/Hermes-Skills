# Addendum: Leakage-Aware Near-Miss Repair Splits

Status: draft addendum  
Date: April 26, 2026

## Thesis

The near-miss curriculum should not be trained or reported as a random supervised corpus. The right methodology is to split by base case and failure family, because the mechanism being tested is whether MeTTa-framed TRM gates learn reusable repair, verification, and commit behavior rather than memorizing a specific repaired output.

The generated split report is [near_miss_repair_splits.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\near_miss_repair_curriculum\splits\near_miss_repair_splits.md>). The candidate trainer spec is [candidate_trainer_specs.json](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\near_miss_repair_curriculum\splits\candidate_trainer_specs.json>).

## Split Shape

Current split over `244` rows:

| Split | Rows | Use |
| --- | ---: | --- |
| `train` | `156` | Repair/verifier/commit replay curriculum. |
| `val_seen` | `34` | Tune thresholds inside known failure families. |
| `holdout_seen` | `36` | Test case-level generalization without family shift. |
| `holdout_unseen_family` | `18` | Test transfer to held-out failure labels. |

The split keeps policy variants for the same base case together. Rare labels reserved for unseen-family testing are `bullet_word_count_failure`, `grid_shape_failure`, `hashtag_contract_failure`, `json_parse_failure`, `json_value_mismatch`, and `partial_tree`.

## Candidate TRM Training Lanes

The immediate high-confidence lane is `repair_verifier_logic_c_signature`: `148` train rows, `34` seen validation rows, and `36` seen holdout rows. This is the lane most directly tied to the Intellect-3 logic lift from `0.3028` to `0.6789` in post-hoc replay.

The `commit_veto_multirole` lane has full coverage across all `244` rows and is the safest general training target: it teaches when to commit a repair, when to preserve an exact positive, and when to reject no-gain repairs.

The structured-contract, numeric, and abstain lanes remain small. They should be reported as transfer probes or seed corpora, not as statistically strong standalone training datasets.

## Claim Boundary

This split package is training infrastructure. It is not a new benchmark result. A publishable claim should require:

- train a repair/verifier or commit-veto TRM on `train`;
- tune only on `val_seen`;
- report `holdout_seen` and `holdout_unseen_family` separately;
- compare against no-MeTTa and prompt-only MeTTa baselines;
- report false-commit and repair-regression rates, not only exact score.
