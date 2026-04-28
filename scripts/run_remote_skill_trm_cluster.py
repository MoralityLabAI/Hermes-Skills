from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parent
SCRIPTS_ROOT = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.trm_retrieval import load_jsonl, stable_holdout_bucket


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run(cmd: List[str]) -> None:
    subprocess.run(cmd, cwd=str(ROOT), check=True)


def effective_holdout_ratio(input_path: str, requested_ratio: float) -> float:
    rows = load_jsonl(Path(input_path))
    if len(rows) <= 1:
        return 0.0
    target_eval = max(1, min(len(rows) - 1, round(len(rows) * requested_ratio)))
    values = sorted(stable_holdout_bucket(row) for row in rows)
    chosen = values[target_eval - 1]
    return min(chosen + 1e-9, 0.999999999)


def main() -> None:
    parser = argparse.ArgumentParser(description="Remote runner for one specialist TRM cluster.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--holdout-ratio", type=float, default=0.2)
    parser.add_argument("--min-supervision-weight", type=float, default=0.4)
    parser.add_argument("--cluster-id", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    model_dir = out_dir / "models"
    bench_dir = out_dir / "bench"
    model_dir.mkdir(parents=True, exist_ok=True)
    bench_dir.mkdir(parents=True, exist_ok=True)
    bench_holdout_ratio = effective_holdout_ratio(args.input, args.holdout_ratio)

    run(
        [
            sys.executable,
            str(SCRIPTS_ROOT / "train_trm_critic.py"),
            "--input",
            args.input,
            "--output",
            str(model_dir / "trm_critic.json"),
            "--summary",
            str(model_dir / "trm_critic.summary.json"),
            "--k",
            str(args.top_k),
        ]
    )
    run(
        [
            sys.executable,
            str(SCRIPTS_ROOT / "bench_trm_critic.py"),
            "--input",
            args.input,
            "--summary",
            str(bench_dir / "trm_critic_bench.summary.json"),
            "--predictions",
            str(bench_dir / "trm_critic_bench.jsonl"),
            "--holdout-ratio",
            str(bench_holdout_ratio),
            "--k",
            str(args.top_k),
        ]
    )
    run(
        [
            sys.executable,
            str(SCRIPTS_ROOT / "train_trm_retriever.py"),
            "--input",
            args.input,
            "--output",
            str(model_dir / "trm_retriever.json"),
            "--summary",
            str(model_dir / "trm_retriever.summary.json"),
            "--min-supervision-weight",
            str(args.min_supervision_weight),
        ]
    )
    run(
        [
            sys.executable,
            str(SCRIPTS_ROOT / "bench_trm_retriever.py"),
            "--input",
            args.input,
            "--summary",
            str(bench_dir / "trm_retriever_bench.summary.json"),
            "--predictions",
            str(bench_dir / "trm_retriever_bench.jsonl"),
            "--holdout-ratio",
            str(bench_holdout_ratio),
            "--min-supervision-weight",
            str(args.min_supervision_weight),
        ]
    )
    run(
        [
            sys.executable,
            str(SCRIPTS_ROOT / "bench_trm_router.py"),
            "--input",
            args.input,
            "--summary",
            str(bench_dir / "trm_router_bench.summary.json"),
            "--predictions",
            str(bench_dir / "trm_router_bench.jsonl"),
            "--holdout-ratio",
            str(bench_holdout_ratio),
            "--top-k",
            str(args.top_k),
            "--min-supervision-weight",
            str(args.min_supervision_weight),
        ]
    )

    summary = {
        "cluster_id": args.cluster_id,
        "input": args.input,
        "out_dir": str(out_dir),
        "top_k": args.top_k,
        "holdout_ratio": args.holdout_ratio,
        "bench_holdout_ratio": bench_holdout_ratio,
        "min_supervision_weight": args.min_supervision_weight,
        "critic_train": load_json(model_dir / "trm_critic.summary.json"),
        "critic_bench": load_json(bench_dir / "trm_critic_bench.summary.json"),
        "retriever_train": load_json(model_dir / "trm_retriever.summary.json"),
        "retriever_bench": load_json(bench_dir / "trm_retriever_bench.summary.json"),
        "router_bench": load_json(bench_dir / "trm_router_bench.summary.json"),
    }
    write_json(out_dir / "cluster_training.summary.json", summary)
    print(str((out_dir / "cluster_training.summary.json").resolve()))


if __name__ == "__main__":
    main()
