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

export async function chargeHandler(request: Request) {
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

export async function sessionHandler(request: Request) {
  const result = await mppx.session({
    amount: process.env.MPP_SESSION_PRICE ?? '0.01',
    unitType: process.env.MPP_SESSION_UNIT_TYPE ?? 'request',
    suggestedDeposit: process.env.MPP_SUGGESTED_DEPOSIT ?? '1',
  })(request)

  if (result.status === 402) return result.challenge

  return result.withReceipt(
    Response.json({
      ok: true,
      settledOn: 'tempo',
      mode: 'session',
      message: 'Session-based paid resource unlocked.',
    }),
  )
}

export const handler = chargeHandler
