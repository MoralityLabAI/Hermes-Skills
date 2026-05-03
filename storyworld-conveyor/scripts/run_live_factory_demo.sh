#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <base_world_wsl> <out_config_wsl> [run_id_prefix] [iterations]" >&2
  exit 2
fi

BASE_WORLD="$1"
OUT_CONFIG="$2"
RUN_ID_PREFIX="${3:-live_demo}"
ITERATIONS="${4:-10}"

REPO_ROOT="${REPO_ROOT:-/mnt/c/projects/GPTStoryworld}"
CONVEYOR_ROOT="$REPO_ROOT/hermes-skills/storyworld-conveyor"

cd "$CONVEYOR_ROOT"

python3 scripts/make_factory_config.py \
  --template fresh_seed_artistry \
  --base-world "$BASE_WORLD" \
  --out-config "$OUT_CONFIG" \
  --run-id "${RUN_ID_PREFIX}_seed" \
  --title "Storyworld Live Conveyor Demo" \
  --about "A generated factory config for visible artifact-first conveyor execution." \
  --motif "Every scene leaves a measurable trace on the next choice." \
  --target-encounters 40 \
  --ending-count 4 \
  --secret-ending-count 2 \
  --super-secret-count 1 \
  --avg-options 3.2 \
  --avg-reactions 2.5 \
  --avg-effects 4.5 \
  --include-monte-carlo \
  --include-encounter-index

echo "[demo] generated_config=$OUT_CONFIG"

python3 scripts/run_factory_grind.py \
  --config "$OUT_CONFIG" \
  --run-id-prefix "$RUN_ID_PREFIX" \
  --iterations "$ITERATIONS" \
  --tail-lines 6 \
  --force
