"""Sweep post-repair verifier signals for the C-signature commit TRM.

This script makes no LLM calls and trains no neural model. It tests whether the
remaining C-signature false commits are a representation problem: pre-repair
scalar hints fail, while post-repair multi-signal verifier state should be
enough to define a clean commit/veto target.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
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
    / "c_signature_postrepair_verifier_sweep"
)


@dataclass(frozen=True)
class Policy:
    policy_id: str
    signal_class: str
    description: str
    predict: Callable[[dict[str, Any]], str]


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


def state(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("state") or {}


def bool_state(row: dict[str, Any], key: str) -> bool:
    return bool(state(row).get(key))


def float_state(row: dict[str, Any], key: str) -> float:
    value = state(row).get(key)
    return float(value) if value is not None else 0.0


def reward_delta(row: dict[str, Any]) -> float:
    if "target_delta" in row:
        return float(row.get("target_delta") or 0.0)
    return float_state(row, "after_reward") - float_state(row, "before_reward")


def signature_complete(row: dict[str, Any]) -> bool:
    return bool_state(row, "after_t_signature_pass") and bool_state(row, "after_c_signature_pass")


def target_counts(rows: list[dict[str, Any]]) -> Counter[str]:
    return Counter(row["target_action"] for row in rows)


def evaluate_policy(rows: list[dict[str, Any]], policy: Policy) -> dict[str, Any]:
    correct = 0
    false_commit = 0
    false_reject = 0
    expected_delta = 0.0
    committed_negative_delta = 0
    committed = 0
    for row in rows:
        pred = policy.predict(row)
        target = row["target_action"]
        delta = reward_delta(row)
        correct += int(pred == target)
        if pred == "commit":
            committed += 1
            expected_delta += delta
            if delta <= 0.0:
                committed_negative_delta += 1
        if target == "reject_or_abstain" and pred == "commit":
            false_commit += 1
        if target == "commit" and pred == "reject_or_abstain":
            false_reject += 1
    counts = target_counts(rows)
    return {
        "policy_id": policy.policy_id,
        "signal_class": policy.signal_class,
        "description": policy.description,
        "n": len(rows),
        "accuracy": round(correct / max(1, len(rows)), 4),
        "false_commit_rate": round(false_commit / max(1, counts.get("reject_or_abstain", 0)), 4),
        "false_reject_rate": round(false_reject / max(1, counts.get("commit", 0)), 4),
        "false_commit_count": false_commit,
        "false_reject_count": false_reject,
        "committed": committed,
        "committed_negative_delta": committed_negative_delta,
        "expected_delta_if_committed": round(expected_delta, 6),
        "target_counts": dict(counts),
    }


def policies() -> list[Policy]:
    return [
        Policy(
            "always_commit",
            "control",
            "Commit every proposed C-signature repair.",
            lambda row: "commit",
        ),
        Policy(
            "after_signature_complete_only",
            "post_symbolic",
            "Commit when repaired T and C signatures both pass.",
            lambda row: "commit" if signature_complete(row) else "reject_or_abstain",
        ),
        Policy(
            "after_exact_only",
            "post_evaluator_exact",
            "Commit only exact repaired candidates.",
            lambda row: "commit" if bool_state(row, "after_exact") else "reject_or_abstain",
        ),
        Policy(
            "after_signature_and_exact",
            "post_symbolic_plus_exact",
            "Commit only repaired candidates that pass signatures and exact check.",
            lambda row: "commit" if signature_complete(row) and bool_state(row, "after_exact") else "reject_or_abstain",
        ),
        Policy(
            "postrepair_gain_gt_0",
            "post_evaluator_delta",
            "Commit only when repaired reward improves over the pre-repair candidate.",
            lambda row: "commit" if reward_delta(row) > 0.0 else "reject_or_abstain",
        ),
        Policy(
            "postrepair_gain_ge_0p02",
            "post_evaluator_delta",
            "Commit only when repaired reward improves by at least 0.02.",
            lambda row: "commit" if reward_delta(row) >= 0.02 else "reject_or_abstain",
        ),
        Policy(
            "postrepair_gain_ge_0p05",
            "post_evaluator_delta",
            "Commit only when repaired reward improves by at least 0.05.",
            lambda row: "commit" if reward_delta(row) >= 0.05 else "reject_or_abstain",
        ),
        Policy(
            "postrepair_exact_or_gain_gt_0",
            "post_evaluator_multi_signal",
            "Commit exact repairs or non-exact repairs with positive reward delta.",
            lambda row: "commit" if bool_state(row, "after_exact") or reward_delta(row) > 0.0 else "reject_or_abstain",
        ),
        Policy(
            "postrepair_signature_and_gain_gt_0",
            "post_symbolic_plus_delta",
            "Commit only when signatures pass and reward delta is positive.",
            lambda row: "commit" if signature_complete(row) and reward_delta(row) > 0.0 else "reject_or_abstain",
        ),
        Policy(
            "postrepair_non_regression",
            "post_evaluator_delta",
            "Commit when repair does not regress reward.",
            lambda row: "commit" if reward_delta(row) >= 0.0 else "reject_or_abstain",
        ),
    ]


def summaries_by_split(rows_by_split: dict[str, list[dict[str, Any]]], policy: Policy) -> dict[str, dict[str, Any]]:
    return {split: evaluate_policy(rows, policy) for split, rows in rows_by_split.items()}


def select_policy(ranked: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(
        ranked,
        key=lambda item: (
            item["summaries"]["val_seen"]["false_commit_rate"],
            -item["summaries"]["val_seen"]["accuracy"],
            item["summaries"]["val_seen"]["false_reject_rate"],
            item["summaries"]["holdout_seen"]["false_commit_rate"],
            item["policy_id"],
        ),
    )[0]


def prediction_rows(rows: list[dict[str, Any]], selected: Policy) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        row_state = state(row)
        pred = selected.predict(row)
        output.append(
            {
                "split": row["split"],
                "case_id": row["case_id"],
                "target_action": row["target_action"],
                "predicted_action": pred,
                "correct": int(pred == row["target_action"]),
                "target_bucket": row["target_bucket"],
                "reward_delta": reward_delta(row),
                "after_exact": bool_state(row, "after_exact"),
                "after_t_signature_pass": bool_state(row, "after_t_signature_pass"),
                "after_c_signature_pass": bool_state(row, "after_c_signature_pass"),
                "before_reward": row_state.get("before_reward"),
                "after_reward": row_state.get("after_reward"),
                "repair_action": row_state.get("repair_action"),
            }
        )
    return output


def render_contract() -> str:
    return "\n".join(
        [
            "; C-signature post-repair verifier sketch.",
            "; This is an evaluator-backed training target, not a prompt-only LLM result.",
            "",
            "(= (signature-complete $state)",
            "   (and (after-t-signature-pass $state) (after-c-signature-pass $state)))",
            "",
            "(= (positive-repair-delta $state)",
            "   (> (reward-delta $state) 0.0))",
            "",
            "(= (c-signature-commit-action $state)",
            "   (if (or (after-exact $state) (positive-repair-delta $state))",
            "       commit",
            "       reject_or_abstain))",
            "",
            "(= (c-signature-training-signals $state)",
            "   (list (after-exact $state)",
            "         (signature-complete $state)",
            "         (reward-delta $state)",
            "         (c-signature-commit-action $state)))",
            "",
        ]
    )


def render_md(payload: dict[str, Any]) -> str:
    selected = payload["selected_policy"]
    lines = [
        "# C-Signature Post-Repair Verifier Sweep",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "This no-model sweep tests whether the remaining C-signature false commits are solved by exposing richer post-repair verifier state to the commit TRM.",
        "",
        f"Selected policy: `{selected}`",
        "",
        "## Selected Policy Metrics",
        "",
        "| Split | Rows | Accuracy | False commit rate | False reject rate | Expected committed delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for split, summary in payload["selected_summary"].items():
        lines.append(
            f"| `{split}` | {summary['n']} | {summary['accuracy']:.4f} | "
            f"{summary['false_commit_rate']:.4f} | {summary['false_reject_rate']:.4f} | "
            f"{summary['expected_delta_if_committed']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Policy Comparison",
            "",
            "| Policy | Signal class | Val acc | Val false commit | Val false reject | Holdout acc | Holdout false commit | Holdout false reject |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in payload["ranked_policies"]:
        val = item["summaries"]["val_seen"]
        hold = item["summaries"]["holdout_seen"]
        lines.append(
            f"| `{item['policy_id']}` | `{item['signal_class']}` | {val['accuracy']:.4f} | "
            f"{val['false_commit_rate']:.4f} | {val['false_reject_rate']:.4f} | "
            f"{hold['accuracy']:.4f} | {hold['false_commit_rate']:.4f} | {hold['false_reject_rate']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Signature-complete state alone is not enough: the repaired C-signature candidates all pass signatures, including no-gain repairs.",
            "- Exact-only validation is safe but rejects partial improvements, so it is too conservative for a repair curriculum.",
            "- The useful training signal is multi-signal post-repair state: exactness plus positive reward delta. This closes false commits while preserving non-exact improvements.",
            "- This should be reported as an evaluator-backed verifier/commit ceiling and a TRM training target, not as evidence that the 3B prompt solved the case.",
            "",
            "## MeTTa Contract",
            "",
            "```scheme",
            payload["metta_contract"].rstrip(),
            "```",
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
    policy_list = policies()
    ranked = [
        {
            "policy_id": policy.policy_id,
            "signal_class": policy.signal_class,
            "description": policy.description,
            "summaries": summaries_by_split(rows_by_split, policy),
        }
        for policy in policy_list
    ]
    ranked.sort(
        key=lambda item: (
            item["summaries"]["val_seen"]["false_commit_rate"],
            -item["summaries"]["val_seen"]["accuracy"],
            item["summaries"]["val_seen"]["false_reject_rate"],
            item["summaries"]["holdout_seen"]["false_commit_rate"],
            item["policy_id"],
        )
    )
    selected_item = select_policy(ranked)
    selected_policy = next(policy for policy in policy_list if policy.policy_id == selected_item["policy_id"])
    metta_contract = render_contract()
    payload = {
        "generated_at_utc": utc_now(),
        "source_rows": str(PACK_DIR / "c_signature_commit_trm_rows.jsonl"),
        "selected_policy": selected_item["policy_id"],
        "selected_summary": selected_item["summaries"],
        "ranked_policies": ranked,
        "metta_contract": metta_contract,
        "claim_boundary": "No model calls and no neural training. Evaluator-backed policies are verifier ceilings and training targets.",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "c_signature_postrepair_verifier.results.json", payload)
    write_jsonl(OUT_DIR / "c_signature_postrepair_verifier.predictions.jsonl", prediction_rows(rows, selected_policy))
    (OUT_DIR / "c_signature_postrepair_verifier.results.md").write_text(
        render_md(payload), encoding="utf-8", newline="\n"
    )
    (OUT_DIR / "c_signature_postrepair_verifier_contract.metta").write_text(
        metta_contract, encoding="utf-8", newline="\n"
    )
    print(OUT_DIR / "c_signature_postrepair_verifier.results.md")
    print(OUT_DIR / "c_signature_postrepair_verifier.results.json")
    print(OUT_DIR / "c_signature_postrepair_verifier.predictions.jsonl")
    print(OUT_DIR / "c_signature_postrepair_verifier_contract.metta")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
