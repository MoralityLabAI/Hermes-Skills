# Tempo CLI and agent demo

## Install and authenticate

```bash
curl -fsSL https://tempo.xyz/install | bash
tempo wallet login
tempo wallet whoami
```

If the wallet has no spendable stablecoins yet, fund it on testnet:

```bash
tempo wallet fund
```

## Discover paid services

```bash
tempo wallet services --search ai
tempo wallet services <SERVICE_ID>
```

Use the service detail output to confirm:
- endpoint URL
- HTTP method
- expected payload
- pricing

## Preview payment cost

```bash
tempo request --dry-run -X POST \
  --json '{"prompt":"a sunset over the ocean"}' \
  https://fal.mpp.tempo.xyz/fal-ai/flux/dev
```

## Make the paid request

```bash
tempo request -X POST \
  --json '{"prompt":"a sunset over the ocean"}' \
  https://fal.mpp.tempo.xyz/fal-ai/flux/dev
```

## Agent invocation

Use this exact prompt in an agent that supports Codex-style skill setup:

```txt
Read https://tempo.xyz/SKILL.md and set up tempo
```

After setup, ask the agent to:
- search for a service with `tempo wallet services`
- run `tempo request --dry-run`
- make a paid call only after showing the expected spend
