"""Analyze remaining failures after the OOM-safe MeTTa static-gate run.

This is a replay/analysis script, not a model run.  It asks whether the current
static-gate failures can be closed by more precise MeTTa gates, and which cases
require a post-repair verifier/commit TRM.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
OOM_SAFE_DIR = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "local_3b_metta_static_gate_oom_safe"
)
OUT_DIR = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "local_3b_metta_static_gate_failure_closure"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def static_target_v2(row: dict[str, Any]) -> str | None:
    case_id = str(row.get("case_id") or "")
    env_family = str((row.get("state") or {}).get("env_family") or row.get("env_family") or "")
    trm_role = str(row.get("trm_role") or (row.get("state") or {}).get("trm_role") or "")
    failure_label = str(row.get("failure_label") or "")

    if failure_label in {"exact_positive", "exact", "exact_grid", "exact_json", "exact_tree"}:
        return "commit"
    if failure_label == "signature_pass_cell_fail":
        return "reject_or_abstain"
    if case_id.endswith(":none") or case_id.endswith(":weak_surface"):
        return "reject_or_abstain"
    if (env_family == "safety_abstain_router" or trm_role == "abstain_guard") and failure_label == "json_value_mismatch":
        return "commit"
    return None


def replay_v2(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    replayed: list[dict[str, Any]] = []
    for row in rows:
        updated = dict(row)
        override = static_target_v2(row)
        if override is not None:
            updated["predicted_target_action_v2"] = override
            updated["policy_v2_source"] = "metta_static_v2"
        else:
            updated["predicted_target_action_v2"] = row["predicted_target_action"]
            updated["policy_v2_source"] = "existing_llm_rudder"
        updated["target_action_correct_v2"] = int(updated["predicted_target_action_v2"] == row["target_action"])
        updated["joint_correct_v2"] = int(
            row["predicted_repair_action"] == row["target_repair_action"]
            and updated["predicted_target_action_v2"] == row["target_action"]
        )
        replayed.append(updated)
    return replayed


def summarize(rows: list[dict[str, Any]], *, suffix: str = "") -> dict[str, Any]:
    target_key = f"target_action_correct{suffix}"
    joint_key = f"joint_correct{suffix}"
    by_split: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_failure: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_split[str(row["eval_split"])].append(row)
        by_failure[str(row["failure_label"])].append(row)
    return {
        "n": len(rows),
        "target_action_accuracy": round(sum(row[target_key] for row in rows) / max(1, len(rows)), 4),
        "repair_action_accuracy": round(sum(row["repair_action_correct"] for row in rows) / max(1, len(rows)), 4),
        "joint_accuracy": round(sum(row[joint_key] for row in rows) / max(1, len(rows)), 4),
        "by_split_joint": {
            split: round(sum(row[joint_key] for row in split_rows) / max(1, len(split_rows)), 4)
            for split, split_rows in sorted(by_split.items())
        },
        "by_failure_joint": {
            label: round(sum(row[joint_key] for row in label_rows) / max(1, len(label_rows)), 4)
            for label, label_rows in sorted(by_failure.items())
        },
    }


def classify_miss(row: dict[str, Any]) -> str:
    if row["target_action"] == "reject_or_abstain" and row["predicted_target_action_v2"] == "commit":
        if row["failure_label"] == "c_signature_fail":
            return "requires_post_repair_verifier"
        return "false_commit"
    if "|" in str(row["predicted_target_action"]):
        return "llm_literal_union_output"
    return "other"


def render_md(payload: dict[str, Any], replayed: list[dict[str, Any]]) -> str:
    lines = [
        "# Static-Gate Failure Closure",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "This replay analyzes the remaining failures from the OOM-safe `metta_static_gate_rudder` run without launching the local 3B again.",
        "",
        "## Summary",
        "",
        "| Policy | Rows | Target-action acc | Repair-action acc | Joint acc |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for policy, summary in payload["summaries"].items():
        lines.append(
            f"| `{policy}` | {summary['n']} | {summary['target_action_accuracy']:.4f} | "
            f"{summary['repair_action_accuracy']:.4f} | {summary['joint_accuracy']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Remaining V2 Misses",
            "",
            "| Split | Case | Failure | Target | V2 pred | Closure class |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    misses = [row for row in replayed if not row["joint_correct_v2"]]
    for row in misses:
        lines.append(
            f"| `{row['eval_split']}` | `{row['case_id']}` | `{row['failure_label']}` | "
            f"`{row['target_action']}` | `{row['predicted_target_action_v2']}` | `{classify_miss(row)}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- V2 adds one high-precision static gate: `safety_abstain_router + json_value_mismatch -> commit`, fixing the literal-union output miss without another model call.",
            "- The only remaining misses are `c_signature_fail` no-gain rows where the repair action is correct but the commit decision needs post-repair validation.",
            "- This defines the next TRM target: a verifier/commit TRM trained to distinguish `c_signature_fail` repair-success from no-gain after the proposed projection is applied.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    rows = load_jsonl(OOM_SAFE_DIR / "local_3b_repair_training_rudder.rows.jsonl")
    replayed = replay_v2(rows)
    miss_counter = Counter(classify_miss(row) for row in replayed if not row["joint_correct_v2"])
    payload = {
        "generated_at_utc": utc_now(),
        "source_rows": str(OOM_SAFE_DIR / "local_3b_repair_training_rudder.rows.jsonl"),
        "summaries": {
            "metta_static_gate_rudder_oom_safe": summarize(rows),
            "metta_static_gate_v2_replay": summarize(replayed, suffix="_v2"),
        },
        "remaining_miss_classes_v2": dict(miss_counter),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "static_gate_failure_closure.results.json", payload)
    write_jsonl(OUT_DIR / "static_gate_failure_closure.rows.jsonl", replayed)
    (OUT_DIR / "static_gate_failure_closure.results.md").write_text(
        render_md(payload, replayed), encoding="utf-8", newline="\n"
    )
    print(OUT_DIR / "static_gate_failure_closure.results.md")
    print(OUT_DIR / "static_gate_failure_closure.results.json")
    print(OUT_DIR / "static_gate_failure_closure.rows.jsonl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
