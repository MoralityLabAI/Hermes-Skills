"""Build a harder 30-row mixed-contract suite for repair ablations."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE_STUDY = ROOT / "research" / "studies" / "2026-04-28-mixed-contract-compactification-heldout50"
STUDY = ROOT / "research" / "studies" / "2026-04-28-mixed-contract-hard-ablation30"

ROWS_DIR = STUDY / "rows"
VALIDATORS_DIR = STUDY / "validators"
CONFIGS_DIR = STUDY / "configs"
RESULTS_DIR = STUDY / "results" / "canonical_validator_smoke"
LOCAL_RESULTS_DIR = STUDY / "results" / "local_qwen25_3b_mixed_contract_hard_ablation30"

ROWS_PATH = ROWS_DIR / "mixed_contract_hard_ablation30_rows.jsonl"
CANDIDATES_PATH = RESULTS_DIR / "canonical_candidates.jsonl"
VALIDATOR_PATH = VALIDATORS_DIR / "validate_mixed_contracts.py"
RESULTS_JSON = RESULTS_DIR / "canonical_validator_smoke.results.json"
RESULTS_MD = RESULTS_DIR / "canonical_validator_smoke.results.md"
CONFIG_PATH = CONFIGS_DIR / "hard_ablation30_suite.json"
LOCAL_RESULTS_JSON = LOCAL_RESULTS_DIR / "local_qwen25_3b_mixed_contract.results.json"
LOCAL_JOBCAP_SUMMARY = LOCAL_RESULTS_DIR / "jobcap.summary.json"


def row(
    row_id: str,
    env_family: str,
    prompt: str,
    canonical_output: str,
    validator: dict[str, Any],
    failure_labels: list[str],
    semantic_keywords: list[str] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "row_id": row_id,
        "env_family": env_family,
        "split": "hard_ablation30",
        "prompt": prompt,
        "canonical_output": canonical_output,
        "validator": validator,
        "failure_labels": failure_labels,
    }
    if semantic_keywords:
        payload["semantic_keywords"] = semantic_keywords
    return payload


def numeric_row(row_id: str, prompt: str, expected: int) -> dict[str, Any]:
    return row(
        row_id,
        "math_numeric_contract",
        prompt + " Return only the integer.",
        str(expected),
        {"type": "numeric_answer", "format": "integer", "expected": str(expected)},
        ["numeric_parse", "arithmetic", "extra_text"],
    )


def label_row(row_id: str, prompt: str, allowed: list[str], expected: str) -> dict[str, Any]:
    return row(
        row_id,
        "logic_label_contract",
        prompt + " Return only one allowed label.",
        expected,
        {"type": "exact_label", "allowed": allowed, "expected": expected},
        ["choice_contract", "logic_label", "extra_text"],
    )


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    rows.extend(
        [
            numeric_row("hard_math_001_mod", "Compute ((17 * 19) + 23) modulo 11.", 5),
            numeric_row("hard_math_002_polynomial", "If x=4 and y=7, compute 3*x*x - 2*y + 5.", 39),
            numeric_row(
                "hard_math_003_filter",
                "A verifier starts with 11 schema rows, rejects 3 contract rows, then rejects 2 semantic rows from the remainder. How many exact successes remain?",
                6,
            ),
            numeric_row(
                "hard_math_004_boolean_sum",
                "Truth values a=true, b=false, c=true, d=true are encoded as 1/0. Compute (a AND NOT b) + (c XOR d) + (a AND c).",
                2,
            ),
            numeric_row("hard_math_005_day", "Start at 2026-05-04 and add 9 days. Return the day-of-month number.", 13),
            numeric_row("hard_math_006_grid", "A 4 by 5 grid loses cells (1,2), (2,2), and (4,5). How many cells remain?", 17),
            numeric_row("hard_math_007_majority", "Five judges vote pass, fail, pass, pass, fail. How many more pass votes than fail votes?", 1),
            numeric_row("hard_math_008_prime_count", "How many primes are in this list: 21, 22, 23, 24, 29, 30, 31?", 3),
        ]
    )

    rows.extend(
        [
            label_row(
                "hard_logic_001_router_schema",
                "Every router is a tool. No tool may bypass schema. Can a router bypass schema? Allowed labels: A=yes, B=no, C=unknown.",
                ["A", "B", "C"],
                "B",
            ),
            label_row(
                "hard_logic_002_commit_gate",
                "A commit gate commits iff contract_valid and semantic_valid are both true. Here contract_valid=true and semantic_valid=false. Allowed labels: A=commit, B=repair, C=skip, D=search.",
                ["A", "B", "C", "D"],
                "B",
            ),
            label_row(
                "hard_logic_003_xor",
                "Gate fires iff exactly one signal is true. Signals parse=true and validate=true. Allowed labels: A=fire, B=hold.",
                ["A", "B"],
                "B",
            ),
            label_row(
                "hard_logic_004_failed_parse",
                "A tool route has retrieval_ok=true, parse_ok=false, validator_known=true. Choose the next gate: A=draft, B=parse_repair, C=commit, D=cite.",
                ["A", "B", "C", "D"],
                "B",
            ),
            label_row(
                "hard_logic_005_transitive",
                "If p implies q, q implies r, and p is true, is r true? Allowed labels: true,false.",
                ["true", "false"],
                "true",
            ),
            label_row(
                "hard_logic_006_pass2",
                "Exactly two checks must pass for label PASS2. parse=pass, validate=fail, semantic=pass. Allowed labels: PASS2, OTHER.",
                ["PASS2", "OTHER"],
                "PASS2",
            ),
            label_row(
                "hard_logic_007_cycle",
                "A graph has directed edges A->B, B->C, and C->A. Is the graph acyclic? Allowed labels: true,false.",
                ["true", "false"],
                "false",
            ),
        ]
    )

    json_cases = [
        (
            "hard_schema_001_repair_route",
            "contract_valid=false, semantic_valid=true, previous_attempts=1. Return JSON with route repair, priority high, retry_count previous_attempts+1, safe true.",
            {"route": "repair", "priority": "high", "retry_count": 2, "safe": True},
            {"route": "enum:commit|repair|reject", "priority": "enum:low|medium|high", "retry_count": "int", "safe": "bool"},
        ),
        (
            "hard_schema_002_commit_route",
            "contract_valid=true, semantic_valid=true, previous_attempts=0. Return JSON with route commit, priority low, retry_count 0, safe true.",
            {"route": "commit", "priority": "low", "retry_count": 0, "safe": True},
            {"route": "enum:commit|repair|reject", "priority": "enum:low|medium|high", "retry_count": "int", "safe": "bool"},
        ),
        (
            "hard_schema_003_reject_route",
            "contract_valid=false, semantic_valid=false, unsafe=true. Return JSON with route reject, priority high, retry_count 0, safe false.",
            {"route": "reject", "priority": "high", "retry_count": 0, "safe": False},
            {"route": "enum:commit|repair|reject", "priority": "enum:low|medium|high", "retry_count": "int", "safe": "bool"},
        ),
        (
            "hard_schema_004_window",
            "Batch id seven has 12 rows, 5 failures, and starts on 2026-05-11. Return JSON with batch_id batch-7, passed 7, failed 5, start_date 2026-05-11.",
            {"batch_id": "batch-7", "passed": 7, "failed": 5, "start_date": "2026-05-11"},
            {"batch_id": "str", "passed": "int", "failed": "int", "start_date": "date"},
        ),
        (
            "hard_schema_005_skill",
            "A skill named metta_router has version 3 and active true. Return JSON with name metta_router, version 3, active true.",
            {"name": "metta_router", "version": 3, "active": True},
            {"name": "str", "version": "int", "active": "bool"},
        ),
        (
            "hard_schema_006_score",
            "A row has contract score 2, semantic score 3, and exact true. Return JSON with contract 2, semantic 3, total 5, exact true.",
            {"contract": 2, "semantic": 3, "total": 5, "exact": True},
            {"contract": "int", "semantic": "int", "total": "int", "exact": "bool"},
        ),
    ]
    for row_id, prompt, expected, required in json_cases:
        rows.append(
            row(
                row_id,
                "computed_json_schema",
                prompt + " No markdown fence.",
                json.dumps(expected, separators=(",", ":")),
                {"type": "json_object", "required": required, "expected_values": expected},
                ["json_parse", "type_error", "computed_value"],
            )
        )

    array_cases = [
        ("hard_state_001_repair", ["draft", "parsed", "repair", "commit"]),
        ("hard_state_002_reject", ["draft", "parsed", "reject"]),
        ("hard_state_003_retry", ["collect", "score", "retry", "score", "commit"]),
        ("hard_state_004_branch", ["parse", "route", "tool", "validate", "commit"]),
        ("hard_state_005_abort", ["load", "check", "abort"]),
    ]
    array_prompts = {
        "hard_state_001_repair": "Start draft. parse succeeds, validation fails once, repair succeeds, then commit. Return the visited state labels as a JSON array.",
        "hard_state_002_reject": "Start draft. parse succeeds, both contract and semantic checks fail, then reject. Return the visited state labels as a JSON array.",
        "hard_state_003_retry": "Start collect. score fails once, retry, score succeeds, commit. Return the visited state labels as a JSON array.",
        "hard_state_004_branch": "Start parse. route selects tool, tool returns, validation passes, commit. Return the visited state labels as a JSON array.",
        "hard_state_005_abort": "Start load. check detects unsafe memory pressure, abort. Return the visited state labels as a JSON array.",
    }
    for row_id, expected in array_cases:
        rows.append(
            row(
                row_id,
                "state_sequence_array",
                array_prompts[row_id],
                json.dumps(expected, separators=(",", ":")),
                {"type": "json_array", "length": len(expected), "lowercase_strings": True, "expected_values": expected},
                ["json_parse", "array_length", "state_order"],
            )
        )

    tree_cases = [
        ("hard_tree_001_skill", "skill\n|-- parse\n|   |-- schema\n|   `-- prompt\n`-- commit", ["skill", "|-- parse", "|   |-- schema", "|   `-- prompt", "`-- commit"], ["skill", "parse", "schema", "prompt", "commit"]),
        ("hard_tree_002_eval", "eval\n|-- rows\n|   |-- hard\n|   `-- holdout\n`-- claims", ["eval", "|-- rows", "|   |-- hard", "|   `-- holdout", "`-- claims"], ["eval", "rows", "hard", "holdout", "claims"]),
        ("hard_tree_003_gate", "gate\n|-- metta\n|   `-- select\n|-- trm\n`-- repair", ["gate", "|-- metta", "|   `-- select", "|-- trm", "`-- repair"], ["gate", "metta", "select", "trm", "repair"]),
        ("hard_tree_004_data", "data\n|-- raw\n|-- labels\n|   `-- failures\n`-- audit", ["data", "|-- raw", "|-- labels", "|   `-- failures", "`-- audit"], ["data", "raw", "labels", "failures", "audit"]),
    ]
    for row_id, output, required_lines, nodes in tree_cases:
        rows.append(
            row(
                row_id,
                "deep_ascii_tree",
                f"Return an ASCII tree exactly matching root {nodes[0]} with visible nodes {', '.join(nodes[1:])}. No code fence.",
                output,
                {"type": "ascii_tree_exact", "required_lines": required_lines, "required_nodes": nodes},
                ["tree_shape", "missing_node", "indent"],
            )
        )

    assert len(rows) == 30, len(rows)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in rows:
            handle.write(json.dumps(item, ensure_ascii=True, separators=(",", ":")) + "\n")


def write_validator() -> None:
    source = (SOURCE_STUDY / "validators" / "validate_mixed_contracts.py").read_text(encoding="utf-8")
    numeric_block = '''    elif kind == "numeric_answer":
        stripped = output.strip()
        expected = str(validator["expected"])
        integer_ok = True
        if validator.get("format") == "integer":
            integer_ok = re.fullmatch(r"-?\\d+", stripped) is not None
        contract_valid = bool(integer_ok)
        semantic_valid = stripped == expected
        details.update({"stripped": stripped, "integer_ok": integer_ok})

'''
    marker = '    elif kind == "exact_label":\n'
    if numeric_block not in source:
        source = source.replace(marker, numeric_block + marker)
    VALIDATOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    VALIDATOR_PATH.write_text(source, encoding="utf-8")


def local_result_context() -> dict[str, Any] | None:
    if not LOCAL_RESULTS_JSON.exists() or not LOCAL_JOBCAP_SUMMARY.exists():
        return None
    local_result = json.loads(LOCAL_RESULTS_JSON.read_text(encoding="utf-8-sig"))
    jobcap = json.loads(LOCAL_JOBCAP_SUMMARY.read_text(encoding="utf-8-sig"))
    return {"local_result": local_result, "jobcap": jobcap}


def write_docs(rows: list[dict[str, Any]]) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    counts: dict[str, int] = {}
    for item in rows:
        counts[item["env_family"]] = counts.get(item["env_family"], 0) + 1
    counts_table = "\n".join(f"| `{family}` | {count} |" for family, count in sorted(counts.items()))
    context = local_result_context()

    if context:
        local_result = context["local_result"]
        jobcap = context["jobcap"]
        arms = local_result["summary"]["arms"]
        arm_order = [
            "baseline",
            "pure_trm",
            "metta_runtime",
            "metta_runtime_blind_repair",
            "metta_runtime_repair",
        ]
        arm_table = "\n".join(
            "| `{}` | {}/{} | {:.4f} | {}/{} | {}/{} |".format(
                arm,
                arms[arm]["exact_success"],
                arms[arm]["rows"],
                arms[arm]["exact_rate"],
                arms[arm]["contract_valid"],
                arms[arm]["rows"],
                arms[arm]["semantic_valid"],
                arms[arm]["rows"],
            )
            for arm in arm_order
            if arm in arms
        )
        repair = local_result["summary"].get("repair_opportunities", {})
        repair_rows = repair.get("metta_runtime_failed_rows", 0)
        repair_table = "\n".join(
            "| `{}` | {} | {} | {:.4f} |".format(
                arm,
                metrics["rows"],
                metrics["exact_success"],
                metrics["exact_rate"],
            )
            for arm, metrics in repair.get("arms", {}).items()
        )
        families = sorted(local_result["summary"].get("by_family", {}).get("baseline", {}))
        family_table = "\n".join(
            "| `{}` | {} | {} | {} | {} | {} |".format(
                family,
                "{}/{}".format(
                    local_result["summary"]["by_family"]["baseline"][family]["exact_success"],
                    local_result["summary"]["by_family"]["baseline"][family]["rows"],
                ),
                "{}/{}".format(
                    local_result["summary"]["by_family"]["pure_trm"][family]["exact_success"],
                    local_result["summary"]["by_family"]["pure_trm"][family]["rows"],
                ),
                "{}/{}".format(
                    local_result["summary"]["by_family"]["metta_runtime"][family]["exact_success"],
                    local_result["summary"]["by_family"]["metta_runtime"][family]["rows"],
                ),
                "{}/{}".format(
                    local_result["summary"]["by_family"]["metta_runtime_blind_repair"][family]["exact_success"],
                    local_result["summary"]["by_family"]["metta_runtime_blind_repair"][family]["rows"],
                ),
                "{}/{}".format(
                    local_result["summary"]["by_family"]["metta_runtime_repair"][family]["exact_success"],
                    local_result["summary"]["by_family"]["metta_runtime_repair"][family]["rows"],
                ),
            )
            for family in families
        )
        caps = jobcap["caps"]
        local_section = f"""## Local 3B Result

