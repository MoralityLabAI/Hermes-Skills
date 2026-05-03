from __future__ import annotations

import json
import re
import statistics
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from .base import BaseTRM
from .schemas import TRMContext, TRMResult


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_mc_report(text: str) -> Dict[str, Any]:
    endings: Dict[str, float] = {}
    secrets: Dict[str, float] = {}
    dead_end_rate = 0.0
    section = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("---"):
            section = line
            continue
        if section == "--- Ending Distribution ---" and line.startswith("page_"):
            match = re.match(r"^(page_[^\s]+)\s+\d+\s+\(\s*([0-9.]+)%\)", line)
            if match:
                endings[match.group(1)] = float(match.group(2))
        elif section == "--- Secret Reachability ---" and line.startswith("page_secret_"):
            match = re.match(r"^(page_secret_[^\s]+)\s+\d+\s+\(\s*([0-9.]+)%\)", line)
            if match:
                secrets[match.group(1)] = float(match.group(2))
        elif line.startswith("Dead-end rate:"):
            try:
                dead_end_rate = float(line.split("(")[1].split("%")[0])
            except Exception:
                dead_end_rate = 0.0
    return {"ending_pct": endings, "secret_pct": secrets, "dead_end_rate_pct": dead_end_rate}


def _find_run_dirs(factory_runs_root: Path) -> Iterable[Path]:
    if not factory_runs_root.exists():
        return []
    return sorted(
        [
            path
            for path in factory_runs_root.iterdir()
            if path.is_dir() and path.name.startswith("macbeth_") and (path / "reports" / "quality_gate_overnight.json").exists()
        ],
        key=lambda p: p.name,
    )


def _find_delta_reports(log_root: Path) -> Iterable[Path]:
    if not log_root.exists():
        return []
    return sorted(log_root.glob("macbeth-overnight-*/loop-*/delta_report.json"))


def _extract_stage(config: Dict[str, Any], stage_name: str) -> Dict[str, Any]:
    for stage in config.get("stages", []):
        if stage.get("name") == stage_name:
            return stage
    raise KeyError(stage_name)


def _update_flag(command: List[str], flag: str, value: Any) -> List[str]:
    rendered = [str(item) for item in command]
    if flag in rendered:
        idx = rendered.index(flag)
        if idx + 1 < len(rendered):
            rendered[idx + 1] = str(value)
    else:
        rendered.extend([flag, str(value)])
    return rendered


