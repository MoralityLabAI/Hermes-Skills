"""Run local 3B as a constraint extractor for the camp-gate solver."""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import logic_signature_camp_gate_core as core  # noqa: E402
from run_logic_signature_camp_gate_local_3b import run_llama_completion  # noqa: E402


STUDY = ROOT / "research" / "studies" / "2026-04-29-logic-signature-camp-gate-leakage-safe"
ROWS_PATH = STUDY / "rows" / "logic_signature_camp_gate_rows.jsonl"
DEFAULT_OUT = STUDY / "results" / "local_qwen25_3b_constraint_extract"

DEFAULT_MODEL = Path(r"D:\research_engine\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf")
DEFAULT_LLAMA_COMPLETION = Path(r"D:\research_engine\tools\llama.cpp-b8922-cuda12.4\llama-completion.exe")
EXTRACT_ARMS = ("baseline_extract", "metta_schema_extract", "metta_graph_extract")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local 3B camp-gate constraint extraction run.")
    parser.add_argument("--rows", default=str(ROWS_PATH))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--model-path", default=str(DEFAULT_MODEL))
    parser.add_argument("--llama-completion-path", default=str(DEFAULT_LLAMA_COMPLETION))
    parser.add_argument("--max-cases", type=int, default=0, help="0 means all rows.")
    parser.add_argument("--ctx", type=int, default=1536)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--ubatch-size", type=int, default=32)
    parser.add_argument("--max-tokens", type=int, default=160)
    parser.add_argument("--timeout-sec", type=int, default=120)
    parser.add_argument("--gpu-layers", default="all")
    parser.add_argument("--max-prompt-chars", type=int, default=6000)
    parser.add_argument("--max-child-rss-mb", type=float, default=2600.0)
    parser.add_argument("--cooldown-sec", type=float, default=0.5)
    return parser.parse_args()


def select_rows(rows: list[dict[str, Any]], max_cases: int) -> list[dict[str, Any]]:
    return rows if max_cases <= 0 else rows[:max_cases]


def render_messages(system: str, user: str) -> list[dict[str, str]]:
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def schema_text() -> str:
    return json.dumps(
        {
            "height": "integer",
            "width": "integer",
            "fixed_tents": [["row_integer_1_indexed", "col_integer_1_indexed"]],
            "row_c_counts": ["integer per row"],
            "col_c_counts": ["integer per column"],
        },
        ensure_ascii=True,
        sort_keys=True,
    )


def arm_prompt(row: dict[str, Any], arm: str) -> list[dict[str, str]]:
    final_contract = (
        "Return JSON only. No markdown fence, no explanation. Use keys exactly: "
        "height, width, fixed_tents, row_c_counts, col_c_counts."
    )
    if arm == "baseline_extract":
        return render_messages(
            final_contract,
            f"Extract the campsite grid constraints from this prompt:\n\n{row['prompt']}",
        )
    if arm == "metta_schema_extract":
        return render_messages(
            (
                "You are a MeTTa/TRM constraint extraction gate. Gate sequence: "
                "TRM_PARSE_TEXT -> METTA_FIELD_SCHEMA -> TRM_CANONICALIZE_NUMBERS -> "
                "METTA_JSON_COMMIT. " + final_contract
            ),
            (
                f"Prompt:\n{row['prompt']}\n\n"
                f"Output schema:\n{schema_text()}\n\n"
                "Extract only the public constraints. Do not solve the grid."
            ),
        )
    if arm == "metta_graph_extract":
        return render_messages(
            (
                "You are a MeTTa/TRM graph router for public constraint extraction. "
                "Run independent gates before the final commit: "
                "DIMENSION_GATE extracts height and width; "
                "ANCHOR_GATE extracts fixed T anchor coordinates; "
                "ROW_QUOTA_GATE extracts row C counts from top row to bottom row; "
                "COLUMN_QUOTA_GATE extracts column C counts from left column to right column; "
                "COMMIT_GATE emits one JSON object. "
                "Coordinates are 1-indexed: r2c3 means [2,3], and '(1 from top, 4 from left)' means [1,4]. "
                "Never subtract 1 from coordinates. Never copy column counts into row counts. "
                "The row_c_counts length must equal height; col_c_counts length must equal width. "
                "The sums of row_c_counts and col_c_counts must equal the number of fixed_tents. "
                + final_contract
            ),
            (
                f"Prompt:\n{row['prompt']}\n\n"
                f"Output schema:\n{schema_text()}\n\n"
                "Extract only public constraints. Do not solve the grid. "
                "Return exactly one JSON object."
            ),
        )
    raise ValueError(f"unknown arm: {arm}")


