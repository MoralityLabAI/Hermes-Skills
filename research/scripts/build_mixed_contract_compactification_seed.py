"""Seed and validate the mixed-contract compactification study.

This is the first dry run of the MeTTa agent navigation guide. It creates a
small no-model study for the `paper_main_claim_extension` route:

- frozen mixed-contract rows
- deterministic candidate outputs for four arms
- an exact validator script
- a result table and claim audit

The result is not a model benchmark. It is a validator and artifact-contract
smoke test that prepares the study for later local 3B, 9B, and 27B runs.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "research" / "studies" / "2026-04-28-mixed-contract-compactification-seed"
ROWS_DIR = STUDY / "rows"
VALIDATORS_DIR = STUDY / "validators"
CONFIGS_DIR = STUDY / "configs"
RESULTS_DIR = STUDY / "results"

ROWS_PATH = ROWS_DIR / "mixed_contract_seed_rows.jsonl"
CANDIDATES_PATH = RESULTS_DIR / "seed_candidates.jsonl"
VALIDATOR_PATH = VALIDATORS_DIR / "validate_mixed_contracts.py"
RESULTS_JSON = RESULTS_DIR / "validator_smoke.results.json"
RESULTS_MD = RESULTS_DIR / "validator_smoke.results.md"
CONFIG_PATH = CONFIGS_DIR / "seed_arms.json"


ROWS: list[dict[str, Any]] = [
    {
        "row_id": "ifsum_lakebed_001",
        "env_family": "if_summarize_judge",
        "split": "seed_holdout",
        "prompt": "Summarize: Mars rover samples show evidence of an ancient lakebed. Return exactly 6 words and no punctuation.",
        "canonical_output": "Mars rover samples reveal ancient lakebed",
        "semantic_keywords": ["mars", "samples", "lakebed"],
        "validator": {"type": "exact_word_count", "word_count": 6, "forbid_punctuation": True},
        "failure_labels": ["word_count", "punctuation"],
    },
    {
        "row_id": "ifsum_gate_question_002",
        "env_family": "if_summarize_judge",
        "split": "seed_holdout",
        "prompt": "Summarize the claim as a question with exactly 8 words: symbolic gates reduce invalid contract commits.",
        "canonical_output": "Could symbolic gates prevent invalid contract commits today?",
        "semantic_keywords": ["symbolic", "gates", "contract", "commits"],
        "validator": {"type": "exact_word_count", "word_count": 8, "require_suffix": "?"},
        "failure_labels": ["word_count", "question_form"],
    },
    {
        "row_id": "pyd_task_003",
        "env_family": "pydantic_adherence",
        "split": "seed_holdout",
        "prompt": "Return JSON with task, priority, due_date, and blocked for the row collection task.",
        "canonical_output": '{"task":"collect rows","priority":"high","due_date":"2026-05-02","blocked":false}',
        "validator": {
            "type": "json_object",
            "required": {
                "task": "str",
                "priority": "enum:low|medium|high",
                "due_date": "date",
                "blocked": "bool",
            },
            "expected_values": {
                "task": "collect rows",
                "priority": "high",
                "due_date": "2026-05-02",
                "blocked": False,
            },
        },
        "failure_labels": ["json_parse", "missing_field", "enum", "date"],
    },
    {
        "row_id": "pyd_verifier_004",
        "env_family": "pydantic_adherence",
        "split": "seed_holdout",
        "prompt": "Return JSON for a verifier component with name, retries, and safe fields.",
        "canonical_output": '{"name":"verifier","retries":2,"safe":true}',
        "validator": {
            "type": "json_object",
            "required": {"name": "str", "retries": "int", "safe": "bool"},
            "expected_values": {"name": "verifier", "retries": 2, "safe": True},
        },
        "failure_labels": ["json_parse", "type_error"],
    },
    {
        "row_id": "ascii_flat_005",
        "env_family": "ascii_tree",
        "split": "seed_holdout",
        "prompt": "Return an ASCII tree with root, rows, validators, and results.",
        "canonical_output": "root\n|-- rows\n|-- validators\n`-- results",
        "validator": {
            "type": "ascii_tree_exact",
            "required_lines": ["root", "|-- rows", "|-- validators", "`-- results"],
            "required_nodes": ["root", "rows", "validators", "results"],
        },
        "failure_labels": ["tree_shape", "missing_node"],
    },
    {
        "row_id": "ascii_nested_006",
        "env_family": "ascii_tree",
        "split": "seed_holdout",
        "prompt": "Return an ASCII tree for pipeline with parse/classify nested and commit as final sibling.",
        "canonical_output": "pipeline\n|-- parse\n|   `-- classify\n`-- commit",
        "validator": {
            "type": "ascii_tree_exact",
            "required_lines": ["pipeline", "|-- parse", "|   `-- classify", "`-- commit"],
            "required_nodes": ["pipeline", "parse", "classify", "commit"],
        },
        "failure_labels": ["tree_shape", "indent"],
    },
    {
        "row_id": "ifeval_bullets_007",
        "env_family": "ifeval_contract_family",
        "split": "seed_holdout",
        "prompt": "Return exactly three bullet lines for the control loop: parse, validate, commit. No intro.",
        "canonical_output": "- parse\n- validate\n- commit",
        "semantic_keywords": ["parse", "validate", "commit"],
        "validator": {"type": "bullet_list", "count": 3, "prefix": "- "},
        "failure_labels": ["line_count", "extra_text"],
    },
    {
        "row_id": "ifeval_json_array_008",
        "env_family": "ifeval_contract_family",
        "split": "seed_holdout",
        "prompt": "Return a JSON array of exactly three lowercase stages: route, repair, commit.",
        "canonical_output": '["route","repair","commit"]',
        "validator": {
            "type": "json_array",
            "length": 3,
            "lowercase_strings": True,
            "expected_values": ["route", "repair", "commit"],
        },
        "failure_labels": ["json_parse", "array_length", "case"],
    },
    {
        "row_id": "boolq_nile_009",
        "env_family": "boolq_choice_contract",
        "split": "seed_holdout",
        "prompt": "Context: The Nile is in Africa. Question: Is the Nile in Africa? Answer exactly true or false.",
        "canonical_output": "true",
        "validator": {"type": "exact_label", "allowed": ["true", "false"], "expected": "true"},
        "failure_labels": ["choice_contract", "semantic_label"],
    },
    {
        "row_id": "boolq_sky_010",
        "env_family": "boolq_choice_contract",
        "split": "seed_holdout",
        "prompt": "Context: A clear daytime sky is usually blue, not green. Question: Is a clear daytime sky usually green? Answer exactly true or false.",
        "canonical_output": "false",
        "validator": {"type": "exact_label", "allowed": ["true", "false"], "expected": "false"},
        "failure_labels": ["choice_contract", "semantic_label"],
    },
    {
        "row_id": "choice_letter_011",
        "env_family": "choice_contract",
        "split": "seed_holdout",
        "prompt": "Choose the only valid commit action: A reject, B commit, C defer. Return only A, B, or C.",
        "canonical_output": "B",
        "validator": {"type": "exact_label", "allowed": ["A", "B", "C"], "expected": "B"},
        "failure_labels": ["choice_contract", "extra_text"],
    },
    {
        "row_id": "pipe_triplet_012",
        "env_family": "structured_contract",
        "split": "seed_holdout",
        "prompt": "Return exactly date|owner|status for today's seed artifact. Status must be ready.",
        "canonical_output": "2026-04-28|trm|ready",
        "validator": {
            "type": "pipe_triplet",
            "date_index": 0,
            "owner_index": 1,
            "status_index": 2,
            "allowed_status": ["ready", "blocked"],
            "expected_values": ["2026-04-28", "trm", "ready"],
        },
        "failure_labels": ["delimiter", "date", "status"],
    },
]


BASELINE_OUTPUTS = {
    "ifsum_lakebed_001": "Mars rover samples show ancient lakebed.",
    "ifsum_gate_question_002": "Symbolic gates reduce invalid contract commits.",
    "pyd_task_003": "{task: collect rows, priority: urgent, due_date: May 2, blocked: no}",
    "pyd_verifier_004": '{"name":"verifier","retries":"two","safe":"yes"}',
    "ascii_flat_005": "root: rows, validators, results",
    "ascii_nested_006": "pipeline\n- parse\n- classify\n- commit",
    "ifeval_bullets_007": "The steps are parse, validate, and commit.",
    "ifeval_json_array_008": "Route, Repair, Commit",
    "boolq_nile_009": "Yes, true.",
    "boolq_sky_010": "false",
    "choice_letter_011": "B",
    "pipe_triplet_012": "2026/04/28 | trm | ready",
}

PURE_TRM_OUTPUTS = {
    "ifsum_lakebed_001": "Mars rover samples reveal ancient lakebed",
    "ifsum_gate_question_002": "Can symbolic gates reduce invalid contract commits?",
    "pyd_task_003": '{"task":"collect rows","priority":"high","due_date":"2026-05-02"}',
    "pyd_verifier_004": '{"name":"verifier","retries":2,"safe":true}',
    "ascii_flat_005": "root\n|-- rows\n|-- validators\n`-- results",
    "ascii_nested_006": "pipeline\n|-- parse\n|-- classify\n`-- commit",
    "ifeval_bullets_007": "- parse\n- validate\n- commit",
    "ifeval_json_array_008": '["route","repair","commit"]',
    "boolq_nile_009": "true",
    "boolq_sky_010": "false",
    "choice_letter_011": "Commit: B",
    "pipe_triplet_012": "2026-04-28|trm|ready",
}

METTA_RUNTIME_OUTPUTS = {
    "ifsum_lakebed_001": "Mars rover samples reveal ancient lakebed",
    "ifsum_gate_question_002": "Could symbolic gates reduce invalid commits today?",
    "pyd_task_003": '{"task":"collect rows","priority":"high","due_date":"2026-05-02","blocked":false}',
    "pyd_verifier_004": '{"name":"verifier","retries":2,"safe":true}',
    "ascii_flat_005": "root\n|-- rows\n|-- validators\n`-- results",
    "ascii_nested_006": "pipeline\n|-- parse\n|   `-- classify\n`-- commit",
    "ifeval_bullets_007": "- parse\n- validate\n- commit",
    "ifeval_json_array_008": '["route","repair","commit"]',
    "boolq_nile_009": "true",
    "boolq_sky_010": "false",
    "choice_letter_011": "B",
    "pipe_triplet_012": "2026-04-28|trm|ready",
}


VALIDATOR_SCRIPT = r'''
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
'''.lstrip()


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")


def candidates_for_rows() -> list[dict[str, Any]]:
    generated_at = datetime.now(timezone.utc).isoformat()
    candidates: list[dict[str, Any]] = []
    for row in ROWS:
        row_id = row["row_id"]
        outputs_by_arm = {
            "baseline": BASELINE_OUTPUTS[row_id],
            "pure_trm": PURE_TRM_OUTPUTS[row_id],
            "metta_runtime": METTA_RUNTIME_OUTPUTS[row_id],
            "metta_runtime_repair": row["canonical_output"],
        }
        for arm, output in outputs_by_arm.items():
            candidates.append(
                {
                    "row_id": row_id,
                    "arm": arm,
                    "output": output,
                    "evidence_class": "no_model_validator_smoke",
                    "generated_at_utc": generated_at,
                }
            )
    return candidates


def write_docs() -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    readme = f"""# Mixed Contract Compactification Seed

