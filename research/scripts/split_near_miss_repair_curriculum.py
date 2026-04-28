"""Split the near-miss repair curriculum into train/eval artifacts.

The split is deterministic and leakage-aware:
- policy variants for the same base case stay in the same split;
- rare failure labels are reserved as unseen-family holdout;
- Pure-TRM rows are exported beside the richer curriculum rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
DEFAULT_CURRICULUM_DIR = ROOT / "research" / "generated" / "near_miss_repair_curriculum"
DEFAULT_OUT_DIR = DEFAULT_CURRICULUM_DIR / "splits"

UNSEEN_FAILURE_LABELS = {
    "bullet_word_count_failure",
    "grid_shape_failure",
    "hashtag_contract_failure",
    "json_parse_failure",
    "json_value_mismatch",
    "partial_tree",
}

SPLIT_FILENAMES = {
    "train": "train.curriculum.jsonl",
    "val_seen": "val_seen.curriculum.jsonl",
    "holdout_seen": "holdout_seen.curriculum.jsonl",
    "holdout_unseen_family": "holdout_unseen_family.curriculum.jsonl",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create deterministic train/eval splits for the near-miss repair curriculum.")
    parser.add_argument("--curriculum-dir", default=str(DEFAULT_CURRICULUM_DIR))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--train-pct", type=int, default=70)
    parser.add_argument("--val-pct", type=int, default=15)
    parser.add_argument(
        "--unseen-label",
        action="append",
        default=[],
        help="Additional failure_label to reserve entirely as unseen-family holdout.",
    )
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def stable_percent(key: str) -> int:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100


def base_case_key(row: dict[str, Any]) -> str:
    meta = row.get("meta") or {}
    row_id = str(meta.get("row_id") or "").strip()
    case_id = str(row.get("case_id") or "").strip()
    if not row_id and ":" in case_id:
        row_id = case_id.split(":", 1)[0]
    return "|".join(
        [
            str(row.get("source") or ""),
            str(row.get("env_family") or ""),
            str(row.get("trm_role") or ""),
            row_id or case_id,
        ]
    )


def assign_split(
    row: dict[str, Any],
    *,
    train_pct: int,
    val_pct: int,
    unseen_labels: set[str],
    unseen_case_keys: set[str],
) -> str:
    if base_case_key(row) in unseen_case_keys or str(row.get("failure_label") or "") in unseen_labels:
        return "holdout_unseen_family"
    bucket = stable_percent(base_case_key(row))
    if bucket < train_pct:
        return "train"
    if bucket < train_pct + val_pct:
        return "val_seen"
    return "holdout_seen"


def commit_target(row: dict[str, Any]) -> str:
    bucket = str(row.get("bucket") or "")
    if bucket in {"repair_success", "partial_repair_improvement", "exact_positive"}:
        return "commit"
    if float(row.get("after_reward") or 0.0) > float(row.get("before_reward") or 0.0):
        return "commit"
    return "reject_or_abstain"


def pure_trm_row(row: dict[str, Any]) -> dict[str, Any]:
    target = commit_target(row)
    return {
        "state": {
            "env_family": row["env_family"],
            "case_id": row["case_id"],
            "trm_role": row["trm_role"],
            "before_arm": row["before_arm"],
            "after_arm": row["after_arm"],
            "before_reward": row["before_reward"],
            "failure_label": row["failure_label"],
            "candidate_excerpt": row["candidate_excerpt"],
        },
        "tools": [
            {"name": "route_gate", "result": row["trm_role"]},
            {"name": "validate_gate", "result": row["failure_label"]},
            {"name": "repair_gate", "result": row["repair_action"]},
            {"name": "commit_gate", "result": "commit" if target == "commit" else "reject"},
        ],
        "action": row["repair_action"],
        "target_action": target,
        "bucket": row["bucket"],
        "supervision_weight": supervision_weight(row),
        "meta": {
            "source": row["source"],
            "evidence_class": row["evidence_class"],
            "delta": row["delta"],
            "split": row["split"],
            "base_case_key": base_case_key(row),
        },
    }


def supervision_weight(row: dict[str, Any]) -> float:
    bucket = str(row.get("bucket") or "")
    if bucket == "repair_success":
        return 2.5
    if bucket == "partial_repair_improvement":
        return 1.5
    if bucket == "exact_positive":
        return 2.0
    if bucket == "repair_failure_or_no_gain":
        return 0.75
    return 1.0


def count_rows(rows: Iterable[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(Counter(str(row.get(field) or "") for row in rows))


def nested_counts(rows: Iterable[dict[str, Any]], left: str, right: str) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        counts[str(row.get(left) or "")][str(row.get(right) or "")] += 1
    return {key: dict(counter) for key, counter in sorted(counts.items())}


def spec_filter(rows: list[dict[str, Any]], *, roles: set[str], labels: set[str] | None = None) -> list[dict[str, Any]]:
    selected = [row for row in rows if str(row.get("trm_role") or "") in roles]
    if labels is not None:
        selected = [row for row in selected if str(row.get("failure_label") or "") in labels]
    return selected


def make_trainer_specs(rows: list[dict[str, Any]]) -> dict[str, Any]:
    specs = {
        "repair_verifier_logic_c_signature": {
            "purpose": "Train the logic repair/verifier circuit around C-signature failure, exact positives, and signature-pass cell failures.",
            "roles": ["hard_reasoning_logic"],
            "failure_labels": ["c_signature_fail", "signature_pass_cell_fail", "exact_positive"],
            "target_gates": ["validate_gate", "repair_gate", "commit_gate"],
            "eval_metrics": ["exact_delta", "cell_accuracy_delta", "false_commit_rate", "repair_regression_rate"],
        },
        "commit_veto_multirole": {
            "purpose": "Train commit/veto policy to accept repairs and positives while rejecting no-gain repairs.",
            "roles": ["abstain_guard", "choice_contract", "hard_reasoning_logic", "hard_reasoning_numeric", "structured_map"],
            "failure_labels": None,
            "target_gates": ["commit_gate"],
            "eval_metrics": ["false_commit_rate", "false_reject_rate", "expected_reward_delta"],
        },
        "structured_contract_repair": {
            "purpose": "Train schema, tree, and choice-contract repair gates where symbolic closure is available.",
            "roles": ["choice_contract", "structured_map"],
            "failure_labels": None,
            "target_gates": ["validate_gate", "repair_gate", "commit_gate"],
            "eval_metrics": ["contract_validity", "canonical_exact", "repair_regression_rate"],
        },
        "numeric_teacher_auditor": {
            "purpose": "Keep hard numeric rows as teacher-candidate audit and veto data, not standalone solver training.",
            "roles": ["hard_reasoning_numeric"],
            "failure_labels": None,
            "target_gates": ["validate_gate", "commit_gate"],
            "eval_metrics": ["candidate_selection_accuracy", "false_commit_rate"],
        },
        "abstain_guard": {
            "purpose": "Train abstain/route guard rows where a malformed or unsafe candidate should be rejected.",
            "roles": ["abstain_guard"],
            "failure_labels": None,
            "target_gates": ["route_gate", "commit_gate"],
            "eval_metrics": ["reject_accuracy", "false_accept_rate"],
        },
    }

    by_split = {split: [row for row in rows if row["split"] == split] for split in SPLIT_FILENAMES}
    for spec_id, spec in specs.items():
        labels = set(spec["failure_labels"]) if spec["failure_labels"] is not None else None
        roles = set(spec["roles"])
        spec["row_counts"] = {
            split: len(spec_filter(split_rows, roles=roles, labels=labels))
            for split, split_rows in by_split.items()
        }
    return specs


def summarize(rows: list[dict[str, Any]], unseen_labels: set[str]) -> dict[str, Any]:
    by_split = {split: [row for row in rows if row["split"] == split] for split in SPLIT_FILENAMES}
    return {
        "generated_at_utc": utc_now(),
        "row_count": len(rows),
        "unseen_failure_labels": sorted(unseen_labels),
        "split_counts": {split: len(split_rows) for split, split_rows in by_split.items()},
        "split_bucket_counts": {split: count_rows(split_rows, "bucket") for split, split_rows in by_split.items()},
        "split_role_counts": {split: count_rows(split_rows, "trm_role") for split, split_rows in by_split.items()},
        "split_failure_label_counts": {split: count_rows(split_rows, "failure_label") for split, split_rows in by_split.items()},
        "role_bucket_counts": nested_counts(rows, "trm_role", "bucket"),
        "trainer_specs": make_trainer_specs(rows),
    }


def render_md(summary: dict[str, Any]) -> str:
    lines = [
        "# Near-Miss Repair Curriculum Splits",
        "",
        f"Generated: `{summary['generated_at_utc']}`",
        "",
        "These files convert the near-miss repair curriculum into leakage-aware train/eval slices for repair, verifier, and commit/veto TRMs.",
        "",
        "## Split Counts",
        "",
        "| Split | Rows | Buckets | Roles |",
        "| --- | ---: | --- | --- |",
    ]
    for split, count in summary["split_counts"].items():
        buckets = ", ".join(f"`{key}`:{value}" for key, value in sorted(summary["split_bucket_counts"][split].items()))
        roles = ", ".join(f"`{key}`:{value}" for key, value in sorted(summary["split_role_counts"][split].items()))
        lines.append(f"| `{split}` | {count} | {buckets} | {roles} |")
    lines.extend(
        [
            "",
            "## Unseen-Family Holdout",
            "",
            ", ".join(f"`{label}`" for label in summary["unseen_failure_labels"]),
            "",
            "## Candidate Trainer Specs",
            "",
            "| Spec | Purpose | Train | Val seen | Holdout seen | Holdout unseen-family |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for spec_id, spec in summary["trainer_specs"].items():
        counts = spec["row_counts"]
        lines.append(
            f"| `{spec_id}` | {spec['purpose']} | {counts['train']} | {counts['val_seen']} | "
            f"{counts['holdout_seen']} | {counts['holdout_unseen_family']} |"
        )
    lines.extend(
        [
            "",
            "## Method Notes",
            "",
            "- Treat `train` as replay/curriculum data, not benchmark evidence.",
            "- Use `val_seen` to tune repair thresholds inside known failure families.",
            "- Use `holdout_seen` to test case-level generalization without family shift.",
            "- Use `holdout_unseen_family` to test whether MeTTa-framed gates transfer to new failure labels.",
            "- Keep `hard_reasoning_numeric` under teacher-auditor or veto training until stronger candidate generators exist.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    if args.train_pct <= 0 or args.val_pct <= 0 or args.train_pct + args.val_pct >= 100:
        raise ValueError("--train-pct and --val-pct must be positive and sum to less than 100")

    curriculum_dir = Path(args.curriculum_dir)
    out_dir = Path(args.out_dir)
    rows = load_jsonl(curriculum_dir / "near_miss_repair_curriculum.jsonl")
    unseen_labels = set(UNSEEN_FAILURE_LABELS) | {str(label).strip() for label in args.unseen_label if str(label).strip()}
    unseen_case_keys = {
        base_case_key(row)
        for row in rows
        if str(row.get("failure_label") or "") in unseen_labels
    }

    split_rows: dict[str, list[dict[str, Any]]] = {split: [] for split in SPLIT_FILENAMES}
    for row in rows:
        split = assign_split(
            row,
            train_pct=args.train_pct,
            val_pct=args.val_pct,
            unseen_labels=unseen_labels,
            unseen_case_keys=unseen_case_keys,
        )
        enriched = dict(row)
        enriched["split"] = split
        enriched["base_case_key"] = base_case_key(row)
        split_rows[split].append(enriched)

    all_rows = [row for split in SPLIT_FILENAMES for row in split_rows[split]]
    summary = summarize(all_rows, unseen_labels)

    out_dir.mkdir(parents=True, exist_ok=True)
    for split, filename in SPLIT_FILENAMES.items():
        rows_for_split = sorted(split_rows[split], key=lambda row: (row["base_case_key"], row["case_id"], row["after_arm"]))
        write_jsonl(out_dir / filename, rows_for_split)
        write_jsonl(out_dir / filename.replace(".curriculum.", ".pure_trm."), [pure_trm_row(row) for row in rows_for_split])

    write_json(out_dir / "split_manifest.json", summary)
    write_json(out_dir / "candidate_trainer_specs.json", summary["trainer_specs"])
    (out_dir / "near_miss_repair_splits.md").write_text(render_md(summary), encoding="utf-8", newline="\n")

    print(out_dir / "near_miss_repair_splits.md")
    print(out_dir / "split_manifest.json")
    print(out_dir / "candidate_trainer_specs.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