The full hard-ablation run completed under the Windows job-cap wrapper with a {caps["ram_mb"]:,} MB RAM cap, {caps["cpu_pct"]}% CPU cap, {caps["io_mb_s"]} MB/s IO cap, and {caps["timeout_sec"]:,} second timeout. Runner-level child RSS peaked at `{local_result["summary"]["peak_child_ram_mb"]:.2f} MB`; the job-cap wrapper reported `{jobcap["status"]}`.

| Arm | Exact | Exact Rate | Contract Valid | Semantic Valid |
| --- | ---: | ---: | ---: | ---: |
{arm_table}

## Repair Opportunity Result

Rows where `metta_runtime` failed exactly: `{repair_rows}`.

| Repair arm | Opportunity Rows | Exact Repairs | Exact Rate |
| --- | ---: | ---: | ---: |
{repair_table}

## Family Breakdown

| Family | Baseline | Pure TRM | MeTTa Runtime | Blind Repair | Feedback Repair |
| --- | ---: | ---: | ---: | ---: | ---: |
{family_table}
"""
        evidence_classes = "`no_model_validator_smoke`, `live_model_local_3b`"
        baseline_exact = arms["baseline"]["exact_success"]
        metta_exact = arms["metta_runtime"]["exact_success"]
        blind_exact = arms["metta_runtime_blind_repair"]["exact_success"]
        feedback_exact = arms["metta_runtime_repair"]["exact_success"]
        blind_opp = repair.get("arms", {}).get("metta_runtime_blind_repair", {}).get("exact_success", 0)
        feedback_opp = repair.get("arms", {}).get("metta_runtime_repair", {}).get("exact_success", 0)
        allowed_live = (
            f"- On this local 3B run, feedback repair scored {feedback_exact}/30 exact versus "
            f"baseline {baseline_exact}/30, blind repair {blind_exact}/30, and MeTTa runtime {metta_exact}/30."
        )
        repair_live = (
            f"- On the {repair_rows} failed MeTTa-runtime opportunities, feedback repair fixed {feedback_opp} rows "
            f"versus {blind_opp} rows for blind repair."
        )
        disallowed_live = (
            "- Do not present this as strong hard-suite lift; the feedback repair advantage is small and "
            "must be reported separately from the easier heldout50 result."
        )
    else:
        local_section = """## Next Step

