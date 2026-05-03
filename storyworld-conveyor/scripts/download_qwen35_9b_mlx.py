from __future__ import annotations

import json
import time
from pathlib import Path

from huggingface_hub import snapshot_download


REPO_ID = "mlx-community/Qwen3.5-9B-4bit"
WORKER_ROOT = Path.home() / "worker"
MODEL_DIR = WORKER_ROOT / "models" / "Qwen3.5-9B-4bit"
LOG_DIR = WORKER_ROOT / "logs"
STATUS_PATH = LOG_DIR / "qwen35_9b_download_status.json"


def write_status(status: str, extra: dict | None = None) -> None:
    payload = {
        "repo_id": REPO_ID,
        "status": status,
        "timestamp": int(time.time()),
        "model_dir": str(MODEL_DIR),
    }
    if extra:
        payload.update(extra)
    STATUS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.parent.mkdir(parents=True, exist_ok=True)
    write_status("running")
    snapshot_path = snapshot_download(
        repo_id=REPO_ID,
        local_dir=MODEL_DIR,
        local_dir_use_symlinks=False,
    )
    files = sorted(str(p.relative_to(MODEL_DIR)) for p in MODEL_DIR.rglob("*") if p.is_file())
    write_status(
        "completed",
        {
            "snapshot_path": snapshot_path,
            "file_count": len(files),
        },
    )
    print(f"downloaded {REPO_ID} to {MODEL_DIR}")
    print(f"file_count={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
