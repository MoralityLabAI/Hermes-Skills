from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from primelab_hermes.hosted_training import parse_hosted_log, render_run_summary, save_receipt


def _default_runs_root(repo_root: Path) -> Path:
    return repo_root / "runs" / "hosted_training"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _fetch_logs(run_id: str, repo_root: Path, tail: int) -> str:
    if os.name == "nt":
        repo_posix = repo_root.as_posix().replace("C:", "/mnt/c")
        cmd = [
            "bash",
            "-lc",
            f"cd {shlex.quote(repo_posix)} && prime rl logs {shlex.quote(run_id)} --tail {tail}",
        ]
    else:
        cmd = ["prime", "rl", "logs", run_id, "--tail", str(tail)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


def main() -> int:
    ap = argparse.ArgumentParser(description="Capture a Prime hosted training run into a local receipt.")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--tail", type=int, default=4000)
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--config")
    ap.add_argument("--log-file")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    runs_root = _default_runs_root(repo_root)
    run_root = runs_root / args.run_id
    run_root.mkdir(parents=True, exist_ok=True)

    if args.log_file:
        log_text = _read_text(Path(args.log_file))
    else:
        log_text = _fetch_logs(args.run_id, repo_root, args.tail)

    raw_log_path = run_root / "prime_rl.log"
    raw_log_path.write_text(log_text, encoding="utf-8")

    payload = {
        "run_id": args.run_id,
        "dashboard_url": f"https://app.primeintellect.ai/dashboard/training/{args.run_id}",
        "config_path": str(Path(args.config).resolve()) if args.config else None,
        "model": None,
        "summary": parse_hosted_log(log_text),
    }
    payload["model"] = payload["summary"].get("model")

    if args.config:
        config_text = _read_text(Path(args.config))
        (run_root / "config.toml").write_text(config_text, encoding="utf-8")

    receipt_path = save_receipt(run_root, payload)
    print(render_run_summary(payload))
    print()
    print(json.dumps({"receipt": str(receipt_path), "log": str(raw_log_path)}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
