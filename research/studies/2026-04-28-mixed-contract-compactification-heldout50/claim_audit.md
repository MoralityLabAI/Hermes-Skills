# Claim Audit

## Evidence Class

- `no_model_validator_smoke` for canonical validator validation.
- `live_model_local_3b` for local Qwen2.5-3B Q4 model completions under the Windows job-cap wrapper.

## Allowed Claims

- The row suite is held out from the 12-row seed smoke.
- The validators separate contract validity from semantic validity across mixed observable contracts.
- Live local model results can be used as a held-out 50-row prompt/repair-gate benchmark because job-cap receipts and result JSON are present.
- On this suite, `metta_runtime_repair` improves exact success from 23/50 baseline to 37/50, with `metta_runtime` at 32/50 and `pure_trm` at 27/50.

## Disallowed Claims

- Do not call repair-prompt gains trained TRM lift.
- Do not claim broad reasoning gain from output-contract wins.
- Do not mix canonical validator smoke with live model arms.
- Do not compare this to 9B/27B unless row IDs and validators are identical.
- Do not treat easy delimiter, choice, or label rows as sufficient evidence for harder math/logic generalization.
