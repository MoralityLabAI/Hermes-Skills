# Tempo machine-payments notes

## When to use what
- Use `tempo request` and `tempo wallet` when the user wants a terminal or AI-agent workflow with minimal integration code.
- Use `mppx/client` when the user wants an app or script to pay `402 Payment Required` challenges automatically.
- Use `mppx/server` or framework middleware when the user wants to gate HTTP endpoints behind Tempo-based payments.
- Use `charge` for one-off calls with on-chain settlement.
- Use `session` for metered APIs, repeated requests, or streamed responses where off-chain vouchers matter.

## Confirmed doc facts
- MPP on Tempo uses the standard HTTP payment loop:
  - client request
  - server returns `402` plus payment challenge
  - client fulfills payment
  - client retries with payment credential
  - server verifies and returns the resource plus a receipt
- Tempo docs highlight these fit reasons:
  - deterministic finality around 500ms
  - sub-cent fees
  - fee sponsorship
  - 2D and expiring nonces
  - throughput suitable for payment-channel settlement
- Agent quickstart:
  - install with `curl -fsSL https://tempo.xyz/install | bash`
  - authenticate with `tempo wallet login`
  - inspect services with `tempo wallet services`
  - preview cost with `tempo request --dry-run`
- TypeScript client quickstart:
  - install `mppx` and `viem`
  - call `Mppx.create({ methods: [tempo({ account })] })`
  - use `fetch` or `mppx.fetch`
- TypeScript server quickstart:
  - create `Mppx` instance with `tempo({ currency, recipient })`
  - use `mppx.charge(...)` or `mppx.session(...)`
  - `feePayer` is relevant for pull-mode requests
- Session guide:
  - channel opens on-chain
  - repeated requests use off-chain vouchers
  - `maxDeposit` caps escrowed funds on the client

## Guardrails
- Do not blur `charge` and `session`; they have different UX, settlement, and verification behavior.
- Do not invent supported tokens; use the official payment-method docs or Tempo docs.
- Do not assume fee sponsorship applies to push-mode MPP clients.
- Do not describe MPP as replacing Tempo Transactions; MPP uses Tempo for settlement.
