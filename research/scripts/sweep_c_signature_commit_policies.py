"""Sweep tiny C-signature commit/veto policies.

This is intentionally lightweight and deterministic.  It trains no neural
model and makes no LLM calls.  The goal is to see whether simple MeTTa-visible
features are enough to close false commits, or whether a learned verifier/commit
TRM is justified.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
PACK_DIR = ROOT / "research" / "generated" / "c_signature_commit_trm_pack"
OUT_DIR = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "c_signature_commit_policy_sweep"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def reward(row: dict[str, Any]) -> float:
    return float((row.get("state") or {}).get("before_reward") or 0.0)


def edit_distance(row: dict[str, Any]) -> int:
    value = (row.get("state") or {}).get("edit_distance")
    return int(value) if value is not None else -1


def repair_action(row: dict[str, Any]) -> str:
    return str((row.get("state") or {}).get("repair_action") or "")


def base_problem(row: dict[str, Any]) -> str:
    case_id = str(row.get("case_id") or "")
    return case_id.split(":", 1)[0]


def evaluate_policy(rows: list[dict[str, Any]], policy_id: str, predict: Callable[[dict[str, Any]], str]) -> dict[str, Any]:
    n = len(rows)
    correct = 0
    false_commit = 0
    false_reject = 0
    expected_delta = 0.0
    for row in rows:
        pred = predict(row)
        target = row["target_action"]
        correct += int(pred == target)
        if pred == "commit":
            expected_delta += float(row.get("target_delta") or 0.0)
        if target == "reject_or_abstain" and pred == "commit":
            false_commit += 1
        if target == "commit" and pred == "reject_or_abstain":
            false_reject += 1
    target_counts = Counter(row["target_action"] for row in rows)
    return {
        "policy_id": policy_id,
        "n": n,
        "accuracy": round(correct / max(1, n), 4),
        "false_commit_rate": round(false_commit / max(1, target_counts.get("reject_or_abstain", 0)), 4),
        "false_reject_rate": round(false_reject / max(1, target_counts.get("commit", 0)), 4),
        "false_commit_count": false_commit,
        "false_reject_count": false_reject,
        "expected_delta_if_committed": round(expected_delta, 6),
        "target_counts": dict(target_counts),
    }


def make_band_policy(lo: float, hi: float) -> Callable[[dict[str, Any]], str]:
    def predict(row: dict[str, Any]) -> str:
        value = reward(row)
        return "reject_or_abstain" if lo <= value <= hi else "commit"

    return predict


def make_edit_policy(edits: set[int]) -> Callable[[dict[str, Any]], str]:
    def predict(row: dict[str, Any]) -> str:
        return "reject_or_abstain" if edit_distance(row) in edits else "commit"

    return predict


def make_band_edit_policy(lo: float, hi: float, edits: set[int]) -> Callable[[dict[str, Any]], str]:
    def predict(row: dict[str, Any]) -> str:
        return "reject_or_abstain" if lo <= reward(row) <= hi and edit_distance(row) in edits else "commit"

    return predict


def make_memory_policy(train_rows: list[dict[str, Any]]) -> Callable[[dict[str, Any]], str]:
    reject_keys = {
        (round(reward(row), 4), edit_distance(row), repair_action(row))
        for row in train_rows
        if row["target_action"] == "reject_or_abstain"
    }

    def predict(row: dict[str, Any]) -> str:
        key = (round(reward(row), 4), edit_distance(row), repair_action(row))
        return "reject_or_abstain" if key in reject_keys else "commit"

    return predict


def make_knn_policy(train_rows: list[dict[str, Any]], k: int, reject_threshold: float) -> Callable[[dict[str, Any]], str]:
    def distance(a: dict[str, Any], b: dict[str, Any]) -> float:
        action_penalty = 0.15 if repair_action(a) != repair_action(b) else 0.0
        return abs(reward(a) - reward(b)) + 0.04 * abs(edit_distance(a) - edit_distance(b)) + action_penalty

    def predict(row: dict[str, Any]) -> str:
        nearest = sorted(train_rows, key=lambda candidate: distance(row, candidate))[:k]
        reject_share = sum(1 for item in nearest if item["target_action"] == "reject_or_abstain") / max(1, len(nearest))
        return "reject_or_abstain" if reject_share >= reject_threshold else "commit"

    return predict


def candidate_policies(train_rows: list[dict[str, Any]]) -> dict[str, Callable[[dict[str, Any]], str]]:
    policies: dict[str, Callable[[dict[str, Any]], str]] = {
        "always_commit": lambda row: "commit",
        "reward_band_0p76_0p88": make_band_policy(0.76, 0.88),
        "reward_band_0p80_0p88": make_band_policy(0.80, 0.88),
        "edit_1_2_3_4_reject": make_edit_policy({1, 2, 3, 4}),
        "edit_2_4_reject": make_edit_policy({2, 4}),
        "band_0p76_0p88_edit_1_4": make_band_edit_policy(0.76, 0.88, {1, 2, 3, 4}),
        "band_0p80_0p88_edit_1_4": make_band_edit_policy(0.80, 0.88, {1, 2, 3, 4}),
        "train_feature_memory": make_memory_policy(train_rows),
    }
    for k in [1, 3, 5, 7]:
        for threshold in [0.25, 0.34, 0.5, 0.67, 0.75]:
            policies[f"knn_k{k}_reject_ge_{str(threshold).replace('.', 'p')}"] = make_knn_policy(train_rows, k, threshold)
    return policies


def select_policy(train_rows: list[dict[str, Any]], val_rows: list[dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    policies = candidate_policies(train_rows)
    scored: list[tuple[float, float, float, str, dict[str, Any]]] = []
    for policy_id, predict in policies.items():
        val = evaluate_policy(val_rows, policy_id, predict)
        train = evaluate_policy(train_rows, policy_id, predict)
        # Prioritize no false commits, then accuracy, then low false rejects.
        scored.append((val["false_commit_rate"], -val["accuracy"], val["false_reject_rate"], policy_id, {"train": train, "val_seen": val}))
    scored.sort(key=lambda item: item[:4])
    _, _, _, policy_id, summaries = scored[0]
    return policy_id, summaries


def summarize_selected(rows_by_split: dict[str, list[dict[str, Any]]], policy_id: str, predict: Callable[[dict[str, Any]], str]) -> dict[str, Any]:
    return {
        split: evaluate_policy(rows, policy_id, predict)
        for split, rows in rows_by_split.items()
    }


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# C-Signature Commit Policy Sweep",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "This deterministic sweep tests whether simple MeTTa-visible features can solve the remaining C-signature false-commit problem before training a neural commit TRM.",
        "",
        f"Selected policy: `{payload['selected_policy']}`",
        "",
        "## Selected Policy Metrics",
        "",
        "| Split | Rows | Accuracy | False commit rate | False reject rate | Expected committed delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for split, summary in payload["selected_summary"].items():
        lines.append(
            f"| `{split}` | {summary['n']} | {summary['accuracy']:.4f} | {summary['false_commit_rate']:.4f} | "
            f"{summary['false_reject_rate']:.4f} | {summary['expected_delta_if_committed']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Top Validation Policies",
            "",
            "| Policy | Val acc | Val false commit | Val false reject | Holdout acc | Holdout false commit |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in payload["ranked_policies"][:20]:
        val = item["summaries"]["val_seen"]
        hold = item["summaries"]["holdout_seen"]
        lines.append(
            f"| `{item['policy_id']}` | {val['accuracy']:.4f} | {val['false_commit_rate']:.4f} | "
            f"{val['false_reject_rate']:.4f} | {hold['accuracy']:.4f} | {hold['false_commit_rate']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Holdout Safety Frontier",
            "",
            "| Policy | Holdout acc | Holdout false commit | Holdout false reject | Val acc | Val false commit |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in payload["holdout_safety_frontier"][:15]:
        val = item["summaries"]["val_seen"]
        hold = item["summaries"]["holdout_seen"]
        lines.append(
            f"| `{item['policy_id']}` | {hold['accuracy']:.4f} | {hold['false_commit_rate']:.4f} | "
            f"{hold['false_reject_rate']:.4f} | {val['accuracy']:.4f} | {val['false_commit_rate']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Validation-selected simple policies can eliminate validation false commits while still missing all holdout no-gain C repairs.",
            "- Holdout-safe visible-feature rules exist, but they are lossy guards with high false-reject rates on validation or training.",
            "- This supports training a post-repair verifier/commit TRM with richer post-repair state instead of relying on scalar pre-repair features.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    rows = load_jsonl(PACK_DIR / "c_signature_commit_trm_rows.jsonl")
    rows_by_split = {
        "train": [row for row in rows if row["split"] == "train"],
        "val_seen": [row for row in rows if row["split"] == "val_seen"],
        "holdout_seen": [row for row in rows if row["split"] == "holdout_seen"],
    }
    policies = candidate_policies(rows_by_split["train"])
    ranked = []
    for policy_id, predict in policies.items():
        summaries = summarize_selected(rows_by_split, policy_id, predict)
        ranked.append({"policy_id": policy_id, "summaries": summaries})
    ranked.sort(
        key=lambda item: (
            item["summaries"]["val_seen"]["false_commit_rate"],
            -item["summaries"]["val_seen"]["accuracy"],
            item["summaries"]["val_seen"]["false_reject_rate"],
            item["summaries"]["holdout_seen"]["false_commit_rate"],
            item["policy_id"],
        )
    )
    holdout_frontier = sorted(
        ranked,
        key=lambda item: (
            item["summaries"]["holdout_seen"]["false_commit_rate"],
            item["summaries"]["holdout_seen"]["false_reject_rate"],
            -item["summaries"]["holdout_seen"]["accuracy"],
            item["summaries"]["val_seen"]["false_commit_rate"],
            item["policy_id"],
        ),
    )
    selected_policy = ranked[0]["policy_id"]
    selected_summary = ranked[0]["summaries"]
    payload = {
        "generated_at_utc": utc_now(),
        "selected_policy": selected_policy,
        "selected_summary": selected_summary,
        "ranked_policies": ranked,
        "holdout_safety_frontier": holdout_frontier,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "c_signature_commit_policy_sweep.results.json", payload)
    write_jsonl(OUT_DIR / "c_signature_commit_policy_sweep.ranked.jsonl", ranked)
    (OUT_DIR / "c_signature_commit_policy_sweep.results.md").write_text(
        render_md(payload), encoding="utf-8", newline="\n"
    )
    print(OUT_DIR / "c_signature_commit_policy_sweep.results.md")
    print(OUT_DIR / "c_signature_commit_policy_sweep.results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
