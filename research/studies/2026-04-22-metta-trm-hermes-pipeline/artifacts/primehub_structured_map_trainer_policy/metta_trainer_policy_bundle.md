# MeTTa Trainer-Policy Bundle

- cluster_id: `structured_map`
- row_count: `63`
- avg_supervision_weight: `1.5195`

## Trainer Policy

- policy_name: `format_support_trainer_policy`
- support_tier: `format_support`
- routing_strength: `moderate`
- min_supervision_weight: `0.35`

## Signal Counts

| Signal | Total | Positive | Negative |
| --- | ---: | ---: | ---: |
| contract_family_match | 3 | 3 | 0 |
| contract_validity | 9 | 6 | 3 |
| critic_verdict_agreement | 6 | 6 | 0 |
| failure_localization | 6 | 6 | 0 |
| repair_success | 3 | 3 | 0 |
| retrieval_selection_correctness | 3 | 3 | 0 |
| task_success | 9 | 6 | 3 |
| transport_no_fallback | 12 | 12 | 0 |
| transport_visible_output | 12 | 12 | 0 |

## Bucket Counts

| Bucket | Count |
| --- | ---: |
| exact_positive | 18 |
| near_miss | 6 |
| negative | 6 |
| weak_positive | 33 |
