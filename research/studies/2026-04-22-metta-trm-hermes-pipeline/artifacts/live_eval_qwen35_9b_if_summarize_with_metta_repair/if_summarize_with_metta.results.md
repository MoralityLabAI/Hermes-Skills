# if_summarize_judge With-MeTTa Eval

| Arm | Seeds | Episodes | Total Reward | Avg Reward | Prompt Tokens | Completion Tokens | Profiles Seen |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| without_metta | 7, 11, 19 | 3 | 1.0 | 0.3333 | 2636 | 88 | exact_10w_bullets:1, one_comma:1, single_question:1 |
| with_metta_runtime | 7, 11, 19 | 3 | 1.0 | 0.3333 | 4973 | 88 | exact_10w_bullets:1, one_comma:1, single_question:1 |
| with_metta_runtime_repair | 7, 11, 19 | 3 | 3.0 | 1.0000 | 4973 | 88 | exact_10w_bullets:1, one_comma:1, single_question:1 |

## Notes

- `without_metta`: base `primehub-constraint-summarize-hermes` prompt only.
- `with_metta_runtime`: same base prompt plus the compact profile-aware MeTTa runtime packet.
- `with_metta_runtime_repair`: same runtime arm, then deterministic MeTTa repair before remote verifier scoring.

