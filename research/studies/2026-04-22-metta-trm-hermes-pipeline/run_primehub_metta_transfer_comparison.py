from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


STUDY_DIR = Path(__file__).resolve().parent
REPO_ROOT = STUDY_DIR.parents[2]
HARNESS_ROOT = Path(r"C:/projects/trm_observability_harness")
DEFAULT_OUT_DIR = STUDY_DIR / "artifacts" / "primehub_transfer_comparison"
DEFAULT_BASE_CORPUS = REPO_ROOT / "data" / "primehub_trm_autoresearch" / "cycle_12" / "primehub_trm_merged.jsonl"
DEFAULT_STRUCTURED_TRANSFER = STUDY_DIR / "artifacts" / "primehub_structured_map_transfer" / "metta_primehub_transfer_bundle.jsonl"
DEFAULT_IF_TRANSFER = STUDY_DIR / "artifacts" / "if_summarize_judge_transfer" / "metta_primehub_transfer_bundle.jsonl"

if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

from harness.trm_critic import TRMCritic  # noqa: E402
from harness.trm_retrieval import TRMRetriever, grid_cell_accuracy, load_jsonl, normalize_text, stable_split  # noqa: E402


ALLOWED_BUCKETS = {
    "exact_positive": {"exact_positive", "near_miss", "weak_positive"},
    "near_miss": {"near_miss", "exact_positive", "weak_positive"},
    "weak_positive": {"weak_positive", "near_miss", "exact_positive"},
    "negative": set(),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare primehub transfer bundles against the original external primehub holdout rows.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--base-corpus", default=str(DEFAULT_BASE_CORPUS))
    parser.add_argument("--structured-transfer", default=str(DEFAULT_STRUCTURED_TRANSFER))
    parser.add_argument("--if-transfer", default=str(DEFAULT_IF_TRANSFER))
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--holdout-ratio", type=float, default=0.2)
    parser.add_argument("--min-supervision-weight", type=float, default=0.4)
    parser.add_argument("--events-path", help="Optional JSONL event log path.")
    parser.add_argument("--summary-path", help="Optional summary JSON path.")
    parser.add_argument("--training-task-id", default="metta-primehub-transfer-comparison-20260423")
    parser.add_argument("--checkpoint-interval", default="variant_complete")
    parser.add_argument("--chunk-strategy", default="variant_per_run")
    return parser.parse_args()


def run(cmd: List[str], *, cwd: Path) -> None:
    subprocess.run(cmd, cwd=str(cwd), check=True)


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


def merge_inputs(inputs: List[Path], out_jsonl: Path, out_summary: Path) -> None:
    cmd = [sys.executable, str(HARNESS_ROOT / "scripts" / "merge_trm_train_rows.py")]
    for input_path in inputs:
        cmd.extend(["--input", str(input_path)])
    cmd.extend(
        [
            "--output",
            str(out_jsonl),
            "--summary",
            str(out_summary),
            "--min-exact-positives-per-family",
            "2",
        ]
    )
    run(cmd, cwd=REPO_ROOT)


def run_rollup(
    *,
    input_path: Path,
    out_dir: Path,
    top_k: int,
    holdout_ratio: float,
    min_supervision_weight: float,
) -> Dict[str, Any]:
    model_dir = out_dir / "models"
    bench_dir = out_dir / "bench"
    model_dir.mkdir(parents=True, exist_ok=True)
    bench_dir.mkdir(parents=True, exist_ok=True)

    critic_model = model_dir / "trm_critic.json"
    critic_summary = model_dir / "trm_critic.summary.json"
    critic_bench_summary = bench_dir / "trm_critic_bench.summary.json"
    critic_predictions = bench_dir / "trm_critic_bench.jsonl"

    retriever_model = model_dir / "trm_retriever.json"
    retriever_summary = model_dir / "trm_retriever.summary.json"
    retriever_bench_summary = bench_dir / "trm_retriever_bench.summary.json"
    retriever_predictions = bench_dir / "trm_retriever_bench.jsonl"

    router_bench_summary = bench_dir / "trm_router_bench.summary.json"
    router_predictions = bench_dir / "trm_router_bench.jsonl"

    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "train_trm_critic.py"),
            "--input",
            str(input_path),
            "--output",
            str(critic_model),
            "--summary",
            str(critic_summary),
            "--k",
            str(top_k),
        ],
        cwd=REPO_ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "bench_trm_critic.py"),
            "--input",
            str(input_path),
            "--summary",
            str(critic_bench_summary),
            "--predictions",
            str(critic_predictions),
            "--holdout-ratio",
            str(holdout_ratio),
            "--k",
            str(top_k),
        ],
        cwd=REPO_ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "train_trm_retriever.py"),
            "--input",
            str(input_path),
            "--output",
            str(retriever_model),
            "--summary",
            str(retriever_summary),
            "--min-supervision-weight",
            str(min_supervision_weight),
        ],
        cwd=REPO_ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "bench_trm_retriever.py"),
            "--input",
            str(input_path),
            "--summary",
            str(retriever_bench_summary),
            "--predictions",
            str(retriever_predictions),
            "--holdout-ratio",
            str(holdout_ratio),
            "--min-supervision-weight",
            str(min_supervision_weight),
        ],
        cwd=REPO_ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "bench_trm_router.py"),
            "--input",
            str(input_path),
            "--summary",
            str(router_bench_summary),
            "--predictions",
            str(router_predictions),
            "--holdout-ratio",
            str(holdout_ratio),
            "--top-k",
            str(top_k),
            "--min-supervision-weight",
            str(min_supervision_weight),
        ],
        cwd=REPO_ROOT,
    )

    return {
        "critic_model": str(critic_model),
        "critic_summary": json.loads(critic_summary.read_text(encoding="utf-8")),
        "critic_bench_summary": json.loads(critic_bench_summary.read_text(encoding="utf-8")),
        "retriever_model": str(retriever_model),
        "retriever_summary": json.loads(retriever_summary.read_text(encoding="utf-8")),
        "retriever_bench_summary": json.loads(retriever_bench_summary.read_text(encoding="utf-8")),
        "router_bench_summary": json.loads(router_bench_summary.read_text(encoding="utf-8")),
    }


