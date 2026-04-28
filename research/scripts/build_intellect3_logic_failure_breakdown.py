"""Build per-problem Intellect-3 logic failure breakdowns.

This consumes existing prediction receipts and emits both aggregate failure
taxonomies and row-level failed-problem tables.  It does not run models.
"""

from __future__ import annotations

import argparse
import ast
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
GENERATED = ROOT / "research" / "generated"

DEFAULT_RUNS = [
    Path(r"C:\projects\trm_observability_harness\data\qwen35_4b_intellect3_logic_hybrid_25\predictions.jsonl"),
    Path(r"C:\projects\trm_observability_harness\data\qwen27b_intellect3_logic_hybrid_200\predictions.jsonl"),
    ROOT / "data" / "qwen35_4b_intellect3_logic_hybrid_10_no_trm" / "predictions.jsonl",
]

SYMBOLS = ("T", "C", "X")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Intellect-3 logic failure breakdowns.")
    parser.add_argument("--predictions", action="append", default=None)
    parser.add_argument("--out-dir", default=str(GENERATED / "intellect3_logic_failure_breakdown"))
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            rows.append(json.loads(text))
    return rows


def parse_grid(text: Any) -> list[list[str]] | None:
    if isinstance(text, list):
        value = text
    else:
        try:
            value = ast.literal_eval(str(text or "").strip())
        except Exception:
            return None
    if not isinstance(value, list) or not value:
        return None
    grid: list[list[str]] = []
    width: int | None = None
    for row in value:
        if not isinstance(row, list) or not row:
            return None
        parsed_row = [str(cell).strip() for cell in row]
        if any(cell not in SYMBOLS for cell in parsed_row):
            return None
        if width is None:
            width = len(parsed_row)
        elif len(parsed_row) != width:
            return None
        grid.append(parsed_row)
    return grid


def symbol_counts(values: list[str]) -> dict[str, int]:
    counts = Counter(values)
    return {symbol: int(counts.get(symbol, 0)) for symbol in SYMBOLS}


def count_grid_symbols(grid: list[list[str]]) -> dict[str, int]:
    counts = Counter(cell for row in grid for cell in row)
    return {symbol: int(counts.get(symbol, 0)) for symbol in SYMBOLS}


def grid_shape(grid: list[list[str]]) -> tuple[int, int]:
    return len(grid), len(grid[0]) if grid else 0


def row_symbol_signature(grid: list[list[str]], symbol: str) -> list[int]:
    return [sum(1 for cell in row if cell == symbol) for row in grid]


def col_symbol_signature(grid: list[list[str]], symbol: str) -> list[int]:
    height, width = grid_shape(grid)
    return [sum(1 for r in range(height) if grid[r][c] == symbol) for c in range(width)]


