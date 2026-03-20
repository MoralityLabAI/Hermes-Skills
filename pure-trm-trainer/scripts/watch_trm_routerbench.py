#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def format_duration(seconds: float | None) -> str:
    if seconds is None or seconds < 0:
        return "estimating"
    total = int(round(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def clip_text(value: Any, limit: int) -> str:
    text = str(value)
    if len(text) <= limit:
        return text
    if limit <= 3:
        return text[:limit]
    return text[: limit - 3] + "..."


def format_progress_bar(completed: int, total: int, width: int = 18) -> str:
    if total <= 0:
        return "[" + ("-" * width) + "]"
    filled = max(0, min(width, int(round((completed / total) * width))))
    return "[" + ("#" * filled) + ("-" * (width - filled)) + "]"


def normalize_ram_budget(raw: Any) -> str:
    if raw in (None, "", 0, 0.0):
        return "auto"
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return str(raw)
    if value.is_integer():
        return f"{int(value)} GB"
    return f"{value:.1f} GB"


def score_value(scorecard: Dict[str, Any], primary: str, fallback: str = "") -> float:
    for key in (primary, fallback):
        if key and key in scorecard:
            try:
                return float(scorecard[key])
            except (TypeError, ValueError):
                continue
    return 0.0


def render_status_card(snapshot: Dict[str, Any]) -> str:
    width = 76
    border = "+" + "-" * (width - 2) + "+"
    completed = int(snapshot.get("completed_count", 0) or 0)
    total = int(snapshot.get("total_candidates", 0) or 0)
    current_metrics = clip_text(
        f"anchor={snapshot['current_anchor']:.4f} train={snapshot['current_train']:.4f} gap={snapshot['current_gap']:.4f}",
        56,
    )
    best_metrics = clip_text(
        f"anchor={snapshot['best_anchor']:.4f} train={snapshot['best_train']:.4f} gap={snapshot['best_gap']:.4f}",
        56,
    )
    lines = [
        border,
        f"| Hermes TRM Run: {clip_text(snapshot['run_id'], 56):<56}|",
        f"| phase   : {clip_text(snapshot['phase'], 56):<56}|",
        f"| step    : {clip_text(snapshot['step'], 56):<56}|",
        f"| source  : {clip_text(snapshot['data_source'], 56):<56}|",
        f"| RAM     : {clip_text(snapshot['ram_budget'], 56):<56}|",
        f"| ETA     : {clip_text(snapshot['eta'], 56):<56}|",
        f"| done    : {format_progress_bar(completed, total)} {snapshot['percent_complete']:>6.1f}%{'':<34}|",
        f"| current : {current_metrics:<56}|",
        f"| best    : {best_metrics:<56}|",
        border,
    ]
    return "\n".join(lines)


def build_snapshot(run_id: str, progress: Dict[str, Any] | None, summary: Dict[str, Any] | None) -> Dict[str, Any]:
    progress = progress or {}
    summary = summary or {}
    best = summary.get("best") or progress.get("best") or {}
    current_result = progress.get("current_result") or best
    total = int(progress.get("total_candidates", summary.get("total_candidates", 0)) or 0)
    completed = int(progress.get("completed_count", summary.get("completed_count", 0)) or 0)
    percent = float(progress.get("percent_complete", 0.0) or 0.0)
    return {
        "run_id": run_id,
        "phase": progress.get("phase", summary.get("phase", "unknown")),
        "step": progress.get("step", summary.get("step", "waiting")),
        "data_source": progress.get("data_source", summary.get("data_source", "unknown")),
        "ram_budget": normalize_ram_budget(progress.get("ram_budget", summary.get("memory_budget_gb"))),
        "eta": progress.get("eta", summary.get("eta", "estimating")),
        "percent_complete": percent,
        "completed_count": completed,
        "total_candidates": total,
        "current_anchor": score_value(current_result, "anchor_score", "judge_score"),
        "current_train": score_value(current_result, "train_score", "env_score"),
        "current_gap": score_value(current_result, "generalization_gap"),
        "best_anchor": score_value(best, "anchor_score", "judge_score"),
        "best_train": score_value(best, "train_score", "env_score"),
        "best_gap": score_value(best, "generalization_gap"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tail a TRM routerBench run with a compact Hermes-style card.")
    parser.add_argument("--run-dir", required=True, help="Path to the run directory.")
    parser.add_argument("--interval", type=float, default=2.0, help="Polling interval in seconds.")
    parser.add_argument("--once", action="store_true", help="Render once and exit.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir).expanduser().resolve()
    progress_path = run_dir / "progress.snapshot.json"
    summary_path = run_dir / "summary.json"
    last_render: Optional[str] = None

    while True:
        progress = read_json(progress_path) if progress_path.exists() else {}
        summary = read_json(summary_path) if summary_path.exists() else {}
        run_id = str(summary.get("run_id") or progress.get("run_id") or run_dir.name)
        snapshot = build_snapshot(run_id, progress, summary)
        card = render_status_card(snapshot)
        if card != last_render:
            print(card, flush=True)
            last_render = card
        if args.once:
            return 0
        if summary_path.exists() and (progress.get("phase") == "complete" or summary.get("best")):
            return 0
        time.sleep(max(0.5, float(args.interval)))


if __name__ == "__main__":
    raise SystemExit(main())
