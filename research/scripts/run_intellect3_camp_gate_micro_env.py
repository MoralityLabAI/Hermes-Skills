"""Run an Intellect-3 Campsite MeTTa/TRM gate micro-env.

The env consumes existing Intellect-3 prediction receipts and asks a narrower
question than exact puzzle solving:

1. Can a candidate pass the observed T/C row-column signature gates?
2. If not, can deterministic MeTTa/TRM-style projection repair the candidate?
3. Which failed problems remain unsolved after C-only or coupled T+C repair?

This does not run a model.  It is intended as a decomposable benchmark for the
camp-placement failure mode found in the Intellect-3 receipts.
"""

from __future__ import annotations

import argparse
import ast
import itertools
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
DEFAULT_SOURCE = Path(r"C:\projects\trm_observability_harness\data\qwen27b_intellect3_logic_hybrid_200\predictions.jsonl")
DEFAULT_OUT = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "intellect3_camp_gate_micro_env"
)

SYMBOLS = ("T", "C", "X")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Intellect-3 Campsite camp-gate micro-env.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
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
    width: int | None = None
    grid: list[list[str]] = []
    for raw_row in value:
        if not isinstance(raw_row, list) or not raw_row:
            return None
        row = [str(cell).strip() for cell in raw_row]
        if any(cell not in SYMBOLS for cell in row):
            return None
        if width is None:
            width = len(row)
        elif len(row) != width:
            return None
        grid.append(row)
    return grid


def grid_shape(grid: list[list[str]]) -> tuple[int, int]:
    return len(grid), len(grid[0]) if grid else 0


def row_signature(grid: list[list[str]], symbol: str) -> list[int]:
    return [sum(1 for cell in row if cell == symbol) for row in grid]


def col_signature(grid: list[list[str]], symbol: str) -> list[int]:
    height, width = grid_shape(grid)
    return [sum(1 for r in range(height) if grid[r][c] == symbol) for c in range(width)]


def signature_pass(candidate: list[list[str]], expected: list[list[str]], symbol: str) -> bool:
    return row_signature(candidate, symbol) == row_signature(expected, symbol) and col_signature(
        candidate, symbol
    ) == col_signature(expected, symbol)


def cell_accuracy(candidate: list[list[str]] | None, expected: list[list[str]] | None) -> float:
    if candidate is None or expected is None or grid_shape(candidate) != grid_shape(expected):
        return 0.0
    height, width = grid_shape(expected)
    total = height * width
    correct = sum(1 for r in range(height) for c in range(width) if candidate[r][c] == expected[r][c])
    return correct / max(1, total)


def exact_match(candidate: list[list[str]] | None, expected: list[list[str]] | None) -> bool:
    return bool(candidate is not None and expected is not None and candidate == expected)


def confusion_counts(candidate: list[list[str]] | None, expected: list[list[str]] | None) -> dict[str, int]:
    if candidate is None or expected is None or grid_shape(candidate) != grid_shape(expected):
        return {}
    counts: Counter[str] = Counter()
    height, width = grid_shape(expected)
    for r in range(height):
        for c in range(width):
            if candidate[r][c] != expected[r][c]:
                counts[f"{expected[r][c]}->{candidate[r][c]}"] += 1
    return dict(counts)


def c_only_projection(candidate: list[list[str]], expected: list[list[str]]) -> list[list[str]] | None:
    """Project C cells to the target C row/column signature while preserving candidate T cells."""
    height, width = grid_shape(expected)
    if grid_shape(candidate) != (height, width):
        return None
    target_row_c = row_signature(expected, "C")
    target_col_c = tuple(col_signature(expected, "C"))
    row_options: list[list[tuple[int, tuple[str, ...]]]] = []
    for r in range(height):
        available = [c for c in range(width) if candidate[r][c] != "T"]
        if target_row_c[r] > len(available):
            return None
        options: list[tuple[int, tuple[str, ...]]] = []
        for c_positions in itertools.combinations(available, target_row_c[r]):
            c_set = set(c_positions)
            row = tuple("T" if candidate[r][c] == "T" else ("C" if c in c_set else "X") for c in range(width))
            cost = sum(1 for c in range(width) if row[c] != candidate[r][c])
            options.append((cost, row))
        row_options.append(options)
    return _best_projection_from_row_options(row_options, target_col_c, symbol="C")


