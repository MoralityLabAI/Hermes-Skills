#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tail a named TRM bench run.")
    parser.add_argument("--run-dir", required=True, help="Run directory to watch.")
    parser.add_argument("--interval", type=float, default=2.0, help="Polling interval in seconds.")
    parser.add_argument("--once", action="store_true", help="Render once and exit.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    watcher = skill_root / "scripts" / "watch_trm_routerbench.py"
    cmd = [
        sys.executable,
        str(watcher),
        "--run-dir",
        args.run_dir,
        "--interval",
        str(args.interval),
    ]
    if args.once:
        cmd.append("--once")
    return int(subprocess.call(cmd, cwd=str(skill_root)))


if __name__ == "__main__":
    raise SystemExit(main())
