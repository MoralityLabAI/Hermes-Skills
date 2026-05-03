from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_ARTIFACT_ROOT = "C:/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/factory_runs"
DEFAULT_REPO_ROOT = "C:/projects/GPTStoryworld"
DEFAULT_STORYWORLD_SCRIPTS = "C:/projects/GPTStoryworld/codex-skills/storyworld-building/scripts"
DEFAULT_SMALL_BUILDER_SCRIPTS = "C:/projects/GPTStoryworld/codex-skills/small-storyworld-builder/scripts"


def parse_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def catalog() -> Dict[str, Any]:
    return {
        "version": 1,
        "templates": [
            {
                "id": "fresh_seed_artistry",
                "description": "Fresh build from a validated base world through seed, spool, artistry, validation, quality gate, and SWMD-min export.",
                "required_args": ["--base-world", "--out-config", "--title", "--about", "--motif"],
                "supports": [
                    "--target-encounters",
                    "--characters",
                    "--ending-count",
                    "--secret-ending-count",
                    "--super-secret-count",
                    "--avg-options",
                    "--avg-reactions",
                    "--avg-effects",
                    "--gate-pct",
                    "--include-monte-carlo",
                    "--include-encounter-index",
                ],
            },
            {
                "id": "balanced_secret_topology",
                "description": "Fresh build plus path probing, Monte Carlo, reachability rebalance, and optional QLoRA export.",
                "required_args": ["--base-world", "--out-config", "--title", "--about", "--motif"],
                "supports": [
                    "--target-encounters",
                    "--characters",
                    "--ending-count",
                    "--secret-ending-count",
                    "--super-secret-count",
                    "--avg-options",
                    "--avg-reactions",
                    "--avg-effects",
                    "--gate-pct",
                    "--mc-runs",
                    "--probe-runs",
                    "--include-qlora",
                ],
            },
            {
                "id": "desirability_grind",
                "description": "Rewrite desirability/effect scripts across an already-built world and run quality checks.",
                "required_args": ["--base-world", "--out-config"],
                "supports": [
                    "--characters",
                    "--ending-count",
                    "--secret-ending-count",
                    "--super-secret-count",
                    "--avg-options",
                    "--avg-reactions",
                    "--avg-effects",
                    "--include-monte-carlo",
                ],
            },
        ],
    }


def base_config(args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "artifact_root": args.artifact_root,
        "run_id": args.run_id or "storyworld_factory_run",
        "base_world": args.base_world,
        "paths": {
            "repo_root": args.repo_root,
            "python_bin": args.python_bin,
            "storyworld_scripts": args.storyworld_scripts,
            "small_builder_scripts": args.small_builder_scripts,
        },
        "story_brief": {
            "title": args.title,
            "about": args.about,
            "motif": args.motif,
            "theme": args.theme,
            "genre": args.genre,
            "characters": parse_csv(args.characters),
        },
        "design_targets": {
            "target_encounters": args.target_encounters,
            "ending_count": args.ending_count,
            "secret_ending_count": args.secret_ending_count,
            "super_secret_count": args.super_secret_count,
            "avg_options_per_encounter": args.avg_options,
            "avg_reactions_per_option": args.avg_reactions,
            "avg_effects_per_reaction": args.avg_effects,
        },
    }


