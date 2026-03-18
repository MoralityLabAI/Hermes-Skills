export type TempoNetworkConfig = {
  readonly name: string
  readonly chainId: number
  readonly currencySymbol: 'USD'
  readonly httpRpcUrl: string
  readonly wsRpcUrl: string
  readonly explorerBaseUrl: string
  readonly sponsorUrl?: string
  readonly docsBaseUrl: string
  readonly docsMcpUrl: string
  readonly docsLlmsIndexUrl: string
  readonly docsLlmsFullUrl: string
  readonly pathUsd: `0x${string}`
  readonly alphaUsd: `0x${string}`
  readonly betaUsd: `0x${string}`
  readonly thetaUsd: `0x${string}`
}

const DOCS_BASE_URL = 'https://docs.tempo.xyz'
const DOCS_MCP_URL = `${DOCS_BASE_URL}/api/mcp`
const DOCS_LLMS_INDEX_URL = `${DOCS_BASE_URL}/llms.txt`
const DOCS_LLMS_FULL_URL = `${DOCS_BASE_URL}/llms-full.txt`

export const TEMPO_MAINNET: TempoNetworkConfig = {
  name: 'Tempo Mainnet',
  chainId: 4217,
  currencySymbol: 'USD',
  httpRpcUrl: 'https://rpc.tempo.xyz',
  wsRpcUrl: 'wss://rpc.tempo.xyz',
  explorerBaseUrl: 'https://explore.tempo.xyz',
  docsBaseUrl: DOCS_BASE_URL,
  docsMcpUrl: DOCS_MCP_URL,
  docsLlmsIndexUrl: DOCS_LLMS_INDEX_URL,
  docsLlmsFullUrl: DOCS_LLMS_FULL_URL,
  pathUsd: '0x20c0000000000000000000000000000000000000',
  alphaUsd: '0x20c0000000000000000000000000000000000001',
  betaUsd: '0x20c0000000000000000000000000000000000002',
  thetaUsd: '0x20c0000000000000000000000000000000000003',
}

export const TEMPO_MODERATO: TempoNetworkConfig = {
  name: 'Tempo Testnet (Moderato)',
  chainId: 42431,
  currencySymbol: 'USD',
  httpRpcUrl: 'https://rpc.moderato.tempo.xyz',
  wsRpcUrl: 'wss://rpc.moderato.tempo.xyz',
  explorerBaseUrl: 'https://explore.testnet.tempo.xyz',
  sponsorUrl: 'https://sponsor.moderato.tempo.xyz',
  docsBaseUrl: DOCS_BASE_URL,
  docsMcpUrl: DOCS_MCP_URL,
  docsLlmsIndexUrl: DOCS_LLMS_INDEX_URL,
  docsLlmsFullUrl: DOCS_LLMS_FULL_URL,
  pathUsd: '0x20c0000000000000000000000000000000000000',
  alphaUsd: '0x20c0000000000000000000000000000000000001',
  betaUsd: '0x20c0000000000000000000000000000000000002',
  thetaUsd: '0x20c0000000000000000000000000000000000003',
}

export function explorerTxUrl(hash: `0x${string}`, network: TempoNetworkConfig = TEMPO_MODERATO): string {
  return `${network.explorerBaseUrl}/tx/${hash}`
}

export function docMarkdownUrl(path: string): string {
  const trimmed = path.startsWith('/') ? path.slice(1) : path
  return `${DOCS_BASE_URL}/${trimmed}.md`
}
