#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/mnt/c/projects/GPTStoryworld}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
BATCH_DIR="${BATCH_DIR:-$REPO_ROOT/storyworlds/3-5-2026-morality-constitutions-batch-v1}"
RUNS="${RUNS:-200}"

cd "$REPO_ROOT"

"$PYTHON_BIN" "$REPO_ROOT/tools/gen_morality_constitution_batch.py"

OUT_REPORT="$BATCH_DIR/_reports/routing_probe_smoke.json"
"$PYTHON_BIN" "$REPO_ROOT/tools/probe_morality_batch_routing.py" \
  --batch-dir "$BATCH_DIR" \
  --runs "$RUNS" \
  --out "$OUT_REPORT"

echo "[moral-smoke] batch_dir=$BATCH_DIR"
echo "[moral-smoke] routing_report=$OUT_REPORT"
