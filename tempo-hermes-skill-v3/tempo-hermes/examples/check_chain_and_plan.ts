import { assertTempoChain, createTempoPublicClient } from '../src/rpc/client.js'
import { renderDocsRoutingNote } from '../src/docs/tempoDocs.js'

async function main() {
  const client = createTempoPublicClient()
  const chainId = await assertTempoChain(client)
  console.log(`Connected to Tempo chain ${chainId}`)
  console.log(renderDocsRoutingNote())
}

main().catch((err) => {
  console.error(err)
  process.exitCode = 1
})
