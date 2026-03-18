import { sendTip20Transfer } from '../src/payments/transfers.js'

async function main() {
  const privateKey = process.env.TEMPO_PRIVATE_KEY as `0x${string}`
  if (!privateKey) throw new Error('Missing TEMPO_PRIVATE_KEY')

  const result = await sendTip20Transfer({
    privateKey,
    token: '0x20c0000000000000000000000000000000000001',
    recipient: '0x000000000000000000000000000000000000dead',
    humanAmount: '100',
    memo: 'invoice-42',
    feeToken: '0x20c0000000000000000000000000000000000001',
    broadcastConfirmed: true,
  })

  console.log(result)
}

main().catch((err) => {
  console.error(err)
  process.exitCode = 1
})
