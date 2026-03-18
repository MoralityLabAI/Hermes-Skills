import { explorerTxUrl } from '../config/tempo.js'

export type TempoReceiptSummary = {
  transactionHash: `0x${string}`
  token: `0x${string}`
  amount: bigint
  recipient: `0x${string}`
  memo?: string
}

export function formatReceiptSummary(receipt: TempoReceiptSummary): string {
  const parts = [
    `tx=${receipt.transactionHash}`,
    `explorer=${explorerTxUrl(receipt.transactionHash)}`,
    `token=${receipt.token}`,
    `amount=${receipt.amount.toString()}`,
    `recipient=${receipt.recipient}`,
  ]
  if (receipt.memo) parts.push(`memo=${receipt.memo}`)
  return parts.join(' | ')
}
