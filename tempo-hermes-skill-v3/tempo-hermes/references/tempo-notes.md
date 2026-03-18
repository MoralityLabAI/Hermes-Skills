# Tempo implementation notes

## Confirmed from current public docs
- Tempo is EVM-compatible and targets the Osaka EVM hard fork.
- Standard Ethereum JSON-RPC methods work.
- Tempo has no native gas token.
- Fees are denominated in USD and can be paid in USD-denominated TIP-20 tokens.
- Tempo recommends Tempo Transactions over regular Ethereum transactions.
- Mainnet docs list chain ID `4217`, HTTP RPC `https://rpc.tempo.xyz`, WS `wss://rpc.tempo.xyz`, and explorer `https://explore.tempo.xyz`.
- Moderato testnet docs list chain ID `42431`, HTTP RPC `https://rpc.moderato.tempo.xyz`, WS `wss://rpc.moderato.tempo.xyz`, and explorer `https://explore.testnet.tempo.xyz`.
- Testnet faucet docs list:
  - pathUSD `0x20c0000000000000000000000000000000000000`
  - AlphaUSD `0x20c0000000000000000000000000000000000001`
  - BetaUSD `0x20c0000000000000000000000000000000000002`
  - ThetaUSD `0x20c0000000000000000000000000000000000003`
- The machine-payments docs position MPP as the HTTP payment layer on top of Tempo with:
  - `charge` for one-time on-chain payments
  - `session` for pay-as-you-go vouchers and channels
  - `tempo` CLI for terminal and agent usage
  - `mppx` for TypeScript client/server integration
- The AI docs expose `/llms.txt`, `/llms-full.txt`, Markdown page rendering with `.md`, and an MCP server at `https://docs.tempo.xyz/api/mcp`.

## Working posture for Codex/Hermes
- Treat MPP as separate from the Tempo transaction layer, but fully supported by this skill.
- Use policy checks before mutable actions.
- Prefer docs-assisted implementation over guessed viem/tempo action names.
- Prefer `tempo request` for no-code or agent-first flows.
- Prefer `mppx` for payment-gated HTTP clients or servers.
- Swap placeholder send paths with the exact current Tempo SDK action once the target repo chooses its dependency surface.
