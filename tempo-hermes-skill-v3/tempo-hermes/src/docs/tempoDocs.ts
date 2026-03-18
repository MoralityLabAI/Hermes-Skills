import { TEMPO_MODERATO, docMarkdownUrl } from '../config/tempo.js'

export const tempoDocHints = {
  llmsIndex: TEMPO_MODERATO.docsLlmsIndexUrl,
  llmsFull: TEMPO_MODERATO.docsLlmsFullUrl,
  mcp: TEMPO_MODERATO.docsMcpUrl,
  pages: {
    connect: docMarkdownUrl('quickstart/connection-details'),
    evmDifferences: docMarkdownUrl('quickstart/evm-compatibility'),
    tempoTransactions: docMarkdownUrl('guide/tempo-transaction'),
    sendPayment: docMarkdownUrl('guide/payments/send-a-payment'),
    feeTokens: docMarkdownUrl('guide/payments/pay-fees-in-any-stablecoin'),
    machinePayments: docMarkdownUrl('guide/machine-payments'),
    mppAgent: docMarkdownUrl('guide/machine-payments/agent'),
    mppClient: docMarkdownUrl('guide/machine-payments/client'),
    mppServer: docMarkdownUrl('guide/machine-payments/server'),
    mppSession: docMarkdownUrl('guide/machine-payments/pay-as-you-go'),
    ai: docMarkdownUrl('guide/using-tempo-with-ai'),
  },
} as const

export function renderDocsRoutingNote(): string {
  return [
    `llms.txt: ${tempoDocHints.llmsIndex}`,
    `llms-full.txt: ${tempoDocHints.llmsFull}`,
    `MCP: ${tempoDocHints.mcp}`,
    `connect docs: ${tempoDocHints.pages.connect}`,
    `payments docs: ${tempoDocHints.pages.sendPayment}`,
    `mpp overview: ${tempoDocHints.pages.machinePayments}`,
    `mpp client: ${tempoDocHints.pages.mppClient}`,
    `mpp server: ${tempoDocHints.pages.mppServer}`,
    `ai docs: ${tempoDocHints.pages.ai}`,
  ].join('\n')
}
