"""Replay the camp-gate local run with a public-constraint solver arm."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "research" / "studies" / "2026-04-29-logic-signature-camp-gate-leakage-safe"
ROWS_PATH = STUDY / "rows" / "logic_signature_camp_gate_rows.jsonl"
VALIDATOR_PATH = STUDY / "validators" / "validate_logic_signature_camp_gate.py"
SOURCE_RESULTS = (
    STUDY
    / "results"
    / "local_qwen25_3b_logic_signature_camp_gate"
    / "local_qwen25_3b_logic_signature_camp_gate.results.json"
)
OUT_DIR = STUDY / "results" / "projection_ablation"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def load_validator(path: Path):
    spec = importlib.util.spec_from_file_location("logic_signature_camp_gate_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate_candidate(validator: Any, row: dict[str, Any], output: str, arm: str, diagnostics: dict[str, Any]) -> dict[str, Any]:
    verdict = validator.validate_output(row, output)
    return {
        "ts": utc_now(),
        "row_id": row["row_id"],
        "env_family": row["env_family"],
        "arm": arm,
        "output": output,
        "evidence_class": "live_log_replay_public_constraint_solver",
        "contract_valid": verdict["contract_valid"],
        "semantic_valid": verdict["semantic_valid"],
        "exact_success": verdict["exact_success"],
        "cell_accuracy": verdict["cell_accuracy"],
        "proposal_tier": verdict["proposal_tier"],
        "details": verdict["details"],
        "diagnostics": diagnostics,
    }


def error_candidate(row: dict[str, Any], arm: str, reason: str, diagnostics: dict[str, Any]) -> dict[str, Any]:
    return {
        "ts": utc_now(),
        "row_id": row["row_id"],
        "env_family": row["env_family"],
        "arm": arm,
        "output": "",
        "evidence_class": "live_log_replay_public_constraint_solver",
        "contract_valid": False,
        "semantic_valid": False,
        "exact_success": False,
        "cell_accuracy": 0.0,
        "proposal_tier": "none",
        "details": {"kind": "solver_error", "error": reason},
        "diagnostics": diagnostics,
    }


def summarize(evaluated: list[dict[str, Any]]) -> dict[str, Any]:
    arms = sorted({row["arm"] for row in evaluated})
    by_arm: dict[str, dict[str, Any]] = {}
    for arm in arms:
        rows = [row for row in evaluated if row["arm"] == arm]
        tiers: dict[str, int] = {}
        for row in rows:
            tier = str(row.get("proposal_tier", "unknown"))
            tiers[tier] = tiers.get(tier, 0) + 1
        by_arm[arm] = {
            "rows": len(rows),
            "contract_valid": sum(1 for row in rows if row["contract_valid"]),
            "semantic_valid": sum(1 for row in rows if row["semantic_valid"]),
            "exact_success": sum(1 for row in rows if row["exact_success"]),
            "contract_rate": sum(1 for row in rows if row["contract_valid"]) / max(1, len(rows)),
            "exact_rate": sum(1 for row in rows if row["exact_success"]) / max(1, len(rows)),
            "avg_cell_accuracy": sum(float(row.get("cell_accuracy", 0.0)) for row in rows) / max(1, len(rows)),
            "proposal_tier_counts": tiers,
        }
    return {
        "evidence_class": "live_log_replay_public_constraint_solver",
        "rows": len({row["row_id"] for row in evaluated}),
        "arms": by_arm,
        "note": "Public solver uses frozen prompt constraints only. It is intentionally not candidate-conditioned.",
    }


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Logic Signature Camp-Gate Projection Ablation",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "Evidence class: `live_log_replay_public_constraint_solver`",
        "",
        "This replay fixes the prior parse/shape bottleneck by adding a public-constraint solver arm. It does not replace the candidate-conditioned projection metric.",
        "",
        "## Arm Summary",
        "",
        "| Arm | Rows | Exact | Exact Rate | Contract Valid | Avg Cell Acc | Tier Counts |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for arm, metrics in payload["summary"]["arms"].items():
        tiers = ", ".join(f"{key}:{value}" for key, value in sorted(metrics["proposal_tier_counts"].items()))
        lines.append(
            f"| `{arm}` | {metrics['rows']} | {metrics['exact_success']} | {metrics['exact_rate']:.4f} | "
            f"{metrics['contract_valid']} | {metrics['avg_cell_accuracy']:.4f} | {tiers or '-'} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `candidate_conditioned_projection` is the fair measure of whether the 3B emitted a parseable verifier-visible grid state.",
            "- `public_constraint_solver` shows the stronger closure threshold: once public constraints are machine-visible and unique, the LLM is no longer needed for grid execution.",
            "- The next empirical bottleneck is constraint extraction from less-structured natural-language puzzle statements.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay camp-gate projection with public solver fallback.")
    parser.add_argument("--rows", default=str(ROWS_PATH), type=Path)
    parser.add_argument("--validator", default=str(VALIDATOR_PATH), type=Path)
    parser.add_argument("--source-results", default=str(SOURCE_RESULTS), type=Path)
    parser.add_argument("--out-dir", default=str(OUT_DIR), type=Path)
    args = parser.parse_args()

    rows = load_jsonl(args.rows)
    rows_by_id = {row["row_id"]: row for row in rows}
    validator = load_validator(args.validator)
    source = json.loads(args.source_results.read_text(encoding="utf-8-sig"))

    evaluated: list[dict[str, Any]] = []
    for row in source["evaluated"]:
        if row["arm"] in {"baseline", "pure_trm", "metta_runtime", "metta_signature_projection"}:
            evaluated.append(dict(row))

    metta_by_row = {row["row_id"]: row for row in source["evaluated"] if row["arm"] == "metta_runtime"}
    for row_id, source_row in metta_by_row.items():
        row = rows_by_id[row_id]
        projected, projection = validator.project_output(row, str(source_row.get("output", "")))
        if projected is None:
            evaluated.append(error_candidate(row, "candidate_conditioned_projection", projection.get("reason", "projection_failed"), projection))
        else:
            evaluated.append(evaluate_candidate(validator, row, projected, "candidate_conditioned_projection", projection))

        solved, solver = validator.public_constraint_solver_output(row)
        if solved is None:
            evaluated.append(error_candidate(row, "public_constraint_solver", solver.get("reason", "solver_failed"), solver))
        else:
            evaluated.append(evaluate_candidate(validator, row, solved, "public_constraint_solver", solver))

    payload = {
        "generated_at_utc": utc_now(),
        "source_results": str(args.source_results),
        "rows_path": str(args.rows),
        "validator_path": str(args.validator),
        "summary": summarize(evaluated),
        "evaluated": evaluated,
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_json = args.out_dir / "projection_ablation.results.json"
    out_md = args.out_dir / "projection_ablation.results.md"
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(render_md(payload), encoding="utf-8")
    print(out_md)
    print(out_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