Generated: `{generated_at}`

This study is the first dry run of the MeTTa agent navigation guide.

- Route: `paper_main_claim_extension`
- Project: `mixed_contract_compactification`
- Evidence class: `no_model_validator_smoke`
- Source guide: `research/generated/metta_agent_navigation.md`
- Source menu: `research/generated/metta_project_menu.md`

## Purpose

Create the first artifact required by the agent guide: frozen rows, exact validators, configs, result files, and a claim audit. This is deliberately no-model so future model runs can reuse the same row IDs and validators.

## Artifacts

- Rows: `rows/mixed_contract_seed_rows.jsonl`
- Arms config: `configs/seed_arms.json`
- Validator: `validators/validate_mixed_contracts.py`
- Candidate outputs: `results/seed_candidates.jsonl`
- Smoke results: `results/validator_smoke.results.json`
- Smoke summary: `results/validator_smoke.results.md`
- Claim audit: `claim_audit.md`

## Next Step

Replace deterministic candidate outputs with local 3B completions for the same row IDs and score with the same validator script. Do not change the validator between model arms.
"""
    plan = """# Mixed Contract Compactification Study Plan

## Hypothesis

Small LLMs can act as proposal engines when explicit MeTTa/TRM gates own observable output contracts such as word count, JSON schema, ASCII tree shape, choice labels, and delimiter formats.