def evaluate_extraction(row: dict[str, Any], arm: str, output: str, diagnostics: dict[str, Any]) -> dict[str, Any]:
    raw_packet = core.extract_json_object(output)
    packet = core.normalize_constraint_packet(raw_packet)
    repaired_packet, repair_diagnostics = core.repair_constraint_packet(row, raw_packet)
    solved_output, solver = core.solve_from_constraint_packet(row, packet)
    solve_verdict = core.validate_output(row, solved_output or "")
    repaired_solved_output, repaired_solver = core.solve_from_constraint_packet(row, repaired_packet)
    repaired_solve_verdict = core.validate_output(row, repaired_solved_output or "")
    return {
        "ts": utc_now(),
        "row_id": row["row_id"],
        "env_family": row["env_family"],
        "arm": arm,
        "output": output,
        "evidence_class": "live_model_local_3b_constraint_extract",
        "json_parse": raw_packet is not None,
        "packet_valid": packet is not None,
        "packet_exact": core.constraint_packet_exact(row, packet),
        "solver_unique": bool(solver.get("solved")),
        "solve_exact": bool(solve_verdict["exact_success"]),
        "solve_cell_accuracy": solve_verdict["cell_accuracy"],
        "repair_packet_valid": repaired_packet is not None,
        "repair_packet_exact": core.constraint_packet_exact(row, repaired_packet),
        "repair_solver_unique": bool(repaired_solver.get("solved")),
        "repair_solve_exact": bool(repaired_solve_verdict["exact_success"]),
        "repair_solve_cell_accuracy": repaired_solve_verdict["cell_accuracy"],
        "normalized_packet": packet,
        "repaired_packet": repaired_packet,
        "canonical_packet": core.canonical_constraint_packet(row),
        "solver": solver,
        "repair_solver": repaired_solver,
        "repair_diagnostics": repair_diagnostics,
        "solved_output": solved_output or "",
        "repair_solved_output": repaired_solved_output or "",
        "diagnostics": diagnostics,
    }


def error_extraction(row: dict[str, Any], arm: str, error: str) -> dict[str, Any]:
    return {
        "ts": utc_now(),
        "row_id": row["row_id"],
        "env_family": row["env_family"],
        "arm": arm,
        "output": "",
        "evidence_class": "live_model_local_3b_constraint_extract_error",
        "json_parse": False,
        "packet_valid": False,
        "packet_exact": False,
        "solver_unique": False,
        "solve_exact": False,
        "solve_cell_accuracy": 0.0,
        "repair_packet_valid": False,
        "repair_packet_exact": False,
        "repair_solver_unique": False,
        "repair_solve_exact": False,
        "repair_solve_cell_accuracy": 0.0,
        "normalized_packet": None,
        "repaired_packet": None,
        "canonical_packet": core.canonical_constraint_packet(row),
        "solver": {"solved": False, "reason": "runner_error"},
        "repair_solver": {"solved": False, "reason": "runner_error"},
        "solved_output": "",
        "repair_solved_output": "",
        "diagnostics": {"error": error},
    }


