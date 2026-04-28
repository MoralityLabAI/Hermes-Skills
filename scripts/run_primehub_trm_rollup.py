from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
HARNESS_ROOT = Path(r"C:/projects/trm_observability_harness")
DEFAULT_RUN_ROOTS = [
    ROOT / "data" / "primehub_eligible_benchmark_v1",
    ROOT / "data" / "primehub_eligible_benchmark_v1_retry_27b_tail",
]


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


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
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def run(cmd: List[str], *, cwd: Path) -> None:
    subprocess.run(cmd, cwd=str(cwd), check=True)


def discover_replays(run_roots: List[Path], model_dirs: List[str]) -> List[Path]:
    files: List[Path] = []
    seen = set()
    wanted = {item.strip().lower() for item in model_dirs if item.strip()}
    for run_root in run_roots:
        if not run_root.exists():
            continue
        for path in sorted(run_root.rglob("*.jsonl")):
            parent_name = path.parent.name.lower()
            if not parent_name.startswith("qwen35_"):
                continue
            if wanted and parent_name not in wanted:
                continue
            key = str(path.resolve()).lower()
            if key not in seen:
                seen.add(key)
                files.append(path.resolve())
    return files


def stage_one_replay(
    replay_path: Path,
    stage_dir: Path,
    *,
    impute_exact_positive_target_action: bool,
) -> Dict[str, Any]:
    stem = replay_path.stem
    trm_path = stage_dir / f"{stem}.trm.jsonl"
    summary_path = stage_dir / f"{stem}.trm.summary.json"
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "build_trm_train_rows.py"),
            "--input",
            str(replay_path),
            "--output",
            str(trm_path),
            "--summary",
            str(summary_path),
        ],
        cwd=ROOT,
    )
    rows = load_jsonl(trm_path)
    imputed = 0
    if impute_exact_positive_target_action:
        for row in rows:
            if row.get("target_action"):
                continue
            if str(row.get("bucket") or "") != "exact_positive":
                continue
            model_action = str(row.get("model_action") or "").strip()
            if not model_action:
                continue
            row["target_action"] = model_action
            meta = row.setdefault("meta", {})
            if isinstance(meta, dict):
                meta["target_action_source"] = "model_action_exact_positive_imputation"
            imputed += 1
    if imputed:
        write_jsonl(trm_path, rows)
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["target_action_imputed_rows"] = imputed
        write_json(summary_path, summary)

    bucket_counts = Counter(str(row.get("bucket") or "unknown") for row in rows)
    target_action_rows = sum(1 for row in rows if row.get("target_action"))
    return {
        "input_replay": str(replay_path),
        "staged_trm": str(trm_path),
        "staged_summary": str(summary_path),
        "rows": len(rows),
        "bucket_counts": dict(bucket_counts),
        "target_action_rows": target_action_rows,
        "target_action_imputed_rows": imputed,
        "model_dir": replay_path.parent.name,
    }


def merge_stage_inputs(input_paths: List[Path], merged_jsonl: Path, merged_summary: Path, min_exact_positives_per_family: int) -> None:
    cmd = [
        sys.executable,
        str(HARNESS_ROOT / "scripts" / "merge_trm_train_rows.py"),
        "--input",
        str(input_paths[0]),
        "--output",
        str(merged_jsonl),
        "--summary",
        str(merged_summary),
        "--min-exact-positives-per-family",
        str(min_exact_positives_per_family),
    ]
    for extra in input_paths[1:]:
        cmd.extend(["--input", str(extra)])
    run(cmd, cwd=ROOT)


