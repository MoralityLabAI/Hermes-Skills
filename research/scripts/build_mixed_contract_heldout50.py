"""Build a 50-row held-out suite for mixed-contract compactification."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / "research" / "studies" / "2026-04-28-mixed-contract-compactification-seed"
STUDY = ROOT / "research" / "studies" / "2026-04-28-mixed-contract-compactification-heldout50"

ROWS_DIR = STUDY / "rows"
VALIDATORS_DIR = STUDY / "validators"
CONFIGS_DIR = STUDY / "configs"
RESULTS_DIR = STUDY / "results" / "canonical_validator_smoke"

ROWS_PATH = ROWS_DIR / "mixed_contract_heldout50_rows.jsonl"
CANDIDATES_PATH = RESULTS_DIR / "canonical_candidates.jsonl"
VALIDATOR_PATH = VALIDATORS_DIR / "validate_mixed_contracts.py"
RESULTS_JSON = RESULTS_DIR / "canonical_validator_smoke.results.json"
RESULTS_MD = RESULTS_DIR / "canonical_validator_smoke.results.md"
CONFIG_PATH = CONFIGS_DIR / "heldout50_suite.json"
LOCAL_RESULTS_DIR = STUDY / "results" / "local_qwen25_3b_mixed_contract_heldout50"
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
        "split": "heldout50",
        "prompt": prompt,
        "canonical_output": canonical_output,
        "validator": validator,
        "failure_labels": failure_labels,
    }
    if semantic_keywords:
        payload["semantic_keywords"] = semantic_keywords
    return payload


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    summary_cases = [
        ("climate", "Climate sensors detected steady coastal warming", 6, True, ["climate", "sensor", "warming"]),
        ("robotics", "Warehouse robots delayed because charging docks failed", 7, True, ["robots", "charging", "failed"]),
        ("security", "Encrypted backups prevented data loss after outage", 7, True, ["backups", "data", "outage"]),
        ("biology", "Protein assay confirmed improved enzyme stability", 6, True, ["protein", "enzyme", "stability"]),
        ("energy", "Solar microgrid restored power before sunrise", 6, True, ["solar", "power", "sunrise"]),
        ("archive", "Archive index exposed missing migration receipts", 6, True, ["archive", "index", "receipts"]),
        ("question_logic", "Could verifier gates reduce invalid commits tomorrow?", 7, False, ["verifier", "gates", "commits"]),
        ("question_data", "Can typed rows reveal brittle validators?", 6, False, ["typed", "rows", "validators"]),
        ("question_tools", "Will schema memory improve tool routing?", 6, False, ["schema", "memory", "routing"]),
        ("question_repair", "Should repair gates reject unsafe outputs?", 6, False, ["repair", "gates", "outputs"]),
    ]
    for idx, (name, output, word_count, no_punct, keywords) in enumerate(summary_cases, start=1):
        validator: dict[str, Any] = {"type": "exact_word_count", "word_count": word_count}
        prompt_suffix = f"Return exactly {word_count} words"
        labels = ["word_count"]
        if no_punct:
            validator["forbid_punctuation"] = True
            prompt_suffix += " and no punctuation"
            labels.append("punctuation")
        else:
            validator["require_suffix"] = "?"
            prompt_suffix += " as a question"
            labels.append("question_form")
        rows.append(
            row(
                f"heldout_ifsum_{idx:03d}_{name}",
                "if_summarize_judge",
                f"Summarize this claim: {output}. {prompt_suffix}.",
                output + ("?" if not no_punct and not output.endswith("?") else ""),
                validator,
                labels,
                keywords,
            )
        )

    json_cases = [
        ("collect invoices", "high", "2026-05-03", False),
        ("audit validators", "medium", "2026-05-04", False),
        ("freeze prompts", "high", "2026-05-05", True),
        ("label failures", "medium", "2026-05-06", False),
        ("ship receipts", "low", "2026-05-07", False),
    ]
    for idx, (task, priority, due_date, blocked) in enumerate(json_cases, start=1):
        expected = {"task": task, "priority": priority, "due_date": due_date, "blocked": blocked}
        rows.append(
            row(
                f"heldout_pyd_task_{idx:03d}",
                "pydantic_adherence",
                f"Return JSON for task {task} with priority {priority}, due_date {due_date}, and blocked {str(blocked).lower()}.",
                json.dumps(expected, separators=(",", ":")),
                {
                    "type": "json_object",
                    "required": {
                        "task": "str",
                        "priority": "enum:low|medium|high",
                        "due_date": "date",
                        "blocked": "bool",
                    },
                    "expected_values": expected,
                },
                ["json_parse", "missing_field", "enum", "date"],
            )
        )

    component_cases = [
        ("router", 1, True),
        ("retriever", 2, True),
        ("auditor", 3, False),
        ("repairer", 2, True),
        ("committer", 1, False),
    ]
    for idx, (name, retries, safe) in enumerate(component_cases, start=1):
        expected = {"name": name, "retries": retries, "safe": safe}
        rows.append(
            row(
                f"heldout_pyd_component_{idx:03d}",
                "pydantic_adherence",
                f"Return JSON for component name {name}, retries {retries}, and safe {str(safe).lower()}.",
                json.dumps(expected, separators=(",", ":")),
                {
                    "type": "json_object",
                    "required": {"name": "str", "retries": "int", "safe": "bool"},
                    "expected_values": expected,
                },
                ["json_parse", "type_error"],
            )
        )

    tree_cases = [
        ("heldout_ascii_001_docs", "docs\n|-- drafts\n|-- figures\n`-- refs", ["docs", "|-- drafts", "|-- figures", "`-- refs"], ["docs", "drafts", "figures", "refs"]),
        ("heldout_ascii_002_eval", "eval\n|-- rows\n|   `-- heldout\n`-- results", ["eval", "|-- rows", "|   `-- heldout", "`-- results"], ["eval", "rows", "heldout", "results"]),
        ("heldout_ascii_003_tools", "tools\n|-- search\n|-- weather\n`-- calendar", ["tools", "|-- search", "|-- weather", "`-- calendar"], ["tools", "search", "weather", "calendar"]),
        ("heldout_ascii_004_gate", "gate\n|-- parse\n|-- validate\n`-- commit", ["gate", "|-- parse", "|-- validate", "`-- commit"], ["gate", "parse", "validate", "commit"]),
        ("heldout_ascii_005_pipe", "pipeline\n|-- collect\n|   `-- score\n`-- audit", ["pipeline", "|-- collect", "|   `-- score", "`-- audit"], ["pipeline", "collect", "score", "audit"]),
        ("heldout_ascii_006_repo", "repo\n|-- skills\n|-- studies\n`-- scripts", ["repo", "|-- skills", "|-- studies", "`-- scripts"], ["repo", "skills", "studies", "scripts"]),
        ("heldout_ascii_007_agent", "agent\n|-- route\n|   `-- project\n`-- report", ["agent", "|-- route", "|   `-- project", "`-- report"], ["agent", "route", "project", "report"]),
        ("heldout_ascii_008_model", "model\n|-- prompt\n|-- output\n`-- verdict", ["model", "|-- prompt", "|-- output", "`-- verdict"], ["model", "prompt", "output", "verdict"]),
    ]
    for row_id, output, required_lines, nodes in tree_cases:
        rows.append(
            row(
                row_id,
                "ascii_tree",
                f"Return an ASCII tree exactly matching root {nodes[0]} with visible nodes {', '.join(nodes[1:])}. No code fence.",
                output,
                {"type": "ascii_tree_exact", "required_lines": required_lines, "required_nodes": nodes},
                ["tree_shape", "missing_node", "indent"],
            )
        )

    bullet_cases = [
        ("heldout_bullets_001", ["parse", "validate", "commit"], ["parse", "validate", "commit"]),
        ("heldout_bullets_002", ["collect rows", "score rows", "audit claims"], ["collect", "score", "audit"]),
        ("heldout_bullets_003", ["freeze prompts", "run models", "compare arms"], ["freeze", "run", "compare"]),
        ("heldout_bullets_004", ["label failures", "repair outputs", "log receipts"], ["label", "repair", "log"]),
        ("heldout_bullets_005", ["route tools", "fill args", "check schema"], ["route", "args", "schema"]),
        ("heldout_bullets_006", ["draft table", "render figure", "write claim"], ["table", "figure", "claim"]),
        ("heldout_bullets_007", ["load rows", "call model", "store verdicts"], ["load", "model", "verdicts"]),
        ("heldout_bullets_008", ["reject leak", "guard split", "publish audit"], ["reject", "guard", "audit"]),
    ]
    for row_id, items, keywords in bullet_cases:
        output = "\n".join(f"- {item}" for item in items)
        rows.append(
            row(
                row_id,
                "ifeval_contract_family",
                f"Return exactly {len(items)} bullet lines for: {', '.join(items)}. No intro.",
                output,
                {"type": "bullet_list", "count": len(items), "prefix": "- "},
                ["line_count", "extra_text"],
                keywords,
            )
        )

    array_cases = [
        ("heldout_array_001", ["route", "repair", "commit"]),
        ("heldout_array_002", ["train", "validate", "holdout"]),
        ("heldout_array_003", ["search", "read", "answer"]),
        ("heldout_array_004", ["schema", "args", "call"]),
        ("heldout_array_005", ["draft", "score", "audit"]),
        ("heldout_array_006", ["rows", "metrics", "claims"]),
    ]
    for row_id, values in array_cases:
        rows.append(
            row(
                row_id,
                "ifeval_contract_family",
                f"Return a JSON array of exactly {len(values)} lowercase strings: {', '.join(values)}.",
                json.dumps(values, separators=(",", ":")),
                {"type": "json_array", "length": len(values), "lowercase_strings": True, "expected_values": values},
                ["json_parse", "array_length", "case"],
            )
        )

    label_cases = [
        ("heldout_bool_001", "Context: Granite is a rock. Question: Is granite a rock?", ["true", "false"], "true"),
        ("heldout_bool_002", "Context: Penguins are birds, not mammals. Question: Are penguins mammals?", ["true", "false"], "false"),
        ("heldout_bool_003", "Context: The Pacific is an ocean. Question: Is the Pacific an ocean?", ["true", "false"], "true"),
        ("heldout_choice_004", "Choose the valid route: A search, B weather, C calendar. The user asks for tomorrow's rain forecast.", ["A", "B", "C"], "B"),
        ("heldout_choice_005", "Choose the valid route: A reject, B commit, C retry. The output passed every validator.", ["A", "B", "C"], "B"),
    ]
    for row_id, prompt, allowed, expected in label_cases:
        rows.append(
            row(
                row_id,
                "choice_contract" if row_id.startswith("heldout_choice") else "boolq_choice_contract",
                prompt + " Return only one allowed label.",
                expected,
                {"type": "exact_label", "allowed": allowed, "expected": expected},
                ["choice_contract", "semantic_label", "extra_text"],
            )
        )

    pipe_cases = [
        ("heldout_pipe_001", ["2026-05-08", "eval", "ready"]),
        ("heldout_pipe_002", ["2026-05-09", "audit", "blocked"]),
        ("heldout_pipe_003", ["2026-05-10", "paper", "ready"]),
    ]
    for row_id, expected in pipe_cases:
        rows.append(
            row(
                row_id,
                "structured_contract",
                f"Return exactly date|owner|status using date {expected[0]}, owner {expected[1]}, and status {expected[2]}.",
                "|".join(expected),
                {
                    "type": "pipe_triplet",
                    "date_index": 0,
                    "owner_index": 1,
                    "status_index": 2,
                    "allowed_status": ["ready", "blocked"],
                    "expected_values": expected,
                },
                ["delimiter", "date", "status"],
            )
        )

    assert len(rows) == 50, len(rows)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in rows:
            handle.write(json.dumps(item, ensure_ascii=True, separators=(",", ":")) + "\n")


def write_docs(rows: list[dict[str, Any]]) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    counts: dict[str, int] = {}
    for item in rows:
        counts[item["env_family"]] = counts.get(item["env_family"], 0) + 1
    counts_table = "\n".join(f"| `{family}` | {count} |" for family, count in sorted(counts.items()))

    local_result: dict[str, Any] | None = None
    jobcap: dict[str, Any] | None = None
    if LOCAL_RESULTS_JSON.exists() and LOCAL_JOBCAP_SUMMARY.exists():
        local_result = json.loads(LOCAL_RESULTS_JSON.read_text(encoding="utf-8-sig"))
        jobcap = json.loads(LOCAL_JOBCAP_SUMMARY.read_text(encoding="utf-8-sig"))

    if local_result and jobcap:
        evidence_classes = "`no_model_validator_smoke`, `live_model_local_3b`"
        local_artifacts = """- Local 3B run: `results/local_qwen25_3b_mixed_contract_heldout50/local_qwen25_3b_mixed_contract.results.md`