def analyze_prediction(record: dict[str, Any]) -> dict[str, Any]:
    expected = parse_grid(record.get("expected_action"))
    final = record.get("final") or {}
    predicted = parse_grid(final.get("action") or final.get("raw_action") or final.get("raw_text"))
    exact = bool(final.get("exact_match"))
    accuracy = float(final.get("grid_cell_accuracy") or 0.0)
    result: dict[str, Any] = {
        "row_id": record.get("row_id"),
        "arm": record.get("arm"),
        "exact_match": exact,
        "grid_cell_accuracy": accuracy,
        "output_status": final.get("output_status"),
        "visible_output_emitted": bool(final.get("visible_output_emitted")),
        "failure_tags": [],
        "wrong_cells": None,
        "symbol_confusions": {},
        "expected_symbol_counts": {},
        "predicted_symbol_counts": {},
        "row_t_mismatches": None,
        "col_t_mismatches": None,
        "row_c_mismatches": None,
        "col_c_mismatches": None,
    }
    tags: list[str] = []
    if expected is None:
        tags.append("expected_parse_failure")
        result["failure_tags"] = tags
        return result
    if predicted is None:
        tags.append("prediction_parse_failure")
        result["failure_tags"] = tags
        return result
    if grid_shape(expected) != grid_shape(predicted):
        tags.append("shape_mismatch")
        result["failure_tags"] = tags
        return result
    height, width = grid_shape(expected)
    wrong_cells = 0
    confusions: Counter[str] = Counter()
    for r in range(height):
        for c in range(width):
            exp = expected[r][c]
            pred = predicted[r][c]
            if exp != pred:
                wrong_cells += 1
                confusions[f"{exp}->{pred}"] += 1
    expected_counts = count_grid_symbols(expected)
    predicted_counts = count_grid_symbols(predicted)
    row_t_expected = row_symbol_signature(expected, "T")
    row_t_predicted = row_symbol_signature(predicted, "T")
    col_t_expected = col_symbol_signature(expected, "T")
    col_t_predicted = col_symbol_signature(predicted, "T")
    row_c_expected = row_symbol_signature(expected, "C")
    row_c_predicted = row_symbol_signature(predicted, "C")
    col_c_expected = col_symbol_signature(expected, "C")
    col_c_predicted = col_symbol_signature(predicted, "C")
    row_t_mismatches = sum(1 for left, right in zip(row_t_expected, row_t_predicted) if left != right)
    col_t_mismatches = sum(1 for left, right in zip(col_t_expected, col_t_predicted) if left != right)
    row_c_mismatches = sum(1 for left, right in zip(row_c_expected, row_c_predicted) if left != right)
    col_c_mismatches = sum(1 for left, right in zip(col_c_expected, col_c_predicted) if left != right)
    if wrong_cells and not exact:
        tags.append("cell_mismatch")
    if expected_counts.get("T") != predicted_counts.get("T"):
        tags.append("tent_count_mismatch")
    if expected_counts.get("C") != predicted_counts.get("C"):
        tags.append("camp_count_mismatch")
    if row_t_mismatches or col_t_mismatches:
        tags.append("tent_signature_mismatch")
    if row_c_mismatches or col_c_mismatches:
        tags.append("camp_signature_mismatch")
    result.update(
        {
            "failure_tags": sorted(set(tags)),
            "wrong_cells": wrong_cells,
            "symbol_confusions": dict(confusions),
            "expected_symbol_counts": expected_counts,
            "predicted_symbol_counts": predicted_counts,
            "row_t_mismatches": row_t_mismatches,
            "col_t_mismatches": col_t_mismatches,
            "row_c_mismatches": row_c_mismatches,
            "col_c_mismatches": col_c_mismatches,
        }
    )
    return result


def summarize_run(path: Path) -> dict[str, Any]:
    records = load_jsonl(path)
    analyzed = [analyze_prediction(record) for record in records]
    by_arm: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in analyzed:
        by_arm[str(row["arm"])].append(row)
    arm_summaries: dict[str, Any] = {}
    for arm, rows in sorted(by_arm.items()):
        failures = [row for row in rows if not row["exact_match"]]
        tag_counts: Counter[str] = Counter(tag for row in failures for tag in row["failure_tags"])
        confusion_counts: Counter[str] = Counter()
        for row in failures:
            confusion_counts.update(row["symbol_confusions"])
        arm_summaries[arm] = {
            "rows": len(rows),
            "exact_match_rate": sum(1 for row in rows if row["exact_match"]) / max(1, len(rows)),
            "failed_rows": len(failures),
            "avg_grid_cell_accuracy": sum(float(row["grid_cell_accuracy"]) for row in rows) / max(1, len(rows)),
            "avg_wrong_cells_on_failed": (
                sum(int(row["wrong_cells"] or 0) for row in failures) / max(1, len(failures))
            ),
            "failure_tag_counts": dict(tag_counts),
            "symbol_confusion_counts": dict(confusion_counts),
        }
    baseline_arm = "vanilla" if "vanilla" in by_arm else sorted(by_arm)[0]
    compare_arm = "logic_skill_trm" if "logic_skill_trm" in by_arm else sorted(by_arm)[-1]
    by_row_arm = {(str(row["row_id"]), str(row["arm"])): row for row in analyzed}
    problem_rows: list[dict[str, Any]] = []
    row_ids = sorted({str(row["row_id"]) for row in analyzed})
    for row_id in row_ids:
        baseline = by_row_arm.get((row_id, baseline_arm))
        compare = by_row_arm.get((row_id, compare_arm))
        if not baseline or not compare:
            continue
        status = "same"
        if not baseline["exact_match"] and compare["exact_match"]:
            status = "fixed_by_compare"
        elif baseline["exact_match"] and not compare["exact_match"]:
            status = "regressed_by_compare"
        elif not baseline["exact_match"] and not compare["exact_match"]:
            b_acc = float(baseline["grid_cell_accuracy"])
            c_acc = float(compare["grid_cell_accuracy"])
            if c_acc > b_acc:
                status = "partial_improvement"
            elif c_acc < b_acc:
                status = "partial_regression"
            else:
                status = "unfixed"
        problem_rows.append(
            {
                "row_id": row_id,
                "baseline_arm": baseline_arm,
                "compare_arm": compare_arm,
                "baseline_exact": baseline["exact_match"],
                "compare_exact": compare["exact_match"],
                "baseline_accuracy": baseline["grid_cell_accuracy"],
                "compare_accuracy": compare["grid_cell_accuracy"],
                "accuracy_delta": round(float(compare["grid_cell_accuracy"]) - float(baseline["grid_cell_accuracy"]), 4),
                "status": status,
                "compare_wrong_cells": compare["wrong_cells"],
                "compare_failure_tags": compare["failure_tags"],
                "compare_symbol_confusions": compare["symbol_confusions"],
            }
        )
    status_counts = Counter(row["status"] for row in problem_rows)
    return {
        "source_path": str(path),
        "run_id": path.parent.name,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "arms": arm_summaries,
        "baseline_arm": baseline_arm,
        "compare_arm": compare_arm,
        "problem_status_counts": dict(status_counts),
        "problem_rows": problem_rows,
    }


