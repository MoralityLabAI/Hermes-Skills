from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .io_utils import append_jsonl, dump_json, ensure_dir, load_json, now_iso, sha256_text


def normalize_host_path(value: str) -> str:
    if os.name == "nt":
        return value
    normalized = value.replace("\\", "/")
    match = re.match(r"^([A-Za-z]):/(.*)$", normalized)
    if match:
        drive = match.group(1).lower()
        rest = match.group(2)
        return f"/mnt/{drive}/{rest}"
    return value


def load_factory_config(config_path: Path) -> Dict[str, Any]:
    payload = load_json(config_path)
    if "artifact_root" in payload:
        payload["artifact_root"] = normalize_host_path(payload["artifact_root"])
    if "base_world" in payload:
        payload["base_world"] = normalize_host_path(payload["base_world"])
    if "paths" in payload:
        payload["paths"] = {
            key: normalize_host_path(value) if isinstance(value, str) else value
            for key, value in payload["paths"].items()
        }
    payload["_config_path"] = str(config_path)
    return payload


def init_factory_run(config: Dict[str, Any], run_root: Path, run_id: Optional[str]) -> tuple[str, Path]:
    actual_run_id = run_id or config.get("run_id") or f"factory_{now_iso().replace(':', '').replace('-', '')}"
    run_dir = ensure_dir(run_root / actual_run_id)
    dump_json(run_dir / "factory_config.snapshot.json", {k: v for k, v in config.items() if not k.startswith("_")})
    return actual_run_id, run_dir


def stage_manifest(run_id: str, stage_name: str, config: Dict[str, Any], status: str, command: List[str], outputs: List[str], returncode: int, started_at: str, notes: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "run_id": run_id,
        "stage": stage_name,
        "status": status,
        "started_at": started_at,
        "completed_at": now_iso(),
        "command": command,
        "outputs": outputs,
        "returncode": returncode,
        "config_digest": sha256_text(json.dumps(config, sort_keys=True)),
        "notes": notes or [],
    }


def build_context(config: Dict[str, Any], run_dir: Path) -> Dict[str, str]:
    paths = config["paths"]
    ctx = {
        "repo_root": paths["repo_root"],
        "base_world": config["base_world"],
        "run_dir": str(run_dir),
        "out_dir": str(ensure_dir(run_dir / "worlds")),
        "report_dir": str(ensure_dir(run_dir / "reports")),
        "log_dir": str(ensure_dir(run_dir / "logs")),
        "index_dir": str(ensure_dir(run_dir / "indices")),
        "qlora_dir": str(ensure_dir(run_dir / "qlora")),
    }
    for key, value in paths.items():
        ctx[key] = value
    return ctx


def render(template: str, ctx: Dict[str, str]) -> str:
    return template.format(**ctx)


def stage_completed(run_dir: Path, stage_name: str) -> bool:
    manifest_path = run_dir / stage_name / "manifest.json"
    return manifest_path.exists() and load_json(manifest_path).get("status") == "completed"


def run_stage(run_id: str, run_dir: Path, config: Dict[str, Any], stage: Dict[str, Any], ctx: Dict[str, str], force: bool) -> None:
    stage_name = stage["name"]
    stage_dir = ensure_dir(run_dir / stage_name)
    if stage_completed(run_dir, stage_name) and not force:
        return
    command = [render(item, ctx) for item in stage["command"]]
    outputs = [render(item, ctx) for item in stage.get("outputs", [])]
    stdout_capture = render(stage["stdout_to"], ctx) if stage.get("stdout_to") else None
    stderr_capture = render(stage["stderr_to"], ctx) if stage.get("stderr_to") else None
    started_at = now_iso()
    progress = {
        "run_id": run_id,
        "stage": stage_name,
        "status": "running",
        "started_at": started_at,
        "command": command,
        "outputs": outputs,
    }
    dump_json(stage_dir / "progress.json", progress)
    append_jsonl(stage_dir / "events.jsonl", {"event": "stage_started", "at": started_at, "command": command})
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.update(stage.get("env", {}))
    stdout_path = stage_dir / "stdout.log"
    stderr_path = stage_dir / "stderr.log"
    with stdout_path.open("w", encoding="utf-8") as stdout_handle, stderr_path.open("w", encoding="utf-8") as stderr_handle:
        proc = subprocess.run(command, cwd=render(stage.get("cwd", "{repo_root}"), ctx), env=env, text=True, stdout=stdout_handle, stderr=stderr_handle, shell=False)
    if stdout_capture:
        ensure_dir(Path(stdout_capture).parent)
        Path(stdout_capture).write_text(stdout_path.read_text(encoding="utf-8"), encoding="utf-8")
    if stderr_capture:
        ensure_dir(Path(stderr_capture).parent)
        Path(stderr_capture).write_text(stderr_path.read_text(encoding="utf-8"), encoding="utf-8")
    status = "completed" if proc.returncode == 0 else "failed"
    manifest = stage_manifest(run_id, stage_name, config, status, command, outputs, proc.returncode, started_at, stage.get("notes"))
    dump_json(stage_dir / "manifest.json", manifest)
    dump_json(stage_dir / "progress.json", {"run_id": run_id, "stage": stage_name, "status": status, "completed_at": now_iso(), "returncode": proc.returncode, "outputs": outputs})
    append_jsonl(stage_dir / "events.jsonl", {"event": f"stage_{status}", "at": now_iso(), "returncode": proc.returncode})
    if proc.returncode != 0 and not stage.get("continue_on_failure", False):
        raise RuntimeError(f"Stage failed: {stage_name}")


def run_factory(config: Dict[str, Any], run_root: Path, run_id: Optional[str] = None, force: bool = False, stop_after: Optional[str] = None) -> Path:
    run_id, run_dir = init_factory_run(config, run_root, run_id)
    ctx = build_context(config, run_dir)
    for key, value in config.get("artifacts", {}).items():
        ctx[key] = render(value, ctx)
    for stage in config["stages"]:
        run_stage(run_id, run_dir, config, stage, ctx, force)
        if stop_after == stage["name"]:
            break
    return run_dir
