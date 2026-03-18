# Tempo docs index

## Core chain docs
- Connect to the Network: mainnet and Moderato RPC, WS, chain IDs, explorers
- EVM Differences: no native gas token, wallet balance quirks
- Use Tempo Transactions: preferred tx type, fee tokens, sponsorship, batching, access keys, 2D and expiring nonces
- Send a Payment: TIP-20 transfer patterns, receipts, memos, batching
- Pay Fees in Any Stablecoin: explicit fee token handling

## Machine Payments docs
- Machine Payments: MPP overview, charge vs session, why Tempo fits inline payments
- Agent quickstart: `tempo` CLI install, login, service discovery, `tempo request --dry-run`
- Client quickstart: `mppx/client`, `Mppx.create`, `tempo({ account })`, fetch polyfill
- Server quickstart: `mppx` middleware for Next.js, Hono, Express, Fetch API
- Accept pay-as-you-go payments: `mppx.session`, off-chain vouchers, `maxDeposit`
- Accept one-time payments: `mppx.charge`, on-chain per-request settlement
- Accept streamed payments: SSE plus per-unit billing

## AI / agent docs
- Using Tempo with AI: docs grounding, wallet setup, agent usage
- `llms.txt` and `llms-full.txt`: machine-readable docs index
- Markdown rendering with `.md`
- MCP endpoint: Tempo docs MCP server