## Arms

- `baseline`: intentionally loose plain-output candidate.
- `pure_trm`: typed but not fully repair-gated candidate.
- `metta_runtime`: gate-aware candidate without final canonical repair in every case.
- `metta_runtime_repair`: canonical deterministic repair target for validator smoke only.

## Metrics

- `contract_valid`: output satisfies the observable contract.
- `semantic_valid`: output preserves the row's minimal semantic target.
- `exact_success`: both contract and semantic checks pass.

## Promotion Rule

Promote to local 3B benchmarking only if the no-model validator catches the intended failures across all included env families and the row schema is stable.

## Stop Rule

If a positive result can be produced only by canonical postprocessing, report it as verifier-owned repair and do not call it trained TRM lift.
"""
    audit = """# Claim Audit

## Evidence Class

`no_model_validator_smoke`

This study does not contain live model calls. It is an artifact-contract test for rows, validators, configs, and result schema.

## Allowed Claim

The generated rows and validators can separate contract validity from semantic validity across mixed contract families.

## Disallowed Claims

- Do not claim benchmark improvement.
- Do not claim TRM training lift.
- Do not claim small-model reasoning improvement.
- Do not mix this deterministic repair smoke with live model columns.

## Next Evidence Upgrade

The next run should be a local 3B `live_model` or `replay_from_live_log` result over the same row IDs, with the same validator script and arm names.
"""
    config = {
        "generated_at_utc": generated_at,
        "route_id": "paper_main_claim_extension",
        "project_id": "mixed_contract_compactification",
        "evidence_class": "no_model_validator_smoke",
        "arms": [
            "baseline",
            "pure_trm",
            "metta_runtime",
            "metta_runtime_repair",
        ],
        "row_count": len(ROWS),
        "model_calls": 0,
        "next_live_model_requirement": "Preserve row_id, prompt, validator, and arm schema for local 3B/9B/27B comparison.",
    }
    STUDY.mkdir(parents=True, exist_ok=True)
    (STUDY / "README.md").write_text(readme, encoding="utf-8")
    (STUDY / "study_plan.md").write_text(plan, encoding="utf-8")
    (STUDY / "claim_audit.md").write_text(audit, encoding="utf-8")
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for directory in (ROWS_DIR, VALIDATORS_DIR, CONFIGS_DIR, RESULTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    write_jsonl(ROWS_PATH, ROWS)
    write_jsonl(CANDIDATES_PATH, candidates_for_rows())
    VALIDATOR_PATH.write_text(VALIDATOR_SCRIPT, encoding="utf-8")
    write_docs()
    subprocess.run(
        [
            sys.executable,
            str(VALIDATOR_PATH),
            "--rows",
            str(ROWS_PATH),
            "--candidates",
            str(CANDIDATES_PATH),
            "--out-json",
            str(RESULTS_JSON),
            "--out-md",
            str(RESULTS_MD),
        ],
        check=True,
    )
    print(STUDY)


if __name__ == "__main__":
    main()