def dual_signature_projection(candidate: list[list[str]], expected: list[list[str]]) -> list[list[str]] | None:
    """Project to the target T and C row/column signatures with minimum edit distance."""
    height, width = grid_shape(expected)
    if grid_shape(candidate) != (height, width):
        return None
    target_row_t = row_signature(expected, "T")
    target_row_c = row_signature(expected, "C")
    target_col_t = tuple(col_signature(expected, "T"))
    target_col_c = tuple(col_signature(expected, "C"))
    row_options: list[list[tuple[int, tuple[str, ...]]]] = []
    all_cols = set(range(width))
    for r in range(height):
        options: list[tuple[int, tuple[str, ...]]] = []
        for t_positions in itertools.combinations(range(width), target_row_t[r]):
            remaining = sorted(all_cols - set(t_positions))
            for c_positions in itertools.combinations(remaining, target_row_c[r]):
                t_set = set(t_positions)
                c_set = set(c_positions)
                row = tuple("T" if c in t_set else ("C" if c in c_set else "X") for c in range(width))
                cost = sum(1 for c in range(width) if row[c] != candidate[r][c])
                options.append((cost, row))
        row_options.append(options)
    return _best_dual_projection_from_row_options(row_options, target_col_t, target_col_c)


def _best_projection_from_row_options(
    row_options: list[list[tuple[int, tuple[str, ...]]]], target_cols: tuple[int, ...], *, symbol: str
) -> list[list[str]] | None:
    width = len(target_cols)
    states: dict[tuple[int, ...], tuple[int, list[tuple[str, ...]]]] = {tuple([0] * width): (0, [])}
    for options in row_options:
        next_states: dict[tuple[int, ...], tuple[int, list[tuple[str, ...]]]] = {}
        for cols, (base_cost, rows) in states.items():
            for option_cost, row in options:
                next_cols = tuple(cols[c] + (1 if row[c] == symbol else 0) for c in range(width))
                if any(next_cols[c] > target_cols[c] for c in range(width)):
                    continue
                cost = base_cost + option_cost
                prior = next_states.get(next_cols)
                if prior is None or cost < prior[0]:
                    next_states[next_cols] = (cost, rows + [row])
        states = next_states
        if not states:
            return None
    final = states.get(target_cols)
    if final is None:
        return None
    return [list(row) for row in final[1]]


def _best_dual_projection_from_row_options(
    row_options: list[list[tuple[int, tuple[str, ...]]]], target_col_t: tuple[int, ...], target_col_c: tuple[int, ...]
) -> list[list[str]] | None:
    width = len(target_col_t)
    zero = tuple([0] * width)
    states: dict[tuple[tuple[int, ...], tuple[int, ...]], tuple[int, list[tuple[str, ...]]]] = {(zero, zero): (0, [])}
    for options in row_options:
        next_states: dict[tuple[tuple[int, ...], tuple[int, ...]], tuple[int, list[tuple[str, ...]]]] = {}
        for (cols_t, cols_c), (base_cost, rows) in states.items():
            for option_cost, row in options:
                next_t = tuple(cols_t[c] + (1 if row[c] == "T" else 0) for c in range(width))
                next_c = tuple(cols_c[c] + (1 if row[c] == "C" else 0) for c in range(width))
                if any(next_t[c] > target_col_t[c] or next_c[c] > target_col_c[c] for c in range(width)):
                    continue
                cost = base_cost + option_cost
                key = (next_t, next_c)
                prior = next_states.get(key)
                if prior is None or cost < prior[0]:
                    next_states[key] = (cost, rows + [row])
        states = next_states
        if not states:
            return None
    final = states.get((target_col_t, target_col_c))
    if final is None:
        return None
    return [list(row) for row in final[1]]


def stage_tags(candidate: list[list[str]] | None, expected: list[list[str]] | None) -> list[str]:
    if expected is None:
        return ["expected_parse_failure"]
    if candidate is None:
        return ["candidate_parse_failure"]
    if grid_shape(candidate) != grid_shape(expected):
        return ["shape_mismatch"]
    tags: list[str] = []
    if not signature_pass(candidate, expected, "T"):
        tags.append("t_signature_fail")
    if not signature_pass(candidate, expected, "C"):
        tags.append("c_signature_fail")
    if candidate != expected:
        tags.append("cell_commit_fail")
    return tags


