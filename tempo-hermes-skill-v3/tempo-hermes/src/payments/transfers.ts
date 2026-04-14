import { encodeFunctionData, erc20Abi, pad, parseUnits, stringToHex } from 'viem'
import { createTempoWalletClient } from '../rpc/client.js'
import { assertSpendAllowed, defaultPolicy, type SpendLedger, type SpendPolicy } from '../policy/spendPolicy.js'
import { TEMPO_MODERATO } from '../config/tempo.js'

export type TransferRequest = {
  privateKey: `0x${string}`
  token: `0x${string}`
  recipient: `0x${string}`
  humanAmount: string
  decimals?: number
  feeToken?: `0x${string}`
  memo?: string
  policy?: SpendPolicy
  ledger?: SpendLedger
  broadcastConfirmed?: boolean
}

export function normalizeTempoMemo(memo?: string): `0x${string}` | undefined {
  if (!memo) return undefined
  if (Buffer.byteLength(memo, "utf8") > 32) {
    throw new Error("Tempo memo must be at most 32 bytes.")
  }
  const hex = stringToHex(memo)
  return pad(hex, { size: 32 })
}

export function buildTransferCalldata(recipient: `0x${string}`, humanAmount: string, decimals = 6): `0x${string}` {
  const amount = parseUnits(humanAmount, decimals)
  return encodeFunctionData({
    abi: erc20Abi,
    functionName: 'transfer',
    args: [recipient, amount],
  })
}

export async function sendTip20Transfer(req: TransferRequest) {
  const policy = req.policy ?? defaultPolicy()
  const ledger = req.ledger ?? { spentTodayUnits: 0n }
  const amount = parseUnits(req.humanAmount, req.decimals ?? 6)

  assertSpendAllowed({
    amount,
    recipient: req.recipient,
    policy,
    ledger,
    broadcastConfirmed: req.broadcastConfirmed ?? false,
  })

  const client = createTempoWalletClient(req.privateKey)
  const normalizedMemo = normalizeTempoMemo(req.memo)
  const transaction: Record<string, unknown> = {
    to: req.token,
    data: buildTransferCalldata(req.recipient, req.humanAmount, req.decimals ?? 6),
  }

  if (req.feeToken) {
    transaction.feeToken = req.feeToken
  }
  if (normalizedMemo) {
    transaction.memo = normalizedMemo
  }

  // NOTE:
  // Tempo docs recommend Tempo Transactions and fee-token-aware mutable actions.
  // This starter uses a plain wallet sendTransaction shape as a conservative scaffold.
  // Codex should swap this to the current viem/tempo action or SDK helper the project chooses.
  const hash = await client.sendTransaction(transaction as any)

  return {
    transactionHash: hash,
    token: req.token,
    amount,
    recipient: req.recipient,
    memo: req.memo,
    network: TEMPO_MODERATO.name,
  }
}
