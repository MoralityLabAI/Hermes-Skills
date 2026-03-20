#!/usr/bin/env bash
set -euo pipefail

CONFIG=configs/base_rl.yaml

echo "Launching Prime RL with ${CONFIG}"
prime rl run ${CONFIG}
