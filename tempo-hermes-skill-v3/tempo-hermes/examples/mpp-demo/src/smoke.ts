import { spawn, type ChildProcess } from 'node:child_process'

const port = 3100 + Math.floor(Math.random() * 1000)
const baseUrl = `http://127.0.0.1:${port}`
const path = process.argv.includes('--session') ? '/session' : '/paid'

function startServer(): Promise<ChildProcess> {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, ['dist/devServer.js'], {
      cwd: process.cwd(),
      env: {
        ...process.env,
        PORT: String(port),
        MPP_PRICE: '0.01',
        MPP_RECIPIENT: '0x000000000000000000000000000000000000dEaD',
        MPP_CURRENCY_TOKEN: '0x20c0000000000000000000000000000000000000',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    })

    let settled = false
    child.stderr?.on('data', (chunk) => {
      process.stderr.write(chunk)
    })

    child.on('exit', (code) => {
      if (settled) return
      settled = true
      if (code !== null && code !== 0) {
        reject(new Error(`Demo server exited early with code ${code}`))
      }
    })

    void waitForServer(child)
      .then(() => {
        if (settled) return
        settled = true
        resolve(child)
      })
      .catch((error) => {
        if (settled) return
        settled = true
        child.kill()
        reject(error)
      })
  })
}

async function waitForServer(child: ChildProcess): Promise<void> {
  const deadline = Date.now() + 10000

  while (Date.now() < deadline) {
    if (child.exitCode !== null) {
      throw new Error(`Demo server exited early with code ${child.exitCode}`)
    }

    try {
      const response = await fetch(`${baseUrl}${path}`, { redirect: 'manual' })
      if (response.status > 0) return
    } catch {
      // Server is not ready yet.
    }

    await new Promise((resolve) => setTimeout(resolve, 200))
  }

  throw new Error('Timed out waiting for demo server to start')
}

async function stopServer(child: ChildProcess): Promise<void> {
  await new Promise<void>((resolve) => {
    child.once('exit', () => resolve())
    child.kill()
  })
}

async function main() {
  const child = await startServer()

  try {
    const response = await fetch(`${baseUrl}${path}`)
    const authenticate = response.headers.get('www-authenticate')

    if (response.status !== 402) {
      throw new Error(`Expected 402, got ${response.status}`)
    }

    if (!authenticate || !authenticate.toLowerCase().includes('payment')) {
      throw new Error('Missing payment challenge in www-authenticate header')
    }

    console.log(`Smoke test passed: local MPP demo returned a payment challenge for ${path}.`)
  } finally {
    await stopServer(child)
  }
}

main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
