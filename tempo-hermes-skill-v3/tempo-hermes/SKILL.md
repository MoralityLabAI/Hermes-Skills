---
name: tempo-hermes
description: Use this skill when the user needs Hermes/Codex help with the Tempo blockchain, including current network/docs lookup, Tempo Transactions, TIP-20 stablecoin payments, MPP machine-payments flows, fee sponsorship, and Tempo CLI or agent workflows.
---

# Tempo Hermes Skill

Use this skill when the user wants to build against Tempo in a docs-grounded way.

## Primary jobs
- connect to Tempo mainnet or Moderato testnet safely
- scaffold Tempo-native TypeScript code
- design TIP-20 payment flows and transfer memo handling
- design MPP machine-payments client, server, agent, and session flows
- handle fee-token and sponsorship semantics
- explain wallet quirks caused by the lack of a native gas token
- generate Codex-ready implementation plans
- route Hermes/Codex to Tempo docs, markdown pages, llms files, and MCP

## Hard rules
1. Tempo is EVM-compatible, but **there is no native gas token**.
2. Do not interpret `eth_getBalance` as spendable ETH.
3. Prefer **Tempo Transactions** over regular Ethereum transactions unless compatibility forces otherwise.
4. Treat fee-token, sponsorship, nonce-key, and memo handling as first-class Tempo concerns.
5. For **MPP**, use the official Tempo docs plus `mpp.dev` as the source of truth. Do not invent challenge, credential, session, or receipt semantics.
6. Keep **Tempo Transactions** and **MPP** conceptually separate:
   - Tempo Transactions are the chain-native transaction model.
   - MPP is the HTTP payment protocol layered on top of Tempo settlement.
7. Do not invent bridge paths, card rails, sponsor endpoints, or mainnet-only assumptions that the docs do not state.

## Default working style
- check the current Tempo docs first when chain details, packages, routes, or examples matter
- plan first
- default examples to Moderato testnet unless the user explicitly wants mainnet
- enforce policy limits before mutable actions
- make unknowns explicit
- give Codex concrete files to edit instead of vague prose

## Workflow
1. Confirm whether the user wants:
   - generic chain integration
   - Tempo Transactions and stablecoin payments
   - MPP client or agent work
   - MPP server or session billing work
2. Load only the relevant references:
   - `references/tempo-notes.md` for current network and product facts
   - `references/tempo-docs-index.md` for doc routing
   - `references/tempo-machine-payments.md` for MPP-specific guidance
3. If writing code:
   - use Tempo network config from `src/config/tempo.ts`
   - keep mutable actions behind explicit confirmation or policy gates
   - prefer official Tempo SDK surfaces when the target repo already depends on them
4. If the user is setting up agentic payments:
   - prefer the Tempo CLI path first for zero-integration workflows
   - use `mppx` for client/server SDK work
   - call out whether the flow is `charge` or `session`

## Reference map
- Network details, RPC URLs, explorer URLs, docs routes: `references/tempo-notes.md`
- Current doc navigation: `references/tempo-docs-index.md`
- MPP quickstarts and decision rules: `references/tempo-machine-payments.md`
- Shared constants and routing helpers: `src/config/tempo.ts`, `src/docs/tempoDocs.ts`
- Payment/policy scaffolding: `src/payments/*`, `src/policy/*`, `src/sponsorship/*`
- Installable skill metadata: `agents/openai.yaml`
- Runnable MPP example project: `examples/mpp-demo/`

## Good outputs from this skill
- a runnable or near-runnable TypeScript scaffold
- a short implementation plan with explicit unknowns
- a payment helper with policy gates
- an MPP client/server/agent starter grounded in official docs
- docs links and MCP hooks for Codex/Hermes
- a clear explanation of Tempo-specific semantics