def train_and_bench(work_dir: Path, merged_jsonl: Path, *, top_k: int, holdout_ratio: float, min_supervision_weight: float) -> Dict[str, str]:
    model_dir = work_dir / "models"
    bench_dir = work_dir / "bench"
    model_dir.mkdir(parents=True, exist_ok=True)
    bench_dir.mkdir(parents=True, exist_ok=True)

    critic_model = model_dir / "trm_critic.json"
    critic_summary = model_dir / "trm_critic.summary.json"
    critic_bench_summary = bench_dir / "trm_critic_bench.summary.json"
    critic_bench_predictions = bench_dir / "trm_critic_bench.jsonl"

    retriever_model = model_dir / "trm_retriever.json"
    retriever_summary = model_dir / "trm_retriever.summary.json"
    retriever_bench_summary = bench_dir / "trm_retriever_bench.summary.json"
    retriever_bench_predictions = bench_dir / "trm_retriever_bench.jsonl"

    router_bench_summary = bench_dir / "trm_router_bench.summary.json"
    router_bench_predictions = bench_dir / "trm_router_bench.jsonl"

    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "train_trm_critic.py"),
            "--input",
            str(merged_jsonl),
            "--output",
            str(critic_model),
            "--summary",
            str(critic_summary),
            "--k",
            str(top_k),
        ],
        cwd=ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "bench_trm_critic.py"),
            "--input",
            str(merged_jsonl),
            "--summary",
            str(critic_bench_summary),
            "--predictions",
            str(critic_bench_predictions),
            "--holdout-ratio",
            str(holdout_ratio),
            "--k",
            str(top_k),
        ],
        cwd=ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "train_trm_retriever.py"),
            "--input",
            str(merged_jsonl),
            "--output",
            str(retriever_model),
            "--summary",
            str(retriever_summary),
            "--min-supervision-weight",
            str(min_supervision_weight),
        ],
        cwd=ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "bench_trm_retriever.py"),
            "--input",
            str(merged_jsonl),
            "--summary",
            str(retriever_bench_summary),
            "--predictions",
            str(retriever_bench_predictions),
            "--holdout-ratio",
            str(holdout_ratio),
            "--min-supervision-weight",
            str(min_supervision_weight),
        ],
        cwd=ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "bench_trm_router.py"),
            "--input",
            str(merged_jsonl),
            "--summary",
            str(router_bench_summary),
            "--predictions",
            str(router_bench_predictions),
            "--holdout-ratio",
            str(holdout_ratio),
            "--top-k",
            str(top_k),
            "--min-supervision-weight",
            str(min_supervision_weight),
        ],
        cwd=ROOT,
    )
    return {
        "critic_model": str(critic_model),
        "critic_summary": str(critic_summary),
        "critic_bench_summary": str(critic_bench_summary),
        "retriever_model": str(retriever_model),
        "retriever_summary": str(retriever_summary),
        "retriever_bench_summary": str(retriever_bench_summary),
        "router_bench_summary": str(router_bench_summary),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage Prime-env benchmark replays into a TRM training/benchmark corpus.")
    parser.add_argument(
        "--run-root",
        action="append",
        dest="run_roots",
        default=[],
        help="Benchmark run root to scan. Repeat to include multiple roots.",
    )
    parser.add_argument(
        "--model-dir",
        action="append",
        dest="model_dirs",
        default=[],
        help="Optional replay subdir filter such as qwen35_9b or qwen35_27b. Repeatable.",
    )
    parser.add_argument(
        "--work-dir",
        default=str(ROOT / "data" / "primehub_trm_rollup" / now_stamp()),
        help="Output working directory.",
    )
    parser.add_argument("--min-exact-positives-per-family", type=int, default=2)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--holdout-ratio", type=float, default=0.2)
    parser.add_argument("--min-supervision-weight", type=float, default=0.4)
    parser.add_argument(
        "--no-impute-target-action",
        action="store_true",
        help="Do not set target_action=model_action for exact_positive rows that lack a gold target.",
    )
    parser.add_argument(
        "--stage-only",
        action="store_true",
        help="Only stage and merge the corpus; skip train/bench runs.",
    )
    args = parser.parse_args()

    run_roots = [Path(item).resolve() for item in (args.run_roots or [str(path) for path in DEFAULT_RUN_ROOTS])]
    work_dir = Path(args.work_dir).resolve()
    stage_dir = work_dir / "stage"
    stage_dir.mkdir(parents=True, exist_ok=True)

    replays = discover_replays(run_roots, args.model_dirs)
    if not replays:
        raise SystemExit("No Prime benchmark replay JSONL files found.")

    staged: List[Dict[str, Any]] = []
    for replay_path in replays:
        staged.append(
            stage_one_replay(
                replay_path,
                stage_dir,
                impute_exact_positive_target_action=not args.no_impute_target_action,
            )
        )

    merged_jsonl = work_dir / "primehub_trm_merged.jsonl"
    merged_summary = work_dir / "primehub_trm_merged.summary.json"
    merge_stage_inputs(
        [Path(item["staged_trm"]) for item in staged],
        merged_jsonl,
        merged_summary,
        args.min_exact_positives_per_family,
    )

    merged_rows = load_jsonl(merged_jsonl)
    merged_bucket_counts = Counter(str(row.get("bucket") or "unknown") for row in merged_rows)
    merged_target_action_rows = sum(1 for row in merged_rows if row.get("target_action"))
    manifest: Dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "run_roots": [str(path) for path in run_roots],
        "model_dirs": args.model_dirs,
        "replays_found": len(replays),
        "staged_sources": staged,
        "merged": {
            "jsonl": str(merged_jsonl),
            "summary": str(merged_summary),
            "rows": len(merged_rows),
            "bucket_counts": dict(merged_bucket_counts),
            "target_action_rows": merged_target_action_rows,
            "target_action_coverage": round(merged_target_action_rows / len(merged_rows), 4) if merged_rows else 0.0,
        },
        "impute_exact_positive_target_action": not args.no_impute_target_action,
    }

    if not args.stage_only:
        manifest["train_bench"] = train_and_bench(
            work_dir,
            merged_jsonl,
            top_k=args.top_k,
            holdout_ratio=args.holdout_ratio,
            min_supervision_weight=args.min_supervision_weight,
        )

    manifest_path = work_dir / "primehub_trm_rollup.manifest.json"
    write_json(manifest_path, manifest)
    print(json.dumps({"manifest": str(manifest_path), "merged_rows": len(merged_rows), "bucket_counts": dict(merged_bucket_counts)}, indent=2))


if __name__ == "__main__":
    main()
