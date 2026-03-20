#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)}"
SPEC_JSON="${SPEC_JSON:-configs/qlora_conveyor.example.json}"
RUN_ID="${RUN_ID:-qlora-$(date +%Y%m%d-%H%M%S)}"
POD_NAME="${POD_NAME:-${RUN_ID}}"
POD_IMAGE="${POD_IMAGE:-cuda_12_4_pytorch_2_4}"
POD_DISK_GB="${POD_DISK_GB:-160}"
POD_VCPUS="${POD_VCPUS:-}"
POD_MEMORY_GB="${POD_MEMORY_GB:-}"
PRIME_GPU_TYPE="${PRIME_GPU_TYPE:-A6000_48GB}"
PEM_PATH="${PEM_PATH:-$HOME/.ssh/id_rsa}"
REMOTE_ROOT="${REMOTE_ROOT:-/workspace/primelab-hermes}"
RUN_ROOT_LOCAL="${RUN_ROOT_LOCAL:-runs/qlora_conveyor/${RUN_ID}}"
DATA_ROOT_LOCAL="${DATA_ROOT_LOCAL:-data/qlora_conveyor/${RUN_ID}}"
RUN_ROOT_REMOTE="${RUN_ROOT_REMOTE:-${REMOTE_ROOT}/runs/qlora_conveyor/${RUN_ID}}"
DATA_ROOT_REMOTE="${DATA_ROOT_REMOTE:-${REMOTE_ROOT}/${DATA_ROOT_LOCAL}}"
BUNDLE_LOCAL="${BUNDLE_LOCAL:-${RUN_ROOT_LOCAL}/qlora_bundle.tar.gz}"

cd "$ROOT"
export PYTHONPATH="$ROOT/src:${PYTHONPATH:-}"

if [[ -f .venv/bin/activate ]]; then
  source .venv/bin/activate
fi

if [[ -z "${PRIME_API_KEY:-}" ]]; then
  if [[ -f "$HOME/.prime/config.json" ]]; then
    export PRIME_API_KEY="$(python - <<'PY'
import json
from pathlib import Path

cfg = Path.home() / ".prime" / "config.json"
print(json.loads(cfg.read_text(encoding="utf-8"))["api_key"])
PY
)"
  fi
fi

if [[ -z "${PRIME_API_KEY:-}" ]]; then
  echo "PRIME_API_KEY is required" >&2
  exit 1
fi

mkdir -p "$RUN_ROOT_LOCAL" "$DATA_ROOT_LOCAL"

python - <<PY
from primelab_hermes.qlora_conveyor import append_receipt, write_stage_state
write_stage_state("${RUN_ROOT_LOCAL}", "bootstrapping", "running", spec_json="${SPEC_JSON}")
append_receipt("${RUN_ROOT_LOCAL}", "bootstrapping", "running", spec_json="${SPEC_JSON}")
PY

python scripts/build_qlora_dataset.py --spec-json "$SPEC_JSON" --out-root "$DATA_ROOT_LOCAL"
python scripts/stage_qlora_bundle.py --root "$ROOT" --spec-json "$SPEC_JSON" --data-root "$DATA_ROOT_LOCAL" --out "$BUNDLE_LOCAL"

python - <<PY
from primelab_hermes.qlora_conveyor import append_receipt, write_stage_state
write_stage_state("${RUN_ROOT_LOCAL}", "fetching", "ready", bundle="${BUNDLE_LOCAL}", data_root="${DATA_ROOT_LOCAL}")
append_receipt("${RUN_ROOT_LOCAL}", "fetching", "ready", bundle="${BUNDLE_LOCAL}", data_root="${DATA_ROOT_LOCAL}")
PY

POD_ID_SHORT="$(
  prime availability list --gpu-type "$PRIME_GPU_TYPE" --output json | python -c '
import json, sys
data = json.load(sys.stdin)
rows = [r for r in data.get("gpu_resources", []) if r.get("gpu_count") == 1]
if not rows:
    raise SystemExit(1)
rows = sorted(rows, key=lambda r: (r.get("price_value", 9999), r.get("id", "")))
print(rows[0]["id"])
'
)"

python - <<'PY'
import json
import os
from pathlib import Path
import urllib.request

api_key = os.environ["PRIME_API_KEY"]
pub_path = Path.home() / ".ssh" / "id_rsa.pub"
if not pub_path.exists():
    raise SystemExit(f"Missing Prime SSH public key at {pub_path}")
pub = pub_path.read_text(encoding="utf-8").strip()

req = urllib.request.Request(
    "https://api.primeintellect.ai/api/v1/ssh_keys/",
    headers={"Authorization": f"Bearer {api_key}"},
)
with urllib.request.urlopen(req, timeout=30) as resp:
    payload = json.loads(resp.read().decode("utf-8"))

rows = payload.get("data", [])
if any(row.get("publicKey") == pub for row in rows):
    print("Prime SSH key already registered")
    raise SystemExit(0)

create_req = urllib.request.Request(
    "https://api.primeintellect.ai/api/v1/ssh_keys/",
    data=json.dumps({"name": "primelab-hermes-id-rsa", "publicKey": pub}).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    method="POST",
)
with urllib.request.urlopen(create_req, timeout=30) as resp:
    created = json.loads(resp.read().decode("utf-8"))
