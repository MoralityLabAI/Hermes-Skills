# Claim Audit

## Evidence Class

- `no_model_validator_smoke` only. This validates row keys and validator behavior, not model lift.

## Allowed Claims

- The suite covers repo search, file lookup, shell-safe planning, scheduling, weather-like lookup, and JSON argument traps.
- The validator separates schema/tool-call validity from exact semantic route and argument correctness.
- Destructive or ambiguous requests are represented as explicit reject or clarification tool calls.

## Disallowed Claims

- Do not report MeTTa/TRM tool-use lift until a live model benchmark exists.
- Do not claim high-stakes answer quality; this suite only scores routing, arguments, and safety contracts.
- Do not execute shell commands from benchmark rows; this suite validates planned calls only.