def choose_gated_action(
    row: Dict[str, Any],
    *,
    retriever: TRMRetriever,
    critic: TRMCritic,
    top_k: int,
) -> Optional[str]:
    critic_pred = critic.predict(row)
    predicted_bucket = str(critic_pred["predicted_bucket"])
    allowed = ALLOWED_BUCKETS.get(predicted_bucket, set())
    if predicted_bucket == "negative" or not allowed:
        return None
    ranked = retriever.ranked_candidates(row, limit=top_k)
    for _, example in ranked:
        if example.bucket in allowed:
            return example.target_action
    if ranked:
        return ranked[0][1].target_action
    return None


def evaluate_subset(
    rows: List[Dict[str, Any]],
    *,
    retriever: TRMRetriever,
    critic: TRMCritic,
    top_k: int,
) -> Dict[str, Any]:
    if not rows:
        return {
            "rows": 0,
            "critic_bucket_accuracy": None,
            "retriever_exact_match_rate": None,
            "router_retrieval_only_exact_match_rate": None,
            "router_critic_gated_exact_match_rate": None,
            "router_critic_gated_route_abstain_rate": None,
        }

    critic_hits = 0
    retrieval_hits = 0
    router_retrieval_hits = 0
    router_gated_hits = 0
    router_abstains = 0

    for row in rows:
        critic_pred = critic.predict(row)
        critic_hits += int(str(critic_pred["predicted_bucket"]) == str(row.get("bucket") or ""))

        base_action, _, _ = retriever.predict(row)
        gold_action = row.get("target_action")
        base_exact = bool(base_action) and normalize_text(base_action) == normalize_text(gold_action)
        retrieval_hits += int(base_exact)
        router_retrieval_hits += int(base_exact)

        gated_action = choose_gated_action(row, retriever=retriever, critic=critic, top_k=top_k)
        gated_exact = bool(gated_action) and normalize_text(gated_action) == normalize_text(gold_action)
        router_gated_hits += int(gated_exact)
        router_abstains += int(not gated_action)

    total = len(rows)
    return {
        "rows": total,
        "critic_bucket_accuracy": round(critic_hits / total, 4),
        "retriever_exact_match_rate": round(retrieval_hits / total, 4),
        "router_retrieval_only_exact_match_rate": round(router_retrieval_hits / total, 4),
        "router_critic_gated_exact_match_rate": round(router_gated_hits / total, 4),
        "router_critic_gated_route_abstain_rate": round(router_abstains / total, 4),
    }


