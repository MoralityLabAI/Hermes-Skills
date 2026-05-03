from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storyworld_conveyor.factory import load_factory_config, run_factory  # noqa: E402


def tail_lines(path: Path, count: int) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-count:]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a factory config repeatedly and print real stage/log checkpoints.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--run-root", default=None)
    parser.add_argument("--run-id-prefix", required=True)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--tail-lines", type=int, default=6)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--stop-after", default=None)
    args = parser.parse_args()

    config = load_factory_config(Path(args.config))
    run_root = Path(args.run_root or config["artifact_root"])
    for index in range(1, args.iterations + 1):
        run_id = f"{args.run_id_prefix}_{index:03d}"
        print(f"[grind] start iteration={index}/{args.iterations} run_id={run_id}")
        run_dir = run_factory(config, run_root, run_id=run_id, force=args.force, stop_after=args.stop_after)
        print(f"[grind] run_dir={run_dir}")
        for stage in config["stages"]:
            stage_dir = run_dir / stage["name"]
            manifest_path = stage_dir / "manifest.json"
            stdout_path = stage_dir / "stdout.log"
            if not manifest_path.exists():
                print(f"[stage] name={stage['name']} status=not_started")
                continue
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            print(f"[stage] name={stage['name']} status={manifest.get('status')} manifest={manifest_path}")
            for line in tail_lines(stdout_path, args.tail_lines):
                print(f"[tail] {line}")
        print(f"[grind] end iteration={index}/{args.iterations} run_id={run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
