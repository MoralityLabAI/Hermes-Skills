from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX_ROOT = ROOT / "data" / "primehub_skill_trm_matrix" / "latest"
DEFAULT_ROLE_IMPRINT_JSON = DEFAULT_MATRIX_ROOT / "role_based_imprint.json"
DEFAULT_MANIFEST = ROOT / "data" / "primehub_skill_batch_evolution" / "latest.manifest.json"
ACTION_SUPPORT_TIERS = {"action_support", "format_support", "narrow_action_support"}
ACTION_ORIENTED_CLUSTERS = {"choice_contract", "structured_map", "constraint_summarize", "internal_action"}

ROLE_NAMES = {
    "hard_reasoning_numeric": "critic_verify_numeric",
    "hard_reasoning_logic": "critic_verify_logic",
    "choice_contract": "contract_formatter",
    "structured_map": "schema_formatter",
    "constraint_summarize": "constraint_summarizer",
    "internal_action": "latent_action_retriever",
    "abstain_guard": "guarded_critic",
}

DEFAULT_SIGNAL_WEIGHTS_BY_TIER = {
    "critic_verify_sparse": {
        "task_success": 1.0,
        "contract_validity": 1.15,
        "repair_success": 1.0,
        "retrieval_selection_correctness": 0.8,
        "profile_selection_correctness": 0.8,
        "critic_verdict_agreement": 1.3,
        "failure_localization": 1.15,
        "contract_family_match": 0.85,
        "transport_visible_output": 0.6,
        "transport_no_fallback": 0.6,
    },
    "critic_guard": {
        "task_success": 0.95,
        "contract_validity": 1.0,
        "repair_success": 0.9,
        "retrieval_selection_correctness": 0.65,
        "profile_selection_correctness": 0.65,
        "critic_verdict_agreement": 1.5,
        "failure_localization": 1.1,
        "contract_family_match": 0.7,
        "transport_visible_output": 0.6,
        "transport_no_fallback": 0.6,
    },
    "action_support": {
        "task_success": 1.25,
        "contract_validity": 1.35,
        "repair_success": 1.25,
        "retrieval_selection_correctness": 1.25,
        "profile_selection_correctness": 1.25,
        "critic_verdict_agreement": 1.0,
        "failure_localization": 1.0,
        "contract_family_match": 1.1,
        "transport_visible_output": 0.75,
        "transport_no_fallback": 0.75,
    },
    "format_support": {
        "task_success": 1.15,
        "contract_validity": 1.45,
        "repair_success": 1.5,
        "retrieval_selection_correctness": 1.2,
        "profile_selection_correctness": 1.35,
        "critic_verdict_agreement": 1.0,
        "failure_localization": 1.05,
        "contract_family_match": 1.2,
        "transport_visible_output": 0.8,
        "transport_no_fallback": 0.8,
    },
    "narrow_action_support": {
        "task_success": 1.4,
        "contract_validity": 1.4,
        "repair_success": 1.25,
        "retrieval_selection_correctness": 1.6,
        "profile_selection_correctness": 1.6,
        "critic_verdict_agreement": 1.0,
        "failure_localization": 1.0,
        "contract_family_match": 1.15,
        "transport_visible_output": 0.85,
        "transport_no_fallback": 0.85,
    },
}


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_cluster_profiles(manifest_path: Path) -> Dict[str, Dict[str, Any]]:
    if not manifest_path.exists():
        return {}
    payload = load_json(manifest_path)
    profiles = payload.get("cluster_profiles") or {}
    return {str(key): dict(value or {}) for key, value in profiles.items()}


def discover_cluster_ids(matrix_root: Path) -> List[str]:
    cluster_ids: List[str] = []
    if not matrix_root.exists():
        return cluster_ids
    for path in sorted(matrix_root.iterdir()):
        if not path.is_dir():
            continue
        if path.name == "remote_summaries":
            continue
        cluster_ids.append(path.name)
    return cluster_ids


