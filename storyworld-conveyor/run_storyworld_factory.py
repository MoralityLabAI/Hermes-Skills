from pathlib import Path
import sys
import argparse


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storyworld_conveyor.factory import load_factory_config, run_factory  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run storyworld factory stages with manifests")
    parser.add_argument("--config", required=True)
    parser.add_argument("--run-root", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--stop-after", default=None)
    args = parser.parse_args()
    config = load_factory_config(Path(args.config))
    run_root = Path(args.run_root or config["artifact_root"])
    output = run_factory(config, run_root, run_id=args.run_id, force=args.force, stop_after=args.stop_after)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
