#!/usr/bin/env bash
set -euo pipefail
RPC_URL="${1:-https://rpc.moderato.tempo.xyz}"
echo "Checking Tempo RPC: $RPC_URL"
curl -sS -X POST "$RPC_URL" -H 'content-type: application/json' --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
echo
curl -sS -X POST "$RPC_URL" -H 'content-type: application/json' --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":2}'
echo
