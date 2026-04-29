"""Leakage-safe Campsite-style grid validator and projection utilities.

Rows generated from this module expose only prompt-derived constraints:
fixed T cells, row/column C signatures, and adjacency rules. The projection
gate may use those public constraints plus a candidate grid, but not the
canonical target grid.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import html
import itertools
import json
import random
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SYMBOLS = ("T", "C", "X")
ENV_FAMILY = "intellect3_logic_camp_gate"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def grid_to_text(grid: list[list[str]]) -> str:
    return "\n".join("".join(row) for row in grid)


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def neighbors4(r: int, c: int, height: int, width: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < height and 0 <= nc < width:
            out.append((nr, nc))
    return out


def neighbors8(r: int, c: int, height: int, width: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
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


def fixed_tents_from_grid(grid: list[list[str]]) -> list[list[int]]:
    tents: list[list[int]] = []
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == "T":
                tents.append([r + 1, c + 1])
    return tents


def blank_grid(height: int, width: int) -> list[list[str]]:
    return [["X" for _ in range(width)] for _ in range(height)]


def candidate_distance(a: list[list[str]], b: list[list[str]]) -> int:
    if not a or not b or len(a) != len(b) or len(a[0]) != len(b[0]):
        return 10**9
    return sum(1 for r in range(len(a)) for c in range(len(a[0])) if a[r][c] != b[r][c])


def cell_accuracy(candidate: list[list[str]] | None, expected: list[list[str]]) -> float:
    if candidate is None:
        return 0.0
    if len(candidate) != len(expected) or len(candidate[0]) != len(expected[0]):
        return 0.0
    total = len(expected) * len(expected[0])
    return sum(
        1
        for r in range(len(expected))
        for c in range(len(expected[0]))
        if candidate[r][c] == expected[r][c]
    ) / max(1, total)


def parse_grid(text: Any, height: int, width: int) -> list[list[str]] | None:
    if isinstance(text, list):
        return parse_grid_value(text, height, width)

    raw = str(text or "").strip()
    if not raw:
        return None

    if raw.startswith("["):
        try:
            parsed = ast.literal_eval(raw)
        except Exception:
            parsed = None
        if parsed is not None:
            grid = parse_grid_value(parsed, height, width)
            if grid is not None:
                return grid

    valid_lines: list[str] = []
    for line in raw.splitlines():
        compact = re.sub(r"[\s|,;\[\]'\"]+", "", line.strip().upper())
        if len(compact) == width and set(compact).issubset(set(SYMBOLS)):
            valid_lines.append(compact)
    if len(valid_lines) < height:
        return None
    for start in range(0, len(valid_lines) - height + 1):
        block = valid_lines[start : start + height]
        if len(block) == height:
            return [list(row) for row in block]
    return None


def parse_grid_value(value: Any, height: int, width: int) -> list[list[str]] | None:
    if not isinstance(value, list) or len(value) != height:
        return None
    grid: list[list[str]] = []
    for raw_row in value:
        if isinstance(raw_row, str):
            row = list(raw_row.strip().upper())
        elif isinstance(raw_row, list):
            row = [str(cell).strip().upper() for cell in raw_row]
        else:
            return None
        if len(row) != width or any(cell not in SYMBOLS for cell in row):
            return None
        grid.append(row)
    return grid


def public_constraints(row: dict[str, Any]) -> dict[str, Any]:
    validator = row["validator"]
    return {
        "height": validator["height"],
        "width": validator["width"],
        "symbols": list(SYMBOLS),
        "fixed_tents_1_indexed": validator["fixed_tents"],
        "row_c_counts": validator["row_c_counts"],
        "col_c_counts": validator["col_c_counts"],
        "rules": [
            "fixed_t_cells_exact",
            "each_t_has_exactly_one_orthogonal_c",
            "each_c_has_exactly_one_orthogonal_t",
            "no_two_c_touch_orthogonally_or_diagonally",
            "all_other_cells_x",
        ],
    }


def prompt_for_row(height: int, width: int, tents: list[list[int]], rows: list[int], cols: list[int]) -> str:
    tent_text = ", ".join(f"({r},{c})" for r, c in tents)
    row_text = ", ".join(f"r{i + 1}={value}" for i, value in enumerate(rows))
    col_text = ", ".join(f"c{i + 1}={value}" for i, value in enumerate(cols))
    return (
        "Solve this campsite micro-grid.\n\n"
        "Symbols: T is a fixed tent/anchor, C is a camp, X is empty.\n"
        f"Grid size: {height} rows x {width} columns.\n"
        f"Fixed T cells, 1-indexed row,column: {tent_text}.\n"
        f"Row C counts: {row_text}.\n"
        f"Column C counts: {col_text}.\n\n"
        "Rules:\n"
        "1. Keep exactly the listed T cells as T; do not add extra T cells.\n"
        "2. Each T must have exactly one orthogonally adjacent C.\n"
        "3. Each C must be orthogonally adjacent to exactly one T.\n"
        "4. No two C cells may touch orthogonally or diagonally.\n"
        "5. Every non-T and non-C cell must be X.\n\n"
        f"Return only the grid: exactly {height} lines, exactly {width} characters per line, using only T C X."
    )


def constraint_details(row: dict[str, Any], grid: list[list[str]] | None) -> dict[str, Any]:
    validator = row["validator"]
    height = int(validator["height"])
    width = int(validator["width"])
    expected_tents = {tuple(item) for item in validator["fixed_tents"]}
    details: dict[str, Any] = {
        "parse_ok": grid is not None,
        "shape_ok": False,
        "fixed_tents_ok": False,
        "no_extra_tents_ok": False,
        "row_c_signature_ok": False,
        "col_c_signature_ok": False,
        "camp_no_touch_ok": False,
        "each_t_one_c_ok": False,
        "each_c_one_t_ok": False,
    }
    if grid is None:
        return details
    details["shape_ok"] = len(grid) == height and all(len(grid_row) == width for grid_row in grid)
    if not details["shape_ok"]:
        return details

    actual_tents = {
        (r + 1, c + 1)
        for r in range(height)
        for c in range(width)
        if grid[r][c] == "T"
    }
    c_cells = [(r, c) for r in range(height) for c in range(width) if grid[r][c] == "C"]
    details["fixed_tents_ok"] = expected_tents.issubset(actual_tents)
    details["no_extra_tents_ok"] = actual_tents == expected_tents
    details["row_c_signature_ok"] = row_c_counts(grid) == validator["row_c_counts"]
    details["col_c_signature_ok"] = col_c_counts(grid) == validator["col_c_counts"]

    camp_no_touch = True
    for r, c in c_cells:
        if any(grid[nr][nc] == "C" for nr, nc in neighbors8(r, c, height, width)):
            camp_no_touch = False
            break
    details["camp_no_touch_ok"] = camp_no_touch

    each_t = True
    for raw_r, raw_c in expected_tents:
        r = raw_r - 1
        c = raw_c - 1
        adjacent_c = sum(1 for nr, nc in neighbors4(r, c, height, width) if grid[nr][nc] == "C")
        if adjacent_c != 1:
            each_t = False
            break
    details["each_t_one_c_ok"] = each_t

    each_c = True
    for r, c in c_cells:
        adjacent_t = sum(1 for nr, nc in neighbors4(r, c, height, width) if grid[nr][nc] == "T")
        if adjacent_t != 1:
            each_c = False
            break
    details["each_c_one_t_ok"] = each_c
    return details


def constraint_valid_from_details(details: dict[str, Any]) -> bool:
    keys = [
        "shape_ok",
        "fixed_tents_ok",
        "no_extra_tents_ok",
        "row_c_signature_ok",
        "col_c_signature_ok",
        "camp_no_touch_ok",
        "each_t_one_c_ok",
        "each_c_one_t_ok",
    ]
    return all(bool(details.get(key)) for key in keys)


def proposal_tier(details: dict[str, Any], exact_success: bool) -> str:
    if not details.get("parse_ok"):
        return "none"
    if not details.get("shape_ok"):
        return "none"
    if exact_success:
        return "full_candidate"
    if (
        details.get("fixed_tents_ok")
        and details.get("no_extra_tents_ok")
        and details.get("row_c_signature_ok")
        and details.get("col_c_signature_ok")
    ):
        return "partial_semantic"
    if details.get("fixed_tents_ok") and details.get("no_extra_tents_ok"):
        return "weak_surface"
    return "weak_surface"


def validate_output(row: dict[str, Any], output: str) -> dict[str, Any]:
    validator = row["validator"]
    height = int(validator["height"])
    width = int(validator["width"])
    grid = parse_grid(output, height, width)
    expected_grid = parse_grid(row["canonical_output"], height, width)
    if expected_grid is None:
        raise ValueError(f"canonical grid failed to parse for {row['row_id']}")
    details = constraint_details(row, grid)
    constraint_valid = constraint_valid_from_details(details)
    exact_success = bool(grid is not None and grid == expected_grid)
    details.update(
        {
            "row_c_counts_actual": row_c_counts(grid) if grid else [],
            "col_c_counts_actual": col_c_counts(grid) if grid else [],
            "row_c_counts_expected": validator["row_c_counts"],
            "col_c_counts_expected": validator["col_c_counts"],
            "cell_accuracy": round(cell_accuracy(grid, expected_grid), 6),
            "proposal_tier": proposal_tier(details, exact_success),
        }
    )
    return {
        "contract_valid": bool(constraint_valid),
        "semantic_valid": bool(constraint_valid),
        "exact_success": exact_success,
        "cell_accuracy": details["cell_accuracy"],
        "proposal_tier": details["proposal_tier"],
        "details": details,
    }


def solve_from_constraints(row: dict[str, Any], max_solutions: int = 5000) -> list[list[list[str]]]:
    validator = row["validator"]
    height = int(validator["height"])
    width = int(validator["width"])
    tents = {tuple(item) for item in validator["fixed_tents"]}
    target_rows = list(validator["row_c_counts"])
    target_cols = list(validator["col_c_counts"])
    row_options: list[list[set[int]]] = []

    for r in range(height):
        available_cols = [c for c in range(width) if (r + 1, c + 1) not in tents]
        options: list[set[int]] = []
        for combo in itertools.combinations(available_cols, target_rows[r]):
            cols = set(combo)
            if any((c + 1) in cols for c in cols):
                continue
            options.append(cols)
        row_options.append(options)

    solutions: list[list[list[str]]] = []

    def backtrack(r: int, prev_c_cols: set[int], col_counts: list[int], selected: list[set[int]]) -> None:
        if len(solutions) >= max_solutions:
            return
        if r == height:
            if col_counts != target_cols:
                return
            grid = blank_grid(height, width)
            for raw_r, raw_c in tents:
                grid[raw_r - 1][raw_c - 1] = "T"
            for rr, cols in enumerate(selected):
                for cc in cols:
                    grid[rr][cc] = "C"
            if constraint_valid_from_details(constraint_details(row, grid)):
                solutions.append(grid)
            return
        for cols in row_options[r]:
            if any(c in prev_c_cols or c - 1 in prev_c_cols or c + 1 in prev_c_cols for c in cols):
                continue
            next_counts = list(col_counts)
            ok = True
            for c in cols:
                next_counts[c] += 1
                if next_counts[c] > target_cols[c]:
                    ok = False
                    break
            if not ok:
                continue
            remaining_rows = height - r - 1
            if any(next_counts[c] + remaining_rows < target_cols[c] for c in range(width)):
                continue
            backtrack(r + 1, cols, next_counts, selected + [cols])

    backtrack(0, set(), [0 for _ in range(width)], [])
    return solutions


def project_output(row: dict[str, Any], output: str) -> tuple[str | None, dict[str, Any]]:
    validator = row["validator"]
    height = int(validator["height"])
    width = int(validator["width"])
    candidate = parse_grid(output, height, width)
    if candidate is None:
        return None, {"projected": False, "reason": "candidate_parse_failure"}
    solutions = solve_from_constraints(row)
    if not solutions:
        return None, {"projected": False, "reason": "no_prompt_constraint_solution"}
    best = min(solutions, key=lambda grid: (candidate_distance(candidate, grid), grid_to_text(grid)))
    return grid_to_text(best), {
        "projected": True,
        "projection_source": "prompt_constraints_min_edit",
        "candidate_distance": candidate_distance(candidate, best),
        "valid_solution_count_from_prompt_constraints": len(solutions),
        "target_grid_used_by_projection": False,
    }


def is_valid_generated_solution(grid: list[list[str]]) -> bool:
    height = len(grid)
    width = len(grid[0]) if grid else 0
    row = make_row_payload("tmp", grid, "train")
    return constraint_valid_from_details(constraint_details(row, grid))


def make_row_payload(row_id: str, grid: list[list[str]], split: str) -> dict[str, Any]:
    height = len(grid)
    width = len(grid[0])
    tents = fixed_tents_from_grid(grid)
    rows = row_c_counts(grid)
    cols = col_c_counts(grid)
    canonical_output = grid_to_text(grid)
    validator = {
        "type": "camp_grid",
        "height": height,
        "width": width,
        "fixed_tents": tents,
        "row_c_counts": rows,
        "col_c_counts": cols,
    }
    payload = {
        "row_id": row_id,
        "env_family": ENV_FAMILY,
        "split": split,
        "prompt": prompt_for_row(height, width, tents, rows, cols),
        "canonical_output": canonical_output,
        "canonical_sha256": text_sha256(canonical_output),
        "validator": validator,
        "failure_labels": [
            "parse_failure",
            "shape_mismatch",
            "fixed_tents_error",
            "c_signature_mismatch",
            "camp_adjacency_error",
            "cell_commit_error",
        ],
        "leakage_audit": {
            "target_grid_in_prompt": False,
            "projection_uses_target_grid": False,
            "signature_source": "prompt_visible_row_col_c_counts",
            "fixed_t_source": "prompt_visible_fixed_t_cells",
        },
    }
    return payload


def generate_solution_candidate(rng: random.Random, height: int, width: int, camps: int) -> list[list[str]] | None:
    cells = [(r, c) for r in range(height) for c in range(width)]
    rng.shuffle(cells)
    c_cells: list[tuple[int, int]] = []
    for cell in cells:
        if any(abs(cell[0] - other[0]) <= 1 and abs(cell[1] - other[1]) <= 1 for other in c_cells):
            continue
        c_cells.append(cell)
        if len(c_cells) == camps:
            break
    if len(c_cells) != camps:
        return None

    t_cells: list[tuple[int, int]] = []
    for c_cell in sorted(c_cells):
        choices = [
            item
            for item in neighbors4(c_cell[0], c_cell[1], height, width)
            if item not in c_cells
            and item not in t_cells
            and sum(1 for other_c in c_cells if item in neighbors4(other_c[0], other_c[1], height, width)) == 1
        ]
        rng.shuffle(choices)
        if not choices:
            return None
        t_cells.append(choices[0])

    grid = blank_grid(height, width)
    for r, c in c_cells:
        grid[r][c] = "C"
    for r, c in t_cells:
        grid[r][c] = "T"
    if not is_valid_generated_solution(grid):
        return None
    return grid


def generate_rows(target_rows: int = 12, seed: int = 43027) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    sizes = [(4, 4, 3), (4, 5, 4), (5, 4, 4), (5, 5, 5)]
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    attempts = 0
    while len(rows) < target_rows and attempts < 20000:
        attempts += 1
        height, width, camps = sizes[attempts % len(sizes)]
        grid = generate_solution_candidate(rng, height, width, camps)
        if grid is None:
            continue
        row_id = f"camp_gate_{len(rows) + 1:03d}_{height}x{width}_{camps}c"
        payload = make_row_payload(row_id, grid, "leakage_safe_micro")
        solutions = solve_from_constraints(payload, max_solutions=100)
        payload["leakage_audit"]["solution_count_from_prompt_constraints"] = len(solutions)
        payload["leakage_audit"]["unique_solution_from_prompt_constraints"] = len(solutions) == 1
        if len(solutions) != 1:
            continue
        digest = payload["canonical_sha256"]
        if digest in seen:
            continue
        seen.add(digest)
        rows.append(payload)
    if len(rows) != target_rows:
        raise RuntimeError(f"generated {len(rows)} rows, wanted {target_rows}")
    return rows


def weak_surface_candidate(row: dict[str, Any]) -> str:
    validator = row["validator"]
    grid = blank_grid(int(validator["height"]), int(validator["width"]))
    for raw_r, raw_c in validator["fixed_tents"]:
        grid[raw_r - 1][raw_c - 1] = "T"
    return grid_to_text(grid)


def partial_semantic_candidate(row: dict[str, Any]) -> str:
    grid = parse_grid(row["canonical_output"], row["validator"]["height"], row["validator"]["width"])
    if grid is None:
        return weak_surface_candidate(row)
    height = len(grid)
    width = len(grid[0])
    c_cells = [(r, c) for r in range(height) for c in range(width) if grid[r][c] == "C"]
    for r1, c1 in c_cells:
        for r2, c2 in c_cells:
            if r1 == r2 or c1 == c2:
                continue
            if grid[r1][c2] != "X" or grid[r2][c1] != "X":
                continue
            candidate = [list(row_cells) for row_cells in grid]
            candidate[r1][c1] = "X"
            candidate[r2][c2] = "X"
            candidate[r1][c2] = "C"
            candidate[r2][c1] = "C"
            verdict = validate_output(row, grid_to_text(candidate))
            if not verdict["exact_success"] and verdict["details"]["row_c_signature_ok"] and verdict["details"]["col_c_signature_ok"]:
                return grid_to_text(candidate)
    for r, row_cells in enumerate(grid):
        for c, cell in enumerate(row_cells):
            if cell == "C":
                grid[r][c] = "X"
                return grid_to_text(grid)
    return grid_to_text(grid)


def canonical_tier_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    generated_at = utc_now()
    candidates: list[dict[str, Any]] = []
    for row in rows:
        examples = {
            "none_candidate": "I cannot solve this grid.",
            "weak_surface_candidate": weak_surface_candidate(row),
            "partial_semantic_candidate": partial_semantic_candidate(row),
            "full_candidate": row["canonical_output"],
        }
        for arm, output in examples.items():
            candidates.append(
                {
                    "row_id": row["row_id"],
                    "arm": arm,
                    "output": output,
                    "evidence_class": "no_model_proposal_tier_smoke",
                    "generated_at_utc": generated_at,
                }
            )
            projected, projection = project_output(row, output)
            if projected is not None:
                candidates.append(
                    {
                        "row_id": row["row_id"],
                        "arm": f"{arm}_metta_projection",
                        "output": projected,
                        "evidence_class": "no_model_proposal_tier_smoke",
                        "generated_at_utc": generated_at,
                        "projection": projection,
                    }
                )
    return candidates


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n")


def evaluate_candidates(rows: list[dict[str, Any]], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {row["row_id"]: row for row in rows}
    evaluated: list[dict[str, Any]] = []
    for candidate in candidates:
        row = by_id[candidate["row_id"]]
        verdict = validate_output(row, str(candidate.get("output", "")))
        evaluated.append({**candidate, "env_family": row["env_family"], **verdict})
    return evaluated


def summarize_evaluated(evaluated: list[dict[str, Any]]) -> dict[str, Any]:
    arms = sorted({row["arm"] for row in evaluated})
    by_arm: dict[str, dict[str, Any]] = {}
    for arm in arms:
        rows = [row for row in evaluated if row["arm"] == arm]
        tier_counts = Counter(str(row.get("proposal_tier", "unknown")) for row in rows)
        by_arm[arm] = {
            "rows": len(rows),
            "contract_valid": sum(1 for row in rows if row["contract_valid"]),
            "semantic_valid": sum(1 for row in rows if row["semantic_valid"]),
            "exact_success": sum(1 for row in rows if row["exact_success"]),
            "avg_cell_accuracy": round(sum(float(row.get("cell_accuracy", 0.0)) for row in rows) / max(1, len(rows)), 6),
            "exact_rate": round(sum(1 for row in rows if row["exact_success"]) / max(1, len(rows)), 6),
            "contract_rate": round(sum(1 for row in rows if row["contract_valid"]) / max(1, len(rows)), 6),
            "proposal_tier_counts": dict(tier_counts),
        }
    return {
        "rows": len({row["row_id"] for row in evaluated}),
        "arms": by_arm,
        "evaluated_count": len(evaluated),
    }


def render_results_md(title: str, payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        f"# {title}",
        "",
        f"Generated: `{payload.get('generated_at_utc', utc_now())}`",
        "",
        f"Evidence class: `{payload.get('evidence_class', 'unknown')}`",
        "",
        "## Arm Summary",
        "",
        "| Arm | Rows | Exact | Exact Rate | Contract Valid | Avg Cell Acc | Tier Counts |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for arm, metrics in summary["arms"].items():
        tiers = ", ".join(f"{key}:{value}" for key, value in sorted(metrics["proposal_tier_counts"].items()))
        lines.append(
            f"| `{arm}` | {metrics['rows']} | {metrics['exact_success']} | {metrics['exact_rate']:.4f} | "
            f"{metrics['contract_valid']} | {metrics['avg_cell_accuracy']:.4f} | {tiers or '-'} |"
        )
    lines.extend(
        [
            "",
            "## Failed Rows",
            "",
            "| Row | Arm | Tier | Exact | Contract | Cell Acc | Output |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    failures = [row for row in payload["evaluated"] if not row["exact_success"]]
    if not failures:
        lines.append("| - | - | - | - | - | - | No failures |")
    for row in failures[:120]:
        output = html.escape(str(row.get("output", "")).replace("\n", "\\n")).replace("|", "\\|")
        lines.append(
            f"| `{row['row_id']}` | `{row['arm']}` | `{row.get('proposal_tier', '-')}` | "
            f"{int(row['exact_success'])} | {int(row['contract_valid'])} | {float(row.get('cell_accuracy', 0.0)):.4f} | "
            f"<code>{output[:220]}</code> |"
        )
    lines.extend(
        [
            "",
            "## Claim Audit",
            "",
            "- Projection arms use prompt-visible constraints only: fixed T cells, row/column C counts, and adjacency rules.",
            "- Target grids are used for scoring and uniqueness audit, not as projection inputs.",
            "- If projection succeeds from weak-surface candidates, report it as symbolic closure over public constraints, not model reasoning.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate leakage-safe camp-gate candidates.")
    parser.add_argument("--rows", required=True, type=Path)
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--out-json", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    parser.add_argument("--title", default="Logic Signature Camp-Gate Results")
    parser.add_argument("--evidence-class", default="candidate_validation")
    args = parser.parse_args()

    rows = load_jsonl(args.rows)
    candidates = load_jsonl(args.candidates)
    evaluated = evaluate_candidates(rows, candidates)
    payload = {
        "generated_at_utc": utc_now(),
        "evidence_class": args.evidence_class,
        "summary": summarize_evaluated(evaluated),
        "evaluated": evaluated,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    args.out_md.write_text(render_results_md(args.title, payload), encoding="utf-8")
    print(args.out_md)
    print(args.out_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
