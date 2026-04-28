"""Build the next verifier/commit TRM pack for Intellect-3 C-signature repairs."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
SPLIT_DIR = ROOT / "research" / "generated" / "near_miss_repair_curriculum" / "splits"
OUT_DIR = ROOT / "research" / "generated" / "c_signature_commit_trm_pack"
LOGIC_FLOW_ROWS = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "intellect3_logic_flow_policy_sweep"
    / "intellect3_logic_flow_policy_sweep.rows.jsonl"
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


def load_logic_index() -> dict[tuple[str, str], dict[str, Any]]:
    if not LOGIC_FLOW_ROWS.exists():
        return {}
    return {
        (str(row.get("row_id")), str(row.get("policy"))): row
        for row in load_jsonl(LOGIC_FLOW_ROWS)
    }


def make_pack_row(row: dict[str, Any], split: str, logic_index: dict[tuple[str, str], dict[str, Any]]) -> dict[str, Any]:
    meta = row.get("meta") or {}
    row_id = str(meta.get("row_id") or "")
    before_logic = logic_index.get((row_id, str(row.get("before_arm"))), {})
    after_logic = logic_index.get((row_id, str(row.get("after_arm"))), {})
    before_reward = float(row["before_reward"])
    after_reward = float(row["after_reward"])
    reward_delta = float(row["delta"])
    before_exact = bool(meta.get("before_exact"))
    after_exact = bool(meta.get("after_exact"))
    return {
        "split": split,
        "case_id": row["case_id"],
        "base_case_key": row.get("base_case_key"),
        "state": {
            "env_family": row["env_family"],
            "trm_role": row["trm_role"],
            "before_arm": row["before_arm"],
            "after_arm": row["after_arm"],
            "failure_label": row["failure_label"],
            "before_reward": before_reward,
            "after_reward": after_reward,
            "reward_delta": reward_delta,
            "repair_action": row["repair_action"],
            "edit_distance": meta.get("edit_distance"),
            "before_exact": before_exact,
            "after_exact": after_exact,
            "before_cell_accuracy": before_logic.get("cell_accuracy", before_reward),
            "after_cell_accuracy": after_logic.get("cell_accuracy", after_reward),
            "before_t_signature_pass": before_logic.get("t_signature_pass"),
            "before_c_signature_pass": before_logic.get("c_signature_pass"),
            "after_t_signature_pass": after_logic.get("t_signature_pass"),
            "after_c_signature_pass": after_logic.get("c_signature_pass"),
            "before_selected": before_logic.get("selected"),
            "after_selected": after_logic.get("selected"),
            "candidate_excerpt": row["candidate_excerpt"],
            "repaired_excerpt": row["repaired_excerpt"],
            "post_repair_signals": {
                "after_exact": after_exact,
                "positive_reward_delta": reward_delta > 0.0,
                "non_regression": reward_delta >= 0.0,
                "signature_complete": bool(after_logic.get("t_signature_pass")) and bool(after_logic.get("c_signature_pass")),
            },
        },
        "target_action": "commit" if row["bucket"] in {"repair_success", "partial_repair_improvement"} else "reject_or_abstain",
        "target_bucket": row["bucket"],
        "target_delta": reward_delta,
        "supervision_weight": 2.5 if row["bucket"] == "repair_success" else 1.5 if row["bucket"] == "partial_repair_improvement" else 2.0,
        "eval_metrics": ["false_commit_rate", "false_reject_rate", "expected_reward_delta"],
    }


def load_pack_rows() -> list[dict[str, Any]]:
    logic_index = load_logic_index()
    rows: list[dict[str, Any]] = []
    for split in ["train", "val_seen", "holdout_seen"]:
        for row in load_jsonl(SPLIT_DIR / f"{split}.curriculum.jsonl"):
            if row.get("env_family") == "intellect3_logic" and row.get("failure_label") == "c_signature_fail":
                rows.append(make_pack_row(row, split, logic_index))
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_split: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_split_target: dict[str, Counter[str]] = defaultdict(Counter)
    by_bucket = Counter(row["target_bucket"] for row in rows)
    for row in rows:
        by_split[row["split"]].append(row)
        by_split_target[row["split"]][row["target_action"]] += 1
    return {
        "generated_at_utc": utc_now(),
        "row_count": len(rows),
        "by_split": {split: len(split_rows) for split, split_rows in sorted(by_split.items())},
        "by_split_target": {split: dict(counter) for split, counter in sorted(by_split_target.items())},
        "by_bucket": dict(by_bucket),
        "purpose": "Train a post-repair verifier/commit TRM for c_signature_fail rows where MeTTa can select the repair action but pre-repair 3B over-commits no-gain repairs.",
    }


def render_md(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# C-Signature Commit TRM Pack",
        "",
        f"Generated: `{summary['generated_at_utc']}`",
        "",
        "This pack isolates the remaining Intellect-3 logic failure mode after MeTTa action-space narrowing: deciding whether a proposed C-signature repair should be committed or rejected.",
        "",
        "## Summary",
        "",
        f"- Rows: `{summary['row_count']}`",
        f"- Purpose: {summary['purpose']}",
        "",
        "## Companion Artifacts",
        "",
        "- Training plan: `research/generated/c_signature_commit_trm_pack/c_signature_commit_trm_training_plan.md`",
        "- Capped Windows wrapper: `research/scripts/run_c_signature_commit_trm_jobcap.ps1`",
        "- Post-repair verifier sweep: `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/c_signature_postrepair_verifier_sweep/c_signature_postrepair_verifier.results.md`",
        "",
        "| Split | Rows | Target mix |",
        "| --- | ---: | --- |",
    ]
    for split, count in summary["by_split"].items():
        mix = ", ".join(f"`{target}`:{value}" for target, value in sorted(summary["by_split_target"][split].items()))
        lines.append(f"| `{split}` | {count} | {mix} |")
    lines.extend(["", "## Bucket Mix", "", "| Bucket | Rows |", "| --- | ---: |"])
    for bucket, count in sorted(summary["by_bucket"].items()):
        lines.append(f"| `{bucket}` | {count} |")
    lines.extend(
        [
            "",
            "## Training Interpretation",
            "",
            "- `commit` rows are successful or partially improving C-signature repairs.",
            "- `reject_or_abstain` rows are no-gain repairs that the 3B static-gate rudder still tends to over-commit.",
            "- The target TRM should run after MeTTa proposes the C-signature repair, not before repair-action selection.",
            "- The pack preserves post-repair signals (`after_exact`, reward delta, and signature pass state) so verifier TRMs can learn from multiple success metrics instead of a single scalar reward.",
            "- Report false-commit rate as the primary safety metric; exact/joint accuracy alone hides no-gain over-commit.",
            "",
            "## High-Risk Reject Rows",
            "",
            "| Split | Case | Before reward | After reward | Edit distance | After exact | Target |",
            "| --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in rows:
        if row["target_action"] == "reject_or_abstain":
            state = row["state"]
            lines.append(
                f"| `{row['split']}` | `{row['case_id']}` | {float(state['before_reward']):.4f} | "
                f"{float(state['after_reward']):.4f} | {state.get('edit_distance')} | "
                f"`{state.get('after_exact')}` | `{row['target_action']}` |"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    rows = load_pack_rows()
    summary = summarize(rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(OUT_DIR / "c_signature_commit_trm_rows.jsonl", rows)
    write_json(OUT_DIR / "c_signature_commit_trm_summary.json", summary)
    (OUT_DIR / "c_signature_commit_trm_pack.md").write_text(render_md(summary, rows), encoding="utf-8", newline="\n")
    print(OUT_DIR / "c_signature_commit_trm_pack.md")
    print(OUT_DIR / "c_signature_commit_trm_rows.jsonl")
    print(OUT_DIR / "c_signature_commit_trm_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
