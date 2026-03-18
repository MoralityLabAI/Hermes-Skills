# tempo-hermes skill v3

A more executable Hermes/Codex starter for **Tempo chain operations and MPP machine payments**.

## What changed in v3
- upgrades the scaffold from notes-only to a small TypeScript module layout
- bakes in current public Tempo docs assumptions for mainnet and Moderato testnet
- adds payment, policy, sponsorship, and docs/MCP helper modules
- adds docs-grounded MPP routing for CLI, client, server, and session flows
- gives Codex a safer default path: **plan first, broadcast only when explicitly enabled**
- preserves the conceptual split between **Tempo Transactions** and **MPP-specific work**

## Included
- `tempo-hermes/SKILL.md`
- `tempo-hermes/agents/openai.yaml`
- `tempo-hermes/package.json`
- `tempo-hermes/tsconfig.json`
- `tempo-hermes/src/config/tempo.ts`
- `tempo-hermes/src/rpc/client.ts`
- `tempo-hermes/src/payments/transfers.ts`
- `tempo-hermes/src/payments/receipts.ts`
- `tempo-hermes/src/policy/spendPolicy.ts`
- `tempo-hermes/src/sponsorship/sponsor.ts`
- `tempo-hermes/src/docs/tempoDocs.ts`
- `tempo-hermes/examples/*.ts`
- `tempo-hermes/examples/mpp-demo/*`
- `tempo-hermes/references/*.md`
- `tempo-hermes/scripts/check_tempo_rpc.sh`

## Design intent
This is still a starter, but it is closer to runnable code:
- config is centralized
- docs assumptions are explicit
- policy checks exist before mutable actions
- payment helpers are shaped for Codex to finish rather than reinvent
- MPP workflows are routed to the official quickstarts instead of guessed abstractions
- the skill now includes installable agent metadata and a self-contained MPP demo package

## Deliberate non-goals
- no fake Tempo->ETH bridge logic
- no invented MPP settlement internals
- no auto-broadcast by default
- no assumption that the public testnet sponsor endpoint exists on mainnet
