from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


STUDY_DIR = Path(__file__).resolve().parent
REPO_ROOT = STUDY_DIR.parents[2]
HARNESS_ROOT = Path(r"C:/projects/trm_observability_harness")
DEFAULT_OUT_DIR = STUDY_DIR / "artifacts" / "primehub_rollup_metta_comparison"
DEFAULT_BASE_CORPUS = REPO_ROOT / "data" / "primehub_trm_autoresearch" / "cycle_12" / "primehub_trm_merged.jsonl"
DEFAULT_OFFICIAL_BENCH_DIR = REPO_ROOT / "data" / "primehub_trm_autoresearch" / "cycle_12" / "bench"
DEFAULT_STRUCTURED_BUNDLE = STUDY_DIR / "artifacts" / "primehub_structured_map_trainer_policy" / "metta_trainer_policy_bundle.jsonl"
DEFAULT_IF_SUMMARIZE_BUNDLE = STUDY_DIR / "artifacts" / "if_summarize_judge_trainer_policy" / "metta_trainer_policy_bundle.jsonl"
DEFAULT_BASELINE_LEDGER = REPO_ROOT / "data" / "primehub_trainer_policy_baseline_rerun_20260421" / "ledger.jsonl"
DEFAULT_MINING_LEDGER = REPO_ROOT / "data" / "primehub_trainer_policy_mining_rerun_20260421" / "ledger.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare control Primehub TRM rollup against MeTTa-augmented trainer-policy bundles.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--base-corpus", default=str(DEFAULT_BASE_CORPUS))
    parser.add_argument("--official-base-bench-dir", default=str(DEFAULT_OFFICIAL_BENCH_DIR))
    parser.add_argument("--structured-bundle", default=str(DEFAULT_STRUCTURED_BUNDLE))
    parser.add_argument("--if-summarize-bundle", default=str(DEFAULT_IF_SUMMARIZE_BUNDLE))
    parser.add_argument("--baseline-ledger", default=str(DEFAULT_BASELINE_LEDGER))
    parser.add_argument("--mining-ledger", default=str(DEFAULT_MINING_LEDGER))
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--holdout-ratio", type=float, default=0.2)
    parser.add_argument("--min-supervision-weight", type=float, default=0.4)
    parser.add_argument("--events-path", help="Optional JSONL event log path.")
    parser.add_argument("--summary-path", help="Optional summary JSON path.")
    parser.add_argument("--training-task-id", default="metta-primehub-rollup-comparison-20260423")
    parser.add_argument("--checkpoint-interval", default="variant_complete")
    parser.add_argument("--chunk-strategy", default="variant_per_run")
    return parser.parse_args()


def run(cmd: List[str], *, cwd: Path) -> None:
    subprocess.run(cmd, cwd=str(cwd), check=True)


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


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


def merge_inputs(
    *,
    inputs: List[Path],
    out_jsonl: Path,
    out_summary: Path,
) -> None:
    cmd = [
        sys.executable,
        str(HARNESS_ROOT / "scripts" / "merge_trm_train_rows.py"),
    ]
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
        "critic_summary": load_json(critic_summary),
        "critic_bench_summary": load_json(critic_bench_summary),
        "retriever_summary": load_json(retriever_summary),
        "retriever_bench_summary": load_json(retriever_bench_summary),
        "router_bench_summary": load_json(router_bench_summary),
        "router_predictions_path": str(router_predictions),
    }


def compute_primehub_router_metrics(predictions_path: Path) -> Dict[str, Any]:
    rows = [row for row in load_jsonl(predictions_path) if str(row.get("task_family") or "") == "primehub"]
    total = len(rows)
    if not rows:
        return {
            "rows": 0,
            "retrieval_only_exact_match_rate": None,
            "critic_gated_exact_match_rate": None,
            "critic_gated_route_abstain_rate": None,
        }
    retrieval_exact = sum(1 for row in rows if bool(row.get("retrieval_only_exact")))
    critic_gated_exact = sum(1 for row in rows if bool(row.get("critic_gated_exact")))
    route_abstains = sum(1 for row in rows if bool(row.get("critic_gated_abstained")))
    return {
        "rows": total,
        "retrieval_only_exact_match_rate": round(retrieval_exact / total, 4),
        "critic_gated_exact_match_rate": round(critic_gated_exact / total, 4),
        "critic_gated_route_abstain_rate": round(route_abstains / total, 4),
    }


