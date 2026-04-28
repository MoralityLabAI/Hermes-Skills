# Claim Audit

## Evidence Class

- `no_model_validator_smoke` for canonical validator validation.
- `live_model_local_3b` only after local result JSON and job-cap summary exist.

## Allowed Claims

- The row suite is harder than heldout50 by family mix: numeric micro-math, logic labels, computed JSON, state sequences, and deeper trees.
- The canonical validator smoke validates the answer keys and exact validators before model calls.
- On this local 3B run, feedback repair scored 13/30 exact versus baseline 12/30, blind repair 12/30, and MeTTa runtime 9/30.
- On the 21 failed MeTTa-runtime opportunities, feedback repair fixed 4 rows versus 3 rows for blind repair.

## Disallowed Claims

- Do not call repair-prompt gains trained TRM lift.
- Do not claim broad math or logic reasoning gain from this suite alone.
- Do not compare to 9B/27B unless row IDs and validators are identical.
- Do not present this as strong hard-suite lift; the feedback repair advantage is small and must be reported separately from the easier heldout50 result.