def fresh_seed_artistry(args: argparse.Namespace) -> Dict[str, Any]:
    config = base_config(args)
    config["artifacts"] = {
        "seed_world": "{out_dir}/seed_world.json",
        "spooled_world": "{out_dir}/spooled_world.json",
        "artistry_world": "{out_dir}/artistry_world.json",
        "quality_report": "{report_dir}/quality_gate.json",
        "swmd_min": "{out_dir}/storyworld.swmd.min.md",
        "encounter_index_dir": "{index_dir}/encounter_index",
        "paths_report": "{report_dir}/multiple_paths.txt",
        "mc_report": "{report_dir}/monte_carlo.txt",
    }
    seed_command = [
        "{python_bin}",
        "{storyworld_scripts}/one_shot_factory.py",
        "--base",
        "{base_world}",
        "--out",
        "{seed_world}",
        "--target-encounters",
        str(args.target_encounters),
        "--title",
        args.title,
        "--about",
        args.about,
        "--motif",
        args.motif,
    ]
    if str(args.base_world).startswith("fresh:"):
        seed_command = [
            "{python_bin}",
            "{storyworld_scripts}/fresh_storyworld_seed.py",
            "--slug",
            str(args.base_world).split(":", 1)[1],
            "--out",
            "{seed_world}",
            "--target-encounters",
            str(args.target_encounters),
            "--title",
            args.title,
            "--about",
            args.about,
            "--motif",
            args.motif,
        ]
    stages: List[Dict[str, Any]] = [
        {
            "name": "seed_world",
            "command": seed_command,
            "outputs": ["{seed_world}"],
        },
        {
            "name": "validate_seed",
            "command": [
                "{python_bin}",
                "{storyworld_scripts}/sweepweave_validator.py",
                "validate",
                "{seed_world}",
            ],
            "outputs": ["{seed_world}"],
        },
        {
            "name": "materialize_spools",
            "command": [
                "{python_bin}",
                "{storyworld_scripts}/materialize_spools.py",
                "{seed_world}",
                "{spooled_world}",
            ],
            "outputs": ["{spooled_world}"],
        },
        {
            "name": "sequence_spools",
            "command": [
                "{python_bin}",
                "{storyworld_scripts}/spool_sequencing.py",
                "{spooled_world}",
            ],
            "outputs": ["{spooled_world}"],
        },
        {
            "name": "apply_artistry",
            "command": [
                "{python_bin}",
                "{storyworld_scripts}/apply_artistry_pass.py",
                "--in-json",
                "{spooled_world}",
                "--out-json",
                "{artistry_world}",
                "--gate-pct",
                str(args.gate_pct),
            ],
            "outputs": ["{artistry_world}"],
        },
        {
            "name": "validate_artistry",
            "command": [
                "{python_bin}",
                "{storyworld_scripts}/sweepweave_validator.py",
                "validate",
                "{artistry_world}",
            ],
            "outputs": ["{artistry_world}"],
        },
        {
            "name": "quality_gate",
            "command": [
                "{python_bin}",
                "{storyworld_scripts}/storyworld_quality_gate.py",
                "--storyworld",
                "{artistry_world}",
                "--strict",
                "--report-out",
                "{quality_report}",
            ],
            "outputs": ["{quality_report}"],
            "continue_on_failure": True,
        },
        {
            "name": "export_swmd_min",
            "command": [
                "{python_bin}",
                "{storyworld_scripts}/json_to_swmd.py",
                "{artistry_world}",
                "{swmd_min}",
                "--mode",
                "minified",
            ],
            "outputs": ["{swmd_min}"],
        },
    ]
    if args.include_encounter_index:
        stages.append(
            {
                "name": "build_encounter_index",
                "command": [
                    "{python_bin}",
                    "{small_builder_scripts}/swmd_encounter_index.py",
                    "--swmd",
                    "{swmd_min}",
                    "--out-dir",
                    "{encounter_index_dir}",
                ],
                "outputs": ["{encounter_index_dir}"],
            }
        )
    if args.include_monte_carlo:
        stages.extend(
            [
                {
                    "name": "multiple_paths_probe",
                    "command": [
                        "{python_bin}",
                        "{storyworld_scripts}/multiple_paths.py",
                        "--runs",
                        str(args.probe_runs),
                        "--seed",
                        str(args.seed),
                        "{artistry_world}",
                    ],
                    "outputs": ["{paths_report}"],
                    "stdout_to": "{paths_report}",
                    "continue_on_failure": True,
                },
                {
                    "name": "monte_carlo_baseline",
                    "command": [
                        "{python_bin}",
                        "{storyworld_scripts}/monte_carlo_rehearsal.py",
                        "{artistry_world}",
                        "--runs",
                        str(args.mc_runs),
                        "--seed",
                        str(args.seed),
                    ],
                    "outputs": ["{mc_report}"],
                    "stdout_to": "{mc_report}",
                    "continue_on_failure": True,
                },
            ]
        )
    config["stages"] = stages
    return config