class StoryworldRebalanceAdvisorTRM(BaseTRM):
    name = "trm_storyworld_rebalance"
    description = "Mine historical Macbeth runs and emit a deterministic rebalance plan."

    def run(self, context: TRMContext, **kwargs: Any) -> TRMResult:
        config = kwargs["config"]
        factory_runs_root = Path(kwargs["factory_runs_root"])
        log_root = Path(kwargs["log_root"])
        target_ending_ids = kwargs.get(
            "target_ending_ids",
            [
                "page_end_0201",
                "page_end_0202",
                "page_end_0203",
                "page_end_0204",
                "page_secret_0201",
                "page_secret_0202",
                "page_secret_0299",
            ],
        )

        quality_runs: List[Tuple[str, Dict[str, Any]]] = []
        mc_runs: List[Tuple[str, Dict[str, Any]]] = []
        for run_dir in _find_run_dirs(factory_runs_root):
            quality = _load_json(run_dir / "reports" / "quality_gate_overnight.json")
            mc = _parse_mc_report((run_dir / "reports" / "monte_carlo_overnight.txt").read_text(encoding="utf-8"))
            quality_runs.append((run_dir.name, quality))
            mc_runs.append((run_dir.name, mc))

        delta_reports = [_load_json(path) for path in _find_delta_reports(log_root)]
        no_op_count = sum(1 for report in delta_reports if report.get("no_op"))

        share_history: Dict[str, List[float]] = {ending_id: [] for ending_id in target_ending_ids}
        dead_end_rates: List[float] = []
        for _, mc in mc_runs:
            dead_end_rates.append(float(mc.get("dead_end_rate_pct", 0.0)))
            for ending_id in target_ending_ids:
                share_history[ending_id].append(float(mc["ending_pct"].get(ending_id, 0.0)))

        target_share = round(100.0 / len(target_ending_ids), 3)
        mean_share = {
            ending_id: round(statistics.fmean(values), 3) if values else 0.0
            for ending_id, values in share_history.items()
        }
        share_gap = {ending_id: round(target_share - mean_share[ending_id], 3) for ending_id in target_ending_ids}
        weakest_ending = max(target_ending_ids, key=lambda ending_id: share_gap[ending_id])

        secret_ids = [ending_id for ending_id in target_ending_ids if ending_id.startswith("page_secret_")]
        weakest_secret = max(secret_ids, key=lambda ending_id: share_gap[ending_id])
        strongest_secret = min(secret_ids, key=lambda ending_id: share_gap[ending_id])

        failing_checks = Counter()
        super_secret_gate_failures = 0
        for _, quality in quality_runs:
            for failure in quality.get("failures", []):
                failing_checks[failure] += 1
            for ending_id, vars_count, passed in quality.get("polish_metrics", {}).get("secret_checks", []):
                if ending_id == "page_secret_0299" and not passed:
                    super_secret_gate_failures += 1

        config_copy = json.loads(json.dumps(config))
        end_stage = _extract_stage(config_copy, "ending_reachability_balance")
        late_stage = _extract_stage(config_copy, "late_stage_balance")

        average_dead_end = round(statistics.fmean(dead_end_rates), 3) if dead_end_rates else 0.0
        base_bias = 0.08
        base_warped = 0.92
        bias = min(0.14, round(base_bias + max(share_gap[weakest_secret], 0.0) / 400.0 + average_dead_end / 100.0, 3))
        warped_min = min(0.98, round(base_warped + max(share_gap[weakest_ending], 0.0) / 500.0, 3))
        accept_threshold = max(0.08, round(0.12 - max(share_gap[weakest_secret], 0.0) / 500.0, 3))
        target_min = max(0.06, round((target_share - 2.5) / 100.0, 3))
        target_max = min(0.22, round((target_share + 2.5) / 100.0, 3))
        late_bias = min(0.08, round(0.04 + max(share_gap[weakest_secret], 0.0) / 700.0, 3))
        weight = min(1.15, round(0.85 + max(share_gap[weakest_secret], 0.0) / 120.0, 3))

        end_stage["command"] = _update_flag(end_stage["command"], "--bias", bias)
        end_stage["command"] = _update_flag(end_stage["command"], "--warped-min", warped_min)
        late_stage["command"] = _update_flag(late_stage["command"], "--ending-id", weakest_secret)
        late_stage["command"] = _update_flag(late_stage["command"], "--accept-threshold", accept_threshold)
        late_stage["command"] = _update_flag(late_stage["command"], "--weight", weight)
        late_stage["command"] = _update_flag(late_stage["command"], "--bias", late_bias)
        late_stage["command"] = _update_flag(late_stage["command"], "--target-min", target_min)
        late_stage["command"] = _update_flag(late_stage["command"], "--target-max", target_max)

        notes = [
            f"Historical Macbeth runs analyzed: {len(mc_runs)}.",
            f"Historical no-op loop count: {no_op_count}.",
            f"Weakest ending by mean share: {weakest_ending} ({mean_share[weakest_ending]}%).",
            f"Weakest secret by mean share: {weakest_secret} ({mean_share[weakest_secret]}%).",
        ]
        if super_secret_gate_failures:
            notes.append(f"Super-secret gate failed in {super_secret_gate_failures} historical quality reports.")
        if failing_checks:
            notes.append(f"Most common quality failures: {', '.join(name for name, _ in failing_checks.most_common(3))}.")

        payload = {
            "target_share_pct": target_share,
            "historical_runs": [name for name, _ in mc_runs],
            "historical_no_op_loops": no_op_count,
            "historical_mean_share_pct": mean_share,
            "historical_share_gap_pct": share_gap,
            "weakest_ending": weakest_ending,
            "weakest_secret": weakest_secret,
            "strongest_secret": strongest_secret,
            "average_dead_end_rate_pct": average_dead_end,
            "super_secret_gate_failures": super_secret_gate_failures,
            "quality_failure_counts": dict(failing_checks),
            "recommended_overrides": {
                "ending_reachability_balance": {
                    "bias": bias,
                    "warped_min": warped_min,
                },
                "late_stage_balance": {
                    "ending_id": weakest_secret,
                    "accept_threshold": accept_threshold,
                    "weight": weight,
                    "bias": late_bias,
                    "target_min": target_min,
                    "target_max": target_max,
                },
            },
            "patched_config": config_copy,
            "context": asdict(context),
        }
        return TRMResult(
            name=self.name,
            action="emit_rebalance_packet",
            payload=payload,
            confidence=0.87 if mc_runs else 0.58,
            notes=notes,
            continue_pipeline=True,
        )
