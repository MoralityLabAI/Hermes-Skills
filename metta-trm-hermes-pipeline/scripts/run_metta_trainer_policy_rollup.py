from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PIPELINE_ROOT.parents[0]
HARNESS_ROOT = Path(r"C:/projects/trm_observability_harness")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train and bench the local TRM harness on a MeTTa trainer-policy bundle.")
    parser.add_argument("--input", required=True, help="Input metta_trainer_policy_bundle.jsonl path.")
    parser.add_argument("--out-dir", required=True, help="Output directory for models and bench summaries.")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--holdout-ratio", type=float, default=0.2)
    parser.add_argument("--min-supervision-weight", type=float, default=0.25)
    return parser.parse_args()


def run(cmd: List[str], *, cwd: Path) -> None:
    subprocess.run(cmd, cwd=str(cwd), check=True)


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    out_dir = Path(args.out_dir).resolve()
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
            str(args.top_k),
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
            str(args.holdout_ratio),
            "--k",
            str(args.top_k),
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
            str(args.min_supervision_weight),
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
            str(args.holdout_ratio),
            "--min-supervision-weight",
            str(args.min_supervision_weight),
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
            str(args.holdout_ratio),
            "--top-k",
            str(args.top_k),
            "--min-supervision-weight",
            str(args.min_supervision_weight),
        ],
        cwd=REPO_ROOT,
    )

    manifest = {
        "input": str(input_path),
        "out_dir": str(out_dir),
        "top_k": args.top_k,
        "holdout_ratio": args.holdout_ratio,
        "min_supervision_weight": args.min_supervision_weight,
        "critic_summary": load_json(critic_summary),
        "critic_bench_summary": load_json(critic_bench_summary),
        "retriever_summary": load_json(retriever_summary),
        "retriever_bench_summary": load_json(retriever_bench_summary),
        "router_bench_summary": load_json(router_bench_summary),
    }
    manifest_path = out_dir / "metta_trainer_policy_rollup.manifest.json"
    write_json(manifest_path, manifest)

    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
