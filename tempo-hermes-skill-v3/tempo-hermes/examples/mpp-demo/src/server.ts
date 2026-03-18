import { Mppx, tempo } from 'mppx/server'

function requireEnv(name: string): string {
  const value = process.env[name]
  if (!value) throw new Error(`Missing ${name}`)
  return value
}

const mppx = Mppx.create({
  methods: [
    tempo({
      currency: process.env.MPP_CURRENCY_TOKEN ?? '0x20c0000000000000000000000000000000000000',
      recipient: requireEnv('MPP_RECIPIENT') as `0x${string}`,
    }),
  ],
})

export async function handler(request: Request) {
  const result = await mppx.charge({
    amount: process.env.MPP_PRICE ?? '0.01',
  })(request)

  if (result.status === 402) return result.challenge

  return result.withReceipt(
    Response.json({
      ok: true,
      settledOn: 'tempo',
      message: 'Paid resource unlocked.',
    }),
  )
}
