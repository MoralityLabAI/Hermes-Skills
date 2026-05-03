#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def build_stage_manifest(
    run_id: str,
    stage: str,
    status: str,
    input_files: List[str],
    output_files: List[str],
    counters: Dict[str, Any],
    notes: List[str] | None = None,
) -> Dict[str, Any]:
    ts = now_iso()
    return {
        "run_id": run_id,
        "stage": stage,
        "status": status,
        "started_at": ts,
        "completed_at": ts,
        "input_files": input_files,
        "output_files": output_files,
        "counters": counters,
        "notes": notes or [],
    }


def run_command(stage_dir: Path, command: List[str], workdir: Path) -> int:
    stdout_path = stage_dir / "stdout.log"
    stderr_path = stage_dir / "stderr.log"
    with stdout_path.open("w", encoding="utf-8", newline="\n") as out_handle, stderr_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as err_handle:
        proc = subprocess.run(command, cwd=str(workdir), stdout=out_handle, stderr=err_handle, text=True, check=False)
    return int(proc.returncode)


def _merge_dict(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = json.loads(json.dumps(base))
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def _resolve_train_paths(config_dir: Path, cfg: Dict[str, Any]) -> Dict[str, Any]:
    train = dict(cfg.get("train", {}))
    for key in ("data", "out", "resume_checkpoint"):
        raw = str(train.get(key, "") or "")
        if raw:
            path = Path(raw)
            if not path.is_absolute():
                train[key] = str((config_dir / path).resolve())
    cfg["train"] = train
    return cfg


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes wrapper for pure TRM trainer runs.")
    parser.add_argument("--config", required=True, help="JSON config path.")
    parser.add_argument("--run-id", default="", help="Optional run id override.")
    parser.add_argument("--dry-run", action="store_true", help="Prepare corpus and config without launching trainer.")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))

    run_id = str(args.run_id or config.get("run_id") or f"trm_hermes_{int(time.time())}")
    artifact_root = ensure_dir(Path(config["artifact_root"]).resolve())
    run_dir = ensure_dir(artifact_root / run_id)
    dump_json(run_dir / "run_config.snapshot.json", config)

    scripts_dir = Path(__file__).resolve().parent
    template_root = Path(config["template_root"]).resolve()
    trainer_script = Path(config.get("trainer_script") or (template_root / "run_trainer.ps1")).resolve()
    base_trainer_config = Path(config.get("base_trainer_config") or (template_root / "trainer_config_safe.json")).resolve()

    corpus_stage = ensure_dir(run_dir / "prepare_corpus")
    corpus_spec_path = Path(config["corpus_spec"]).resolve()
    corpus_out_dir = ensure_dir(run_dir / "corpus")
    corpus_cmd = [
        sys.executable,
        str(scripts_dir / "build_trm_training_corpus.py"),
        "--config",
        str(corpus_spec_path),
        "--out-dir",
        str(corpus_out_dir),
    ]
    dump_json(corpus_stage / "command.json", {"command": corpus_cmd})
    corpus_status = "planned" if args.dry_run else ("completed" if run_command(corpus_stage, corpus_cmd, scripts_dir.parent) == 0 else "failed")
    corpus_manifest = corpus_out_dir / "manifest.json"
    train_jsonl = corpus_out_dir / "train.jsonl"
    dump_json(
        corpus_stage / "manifest.json",
        build_stage_manifest(
            run_id,
            "prepare_corpus",
            corpus_status,
            [str(corpus_spec_path)],
            [str(train_jsonl), str(corpus_manifest)],
            {"corpus_dir_exists": corpus_out_dir.exists()},
            notes=["Normalized mixed TRM sources into a conductor-style corpus"],
        ),
    )
    dump_json(corpus_stage / "progress.json", {"stage": "prepare_corpus", "status": corpus_status, "updated_at": now_iso()})
    append_jsonl(corpus_stage / "events.jsonl", {"event": "stage_finished", "status": corpus_status, "at": now_iso()})
    if corpus_status == "failed":
        return 1

    prepare_stage = ensure_dir(run_dir / "prepare_config")
    base_cfg = json.loads(base_trainer_config.read_text(encoding="utf-8"))
    base_cfg["run_id"] = run_id
    if "output_dir" in config:
        base_cfg["output_dir"] = str(Path(config["output_dir"]).resolve())
    trainer_overrides = dict(config.get("trainer_overrides", {}))
    merged_cfg = _merge_dict(base_cfg, trainer_overrides)
    merged_cfg.setdefault("train", {})
    merged_cfg["train"]["type"] = "conductor"
    merged_cfg["train"]["data"] = str(train_jsonl)
    merged_cfg = _resolve_train_paths(config_path.parent, merged_cfg)
    resolved_cfg_path = run_dir / "trainer_config.resolved.json"
    dump_json(resolved_cfg_path, merged_cfg)
    dump_json(
        prepare_stage / "manifest.json",
        build_stage_manifest(
            run_id,
            "prepare_config",
            "completed",
            [str(base_trainer_config), str(config_path), str(train_jsonl)],
            [str(resolved_cfg_path)],
            {"override_keys": len(trainer_overrides.keys())},
            notes=["Resolved pure TRM trainer config for Hermes-run launch"],
        ),
    )
    dump_json(prepare_stage / "progress.json", {"stage": "prepare_config", "status": "completed", "updated_at": now_iso()})
    append_jsonl(prepare_stage / "events.jsonl", {"event": "stage_finished", "status": "completed", "at": now_iso()})

    launch_stage = ensure_dir(run_dir / "launch_trainer")
    powershell_bin = str(config.get("powershell_bin") or "powershell")
    launch_cmd = [powershell_bin, "-ExecutionPolicy", "Bypass", "-File", str(trainer_script), "-ConfigPath", str(resolved_cfg_path)]
    dump_json(launch_stage / "command.json", {"command": launch_cmd})
    if args.dry_run:
        launch_status = "planned"
    else:
        rc = run_command(launch_stage, launch_cmd, template_root)
        launch_status = "completed" if rc == 0 else "failed"

    trainer_output_root = Path(merged_cfg.get("output_dir", "outputs"))
    if not trainer_output_root.is_absolute():
        trainer_output_root = (resolved_cfg_path.parent / trainer_output_root).resolve()
    trainer_run_dir = trainer_output_root / run_id
    expected_outputs = [str(trainer_run_dir / "events.jsonl"), str(trainer_run_dir / "summary.json"), str(trainer_run_dir / "checkpoints")]
    dump_json(
        launch_stage / "manifest.json",
        build_stage_manifest(
            run_id,
            "launch_trainer",
            launch_status,
            [str(resolved_cfg_path), str(trainer_script)],
            expected_outputs,
            {"trainer_run_dir_exists": trainer_run_dir.exists()},
            notes=["Pure TRM trainer launched under Hermes manifest wrapper"],
        ),
    )
    dump_json(launch_stage / "progress.json", {"stage": "launch_trainer", "status": launch_status, "updated_at": now_iso()})
    append_jsonl(launch_stage / "events.jsonl", {"event": "stage_finished", "status": launch_status, "at": now_iso()})
    if launch_status == "failed":
        return 1

    summary = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "corpus_manifest": str(corpus_manifest),
        "trainer_config": str(resolved_cfg_path),
        "trainer_run_dir": str(trainer_run_dir),
        "trainer_outputs": expected_outputs,
    }
    dump_json(run_dir / "summary.json", summary)
    print(str(run_dir))
    print(str(run_dir / "summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
