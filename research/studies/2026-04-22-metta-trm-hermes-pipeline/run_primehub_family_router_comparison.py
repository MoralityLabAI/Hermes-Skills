from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence


STUDY_DIR = Path(__file__).resolve().parent
REPO_ROOT = STUDY_DIR.parents[2]
HARNESS_ROOT = Path(r"C:/projects/trm_observability_harness")
DEFAULT_OUT_DIR = STUDY_DIR / "artifacts" / "primehub_family_router_comparison"
DEFAULT_BASE_CORPUS = REPO_ROOT / "data" / "primehub_trm_autoresearch" / "cycle_12" / "primehub_trm_merged.jsonl"
DEFAULT_ROUTER_BUNDLE = STUDY_DIR / "artifacts" / "primehub_family_router_bundle" / "primehub_family_router_bundle.json"
DEFAULT_EXTERNAL_ABSTRACTION = STUDY_DIR / "artifacts" / "primehub_external_abstraction_bundle" / "primehub_external_abstraction_bundle.jsonl"
DEFAULT_EXTERNAL_CRITIC_SUPPORT = STUDY_DIR / "artifacts" / "primehub_external_critic_support_bundle" / "primehub_external_critic_support_bundle.jsonl"

if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

from harness.trm_critic import TRMCritic  # noqa: E402
from harness.trm_retrieval import TRMRetriever, load_jsonl, normalize_text, stable_split  # noqa: E402


ALLOWED_BUCKETS = {
    "exact_positive": {"exact_positive", "near_miss", "weak_positive"},
    "near_miss": {"near_miss", "exact_positive", "weak_positive"},
    "weak_positive": {"weak_positive", "near_miss", "exact_positive"},
    "negative": set(),
}


class ModelSet:
    def __init__(self, rows: Sequence[Dict[str, Any]], *, holdout_ratio: float, top_k: int, min_supervision_weight: float):
        train_rows, _ = stable_split(rows, holdout_ratio)
        self.train_rows = train_rows
        self.critic = TRMCritic.from_rows(train_rows, k=top_k)
        self.retriever = TRMRetriever.from_rows(
            train_rows,
            include_buckets=["exact_positive", "near_miss", "weak_positive"],
            min_supervision_weight=min_supervision_weight,
        )


class RouterModel:
    def __init__(self, default: ModelSet, specialists: Dict[str, ModelSet]):
        self.default = default
        self.specialists = specialists

    def for_row(self, row: Dict[str, Any]) -> ModelSet:
        env_name = str(row.get("source_env_name") or "")
        return self.specialists.get(env_name, self.default)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare routed MeTTa family specialists against shared merged-family critics.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--base-corpus", default=str(DEFAULT_BASE_CORPUS))
    parser.add_argument("--router-bundle", default=str(DEFAULT_ROUTER_BUNDLE))
    parser.add_argument("--external-abstraction", default=str(DEFAULT_EXTERNAL_ABSTRACTION))
    parser.add_argument("--external-critic-support", default=str(DEFAULT_EXTERNAL_CRITIC_SUPPORT))
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--holdout-ratio", type=float, default=0.2)
    parser.add_argument("--min-supervision-weight", type=float, default=0.4)
    parser.add_argument("--events-path")
    parser.add_argument("--summary-path")
    parser.add_argument("--training-task-id", default="metta-primehub-family-router-comparison-20260423")
    parser.add_argument("--checkpoint-interval", default="variant_complete")
    parser.add_argument("--chunk-strategy", default="router_variant_per_run")
    return parser.parse_args()


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def emit_event(event_path: Path, event: str, **payload: Any) -> None:
    event_path.parent.mkdir(parents=True, exist_ok=True)
    row = {"ts": utc_now(), "event": event}
    row.update(payload)
    with event_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def maybe_load_jsonl(path: Path) -> List[Dict[str, Any]]:
    return load_jsonl(path) if path.exists() else []


