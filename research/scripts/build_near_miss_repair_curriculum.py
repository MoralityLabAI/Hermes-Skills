"""Build a near-miss repair curriculum from local MeTTa/TRM artifacts.

The curriculum is intentionally role-aware.  It collects semi-failed outputs
that can teach repair, verifier, routing, and commit/veto TRMs.  It does not
pretend these rows are raw reasoning successes.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
ARTIFACT_ROOT = ROOT / "research" / "studies" / "2026-04-22-metta-trm-hermes-pipeline" / "artifacts"
OUT_DIR = ROOT / "research" / "generated" / "near_miss_repair_curriculum"

SCALE_PROBE = ARTIFACT_ROOT / "scale_transfer_probe_suite_qwen25_3b_q4km" / "scale_transfer_probe.results.json"
SYMBOLIC_THRESHOLD = ARTIFACT_ROOT / "symbolic_closure_threshold_suite" / "symbolic_closure_threshold.results.json"
LOGIC_FLOW_ROWS = ARTIFACT_ROOT / "intellect3_logic_flow_policy_sweep" / "intellect3_logic_flow_policy_sweep.rows.jsonl"
LOGIC_FLOW_TRM = ARTIFACT_ROOT / "intellect3_logic_flow_policy_sweep" / "pure_trm_flow_policy_rows.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def role_for_env(env_family: str) -> str:
    env = env_family.lower()
    if any(token in env for token in ("tool", "schema", "pydantic")):
        return "structured_map"
    if any(token in env for token in ("choice", "ifeval", "boolq", "hashtag", "bullet")):
        return "choice_contract"
    if any(token in env for token in ("tree", "ascii")):
        return "structured_map"
    if any(token in env for token in ("logic", "camp")):
        return "hard_reasoning_logic"
    if any(token in env for token in ("math", "aime")):
        return "hard_reasoning_numeric"
    if any(token in env for token in ("safety", "abstain")):
        return "abstain_guard"
    if any(token in env for token in ("psycho", "profile")):
        return "structured_map"
    return "unknown"


def curriculum_bucket(*, before: float, after: float, arm: str, note: str = "") -> str:
    if after >= 1.0 and before < 1.0:
        return "repair_success"
    if after > before and after < 1.0:
        return "partial_repair_improvement"
    if before >= 1.0:
        return "exact_positive"
    if "abstain" in arm and after <= 0.0:
        return "unrecoverable_or_abstain"
    if after <= before:
        return "repair_failure_or_no_gain"
    return "near_miss"


def make_row(
    *,
    source: str,
    env_family: str,
    case_id: str,
    role: str,
    before_arm: str,
    after_arm: str,
    before_reward: float,
    after_reward: float,
    failure_label: str,
    repair_action: str,
    candidate_excerpt: str,
    repaired_excerpt: str,
    evidence_class: str,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    bucket = curriculum_bucket(before=before_reward, after=after_reward, arm=after_arm, note=failure_label)
    return {
        "source": source,
        "env_family": env_family,
        "case_id": case_id,
        "trm_role": role,
        "bucket": bucket,
        "before_arm": before_arm,
        "after_arm": after_arm,
        "before_reward": round(float(before_reward), 6),
        "after_reward": round(float(after_reward), 6),
        "delta": round(float(after_reward) - float(before_reward), 6),
        "failure_label": failure_label,
        "repair_action": repair_action,
        "candidate_excerpt": candidate_excerpt[:240],
        "repaired_excerpt": repaired_excerpt[:240],
        "evidence_class": evidence_class,
        "meta": meta or {},
    }


def rows_from_scale_probe() -> list[dict[str, Any]]:
    if not SCALE_PROBE.exists():
        return []
    payload = load_json(SCALE_PROBE)
    grouped: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in payload.get("rows", []):
        grouped[(row["env_family"], row["case_id"])][row["arm_id"]] = row
    rows: list[dict[str, Any]] = []
    for (env, case), arms in grouped.items():
        raw = arms.get("without_metta")
        runtime = arms.get("with_metta_runtime")
        repair = arms.get("with_metta_runtime_repair")
        if raw and repair:
            rows.append(
                make_row(
                    source="scale_transfer_probe_suite_qwen25_3b_q4km",
                    env_family=env,
                    case_id=case,
                    role=role_for_env(env),
                    before_arm="without_metta",
                    after_arm="with_metta_runtime_repair",
                    before_reward=float(raw.get("reward", 0.0)),
                    after_reward=float(repair.get("reward", 0.0)),
                    failure_label=str(raw.get("judge_note", "")),
                    repair_action=str((repair.get("repair_report") or {}).get("applied_repairs") or "canonical_commit"),
                    candidate_excerpt=str(raw.get("action", "")),
                    repaired_excerpt=str(repair.get("action", "")),
                    evidence_class="live_model_local_3b_plus_deterministic_repair",
                    meta={"runtime_reward": float((runtime or {}).get("reward", 0.0))},
                )
            )
    return rows


def rows_from_symbolic_threshold() -> list[dict[str, Any]]:
    if not SYMBOLIC_THRESHOLD.exists():
        return []
    payload = load_json(SYMBOLIC_THRESHOLD)
    grouped: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in payload.get("rows", []):
        grouped[(row["env_family"], row["case_id"], row["proposal_tier"])][row["arm_id"]] = row
    rows: list[dict[str, Any]] = []
    for (env, case, tier), arms in grouped.items():
        direct = arms.get("llm_direct")
        circuit = arms.get("metta_trm_circuit")
        if not direct or not circuit:
            continue
        rows.append(
            make_row(
                source="symbolic_closure_threshold_suite",
                env_family=env,
                case_id=f"{case}:{tier}",
                role=role_for_env(env),
                before_arm="llm_direct",
                after_arm="metta_trm_circuit",
                before_reward=float(direct.get("reward", 0.0)),
                after_reward=float(circuit.get("reward", 0.0)),
                failure_label=str(direct.get("judge_note", "")),
                repair_action=str((circuit.get("gate_report") or {}).get("gate") or "metta_gate"),
                candidate_excerpt=str(direct.get("action", "")),
                repaired_excerpt=str(circuit.get("action", "")),
                evidence_class="control_plane_threshold_eval",
                meta={"proposal_tier": tier, "scale_class": direct.get("scale_class")},
            )
        )
    return rows


def rows_from_logic_flow() -> list[dict[str, Any]]:
    if not LOGIC_FLOW_ROWS.exists():
        return []
    rows = load_jsonl(LOGIC_FLOW_ROWS)
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        grouped[row["row_id"]][row["policy"]] = row
    curriculum: list[dict[str, Any]] = []
    for row_id, policies in grouped.items():
        original = policies.get("logic_trm_original")
        if original is None:
            continue
        for policy in ("logic_trm_c_repair_if_c_fail", "logic_trm_dual_repair_if_any_sig_fail"):
            repaired = policies.get(policy)
            if repaired is None:
                continue
            before = float(original.get("cell_accuracy", 0.0))
            after = float(repaired.get("cell_accuracy", 0.0))
            before_reward = 1.0 if original.get("exact") else before
            after_reward = 1.0 if repaired.get("exact") else after
            curriculum.append(
                make_row(
                    source="intellect3_logic_flow_policy_sweep",
                    env_family="intellect3_logic",
                    case_id=f"{row_id}:{policy}",
                    role="hard_reasoning_logic",
                    before_arm="logic_trm_original",
                    after_arm=policy,
                    before_reward=before_reward,
                    after_reward=after_reward,
                    failure_label=logic_failure_label(original),
                    repair_action=str(repaired.get("transform")),
                    candidate_excerpt=f"arm={original.get('source_arm')} transform=original",
                    repaired_excerpt=f"arm={repaired.get('source_arm')} transform={repaired.get('transform')}",
                    evidence_class="post_hoc_projection",
                    meta={
                        "row_id": row_id,
                        "policy": policy,
                        "edit_distance": repaired.get("edit_distance"),
                        "before_exact": bool(original.get("exact")),
                        "after_exact": bool(repaired.get("exact")),
                    },
                )
            )
    return curriculum


def logic_failure_label(row: dict[str, Any]) -> str:
    if not row.get("selected"):
        return "abstain_no_candidate"
    if row.get("exact"):
        return "exact_positive"
    if not row.get("c_signature_pass"):
        return "c_signature_fail"
    if not row.get("t_signature_pass"):
        return "t_signature_fail"
    return "signature_pass_cell_fail"


def commit_target(row: dict[str, Any]) -> str:
    bucket = str(row["bucket"])
    if bucket in {"repair_success", "partial_repair_improvement", "exact_positive"}:
        return "commit"
    if float(row["after_reward"]) > float(row["before_reward"]):
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
        },
    }


def supervision_weight(row: dict[str, Any]) -> float:
    if row["bucket"] == "repair_success":
        return 2.5
    if row["bucket"] == "partial_repair_improvement":
        return 1.5
    if row["bucket"] == "exact_positive":
        return 2.0
    if row["bucket"] == "repair_failure_or_no_gain":
        return 0.75
    return 1.0


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_role = Counter(row["trm_role"] for row in rows)
    by_bucket = Counter(row["bucket"] for row in rows)
    by_source = Counter(row["source"] for row in rows)
    role_bucket: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        role_bucket[row["trm_role"]][row["bucket"]] += 1
    return {
        "generated_at_utc": utc_now(),
        "row_count": len(rows),
        "by_role": dict(by_role),
        "by_bucket": dict(by_bucket),
        "by_source": dict(by_source),
        "role_bucket": {role: dict(counts) for role, counts in sorted(role_bucket.items())},
        "avg_positive_delta": round(
            sum(max(0.0, float(row["delta"])) for row in rows) / max(1, len(rows)),
            6,
        ),
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def render_md(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Near-Miss Repair Curriculum",
        "",
        f"Generated: `{summary['generated_at_utc']}`",
        "",
        "This curriculum collects semi-failed outputs where MeTTa/TRM repair, verifier, or commit gates can learn useful control behavior. It is a curation artifact, not a model-training result.",
        "",
        "## Summary",
        "",
        f"- Rows: `{summary['row_count']}`",
        f"- Average positive delta per row: `{summary['avg_positive_delta']:.4f}`",
        "",
        "## Buckets",
        "",
        "| Bucket | Rows |",
        "| --- | ---: |",
    ]
    for bucket, count in sorted(summary["by_bucket"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{bucket}` | {count} |")
    lines.extend(["", "## Roles", "", "| TRM role | Rows | Bucket mix |", "| --- | ---: | --- |"])
    for role, count in sorted(summary["by_role"].items(), key=lambda item: (-item[1], item[0])):
        mix = ", ".join(f"`{bucket}`:{value}" for bucket, value in sorted(summary["role_bucket"][role].items()))
        lines.append(f"| `{role}` | {count} | {mix} |")
    lines.extend(["", "## Sources", "", "| Source | Rows |", "| --- | ---: |"])
    for source, count in sorted(summary["by_source"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{source}` | {count} |")
    lines.extend(
        [
            "",
            "## High-Value Rows",
            "",
            "| Source | Role | Case | Bucket | Before | After | Delta | Failure | Repair |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    high_value = sorted(rows, key=lambda row: (-float(row["delta"]), row["source"], row["case_id"]))[:60]
    for row in high_value:
        lines.append(
            f"| `{row['source']}` | `{row['trm_role']}` | `{row['case_id']}` | `{row['bucket']}` | "
            f"{row['before_reward']:.4f} | {row['after_reward']:.4f} | {row['delta']:.4f} | "
            f"`{row['failure_label']}` | `{row['repair_action']}` |"
        )
    lines.extend(
        [
            "",
            "## Methodology Use",
            "",
            "- Train repair/verifier TRMs on `repair_success` and `partial_repair_improvement` rows.",
            "- Keep `repair_failure_or_no_gain` rows as hard negatives for commit/veto TRMs.",
            "- Do not merge `hard_reasoning_numeric` rows into solver training unless teacher candidates or invariants exist.",
            "- Evaluate by held-out failure family, not just held-out examples.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = rows_from_scale_probe() + rows_from_symbolic_threshold() + rows_from_logic_flow()
    rows = sorted(rows, key=lambda row: (row["source"], row["trm_role"], row["case_id"], row["after_arm"]))
    pure_rows = [pure_trm_row(row) for row in rows]
    summary = summarize(rows)
    curriculum_path = OUT_DIR / "near_miss_repair_curriculum.jsonl"
    pure_path = OUT_DIR / "near_miss_repair_pure_trm_rows.jsonl"
    summary_path = OUT_DIR / "near_miss_repair_curriculum.summary.json"
    md_path = OUT_DIR / "near_miss_repair_curriculum.md"
    write_jsonl(curriculum_path, rows)
    write_jsonl(pure_path, pure_rows)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    md_path.write_text(render_md(summary, rows), encoding="utf-8")
    print(md_path)
    print(curriculum_path)
    print(pure_path)
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
