# Claim Audit

## Evidence Class

- `no_model_validator_smoke` validates row keys and validator behavior.
- `live_model_local_3b` applies only when local result JSON and job-cap summary are present.

## Allowed Claims

- The suite covers repo search, file lookup, shell-safe planning, scheduling, weather-like lookup, and JSON argument traps.
- The validator separates schema/tool-call validity from exact semantic route and argument correctness.
- Destructive or ambiguous requests are represented as explicit reject or clarification tool calls.
- Live local 3B evidence shows schema and route-control lift, with exact success still low: feedback repair scored 4/36 exact.
- Alias V2 evidence shows memory-driven lift: `pure_trm` scored 14/36 exact and the no-model static safety overlay reduced unsafe commits to zero.

## Disallowed Claims

- Do not claim high-stakes answer quality; this suite only scores routing, arguments, and safety contracts.
- Do not execute shell commands from benchmark rows; this suite validates planned calls only.
- Do not present this as a successful exact tool-use benchmark; exact argument recovery is still the failure point.
- Do not report the static safety overlay as live model lift; it is a deterministic post-processing gate.