def canonical_packet_result(row: dict[str, Any]) -> dict[str, Any]:
    packet = core.canonical_constraint_packet(row)
    solved_output, solver = core.solve_from_constraint_packet(row, packet)
    solve_verdict = core.validate_output(row, solved_output or "")
    return {
        "ts": utc_now(),
        "row_id": row["row_id"],
        "env_family": row["env_family"],
        "arm": "canonical_packet_solver",
        "output": json.dumps(packet, ensure_ascii=True, separators=(",", ":")),
        "evidence_class": "no_model_canonical_constraint_solver",
        "json_parse": True,
        "packet_valid": True,
        "packet_exact": True,
        "solver_unique": bool(solver.get("solved")),
        "solve_exact": bool(solve_verdict["exact_success"]),
        "solve_cell_accuracy": solve_verdict["cell_accuracy"],
        "repair_packet_valid": True,
        "repair_packet_exact": True,
        "repair_solver_unique": bool(solver.get("solved")),
        "repair_solve_exact": bool(solve_verdict["exact_success"]),
        "repair_solve_cell_accuracy": solve_verdict["cell_accuracy"],
        "normalized_packet": packet,
        "repaired_packet": packet,
        "canonical_packet": packet,
        "solver": solver,
        "repair_solver": solver,
        "solved_output": solved_output or "",
        "repair_solved_output": solved_output or "",
        "diagnostics": {"model_calls": 0},
    }


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n")


