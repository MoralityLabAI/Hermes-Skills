#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/mnt/c/projects/GPTStoryworld}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
MODEL_NAME="${MODEL_NAME:-Qwen/Qwen2.5-1.5B}"
RUN_ROOT="${1:-}"
OUTPUT_DIR="${2:-$REPO_ROOT/hermes-skills/storyworld-conveyor/local_adapter_runs/qwen_adapter_run}"

if [[ -z "$RUN_ROOT" ]]; then
  RUN_ROOT="$(find "$REPO_ROOT/hermes-skills/storyworld-conveyor/factory_runs" -path '*/qlora/*/train_messages.jsonl' -printf '%h\n' | sort | tail -n 1)"
fi

if [[ -z "$RUN_ROOT" || ! -f "$RUN_ROOT/train_messages.jsonl" || ! -f "$RUN_ROOT/val_messages.jsonl" ]]; then
  echo "Could not find train_messages.jsonl / val_messages.jsonl. Provide a qlora dataset dir explicitly." >&2
  exit 2
fi

mkdir -p "$OUTPUT_DIR"

"$PYTHON_BIN" "$REPO_ROOT/hermes-skills/storyworld-conveyor/scripts/train_local_qwen_adapter.py" \
  --model-name "$MODEL_NAME" \
  --train-jsonl "$RUN_ROOT/train_messages.jsonl" \
  --val-jsonl "$RUN_ROOT/val_messages.jsonl" \
  --output-dir "$OUTPUT_DIR"

echo "[adapter-cycle] dataset_dir=$RUN_ROOT"
echo "[adapter-cycle] output_dir=$OUTPUT_DIR"
