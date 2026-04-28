"""Build a multi-env methodology-lift matrix for MeTTa-scaffolded TRM targets.

This is a deterministic artifact builder. It makes no model calls and trains no
neural model. The goal is to show whether the C-signature lesson generalizes:
pre-repair scalar hints are brittle, env-specific symbolic checks are useful but
sometimes incomplete, and post-repair multi-signal state defines cleaner
commit/veto supervision for TRM infusion.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
ARTIFACT_ROOT = ROOT / "research" / "studies" / "2026-04-22-metta-trm-hermes-pipeline" / "artifacts"
OUT_DIR = ARTIFACT_ROOT / "metta_trm_methodology_lift_matrix"

C_SIGNATURE_ROWS = ROOT / "research" / "generated" / "c_signature_commit_trm_pack" / "c_signature_commit_trm_rows.jsonl"
SCALE_PROBE_JSON = ARTIFACT_ROOT / "scale_transfer_probe_suite_qwen25_3b_q4km" / "scale_transfer_probe.results.json"
SYMBOLIC_THRESHOLD_JSON = ARTIFACT_ROOT / "symbolic_closure_threshold_suite" / "symbolic_closure_threshold.results.json"


POLICY_ORDER = [
    "naive_commit_all",
    "pre_reward_ge_0p8",
    "post_symbolic_adapter",
    "post_exact_only",
    "post_multi_signal",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def exact_from_reward(reward: float, note: str = "") -> bool:
    exact_notes = {
        "exact",
        "exact_grid",
        "exact_json",
        "exact_tree",
        "four_hashtags",
        "two_bullets_five_words",
    }
    return reward >= 1.0 or note in exact_notes


def target_action(before_reward: float, after_reward: float, after_exact: bool) -> str:
    return "commit" if after_exact or after_reward > before_reward else "reject_or_abstain"


def target_bucket(before_reward: float, after_reward: float, before_exact: bool, after_exact: bool) -> str:
    if before_exact and after_exact:
        return "exact_positive"
    if after_exact and not before_exact:
        return "repair_success"
    if after_reward > before_reward:
        return "partial_repair_improvement"
    return "repair_failure_or_no_gain"


def row_read(env_family: str) -> str:
    reads = {
        "intellect3_logic_c_signature": "Post-repair reward delta is required; repaired signatures alone still false-commit no-gain repairs.",
        "tool_contract_router": "Intent/schema atoms make tool-call repair separable once a partial semantic proposal exists.",
        "choice_contract": "A recoverable label is enough for symbolic extraction; absent labels should be rejected.",
        "ascii_tree_deep": "Node completeness is the symbolic hinge; exact formatting can be circuit-owned after nodes are present.",
        "intellect3_camp_gate": "Signature projection helps once a plausible grid exposes enough row/column structure.",
        "math_answer_search": "Negative control: without an exact candidate or solver, symbolic gates cannot invent the answer.",
        "pydantic_hard_schema": "Schema and field validation are highly separable once canonical repair or exact runtime state is available.",
        "ifeval_contract_subset": "Literal-count contracts are separable after canonical repair, but raw prompt hints are weak.",
        "safety_abstain_router": "Route labels become separable when the decision/reason/safe-step schema is explicit.",
    }
    return reads.get(env_family, "No env-specific read registered.")


def make_methodology_row(
    *,
    source: str,
    env_family: str,
    case_id: str,
    split: str,
    proposal_tier: str,
    before_reward: float,
    after_reward: float,
    before_note: str,
    after_note: str,
    symbolic_pass: bool,
    symbolic_label: str,
    meta: dict[str, Any],
) -> dict[str, Any]:
    before_reward = float(before_reward)
    after_reward = float(after_reward)
    before_exact = exact_from_reward(before_reward, before_note)
    after_exact = exact_from_reward(after_reward, after_note)
    target = target_action(before_reward, after_reward, after_exact)
    return {
        "source": source,
        "env_family": env_family,
        "case_id": case_id,
        "split": split,
        "proposal_tier": proposal_tier,
        "before_reward": round(before_reward, 6),
        "after_reward": round(after_reward, 6),
        "reward_delta": round(after_reward - before_reward, 6),
        "before_exact": before_exact,
        "after_exact": after_exact,
        "before_note": before_note,
        "after_note": after_note,
        "symbolic_pass": bool(symbolic_pass),
        "symbolic_label": symbolic_label,
        "target_action": target,
        "target_bucket": target_bucket(before_reward, after_reward, before_exact, after_exact),
        "read": row_read(env_family),
        "meta": meta,
    }


def symbolic_from_threshold(env_family: str, gate_report: dict[str, Any]) -> tuple[bool, str]:
    if env_family == "tool_contract_router":
        source = str(gate_report.get("source") or "")
        return source not in {"", "insufficient_intent_atoms"}, source or "no_source"
    if env_family == "choice_contract":
        source = str(gate_report.get("source") or "")
        return source not in {"", "no_allowed_label"}, source or "no_allowed_label"
    if env_family == "ascii_tree_deep":
        missing = gate_report.get("missing")
        return isinstance(missing, list) and len(missing) == 0, f"missing={len(missing) if isinstance(missing, list) else 'unknown'}"
    if env_family == "intellect3_camp_gate":
        row_c_counts = gate_report.get("row_c_counts")
        return isinstance(row_c_counts, list), "row_c_counts=matched" if isinstance(row_c_counts, list) else "row_c_counts=unmatched"
    if env_family == "math_answer_search":
        source_note = str(gate_report.get("source_note") or "")
        return source_note == "exact", source_note or "no_exact_candidate"
    return False, "unsupported_threshold_adapter"


def symbolic_from_scale(env_family: str, repair_report: dict[str, Any], after_note: str) -> tuple[bool, str]:
    status = str(repair_report.get("status") or "")
    applied = repair_report.get("applied_repairs") or []
    if status in {"already_valid", "repaired_from_metta_contract"}:
        return True, status if not applied else f"{status}:{','.join(map(str, applied))}"
    return exact_from_reward(1.0 if after_note.startswith("exact") else 0.0, after_note), after_note or status or "unsupported_scale_adapter"


def rows_from_c_signature() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in load_jsonl(C_SIGNATURE_ROWS):
        state = row.get("state") or {}
        after_t = bool(state.get("after_t_signature_pass"))
        after_c = bool(state.get("after_c_signature_pass"))
        rows.append(
            make_methodology_row(
                source="c_signature_commit_trm_pack",
                env_family="intellect3_logic_c_signature",
                case_id=str(row.get("case_id")),
                split=str(row.get("split") or ""),
                proposal_tier="post_repair_projection",
                before_reward=float(state.get("before_reward") or 0.0),
                after_reward=float(state.get("after_reward") or 0.0),
                before_note=str(state.get("failure_label") or ""),
                after_note="exact" if state.get("after_exact") else "signature_complete" if after_t and after_c else "signature_incomplete",
                symbolic_pass=after_t and after_c,
                symbolic_label="signature_complete" if after_t and after_c else "signature_incomplete",
                meta={
                    "repair_action": state.get("repair_action"),
                    "edit_distance": state.get("edit_distance"),
                    "target_bucket": row.get("target_bucket"),
                },
            )
        )
    return rows


def rows_from_symbolic_threshold() -> list[dict[str, Any]]:
    if not SYMBOLIC_THRESHOLD_JSON.exists():
        return []
    payload = load_json(SYMBOLIC_THRESHOLD_JSON)
    grouped: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in payload.get("rows", []):
        grouped[(row["env_family"], row["case_id"], row["proposal_tier"])][row["arm_id"]] = row
    rows: list[dict[str, Any]] = []
    for (env_family, case_id, tier), arms in grouped.items():
        before = arms.get("llm_direct")
        after = arms.get("metta_trm_circuit")
        if not before or not after:
            continue
        symbolic_pass, symbolic_label = symbolic_from_threshold(env_family, after.get("gate_report") or {})
        rows.append(
            make_methodology_row(
                source="symbolic_closure_threshold_suite",
                env_family=env_family,
                case_id=case_id,
                split="proposal_tier",
                proposal_tier=tier,
                before_reward=float(before.get("reward") or 0.0),
                after_reward=float(after.get("reward") or 0.0),
                before_note=str(before.get("judge_note") or ""),
                after_note=str(after.get("judge_note") or ""),
                symbolic_pass=symbolic_pass,
                symbolic_label=symbolic_label,
                meta={"scale_class": before.get("scale_class"), "gate_report": after.get("gate_report") or {}},
            )
        )
    return rows


def rows_from_scale_probe() -> list[dict[str, Any]]:
    if not SCALE_PROBE_JSON.exists():
        return []
    payload = load_json(SCALE_PROBE_JSON)
    grouped: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in payload.get("rows", []):
        grouped[(row["env_family"], row["case_id"])][row["arm_id"]] = row
    rows: list[dict[str, Any]] = []
    for (env_family, case_id), arms in grouped.items():
        before = arms.get("without_metta")
        after = arms.get("with_metta_runtime_repair")
        if not before or not after:
            continue
        repair_report = after.get("repair_report") or {}
        symbolic_pass, symbolic_label = symbolic_from_scale(env_family, repair_report, str(after.get("judge_note") or ""))
        rows.append(
            make_methodology_row(
                source="scale_transfer_probe_suite_qwen25_3b_q4km",
                env_family=env_family,
                case_id=case_id,
                split="local_3b_probe",
                proposal_tier="runtime_repair",
                before_reward=float(before.get("reward") or 0.0),
                after_reward=float(after.get("reward") or 0.0),
                before_note=str(before.get("judge_note") or ""),
                after_note=str(after.get("judge_note") or ""),
                symbolic_pass=symbolic_pass,
                symbolic_label=symbolic_label,
                meta={"repair_report": repair_report},
            )
        )
    return rows


def load_methodology_rows() -> list[dict[str, Any]]:
    rows = rows_from_c_signature() + rows_from_symbolic_threshold() + rows_from_scale_probe()
    rows.sort(key=lambda row: (row["env_family"], row["source"], row["case_id"], row["proposal_tier"]))
    return rows


def policy_naive_commit_all(row: dict[str, Any]) -> str:
    return "commit"


def policy_pre_reward_ge_0p8(row: dict[str, Any]) -> str:
    return "commit" if float(row["before_reward"]) >= 0.8 or bool(row["before_exact"]) else "reject_or_abstain"


def policy_post_symbolic_adapter(row: dict[str, Any]) -> str:
    return "commit" if bool(row.get("symbolic_pass")) else "reject_or_abstain"


def policy_post_exact_only(row: dict[str, Any]) -> str:
    return "commit" if bool(row.get("after_exact")) else "reject_or_abstain"


def policy_post_multi_signal(row: dict[str, Any]) -> str:
    return "commit" if bool(row.get("after_exact")) or float(row.get("reward_delta") or 0.0) > 0.0 else "reject_or_abstain"


POLICIES: dict[str, Callable[[dict[str, Any]], str]] = {
    "naive_commit_all": policy_naive_commit_all,
    "pre_reward_ge_0p8": policy_pre_reward_ge_0p8,
    "post_symbolic_adapter": policy_post_symbolic_adapter,
    "post_exact_only": policy_post_exact_only,
    "post_multi_signal": policy_post_multi_signal,
}


def evaluate(rows: list[dict[str, Any]], policy_id: str, predict: Callable[[dict[str, Any]], str]) -> dict[str, Any]:
    counts = Counter(row["target_action"] for row in rows)
    correct = 0
    false_commit = 0
    false_reject = 0
    expected_delta = 0.0
    committed = 0
    for row in rows:
        pred = predict(row)
        target = row["target_action"]
        correct += int(pred == target)
        if pred == "commit":
            committed += 1
            expected_delta += float(row.get("reward_delta") or 0.0)
        if target == "reject_or_abstain" and pred == "commit":
            false_commit += 1
        if target == "commit" and pred == "reject_or_abstain":
            false_reject += 1
    return {
        "policy_id": policy_id,
        "n": len(rows),
        "accuracy": round(correct / max(1, len(rows)), 4),
        "false_commit_rate": round(false_commit / max(1, counts.get("reject_or_abstain", 0)), 4),
        "false_reject_rate": round(false_reject / max(1, counts.get("commit", 0)), 4),
        "false_commit_count": false_commit,
        "false_reject_count": false_reject,
        "committed": committed,
        "expected_delta_if_committed": round(expected_delta, 6),
        "target_counts": dict(counts),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_env: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_env[row["env_family"]].append(row)

    policy_summary = {
        policy_id: evaluate(rows, policy_id, predict)
        for policy_id, predict in POLICIES.items()
    }

    env_summary: dict[str, Any] = {}
    for env_family, env_rows in sorted(by_env.items()):
        env_policies = {
            policy_id: evaluate(env_rows, policy_id, predict)
            for policy_id, predict in POLICIES.items()
        }
        avg_before_reward = sum(float(row["before_reward"]) for row in env_rows) / max(1, len(env_rows))
        avg_after_reward = sum(float(row["after_reward"]) for row in env_rows) / max(1, len(env_rows))
        before_exact_count = sum(1 for row in env_rows if row["before_exact"])
        after_exact_count = sum(1 for row in env_rows if row["after_exact"])
        pre = env_policies["pre_reward_ge_0p8"]
        multi = env_policies["post_multi_signal"]
        symbolic = env_policies["post_symbolic_adapter"]
        env_summary[env_family] = {
            "n": len(env_rows),
            "target_counts": dict(Counter(row["target_action"] for row in env_rows)),
            "target_buckets": dict(Counter(row["target_bucket"] for row in env_rows)),
            "avg_before_reward": round(avg_before_reward, 6),
            "avg_after_reward": round(avg_after_reward, 6),
            "avg_reward_lift": round(avg_after_reward - avg_before_reward, 6),
            "before_exact_count": before_exact_count,
            "after_exact_count": after_exact_count,
            "exact_count_lift": after_exact_count - before_exact_count,
            "policies": env_policies,
            "accuracy_lift_vs_pre_scalar": round(multi["accuracy"] - pre["accuracy"], 4),
            "false_commit_reduction_vs_pre_scalar": round(pre["false_commit_rate"] - multi["false_commit_rate"], 4),
            "symbolic_gap_to_multi_signal": round(multi["accuracy"] - symbolic["accuracy"], 4),
            "read": row_read(env_family),
        }

    return {
        "generated_at_utc": utc_now(),
        "suite_type": "deterministic_metta_trm_methodology_lift_matrix",
        "row_count": len(rows),
        "source_counts": dict(Counter(row["source"] for row in rows)),
        "env_counts": {env: len(env_rows) for env, env_rows in sorted(by_env.items())},
        "policy_summary": policy_summary,
        "env_summary": env_summary,
        "resource_profile": {
            "model_calls": 0,
            "training_runs": 0,
            "ram_cap_policy": "deterministic Python-only artifact generation; no model subprocess",
            "hrm_trainer_caps_for_future_training": {"ram_mb": 2048, "cpu_pct": 50, "io_mb_s": 50},
        },
        "claim_boundary": "Post-multi-signal rows define verifier/commit TRM targets and separability ceilings, not trained TRM-weight performance.",
    }


def render_contracts() -> str:
    return "\n".join(
        [
            "; Multi-env MeTTa/TRM methodology-lift contract sketch.",
            "; These rules define commit/veto training targets from post-repair state.",
            "",
            "(= (positive-repair-delta $state)",
            "   (> (reward-delta $state) 0.0))",
            "",
            "(= (post-multi-signal-commit $state)",
            "   (if (or (after-exact $state) (positive-repair-delta $state))",
            "       commit",
            "       reject_or_abstain))",
            "",
            "(= (post-symbolic-commit $state)",
            "   (if (env-symbolic-pass $state)",
            "       commit",
            "       reject_or_abstain))",
            "",
            "(= (env-symbolic-pass $state)",
            "   (match (env-family $state)",
            "     (intellect3_logic_c_signature (and (after-t-signature-pass $state) (after-c-signature-pass $state)))",
            "     (tool_contract_router (has-valid-tool-and-required-arguments $state))",
            "     (choice_contract (has-allowed-choice-label $state))",
            "     (ascii_tree_deep (node-set-complete $state))",
            "     (intellect3_camp_gate (signature-projection-matched $state))",
            "     (math_answer_search (exact-candidate-present $state))",
            "     (_ False)))",
            "",
        ]
    )


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# MeTTa/TRM Methodology Lift Matrix",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "This deterministic matrix generalizes the C-signature finding across multiple Hermes/Prime-style envs. It compares naive commit behavior, pre-repair scalar hints, env-specific symbolic checks, exact-only verification, and post-repair multi-signal commit targets.",
        "",
        "No model calls and no TRM training were run for this artifact.",
        "",
        "## Overall Policy Summary",
        "",
        "| Policy | Rows | Accuracy | False commit rate | False reject rate | Expected committed delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for policy_id in POLICY_ORDER:
        summary = payload["policy_summary"][policy_id]
        lines.append(
            f"| `{policy_id}` | {summary['n']} | {summary['accuracy']:.4f} | {summary['false_commit_rate']:.4f} | "
            f"{summary['false_reject_rate']:.4f} | {summary['expected_delta_if_committed']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Env-Level Methodology Lift",
            "",
            "| Env | Rows | Avg reward lift | Exact lift | Targets | Pre-scalar acc | Symbolic acc | Multi-signal acc | FC reduction vs pre | Symbolic gap | Read |",
            "| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for env_family, summary in payload["env_summary"].items():
        targets = ", ".join(f"{key}:{value}" for key, value in sorted(summary["target_counts"].items()))
        pre = summary["policies"]["pre_reward_ge_0p8"]
        symbolic = summary["policies"]["post_symbolic_adapter"]
        multi = summary["policies"]["post_multi_signal"]
        lines.append(
            f"| `{env_family}` | {summary['n']} | {summary['avg_reward_lift']:.4f} | {summary['exact_count_lift']} | "
            f"{targets} | {pre['accuracy']:.4f} | "
            f"{symbolic['accuracy']:.4f} | {multi['accuracy']:.4f} | "
            f"{summary['false_commit_reduction_vs_pre_scalar']:.4f} | {summary['symbolic_gap_to_multi_signal']:.4f} | "
            f"{summary['read']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The C-signature lesson generalizes as a methodology: make repair rows carry before/after verifier state, then train commit/veto TRMs on multi-signal post-repair targets.",
            "- Env-specific symbolic checks are valuable but not universally sufficient. C-signature repairs show the key limitation: all repaired candidates can pass signatures while no-gain repairs still need vetoing.",
            "- Exact-only commit is safe but too conservative in lanes with partial repair improvements, so it can hide useful training signal.",
            "- Math remains the negative-control boundary: without an exact candidate, solver, or richer numeric invariant, MeTTa/TRM control logic cannot invent the missing answer.",
            "- Treat `post_multi_signal` as a separability ceiling and target definition, not trained TRM performance.",
            "",
            "## MeTTa Contract Sketch",
            "",
            "```scheme",
            payload["metta_contract"].rstrip(),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    rows = load_methodology_rows()
    payload = summarize(rows)
    payload["metta_contract"] = render_contracts()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(OUT_DIR / "methodology_lift.rows.jsonl", rows)
    write_json(OUT_DIR / "methodology_lift.results.json", payload)
    (OUT_DIR / "methodology_lift.results.md").write_text(render_md(payload), encoding="utf-8", newline="\n")
    (OUT_DIR / "methodology_lift_contracts.metta").write_text(
        payload["metta_contract"], encoding="utf-8", newline="\n"
    )
    print(OUT_DIR / "methodology_lift.results.md")
    print(OUT_DIR / "methodology_lift.results.json")
    print(OUT_DIR / "methodology_lift.rows.jsonl")
    print(OUT_DIR / "methodology_lift_contracts.metta")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