def load_router_bundle(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def choose_gated_action(row: Dict[str, Any], *, model: ModelSet, top_k: int) -> Optional[str]:
    critic_pred = model.critic.predict(row)
    predicted_bucket = str(critic_pred["predicted_bucket"])
    allowed = ALLOWED_BUCKETS.get(predicted_bucket, set())
    if predicted_bucket == "negative" or not allowed:
        return None
    ranked = model.retriever.ranked_candidates(row, limit=top_k)
    for _, example in ranked:
        if example.bucket in allowed:
            return example.target_action
    if ranked:
        return ranked[0][1].target_action
    return None


def parse_ifeval_contract(action: Optional[str]) -> Dict[str, bool]:
    text = str(action or "").strip()
    if not text:
        return {
            "action_nonempty": False,
            "postscript_present": False,
            "postscript_last_line": False,
            "semantic_match": False,
            "contract_success": False,
        }
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    last_line = lines[-1].lower() if lines else ""
    lowered = text.lower()
    postscript_prefix = "before i forget:"
    postscript_present = postscript_prefix in lowered
    semantic_region = lowered.split(postscript_prefix, 1)[0] if postscript_present else lowered
    semantic_match = bool(re.search(r"\bnegative\b", semantic_region)) and not bool(re.search(r"\bpositive\b", semantic_region))
    return {
        "action_nonempty": True,
        "postscript_present": postscript_present,
        "postscript_last_line": last_line.startswith(postscript_prefix),
        "semantic_match": semantic_match,
        "contract_success": last_line.startswith(postscript_prefix) and semantic_match,
    }


def parse_aime_action(action: Optional[str], expected_integer: str = "39") -> Dict[str, bool]:
    text = str(action or "").strip()
    if not text:
        return {
            "action_nonempty": False,
            "box_present": False,
            "boxed_exact": False,
        }
    match = re.search(r"\\boxed\s*\{\s*([^{}]+?)\s*\}", text)
    if not match:
        return {
            "action_nonempty": True,
            "box_present": False,
            "boxed_exact": False,
        }
    return {
        "action_nonempty": True,
        "box_present": True,
        "boxed_exact": match.group(1).strip() == expected_integer,
    }


def evaluate_subset(
    rows: List[Dict[str, Any]],
    *,
    model_for_row: Callable[[Dict[str, Any]], ModelSet],
    top_k: int,
) -> Dict[str, Any]:
    if not rows:
        return {
            "rows": 0,
            "critic_bucket_accuracy": None,
            "retriever_exact_match_rate": None,
            "router_critic_gated_exact_match_rate": None,
            "router_critic_gated_route_abstain_rate": None,
        }

    critic_hits = 0
    retrieval_hits = 0
    router_gated_hits = 0
    router_abstains = 0
    for row in rows:
        model = model_for_row(row)
        critic_pred = model.critic.predict(row)
        critic_hits += int(str(critic_pred["predicted_bucket"]) == str(row.get("bucket") or ""))
        base_action, _, _ = model.retriever.predict(row)
        gold_action = row.get("target_action")
        retrieval_hits += int(bool(base_action) and normalize_text(base_action) == normalize_text(gold_action))
        gated_action = choose_gated_action(row, model=model, top_k=top_k)
        router_gated_hits += int(bool(gated_action) and normalize_text(gated_action) == normalize_text(gold_action))
        router_abstains += int(not gated_action)

    total = len(rows)
    return {
        "rows": total,
        "critic_bucket_accuracy": round(critic_hits / total, 4),
        "retriever_exact_match_rate": round(retrieval_hits / total, 4),
        "router_critic_gated_exact_match_rate": round(router_gated_hits / total, 4),
        "router_critic_gated_route_abstain_rate": round(router_abstains / total, 4),
    }


def evaluate_ifeval(
    rows: List[Dict[str, Any]],
    *,
    model_for_row: Callable[[Dict[str, Any]], ModelSet],
    top_k: int,
) -> Dict[str, Any]:
    if not rows:
        return {
            "rows": 0,
            "retrieval_contract_success_rate": None,
            "gated_contract_success_rate": None,
        }
    retrieval_hits = 0
    gated_hits = 0
    for row in rows:
        model = model_for_row(row)
        retrieval_action, _, _ = model.retriever.predict(row)
        retrieval_hits += int(parse_ifeval_contract(retrieval_action)["contract_success"])
        gated_action = choose_gated_action(row, model=model, top_k=top_k)
        gated_hits += int(parse_ifeval_contract(gated_action)["contract_success"])
    total = len(rows)
    return {
        "rows": total,
        "retrieval_contract_success_rate": round(retrieval_hits / total, 4),
        "gated_contract_success_rate": round(gated_hits / total, 4),
    }


def evaluate_aime(
    rows: List[Dict[str, Any]],
    *,
    model_for_row: Callable[[Dict[str, Any]], ModelSet],
    top_k: int,
) -> Dict[str, Any]:
    if not rows:
        return {
            "rows": 0,
            "retrieval_boxed_exact_rate": None,
            "gated_boxed_exact_rate": None,
            "gated_action_nonempty_rate": None,
        }
    retrieval_hits = 0
    gated_hits = 0
    gated_nonempty = 0
    for row in rows:
        model = model_for_row(row)
        retrieval_action, _, _ = model.retriever.predict(row)
        retrieval_hits += int(parse_aime_action(retrieval_action)["boxed_exact"])
        gated_action = choose_gated_action(row, model=model, top_k=top_k)
        gated_eval = parse_aime_action(gated_action)
        gated_hits += int(gated_eval["boxed_exact"])
        gated_nonempty += int(gated_eval["action_nonempty"])
    total = len(rows)
    return {
        "rows": total,
        "retrieval_boxed_exact_rate": round(retrieval_hits / total, 4),
        "gated_boxed_exact_rate": round(gated_hits / total, 4),
        "gated_action_nonempty_rate": round(gated_nonempty / total, 4),
    }


def build_model(rows: Sequence[Dict[str, Any]], *, holdout_ratio: float, top_k: int, min_supervision_weight: float) -> ModelSet:
    return ModelSet(rows, holdout_ratio=holdout_ratio, top_k=top_k, min_supervision_weight=min_supervision_weight)


def evaluate_variant(
    *,
    variant_name: str,
    model_for_row: Callable[[Dict[str, Any]], ModelSet],
    eval_rows: List[Dict[str, Any]],
    routed_envs: List[str],
    top_k: int,
) -> Dict[str, Any]:
    original_external = [
        row
        for row in eval_rows
        if str(row.get("source_env_type") or "") == "ExternalPrimeHubEnv"
        and str(row.get("task_family") or "") == "primehub"
    ]
    target_rows = [row for row in original_external if str(row.get("source_env_name") or "") in routed_envs]
    unrelated_rows = [row for row in original_external if str(row.get("source_env_name") or "") not in routed_envs]
    ifeval_rows = [row for row in original_external if str(row.get("source_env_name") or "") == "allenai_ifeval"]
    aime_rows = [row for row in original_external if str(row.get("source_env_name") or "") == "aime2026"]

    per_env: Dict[str, Any] = {}
    for env_name in sorted({str(row.get("source_env_name") or "") for row in original_external}):
        per_env[env_name] = evaluate_subset(
            [row for row in original_external if str(row.get("source_env_name") or "") == env_name],
            model_for_row=model_for_row,
            top_k=top_k,
        )

    return {
        "variant": variant_name,
        "original_external_primehub_eval": evaluate_subset(original_external, model_for_row=model_for_row, top_k=top_k),
        "target_family_eval": evaluate_subset(target_rows, model_for_row=model_for_row, top_k=top_k),
        "unrelated_external_eval": evaluate_subset(unrelated_rows, model_for_row=model_for_row, top_k=top_k),
        "ifeval_contract_eval": evaluate_ifeval(ifeval_rows, model_for_row=model_for_row, top_k=top_k),
        "aime_numeric_eval": evaluate_aime(aime_rows, model_for_row=model_for_row, top_k=top_k),
        "per_env": per_env,
    }


def delta(current: Optional[float], baseline: Optional[float]) -> Optional[float]:
    if isinstance(current, (int, float)) and isinstance(baseline, (int, float)):
        return round(current - baseline, 4)
    return None


def positive_drop(baseline: Optional[float], current: Optional[float]) -> float:
    if not isinstance(current, (int, float)) or not isinstance(baseline, (int, float)):
        return 0.0
    return round(max(0.0, baseline - current), 4)


def build_interference(variants: Dict[str, Any], baseline_name: str = "global_common") -> Dict[str, Any]:
    baseline = variants[baseline_name]
    out: Dict[str, Any] = {}
    for name, variant in variants.items():
        if name == baseline_name:
            continue
        ifeval_lift = delta(
            variant["ifeval_contract_eval"]["gated_contract_success_rate"],
            baseline["ifeval_contract_eval"]["gated_contract_success_rate"],
        )
        aime_lift = delta(
            variant["aime_numeric_eval"]["gated_boxed_exact_rate"],
            baseline["aime_numeric_eval"]["gated_boxed_exact_rate"],
        )
        target_lift = round((ifeval_lift or 0.0) + (aime_lift or 0.0), 4)
        unrelated_critic_drift = positive_drop(
            baseline["unrelated_external_eval"]["critic_bucket_accuracy"],
            variant["unrelated_external_eval"]["critic_bucket_accuracy"],
        )
        unrelated_router_regression = positive_drop(
            baseline["unrelated_external_eval"]["router_critic_gated_exact_match_rate"],
            variant["unrelated_external_eval"]["router_critic_gated_exact_match_rate"],
        )
        whole_critic_drift = positive_drop(
            baseline["original_external_primehub_eval"]["critic_bucket_accuracy"],
            variant["original_external_primehub_eval"]["critic_bucket_accuracy"],
        )
        out[name] = {
            "ifeval_gated_contract_lift": ifeval_lift,
            "aime_gated_boxed_exact_lift": aime_lift,
            "target_family_lift": target_lift,
            "unrelated_critic_drift": unrelated_critic_drift,
            "unrelated_gated_router_regression": unrelated_router_regression,
            "whole_holdout_critic_drift": whole_critic_drift,
            "net_interference_score": round(target_lift - unrelated_critic_drift - unrelated_router_regression, 4),
        }
    return out


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    if value is None:
        return "n/a"
    return str(value)


def build_markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# Primehub Family Router Comparison",
        "",
        "## Variants",
        "",
        "| Variant | Whole critic | Whole gated | Unrelated critic | Unrelated gated | IFEval gated contract | AIME gated exact |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, variant in summary["variants"].items():
        whole = variant["original_external_primehub_eval"]
        unrelated = variant["unrelated_external_eval"]
        ifeval = variant["ifeval_contract_eval"]
        aime = variant["aime_numeric_eval"]
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    fmt(whole["critic_bucket_accuracy"]),
                    fmt(whole["router_critic_gated_exact_match_rate"]),
                    fmt(unrelated["critic_bucket_accuracy"]),
                    fmt(unrelated["router_critic_gated_exact_match_rate"]),
                    fmt(ifeval["gated_contract_success_rate"]),
                    fmt(aime["gated_boxed_exact_rate"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Interference Vs Global Common",
            "",
            "| Variant | Target lift | Unrelated critic drift | Unrelated gated regression | Whole critic drift | Net score |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, item in summary["interference"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    fmt(item["target_family_lift"]),
                    fmt(item["unrelated_critic_drift"]),
                    fmt(item["unrelated_gated_router_regression"]),
                    fmt(item["whole_holdout_critic_drift"]),
                    fmt(item["net_interference_score"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Readout",
            "",
            f"- Routed envs: `{summary['routed_envs']}`.",
            f"- Best net interference variant: `{summary['best_net_variant']}`.",
            f"- Best target lift variant: `{summary['best_target_lift_variant']}`.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    events_path = Path(args.events_path).resolve() if args.events_path else out_dir / "family_router.events.jsonl"
    summary_path = Path(args.summary_path).resolve() if args.summary_path else out_dir / "family_router.summary.json"
    if events_path.exists():
        events_path.unlink()

    base_corpus = Path(args.base_corpus).resolve()
    router_bundle_path = Path(args.router_bundle).resolve()
    external_abstraction = Path(args.external_abstraction).resolve()
    external_critic_support = Path(args.external_critic_support).resolve()

    router_bundle = load_router_bundle(router_bundle_path)
    profiles = router_bundle.get("profiles", [])
    routed_envs = [str(profile["source_env_name"]) for profile in profiles]
    emit_event(events_path, "trainer_plan", training_task_id=args.training_task_id, routed_envs=routed_envs)

    base_rows = load_jsonl(base_corpus)
    _, base_eval_rows = stable_split(base_rows, args.holdout_ratio)
    common_rows = base_rows + maybe_load_jsonl(external_abstraction) + maybe_load_jsonl(external_critic_support)
    family_abstraction_rows = {
        str(profile["source_env_name"]): maybe_load_jsonl(Path(profile["abstraction_bundle"]))
        for profile in profiles
    }
    family_critic_rows = {
        str(profile["source_env_name"]): maybe_load_jsonl(Path(profile["critic_support_bundle"]))
        for profile in profiles
    }

    def make_model(rows: Sequence[Dict[str, Any]]) -> ModelSet:
        return build_model(
            rows,
            holdout_ratio=args.holdout_ratio,
            top_k=args.top_k,
            min_supervision_weight=args.min_supervision_weight,
        )

    models: Dict[str, Callable[[Dict[str, Any]], ModelSet]] = {}

    control_model = make_model(base_rows)
    models["control"] = lambda row, model=control_model: model

    global_common_model = make_model(common_rows)
    models["global_common"] = lambda row, model=global_common_model: model

    global_all_abstraction_model = make_model(
        common_rows + [row for rows in family_abstraction_rows.values() for row in rows]
    )
    models["global_all_abstractions"] = lambda row, model=global_all_abstraction_model: model

    global_all_stack_model = make_model(
        common_rows
        + [row for rows in family_abstraction_rows.values() for row in rows]
        + [row for rows in family_critic_rows.values() for row in rows]
    )
    models["global_all_stacks"] = lambda row, model=global_all_stack_model: model

    routed_abstraction = RouterModel(
        global_common_model,
        {
            env: make_model(common_rows + rows)
            for env, rows in family_abstraction_rows.items()
            if rows
        },
    )
    models["routed_abstractions"] = routed_abstraction.for_row

    routed_stack = RouterModel(
        global_common_model,
        {
            env: make_model(common_rows + family_abstraction_rows.get(env, []) + family_critic_rows.get(env, []))
            for env in routed_envs
            if family_abstraction_rows.get(env) or family_critic_rows.get(env)
        },
    )
    models["routed_stacks"] = routed_stack.for_row

    variant_results: Dict[str, Any] = {}
    for name, model_for_row in models.items():
        emit_event(events_path, "variant_start", variant=name)
        variant_results[name] = evaluate_variant(
            variant_name=name,
            model_for_row=model_for_row,
            eval_rows=base_eval_rows,
            routed_envs=routed_envs,
            top_k=args.top_k,
        )
        emit_event(events_path, "checkpoint", variant=name, checkpoint="evaluated")

    interference = build_interference(variant_results)
    best_net_variant = max(interference, key=lambda name: interference[name]["net_interference_score"])
    best_target_lift_variant = max(interference, key=lambda name: interference[name]["target_family_lift"])

    summary = {
        "generated_at_utc": utc_now(),
        "trainer_plan": {
            "training_task_id": args.training_task_id,
            "checkpoint_interval": args.checkpoint_interval,
            "chunk_strategy": args.chunk_strategy,
            "holdout_ratio": args.holdout_ratio,
            "top_k": args.top_k,
            "min_supervision_weight": args.min_supervision_weight,
            "base_corpus": str(base_corpus),
            "router_bundle": str(router_bundle_path),
            "external_abstraction": str(external_abstraction),
            "external_critic_support": str(external_critic_support),
        },
        "routed_envs": routed_envs,
        "router_bundle": router_bundle,
        "variants": variant_results,
        "interference": interference,
        "best_net_variant": best_net_variant,
        "best_target_lift_variant": best_target_lift_variant,
    }
    write_json(summary_path, summary)
    write_markdown(out_dir / "family_router.findings.md", build_markdown(summary))
    emit_event(events_path, "done", summary_path=str(summary_path))
    print(str(summary_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
