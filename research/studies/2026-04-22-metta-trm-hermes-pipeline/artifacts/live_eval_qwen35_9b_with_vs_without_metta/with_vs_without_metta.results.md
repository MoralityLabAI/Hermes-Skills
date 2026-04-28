# With-MeTTa Vs Without-MeTTa Live Eval

| Env | Arm | Status | Reward | Visible Output | Action Type | Action Excerpt |
| --- | --- | --- | ---: | --- | --- | --- |
| psycho_bench | without_metta | success | 3.328333333333333 | True | direct_answer | 31: 3 39: 3 17: 4 26: 3 12: 2 16: 3 3: 4 37: 2 18: 3 1: 3 10: 4 40: 3 43: 3 27: 2 2: 2 25: 3 41: 3 35: 3 13: 4 8: 3 30: 3 33: 4 38: 4 21: 3 32: 4 5: 3 20: 3 28: 4 19: 3 34: 3 42: 4 44: 3 29: 3 6: 3 22: 4 9: 4 23: 2 4:... |
| ascii_tree | without_metta | success | 0.7999999999999999 | True | direct_answer | <ascii_formatted> packaging +--brew +--linux-arch +--linux-centos +--linux-debian +--linux-fedora +--mac-ports +--snapcraft +--windows-chocolatey +--tools </ascii_formatted> |
| pydantic_adherence | without_metta | success | 1.0 | True | direct_answer | {"policy_id":"11111111-1111-1111-1111-111111111111","name":"Main","max_books":3,"periods":[{"genre":"fiction","days":14,"allow_renewal":true},{"genre":"non-fiction","days":21,"allow_renewal":true},{"genre":"children",... |
| psycho_bench | with_metta | success | 3.3033333333333332 | True | direct_answer | 31: 3 39: 3 17: 4 26: 3 12: 2 16: 3 3: 4 37: 2 18: 3 1: 3 10: 4 40: 3 43: 3 27: 2 2: 2 25: 3 41: 3 35: 3 13: 4 8: 3 30: 3 33: 4 38: 4 21: 3 32: 4 5: 3 20: 3 28: 4 19: 3 34: 3 42: 4 44: 3 29: 3 6: 3 22: 4 9: 4 23: 2 4:... |
| ascii_tree | with_metta | success | 0.7999999999999999 | True | direct_answer | <ascii_formatted> packaging +--brew +--linux-arch +--linux-centos +--linux-debian +--linux-fedora +--mac-ports +--snapcraft +--windows-chocolatey +--tools </ascii_formatted> |
| pydantic_adherence | with_metta | success | 1.0 | True | direct_answer | {"policy_id":"11111111-1111-1111-1111-111111111111","name":"Main","max_books":3,"periods":[{"genre":"fiction","days":14},{"genre":"non-fiction","days":21},{"genre":"children","days":7},{"genre":"reference","days":5}],... |

## Notes

- `without_metta`: base `primehub-structured-map-hermes` prompt plus the existing non-MeTTa Primehub schema pack.
- `with_metta`: base `primehub-structured-map-hermes` prompt plus the compiled MeTTa retrieval packet and critic hints.

