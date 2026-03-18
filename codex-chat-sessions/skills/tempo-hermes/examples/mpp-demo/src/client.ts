import { Mppx, tempo } from 'mppx/client'
import { privateKeyToAccount } from 'viem/accounts'

function requireEnv(name: string): string {
  const value = process.env[name]
  if (!value) throw new Error(`Missing ${name}`)
  return value
}

const mppx = Mppx.create({
  polyfill: false,
  methods: [
    tempo({
      account: privateKeyToAccount(requireEnv('TEMPO_PRIVATE_KEY') as `0x${string}`),
      maxDeposit: process.env.MPP_MAX_DEPOSIT ?? '1',
    }),
  ],
})

const url = process.env.MPP_RESOURCE_URL ?? 'http://localhost:3000/paid'

async function main() {
  const response = await mppx.fetch(url, {
    headers: {
      'content-type': 'application/json',
    },
  })

  console.log(`status=${response.status}`)
  console.log(await response.text())
}

main().catch((err) => {
  console.error(err)
  process.exitCode = 1
})