- Job-cap receipt: `results/local_qwen25_3b_mixed_contract_heldout50/jobcap.summary.json`"""
        arms = local_result["summary"]["arms"]
        arm_order = ["baseline", "pure_trm", "metta_runtime", "metta_runtime_repair"]
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
        )
        caps = jobcap["caps"]
        local_section = f"""## Local 3B Result

The full 50-row held-out run completed under the Windows job-cap wrapper with a {caps["ram_mb"]:,} MB RAM cap, {caps["cpu_pct"]}% CPU cap, {caps["io_mb_s"]} MB/s IO cap, and {caps["timeout_sec"]:,} second timeout. Runner-level child RSS peaked at `{local_result["summary"]["peak_child_ram_mb"]:.2f} MB`; the job-cap wrapper reported `{jobcap["status"]}`.

| Arm | Exact | Exact Rate | Contract Valid | Semantic Valid |
| --- | ---: | ---: | ---: | ---: |
{arm_table}

This supports a held-out prompt/repair-gate methodology claim: MeTTa-scaffolded runtime framing plus public-validator repair improves local 3B exact mixed-contract success on this suite. It does not establish learned TRM lift.
"""
        audit_evidence = """- `no_model_validator_smoke` for canonical validator validation.
- `live_model_local_3b` for local Qwen2.5-3B Q4 model completions under the Windows job-cap wrapper."""
        live_allowed = "- Live local model results can be used as a held-out 50-row prompt/repair-gate benchmark because job-cap receipts and result JSON are present."
        result_claim = "- On this suite, `metta_runtime_repair` improves exact success from 23/50 baseline to 37/50, with `metta_runtime` at 32/50 and `pure_trm` at 27/50."
        promotion_rule = "Promote this to paper material as held-out local 3B evidence because `metta_runtime_repair` remains positive and the result table explicitly separates prompt-only, repair-prompt, and no-model evidence."
        result_snapshot = "## Result Snapshot\n\nThe full local Qwen2.5-3B Q4 run scored `baseline` 23/50 exact, `pure_trm` 27/50, `metta_runtime` 32/50, and `metta_runtime_repair` 37/50. The paper-safe claim is methodology lift from structured MeTTa/TRM framing and public-validator repair, not trained TRM capability.\n"
        extra_disallowed = "- Do not treat easy delimiter, choice, or label rows as sufficient evidence for harder math/logic generalization."
    else:
        evidence_classes = "`no_model_validator_smoke`, pending `live_model_local_3b`"
        local_artifacts = ""
        local_section = """## Next Step

