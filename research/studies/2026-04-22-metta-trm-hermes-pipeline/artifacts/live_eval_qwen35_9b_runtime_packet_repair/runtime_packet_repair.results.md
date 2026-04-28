# Runtime-Packet And Repair Live Eval

| Env | Arm | Reward | Prompt Tokens | Completion Tokens | Repair Applied | Action Excerpt |
| --- | --- | ---: | ---: | ---: | --- | --- |
| psycho_bench | without_metta | 3.328333333333333 | 1138 | 255 | False | 31: 3 39: 3 17: 4 26: 3 12: 2 16: 3 3: 4 37: 2 18: 3 1: 3 10: 4 40: 3 43: 3 27: 2 2: 2 25: 3 41: 3 35: 3 13: 4 8: 3 30: 3 33: 4 38: 4 21: 3 32: 4 5: 3 20: 3 28: 4 19: 3 34: 3 42: 4 44: 3 29: 3 6: 3 22: 4 9: 4 23: 2 4:... |
| ascii_tree | without_metta | 0.7999999999999999 | 736 | 64 | False | <ascii_formatted> packaging +--brew +--linux-arch +--linux-centos +--linux-debian +--linux-fedora +--mac-ports +--snapcraft +--windows-chocolatey +--tools </ascii_formatted> |
| pydantic_adherence | without_metta | 1.0 | 1557 | 163 | False | {"policy_id":"11111111-1111-1111-1111-111111111111","name":"Main","max_books":3,"periods":[{"genre":"fiction","days":14,"allow_renewal":true},{"genre":"non-fiction","days":21,"allow_renewal":true},{"genre":"children",... |
| psycho_bench | with_metta_runtime | 3.3483333333333336 | 1187 | 255 | False | 31: 3 39: 3 17: 4 26: 3 12: 2 16: 3 3: 4 37: 2 18: 3 1: 3 10: 4 40: 4 43: 3 27: 2 2: 2 25: 3 41: 3 35: 3 13: 4 8: 3 30: 3 33: 4 38: 4 21: 3 32: 4 5: 3 20: 3 28: 4 19: 3 34: 3 42: 4 44: 3 29: 3 6: 3 22: 4 9: 4 23: 2 4:... |
| ascii_tree | with_metta_runtime | 0.7999999999999999 | 794 | 64 | False | <ascii_formatted> packaging +--brew +--linux-arch +--linux-centos +--linux-debian +--linux-fedora +--mac-ports +--snapcraft +--windows-chocolatey +--tools </ascii_formatted> |
| pydantic_adherence | with_metta_runtime | 1.0 | 1522 | 178 | False | {"policy_id":"11111111-1111-1111-1111-111111111111","name":"Main","max_books":3,"periods":[{"genre":"fiction","days":14,"allow_renewal":true},{"genre":"non-fiction","days":21,"allow_renewal":true},{"genre":"children",... |
| psycho_bench | with_metta_runtime_repair | 3.3483333333333336 | 1187 | 255 | False | 31: 3 39: 3 17: 4 26: 3 12: 2 16: 3 3: 4 37: 2 18: 3 1: 3 10: 4 40: 4 43: 3 27: 2 2: 2 25: 3 41: 3 35: 3 13: 4 8: 3 30: 3 33: 4 38: 4 21: 3 32: 4 5: 3 20: 3 28: 4 19: 3 34: 3 42: 4 44: 3 29: 3 6: 3 22: 4 9: 4 23: 2 4:... |
| ascii_tree | with_metta_runtime_repair | 0.7999999999999999 | 794 | 64 | False | <ascii_formatted> packaging +--brew +--linux-arch +--linux-centos +--linux-debian +--linux-fedora +--mac-ports +--snapcraft +--windows-chocolatey +--tools </ascii_formatted> |
| pydantic_adherence | with_metta_runtime_repair | 1.0 | 1522 | 178 | False | {"policy_id":"11111111-1111-1111-1111-111111111111","name":"Main","max_books":3,"periods":[{"genre":"fiction","days":14,"allow_renewal":true},{"genre":"non-fiction","days":21,"allow_renewal":true},{"genre":"children",... |

## Notes

- `without_metta`: control prompt using the non-MeTTa Primehub schema pack.
- `with_metta_runtime`: compact prompt using `runtime_packet.json`.
- `with_metta_runtime_repair`: same runtime-packet generation, then deterministic MeTTa repair before remote verifier scoring.