Run local 3B with `research/scripts/run_mixed_contract_local_3b.py --include-blind-repair` under the Windows job-cap wrapper.
"""
        evidence_classes = "`no_model_validator_smoke`, pending `live_model_local_3b`"
        allowed_live = "- Live local model claims require job-cap receipts and result JSON."
        repair_live = "- The blind repair arm will separate generic second-pass benefit from public-validator feedback benefit after live evaluation."
        disallowed_live = "- Do not infer the blind-vs-feedback repair split before running the live model ablation."

    readme = f"""# Mixed Contract Hard Ablation30

Generated: `{generated_at}`

- Route: `paper_main_claim_extension`
- Project: `mixed_contract_hard_ablation`
- Evidence classes: {evidence_classes}
- Source heldout study: `research/studies/2026-04-28-mixed-contract-compactification-heldout50`

## Purpose

This suite probes whether the heldout50 lift survives on harder rows and whether public-validator feedback adds value beyond a blind second repair pass.

## Family Counts

| Family | Rows |
| --- | ---: |
{counts_table}

## Artifacts

- Rows: `rows/mixed_contract_hard_ablation30_rows.jsonl`
- Validator: `validators/validate_mixed_contracts.py`
- Suite config: `configs/hard_ablation30_suite.json`
- Canonical smoke: `results/canonical_validator_smoke/canonical_validator_smoke.results.md`
- Local 3B run: `results/local_qwen25_3b_mixed_contract_hard_ablation30/local_qwen25_3b_mixed_contract.results.md`
- Job-cap receipt: `results/local_qwen25_3b_mixed_contract_hard_ablation30/jobcap.summary.json`

