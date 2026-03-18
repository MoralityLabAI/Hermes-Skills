import { formatReceiptSummary } from '../src/payments/receipts.js'
import { defaultPolicy } from '../src/policy/spendPolicy.js'
import { parseUnits } from 'viem'

const summary = formatReceiptSummary({
  transactionHash: '0x1111111111111111111111111111111111111111111111111111111111111111',
  token: '0x20c0000000000000000000000000000000000001',
  amount: parseUnits('100', 6),
  recipient: '0x000000000000000000000000000000000000dead',
  memo: 'invoice-42',
})

console.log(summary)
console.log(defaultPolicy())
