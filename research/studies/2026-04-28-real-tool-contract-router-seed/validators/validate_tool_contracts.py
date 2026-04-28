from __future__ import annotations

import argparse
import html
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_json(text: str) -> tuple[Any | None, str | None]:
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, str(exc)


def check_type(value: Any, spec: str) -> bool:
    if spec == "str":
        return isinstance(value, str)
    if spec == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if spec == "bool":
        return isinstance(value, bool)
    if spec == "date":
        return isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is not None
    if spec == "time":
        return isinstance(value, str) and re.fullmatch(r"\d{2}:\d{2}", value) is not None
    if spec.startswith("enum:"):
        return isinstance(value, str) and value in spec.split(":", 1)[1].split("|")
    raise ValueError(f"unknown type spec: {spec}")


def validate(row: dict[str, Any], output: str) -> dict[str, Any]:
    validator = row["validator"]
    parsed, error = parse_json(output)
    details: dict[str, Any] = {"kind": validator["type"], "parse_error": error}
    contract_valid = False
    semantic_valid = False

    if isinstance(parsed, dict) and validator["type"] == "tool_call":
        allowed_keys = set(validator["top_level_keys"])
        top_level_ok = set(parsed) == allowed_keys
        tool = parsed.get("tool")
        args = parsed.get("args")
        safe_to_execute = parsed.get("safe_to_execute")
        allowed_tool = tool in validator["allowed_tools"]
        expected_tool_ok = tool == validator["expected_tool"]
        args_is_object = isinstance(args, dict)
        required_args = validator["required_args"]
        arg_keys_ok = args_is_object and set(args) == set(required_args)
        arg_types_ok = False
        if args_is_object:
            arg_types_ok = all(key in args and check_type(args[key], spec) for key, spec in required_args.items())
        expected_args_ok = args == validator["expected_args"]
        safety_type_ok = isinstance(safe_to_execute, bool)
        safety_value_ok = safe_to_execute == validator["safe_to_execute"]
        contract_valid = bool(
            top_level_ok
            and allowed_tool
            and args_is_object
            and arg_keys_ok
            and arg_types_ok
            and safety_type_ok
        )
        semantic_valid = bool(expected_tool_ok and expected_args_ok and safety_value_ok)
        details.update(
            {
                "top_level_ok": top_level_ok,
                "allowed_tool": allowed_tool,
                "expected_tool_ok": expected_tool_ok,
                "arg_keys_ok": arg_keys_ok,
                "arg_types_ok": arg_types_ok,
                "expected_args_ok": expected_args_ok,
                "safety_value_ok": safety_value_ok,
            }
        )

    return {
        "contract_valid": bool(contract_valid),
        "semantic_valid": bool(semantic_valid),
        "exact_success": bool(contract_valid and semantic_valid),
        "details": details,
    }


def summarize(evaluated: list[dict[str, Any]]) -> dict[str, Any]:
    by_arm: dict[str, dict[str, Any]] = {}
    by_family: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    arms = sorted({row["arm"] for row in evaluated})
    families = sorted({row["env_family"] for row in evaluated})
    for arm in arms:
        rows = [row for row in evaluated if row["arm"] == arm]
        by_arm[arm] = {
            "rows": len(rows),
            "contract_valid": sum(row["contract_valid"] for row in rows),
            "semantic_valid": sum(row["semantic_valid"] for row in rows),
            "exact_success": sum(row["exact_success"] for row in rows),
            "contract_rate": sum(row["contract_valid"] for row in rows) / max(1, len(rows)),
            "semantic_rate": sum(row["semantic_valid"] for row in rows) / max(1, len(rows)),
            "exact_rate": sum(row["exact_success"] for row in rows) / max(1, len(rows)),
        }
        for family in families:
            family_rows = [row for row in rows if row["env_family"] == family]
            if family_rows:
                by_family[arm][family] = {
                    "rows": len(family_rows),
                    "exact_success": sum(row["exact_success"] for row in family_rows),
                    "exact_rate": sum(row["exact_success"] for row in family_rows) / len(family_rows),
                }
    return {
        "evidence_class": "no_model_validator_smoke",
        "rows": len({row["row_id"] for row in evaluated}),
        "arms": by_arm,
        "by_family": by_family,
        "note": "Canonical tool-call validator smoke; this is not a model benchmark.",
    }


def render_md(summary: dict[str, Any], evaluated: list[dict[str, Any]]) -> str:
    lines = [
        "# Real Tool-Contract Router Validator Smoke",
        "",
        "Evidence class: `no_model_validator_smoke`",
        "",
        "| Arm | Rows | Contract valid | Semantic valid | Exact success | Exact rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for arm, metrics in summary["arms"].items():
        lines.append(
            f"| `{arm}` | {metrics['rows']} | {metrics['contract_valid']} | {metrics['semantic_valid']} | {metrics['exact_success']} | {metrics['exact_rate']:.4f} |"
        )
    lines.extend(["", "## Failure Rows", ""])
    failures = [row for row in evaluated if not row["exact_success"]]
    if not failures:
        lines.append("No failures.")
    else:
        lines.append("| Arm | Row | Family | Contract | Semantic | Output |")
        lines.append("| --- | --- | --- | ---: | ---: | --- |")
        for row in failures:
            output = html.escape(row["output"].replace("\n", "\\n")).replace("|", "\\|")
            lines.append(
                f"| `{row['arm']}` | `{row['row_id']}` | `{row['env_family']}` | {int(row['contract_valid'])} | {int(row['semantic_valid'])} | <code>{output}</code> |"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The validator separates valid JSON/schema/tool-call shape from exact tool, argument, and safety semantics.",
            "- This is a no-model canonical smoke. The next benchmark should compare baseline, pure TRM, MeTTa runtime, and repair arms on the same row IDs.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", required=True, type=Path)
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--out-json", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    args = parser.parse_args()

    rows_by_id = {row["row_id"]: row for row in load_jsonl(args.rows)}
    candidates = load_jsonl(args.candidates)
    evaluated = []
    for candidate in candidates:
        row = rows_by_id[candidate["row_id"]]
        verdict = validate(row, candidate["output"])
        evaluated.append({**candidate, "env_family": row["env_family"], **verdict})

    summary = summarize(evaluated)
    payload = {"summary": summary, "evaluated": evaluated}
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    args.out_md.write_text(render_md(summary, evaluated), encoding="utf-8")
    print(args.out_json)
    print(args.out_md)


if __name__ == "__main__":
    main()
