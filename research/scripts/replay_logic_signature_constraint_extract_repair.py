"""Replay camp-gate constraint extraction with deterministic schema repair."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import logic_signature_camp_gate_core as core  # noqa: E402
from run_logic_signature_constraint_extract_local_3b import (  # noqa: E402
    canonical_packet_result,
    evaluate_extraction,
    render_md,
    summarize,
)


STUDY = ROOT / "research" / "studies" / "2026-04-29-logic-signature-camp-gate-leakage-safe"
ROWS_PATH = STUDY / "rows" / "logic_signature_camp_gate_rows.jsonl"
SOURCE_RESULTS = (
    STUDY
    / "results"
    / "local_qwen25_3b_constraint_extract"
    / "local_qwen25_3b_constraint_extract.results.json"
)
OUT_DIR = STUDY / "results" / "constraint_extract_schema_repair"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay constraint extraction with schema repair.")
    parser.add_argument("--rows", default=str(ROWS_PATH), type=Path)
    parser.add_argument("--source-results", default=str(SOURCE_RESULTS), type=Path)
    parser.add_argument("--out-dir", default=str(OUT_DIR), type=Path)
    args = parser.parse_args()

    rows = core.load_jsonl(args.rows)
    rows_by_id = {row["row_id"]: row for row in rows}
    source = json.loads(args.source_results.read_text(encoding="utf-8-sig"))
    evaluated: list[dict[str, Any]] = []

    for row in rows:
        evaluated.append(canonical_packet_result(row))

    for item in source["evaluated"]:
        if item["arm"] not in {"baseline_extract", "metta_schema_extract"}:
            continue
        row = rows_by_id[item["row_id"]]
        replayed = evaluate_extraction(
            row,
            item["arm"],
            str(item.get("output", "")),
            {
                "replay_source": str(args.source_results),
                "original_diagnostics": item.get("diagnostics", {}),
            },
        )
        replayed["evidence_class"] = "live_log_replay_constraint_extract_schema_repair"
        evaluated.append(replayed)

    payload = {
        "generated_at_utc": utc_now(),
        "model_path": source.get("model_path", ""),
        "llama_completion_path": source.get("llama_completion_path", ""),
        "rows_path": str(args.rows),
        "source_results": str(args.source_results),
        "summary": summarize(evaluated),
        "evaluated": evaluated,
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_json = args.out_dir / "constraint_extract_schema_repair.results.json"
    out_md = args.out_dir / "constraint_extract_schema_repair.results.md"
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(render_md(payload), encoding="utf-8")
    print(out_md)
    print(out_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