{local_section}
"""
    plan = f"""# Hard Ablation30 Study Plan

## Hypothesis

If MeTTa/TRM scaffolding is doing more than output-format nudging, it should retain lift on numeric, logic, computed-schema, state-sequence, and deep-tree contracts. Public validator feedback should outperform blind repair on the subset where `metta_runtime` initially fails.

## Arms

- `baseline`: direct final answer prompt.
- `pure_trm`: TRM contract prompt.
- `metta_runtime`: MeTTa/TRM gate prompt.
- `metta_runtime_blind_repair`: second pass without validator feedback.
- `metta_runtime_repair`: second pass with public validator feedback.

## Metrics

- `exact_success`
- `contract_valid`
- `semantic_valid`
- per-family exact rate
- repair opportunity exact rate on rows where `metta_runtime` failed
- child RSS and job-cap outcome

## Claim Rule

Report this as a hard-suite ablation, not as trained TRM lift. The main comparison is `metta_runtime_blind_repair` versus `metta_runtime_repair` on failed MeTTa runtime rows.

## Current Status

{allowed_live}
{repair_live}
"""
    audit = f"""# Claim Audit

## Evidence Class

- `no_model_validator_smoke` for canonical validator validation.
- `live_model_local_3b` only after local result JSON and job-cap summary exist.

