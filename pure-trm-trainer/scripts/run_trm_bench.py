#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict


BENCHES: Dict[str, Path] = {
    "routerbench": Path(__file__).resolve().parents[1] / "references" / "routerbench-spec.json",
    "primehub-envs": Path(__file__).resolve().parents[1] / "references" / "primehub-envs-bench.json",
    "primehub-baseline": Path(__file__).resolve().parents[1] / "references" / "primehub-baseline-bench.json",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a named TRM bench from the pure-trm-trainer skill.")
    parser.add_argument("--bench", required=True, choices=sorted(BENCHES.keys()), help="Named bench to launch.")
    parser.add_argument("--run-id", default="", help="Optional run id override.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve the bench config and print the path without launching.")
    parser.add_argument("--template-root", default="", help="Optional trainer template root override.")
    parser.add_argument("--corpus-spec", default="", help="Optional corpus spec override.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    spec_path = BENCHES[args.bench]
    runner = skill_root / "scripts" / "run_trm_routerbench.py"
    cmd = [
        sys.executable,
        str(runner),
        "--config",
        str(spec_path),
    ]
    if args.run_id:
        cmd += ["--run-id", args.run_id]
    if args.template_root:
        cmd += ["--template-root", args.template_root]
    if args.corpus_spec:
        cmd += ["--corpus-spec", args.corpus_spec]
    if args.dry_run:
        cmd += ["--dry-run"]
    return int(subprocess.call(cmd, cwd=str(skill_root)))


if __name__ == "__main__":
    raise SystemExit(main())
