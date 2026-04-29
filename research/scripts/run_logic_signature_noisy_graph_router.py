"""Evaluate a script-owned graph router for noisy camp-gate constraints.

This is the control-plane version of the local 3B noisy extraction run: the
LLM is not asked to solve or transcribe fields. Instead, typed extraction
gates parse prompt-visible constraints and pass a canonical packet to the
same public solver used by the model benchmarks.
"""

from __future__ import annotations

import html
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import logic_signature_camp_gate_core as core  # noqa: E402


STUDY = ROOT / "research" / "studies" / "2026-04-29-logic-signature-camp-gate-leakage-safe"
ROWS_PATH = STUDY / "rows" / "logic_signature_camp_gate_noisy_extract_rows.jsonl"
OUT_DIR = STUDY / "results" / "noisy_graph_router_script"

NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def number(raw: str) -> int:
    token = raw.strip().lower()
    if token in NUMBER_WORDS:
        return NUMBER_WORDS[token]
    return int(token)


def segment(text: str, start: str, *ends: str) -> str:
    start_index = text.find(start)
    if start_index < 0:
        return ""
    out = text[start_index + len(start) :]
    end_indexes = [out.find(end) for end in ends if out.find(end) >= 0]
    if end_indexes:
        out = out[: min(end_indexes)]
    return out


