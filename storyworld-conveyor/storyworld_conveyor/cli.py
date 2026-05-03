from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import (
    init_run,
    load_config,
    run_aggregator,
    run_build_encounters,
    run_completions,
    run_env_grader,
    run_export_training,
    run_llm_judge,
    run_pipeline,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Storyworld conveyor scaffold CLI")
    parser.add_argument("--config", required=True, help="Path to pipeline config JSON")
    parser.add_argument("--run-root", default=None, help="Artifact root; defaults to config artifact_root")
    parser.add_argument("--run-id", default=None, help="Optional fixed run id")
    parser.add_argument("--force", action="store_true", help="Rerun stage even if manifest says completed")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in [
        "build-encounters",
        "run-completions",
        "grade-env",
        "judge-llm",
        "aggregate",
        "export-training",
        "run-pipeline",
    ]:
        cmd = sub.add_parser(name)
        if name == "run-pipeline":
            cmd.add_argument(
                "--stop-after",
                choices=[
                    "encounter_builder",
                    "completion_runner",
                    "env_grader",
                    "llm_judge",
                    "aggregator",
                    "trainer_export",
                ],
            )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(Path(args.config))
    run_root = Path(args.run_root or config["artifact_root"])
    run_id, run_dir = init_run(config, run_root, args.run_id)
    if args.command == "build-encounters":
        output = run_build_encounters(run_dir, run_id, config, force=args.force)
    elif args.command == "run-completions":
        output = run_completions(run_dir, run_id, config, force=args.force)
    elif args.command == "grade-env":
        output = run_env_grader(run_dir, run_id, config, force=args.force)
    elif args.command == "judge-llm":
        output = run_llm_judge(run_dir, run_id, config, force=args.force)
    elif args.command == "aggregate":
        output = run_aggregator(run_dir, run_id, config, force=args.force)
    elif args.command == "export-training":
        output = run_export_training(run_dir, run_id, config, force=args.force)
    else:
        output = run_pipeline(config, run_root, run_id, force=args.force, stop_after=args.stop_after)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
