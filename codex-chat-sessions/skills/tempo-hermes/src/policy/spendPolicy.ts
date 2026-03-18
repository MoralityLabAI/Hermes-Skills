export type SpendPolicy = {
  maxUnitsPerTransfer: bigint
  maxDailyUnits: bigint
  allowedRecipients?: Set<`0x${string}`>
  requireExplicitBroadcast: boolean
}

export type SpendLedger = {
  spentTodayUnits: bigint
}

export function defaultPolicy(): SpendPolicy {
  return {
    maxUnitsPerTransfer: 1_000_000n,
    maxDailyUnits: 5_000_000n,
    requireExplicitBroadcast: true,
  }
}

export function assertSpendAllowed(params: {
  amount: bigint
  recipient: `0x${string}`
  policy: SpendPolicy
  ledger: SpendLedger
  broadcastConfirmed: boolean
}) {
  const { amount, recipient, policy, ledger, broadcastConfirmed } = params

  if (policy.requireExplicitBroadcast && !broadcastConfirmed) {
    throw new Error('Broadcast blocked by policy: explicit confirmation required.')
  }
  if (amount > policy.maxUnitsPerTransfer) {
    throw new Error(`Transfer amount ${amount} exceeds per-transfer limit ${policy.maxUnitsPerTransfer}.`)
  }
  if (ledger.spentTodayUnits + amount > policy.maxDailyUnits) {
    throw new Error('Transfer exceeds daily spend budget.')
  }
  if (policy.allowedRecipients && !policy.allowedRecipients.has(recipient)) {
    throw new Error(`Recipient ${recipient} is not allowlisted.`)
  }
}