def parse_dimensions(prompt: str) -> tuple[int, int] | None:
    patterns = [
        r"it is\s+(\w+|\d+)\s+rows tall and\s+(\w+|\d+)\s+columns wide",
        r"board size\s+(\d+)\s+by\s+(\d+)",
        r"map has\s+(\d+)\s+north-south bands and\s+(\d+)\s+west-east files",
        r"height\s+(\d+)\s*,\s*width\s+(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, prompt, flags=re.IGNORECASE)
        if match:
            return number(match.group(1)), number(match.group(2))
    return None


def parse_anchors(prompt: str) -> list[list[int]]:
    anchor_patterns = [
        r"row\s+(\d+)\s*,\s*column\s+(\d+)",
        r"\br(\d+)c(\d+)\b",
        r"\((\d+)\s+from top,\s*(\d+)\s+from left\)",
        r"\bR(\d+)-C(\d+)\b",
    ]
    anchors: list[list[int]] = []
    for pattern in anchor_patterns:
        matches = re.findall(pattern, prompt, flags=re.IGNORECASE)
        if matches:
            anchors.extend([[int(r), int(c)] for r, c in matches])
            break
    return sorted(anchors)


def ordered_pairs_to_counts(pairs: list[tuple[str, str]]) -> list[int]:
    indexed = sorted((int(index), number(value)) for index, value in pairs)
    return [value for _, value in indexed]


def parse_slash_counts(raw: str) -> list[int]:
    return [int(value) for value in re.findall(r"\d+", raw)]


def parse_row_counts(prompt: str) -> list[int]:
    row_segment = segment(
        prompt,
        "Camp totals by row are:",
        ". Camp totals by column",
        ". Column quotas",
        ". Reading column",
        ". For the columns",
    )
    pairs = re.findall(r"row\s+(\d+)\s+gets\s+(\w+|\d+)", row_segment, flags=re.IGNORECASE)
    if pairs:
        return ordered_pairs_to_counts(pairs)

    row_segment = segment(prompt, "Row quotas for C are", "from top row to bottom row")
    if row_segment:
        counts = parse_slash_counts(row_segment)
        if counts:
            return counts

    row_segment = segment(prompt, "Reading row requirements north to south gives", ". Reading column")
    pairs = re.findall(r"\bR(\d+):(\d+)", row_segment, flags=re.IGNORECASE)
    if pairs:
        return ordered_pairs_to_counts(pairs)

    row_segment = segment(prompt, "For the rows, the required camp counts are", ". For the columns")
    pairs = re.findall(r"(\w+|\d+)\s+in lane\s+(\d+)", row_segment, flags=re.IGNORECASE)
    if pairs:
        return ordered_pairs_to_counts([(index, value) for value, index in pairs])

    return []


def parse_col_counts(prompt: str) -> list[int]:
    col_segment = segment(prompt, "Camp totals by column are:", ". T marks")
    pairs = re.findall(r"column\s+(\d+)\s+gets\s+(\w+|\d+)", col_segment, flags=re.IGNORECASE)
    if pairs:
        return ordered_pairs_to_counts(pairs)

    col_segment = segment(prompt, "Column quotas for C are", "from left column to right column")
    if col_segment:
        counts = parse_slash_counts(col_segment)
        if counts:
            return counts

    col_segment = segment(prompt, "Reading column requirements west to east gives", ". T marks")
    pairs = re.findall(r"\bC(\d+):(\d+)", col_segment, flags=re.IGNORECASE)
    if pairs:
        return ordered_pairs_to_counts(pairs)

    col_segment = segment(prompt, "For the columns, the required camp counts are", ". T marks")
    pairs = re.findall(r"(\w+|\d+)\s+in file\s+(\d+)", col_segment, flags=re.IGNORECASE)
    if pairs:
        return ordered_pairs_to_counts([(index, value) for value, index in pairs])

    return []


def graph_router_packet(prompt: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    dimensions = parse_dimensions(prompt)
    anchors = parse_anchors(prompt)
    row_counts = parse_row_counts(prompt)
    col_counts = parse_col_counts(prompt)
    diagnostics: dict[str, Any] = {
        "target_grid_used_by_router": False,
        "gates": {
            "dimension_gate": dimensions is not None,
            "anchor_gate": bool(anchors),
            "row_quota_gate": bool(row_counts),
            "column_quota_gate": bool(col_counts),
        },
    }
    if dimensions is None:
        return None, diagnostics
    packet = {
        "height": dimensions[0],
        "width": dimensions[1],
        "fixed_tents": anchors,
        "row_c_counts": row_counts,
        "col_c_counts": col_counts,
    }
    normalized = core.normalize_constraint_packet(packet)
    diagnostics["raw_packet"] = packet
    diagnostics["normalized"] = normalized is not None
    return normalized, diagnostics


def evaluate(row: dict[str, Any], arm: str, packet: dict[str, Any] | None, diagnostics: dict[str, Any]) -> dict[str, Any]:
    solved_output, solver = core.solve_from_constraint_packet(row, packet)
    verdict = core.validate_output(row, solved_output or "")
    return {
        "ts": utc_now(),
        "row_id": row["row_id"],
        "env_family": row["env_family"],
        "arm": arm,
        "evidence_class": "no_model_prompt_constraint_graph_router",
        "packet_valid": packet is not None,
        "packet_exact": core.constraint_packet_exact(row, packet),
        "solver_unique": bool(solver.get("solved")),
        "solve_exact": bool(verdict["exact_success"]),
        "solve_cell_accuracy": verdict["cell_accuracy"],
        "packet": packet,
        "canonical_packet": core.canonical_constraint_packet(row),
        "solved_output": solved_output or "",
        "solver": solver,
        "diagnostics": diagnostics,
    }


def canonical_result(row: dict[str, Any]) -> dict[str, Any]:
    packet = core.canonical_constraint_packet(row)
    return evaluate(
        row,
        "canonical_packet_solver",
        packet,
        {"target_grid_used_by_router": False, "source": "row_validator_upper_bound"},
    )


def summarize(evaluated: list[dict[str, Any]]) -> dict[str, Any]:
    arms: dict[str, dict[str, Any]] = {}
    for arm in sorted({row["arm"] for row in evaluated}):
        rows = [row for row in evaluated if row["arm"] == arm]
        arms[arm] = {
            "rows": len(rows),
            "packet_valid": sum(1 for row in rows if row["packet_valid"]),
            "packet_exact": sum(1 for row in rows if row["packet_exact"]),
            "solver_unique": sum(1 for row in rows if row["solver_unique"]),
            "solve_exact": sum(1 for row in rows if row["solve_exact"]),
            "solve_exact_rate": sum(1 for row in rows if row["solve_exact"]) / max(1, len(rows)),
            "avg_solve_cell_accuracy": sum(float(row["solve_cell_accuracy"]) for row in rows) / max(1, len(rows)),
        }
    failures_by_gate: dict[str, int] = defaultdict(int)
    for row in evaluated:
        if row["arm"] != "metta_graph_router_script" or row["solve_exact"]:
            continue
        for gate, passed in row.get("diagnostics", {}).get("gates", {}).items():
            if not passed:
                failures_by_gate[gate] += 1
    return {
        "evidence_class": "no_model_prompt_constraint_graph_router",
        "rows": len({row["row_id"] for row in evaluated}),
        "arms": arms,
        "failures_by_gate": dict(failures_by_gate),
    }


def render_contract() -> str:
    return """; Camp-gate noisy constraint extraction graph.
; This contract is a readable MeTTa-style specification for the Python gates.

(= (camp-gate-router $prompt)
   (commit-json
     (dimension-gate $prompt)
     (anchor-gate $prompt)
     (row-quota-gate $prompt)
     (column-quota-gate $prompt)))

(= (dimension-gate $prompt) (script-parse height width))
(= (anchor-gate $prompt) (script-parse fixed_tents_1_indexed))
(= (row-quota-gate $prompt) (script-parse row_c_counts_top_to_bottom))
(= (column-quota-gate $prompt) (script-parse col_c_counts_left_to_right))
(= (solver-gate $packet) (public-constraint-solver $packet))

(claim-boundary target-grid-unused)
(claim-boundary prompt-visible-constraints-only)
(claim-boundary no-llm-solve-step)
"""


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Noisy Camp-Gate Graph Router Script",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "Evidence class: `no_model_prompt_constraint_graph_router`",
        "",
        "This control parses only prompt-visible dimensions, anchors, row quotas, and column quotas, then uses the same public solver as the local 3B extraction benchmark.",
        "",
        "## Arm Summary",
        "",
        "| Arm | Rows | Packet Valid | Packet Exact | Solve Exact | Solve Rate | Avg Cell Acc |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for arm, metrics in payload["summary"]["arms"].items():
        lines.append(
            f"| `{arm}` | {metrics['rows']} | {metrics['packet_valid']} | {metrics['packet_exact']} | "
            f"{metrics['solve_exact']} | {metrics['solve_exact_rate']:.4f} | {metrics['avg_solve_cell_accuracy']:.4f} |"
        )
    failures = [row for row in payload["evaluated"] if row["arm"] == "metta_graph_router_script" and not row["solve_exact"]]
    lines.extend(["", "## Failures", ""])
    if not failures:
        lines.append("No graph-router failures.")
    else:
        lines.extend(["| Row | Packet | Diagnostics |", "| --- | --- | --- |"])
        for row in failures:
            packet = html.escape(json.dumps(row.get("packet"), ensure_ascii=True, sort_keys=True))
            diagnostics = html.escape(json.dumps(row.get("diagnostics"), ensure_ascii=True, sort_keys=True))
            lines.append(f"| `{row['row_id']}` | <code>{packet}</code> | <code>{diagnostics}</code> |")
    lines.extend(
        [
            "",
            "## Method Read",
            "",
            "- `metta_graph_extract` shows how far a 3B can go when the prompt frames extraction as gates.",
            "- `metta_graph_router_script` shows the threshold where typed script gates can own extraction and make the LLM optional for execution.",
            "- This does not claim trained TRM lift; it marks candidate gates for future TRM data collection.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(payload: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "noisy_graph_router.results.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "noisy_graph_router.results.md").write_text(render_md(payload), encoding="utf-8")
    (OUT_DIR / "camp_gate_graph_router_contract.metta").write_text(render_contract(), encoding="utf-8", newline="\n")
    with (OUT_DIR / "noisy_graph_router.events.jsonl").open("w", encoding="utf-8") as handle:
        for row in payload["evaluated"]:
            handle.write(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n")
    print(OUT_DIR / "noisy_graph_router.results.md")
    print(OUT_DIR / "camp_gate_graph_router_contract.metta")


def main() -> int:
    rows = core.load_jsonl(ROWS_PATH)
    evaluated: list[dict[str, Any]] = []
    for row in rows:
        packet, diagnostics = graph_router_packet(row["prompt"])
        evaluated.append(evaluate(row, "metta_graph_router_script", packet, diagnostics))
        evaluated.append(canonical_result(row))
    payload = {
        "generated_at_utc": utc_now(),
        "rows_path": str(ROWS_PATH.relative_to(ROOT)),
        "summary": summarize(evaluated),
        "evaluated": evaluated,
        "contract_path": str((OUT_DIR / "camp_gate_graph_router_contract.metta").relative_to(ROOT)),
    }
    write_outputs(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