## Allowed Claims

- The row suite is harder than heldout50 by family mix: numeric micro-math, logic labels, computed JSON, state sequences, and deeper trees.
- The canonical validator smoke validates the answer keys and exact validators before model calls.
{allowed_live}
{repair_live}

## Disallowed Claims

- Do not call repair-prompt gains trained TRM lift.
- Do not claim broad math or logic reasoning gain from this suite alone.
- Do not compare to 9B/27B unless row IDs and validators are identical.
{disallowed_live}
"""
    config = {
        "generated_at_utc": generated_at,
        "route_id": "paper_main_claim_extension",
        "project_id": "mixed_contract_hard_ablation",
        "row_count": len(rows),
        "family_counts": counts,
        "validator": str(VALIDATOR_PATH.relative_to(ROOT)),
        "recommended_caps": {
            "job_memory_limit_mb": 3000,
            "cpu_rate_percent": 50,
            "io_cap_mb_s": 50,
            "runner_child_rss_mb": 2600,
            "timeout_sec": 7200,
        },
        "required_runner_flag": "--include-blind-repair",
    }

    STUDY.mkdir(parents=True, exist_ok=True)
    (STUDY / "README.md").write_text(readme.rstrip() + "\n", encoding="utf-8")
    (STUDY / "study_plan.md").write_text(plan.rstrip() + "\n", encoding="utf-8")
    (STUDY / "claim_audit.md").write_text(audit.rstrip() + "\n", encoding="utf-8")
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    for directory in (ROWS_DIR, VALIDATORS_DIR, CONFIGS_DIR, RESULTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    write_validator()
    write_jsonl(ROWS_PATH, rows)
    canonical_candidates = [
        {
            "row_id": item["row_id"],
            "arm": "canonical_target",
            "output": item["canonical_output"],
            "evidence_class": "no_model_validator_smoke",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        for item in rows
    ]
    write_jsonl(CANDIDATES_PATH, canonical_candidates)
    write_docs(rows)
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
