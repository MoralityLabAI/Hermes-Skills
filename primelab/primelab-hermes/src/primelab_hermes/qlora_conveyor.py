from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


STAGES = [
    "queued",
    "bootstrapping",
    "fetching",
    "smoke",
    "training",
    "validating",
    "exfiltrating",
    "archived",
    "failed",
]

REQUIRED_SPEC_FIELDS = [
    "model",
    "max_steps",
    "seq_len",
    "batch_size",
    "lr",
    "grad_accum",
    "lora_r",
    "lora_alpha",
    "lora_dropout",
    "target_modules",
    "envs",
]


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def load_spec(spec_path: str | Path) -> dict[str, Any]:
    path = Path(spec_path)
    spec = json.loads(path.read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED_SPEC_FIELDS if key not in spec]
    if missing:
        raise SystemExit(f"Missing required spec fields in {path}: {', '.join(missing)}")
    if not isinstance(spec.get("envs"), list) or not spec["envs"]:
        raise SystemExit(f"Spec {path} must contain a non-empty envs list")
    for env in spec["envs"]:
        if "name" not in env:
            raise SystemExit(f"Env entry is missing name in {path}")
    return spec


def ensure_run_dirs(run_root: str | Path) -> Path:
    root = Path(run_root)
    (root / "receipts").mkdir(parents=True, exist_ok=True)
    (root / "logs").mkdir(parents=True, exist_ok=True)
    return root


def write_stage_state(run_root: str | Path, stage: str, status: str, **extra: Any) -> Path:
    if stage not in STAGES:
        raise ValueError(f"Unknown stage {stage}")
    root = ensure_run_dirs(run_root)
    payload = {
        "stage": stage,
        "status": status,
        "updated_at": utc_now(),
    }
    payload.update(extra)
    out = root / "stage-state.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return out


def append_receipt(run_root: str | Path, stage: str, status: str, **extra: Any) -> Path:
    root = ensure_run_dirs(run_root)
    slug = f"{utc_now().replace(':', '').replace('+00:00', 'Z')}_{stage}_{status}.json"
    out = root / "receipts" / slug
    payload = {
        "stage": stage,
        "status": status,
        "timestamp": utc_now(),
    }
    payload.update(extra)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return out


def summarize_log(log_path: str | Path, max_lines: int = 40) -> list[str]:
    path = Path(log_path)
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-max_lines:]