Run local 3B with `research/scripts/run_mixed_contract_local_3b.py` under the Windows job-cap wrapper. Preserve row IDs, validator, model config, and evidence class.
"""
        audit_evidence = """`no_model_validator_smoke` for canonical validator validation.

Pending `live_model_local_3b` for local Qwen2.5-3B Q4 model completions."""
        live_allowed = "- Live local model results can be used as a seed-scale benchmark only after job-cap receipts and result JSON are present."
        result_claim = ""
        promotion_rule = "Promote this to paper material only if the held-out result remains positive for `metta_runtime_repair` and the result table explicitly separates prompt-only, repair-prompt, and no-model evidence."
        result_snapshot = ""
        extra_disallowed = ""

    readme = f"""# Mixed Contract Compactification Heldout50

Generated: `{generated_at}`

- Route: `paper_main_claim_extension`
- Project: `mixed_contract_compactification`
- Evidence classes: {evidence_classes}
- Source guide: `research/generated/metta_agent_navigation.md`
- Source seed study: `research/studies/2026-04-28-mixed-contract-compactification-seed`

## Purpose

This is the first held-out suite after the 12-row seed smoke. It broadens the same exact validator family to 50 rows across mixed observable contracts.

## Family Counts

| Family | Rows |
| --- | ---: |
{counts_table}

