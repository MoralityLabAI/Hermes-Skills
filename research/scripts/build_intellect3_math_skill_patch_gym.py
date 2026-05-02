"""Build an Intellect-3-Math skill-patch gym for MeTTa/TRM self-improvement.

The gym treats skill revisions as candidates that must pass held-out commit
gates.  It does not assume a stronger prompt is automatically better.  Instead
it emits:

- a patch bank of candidate skill contracts
- a MeTTa gate contract for patch adoption
- TRM rows for commit/veto training from observed live evaluations
- a next-run plan for live patch search on snacksack or another endpoint
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "research" / "studies" / "2026-04-22-metta-trm-hermes-pipeline" / "artifacts"
DEFAULT_SOURCE = ARTIFACTS / "intellect3_math_metta_self_improve_27b_20260502"
DEFAULT_OUT = ARTIFACTS / "intellect3_math_skill_patch_gym_20260502"


CURRENT_SKILL_TASK = (
    "Hermes/Intellect-3-Math-v1. Parse the givens, solve with a short candidate path, "
    "verify arithmetic consistency, and commit only the final integer answer. No prose, no tags, no markdown."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Intellect-3-Math MeTTa skill-patch gym artifacts.")
    parser.add_argument("--source-dir", default=str(DEFAULT_SOURCE), type=Path)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), type=Path)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def patch_bank(source_dir: Path) -> list[dict[str, Any]]:
    patch_path = source_dir / "metta_self_improvement_patch.json"
    live_patch = load_json(patch_path) if patch_path.exists() else {}
    live_prefix = str(live_patch.get("task_prefix") or "").strip()

    return [
        {
            "patch_id": "raw_baseline_no_skill",
            "source": "control",
            "status": "comparison_only",
            "task_prefix": "Solve the math problem. Return only the final integer answer.",
            "metta_rules": [
                "(= (patch_status raw_baseline_no_skill) comparison_only)",
                "(= (adopt_patch raw_baseline_no_skill) False)",
            ],
            "intended_failure_modes": ["no_skill_control"],
        },
        {
            "patch_id": "incumbent_current_skill",
            "source": "codex_5_4_incumbent",
            "status": "incumbent",
            "task_prefix": CURRENT_SKILL_TASK,
            "metta_rules": [
                "(= (commit-skill-patch incumbent_current_skill) incumbent-baseline)",
                "(= (reject-if-no-heldout-gain $patch) True)",
            ],
            "intended_failure_modes": ["none_baseline"],
        },
        {
            "patch_id": "qwen27b_auditor_patch",
            "source": "live_qwen27b_drafted",
            "status": "observed_rejected",
            "task_prefix": live_prefix,
            "metta_rules": live_patch.get("metta_rules") or [],
            "intended_failure_modes": live_patch.get("expected_failure_modes") or ["magnitude_error", "constraint_inconsistency"],
        },
        {
            "patch_id": "codex_domain_router_v1",
            "source": "codex_gym_seed",
            "status": "candidate_pending_live_eval",
            "task_prefix": (
                "Hermes/Intellect-3-Math-Domain-Router-v1. First privately classify the problem as geometry, "
                "number theory, combinatorics, algebra, sequence, or extremal/counting. Use the matching invariant: "
                "geometry -> diagram relation and requested expression; number theory -> divisibility/modular constraints; "
                "combinatorics -> counted object, overcount correction, and boundary cases; algebra -> solve symbolic relation "
                "then substitute. Before output, check answer shape and magnitude against the prompt. Return only the final integer."
            ),
            "metta_rules": [
                "(= (route-domain geometry) diagram-expression-check)",
                "(= (route-domain combinatorics) count-object-overcount-boundary)",
                "(= (route-domain number_theory) modular-divisibility-check)",
                "(= (commit-answer $a) (and (integer $a) (shape-valid $a) (magnitude-plausible $a)))",
            ],
            "intended_failure_modes": ["wrong_domain_tool", "intermediate_answer_commit", "magnitude_outlier"],
        },
        {
            "patch_id": "codex_answer_shape_verifier_v1",
            "source": "codex_gym_seed",
            "status": "candidate_pending_live_eval",
            "task_prefix": (
                "Hermes/Intellect-3-Math-Answer-Shape-Verifier-v1. Solve privately, but treat the final requested "
                "quantity as a contract. If the prompt asks for a+b+c, compute a,b,c explicitly before summing. "
                "If it asks for maximum k, prove the bound and construction mentally. If it asks for a count, verify "
                "non-negativity, integrality, and small cases. Reject answers that look like copied constants or raw "
                "intermediate values. Return only the final integer."
            ),
            "metta_rules": [
                "(= (requested-form a+b+c) require-components-before-sum)",
                "(= (requested-form maximum-k) require-upper-lower-bound)",
                "(= (requested-form count) require-integral-nonnegative-smallcase)",
                "(= (veto-answer copied_constant) True)",
            ],
            "intended_failure_modes": ["answer_shape_mismatch", "copied_constant", "missing_bound_check"],
        },
        {
            "patch_id": "codex_slow_path_trigger_v1",
            "source": "codex_gym_seed",
            "status": "candidate_pending_live_eval",
            "task_prefix": (
                "Hermes/Intellect-3-Math-Slow-Path-Trigger-v1. Use concise private reasoning. Trigger a slow path when "
                "the problem contains triangle, probability, maximum, all possible, modulo, polynomial, sequence, or large "
                "exponent wording. On slow path, identify the invariant and one verification equation before committing. "
                "Do not emit the first plausible integer. Return only the final integer answer."
            ),
            "metta_rules": [
                "(= (slow-path-trigger triangle) geometry-invariant)",
                "(= (slow-path-trigger maximum) extremal-bound)",
                "(= (slow-path-trigger large_exponent) modular-or-log-scale-check)",
                "(= (reject-first-plausible-integer) True)",
            ],
            "intended_failure_modes": ["fast_guess", "large_number_hallucination", "unverified_extremal_answer"],
        },
        {
            "patch_id": "codex_patch_commit_controller_v1",
            "source": "codex_gym_seed",
            "status": "controller_not_solver",
            "task_prefix": (
                "Hermes/Intellect-3-Math-Patch-Commit-Controller-v1. Generate no new math answer unless the candidate "
                "passes answer-shape, magnitude, sign, and domain-invariant checks. If candidate confidence is low, prefer "
                "the incumbent skill output over a speculative mutation. Return only the selected integer."
            ),
            "metta_rules": [
                "(= (adopt-patch $p) (and (> (heldout-exact $p) (heldout-exact incumbent)) (>= (fixes $p) (regressions $p))))",
                "(= (candidate-commit $answer) (and (shape-valid $answer) (not (magnitude-outlier $answer))))",
                "(= (fallback) incumbent_current_skill)",
            ],
            "intended_failure_modes": ["patch_overfit", "regression_without_fix", "candidate_selection_error"],
        },
    ]


def summarize_observed(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_arm: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_arm[str(row.get("arm"))].append(row)
    arms: dict[str, Any] = {}
    for arm, arm_rows in sorted(by_arm.items()):
        arms[arm] = {
            "rows": len(arm_rows),
            "exact": sum(1 for row in arm_rows if row.get("exact")),
            "exact_rate": round(sum(1 for row in arm_rows if row.get("exact")) / max(1, len(arm_rows)), 6),
            "common_actions": dict(Counter(str(row.get("action")) for row in arm_rows).most_common(8)),
        }
    transitions = Counter()
    by_row: dict[str, dict[str, Any]] = defaultdict(dict)
    for row in rows:
        by_row[str(row.get("row_id"))][str(row.get("arm"))] = row
    for group in by_row.values():
        incumbent = group.get("current_skill")
        candidate = group.get("metta_self_improved")
        if not incumbent or not candidate:
            continue
        if not incumbent.get("exact") and candidate.get("exact"):
            transitions["fixed_by_candidate"] += 1
        elif incumbent.get("exact") and not candidate.get("exact"):
            transitions["regressed_by_candidate"] += 1
        elif incumbent.get("action") != candidate.get("action"):
            transitions["changed_wrong_answer"] += 1
        else:
            transitions["same_outcome"] += 1
    return {
        "arms": arms,
        "transitions_qwen27b_patch_vs_incumbent": dict(transitions),
    }


def make_trm_rows(rows: list[dict[str, Any]], patches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_row: dict[str, dict[str, Any]] = defaultdict(dict)
    for row in rows:
        by_row[str(row.get("row_id"))][str(row.get("arm"))] = row
    patch_by_arm = {
        "current_skill": "incumbent_current_skill",
        "metta_self_improved": "qwen27b_auditor_patch",
        "baseline": "raw_baseline_no_skill",
    }
    known_patches = {patch["patch_id"] for patch in patches}
    out: list[dict[str, Any]] = []
    for row_id, group in sorted(by_row.items()):
        incumbent = group.get("current_skill")
        for arm, row in sorted(group.items()):
            patch_id = patch_by_arm.get(arm, arm)
            if patch_id not in known_patches and arm != "baseline":
                continue
            label = "reject_patch"
            reason = "not_better_than_incumbent"
            if arm == "current_skill":
                label = "incumbent"
                reason = "baseline_for_patch_search"
            elif row.get("exact") and not (incumbent or {}).get("exact"):
                label = "commit_patch"
                reason = "fixes_incumbent_miss"
            elif (incumbent or {}).get("exact") and not row.get("exact"):
                reason = "regresses_incumbent_hit"
            elif row.get("action") == (incumbent or {}).get("action"):
                reason = "same_as_incumbent"
            out.append(
                {
                    "row_id": row_id,
                    "env_family": "intellect3_math_skill_patch_gym",
                    "patch_id": patch_id,
                    "arm": arm,
                    "state": {
                        "candidate_action": row.get("action"),
                        "incumbent_action": (incumbent or {}).get("action"),
                        "candidate_exact": bool(row.get("exact")),
                        "incumbent_exact": bool((incumbent or {}).get("exact")),
                    },
                    "label": label,
                    "reason": reason,
                    "target": {
                        "adoption_action": "commit" if label == "commit_patch" else "reject_or_keep_incumbent",
                    },
                }
            )
    return out


def build_payload(source_dir: Path) -> dict[str, Any]:
    patches = patch_bank(source_dir)
    rows = load_jsonl(source_dir / "intellect3_math_metta_self_improve.rows.jsonl")
    observed = summarize_observed(rows)
    trm_rows = make_trm_rows(rows, patches)
    incumbent = observed["arms"].get("current_skill", {})
    qwen_patch = observed["arms"].get("metta_self_improved", {})
    gate = {
        "incumbent_patch_id": "incumbent_current_skill",
        "observed_candidate_patch_id": "qwen27b_auditor_patch",
        "decision": "reject_patch_keep_current_skill",
        "incumbent_exact": incumbent.get("exact", 0),
        "candidate_exact": qwen_patch.get("exact", 0),
        "rule": "adopt only if candidate held-out exact exceeds incumbent and fixed_by_candidate >= regressed_by_candidate",
    }
    return {
        "generated_at_utc": utc_now(),
        "source_dir": str(source_dir),
        "patch_bank": patches,
        "observed": observed,
        "adoption_gate": gate,
        "trm_rows": trm_rows,
        "next_run": {
            "recommended_holdout_rows": 20,
            "recommended_patches": [
                "codex_domain_router_v1",
                "codex_answer_shape_verifier_v1",
                "codex_slow_path_trigger_v1",
                "codex_patch_commit_controller_v1",
            ],
            "execution": "evaluate each patch independently; checkpoint each row-arm result; promote only Pareto-improving patches",
            "resource_note": "snacksack 27B server reset during an uncapped 20-row expansion; keep live batches small and resumable.",
        },
    }


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Intellect-3-Math Skill-Patch Gym",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        f"Source smoke: `{payload['source_dir']}`",
        "",
        "## Why This Gym",
        "",
        "The 27B model can draft plausible MeTTa rules, but a single unverified prompt mutation underperformed the incumbent. The gym turns that into a search/control problem: generate patches, evaluate on held-out rows, train commit/veto TRMs, and only promote verified patches.",
        "",
        "## Observed Seed Result",
        "",
        "| Arm | Exact | Exact Rate | Common Actions |",
        "| --- | ---: | ---: | --- |",
    ]
    for arm, metrics in payload["observed"]["arms"].items():
        actions = ", ".join(f"{key}:{value}" for key, value in metrics["common_actions"].items())
        lines.append(f"| `{arm}` | {metrics['exact']}/{metrics['rows']} | {metrics['exact_rate']:.4f} | {actions or '-'} |")
    lines.extend(
        [
            "",
            "## Patch Bank",
            "",
            "| Patch | Source | Status | Intended Failure Modes |",
            "| --- | --- | --- | --- |",
        ]
    )
    for patch in payload["patch_bank"]:
        modes = ", ".join(patch.get("intended_failure_modes") or [])
        lines.append(f"| `{patch['patch_id']}` | `{patch['source']}` | `{patch['status']}` | {modes or '-'} |")
    lines.extend(
        [
            "",
            "## Adoption Gate",
            "",
            json.dumps(payload["adoption_gate"], indent=2),
            "",
            "## TRM Export",
            "",
            f"- Rows: `{len(payload['trm_rows'])}`",
            "- Labels: `commit_patch`, `reject_patch`, `incumbent`",
            "- Target: train a patch commit/veto controller, not a math solver.",
            "",
            "## Next Run",
            "",
            json.dumps(payload["next_run"], indent=2),
        ]
    )
    return "\n".join(lines) + "\n"


def render_metta(payload: dict[str, Any]) -> str:
    lines = [
        ";; Intellect-3-Math skill-patch gym contract.",
        "(= env_id intellect3_math_skill_patch_gym)",
        "(= incumbent_patch incumbent_current_skill)",
        "(= (adopt_patch $patch)",
        "   (and (> (heldout_exact $patch) (heldout_exact incumbent_current_skill))",
        "        (>= (fixes $patch) (regressions $patch))))",
        "(= (reject_patch $patch)",
        "   (or (<= (heldout_exact $patch) (heldout_exact incumbent_current_skill))",
        "       (> (regressions $patch) (fixes $patch))))",
    ]
    for patch in payload["patch_bank"]:
        lines.append(f"(= (patch_status {patch['patch_id']}) {patch['status']})")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(args.source_dir)
    (args.out_dir / "intellect3_math_skill_patch_gym.results.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8", newline="\n"
    )
    (args.out_dir / "intellect3_math_skill_patch_gym.results.md").write_text(
        render_md(payload), encoding="utf-8", newline="\n"
    )
    (args.out_dir / "intellect3_math_skill_patch_gym_contract.metta").write_text(
        render_metta(payload), encoding="utf-8", newline="\n"
    )
    (args.out_dir / "patch_bank.json").write_text(
        json.dumps(payload["patch_bank"], indent=2), encoding="utf-8", newline="\n"
    )
    with (args.out_dir / "patch_commit_trm_rows.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in payload["trm_rows"]:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    print(args.out_dir / "intellect3_math_skill_patch_gym.results.md")
    print(json.dumps(payload["adoption_gate"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