def fmt_rate(value: Any) -> str:
    return f"{float(value):.4f}"


def render_run_md(summary: dict[str, Any]) -> str:
    lines = [
        f"# Intellect-3 Logic Failure Breakdown: {summary['run_id']}",
        "",
        f"Source: `{summary['source_path']}`",
        "",
        "## Arm Summary",
        "",
        "| Arm | Rows | Exact Match | Failed Rows | Avg Cell Acc | Avg Wrong Cells On Failed | Top Failure Tags |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for arm, data in summary["arms"].items():
        tags = ", ".join(f"{tag}:{count}" for tag, count in sorted(data["failure_tag_counts"].items(), key=lambda item: (-item[1], item[0]))[:5]) or "-"
        lines.append(
            f"| `{arm}` | {data['rows']} | {fmt_rate(data['exact_match_rate'])} | {data['failed_rows']} | {fmt_rate(data['avg_grid_cell_accuracy'])} | {fmt_rate(data['avg_wrong_cells_on_failed'])} | {tags} |"
        )
    lines.extend(
        [
            "",
            "## Baseline Vs Compare",
            "",
            f"Baseline arm: `{summary['baseline_arm']}`. Compare arm: `{summary['compare_arm']}`.",
            "",
            "| Status | Count |",
            "| --- | ---: |",
        ]
    )
    for status, count in sorted(summary["problem_status_counts"].items()):
        lines.append(f"| `{status}` | {count} |")
    lines.extend(
        [
            "",
            "## Failed Or Changed Problems",
            "",
            "| Row | Status | Baseline Exact | Compare Exact | Acc Delta | Compare Wrong Cells | Compare Failure Tags | Compare Confusions |",
            "| --- | --- | --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    interesting = [
        row
        for row in summary["problem_rows"]
        if row["status"] != "same" or not row["compare_exact"]
    ]
    for row in interesting[:200]:
        tags = ", ".join(row["compare_failure_tags"]) or "-"
        confusions = ", ".join(f"{key}:{value}" for key, value in sorted(row["compare_symbol_confusions"].items())) or "-"
        lines.append(
            f"| `{row['row_id']}` | `{row['status']}` | {row['baseline_exact']} | {row['compare_exact']} | {row['accuracy_delta']:.4f} | {row['compare_wrong_cells']} | {tags} | {confusions} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    paths = [Path(path).resolve() for path in args.predictions] if args.predictions else DEFAULT_RUNS
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    index: list[dict[str, str]] = []
    for path in paths:
        if not path.exists():
            continue
        summary = summarize_run(path)
        stem = summary["run_id"]
        json_path = out_dir / f"{stem}.failure_breakdown.json"
        md_path = out_dir / f"{stem}.failure_breakdown.md"
        json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        md_path.write_text(render_run_md(summary), encoding="utf-8")
        index.append({"run_id": stem, "json": str(json_path), "markdown": str(md_path), "source": str(path)})
        print(md_path)
    index_path = out_dir / "index.json"
    index_md = out_dir / "index.md"
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    lines = ["# Intellect-3 Logic Failure Breakdown Index", ""]
    for item in index:
        lines.append(f"- `{item['run_id']}`: [{Path(item['markdown']).name}](<{item['markdown']}>)")
    lines.append("")
    index_md.write_text("\n".join(lines), encoding="utf-8")
    print(index_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
