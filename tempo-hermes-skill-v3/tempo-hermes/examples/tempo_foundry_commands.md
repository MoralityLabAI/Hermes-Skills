# Tempo Foundry / cast snippets

```bash
cast block-number --rpc-url https://rpc.tempo.xyz
cast chain-id --rpc-url https://rpc.tempo.xyz
cast block-number --rpc-url https://rpc.moderato.tempo.xyz
cast chain-id --rpc-url https://rpc.moderato.tempo.xyz
```

Use the mainnet commands when validating launch-chain connectivity. Use the Moderato commands when testing faucet-funded flows.

For testnet funding:

```bash
cast rpc tempo_fundAddress <YOUR_ADDRESS> --rpc-url https://rpc.moderato.tempo.xyz
```
