# if_summarize_judge With-MeTTa Eval

| Arm | Seeds | Episodes | Total Reward | Avg Reward | Prompt Tokens | Completion Tokens | Profiles Seen |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| without_metta | 7, 11, 19 | 3 | 1.0 | 0.3333 | 2636 | 87 | exact_10w_bullets:1, one_comma:1, single_question:1 |
| with_metta_runtime | 7, 11, 19 | 3 | 2.0 | 0.6667 | 4973 | 75 | exact_10w_bullets:1, one_comma:1, single_question:1 |

## Notes

- `without_metta`: base `primehub-constraint-summarize-hermes` prompt only.
- `with_metta_runtime`: same base prompt plus the compact profile-aware MeTTa runtime packet.

