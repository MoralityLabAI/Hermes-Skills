"""Build noisy/paraphrased camp-gate extraction rows.

The rows reuse the leakage-safe micro-suite targets but replace the templated
constraint prompt with less regular natural-language statements. This probes
whether a small model can act as a constraint transcriber before MeTTa owns
schema repair and symbolic solving.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "research" / "studies" / "2026-04-29-logic-signature-camp-gate-leakage-safe"
BASE_ROWS = STUDY / "rows" / "logic_signature_camp_gate_rows.jsonl"
OUT_ROWS = STUDY / "rows" / "logic_signature_camp_gate_noisy_extract_rows.jsonl"
OUT_CONFIG = STUDY / "configs" / "logic_signature_noisy_extract_suite.json"

NUMBER_WORDS = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n")


def word(value: int) -> str:
    return NUMBER_WORDS.get(value, str(value))


def rc_text(tents: list[list[int]], style: int) -> str:
    if style == 0:
        return "; ".join(f"row {r}, column {c}" for r, c in tents)
    if style == 1:
        return ", ".join(f"r{r}c{c}" for r, c in tents)
    if style == 2:
        return " / ".join(f"({r} from top, {c} from left)" for r, c in tents)
    return ", ".join(f"R{r}-C{c}" for r, c in tents)


def rows_text(counts: list[int], style: int) -> str:
    if style == 0:
        return ", ".join(f"row {idx + 1} gets {word(value)}" for idx, value in enumerate(counts))
    if style == 1:
        return " / ".join(str(value) for value in counts) + " from top row to bottom row"
    if style == 2:
        return "; ".join(f"R{idx + 1}:{value}" for idx, value in enumerate(counts))
    return ", ".join(f"{word(value)} in lane {idx + 1}" for idx, value in enumerate(counts))


def cols_text(counts: list[int], style: int) -> str:
    if style == 0:
        return ", ".join(f"column {idx + 1} gets {word(value)}" for idx, value in enumerate(counts))
    if style == 1:
        return " / ".join(str(value) for value in counts) + " from left column to right column"
    if style == 2:
        return "; ".join(f"C{idx + 1}:{value}" for idx, value in enumerate(counts))
    return ", ".join(f"{word(value)} in file {idx + 1}" for idx, value in enumerate(counts))


def noisy_prompt(row: dict[str, Any], index: int) -> str:
    validator = row["validator"]
    height = int(validator["height"])
    width = int(validator["width"])
    tents = validator["fixed_tents"]
    row_counts = validator["row_c_counts"]
    col_counts = validator["col_c_counts"]
    style = index % 4

    common_rules = (
        "T marks a fixed anchor, C marks a camp, and X marks empty ground. "
        "Keep exactly the listed T anchors and add no other T cells. "
        "Each anchor must touch exactly one camp by an edge, and every camp must touch exactly one anchor by an edge. "
        "Camps may not touch any other camp, including diagonally. "
        "All cells that are not anchors or camps are X."
    )

    if style == 0:
        return (
            f"Survey note for a campsite board: it is {word(height)} rows tall and {word(width)} columns wide. "
            "Rows are numbered from the top, columns from the left. "
            f"The fixed anchors are at {rc_text(tents, style)}. "
            f"Camp totals by row are: {rows_text(row_counts, style)}. "
            f"Camp totals by column are: {cols_text(col_counts, style)}. "
            f"{common_rules} Extract the public constraints; do not solve the grid."
        )
    if style == 1:
        return (
            f"Campsite ledger: board size {height} by {width}, meaning {height} horizontal rows and {width} vertical columns. "
            f"Anchor coordinates, in row-column shorthand, are {rc_text(tents, style)}. "
            f"Row quotas for C are {rows_text(row_counts, style)}. "
            f"Column quotas for C are {cols_text(col_counts, style)}. "
            f"{common_rules} Return the constraints only."
        )
    if style == 2:
        return (
            f"The puzzle map has {height} north-south bands and {width} west-east files. "
            f"Pre-placed T anchors: {rc_text(tents, style)}. "
            f"Reading row requirements north to south gives {rows_text(row_counts, style)}. "
            f"Reading column requirements west to east gives {cols_text(col_counts, style)}. "
            f"{common_rules} I only need the machine-readable constraint packet."
        )
    return (
        f"Grid dimensions are not square by assumption: height {height}, width {width}. "
        f"The immovable tent anchors are {rc_text(tents, style)}. "
        f"For the rows, the required camp counts are {rows_text(row_counts, style)}. "
        f"For the columns, the required camp counts are {cols_text(col_counts, style)}. "
        f"{common_rules} Do not include a candidate grid."
    )


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, base in enumerate(load_jsonl(BASE_ROWS)):
        row = dict(base)
        row["row_id"] = f"{base['row_id']}_noisy"
        row["split"] = "noisy_paraphrase_extract"
        row["prompt"] = noisy_prompt(base, index)
        row["source_row_id"] = base["row_id"]
        row["noisy_extract_audit"] = {
            "target_grid_in_prompt": False,
            "reuses_target_solution": True,
            "paraphrase_style": index % 4,
            "constraint_surface": "natural_language_coordinates_and_count_vectors",
        }
        rows.append(row)
    return rows


def main() -> int:
    rows = build_rows()
    write_jsonl(OUT_ROWS, rows)
    config = {
        "generated_at_utc": utc_now(),
        "source_rows": str(BASE_ROWS.relative_to(ROOT)),
        "rows": str(OUT_ROWS.relative_to(ROOT)),
        "row_count": len(rows),
        "split": "noisy_paraphrase_extract",
        "claim_boundary": "Tests structured natural-language constraint extraction, not free-form puzzle parsing.",
    }
    OUT_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    OUT_CONFIG.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(OUT_ROWS)
    print(OUT_CONFIG)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
