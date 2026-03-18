# Tempo MPP demo

This is a small runnable MPP demo package inside the skill.

## What it contains
- `src/server.ts`: charge and session payment-gated handlers using `mppx/server`
- `src/devServer.ts`: local Node HTTP wrapper that exposes `GET/POST /paid` and `/session`
- `src/client.ts`: simple paid client using `mppx/client`

## Environment

Server:

```bash
set MPP_RECIPIENT=0xYOUR_ADDRESS
set MPP_PRICE=0.01
set MPP_SESSION_PRICE=0.01
set MPP_SESSION_UNIT_TYPE=request
set MPP_SUGGESTED_DEPOSIT=1
set MPP_CURRENCY_TOKEN=0x20c0000000000000000000000000000000000000
```

Client:

```bash
set TEMPO_PRIVATE_KEY=0xYOUR_PRIVATE_KEY
set MPP_RESOURCE_URL=http://localhost:3000/paid
set MPP_MAX_DEPOSIT=1
```

## Run it

```bash
npm install
npm run build
npm run smoke
npm run smoke:session
npm run start:server
```

In another terminal:

```bash
npm run start:client
```

To exercise the session path, point the client at:

```bash
set MPP_RESOURCE_URL=http://localhost:3000/session
npm run start:client
```

## Tempo CLI check

With the server running, you can inspect the payment challenge with:

```bash
npx mppx --inspect http://localhost:3000/paid
npx mppx --inspect http://localhost:3000/session
```

Or, if you want to test with the Tempo CLI against a public paid service, use the recipes in `../tempo_cli_agent_demo.md`.

`npm run smoke` is local-only: it starts the demo server, requests `/paid`, and verifies that the endpoint returns a valid `402 Payment Required` challenge.

`npm run smoke:session` does the same for `/session`, which verifies the session-based challenge path without spending funds.