def summarize(evaluated: list[dict[str, Any]]) -> dict[str, Any]:
    by_arm: dict[str, dict[str, Any]] = {}
    for arm in sorted({row["arm"] for row in evaluated}):
        rows = [row for row in evaluated if row["arm"] == arm]
        by_arm[arm] = {
            "rows": len(rows),
            "json_parse": sum(1 for row in rows if row["json_parse"]),
            "packet_valid": sum(1 for row in rows if row["packet_valid"]),
            "packet_exact": sum(1 for row in rows if row["packet_exact"]),
            "solver_unique": sum(1 for row in rows if row["solver_unique"]),
            "solve_exact": sum(1 for row in rows if row["solve_exact"]),
            "solve_exact_rate": sum(1 for row in rows if row["solve_exact"]) / max(1, len(rows)),
            "packet_exact_rate": sum(1 for row in rows if row["packet_exact"]) / max(1, len(rows)),
            "avg_solve_cell_accuracy": sum(float(row["solve_cell_accuracy"]) for row in rows) / max(1, len(rows)),
            "repair_packet_exact": sum(1 for row in rows if row.get("repair_packet_exact")),
            "repair_solve_exact": sum(1 for row in rows if row.get("repair_solve_exact")),
            "repair_solve_exact_rate": sum(1 for row in rows if row.get("repair_solve_exact")) / max(1, len(rows)),
        }
    family_failures: dict[str, int] = defaultdict(int)
    for row in evaluated:
        if row["arm"] != "canonical_packet_solver" and not row["solve_exact"]:
            family_failures[row["env_family"]] += 1
    return {
        "evidence_class": "live_model_local_3b_constraint_extract",
        "rows": len({row["row_id"] for row in evaluated}),
        "arms": by_arm,
        "failure_counts_by_family": dict(family_failures),
        "peak_child_ram_mb": max(
            (float(row.get("diagnostics", {}).get("peak_child_ram_mb", 0.0)) for row in evaluated),
            default=0.0,
        ),
    }


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Local Qwen2.5-3B Constraint Extraction Camp-Gate Run",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "Evidence class: `live_model_local_3b_constraint_extract`",
        "",
        f"Model: `{payload['model_path']}`",
        f"Peak child RSS: `{payload['summary']['peak_child_ram_mb']:.2f} MB`",
        "",
        "## Arm Summary",
        "",
        "| Arm | Rows | JSON Parse | Strict Packet Exact | Strict Solve Exact | Repair Packet Exact | Repair Solve Exact | Repair Solve Rate | Avg Strict Cell Acc |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for arm, metrics in payload["summary"]["arms"].items():
        lines.append(
            f"| `{arm}` | {metrics['rows']} | {metrics['json_parse']} | {metrics['packet_exact']} | "
            f"{metrics['solve_exact']} | {metrics['repair_packet_exact']} | {metrics['repair_solve_exact']} | "
            f"{metrics['repair_solve_exact_rate']:.4f} | {metrics['avg_solve_cell_accuracy']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Repair-Failed Extractions",
            "",
            "| Row | Arm | JSON | Strict Packet Exact | Repair Packet Exact | Repair Solve Exact | Output |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    failures = [
        row
        for row in payload["evaluated"]
        if row["arm"] != "canonical_packet_solver" and not row.get("repair_solve_exact", row["solve_exact"])
    ]
    if not failures:
        lines.append("| - | - | - | - | - | - | No failed model extractions after schema repair |")
    for row in failures[:80]:
        output = html.escape(str(row.get("output", "")).replace("\n", "\\n")).replace("|", "\\|")
        lines.append(
            f"| `{row['row_id']}` | `{row['arm']}` | {int(row['json_parse'])} | {int(row['packet_exact'])} | "
            f"{int(row.get('repair_packet_exact', False))} | {int(row.get('repair_solve_exact', False))} | "
            f"<code>{output[:240]}</code> |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is the extraction-side follow-up to the public-constraint solver ablation.",
            "- If extraction succeeds, the skill can shift the LLM from solver to constraint transcriber.",
            "- If extraction fails on less-structured prompts, the next TRM target is constraint extraction rather than grid execution.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(out_dir: Path, payload: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    results_json = out_dir / "local_qwen25_3b_constraint_extract.results.json"
    results_md = out_dir / "local_qwen25_3b_constraint_extract.results.md"
    results_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    results_md.write_text(render_md(payload), encoding="utf-8")
    print(results_md)
    print(results_json)


def main() -> int:
    args = parse_args()
    rows = select_rows(core.load_jsonl(Path(args.rows).resolve()), args.max_cases)
    out_dir = Path(args.out_dir).resolve()
    model_path = Path(args.model_path).resolve()
    llama_completion = Path(args.llama_completion_path).resolve()
    if not model_path.exists():
        raise SystemExit(f"model not found: {model_path}")
    if not llama_completion.exists():
        raise SystemExit(f"llama-completion not found: {llama_completion}")

    events_path = out_dir / "local_qwen25_3b_constraint_extract.events.jsonl"
    if events_path.exists():
        events_path.unlink()
    evaluated: list[dict[str, Any]] = []
    for row in rows:
        canonical = canonical_packet_result(row)
        evaluated.append(canonical)
        append_jsonl(events_path, canonical)
        for arm in EXTRACT_ARMS:
            try:
                output, diagnostics = run_llama_completion(
                    llama_completion=llama_completion,
                    model_path=model_path,
                    messages=arm_prompt(row, arm),
                    ctx=args.ctx,
                    threads=args.threads,
                    batch_size=args.batch_size,
                    ubatch_size=args.ubatch_size,
                    gpu_layers=args.gpu_layers,
                    max_tokens=args.max_tokens,
                    timeout_sec=args.timeout_sec,
                    max_prompt_chars=args.max_prompt_chars,
                    max_child_rss_mb=args.max_child_rss_mb,
                )
                result = evaluate_extraction(row, arm, output, diagnostics)
            except RuntimeError as exc:
                result = error_extraction(row, arm, str(exc))
            evaluated.append(result)
            append_jsonl(events_path, result)
            time.sleep(args.cooldown_sec)
            if "child_rss_cap_exceeded" in str(result.get("diagnostics", {}).get("error", "")):
                break

    payload = {
        "generated_at_utc": utc_now(),
        "model_path": str(model_path),
        "llama_completion_path": str(llama_completion),
        "rows_path": str(Path(args.rows).resolve()),
        "config": {
            "ctx": args.ctx,
            "threads": args.threads,
            "batch_size": args.batch_size,
            "ubatch_size": args.ubatch_size,
            "max_tokens": args.max_tokens,
            "timeout_sec": args.timeout_sec,
            "gpu_layers": args.gpu_layers,
            "max_child_rss_mb": args.max_child_rss_mb,
        },
        "summary": summarize(evaluated),
        "evaluated": evaluated,
    }
    write_outputs(out_dir, payload)
    print(events_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