def evaluate_record(record: dict[str, Any]) -> dict[str, Any]:
    expected = parse_grid(record.get("expected_action"))
    final = record.get("final") or {}
    candidate = parse_grid(final.get("action") or final.get("raw_action") or final.get("raw_text"))
    c_repaired = c_only_projection(candidate, expected) if candidate is not None and expected is not None else None
    dual_repaired = dual_signature_projection(candidate, expected) if candidate is not None and expected is not None else None
    return {
        "row_id": str(record.get("row_id")),
        "arm": str(record.get("arm")),
        "original_exact": exact_match(candidate, expected),
        "original_cell_accuracy": round(cell_accuracy(candidate, expected), 6),
        "original_t_signature_pass": bool(candidate is not None and expected is not None and signature_pass(candidate, expected, "T")),
        "original_c_signature_pass": bool(candidate is not None and expected is not None and signature_pass(candidate, expected, "C")),
        "original_stage_tags": stage_tags(candidate, expected),
        "original_confusions": confusion_counts(candidate, expected),
        "c_repair_exact": exact_match(c_repaired, expected),
        "c_repair_cell_accuracy": round(cell_accuracy(c_repaired, expected), 6),
        "c_repair_feasible": c_repaired is not None,
        "c_repair_stage_tags": stage_tags(c_repaired, expected),
        "dual_repair_exact": exact_match(dual_repaired, expected),
        "dual_repair_cell_accuracy": round(cell_accuracy(dual_repaired, expected), 6),
        "dual_repair_feasible": dual_repaired is not None,
        "dual_repair_stage_tags": stage_tags(dual_repaired, expected),
        "dual_repair_confusions": confusion_counts(dual_repaired, expected),
    }


def summarize(rows: list[dict[str, Any]], source: Path) -> dict[str, Any]:
    by_arm: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_arm[row["arm"]].append(row)
    arm_summaries: dict[str, Any] = {}
    for arm, arm_rows in sorted(by_arm.items()):
        original_failures = [row for row in arm_rows if not row["original_exact"]]
        unresolved_after_dual = [row for row in arm_rows if not row["dual_repair_exact"]]
        original_tags = Counter(tag for row in original_failures for tag in row["original_stage_tags"])
        dual_tags = Counter(tag for row in unresolved_after_dual for tag in row["dual_repair_stage_tags"])
        original_confusions = Counter()
        dual_confusions = Counter()
        for row in original_failures:
            original_confusions.update(row["original_confusions"])
        for row in unresolved_after_dual:
            dual_confusions.update(row["dual_repair_confusions"])
        arm_summaries[arm] = {
            "rows": len(arm_rows),
            "original_exact_rate": rate(arm_rows, "original_exact"),
            "original_avg_cell_accuracy": avg(arm_rows, "original_cell_accuracy"),
            "original_t_signature_pass_rate": rate(arm_rows, "original_t_signature_pass"),
            "original_c_signature_pass_rate": rate(arm_rows, "original_c_signature_pass"),
            "c_repair_exact_rate": rate(arm_rows, "c_repair_exact"),
            "c_repair_avg_cell_accuracy": avg(arm_rows, "c_repair_cell_accuracy"),
            "dual_repair_exact_rate": rate(arm_rows, "dual_repair_exact"),
            "dual_repair_avg_cell_accuracy": avg(arm_rows, "dual_repair_cell_accuracy"),
            "fixed_by_c_repair": sum(1 for row in arm_rows if not row["original_exact"] and row["c_repair_exact"]),
            "fixed_by_dual_repair": sum(1 for row in arm_rows if not row["original_exact"] and row["dual_repair_exact"]),
            "unresolved_after_dual": len(unresolved_after_dual),
            "original_stage_tag_counts": dict(original_tags),
            "dual_unresolved_stage_tag_counts": dict(dual_tags),
            "original_confusion_counts": dict(original_confusions),
            "dual_unresolved_confusion_counts": dict(dual_confusions),
        }
    return {
        "env_id": "intellect3_camp_gate_micro_env",
        "source_path": str(source),
        "generated_at_utc": utc_now(),
        "rows": len(rows),
        "arms": arm_summaries,
        "problem_rows": rows,
        "read": (
            "C-only repair isolates camp placement failures; dual T+C projection measures whether "
            "a coupled signature gate can convert candidate grids into exact answers."
        ),
    }


def rate(rows: list[dict[str, Any]], key: str) -> float:
    return round(sum(1 for row in rows if row.get(key)) / max(1, len(rows)), 6)


def avg(rows: list[dict[str, Any]], key: str) -> float:
    return round(sum(float(row.get(key) or 0.0) for row in rows) / max(1, len(rows)), 6)


def fmt(value: Any) -> str:
    return f"{float(value):.4f}"


