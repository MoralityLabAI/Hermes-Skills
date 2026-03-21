from __future__ import annotations

import json
import re
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STEP_PATTERN = re.compile(
    r"\[SUCCESS\] Step (?P<step>\d+) \| Time: (?P<time>[0-9.]+)s \| Reward: "
    r"(?P<reward>[0-9.]+) \| Throughput: (?P<throughput>[0-9.]+) tokens/s \| "
    r"Seq\. Length: (?P<seq_len>[0-9.]+) tokens/sample \| Async Level: "
    r"(?P<async>\d+) \| Max\. Off-Policy Level: (?P<off_policy>\d+)"
)
EVAL_PATTERN = re.compile(
    r"\[SUCCESS\] Evaluated (?P<env>.+?) in (?P<time>[0-9.]+)s "
    r"\(Avg@1=(?P<avg>[0-9.]+), Pass@1: (?P<pass>[0-9.]+), "
    r"No-response: (?P<no_response>[0-9.]+)%, Completion Length: "
    r"(?P<completion>[0-9.]+)"
)
MODEL_PATTERN = re.compile(r"Initializing tokenizer for (?P<model>\S+)")
TRAIN_ENV_PATTERN = re.compile(r"Loading \d+ training environment\(s\) \((?P<envs>[^)]*)\)")
TIMESTAMP_PATTERN = re.compile(r"^\d{2}:\d{2}:\d{2} \[(?:INFO|SUCCESS|WARNING|ERROR)\]")
FINISHED_PATTERN = "Orchestrator finished."
FATAL_PATTERN = "[ERROR] Fatal error"
NO_TRAJECTORY_PATTERN = "No trajectory steps for example"


@dataclass
class StepMetric:
    step: int
    seconds: float
    reward: float
    throughput: float
    seq_len: float
    async_level: int
    off_policy_level: int


@dataclass
class EvalMetric:
    env: str
    seconds: float
    avg_at_1: float
    pass_at_1: float
    no_response_pct: float
    completion_length: float


def parse_hosted_log(text: str) -> dict[str, Any]:
    steps: list[StepMetric] = []
    evals: list[EvalMetric] = []
    model: str | None = None
    envs: list[str] = []
    warnings = 0
    status = "unknown"

    for line in _logical_lines(text):
        model_match = MODEL_PATTERN.search(line)
        if model_match:
            model = model_match.group("model")

        train_env_match = TRAIN_ENV_PATTERN.search(line)
        if train_env_match:
            envs = [item.strip() for item in train_env_match.group("envs").split(",")]

        if NO_TRAJECTORY_PATTERN in line:
            warnings += 1

        step_match = STEP_PATTERN.search(line)
        if step_match:
            steps.append(
                StepMetric(
                    step=int(step_match.group("step")),
                    seconds=float(step_match.group("time")),
                    reward=float(step_match.group("reward")),
                    throughput=float(step_match.group("throughput")),
                    seq_len=float(step_match.group("seq_len")),
                    async_level=int(step_match.group("async")),
                    off_policy_level=int(step_match.group("off_policy")),
                )
            )
            continue

        eval_match = EVAL_PATTERN.search(line)
        if eval_match:
            evals.append(
                EvalMetric(
                    env=eval_match.group("env"),
                    seconds=float(eval_match.group("time")),
                    avg_at_1=float(eval_match.group("avg")),
                    pass_at_1=float(eval_match.group("pass")),
                    no_response_pct=float(eval_match.group("no_response")),
                    completion_length=float(eval_match.group("completion")),
                )
            )

        if FINISHED_PATTERN in line:
            status = "completed"
        elif FATAL_PATTERN in line:
            status = "failed"

    rewards = [step.reward for step in steps]
    step_times = [step.seconds for step in steps]

    latest_eval = evals[-1].__dict__ if evals else None
    summary = {
        "status": status,
        "model": model,
        "envs": envs,
        "steps_completed": steps[-1].step if steps else 0,
        "step_count": len(steps),
        "reward": {
            "final": rewards[-1] if rewards else None,
            "best": max(rewards) if rewards else None,
            "mean": statistics.fmean(rewards) if rewards else None,
            "min": min(rewards) if rewards else None,
        },
        "timing": {
            "last_step_seconds": step_times[-1] if step_times else None,
            "mean_step_seconds": statistics.fmean(step_times) if step_times else None,
            "total_logged_seconds": sum(step_times) if step_times else None,
        },
        "warnings": {
            "no_trajectory_count": warnings,
        },
        "latest_eval": latest_eval,
        "eval_count": len(evals),
        "steps": [step.__dict__ for step in steps],
        "evals": [item.__dict__ for item in evals],
    }
    return summary


def _logical_lines(text: str) -> list[str]:
    logical: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if TIMESTAMP_PATTERN.match(line) or not logical:
            logical.append(line)
        else:
            logical[-1] = f"{logical[-1]} {line.lstrip()}"
    return logical


def ascii_table(headers: list[str], rows: list[list[Any]]) -> str:
    str_rows = [[str(cell) for cell in row] for row in rows]
    widths = [len(header) for header in headers]
    for row in str_rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))

    def fmt_row(row: list[str]) -> str:
        return "| " + " | ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(row)) + " |"

    border = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    lines = [border, fmt_row(headers), border]
    for row in str_rows:
        lines.append(fmt_row(row))
    lines.append(border)
    return "\n".join(lines)


def render_run_summary(receipt: dict[str, Any]) -> str:
    summary = receipt["summary"]
    eval_summary = summary.get("latest_eval") or {}
    headers = ["run_id", "status", "steps", "final_reward", "best_reward", "eval_avg@1", "warnings"]
    rows = [[
        receipt["run_id"],
        summary.get("status", "unknown"),
        summary.get("steps_completed", 0),
        _fmt_num(summary.get("reward", {}).get("final")),
        _fmt_num(summary.get("reward", {}).get("best")),
        _fmt_num(eval_summary.get("avg_at_1")),
        summary.get("warnings", {}).get("no_trajectory_count", 0),
    ]]
    return ascii_table(headers, rows)


def render_run_comparison(receipts: list[dict[str, Any]]) -> str:
    headers = [
        "run_id",
        "model",
        "status",
        "steps",
        "mean_reward",
        "final_reward",
        "eval_avg@1",
        "no_response%",
        "warnings",
    ]
    rows: list[list[Any]] = []
    for receipt in receipts:
        summary = receipt["summary"]
        eval_summary = summary.get("latest_eval") or {}
        rows.append([
            receipt["run_id"],
            receipt.get("model") or summary.get("model") or "-",
            summary.get("status", "unknown"),
            summary.get("steps_completed", 0),
            _fmt_num(summary.get("reward", {}).get("mean")),
            _fmt_num(summary.get("reward", {}).get("final")),
            _fmt_num(eval_summary.get("avg_at_1")),
            _fmt_num(eval_summary.get("no_response_pct")),
            summary.get("warnings", {}).get("no_trajectory_count", 0),
        ])
    return ascii_table(headers, rows)


def save_receipt(run_root: Path, payload: dict[str, Any]) -> Path:
    run_root.mkdir(parents=True, exist_ok=True)
    out_path = run_root / "receipt.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return out_path


def load_receipt(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _fmt_num(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.4f}"
