#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)}"
RUN_ROOT_LOCAL="${RUN_ROOT_LOCAL:-}"
ARTIFACT_SUBPATH="${ARTIFACT_SUBPATH:-}"
TERMINATE_POD="${TERMINATE_POD:-1}"
PEM_PATH="${PEM_PATH:-$HOME/.ssh/id_rsa}"

if [[ -z "$RUN_ROOT_LOCAL" ]]; then
  echo "RUN_ROOT_LOCAL is required" >&2
  exit 1
fi

cd "$ROOT"
export PYTHONPATH="$ROOT/src:${PYTHONPATH:-}"

if [[ -f .venv/bin/activate ]]; then
  source .venv/bin/activate
fi

CONNECTION_JSON="${RUN_ROOT_LOCAL}/connection.json"
if [[ ! -f "$CONNECTION_JSON" ]]; then
  echo "Missing connection metadata at $CONNECTION_JSON" >&2
  exit 1
fi

readarray -t CONN < <(python - <<PY
import json
from pathlib import Path

payload = json.loads(Path("${CONNECTION_JSON}").read_text(encoding="utf-8"))
print(payload["pod_id"])
print(payload["ssh_host"])
print(payload["ssh_port"])
print(payload["remote_root"])
print(payload["run_root_remote"])
PY
)

POD_ID="${CONN[0]}"
SSH_HOST="${CONN[1]}"
SSH_PORT="${CONN[2]}"
REMOTE_ROOT="${CONN[3]}"
RUN_ROOT_REMOTE="${CONN[4]}"

if [[ -z "$ARTIFACT_SUBPATH" ]]; then
  ARTIFACT_SUBPATH="${RUN_ROOT_REMOTE}"
fi

DEST_DIR="${RUN_ROOT_LOCAL}/artifacts"
mkdir -p "$DEST_DIR"

python - <<PY
from primelab_hermes.qlora_conveyor import append_receipt, write_stage_state
write_stage_state("${RUN_ROOT_LOCAL}", "exfiltrating", "running", pod_id="${POD_ID}", remote_path="${ARTIFACT_SUBPATH}")
append_receipt("${RUN_ROOT_LOCAL}", "exfiltrating", "running", pod_id="${POD_ID}", remote_path="${ARTIFACT_SUBPATH}")
PY

scp -r -o StrictHostKeyChecking=no -i "$PEM_PATH" -P "$SSH_PORT" root@"$SSH_HOST":"$ARTIFACT_SUBPATH" "$DEST_DIR/"

python - <<PY
from primelab_hermes.qlora_conveyor import append_receipt, write_stage_state
write_stage_state("${RUN_ROOT_LOCAL}", "archived", "artifacts_local", pod_id="${POD_ID}", artifact_dir="${DEST_DIR}")
append_receipt("${RUN_ROOT_LOCAL}", "archived", "artifacts_local", pod_id="${POD_ID}", artifact_dir="${DEST_DIR}")
PY

if [[ "$TERMINATE_POD" == "1" ]]; then
  prime pods terminate "$POD_ID" --yes
  python - <<PY
from primelab_hermes.qlora_conveyor import append_receipt, write_stage_state
write_stage_state("${RUN_ROOT_LOCAL}", "archived", "terminated", pod_id="${POD_ID}", artifact_dir="${DEST_DIR}")
append_receipt("${RUN_ROOT_LOCAL}", "archived", "terminated", pod_id="${POD_ID}", artifact_dir="${DEST_DIR}")
PY
fi

echo "POD_ID=${POD_ID}"
echo "LOCAL_ARTIFACT_DIR=${DEST_DIR}"
