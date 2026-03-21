from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from primelab_hermes.hosted_training import load_receipt, render_run_comparison


def _resolve_receipts(repo_root: Path) -> list[Path]:
    runs_root = repo_root / "runs" / "hosted_training"
    if not runs_root.exists():
        return []
    return sorted(runs_root.glob("*/receipt.json"))


def main() -> int:
    ap = argparse.ArgumentParser(description="List and compare saved Prime hosted training receipts.")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--compare", nargs="*", default=[])
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    receipt_paths = _resolve_receipts(repo_root)
    if not receipt_paths:
        raise SystemExit("No hosted run receipts found under runs/hosted_training")

    receipts = [load_receipt(path) for path in receipt_paths]
    by_id = {receipt["run_id"]: receipt for receipt in receipts}

    if args.compare:
        missing = [run_id for run_id in args.compare if run_id not in by_id]
        if missing:
            raise SystemExit(f"Unknown run ids: {', '.join(missing)}")
        selected = [by_id[run_id] for run_id in args.compare]
        print(render_run_comparison(selected))
        return 0

    print(render_run_comparison(receipts))
    print()
    print("Use --compare <run_id> <run_id> ... to narrow the table.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
