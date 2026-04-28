# Structured-Map Live Eval

| Env | Arm | Status | Reward | Visible Output | Action Type | Action Excerpt |
| --- | --- | --- | ---: | --- | --- | --- |
| psycho_bench | baseline | success | 3.328333333333333 | True | direct_answer | 31: 3 39: 3 17: 4 26: 3 12: 2 16: 3 3: 4 37: 2 18: 3 1: 3 10: 4 40: 3 43: 3 27: 2 2: 2 25: 3 41: 3 35: 3 13: 4 8: 3 30: 3 33: 4 38: 4 21: 3 32: 4 5: 3 20: 3 28: 4 19: 3 34: 3 42: 4 44: 3 29: 3 6: 3 22: 4 9: 4 23: 2 4:... |
| pydantic_adherence | baseline | success | 0.0 | True | direct_answer | {"policy_id":"550e8400-e29b-41d4-a716-446655440000","name":"Standard Policy","max_books":10,"periods":[{"genre":"fiction","days":14,"allow_renewal":true},{"genre":"non-fiction","days":21,"allow_renewal":true},{"genre"... |
| psycho_bench | plain_structured_map | success | 3.306111111111111 | True | direct_answer | 31: 3 39: 3 17: 4 26: 3 12: 2 16: 3 3: 4 37: 2 18: 3 1: 3 10: 4 40: 3 43: 3 27: 2 2: 2 25: 3 41: 3 35: 3 13: 4 8: 3 30: 3 33: 4 38: 4 21: 3 32: 4 5: 3 20: 3 28: 4 19: 3 34: 3 42: 4 44: 3 29: 3 6: 3 22: 3 9: 3 23: 2 4:... |
| pydantic_adherence | plain_structured_map | success | 0.0 | True | direct_answer | {"policy_id":"550e8400-e29b-41d4-a716-446655440000","name":"Standard Lending Policy","max_books":10,"periods":[{"genre":"fiction","days":14,"allow_renewal":true},{"genre":"non-fiction","days":21,"allow_renewal":true},... |
| psycho_bench | retrieval_assisted | success | 3.331111111111111 | True | direct_answer | 31: 3 39: 3 17: 4 26: 3 12: 2 16: 3 3: 4 37: 2 18: 3 1: 3 10: 4 40: 3 43: 3 27: 2 2: 2 25: 3 41: 3 35: 3 13: 4 8: 3 30: 3 33: 4 38: 4 21: 3 32: 4 5: 3 20: 3 28: 4 19: 3 34: 3 42: 4 44: 3 29: 3 6: 3 22: 3 9: 3 23: 2 4:... |
| pydantic_adherence | retrieval_assisted | success | 1.0 | True | direct_answer | {"policy_id":"11111111-1111-1111-1111-111111111111","name":"Main","max_books":3,"periods":[{"genre":"fiction","days":14},{"genre":"non-fiction","days":14},{"genre":"children","days":14},{"genre":"reference","days":7}]... |

## Notes

- `baseline`: no Hermes structured-map prompt.
- `plain_structured_map`: base `primehub-structured-map-hermes` prompt only.
- `retrieval_assisted`: base structured-map prompt plus Primehub schema memory from `primehub_schema_pack`.