def evaluate_original_subsets(
    *,
    merged_rows: List[Dict[str, Any]],
    holdout_ratio: float,
    top_k: int,
    min_supervision_weight: float,
    focus_envs: List[str],
) -> Dict[str, Any]:
    train_rows, eval_rows = stable_split(merged_rows, holdout_ratio)
    critic = TRMCritic.from_rows(train_rows, k=top_k)
    retriever = TRMRetriever.from_rows(
        train_rows,
        include_buckets=["exact_positive", "near_miss", "weak_positive"],
        min_supervision_weight=min_supervision_weight,
    )

    original_external = [
        row
        for row in eval_rows
        if str(row.get("source_env_type") or "") == "ExternalPrimeHubEnv"
        and str(row.get("task_family") or "") == "primehub"
    ]
    focus_external = [
        row for row in original_external if str(row.get("source_env_name") or "") in focus_envs
    ]
    primehub_all = [row for row in eval_rows if str(row.get("task_family") or "") == "primehub"]

    env_counts: Dict[str, int] = {}
    for row in original_external:
        env_id = str(row.get("source_env_name") or "")
        env_counts[env_id] = env_counts.get(env_id, 0) + 1

    focus_env_counts: Dict[str, int] = {}
    for row in focus_external:
        env_id = str(row.get("source_env_name") or "")
        focus_env_counts[env_id] = focus_env_counts.get(env_id, 0) + 1

    return {
        "primehub_all_eval": evaluate_subset(primehub_all, retriever=retriever, critic=critic, top_k=top_k),
        "original_external_primehub_eval": evaluate_subset(original_external, retriever=retriever, critic=critic, top_k=top_k),
        "original_external_focus_eval": evaluate_subset(focus_external, retriever=retriever, critic=critic, top_k=top_k),
        "original_external_env_counts": env_counts,
        "original_external_focus_env_counts": focus_env_counts,
        "focus_envs": focus_envs,
    }


def metric_delta(current: Dict[str, Any], control: Dict[str, Any], keys: Iterable[str]) -> Dict[str, Any]:
    delta: Dict[str, Any] = {}
    for key in keys:
        cur = current.get(key)
        base = control.get(key)
        if isinstance(cur, (int, float)) and isinstance(base, (int, float)):
            delta[key] = round(cur - base, 4)
        else:
            delta[key] = None
    return delta


