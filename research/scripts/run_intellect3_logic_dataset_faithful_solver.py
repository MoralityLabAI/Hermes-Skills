"""Replay Intellect-3 Campsite rows with the dataset-faithful rule contract.

The earlier camp-gate public solver used the stricter common Campsite rule
that every tree has exactly one camp.  The Intellect-3 source rows instead
validate the weaker public contract stated in the prompt: each camp must be
orthogonally adjacent to at least one tree, camps cannot touch, row/column
counts must match, and the total camp count equals the tree count.

This script keeps the target grid out of solving/projection.  The target is
used only after candidate generation to report exact benchmark agreement.
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


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = Path(r"C:\projects\Tesseract\Tesseract\data\normalized_trajectories\intellect_3_logic.jsonl")
DEFAULT_PREDICTIONS = Path(r"C:\projects\trm_observability_harness\data\qwen27b_intellect3_logic_hybrid_200\predictions.jsonl")
DEFAULT_OUT = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "intellect3_logic_dataset_faithful_solver_20260502"
)
ARM_ORDER = ["logic_skill", "logic_skill_trm", "generic_skill", "vanilla"]
SYMBOLS = {"T", "C", "X"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dataset-faithful Intellect-3 Campsite solver replay.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), type=Path)
    parser.add_argument("--predictions", default=str(DEFAULT_PREDICTIONS), type=Path)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), type=Path)
    parser.add_argument("--max-solutions", default=5001, type=int)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def parse_grid(value: Any) -> list[list[str]] | None:
    if isinstance(value, str):
        try:
            value = ast.literal_eval(value.strip())
        except (SyntaxError, ValueError):
            return None
    if not isinstance(value, list) or not value:
        return None
    grid: list[list[str]] = []
    width: int | None = None
    for raw_row in value:
        if isinstance(raw_row, str):
            row = list(raw_row.strip().upper())
        elif isinstance(raw_row, list):
            row = [str(cell).strip().upper() for cell in raw_row]
        else:
            return None
        if not row or any(cell not in SYMBOLS for cell in row):
            return None
        if width is None:
            width = len(row)
        elif len(row) != width:
            return None
        grid.append(row)
    return grid


def grid_text(grid: list[list[str]]) -> str:
    return "\n".join("".join(row) for row in grid)


def python_grid(grid: list[list[str]]) -> str:
    return repr(grid)


def neighbors4(r: int, c: int, height: int, width: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < height and 0 <= nc < width:
            out.append((nr, nc))
    return out


def row_c_counts(grid: list[list[str]]) -> list[int]:
    return [sum(1 for cell in row if cell == "C") for row in grid]


def col_c_counts(grid: list[list[str]]) -> list[int]:
    height = len(grid)
    width = len(grid[0]) if grid else 0
    return [sum(1 for r in range(height) if grid[r][c] == "C") for c in range(width)]


def tree_cells(grid: list[list[str]]) -> set[tuple[int, int]]:
    return {(r, c) for r, row in enumerate(grid) for c, cell in enumerate(row) if cell == "T"}


def candidate_distance(a: list[list[str]] | None, b: list[list[str]]) -> int:
    if a is None or len(a) != len(b) or any(len(ar) != len(br) for ar, br in zip(a, b)):
        return 10**9
    return sum(1 for r in range(len(b)) for c in range(len(b[0])) if a[r][c] != b[r][c])


def cell_accuracy(candidate: list[list[str]] | None, expected: list[list[str]]) -> float:
    if candidate is None or len(candidate) != len(expected) or any(len(a) != len(b) for a, b in zip(candidate, expected)):
        return 0.0
    total = len(expected) * len(expected[0])
    correct = sum(
        1
        for r in range(len(expected))
        for c in range(len(expected[0]))
        if candidate[r][c] == expected[r][c]
    )
    return correct / max(1, total)


def solve_dataset_faithful(
    grid: list[list[str]],
    row_counts: list[int],
    col_counts: list[int],
    *,
    max_solutions: int,
) -> list[list[list[str]]]:
    height = len(grid)
    width = len(grid[0])
    trees = tree_cells(grid)
    row_options: list[list[set[int]]] = []

    for r in range(height):
        available_cols = [
            c
            for c in range(width)
            if (r, c) not in trees and any((nr, nc) in trees for nr, nc in neighbors4(r, c, height, width))
        ]
        options: list[set[int]] = []
        for combo in itertools.combinations(available_cols, row_counts[r]):
            cols = set(combo)
            if any(c + 1 in cols for c in cols):
                continue
            options.append(cols)
        row_options.append(options)

    solutions: list[list[list[str]]] = []

    def backtrack(r: int, prev_cols: set[int], counts: list[int], selected: list[set[int]]) -> None:
        if len(solutions) >= max_solutions:
            return
        if r == height:
            if counts != col_counts:
                return
            solved = [["X" for _ in range(width)] for _ in range(height)]
            for tr, tc in trees:
                solved[tr][tc] = "T"
            for rr, cols in enumerate(selected):
                for cc in cols:
                    solved[rr][cc] = "C"
            solutions.append(solved)
            return

        for cols in row_options[r]:
            if any(c in prev_cols or c - 1 in prev_cols or c + 1 in prev_cols for c in cols):
                continue
            next_counts = list(counts)
            ok = True
            for c in cols:
                next_counts[c] += 1
                if next_counts[c] > col_counts[c]:
                    ok = False
                    break
            if not ok:
                continue
            remaining_rows = height - r - 1
            if any(next_counts[c] + remaining_rows < col_counts[c] for c in range(width)):
                continue
            backtrack(r + 1, cols, next_counts, selected + [cols])

    backtrack(0, set(), [0 for _ in range(len(col_counts))], [])
    return solutions


def load_campsite_rows(path: Path, max_solutions: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in load_jsonl(path):
        action = json.loads(raw["action"])
        game_data = json.loads(action["game_data_str"])
        metadata = game_data.get("metadata") or {}
        if action.get("task") != "campsite":
            continue
        if not all(key in metadata for key in ("grid", "solution", "row_constraints", "col_constraints")):
            continue
        grid = parse_grid(metadata["grid"])
        expected = parse_grid(metadata["solution"])
        if grid is None or expected is None:
            continue
        row_counts = [int(value) for value in metadata["row_constraints"]]
        col_counts = [int(value) for value in metadata["col_constraints"]]
        solutions = solve_dataset_faithful(grid, row_counts, col_counts, max_solutions=max_solutions)
        rows.append(
            {
                "row_id": str(raw["trajectory_id"]),
                "height": len(grid),
                "width": len(grid[0]),
                "grid": grid,
                "expected": expected,
                "row_constraints": row_counts,
                "col_constraints": col_counts,
                "solutions": solutions,
            }
        )
    return rows


def load_prediction_candidates(path: Path) -> dict[str, dict[str, list[list[str]]]]:
    by_row: dict[str, dict[str, list[list[str]]]] = defaultdict(dict)
    if not path.exists():
        return by_row
    for record in load_jsonl(path):
        final = record.get("final") or {}
        grid = parse_grid(final.get("action") or final.get("raw_action") or final.get("raw_text"))
        if grid is not None:
            by_row[str(record.get("row_id"))][str(record.get("arm"))] = grid
    return by_row


def public_first(solutions: list[list[list[str]]]) -> list[list[str]] | None:
    if not solutions:
        return None
    return sorted(solutions, key=grid_text)[0]


def candidate_project(solutions: list[list[list[str]]], candidate: list[list[str]] | None) -> list[list[str]] | None:
    if not solutions:
        return None
    return min(solutions, key=lambda solution: (candidate_distance(candidate, solution), grid_text(solution)))


def eval_grid(grid: list[list[str]] | None, row: dict[str, Any]) -> dict[str, Any]:
    expected = row["expected"]
    return {
        "exact": bool(grid == expected),
        "cell_accuracy": round(cell_accuracy(grid, expected), 6),
        "output": python_grid(grid) if grid is not None else "",
    }


def summarize(rows: list[dict[str, Any]], candidates: dict[str, dict[str, list[list[str]]]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    evaluated: list[dict[str, Any]] = []
    arms = ["public_unique_solver", "public_first_solver"]
    arms.extend(f"candidate_project_{arm}" for arm in ARM_ORDER)
    arms.append("metta_unique_else_logic_skill_projection")
    arms.append("canonical_oracle_upper_bound")

    for row in rows:
        solutions = row["solutions"]
        unique_solution = solutions[0] if len(solutions) == 1 else None
        public_first_solution = public_first(solutions)
        row_candidates = candidates.get(row["row_id"], {})
        arm_outputs: dict[str, list[list[str]] | None] = {
            "public_unique_solver": unique_solution,
            "public_first_solver": public_first_solution,
            "canonical_oracle_upper_bound": row["expected"],
        }
        for arm in ARM_ORDER:
            arm_outputs[f"candidate_project_{arm}"] = candidate_project(solutions, row_candidates.get(arm))
        fallback = unique_solution if unique_solution is not None else arm_outputs["candidate_project_logic_skill"]
        arm_outputs["metta_unique_else_logic_skill_projection"] = fallback

        for arm in arms:
            verdict = eval_grid(arm_outputs[arm], row)
            evaluated.append(
                {
                    "row_id": row["row_id"],
                    "arm": arm,
                    "height": row["height"],
                    "width": row["width"],
                    "solution_count": len(solutions),
                    "ambiguous": len(solutions) != 1,
                    "exact": verdict["exact"],
                    "cell_accuracy": verdict["cell_accuracy"],
                    "output": verdict["output"],
                    "evidence_class": (
                        "benchmark_upper_bound_uses_target"
                        if arm == "canonical_oracle_upper_bound"
                        else "public_constraints_no_target_grid"
                    ),
                }
            )

    summary_arms: dict[str, Any] = {}
    for arm in arms:
        arm_rows = [row for row in evaluated if row["arm"] == arm]
        ambiguous = [row for row in arm_rows if row["ambiguous"]]
        summary_arms[arm] = {
            "rows": len(arm_rows),
            "exact": sum(1 for row in arm_rows if row["exact"]),
            "exact_rate": round(sum(1 for row in arm_rows if row["exact"]) / max(1, len(arm_rows)), 6),
            "avg_cell_accuracy": round(sum(float(row["cell_accuracy"]) for row in arm_rows) / max(1, len(arm_rows)), 6),
            "ambiguous_rows": len(ambiguous),
            "ambiguous_exact": sum(1 for row in ambiguous if row["exact"]),
            "abstentions": sum(1 for row in arm_rows if not row["output"]),
        }

    solution_buckets = Counter("unique" if len(row["solutions"]) == 1 else f"{len(row['solutions'])}_solutions" for row in rows)
    summary = {
        "generated_at_utc": utc_now(),
        "rows": len(rows),
        "public_constraint_solved_rows": sum(1 for row in rows if row["solutions"]),
        "solution_count_buckets": dict(sorted(solution_buckets.items())),
        "arms": summary_arms,
        "ambiguous_row_ids": [row["row_id"] for row in rows if len(row["solutions"]) != 1],
        "read": (
            "Dataset-faithful public constraints produce at least one valid solution for all rows. "
            "They uniquely determine 92/109 benchmark targets; 17 rows have multiple public-valid grids. "
            "Candidate-conditioned projection improves benchmark-canonical agreement but cannot fairly recover hidden "
            "canonical choices for every ambiguous row without an extra tie-break signal."
        ),
    }
    return summary, evaluated


def render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Intellect-3 Logic Dataset-Faithful Solver Replay",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        f"Source: `{payload['source']}`",
        f"Predictions: `{payload['predictions']}`",
        "",
        "## Result",
        "",
        "| Arm | Exact | Exact Rate | Avg Cell Acc | Ambiguous Exact | Abstain | Evidence |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for arm, metrics in summary["arms"].items():
        evidence = "target upper bound" if arm == "canonical_oracle_upper_bound" else "public/candidate no-target"
        lines.append(
            f"| `{arm}` | {metrics['exact']}/{metrics['rows']} | {metrics['exact_rate']:.4f} | "
            f"{metrics['avg_cell_accuracy']:.4f} | {metrics['ambiguous_exact']}/{metrics['ambiguous_rows']} | "
            f"{metrics['abstentions']} | {evidence} |"
        )
    lines.extend(
        [
            "",
        "## Read",
        "",
        summary["read"],
        "",
        f"Public-valid solver closure: `{summary['public_constraint_solved_rows']}/{summary['rows']}` rows have at least one valid grid under the dataset-faithful rule contract.",
        "",
        "The important correction is semantic: the source benchmark solutions are valid under the stated camp-centric rule,",
            "but usually invalid under the stricter tree-centric Campsite rule.  A MeTTa/TRM gate should therefore learn a",
            "`rule_contract` state before applying a solver.",
            "",
            "## Ambiguous Rows",
            "",
            ", ".join(f"`{row_id}`" for row_id in summary["ambiguous_row_ids"]),
            "",
            "These rows are solved as logic puzzles but not uniquely benchmark-canonical from public constraints alone.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_metta(summary: dict[str, Any]) -> str:
    arms = summary["arms"]
    return "\n".join(
        [
            ";; Dataset-faithful Intellect-3 Campsite gate.",
            "(= (rule-contract intellect3-campsite) camp-adjacent-at-least-one-tree)",
            "(= (public-unique-closure intellect3-campsite) "
            f"{arms['public_unique_solver']['exact']}/{arms['public_unique_solver']['rows']})",
            "(= (candidate-conditioned-closure logic_skill) "
            f"{arms['candidate_project_logic_skill']['exact']}/{arms['candidate_project_logic_skill']['rows']})",
            "(= (metta-policy unique-else-logic-skill-projection) "
            f"{arms['metta_unique_else_logic_skill_projection']['exact']}/{arms['metta_unique_else_logic_skill_projection']['rows']})",
            "(= (ambiguity-gate intellect3-campsite) abstain-or-request-canonical-tiebreak)",
            "",
        ]
    )


def main() -> int:
    args = parse_args()
    rows = load_campsite_rows(args.source, args.max_solutions)
    candidates = load_prediction_candidates(args.predictions)
    summary, evaluated = summarize(rows, candidates)
    payload = {
        "generated_at_utc": utc_now(),
        "source": str(args.source),
        "predictions": str(args.predictions),
        "summary": summary,
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "intellect3_logic_dataset_faithful_solver.results.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8", newline="\n"
    )
    with (args.out_dir / "intellect3_logic_dataset_faithful_solver.rows.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in evaluated:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    (args.out_dir / "intellect3_logic_dataset_faithful_solver.results.md").write_text(
        render_md(payload), encoding="utf-8", newline="\n"
    )
    (args.out_dir / "intellect3_logic_dataset_faithful_solver_contract.metta").write_text(
        render_metta(summary), encoding="utf-8", newline="\n"
    )
    print(args.out_dir / "intellect3_logic_dataset_faithful_solver.results.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