def render_md(summary: dict[str, Any]) -> str:
    lines = [
        "# Intellect-3 Campsite Camp-Gate Micro-Env",
        "",
        f"Source: `{summary['source_path']}`",
        f"Generated: `{summary['generated_at_utc']}`",
        "",
        "MeTTa contract: [`intellect3_camp_gate_contract.metta`](<intellect3_camp_gate_contract.metta>)",
        "",
        summary["read"],
        "",
        "## Arm Summary",
        "",
        "| Arm | Rows | Original Exact | Original Cell Acc | T Sig Pass | C Sig Pass | C Repair Exact | Dual Repair Exact | Fixed By Dual | Unresolved Dual |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for arm, data in summary["arms"].items():
        lines.append(
            f"| `{arm}` | {data['rows']} | {fmt(data['original_exact_rate'])} | {fmt(data['original_avg_cell_accuracy'])} | "
            f"{fmt(data['original_t_signature_pass_rate'])} | {fmt(data['original_c_signature_pass_rate'])} | "
            f"{fmt(data['c_repair_exact_rate'])} | {fmt(data['dual_repair_exact_rate'])} | "
            f"{data['fixed_by_dual_repair']} | {data['unresolved_after_dual']} |"
        )
    lines.extend(
        [
            "",
            "## Failure Tags",
            "",
            "| Arm | Original Tags | Original Confusions | Dual-Unresolved Tags | Dual-Unresolved Confusions |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for arm, data in summary["arms"].items():
        lines.append(
            f"| `{arm}` | {top_counts(data['original_stage_tag_counts'])} | {top_counts(data['original_confusion_counts'])} | "
            f"{top_counts(data['dual_unresolved_stage_tag_counts'])} | {top_counts(data['dual_unresolved_confusion_counts'])} |"
        )
    lines.extend(
        [
            "",
            "## Failed Problem Rows",
            "",
            "| Row | Arm | Original Acc | Original Tags | Original Confusions | C Repair Acc | Dual Repair Acc | Dual Tags | Dual Confusions |",
            "| --- | --- | ---: | --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    interesting = [row for row in summary["problem_rows"] if not row["original_exact"] or not row["dual_repair_exact"]]
    for row in interesting[:300]:
        lines.append(
            f"| `{row['row_id']}` | `{row['arm']}` | {fmt(row['original_cell_accuracy'])} | "
            f"{', '.join(row['original_stage_tags']) or '-'} | {top_counts(row['original_confusions'])} | "
            f"{fmt(row['c_repair_cell_accuracy'])} | {fmt(row['dual_repair_cell_accuracy'])} | "
            f"{', '.join(row['dual_repair_stage_tags']) or '-'} | {top_counts(row['dual_repair_confusions'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_metta_contract() -> str:
    return "\n".join(
        [
            ";; Intellect-3 Campsite camp-gate micro-env contract.",
            ";; The LLM/TRM proposes a grid; MeTTa gates score and repair the proposal.",
            "",
            "(: env_id Symbol)",
            "(= env_id intellect3_camp_gate_micro_env)",
            "",
            "(: symbols (List Symbol))",
            "(= symbols (T C X))",
            "",
            "(: stage_order (List Symbol))",
            "(= stage_order (parse candidate verify_c_signature verify_t_signature repair commit))",
            "",
            "(: metric_exact_match Symbol)",
            "(= metric_exact_match grid_exact_match)",
            "(: metric_cell_accuracy Symbol)",
            "(= metric_cell_accuracy grid_cell_accuracy)",
            "(: metric_c_signature_pass Symbol)",
            "(= metric_c_signature_pass row_col_c_signature_pass)",
            "(: metric_t_signature_pass Symbol)",
            "(= metric_t_signature_pass row_col_t_signature_pass)",
            "",
            "(: gate_parse Symbol)",
            "(= gate_parse TRM_PARSE_GRID)",
            "(: gate_c_signature Symbol)",
            "(= gate_c_signature TRM_CAMP_ROW_COL_SIGNATURE)",
            "(: gate_dual_signature Symbol)",
            "(= gate_dual_signature TRM_TENT_CAMP_ROW_COL_SIGNATURE)",
            "(: gate_commit Symbol)",
            "(= gate_commit TRM_COMMIT_GRID)",
            "",
            "(: repair_c_only Symbol)",
            "(= repair_c_only MIN_EDIT_PROJECT_C_SIGNATURE_PRESERVE_T)",
            "(: repair_dual Symbol)",
            "(= repair_dual MIN_EDIT_PROJECT_T_AND_C_SIGNATURES)",
            "",
            "(: failure_taxonomy (List Symbol))",
            "(= failure_taxonomy (candidate_parse_failure shape_mismatch t_signature_fail c_signature_fail cell_commit_fail))",
            "",
        ]
    )


def top_counts(counts: dict[str, int], limit: int = 5) -> str:
    if not counts:
        return "-"
    return ", ".join(f"{key}:{value}" for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit])


def main() -> int:
    args = parse_args()
    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    records = load_jsonl(source)
    rows = [evaluate_record(record) for record in records]
    summary = summarize(rows, source)
    json_path = out_dir / "intellect3_camp_gate_micro_env.results.json"
    md_path = out_dir / "intellect3_camp_gate_micro_env.results.md"
    metta_path = out_dir / "intellect3_camp_gate_contract.metta"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    md_path.write_text(render_md(summary), encoding="utf-8")
    metta_path.write_text(render_metta_contract(), encoding="utf-8")
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
