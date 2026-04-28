from __future__ import annotations

import argparse
import html
import json
import re
import string
from collections import defaultdict
from pathlib import Path
from typing import Any


PUNCTUATION = set(string.punctuation) - {"|", "-", "_"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text)


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
    if spec.startswith("enum:"):
        return isinstance(value, str) and value in spec.split(":", 1)[1].split("|")
    raise ValueError(f"unknown type spec: {spec}")


def validate(row: dict[str, Any], output: str) -> dict[str, Any]:
    validator = row["validator"]
    kind = validator["type"]
    details: dict[str, Any] = {"kind": kind}
    contract_valid = False
    semantic_valid = False

    if kind == "exact_word_count":
        token_count = len(words(output))
        suffix_ok = True
        if "require_suffix" in validator:
            suffix_ok = output.strip().endswith(str(validator["require_suffix"]))
        punctuation_ok = True
        if validator.get("forbid_punctuation"):
            punctuation_ok = not any(ch in PUNCTUATION for ch in output)
        contract_valid = (
            token_count == int(validator["word_count"]) and suffix_ok and punctuation_ok
        )
        semantic_valid = all(
            keyword.lower() in output.lower() for keyword in row.get("semantic_keywords", [])
        )
        details.update(
            {
                "word_count": token_count,
                "suffix_ok": suffix_ok,
                "punctuation_ok": punctuation_ok,
            }
        )

    elif kind == "json_object":
        parsed, error = parse_json(output)
        details["parse_error"] = error
        if isinstance(parsed, dict):
            required = validator["required"]
            type_ok = all(key in parsed and check_type(parsed[key], spec) for key, spec in required.items())
            expected_values = validator.get("expected_values", {})
            values_ok = all(parsed.get(key) == value for key, value in expected_values.items())
            no_extra = set(parsed).issubset(set(required))
            contract_valid = type_ok and no_extra
            semantic_valid = values_ok
            details.update(
                {
                    "type_ok": type_ok,
                    "values_ok": values_ok,
                    "no_extra": no_extra,
                    "keys": sorted(parsed),
                }
            )

    elif kind == "ascii_tree_exact":
        actual_lines = [line.rstrip() for line in output.strip().splitlines()]
        expected_lines = validator["required_lines"]
        contract_valid = actual_lines == expected_lines
        semantic_valid = all(node in output for node in validator.get("required_nodes", []))
        details.update({"actual_lines": actual_lines})

    elif kind == "bullet_list":
        lines = [line.rstrip() for line in output.strip().splitlines() if line.strip()]
        prefix = validator.get("prefix", "- ")
        contract_valid = len(lines) == int(validator["count"]) and all(
            line.startswith(prefix) for line in lines
        )
        joined = "\n".join(lines).lower()
        semantic_valid = all(keyword.lower() in joined for keyword in row.get("semantic_keywords", []))
        details.update({"line_count": len(lines), "lines": lines})

    elif kind == "json_array":
        parsed, error = parse_json(output)
        details["parse_error"] = error
        if isinstance(parsed, list):
            length_ok = len(parsed) == int(validator["length"])
            lowercase_ok = True
            if validator.get("lowercase_strings"):
                lowercase_ok = all(isinstance(item, str) and item == item.lower() for item in parsed)
            values_ok = parsed == validator.get("expected_values", parsed)
            contract_valid = length_ok and lowercase_ok
            semantic_valid = values_ok
            details.update({"length_ok": length_ok, "lowercase_ok": lowercase_ok, "values_ok": values_ok})

    elif kind == "exact_label":
        stripped = output.strip()
        allowed = validator["allowed"]
        contract_valid = stripped in allowed
        semantic_valid = stripped == validator["expected"]
        details.update({"stripped": stripped, "allowed": allowed})

    elif kind == "pipe_triplet":
        parts = output.strip().split("|")
        expected = validator["expected_values"]
        status_index = int(validator["status_index"])
        date_index = int(validator["date_index"])
        contract_valid = (
            len(parts) == 3
            and re.fullmatch(r"\d{4}-\d{2}-\d{2}", parts[date_index]) is not None
            and parts[status_index] in validator["allowed_status"]
        )
        semantic_valid = parts == expected
        details.update({"parts": parts})

    else:
        raise ValueError(f"unknown validator type: {kind}")

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
            "contract_rate": sum(row["contract_valid"] for row in rows) / len(rows),
            "semantic_rate": sum(row["semantic_valid"] for row in rows) / len(rows),
            "exact_rate": sum(row["exact_success"] for row in rows) / len(rows),
        }
        for family in families:
            family_rows = [row for row in rows if row["env_family"] == family]
            if not family_rows:
                continue
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
        "note": "This is a deterministic validator smoke, not a model benchmark.",
    }


def render_md(summary: dict[str, Any], evaluated: list[dict[str, Any]]) -> str:
    lines = [
        "# Mixed Contract Validator Smoke",
        "",
        "Evidence class: `no_model_validator_smoke`",
        "",
        "This run tests frozen rows and exact validators for the mixed-contract compactification study. It does not use model calls and should not be reported as benchmark lift.",
        "",
        "## Arm Summary",
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
            "- The validator surface catches format-only, schema-only, and semantic-label failures separately.",
            "- The `metta_runtime_repair` arm is canonical deterministic repair, not a learned or live model result.",
            "- The next valid benchmark step is to replace deterministic candidates with local 3B completions while preserving these row IDs and validators.",
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
