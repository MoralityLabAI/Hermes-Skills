#!/usr/bin/env bash
set -euo pipefail

ENV_NAME=toy_env
MODEL=qwen-9b

echo "Running Prime eval for ${ENV_NAME} with ${MODEL}"
prime eval run ${ENV_NAME} -m ${MODEL} -n 10 -r 2
