#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_TRAINER_CANDIDATES = [
    Path("D:/Research_Engine/prime_lab/storyworld_sft/train_qlora_sft.py"),
    Path("/mnt/d/Research_Engine/prime_lab/storyworld_sft/train_qlora_sft.py"),
]
DEFAULT_SOURCE_CANDIDATES = [
    Path("D:/Research_Engine/tesseract_persistent/data/router/tesseract-router-dataset-v1.jsonl"),
    Path("/mnt/d/Research_Engine/tesseract_persistent/data/router/tesseract-router-dataset-v1.jsonl"),
]


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def maybe_env(name: str) -> str:
    return str(os.environ.get(name, "")).strip()


def resolve_existing(
    path_like: str | Path | List[str | Path],
    fallback: Path | List[Path],
    base_dir: Path | None = None,
) -> Path:
    if isinstance(path_like, list):
        for item in path_like:
            try:
                return resolve_existing(item, fallback, base_dir=base_dir)
            except FileNotFoundError:
                continue
        raise FileNotFoundError(f"Could not resolve any candidate in {path_like}")
    raw = str(path_like or "").strip()
    if raw:
        candidate = Path(raw).expanduser()
        if candidate.exists():
            return candidate.resolve()
        if base_dir is not None and not candidate.is_absolute():
            base_candidate = (base_dir / candidate).expanduser()
            if base_candidate.exists():
                return base_candidate.resolve()
        # Try the same path under the current platform's common mount points.
        alt_candidates = []
        if raw.startswith("D:/"):
            alt_candidates.append(Path(raw.replace("D:/", "/mnt/d/")))
        if raw.startswith("D:\\"):
            alt_candidates.append(Path(raw.replace("D:\\", "/mnt/d/").replace("\\", "/")))
        if raw.startswith("C:/"):
            alt_candidates.append(Path(raw.replace("C:/", "/mnt/c/")))
        if raw.startswith("C:\\"):
            alt_candidates.append(Path(raw.replace("C:\\", "/mnt/c/").replace("\\", "/")))
        for alt in alt_candidates:
            if alt.exists():
                return alt.resolve()
    if isinstance(fallback, list):
        for candidate in fallback:
            if candidate.exists():
                return candidate.resolve()
        raise FileNotFoundError(f"Could not resolve {raw or fallback[0]}")
    if fallback.exists():
        return fallback.resolve()
    raise FileNotFoundError(f"Could not resolve {raw or fallback}")