def summarize_variant(
    *,
    merged_summary: Dict[str, Any],
    rollup: Dict[str, Any],
) -> Dict[str, Any]:
    critic_bench = rollup["critic_bench_summary"]
    retriever_bench = rollup["retriever_bench_summary"]
    router_bench = rollup["router_bench_summary"]
    primehub_router = compute_primehub_router_metrics(Path(rollup["router_predictions_path"]))
    return {
        "merged_summary": merged_summary,
        "global": {
            "critic_bucket_accuracy": critic_bench["bucket_accuracy"],
            "retriever_exact_match_rate": retriever_bench["exact_match_rate"],
            "router_retrieval_only_exact_match_rate": router_bench["retrieval_only"]["exact_match_rate"],
            "router_critic_gated_exact_match_rate": router_bench["critic_gated"]["exact_match_rate"],
            "router_critic_gated_route_abstain_rate": router_bench["critic_gated"]["route_abstain_rate"],
            "retriever_example_count": retriever_bench["model_example_count"],
            "critic_example_count": critic_bench["model_example_count"],
        },
        "primehub_transfer": {
            "critic_bucket_accuracy": critic_bench["per_family"].get("primehub", {}).get("bucket_accuracy"),
            "retriever_exact_match_rate": retriever_bench["per_family"].get("primehub", {}).get("exact_match_rate"),
            "router_retrieval_only_exact_match_rate": primehub_router["retrieval_only_exact_match_rate"],
            "router_critic_gated_exact_match_rate": primehub_router["critic_gated_exact_match_rate"],
            "router_critic_gated_route_abstain_rate": primehub_router["critic_gated_route_abstain_rate"],
            "rows": primehub_router["rows"],
        },
        "artifacts": rollup,
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


def load_ledger(path: Path) -> List[Dict[str, Any]]:
    return [row for row in load_jsonl(path) if row.get("event") == "task_complete" and row.get("status") == "success"]


def ledger_index(rows: List[Dict[str, Any]]) -> Dict[tuple[str, str, str], Dict[str, Any]]:
    indexed: Dict[tuple[str, str, str], Dict[str, Any]] = {}
    for row in rows:
        key = (str(row.get("model_id") or ""), str(row.get("env_id") or ""), str(row.get("variant_id") or ""))
        indexed[key] = row
    return indexed


def summarize_live_ledgers(baseline_path: Path, mining_path: Path) -> Dict[str, Any]:
    baseline_rows = load_ledger(baseline_path)
    mining_rows = load_ledger(mining_path)
    baseline = ledger_index(baseline_rows)
    mining = ledger_index(mining_rows)

    envs_of_interest = ["psycho_bench", "boolq", "if_summarize_judge", "ascii_tree", "pydantic_adherence"]
    rows: List[Dict[str, Any]] = []
    for key in sorted(set(baseline) | set(mining)):
        model_id, env_id, variant_id = key
        if env_id not in envs_of_interest:
            continue
        base_row = baseline.get(key)
        mining_row = mining.get(key)
        rows.append(
            {
                "model_id": model_id,
                "env_id": env_id,
                "variant_id": variant_id,
                "baseline_reward": (base_row or {}).get("reward_totals", {}).get(env_id),
                "mining_reward": (mining_row or {}).get("reward_totals", {}).get(env_id),
                "reward_delta": round(
                    float((mining_row or {}).get("reward_totals", {}).get(env_id, 0.0))
                    - float((base_row or {}).get("reward_totals", {}).get(env_id, 0.0)),
                    4,
                )
                if base_row or mining_row
                else None,
                "baseline_tokens": (base_row or {}).get("run_token_total"),
                "mining_tokens": (mining_row or {}).get("run_token_total"),
                "token_delta": (
                    int((mining_row or {}).get("run_token_total", 0))
                    - int((base_row or {}).get("run_token_total", 0))
                )
                if base_row or mining_row
                else None,
                "skill_cluster": (mining_row or base_row or {}).get("skill_cluster") or "",
            }
        )

    notable = [
        row
        for row in rows
        if row["reward_delta"] not in (None, 0.0)
    ]
    absent_envs = sorted({env_id for env_id in envs_of_interest if all(row["env_id"] != env_id for row in rows)})
    return {
        "rows": rows,
        "notable_reward_changes": notable,
        "absent_envs": absent_envs,
    }


def build_markdown(
    *,
    summary: Dict[str, Any],
) -> str:
    control = summary["variants"]["control"]
    lines = [
        "# Primehub Rollup Comparison",
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
        "## Variant Results",
        "",
        "| Variant | Rows | Exact+ | Global retriever | Global gated router | Primehub retriever | Primehub gated router | Primehub abstain |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variant_name, variant in summary["variants"].items():
        merged = variant["merged_summary"]
        lines.append(
            "| "
            + " | ".join(
                [
                    variant_name,
                    str(merged["total_rows"]),
                    str(merged["bucket_counts"].get("exact_positive", 0)),
                    f"{variant['global']['retriever_exact_match_rate']:.4f}",
                    f"{variant['global']['router_critic_gated_exact_match_rate']:.4f}",
                    f"{variant['primehub_transfer']['retriever_exact_match_rate']:.4f}",
                    f"{variant['primehub_transfer']['router_critic_gated_exact_match_rate']:.4f}",
                    f"{variant['primehub_transfer']['router_critic_gated_route_abstain_rate']:.4f}",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Delta Vs Control",
            "",
            "| Variant | Global retriever | Global gated router | Primehub retriever | Primehub gated router | Primehub abstain |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for variant_name, delta in summary["control_deltas"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    variant_name,
                    f"{delta['global']['retriever_exact_match_rate']:+.4f}",
                    f"{delta['global']['router_critic_gated_exact_match_rate']:+.4f}",
                    f"{delta['primehub_transfer']['retriever_exact_match_rate']:+.4f}",
                    f"{delta['primehub_transfer']['router_critic_gated_exact_match_rate']:+.4f}",
                    f"{delta['primehub_transfer']['router_critic_gated_route_abstain_rate']:+.4f}",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Official Cycle 12 Reference",
            "",
            f"- Official router gated exact match: `{summary['official_cycle12']['router_critic_gated_exact_match_rate']:.4f}`",
            f"- Official retriever exact match: `{summary['official_cycle12']['retriever_exact_match_rate']:.4f}`",
            f"- Official critic bucket accuracy: `{summary['official_cycle12']['critic_bucket_accuracy']:.4f}`",
            "",
            "## Live Baseline vs Mining Cross-Ref",
            "",
        ]
    )
    if summary["live_crossref"]["rows"]:
        lines.extend(
            [
                "| Model | Env | Variant | Baseline reward | Mining reward | Delta | Baseline tokens | Mining tokens | Delta |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in summary["live_crossref"]["rows"]:
            baseline_reward = "n/a" if row["baseline_reward"] is None else f"{row['baseline_reward']:.4f}"
            mining_reward = "n/a" if row["mining_reward"] is None else f"{row['mining_reward']:.4f}"
            reward_delta = "n/a" if row["reward_delta"] is None else f"{row['reward_delta']:+.4f}"
            baseline_tokens = "n/a" if row["baseline_tokens"] is None else str(row["baseline_tokens"])
            mining_tokens = "n/a" if row["mining_tokens"] is None else str(row["mining_tokens"])
            token_delta = "n/a" if row["token_delta"] is None else f"{row['token_delta']:+d}"
            lines.append(
                "| "
                + " | ".join(
                    [
                        row["model_id"],
                        row["env_id"],
                        row["variant_id"],
                        baseline_reward,
                        mining_reward,
                        reward_delta,
                        baseline_tokens,
                        mining_tokens,
                        token_delta,
                    ]
                )
                + " |"
            )
    else:
        lines.append("- No overlapping live ledger rows were found for the selected envs.")

    lines.extend(
        [
            "",
            "## Readout",
            "",
            f"- Control rerun global retriever exact match is `{control['global']['retriever_exact_match_rate']:.4f}` on `{control['merged_summary']['total_rows']}` rows.",
            f"- Best global lift is `{summary['best_global_variant']}` with delta `{summary['control_deltas'][summary['best_global_variant']]['global']['retriever_exact_match_rate']:+.4f}` retriever exact match.",
            f"- Best primehub transfer lift is `{summary['best_primehub_variant']}` with delta `{summary['control_deltas'][summary['best_primehub_variant']]['primehub_transfer']['retriever_exact_match_rate']:+.4f}` retriever exact match on base `primehub` rows.",
        ]
    )
    if summary["live_crossref"]["notable_reward_changes"]:
        lines.append(
            f"- Live mining rerun still shows the only reward delta in this slice on `{summary['live_crossref']['notable_reward_changes'][0]['env_id']}` for `{summary['live_crossref']['notable_reward_changes'][0]['model_id']}`."
        )
    else:
        lines.append("- No reward changes were observed in the selected live baseline/mining ledger slice.")
    if summary["live_crossref"]["absent_envs"]:
        lines.append(
            "- No live baseline/mining rows exist yet for: "
            + ", ".join(f"`{env_id}`" for env_id in summary["live_crossref"]["absent_envs"])
            + "."
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    events_path = Path(args.events_path).resolve() if args.events_path else out_dir / "comparison.events.jsonl"
    summary_path = Path(args.summary_path).resolve() if args.summary_path else out_dir / "comparison.summary.json"

    base_corpus = Path(args.base_corpus).resolve()
    official_base_bench_dir = Path(args.official_base_bench_dir).resolve()
    structured_bundle = Path(args.structured_bundle).resolve()
    if_summarize_bundle = Path(args.if_summarize_bundle).resolve()
    baseline_ledger = Path(args.baseline_ledger).resolve()
    mining_ledger = Path(args.mining_ledger).resolve()

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
        "structured_bundle": str(structured_bundle),
        "if_summarize_bundle": str(if_summarize_bundle),
    }

    emit_event(events_path, "trainer_plan", trainer_plan=trainer_plan)

    variants = [
        ("control", [base_corpus]),
        ("control_plus_structured_map", [base_corpus, structured_bundle]),
        ("control_plus_structured_map_and_if_summarize", [base_corpus, structured_bundle, if_summarize_bundle]),
    ]

    variant_results: Dict[str, Any] = {}
    for variant_name, inputs in variants:
        variant_dir = out_dir / "variants" / variant_name
        variant_dir.mkdir(parents=True, exist_ok=True)
        merged_jsonl = variant_dir / "merged.jsonl"
        merged_summary_path = variant_dir / "merged.summary.json"

        emit_event(events_path, "variant_start", variant=variant_name, inputs=[str(path) for path in inputs])
        merge_inputs(inputs=inputs, out_jsonl=merged_jsonl, out_summary=merged_summary_path)
        emit_event(events_path, "checkpoint", variant=variant_name, checkpoint="merged", output=str(merged_jsonl))

        rollup = run_rollup(
            input_path=merged_jsonl,
            out_dir=variant_dir,
            top_k=args.top_k,
            holdout_ratio=args.holdout_ratio,
            min_supervision_weight=args.min_supervision_weight,
        )
        merged_summary = load_json(merged_summary_path)
        variant_summary = summarize_variant(merged_summary=merged_summary, rollup=rollup)
        variant_results[variant_name] = variant_summary
        write_json(variant_dir / "variant.manifest.json", variant_summary)
        emit_event(
            events_path,
            "variant_complete",
            variant=variant_name,
            total_rows=merged_summary["total_rows"],
            global_retriever_exact_match_rate=variant_summary["global"]["retriever_exact_match_rate"],
            primehub_retriever_exact_match_rate=variant_summary["primehub_transfer"]["retriever_exact_match_rate"],
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
    for variant_name, variant_summary in variant_results.items():
        if variant_name == "control":
            continue
        control_deltas[variant_name] = {
            "global": metric_delta(variant_summary["global"], control["global"], delta_keys),
            "primehub_transfer": metric_delta(variant_summary["primehub_transfer"], control["primehub_transfer"], delta_keys),
        }

    best_global_variant = max(
        control_deltas,
        key=lambda item: control_deltas[item]["global"]["retriever_exact_match_rate"],
    )
    best_primehub_variant = max(
        control_deltas,
        key=lambda item: control_deltas[item]["primehub_transfer"]["retriever_exact_match_rate"],
    )

    official_cycle12 = {
        "critic_bucket_accuracy": load_json(official_base_bench_dir / "trm_critic_bench.summary.json")["bucket_accuracy"],
        "retriever_exact_match_rate": load_json(official_base_bench_dir / "trm_retriever_bench.summary.json")["exact_match_rate"],
        "router_critic_gated_exact_match_rate": load_json(official_base_bench_dir / "trm_router_bench.summary.json")["critic_gated"]["exact_match_rate"],
    }
    live_crossref = summarize_live_ledgers(baseline_ledger, mining_ledger)

    summary = {
        "generated_at_utc": utc_now(),
        "trainer_plan": trainer_plan,
        "variants": variant_results,
        "control_deltas": control_deltas,
        "best_global_variant": best_global_variant,
        "best_primehub_variant": best_primehub_variant,
        "official_cycle12": official_cycle12,
        "live_crossref": live_crossref,
    }

    write_json(summary_path, summary)
    write_markdown(out_dir / "comparison.findings.md", build_markdown(summary=summary))
    emit_event(events_path, "done", summary_path=str(summary_path))
    print(str(summary_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
