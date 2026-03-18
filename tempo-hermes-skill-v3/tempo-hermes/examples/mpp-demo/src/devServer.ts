import { createServer } from 'node:http'
import { NodeListener } from 'mppx/server'
import { handler } from './server.js'

const port = Number(process.env.PORT ?? 3000)

async function toRequest(req: import('node:http').IncomingMessage): Promise<Request> {
  const origin = `http://${req.headers.host ?? `localhost:${port}`}`
  const url = new URL(req.url ?? '/', origin)
  const body =
    req.method === 'GET' || req.method === 'HEAD'
      ? undefined
      : await readBody(req)

  return new Request(url, {
    method: req.method,
    headers: new Headers(req.headers as Record<string, string>),
    body: body ? new Uint8Array(body) : undefined,
  })
}

async function readBody(req: import('node:http').IncomingMessage): Promise<Buffer> {
  const chunks: Buffer[] = []
  for await (const chunk of req) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk))
  }
  return Buffer.concat(chunks)
}

const server = createServer(async (req, res) => {
  try {
    if ((req.url ?? '/') !== '/paid') {
      await NodeListener.sendResponse(res, new Response('Not Found', { status: 404 }))
      return
    }

    const request = await toRequest(req)
    const response = await handler(request)
    await NodeListener.sendResponse(res, response)
  } catch (error) {
    console.error(error)
    await NodeListener.sendResponse(res, Response.json({ error: 'Internal Server Error' }, { status: 500 }))
  }
})

server.listen(port, () => {
  console.log(`Tempo MPP demo listening on http://localhost:${port}/paid`)
})
