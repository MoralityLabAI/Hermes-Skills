# Codex v3 implementation plan

## Objective
Build a generic Tempo module that is safe enough to extend into real payment tooling without forcing Codex to rediscover Tempo's key quirks.

## Immediate tasks
1. Run the RPC health check.
2. Confirm the chosen dependency surface:
   - pure `viem`
   - `viem/tempo`
   - Tempo's official SDK wrappers
3. Replace the placeholder mutable send path in `src/payments/transfers.ts` with the exact current Tempo action.
4. Add a real memo-aware transfer helper if the chosen SDK exposes it.
5. Add receipt/event parsing around the chosen action.
6. Gate all mutable actions behind `SpendPolicy`.
7. Add a sponsorship adapter only when explicitly enabled.

## Why this saves plan
- config, docs routing, and policy are already split out
- Codex gets anti-hallucination constraints in file form
- the docs/MCP pointers reduce source spelunking
- the transfer scaffold makes the remaining unknowns obvious instead of hidden

## Optional next steps
- add fee-token preference management
- add reusable nonce-key allocation for parallel submissions
- add MPP as a separate skill/module once its docs are ingested