def load_cluster_sources(matrix_root: Path, cluster_id: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
    merged_path = matrix_root / cluster_id / "cluster_merged.summary.json"
    remote_path = matrix_root / "remote_summaries" / f"{cluster_id}.cluster_training.summary.json"
    merged = load_json(merged_path) if merged_path.exists() else {}
    remote = load_json(remote_path) if remote_path.exists() else {}
    return merged, remote


def support_tier(exact_positive_rows: int, target_cov: float, route_abstain: float) -> str:
    if exact_positive_rows >= 2 and target_cov >= 0.75:
        return "narrow_action_support"
    if exact_positive_rows >= 10 and target_cov >= 0.25 and route_abstain <= 0.35:
        return "action_support"
    if exact_positive_rows >= 4 and target_cov >= 0.2 and route_abstain <= 0.5:
        return "format_support"
    if exact_positive_rows >= 2 and route_abstain >= 0.75:
        return "critic_guard"
    return "critic_verify_sparse"


def round_metric(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 4)


def build_skill_lines(cluster_id: str, metrics: Dict[str, Any]) -> List[str]:
    exact_positive_rows = safe_int(metrics.get("exact_positive_rows"))
    target_cov = safe_float(metrics.get("target_action_coverage"))
    critic_acc = safe_float(metrics.get("critic_bucket_accuracy"))
    retrieval_exact = safe_float(metrics.get("retriever_exact_match_rate"))
    route_abstain = safe_float(metrics.get("route_abstain_rate"))

    lines: List[str] = []
    if cluster_id == "choice_contract":
        lines.append(
            "This TRM role is strongest as a contract formatter: recover semantics first, then use support to repair wrappers, choice tokens, and exact answer shells."
        )
        if retrieval_exact <= 0.1:
            lines.append(
                "Treat retrieved support as a formatting prior, not as authority on semantics; if the solved answer conflicts with the template, keep the answer and repair only the wrapper."
            )
        return lines
    if cluster_id == "structured_map":
        lines.append(
            "This TRM role is formatter-friendly: use it to preserve strict line shape, field order, and schema compliance, then reject malformed structure before final output."
        )
        if route_abstain <= 0.1:
            lines.append(
                "When structure and semantics disagree, prioritize structurally valid output that still preserves the intended answer content."
            )
        return lines
    if cluster_id == "internal_action":
        lines.append(
            "This TRM role is a narrow latent-action specialist: when the contract implies deferred internal continuation, emit only `inspect_and_continue` and no visible draft."
        )
        lines.append(
            "Do not generalize this support into normal visible-answer tasks; it is a tiny but clean exact-token niche."
        )
        return lines
    if cluster_id == "abstain_guard":
        lines.append(
            "This TRM role is critic-first and abstention-heavy: default conservative and require explicit contract evidence before any override."
        )
        if route_abstain >= 0.75:
            lines.append(
                "Use retrieved support as a veto signal, not as permission to comply; if exact verification fails, keep the abstention path."
            )
        return lines
    if cluster_id == "hard_reasoning_numeric":
        lines.append(
            "This TRM role is a numeric verifier, not a generic solver: solve locally, then use TRM to catch arithmetic drift, sign errors, and invalid final forms."
        )
        if exact_positive_rows < 5 or target_cov < 0.2:
            lines.append(
                "Do not lean on retrieval-led derivations here; current support is too sparse, so use TRM mainly to veto contradictions or confirm the final exact value."
            )
        return lines
    if cluster_id == "hard_reasoning_logic":
        lines.append(
            "This TRM role is a branch eliminator and verifier: use it to rule out unsupported candidates and confirm the surviving answer, not to improvise a new reasoning trace."
        )
        if critic_acc >= 0.55 and retrieval_exact <= 0.1:
            lines.append(
                "Current support is critic-weighted rather than retrieval-weighted, so stay on the base reasoning path unless the candidate set is already narrow."
            )
        return lines
    lines.append("Use the current TRM role conservatively and prefer exact contract compliance over extra reasoning text.")
    return lines


def build_trainer_lines(cluster_id: str, metrics: Dict[str, Any]) -> List[str]:
    exact_positive_rows = safe_int(metrics.get("exact_positive_rows"))
    target_cov = safe_float(metrics.get("target_action_coverage"))
    route_abstain = safe_float(metrics.get("route_abstain_rate"))

    lines: List[str] = []
    if cluster_id == "choice_contract":
        lines.append("Invest additional collection into answer-wrapper and exact token repair; this is the only broad cluster with meaningful action-bearing coverage.")
        lines.append("Keep semantics-vs-format labels separate so the formatter role can improve without pretending to solve the task from scratch.")
        return lines
    if cluster_id == "structured_map":
        lines.append("Grow schema-preserving rows and malformed-output negatives together; the useful gain here is structural reliability, not open-ended reasoning.")
        return lines
    if cluster_id == "constraint_summarize":
        lines.append("Keep profile selection, exact contract validity, and deterministic repair as separate supervision channels instead of collapsing them into one reward.")
        lines.append("Treat this role as a structural family compiler: the gain comes from dense constraint labels, not broad semantic retrieval.")
        return lines
    if cluster_id == "internal_action":
        lines.append("Add more hidden-action environments before widening this role; the current signal is clean but too narrow to claim generality.")
        return lines
    if cluster_id == "abstain_guard":
        lines.append("Preserve a hard critic gate for this role; do not relax abstention defaults until the override bank grows beyond a couple of exact positives.")
        return lines
    if cluster_id in {"hard_reasoning_numeric", "hard_reasoning_logic"}:
        lines.append("Collect more exact-positive rows before treating this role as retrieval-capable; right now it is primarily a verifier/control-plane specialist.")
        if route_abstain >= 0.5 or target_cov < 0.15:
            lines.append("Keep routing conservative and prefer better row quality over more aggressive router behavior.")
        return lines
    if exact_positive_rows <= 0:
        lines.append("Do not widen routing for this role until it has exact-positive support.")
    else:
        lines.append("Continue collection and keep routing conservative until the role has broader exact-positive support.")
    return lines


def build_trainer_policy(
    cluster_id: str,
    metrics: Dict[str, Any],
    profile: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    profile = profile or {}
    exact_positive_rows = safe_int(metrics.get("exact_positive_rows"))
    target_cov = safe_float(metrics.get("target_action_coverage"))
    route_abstain = safe_float(metrics.get("route_abstain_rate"))
    tier = str(profile.get("support_tier_override") or "").strip() or support_tier(exact_positive_rows, target_cov, route_abstain)

    base_top_k = max(1, safe_int(profile.get("top_k"), 5))
    base_min_supervision = max(0.2, safe_float(profile.get("min_supervision_weight"), 0.4))
    policy: Dict[str, Any] = {
        "policy_name": f"{tier}_trainer_policy",
        "support_tier": tier,
        "routing_strength": "conservative",
        "exact_positive_weight": 1.75,
        "near_miss_weight": 1.2,
        "weak_positive_weight": 0.8,
        "negative_weight": 0.2,
        "min_supervision_weight": base_min_supervision,
        "top_k": base_top_k,
    }

    if tier == "critic_verify_sparse":
        policy.update(
            {
                "routing_strength": "conservative",
                "exact_positive_weight": 2.5,
                "near_miss_weight": 1.6,
                "weak_positive_weight": 1.0,
                "negative_weight": 0.2,
                "min_supervision_weight": max(base_min_supervision, 0.6),
                "top_k": min(base_top_k, 2),
            }
        )
    elif tier == "critic_guard":
        policy.update(
            {
                "routing_strength": "guarded",
                "exact_positive_weight": 1.4,
                "near_miss_weight": 1.1,
                "weak_positive_weight": 0.75,
                "negative_weight": 0.25,
                "min_supervision_weight": max(base_min_supervision, 0.25),
                "top_k": min(base_top_k, 3),
            }
        )
    elif tier == "action_support":
        policy.update(
            {
                "routing_strength": "moderate",
                "exact_positive_weight": 2.0,
                "near_miss_weight": 1.45,
                "weak_positive_weight": 1.15,
                "negative_weight": 0.2,
                "min_supervision_weight": max(base_min_supervision, 0.45),
                "top_k": max(base_top_k, 5),
            }
        )
    elif tier == "format_support":
        policy.update(
            {
                "routing_strength": "moderate",
                "exact_positive_weight": 2.1,
                "near_miss_weight": 1.5,
                "weak_positive_weight": 1.0,
                "negative_weight": 0.15,
                "min_supervision_weight": max(base_min_supervision, 0.35),
                "top_k": max(base_top_k, 4),
            }
        )
    elif tier == "narrow_action_support":
        policy.update(
            {
                "routing_strength": "focused",
                "exact_positive_weight": 3.0,
                "near_miss_weight": 2.0,
                "weak_positive_weight": 1.5,
                "negative_weight": 0.2,
                "min_supervision_weight": max(base_min_supervision, 0.8),
                "top_k": 1,
            }
        )

    if cluster_id in {"hard_reasoning_numeric", "hard_reasoning_logic"}:
        policy["exact_positive_weight"] = max(safe_float(policy.get("exact_positive_weight")), 2.75)
        policy["near_miss_weight"] = max(safe_float(policy.get("near_miss_weight")), 1.8)
        policy["weak_positive_weight"] = max(safe_float(policy.get("weak_positive_weight")), 1.0)
        policy["min_supervision_weight"] = max(safe_float(policy.get("min_supervision_weight")), 0.6)
        policy["top_k"] = min(safe_int(policy.get("top_k"), base_top_k), 2)
        policy["routing_strength"] = "conservative"
    elif cluster_id == "choice_contract":
        policy["exact_positive_weight"] = max(safe_float(policy.get("exact_positive_weight")), 2.25)
        policy["near_miss_weight"] = max(safe_float(policy.get("near_miss_weight")), 1.5)
        policy["weak_positive_weight"] = max(safe_float(policy.get("weak_positive_weight")), 1.25)
    elif cluster_id == "structured_map":
        policy["exact_positive_weight"] = max(safe_float(policy.get("exact_positive_weight")), 2.2)
        policy["near_miss_weight"] = max(safe_float(policy.get("near_miss_weight")), 1.75)
        policy["weak_positive_weight"] = max(safe_float(policy.get("weak_positive_weight")), 1.0)
    elif cluster_id == "internal_action":
        policy["exact_positive_weight"] = max(safe_float(policy.get("exact_positive_weight")), 3.0)
        policy["near_miss_weight"] = max(safe_float(policy.get("near_miss_weight")), 2.0)
        policy["weak_positive_weight"] = max(safe_float(policy.get("weak_positive_weight")), 1.5)
        policy["min_supervision_weight"] = max(safe_float(policy.get("min_supervision_weight")), 0.85)
        policy["top_k"] = 1
        policy["routing_strength"] = "focused"
    elif cluster_id == "abstain_guard":
        policy["exact_positive_weight"] = max(safe_float(policy.get("exact_positive_weight")), 1.5)
        policy["near_miss_weight"] = max(safe_float(policy.get("near_miss_weight")), 1.15)
        policy["negative_weight"] = max(safe_float(policy.get("negative_weight")), 0.25)
        policy["top_k"] = min(safe_int(policy.get("top_k"), base_top_k), 3)
        policy["routing_strength"] = "guarded"

    if exact_positive_rows > 0 and exact_positive_rows < 4 and target_cov < 0.15:
        policy["exact_positive_weight"] = max(safe_float(policy.get("exact_positive_weight")), 3.0)

    signal_weights = dict(DEFAULT_SIGNAL_WEIGHTS_BY_TIER.get(tier, {}))
    if cluster_id == "choice_contract":
        signal_weights.update(
            {
                "contract_validity": max(safe_float(signal_weights.get("contract_validity")), 1.45),
                "task_success": max(safe_float(signal_weights.get("task_success")), 1.3),
                "retrieval_selection_correctness": max(safe_float(signal_weights.get("retrieval_selection_correctness")), 1.2),
            }
        )
    elif cluster_id == "structured_map":
        signal_weights.update(
            {
                "contract_validity": max(safe_float(signal_weights.get("contract_validity")), 1.5),
                "repair_success": max(safe_float(signal_weights.get("repair_success")), 1.55),
                "retrieval_selection_correctness": max(safe_float(signal_weights.get("retrieval_selection_correctness")), 1.3),
                "contract_family_match": max(safe_float(signal_weights.get("contract_family_match")), 1.25),
            }
        )
    elif cluster_id == "constraint_summarize":
        signal_weights.update(
            {
                "profile_selection_correctness": 1.6,
                "contract_validity": 1.6,
                "repair_success": 1.7,
                "failure_localization": 1.2,
                "contract_family_match": 1.4,
                "task_success": 1.3,
                "critic_verdict_agreement": 1.1,
                "transport_visible_output": 0.85,
                "transport_no_fallback": 0.85,
            }
        )
    elif cluster_id == "internal_action":
        signal_weights.update(
            {
                "retrieval_selection_correctness": max(safe_float(signal_weights.get("retrieval_selection_correctness")), 1.7),
                "contract_family_match": max(safe_float(signal_weights.get("contract_family_match")), 1.2),
            }
        )
    elif cluster_id == "abstain_guard":
        signal_weights.update(
            {
                "critic_verdict_agreement": max(safe_float(signal_weights.get("critic_verdict_agreement")), 1.55),
                "failure_localization": max(safe_float(signal_weights.get("failure_localization")), 1.2),
            }
        )

    profile_signal_weights = profile.get("signal_weights") or {}
    if isinstance(profile_signal_weights, dict):
        for signal_name, raw_value in profile_signal_weights.items():
            signal_weights[str(signal_name)] = round(safe_float(raw_value, safe_float(signal_weights.get(str(signal_name)), 1.0)), 4)

    enabled_signals = list(profile.get("enabled_signals") or [])
    if not enabled_signals:
        enabled_signals = sorted(signal_name for signal_name, value in signal_weights.items() if safe_float(value) > 0.0)

    return {
        "policy_name": str(policy.get("policy_name") or ""),
        "support_tier": tier,
        "routing_strength": str(policy.get("routing_strength") or ""),
        "exact_positive_weight": round(safe_float(policy.get("exact_positive_weight")), 4),
        "near_miss_weight": round(safe_float(policy.get("near_miss_weight")), 4),
        "weak_positive_weight": round(safe_float(policy.get("weak_positive_weight")), 4),
        "negative_weight": round(safe_float(policy.get("negative_weight")), 4),
        "min_supervision_weight": round(safe_float(policy.get("min_supervision_weight")), 4),
        "top_k": max(1, safe_int(policy.get("top_k"), base_top_k)),
        "enabled_signals": enabled_signals,
        "signal_weights": {key: round(safe_float(value), 4) for key, value in sorted(signal_weights.items())},
    }


def build_cluster_card(
    cluster_id: str,
    merged_summary: Dict[str, Any],
    remote_summary: Dict[str, Any],
    profile: Dict[str, Any],
) -> Dict[str, Any]:
    bucket_counts = merged_summary.get("bucket_counts") or {}
    critic_bench = remote_summary.get("critic_bench") or {}
    retriever_bench = remote_summary.get("retriever_bench") or {}
    router_bench = remote_summary.get("router_bench") or {}
    critic_gated = router_bench.get("critic_gated") or {}

    exact_positive_rows = safe_int(bucket_counts.get("exact_positive"))
    weak_positive_rows = safe_int(bucket_counts.get("weak_positive"))
    target_cov = safe_float(merged_summary.get("target_action_coverage"))
    critic_acc = safe_float(critic_bench.get("bucket_accuracy"))
    retrieval_exact = safe_float(retriever_bench.get("exact_match_rate"))
    route_abstain = safe_float(critic_gated.get("route_abstain_rate"))

    metrics = {
        "rows": safe_int(merged_summary.get("total_rows")),
        "exact_positive_rows": exact_positive_rows,
        "weak_positive_rows": weak_positive_rows,
        "target_action_coverage": target_cov,
        "critic_bucket_accuracy": critic_acc,
        "retriever_exact_match_rate": retrieval_exact,
        "route_abstain_rate": route_abstain,
    }
    trainer_policy = build_trainer_policy(cluster_id, metrics, profile)
    return {
        "cluster_id": cluster_id,
        "role_name": ROLE_NAMES.get(cluster_id, "specialist_trm"),
        "support_tier": support_tier(exact_positive_rows, target_cov, route_abstain),
        "goal": str(profile.get("goal") or ""),
        "task_family_label": str(profile.get("task_family_label") or ""),
        "rows": metrics["rows"],
        "exact_positive_rows": exact_positive_rows,
        "weak_positive_rows": weak_positive_rows,
        "target_action_coverage": round_metric(target_cov),
        "critic_bucket_accuracy": round_metric(critic_acc) if remote_summary else None,
        "retriever_exact_match_rate": round_metric(retrieval_exact) if remote_summary else None,
        "route_abstain_rate": round_metric(route_abstain) if remote_summary else None,
        "bucket_counts": dict(bucket_counts),
        "source_env_counts": dict(merged_summary.get("source_env_counts") or {}),
        "skill_prompt_lines": build_skill_lines(cluster_id, metrics),
        "trainer_lines": build_trainer_lines(cluster_id, metrics),
        "trainer_policy": trainer_policy,
    }


def build_payload(
    *,
    matrix_root: Path,
    cluster_ids: Iterable[str] | None = None,
    manifest_path: Path = DEFAULT_MANIFEST,
) -> Dict[str, Any]:
    profiles = load_cluster_profiles(manifest_path)
    chosen_cluster_ids = list(cluster_ids or discover_cluster_ids(matrix_root))
    cards: Dict[str, Dict[str, Any]] = {}
    for cluster_id in chosen_cluster_ids:
        merged_summary, remote_summary = load_cluster_sources(matrix_root, cluster_id)
        if not merged_summary:
            continue
        cards[cluster_id] = build_cluster_card(
            cluster_id,
            merged_summary,
            remote_summary,
            profiles.get(cluster_id, {}),
        )

    action_ready = [
        card["cluster_id"]
        for card in sorted(
            cards.values(),
            key=lambda item: (
                -safe_float(item.get("target_action_coverage")),
                -safe_int(item.get("exact_positive_rows")),
                item["cluster_id"],
            ),
        )
        if safe_float(card.get("target_action_coverage")) >= 0.2
    ]
    critic_first = [
        card["cluster_id"]
        for card in sorted(
            cards.values(),
            key=lambda item: (
                -safe_float(item.get("route_abstain_rate")),
                -safe_float(item.get("critic_bucket_accuracy")),
                item["cluster_id"],
            ),
        )
        if safe_float(card.get("target_action_coverage")) < 0.2
    ]

    global_lines: List[str] = []
    if action_ready:
        global_lines.append(
            "Role split: action-bearing TRM support currently lives mainly in "
            + ", ".join(action_ready)
            + "."
        )
    if critic_first:
        global_lines.append(
            "Keep hard reasoning and guarded safety roles critic-first until their exact-positive banks grow: "
            + ", ".join(critic_first[:4])
            + "."
        )

    return {
        "generated_at": utc_now(),
        "matrix_root": str(matrix_root.resolve()),
        "manifest_path": str(manifest_path.resolve()),
        "global_prompt_lines": global_lines,
        "cluster_cards": cards,
    }


def render_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# Primehub Role-Based TRM Imprint",
        "",
    ]
    for line in payload.get("global_prompt_lines", []):
        lines.append(f"- {line}")
    if payload.get("global_prompt_lines"):
        lines.append("")
    for cluster_id, card in (payload.get("cluster_cards") or {}).items():
        lines.extend(
            [
                f"## {cluster_id}",
                f"- role_name: {card.get('role_name', '')}",
                f"- support_tier: {card.get('support_tier', '')}",
                f"- goal: {card.get('goal', '')}",
                f"- rows: {card.get('rows', 0)}",
                f"- exact_positive_rows: {card.get('exact_positive_rows', 0)}",
                f"- target_action_coverage: {safe_float(card.get('target_action_coverage')):.4f}",
            ]
        )
        critic_acc = card.get("critic_bucket_accuracy")
        retrieval_exact = card.get("retriever_exact_match_rate")
        route_abstain = card.get("route_abstain_rate")
        if critic_acc is not None:
            lines.append(f"- critic_bucket_accuracy: {safe_float(critic_acc):.4f}")
        if retrieval_exact is not None:
            lines.append(f"- retriever_exact_match_rate: {safe_float(retrieval_exact):.4f}")
        if route_abstain is not None:
            lines.append(f"- route_abstain_rate: {safe_float(route_abstain):.4f}")
        trainer_policy = card.get("trainer_policy") or {}
        if trainer_policy:
            lines.append(
                "- trainer_policy: "
                + ", ".join(
                    [
                        f"exact_positive_weight={safe_float(trainer_policy.get('exact_positive_weight')):.2f}",
                        f"near_miss_weight={safe_float(trainer_policy.get('near_miss_weight')):.2f}",
                        f"weak_positive_weight={safe_float(trainer_policy.get('weak_positive_weight')):.2f}",
                        f"negative_weight={safe_float(trainer_policy.get('negative_weight')):.2f}",
                        f"min_supervision_weight={safe_float(trainer_policy.get('min_supervision_weight')):.2f}",
                        f"top_k={safe_int(trainer_policy.get('top_k'))}",
                        f"routing_strength={str(trainer_policy.get('routing_strength') or '')}",
                    ]
                )
            )
            signal_weights = trainer_policy.get("signal_weights") or {}
            if signal_weights:
                lines.append(
                    "- signal_weights: "
                    + ", ".join(
                        f"{key}={safe_float(value):.2f}" for key, value in sorted(signal_weights.items())
                    )
                )
        lines.append("- skill_prompt_lines:")
        for item in card.get("skill_prompt_lines", []):
            lines.append(f"  - {item}")
        lines.append("- trainer_lines:")
        for item in card.get("trainer_lines", []):
            lines.append(f"  - {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def load_role_imprint(path: Path | None = None) -> Dict[str, Any]:
    target = path or DEFAULT_ROLE_IMPRINT_JSON
    if target.exists():
        return load_json(target)
    return {}


def load_cluster_skill_prompt_lines(
    cluster_id: str,
    *,
    role_imprint_path: str = "",
    matrix_root: str = "",
) -> List[str]:
    explicit_path = Path(role_imprint_path).resolve() if role_imprint_path else None
    payload = load_role_imprint(explicit_path)
    if not payload:
        target_matrix_root = Path(matrix_root).resolve() if matrix_root else DEFAULT_MATRIX_ROOT
        if not target_matrix_root.exists():
            return []
        payload = build_payload(matrix_root=target_matrix_root)
    cards = payload.get("cluster_cards") or {}
    card = cards.get(cluster_id) or {}
    lines = []
    for item in card.get("skill_prompt_lines", []):
        text = str(item).strip()
        if text:
            lines.append(text)
    return lines


def load_cluster_role_gate(
    cluster_id: str,
    *,
    role_imprint_path: str = "",
) -> Dict[str, Any]:
    explicit_path = Path(role_imprint_path).resolve() if role_imprint_path else None
    payload = load_role_imprint(explicit_path)
    cards = payload.get("cluster_cards") or {}
    card = cards.get(cluster_id) or {}
    support_tier = str(card.get("support_tier") or "")
    role_mode = "action_support" if support_tier in ACTION_SUPPORT_TIERS else "critic_only"
    allow_action = role_mode == "action_support"
    return {
        "cluster_id": cluster_id,
        "support_tier": support_tier,
        "role_mode": role_mode,
        "allow_action": allow_action,
        "action_oriented_cluster": cluster_id in ACTION_ORIENTED_CLUSTERS,
        "goal": str(card.get("goal") or ""),
    }
