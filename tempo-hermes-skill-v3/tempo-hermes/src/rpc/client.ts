import { createPublicClient, createWalletClient, http } from 'viem'
import { privateKeyToAccount } from 'viem/accounts'
import { tempoModerato } from 'viem/chains'
import { TEMPO_MODERATO } from '../config/tempo.js'

export function createTempoPublicClient(rpcUrl: string = TEMPO_MODERATO.httpRpcUrl) {
  return createPublicClient({
    chain: tempoModerato,
    transport: http(rpcUrl),
  })
}

export function createTempoWalletClient(privateKey: `0x${string}`, rpcUrl: string = TEMPO_MODERATO.httpRpcUrl) {
  const account = privateKeyToAccount(privateKey)
  return createWalletClient({
    account,
    chain: tempoModerato,
    transport: http(rpcUrl),
  })
}

export async function assertTempoChain(publicClient = createTempoPublicClient()) {
  const chainId = await publicClient.getChainId()
  if (chainId !== TEMPO_MODERATO.chainId) {
    throw new Error(`Unexpected chain id: ${chainId}. Expected ${TEMPO_MODERATO.chainId}.`)
  }
  return chainId
}
