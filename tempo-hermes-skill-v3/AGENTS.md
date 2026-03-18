# Tempo Hermes Skill Use Cases

This project contains the `tempo-hermes` skill for Hermes/Codex.

## When to use this skill

Use `tempo-hermes` when the task involves any of these:
- connecting to the Tempo blockchain on mainnet or Moderato testnet
- working with Tempo Transactions instead of plain Ethereum transaction flows
- TIP-20 stablecoin payments, transfer memos, fee-token selection, or sponsorship
- MPP machine-payments client, server, or agent integrations on Tempo
- Tempo CLI workflows such as `tempo wallet`, `tempo request`, or paid service discovery
- routing an agent to the current Tempo docs, `llms.txt`, or Tempo docs MCP

## Typical user requests this skill should handle

- "Create a Hermes skill for Tempo."
- "Set up a Tempo payment flow with AlphaUSD or pathUSD."
- "Build an MPP client that can pay `402 Payment Required` endpoints on Tempo."
- "Add a payment-gated server route for MCP or API usage on Tempo."
- "Show how to use `tempo request --dry-run` before a paid call."
- "Explain how Tempo differs from Ethereum wallets and gas handling."
- "Plan a Tempo integration that uses fee sponsorship or session billing."

## What the skill is good at producing

- docs-grounded integration plans
- TypeScript scaffolds for Tempo RPC and payment work
- MPP charge or session demo code
- Tempo CLI and agent usage recipes
- safe guidance that distinguishes Tempo chain mechanics from MPP protocol flows

## Important boundaries

- Do not treat `eth_getBalance` as real spendable ETH on Tempo.
- Do not invent unsupported MPP semantics or Tempo mainnet assumptions.
- Prefer current official Tempo docs over memory when chain details or package usage matter.
