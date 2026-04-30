# MeTTa Trainer-Policy Bundle

- cluster_id: `constraint_summarize`
- row_count: `446`
- avg_supervision_weight: `1.6062`

## Trainer Policy

- policy_name: `format_support_trainer_policy`
- support_tier: `format_support`
- routing_strength: `moderate`
- min_supervision_weight: `0.35`

## Signal Counts

| Signal | Total | Positive | Negative |
| --- | ---: | ---: | ---: |
| contract_family_match | 69 | 69 | 0 |
| contract_validity | 54 | 36 | 18 |
| critic_verdict_agreement | 36 | 36 | 0 |
| failure_localization | 36 | 30 | 6 |
| profile_selection_correctness | 17 | 17 | 0 |
| repair_success | 18 | 18 | 0 |
| retrieval_selection_correctness | 18 | 18 | 0 |
| task_success | 54 | 36 | 18 |
| transport_no_fallback | 72 | 72 | 0 |
| transport_visible_output | 72 | 72 | 0 |

## Bucket Counts

| Bucket | Count |
| --- | ---: |
| exact_positive | 125 |
| near_miss | 30 |
| negative | 42 |
| weak_positive | 249 |
