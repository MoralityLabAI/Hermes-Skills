#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def score_value(payload: Dict[str, Any], primary: str, fallback: str = "") -> float:
    for key in (primary, fallback):
        if key and key in payload:
            try:
                return float(payload[key])
            except (TypeError, ValueError):
                continue
    return 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a compact TRM scorecard from a trainer run directory.")
    parser.add_argument("--trainer-run-dir", required=True, help="Trainer output directory that may contain summary.json.")
    parser.add_argument("--scorecard-path", required=True, help="Destination scorecard JSON path.")
    parser.add_argument("--summary-path", default="", help="Optional summary.json path override.")
    args = parser.parse_args()

    trainer_run_dir = Path(args.trainer_run_dir).resolve()
    scorecard_path = Path(args.scorecard_path).resolve()
    summary_path = Path(args.summary_path).resolve() if args.summary_path else trainer_run_dir / "summary.json"

    summary: Dict[str, Any] = {}
    if summary_path.exists():
        summary = read_json(summary_path)

    scorecard: Dict[str, Any] = {}
    candidate_sources = [
        trainer_run_dir / "scorecard.json",
        trainer_run_dir / "metrics.json",
        trainer_run_dir / "adapter_train_summary.json",
        summary_path,
    ]
    for candidate in candidate_sources:
        if candidate.exists():
            try:
                scorecard = read_json(candidate)
                break
            except json.JSONDecodeError:
                continue

    merged = {
        "train_score": score_value(scorecard, "train_score", "env_score") or score_value(summary, "train_score", "env_score"),
        "anchor_score": score_value(scorecard, "anchor_score", "judge_score") or score_value(summary, "anchor_score", "judge_score"),
        "failure_rate": score_value(scorecard, "failure_rate") or score_value(summary, "failure_rate"),
        "recovery_rate": score_value(scorecard, "recovery_rate") or score_value(summary, "recovery_rate"),
    }
    merged["generalization_gap"] = score_value(scorecard, "generalization_gap") or score_value(summary, "generalization_gap")
    if merged["generalization_gap"] <= 0.0:
        merged["generalization_gap"] = max(0.0, merged["train_score"] - merged["anchor_score"])

    payload = {
        **merged,
        "trainer_run_dir": str(trainer_run_dir),
        "summary_path": str(summary_path),
        "source": "local_evaluator",
        "summary_keys": sorted(list(summary.keys()))[:32],
    }
    dump_json(scorecard_path, payload)
    print(str(scorecard_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