def build_markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# Primehub Transfer Comparison",
        "",
        "## Trainer Plan",
        "",
        f"- `training_task_id`: `{summary['trainer_plan']['training_task_id']}`",
        f"- `chunk_strategy`: `{summary['trainer_plan']['chunk_strategy']}`",
        f"- `checkpoint_interval`: `{summary['trainer_plan']['checkpoint_interval']}`",
        f"- `holdout_ratio`: `{summary['trainer_plan']['holdout_ratio']}`",
        f"- `top_k`: `{summary['trainer_plan']['top_k']}`",
        f"- `min_supervision_weight`: `{summary['trainer_plan']['min_supervision_weight']}`",
        "",
        "## Original External Primehub Holdout",
        "",
        "| Variant | Rows | Critic bucket acc | Retriever exact | Gated router exact | Gated abstain |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variant_name, variant in summary["variants"].items():
        subset = variant["subsets"]["original_external_primehub_eval"]
        lines.append(
            "| "
            + " | ".join(
                [
                    variant_name,
                    str(subset["rows"]),
                    f"{subset['critic_bucket_accuracy']:.4f}" if subset["critic_bucket_accuracy"] is not None else "n/a",
                    f"{subset['retriever_exact_match_rate']:.4f}" if subset["retriever_exact_match_rate"] is not None else "n/a",
                    f"{subset['router_critic_gated_exact_match_rate']:.4f}" if subset["router_critic_gated_exact_match_rate"] is not None else "n/a",
                    f"{subset['router_critic_gated_route_abstain_rate']:.4f}" if subset["router_critic_gated_route_abstain_rate"] is not None else "n/a",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Focus Env Holdout",
            "",
            f"Focus envs: {', '.join('`' + env + '`' for env in summary['focus_envs'])}",
            "",
            "| Variant | Rows | Critic bucket acc | Retriever exact | Gated router exact | Gated abstain |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for variant_name, variant in summary["variants"].items():
        subset = variant["subsets"]["original_external_focus_eval"]
        lines.append(
            "| "
            + " | ".join(
                [
                    variant_name,
                    str(subset["rows"]),
                    f"{subset['critic_bucket_accuracy']:.4f}" if subset["critic_bucket_accuracy"] is not None else "n/a",
                    f"{subset['retriever_exact_match_rate']:.4f}" if subset["retriever_exact_match_rate"] is not None else "n/a",
                    f"{subset['router_critic_gated_exact_match_rate']:.4f}" if subset["router_critic_gated_exact_match_rate"] is not None else "n/a",
                    f"{subset['router_critic_gated_route_abstain_rate']:.4f}" if subset["router_critic_gated_route_abstain_rate"] is not None else "n/a",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Delta Vs Control On Original External Holdout",
            "",
            "| Variant | Critic bucket acc | Retriever exact | Gated router exact | Gated abstain |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for variant_name, delta in summary["control_deltas"].items():
        subset = delta["original_external_primehub_eval"]
        lines.append(
            "| "
            + " | ".join(
                [
                    variant_name,
                    f"{subset['critic_bucket_accuracy']:+.4f}" if subset["critic_bucket_accuracy"] is not None else "n/a",
                    f"{subset['retriever_exact_match_rate']:+.4f}" if subset["retriever_exact_match_rate"] is not None else "n/a",
                    f"{subset['router_critic_gated_exact_match_rate']:+.4f}" if subset["router_critic_gated_exact_match_rate"] is not None else "n/a",
                    f"{subset['router_critic_gated_route_abstain_rate']:+.4f}" if subset["router_critic_gated_route_abstain_rate"] is not None else "n/a",
                ]
            )
            + " |"
        )

    readout = [
        "",
        "## Readout",
        "",
        f"- Original external primehub holdout rows: `{summary['variants']['control']['subsets']['original_external_primehub_eval']['rows']}`.",
    ]
    if summary.get("original_external_lift_observed"):
        readout.append(f"- Best original external lift variant: `{summary['best_original_variant']}`.")
    else:
        readout.append("- No original external lift was observed on the untouched primehub holdout.")
    readout.extend(
        [
            f"- Original external env counts: `{summary['variants']['control']['subsets']['original_external_env_counts']}`.",
            f"- Focus-env overlap in the original holdout: `{summary['variants']['control']['subsets']['original_external_focus_env_counts']}`.",
        ]
    )
    lines.extend(readout)
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    events_path = Path(args.events_path).resolve() if args.events_path else out_dir / "comparison.events.jsonl"
    summary_path = Path(args.summary_path).resolve() if args.summary_path else out_dir / "comparison.summary.json"

    base_corpus = Path(args.base_corpus).resolve()
    structured_transfer = Path(args.structured_transfer).resolve()
    if_transfer = Path(args.if_transfer).resolve()

    if events_path.exists():
        events_path.unlink()

    trainer_plan = {
        "training_task_id": args.training_task_id,
        "checkpoint_interval": args.checkpoint_interval,
        "chunk_strategy": args.chunk_strategy,
        "holdout_ratio": args.holdout_ratio,
        "top_k": args.top_k,
        "min_supervision_weight": args.min_supervision_weight,
        "base_corpus": str(base_corpus),
        "structured_transfer": str(structured_transfer),
        "if_transfer": str(if_transfer),
    }
    emit_event(events_path, "trainer_plan", trainer_plan=trainer_plan)

    variants = [
        ("control", [base_corpus]),
        ("control_plus_structured_transfer", [base_corpus, structured_transfer]),
        ("control_plus_structured_and_if_transfer", [base_corpus, structured_transfer, if_transfer]),
    ]

    focus_envs = sorted(
        {
            row.get("source_env_name")
            for path in [structured_transfer, if_transfer]
            for row in load_jsonl(path)
            if str(row.get("source_env_name") or "").strip()
        }
    )

    variant_results: Dict[str, Any] = {}
    for variant_name, inputs in variants:
        variant_dir = out_dir / "variants" / variant_name
        variant_dir.mkdir(parents=True, exist_ok=True)
        merged_jsonl = variant_dir / "merged.jsonl"
        merged_summary_path = variant_dir / "merged.summary.json"

        emit_event(events_path, "variant_start", variant=variant_name, inputs=[str(path) for path in inputs])
        merge_inputs(inputs, merged_jsonl, merged_summary_path)
        emit_event(events_path, "checkpoint", variant=variant_name, checkpoint="merged", output=str(merged_jsonl))

        rollup = run_rollup(
            input_path=merged_jsonl,
            out_dir=variant_dir,
            top_k=args.top_k,
            holdout_ratio=args.holdout_ratio,
            min_supervision_weight=args.min_supervision_weight,
        )
        merged_rows = load_jsonl(merged_jsonl)
        merged_summary = json.loads(merged_summary_path.read_text(encoding="utf-8"))
        subsets = evaluate_original_subsets(
            merged_rows=merged_rows,
            holdout_ratio=args.holdout_ratio,
            top_k=args.top_k,
            min_supervision_weight=args.min_supervision_weight,
            focus_envs=focus_envs,
        )
        variant_results[variant_name] = {
            "merged_summary": merged_summary,
            "global": {
                "critic_bucket_accuracy": rollup["critic_bench_summary"]["bucket_accuracy"],
                "retriever_exact_match_rate": rollup["retriever_bench_summary"]["exact_match_rate"],
                "router_critic_gated_exact_match_rate": rollup["router_bench_summary"]["critic_gated"]["exact_match_rate"],
                "router_critic_gated_route_abstain_rate": rollup["router_bench_summary"]["critic_gated"]["route_abstain_rate"],
            },
            "subsets": subsets,
            "artifacts": rollup,
        }
        emit_event(
            events_path,
            "variant_complete",
            variant=variant_name,
            total_rows=merged_summary["total_rows"],
            original_external_critic_bucket_accuracy=subsets["original_external_primehub_eval"]["critic_bucket_accuracy"],
            original_external_router_exact=subsets["original_external_primehub_eval"]["router_critic_gated_exact_match_rate"],
        )

    control = variant_results["control"]
    delta_keys = [
        "critic_bucket_accuracy",
        "retriever_exact_match_rate",
        "router_retrieval_only_exact_match_rate",
        "router_critic_gated_exact_match_rate",
        "router_critic_gated_route_abstain_rate",
    ]
    control_deltas: Dict[str, Any] = {}
    for variant_name, variant in variant_results.items():
        if variant_name == "control":
            continue
        control_deltas[variant_name] = {
            "original_external_primehub_eval": metric_delta(
                variant["subsets"]["original_external_primehub_eval"],
                control["subsets"]["original_external_primehub_eval"],
                delta_keys,
            ),
            "original_external_focus_eval": metric_delta(
                variant["subsets"]["original_external_focus_eval"],
                control["subsets"]["original_external_focus_eval"],
                delta_keys,
            ),
        }

    best_original_variant = max(
        control_deltas,
        key=lambda item: (
            control_deltas[item]["original_external_primehub_eval"]["critic_bucket_accuracy"] or -999.0,
            control_deltas[item]["original_external_primehub_eval"]["router_critic_gated_exact_match_rate"] or -999.0,
        ),
    )
    original_external_lift_observed = any(
        (delta["original_external_primehub_eval"].get("critic_bucket_accuracy") or 0.0) > 0.0
        or (delta["original_external_primehub_eval"].get("retriever_exact_match_rate") or 0.0) > 0.0
        or (delta["original_external_primehub_eval"].get("router_retrieval_only_exact_match_rate") or 0.0) > 0.0
        or (delta["original_external_primehub_eval"].get("router_critic_gated_exact_match_rate") or 0.0) > 0.0
        for delta in control_deltas.values()
    )

    summary = {
        "generated_at_utc": utc_now(),
        "trainer_plan": trainer_plan,
        "focus_envs": focus_envs,
        "variants": variant_results,
        "control_deltas": control_deltas,
        "best_original_variant": best_original_variant,
        "original_external_lift_observed": original_external_lift_observed,
    }
    write_json(summary_path, summary)
    write_markdown(out_dir / "comparison.findings.md", build_markdown(summary))
    emit_event(events_path, "done", summary_path=str(summary_path))
    print(str(summary_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