def balanced_secret_topology(args: argparse.Namespace) -> Dict[str, Any]:
    config = fresh_seed_artistry(args)
    config["artifacts"]["qlora_out_dir"] = "{qlora_dir}/examples"
    stages: List[Dict[str, Any]] = []
    for stage in config["stages"]:
        stages.append(stage)
        if stage["name"] == "validate_artistry":
            stages.extend(
                [
                    {
                        "name": "secret_gate_audit",
                        "command": [
                            "{python_bin}",
                            "{storyworld_scripts}/secret_endings_gates.py",
                            "--min-effects",
                            "3",
                            "--min-reactions",
                            "2",
                            "--min-options",
                            "2",
                            "--min-threshold",
                            "0.03",
                            "{artistry_world}",
                        ],
                        "outputs": ["{artistry_world}"],
                        "continue_on_failure": True,
                    },
                    {
                        "name": "ending_reachability_balance",
                        "command": [
                            "{python_bin}",
                            "{storyworld_scripts}/ending_reachability_balance.py",
                            "--runs",
                            str(max(200, args.mc_runs // 2)),
                            "--seed",
                            str(args.seed),
                            "--bias",
                            "0.06",
                            "--warped-min",
                            "0.92",
                            "--apply",
                            "{artistry_world}",
                        ],
                        "outputs": ["{artistry_world}"],
                        "continue_on_failure": True,
                    },
                ]
            )
        if stage["name"] == "export_swmd_min" and args.include_qlora:
            stages.append(
                {
                    "name": "build_qlora_examples",
                    "command": [
                        "{python_bin}",
                        "{small_builder_scripts}/swmd_build_qlora_examples.py",
                        "--swmd-glob",
                        "{swmd_min}",
                        "--out-dir",
                        "{qlora_out_dir}",
                        "--max-total-encounters",
                        str(max(args.target_encounters, 40)),
                        "--examples-per-encounter",
                        "4",
                        "--val-ratio",
                        "0.05",
                    ],
                    "outputs": ["{qlora_out_dir}"],
                    "continue_on_failure": True,
                }
            )
    config["stages"] = stages
    return config


def desirability_grind(args: argparse.Namespace) -> Dict[str, Any]:
    config = base_config(args)
    config["artifacts"] = {
        "rewritten_world": "{out_dir}/storyworld_v2.json",
        "reinforced_world": "{out_dir}/storyworld_v3.json",
        "desirability_report": "{report_dir}/desirability_rewrite_report.json",
        "quality_report": "{report_dir}/quality_gate_v2.json",
        "swmd_min": "{out_dir}/storyworld_v3.swmd.min.md",
        "mc_report": "{report_dir}/monte_carlo.txt",
    }
    stages: List[Dict[str, Any]] = [
        {
            "name": "rewrite_desirability",
            "command": [
                "{python_bin}",
                "{storyworld_scripts}/systematic_desirability_rewrite.py",
                "{base_world}",
                "--out-json",
                "{rewritten_world}",
                "--report-out",
                "{desirability_report}",
            ],
            "outputs": ["{rewritten_world}", "{desirability_report}"],
        },
        {
            "name": "reinforce_super_secret",
            "command": [
                "{python_bin}",
                "{storyworld_scripts}/reinforce_super_secret_route.py",
                "{rewritten_world}",
                "--out-json",
                "{reinforced_world}",
                "--anchor-id",
                "page_0087",
                "--secret-id",
                "page_secret_0299",
            ],
            "outputs": ["{reinforced_world}"],
            "continue_on_failure": True,
        },
        {
            "name": "validate_rewritten",
            "command": [
                "{python_bin}",
                "{storyworld_scripts}/sweepweave_validator.py",
                "validate",
                "{reinforced_world}",
            ],
            "outputs": ["{reinforced_world}"],
        },
        {
            "name": "quality_gate",
            "command": [
                "{python_bin}",
                "{storyworld_scripts}/storyworld_quality_gate.py",
                "--storyworld",
                "{reinforced_world}",
                "--strict",
                "--report-out",
                "{quality_report}",
            ],
            "outputs": ["{quality_report}"],
            "continue_on_failure": True,
        },
        {
            "name": "export_swmd_min",
            "command": [
                "{python_bin}",
                "{storyworld_scripts}/json_to_swmd.py",
                "{reinforced_world}",
                "{swmd_min}",
                "--mode",
                "minified",
            ],
            "outputs": ["{swmd_min}"],
        },
    ]
    if args.include_monte_carlo:
        stages.append(
            {
                "name": "monte_carlo_baseline",
                "command": [
                    "{python_bin}",
                    "{storyworld_scripts}/monte_carlo_rehearsal.py",
                    "{reinforced_world}",
                    "--runs",
                    str(args.mc_runs),
                    "--seed",
                    str(args.seed),
                ],
                "outputs": ["{mc_report}"],
                "stdout_to": "{mc_report}",
                "continue_on_failure": True,
            }
        )
    config["stages"] = stages
    return config


def build_config(args: argparse.Namespace) -> Dict[str, Any]:
    builders = {
        "fresh_seed_artistry": fresh_seed_artistry,
        "balanced_secret_topology": balanced_secret_topology,
        "desirability_grind": desirability_grind,
    }
    return builders[args.template](args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create form-valid storyworld factory configs from a constrained template menu.")
    parser.add_argument("--list-templates", action="store_true")
    parser.add_argument("--template", choices=["fresh_seed_artistry", "balanced_secret_topology", "desirability_grind"])
    parser.add_argument("--out-config")
    parser.add_argument("--base-world")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--artifact-root", default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--repo-root", default=DEFAULT_REPO_ROOT)
    parser.add_argument("--storyworld-scripts", default=DEFAULT_STORYWORLD_SCRIPTS)
    parser.add_argument("--small-builder-scripts", default=DEFAULT_SMALL_BUILDER_SCRIPTS)
    parser.add_argument("--python-bin", default="python3")
    parser.add_argument("--title", default="Storyworld Factory Run")
    parser.add_argument("--about", default="A storyworld factory run with artifact-first verification.")
    parser.add_argument("--motif", default="Every scene leaves a measurable trace on the next choice.")
    parser.add_argument("--theme", default="")
    parser.add_argument("--genre", default="")
    parser.add_argument("--characters", default="")
    parser.add_argument("--target-encounters", type=int, default=80)
    parser.add_argument("--ending-count", type=int, default=4)
    parser.add_argument("--secret-ending-count", type=int, default=2)
    parser.add_argument("--super-secret-count", type=int, default=1)
    parser.add_argument("--avg-options", type=float, default=3.2)
    parser.add_argument("--avg-reactions", type=float, default=2.5)
    parser.add_argument("--avg-effects", type=float, default=4.5)
    parser.add_argument("--gate-pct", type=float, default=0.10)
    parser.add_argument("--mc-runs", type=int, default=1200)
    parser.add_argument("--probe-runs", type=int, default=400)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--include-monte-carlo", action="store_true")
    parser.add_argument("--include-encounter-index", action="store_true")
    parser.add_argument("--include-qlora", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.list_templates:
        print(json.dumps(catalog(), indent=2))
        return 0
    if not args.template or not args.out_config or not args.base_world:
        raise SystemExit("--template, --out-config, and --base-world are required unless --list-templates is used")
    config = build_config(args)
    out_path = Path(args.out_config).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
