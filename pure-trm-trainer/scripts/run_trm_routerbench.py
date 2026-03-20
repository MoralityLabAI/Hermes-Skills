#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def resolve_existing(candidates: Iterable[str | Path], label: str) -> Path:
    checked: List[str] = []
    for raw in candidates:
        if raw is None:
            continue
        path = Path(raw).expanduser()
        checked.append(str(path))
        if path.exists():
            return path.resolve()
    raise FileNotFoundError(f"Could not resolve {label}. Checked: {checked}")


def maybe_env(name: str) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or None


def parse_float(value: Any) -> float | None:
    if value in (None, "", 0, 0.0):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the isolated TRM routerBench harness.")
    parser.add_argument("--config", default="", help="Optional routerbench JSON spec path.")
    parser.add_argument("--run-id", default="", help="Override the run id.")
    parser.add_argument("--dry-run", action="store_true", help="Write the resolved config but do not launch the hill-climb runner.")
    parser.add_argument("--template-root", default="", help="Override the trainer template root.")
    parser.add_argument("--corpus-spec", default="", help="Override the corpus spec path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    repo_root = skill_root.parent
    spec_path = Path(args.config).resolve() if args.config else skill_root / "references" / "routerbench-spec.json"
    spec = read_json(spec_path)

    template_root = resolve_existing(
        [
            args.template_root,
            maybe_env("TRM_TEMPLATE_ROOT"),
            maybe_env("HERMES_TRM_TEMPLATE_ROOT"),
            maybe_env("HRM_TEMPLATE_ROOT"),
            "C:/projects/HRM-re/experiments/hrm_trainer_template",
            "/mnt/c/projects/HRM-re/experiments/hrm_trainer_template",
            "D:/Research Engine/HRM-re/experiments/hrm_trainer_template",
        ],
        "trainer template root",
    )
    corpus_spec = resolve_existing(
        [
            args.corpus_spec,
            maybe_env("TRM_ROUTERBENCH_CORPUS_SPEC"),
            maybe_env("TRM_CORPUS_SPEC"),
            repo_root / "storyworld-conveyor" / "sample_data" / "trm_training_corpus_spec.sample.json",
            "C:/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/sample_data/trm_training_corpus_spec.sample.json",
            "/mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/sample_data/trm_training_corpus_spec.sample.json",
        ],
        "routerBench corpus spec",
    )

    run_id = str(args.run_id or spec.get("run_id") or "trm_routerBench")
    artifact_root = skill_root / "runs"
    resolved_config = {
        "run_id": run_id,
        "artifact_root": str(artifact_root),
        "template_root": str(template_root),
        "trainer_script": str(template_root / "run_trainer.ps1"),
        "base_trainer_config": str(template_root / "trainer_config_safe.json"),
        "trainer_recipe": str(spec.get("trainer_recipe") or "persistent_tesseract_qlora"),
        "corpus_spec": str(corpus_spec),
        "data_source": str(spec.get("data_source") or Path(corpus_spec).name),
        "evaluator_script": str(skill_root / "scripts" / "evaluate_trm_scorecard.py"),
        "scorecard_relpath": str(spec.get("scorecard_relpath") or "scorecard.json"),
        "plateau_patience": int(spec.get("plateau_patience", 1) or 1),
        "maximize_key": str(spec.get("maximize_key") or "anchor_score"),
        "max_generalization_gap": float(spec.get("max_generalization_gap", 0.15) or 0.15),
        "memory_budget_gb": parse_float(spec.get("memory_budget_gb") or maybe_env("TRM_MEMORY_GB")),
        "baseline_model": str(spec.get("baseline_model") or maybe_env("TRM_BASELINE_MODEL") or ""),
        "router_model": str(spec.get("router_model") or maybe_env("TRM_ROUTER_MODEL") or ""),
        "anchor_set": dict(spec.get("anchor_set", {})),
        "mutations": list(spec.get("mutations") or []),
        "generalization_ladder": list(spec.get("generalization_ladder") or []),
        "trainer_overrides": dict(spec.get("trainer_overrides") or {}),
    }

    run_dir = artifact_root / run_id
    resolved_path = run_dir / "routerbench.resolved.json"
    dump_json(resolved_path, resolved_config)

    if args.dry_run:
        print(str(resolved_path))
        return 0

    runner = skill_root / "scripts" / "run_trm_generalization_hillclimb.py"
    cmd = [
        sys.executable,
        str(runner),
        "--config",
        str(resolved_path),
        "--run-id",
        run_id,
    ]
    return int(subprocess.call(cmd, cwd=str(skill_root)))


if __name__ == "__main__":
    raise SystemExit(main())