def merge_dict(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = json.loads(json.dumps(base))
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the persistent-tesseract-style router QLoRA trainer.")
    parser.add_argument("--config", required=True, help="Training spec JSON path.")
    parser.add_argument("--run-id", default="", help="Override the run id.")
    parser.add_argument("--dry-run", action="store_true", help="Write manifests without launching the trainer.")
    return parser.parse_args()


def resolve_path_like(config_dir: Path, raw: str) -> Path:
    path = Path(raw).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (config_dir / path).resolve()


def resolve_output_dir(config: Dict[str, Any], config_dir: Path, run_root: Path, run_id: str) -> Path:
    raw = str(config.get("output_dir") or config.get("out") or "").strip()
    if raw:
        return resolve_path_like(config_dir, raw)
    return (run_root / run_id / "trainer_outputs").resolve()


def build_trainer_cmd(trainer_script: Path, model: str, data_path: Path, out_dir: Path, hparams: Dict[str, Any]) -> List[str]:
    cmd = [
        sys.executable,
        str(trainer_script),
        "--model",
        model,
        "--data",
        str(data_path),
        "--out",
        str(out_dir),
        "--max-steps",
        str(int(hparams.get("max_steps", 200))),
        "--seq-len",
        str(int(hparams.get("seq_len", 512))),
        "--batch-size",
        str(int(hparams.get("batch_size", 1))),
        "--lr",
        str(float(hparams.get("lr", 2e-4))),
        "--grad-accum",
        str(int(hparams.get("grad_accum", 16))),
        "--lora-r",
        str(int(hparams.get("lora_r", 16))),
        "--lora-alpha",
        str(int(hparams.get("lora_alpha", 32))),
        "--lora-dropout",
        str(float(hparams.get("lora_dropout", 0.05))),
        "--target-modules",
        str(hparams.get("target_modules", "q_proj,k_proj,v_proj,o_proj")),
    ]
    if "streaming" in hparams:
        cmd.append("--streaming" if bool(hparams["streaming"]) else "--no-streaming")
    return cmd


def main() -> int:
    args = parse_args()
    config_path = Path(args.config).expanduser().resolve()
    config = read_json(config_path)
    config_dir = config_path.parent
    run_id = str(args.run_id or config.get("run_id") or f"trm_routerTrain_{int(time.time())}")
    skill_root = Path(__file__).resolve().parents[1]
    run_root = Path(str(config.get("artifact_root") or (skill_root / "runs"))).expanduser().resolve()
    run_dir = run_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    trainer_script = resolve_existing(
        config.get("trainer_script") or maybe_env("TRM_ROUTER_TRAINER_SCRIPT"),
        DEFAULT_TRAINER_CANDIDATES,
    )
    corpus_builder = resolve_existing(
        config.get("corpus_builder_script") or maybe_env("TRM_ROUTER_CORPUS_BUILDER"),
        [Path(__file__).resolve().parent / "build_router_training_corpus.py"],
        base_dir=config_dir,
    )
    source_jsonl = resolve_existing(
        config.get("source_jsonl") or maybe_env("TRM_ROUTER_TRAIN_SOURCE"),
        DEFAULT_SOURCE_CANDIDATES,
    )
    messages_jsonl = resolve_path_like(config_dir, str(config.get("messages_jsonl") or f"../runs/{run_id}/router_messages.jsonl"))
    output_dir = resolve_output_dir(config, config_dir, run_root, run_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    model = str(
        config.get("model")
        or maybe_env("TRM_ROUTER_BASE_MODEL")
        or maybe_env("QWOPUS_MODEL_ID")
        or "Qwen/Qwen3.5-9B-Instruct"
    )
    baseline_model = str(config.get("baseline_model") or maybe_env("TRM_BASELINE_MODEL") or "")
    train_hparams = dict(config.get("train_hparams") or {})
    trainer_cfg = dict(config.get("trainer_overrides") or {})
    train_hparams = merge_dict(train_hparams, dict(trainer_cfg.get("train") or {}))

    corpus_spec = {
        "source": str(source_jsonl),
        "out": str(messages_jsonl),
        "max_records": int(config.get("max_records", 0) or 0),
        "system_prompt": str(
            config.get("system_prompt")
            or "You are a TRM router. Emit compact JSON only. Do not output hidden reasoning."
        ),
    }
    corpus_spec_path = resolve_path_like(config_dir, str(config.get("corpus_spec") or f"../runs/{run_id}/router_corpus_spec.json"))
    dump_json(corpus_spec_path, corpus_spec)

    build_cmd = [
        sys.executable,
        str(corpus_builder),
        "--source",
        str(source_jsonl),
        "--out",
        str(messages_jsonl),
        "--system-prompt",
        corpus_spec["system_prompt"],
    ]
    if corpus_spec["max_records"] > 0:
        build_cmd += ["--max-records", str(corpus_spec["max_records"])]

    trainer_cmd = build_trainer_cmd(trainer_script, model, messages_jsonl, output_dir, train_hparams)
    manifest = {
        "run_id": run_id,
        "trainer_recipe": str(config.get("trainer_recipe") or "persistent_tesseract_qlora"),
        "trainer_script": str(trainer_script),
        "corpus_builder_script": str(corpus_builder),
        "source_jsonl": str(source_jsonl),
        "messages_jsonl": str(messages_jsonl),
        "output_dir": str(output_dir),
        "model": model,
        "baseline_model": baseline_model,
        "train_hparams": train_hparams,
        "build_cmd": build_cmd,
        "trainer_cmd": trainer_cmd,
        "dry_run": bool(args.dry_run),
        "benchmark_spec": str(config.get("benchmark_spec") or ""),
    }
    manifest_path = run_dir / "train_launch_manifest.json"
    dump_json(manifest_path, manifest)

    if args.dry_run:
        print(str(manifest_path))
        return 0

    subprocess.run(build_cmd, check=True, cwd=str(config_dir))
    subprocess.run(trainer_cmd, check=True, cwd=str(trainer_script.parent))
    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
