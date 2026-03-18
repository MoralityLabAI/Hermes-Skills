# Tempo MPP quickstart snippets

## Agent / terminal flow

```bash
curl -fsSL https://tempo.xyz/install | bash
tempo wallet login
tempo wallet services --search ai
tempo request --dry-run -X POST --json '{"prompt":"hello"}' https://example.mpp.tempo.xyz/endpoint
```

## TypeScript client flow

```ts
import { Mppx, tempo } from 'mppx/client'
import { privateKeyToAccount } from 'viem/accounts'

const mppx = Mppx.create({
  polyfill: false,
  methods: [tempo({
    account: privateKeyToAccount(process.env.TEMPO_PRIVATE_KEY! as `0x${string}`),
    maxDeposit: '1',
  })],
})

const response = await mppx.fetch('https://example.mpp.tempo.xyz/endpoint')
```

## TypeScript server flow

```ts
import { Mppx, tempo } from 'mppx/server'

const mppx = Mppx.create({
  methods: [tempo({
    currency: '0x20c0000000000000000000000000000000000000',
    recipient: '0x000000000000000000000000000000000000dead',
  })],
})

export async function handler(request: Request) {
  const result = await mppx.charge({ amount: '0.01' })(request)
  if (result.status === 402) return result.challenge
  return result.withReceipt(Response.json({ ok: true }))
}
```