key_id = created["id"]

patch_req = urllib.request.Request(
    f"https://api.primeintellect.ai/api/v1/ssh_keys/{key_id}",
    data=json.dumps({"isPrimary": True}).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    method="PATCH",
)
with urllib.request.urlopen(patch_req, timeout=30) as resp:
    json.loads(resp.read().decode("utf-8"))
print(f"Registered Prime SSH key {key_id}")
PY

CREATE_CMD=(prime pods create --id "$POD_ID_SHORT" --name "$POD_NAME" --disk-size "$POD_DISK_GB" --image "$POD_IMAGE" --yes)
if [[ -n "$POD_VCPUS" ]]; then
  CREATE_CMD+=(--vcpus "$POD_VCPUS")
fi
if [[ -n "$POD_MEMORY_GB" ]]; then
  CREATE_CMD+=(--memory "$POD_MEMORY_GB")
fi
"${CREATE_CMD[@]}"

POD_ID="$(prime pods list --output json | python -c 'import json,sys; data=json.load(sys.stdin); print(data["pods"][-1]["id"])')"

SSH_CONN=""
for _ in $(seq 1 60); do
  SSH_CONN="$(prime pods status "$POD_ID" --output json | python -c 'import json,sys; data=json.load(sys.stdin); print(data.get("ssh",""))')"
  if [[ -n "$SSH_CONN" && "$SSH_CONN" != "N/A" ]]; then
    break
  fi
  sleep 10
done

if [[ -z "$SSH_CONN" || "$SSH_CONN" == "N/A" ]]; then
  echo "SSH connection was not published for pod ${POD_ID}" >&2
  exit 1
fi

SSH_HOST="${SSH_CONN%% -p *}"
SSH_PORT="${SSH_CONN##* -p }"
if [[ "$SSH_PORT" == "$SSH_CONN" ]]; then
  SSH_PORT="22"
fi
SSH_HOST="${SSH_HOST#root@}"

python - <<PY
import json
from pathlib import Path
from primelab_hermes.qlora_conveyor import append_receipt, write_stage_state

payload = {
    "pod_id": "${POD_ID}",
    "ssh_host": "${SSH_HOST}",
    "ssh_port": "${SSH_PORT}",
    "remote_root": "${REMOTE_ROOT}",
    "run_root_remote": "${RUN_ROOT_REMOTE}",
}
Path("${RUN_ROOT_LOCAL}").mkdir(parents=True, exist_ok=True)
Path("${RUN_ROOT_LOCAL}/connection.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
write_stage_state("${RUN_ROOT_LOCAL}", "smoke", "remote_ready", **payload)
append_receipt("${RUN_ROOT_LOCAL}", "smoke", "remote_ready", **payload)
PY

ssh -o StrictHostKeyChecking=no -i "$PEM_PATH" -p "$SSH_PORT" root@"$SSH_HOST" "mkdir -p '$REMOTE_ROOT' '$REMOTE_ROOT/logs' '$RUN_ROOT_REMOTE'"
scp -o StrictHostKeyChecking=no -i "$PEM_PATH" -P "$SSH_PORT" "$BUNDLE_LOCAL" root@"$SSH_HOST":"$REMOTE_ROOT/qlora_bundle.tar.gz"
ssh -o StrictHostKeyChecking=no -i "$PEM_PATH" -p "$SSH_PORT" root@"$SSH_HOST" \
  "cd '$REMOTE_ROOT' && tar --no-same-owner -xzf qlora_bundle.tar.gz && python3 -m venv .venv && source .venv/bin/activate && python -m pip install --upgrade pip && python -m pip install -r requirements/qlora.txt && mkdir -p '$RUN_ROOT_REMOTE/logs' && nohup bash -lc 'cd \"$REMOTE_ROOT\" && source .venv/bin/activate && export PYTHONPATH=\"$REMOTE_ROOT/src:\${PYTHONPATH:-}\" && python scripts/remote_qlora_conveyor.py --spec-json \"$SPEC_JSON\" --data-root \"$DATA_ROOT_REMOTE\" --run-root \"$RUN_ROOT_REMOTE\"' > '$RUN_ROOT_REMOTE/logs/launcher.log' 2>&1 & echo \$! > '$RUN_ROOT_REMOTE/launcher.pid'"

python - <<PY
from primelab_hermes.qlora_conveyor import append_receipt, write_stage_state
write_stage_state("${RUN_ROOT_LOCAL}", "training", "launched", pod_id="${POD_ID}", ssh_host="${SSH_HOST}", ssh_port="${SSH_PORT}")
append_receipt("${RUN_ROOT_LOCAL}", "training", "launched", pod_id="${POD_ID}", ssh_host="${SSH_HOST}", ssh_port="${SSH_PORT}")
PY

echo "POD_ID=${POD_ID}"
echo "SSH=${SSH_HOST}:${SSH_PORT}"
echo "REMOTE_RUN_DIR=${RUN_ROOT_REMOTE}"
echo "LOCAL_RUN_DIR=${RUN_ROOT_LOCAL}"