## Artifacts

- Rows: `rows/mixed_contract_heldout50_rows.jsonl`
- Validator: `validators/validate_mixed_contracts.py`
- Suite config: `configs/heldout50_suite.json`
- Canonical smoke: `results/canonical_validator_smoke/canonical_validator_smoke.results.md`
{local_artifacts}

{local_section}
"""
    plan = f"""# Heldout50 Study Plan

## Hypothesis

MeTTa-scaffolded repair gating should improve exact mixed-contract validity over baseline and prompt-only TRM on held-out rows, but gains must be separated from learned TRM lift.

## Arms

- `baseline`: direct final answer prompt.
- `pure_trm`: TRM contract prompt.
- `metta_runtime`: MeTTa/TRM gate prompt.
- `metta_runtime_repair`: repair-prompt gate using public validator feedback.

## Metrics

- `exact_success`
- `contract_valid`
- `semantic_valid`
- per-family exact rate
- child RSS and job-cap outcome

## Promotion Rule

{promotion_rule}

## Stop Rule

If the lift is concentrated in easy choice or delimiter rows, expand harder schema/tree rows before making a general compactification claim.

{result_snapshot}
"""
    audit = f"""# Claim Audit

## Evidence Class

{audit_evidence}

## Allowed Claims

- The row suite is held out from the 12-row seed smoke.
- The validators separate contract validity from semantic validity across mixed observable contracts.
{live_allowed}
{result_claim}

## Disallowed Claims

- Do not call repair-prompt gains trained TRM lift.
- Do not claim broad reasoning gain from output-contract wins.
- Do not mix canonical validator smoke with live model arms.
- Do not compare this to 9B/27B unless row IDs and validators are identical.
{extra_disallowed}
"""
    config = {
        "generated_at_utc": generated_at,
        "route_id": "paper_main_claim_extension",
        "project_id": "mixed_contract_compactification",
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
    shutil.copyfile(SEED / "validators" / "validate_mixed_contracts.py", VALIDATOR_PATH)
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
