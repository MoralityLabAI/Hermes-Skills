from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_SOURCE = (
    Path(r"C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\plans")
    / "primehub_next_three_families.json"
)
DEFAULT_OUT_DIR = (
    Path(
        r"C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts"
    )
    / "primehub_next_three_family_workplan"
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _bullet_lines(items: list[str], indent: str = "- ") -> list[str]:
    return [f"{indent}{item}" for item in items]


def _row_lines(rows: list[dict[str, str]], key_name: str) -> list[str]:
    return [f"- `{row[key_name]}`: {row['goal']}" for row in rows]


def render_markdown(plan: dict[str, Any], benchmark_manifest: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Primehub Next Three Family Workplan")
    lines.append("")
    lines.append("## Trainer Plan")
    lines.append("")
    lines.extend(
        _bullet_lines(
            [
                f"training task root: `{plan['plan_id']}`",
                f"base corpus: `{plan['base_corpus']}`",
                (
                    "hard caps: "
                    f"RAM `{plan['default_caps']['ram_mb']} MB`, "
                    f"CPU `{plan['default_caps']['cpu_pct']}%`, "
                    f"IO `{plan['default_caps']['io_cap_mb_s']} MB/s`"
                ),
                f"chunk strategy: `{plan['default_run_plan']['chunk_strategy']}`",
                f"checkpoint interval: `{plan['default_run_plan']['checkpoint_interval']}`",
                f"holdout ratio: `{plan['default_run_plan']['holdout_ratio']}`",
                f"top_k: `{plan['default_run_plan']['top_k']}`"
            ]
        )
    )
    lines.append("")
    lines.append("## Selection Basis")
    lines.append("")
    lines.extend(_bullet_lines(plan["selection_basis"]))
    lines.append("")
    lines.append("## Family Table")
    lines.append("")
    lines.append("| Priority | Family | Basis | Cluster | Holdout rows |")
    lines.append("| ---: | --- | --- | --- | ---: |")
    for family in sorted(plan["families"], key=lambda item: item["priority"]):
        lines.append(
            "| {priority} | `{family_id}` | {basis} | `{cluster}` | {rows} |".format(
                priority=family["priority"],
                family_id=family["family_id"],
                basis=family["basis"],
                cluster=family["cluster"],
                rows=family["source_holdout_rows"],
            )
        )
    lines.append("")

    for family in sorted(plan["families"], key=lambda item: item["priority"]):
        lines.append(f"## {family['family_id']}")
        lines.append("")
        lines.extend(
            _bullet_lines(
                [
                    f"basis: `{family['basis']}`",
                    f"cluster: `{family['cluster']}`",
                    f"training task id: `{family['training_task_id']}`",
                    f"source holdout rows: `{family['source_holdout_rows']}`",
                ]
            )
        )
        lines.append("")
        lines.append("Why now:")
        lines.extend(_bullet_lines(family["why_now"]))
        lines.append("")
        lines.append("Observation shape:")
        lines.extend(_bullet_lines(family["observation_shape"]))
        lines.append("")
        lines.append("Retrieval row types:")
        lines.extend(_row_lines(family["retrieval_row_types"], "row_type"))
        lines.append("")
        lines.append("Critic support types:")
        lines.extend(_row_lines(family["critic_support_types"], "support_type"))
        lines.append("")
        lines.append("Repair row types:")
        lines.extend(_row_lines(family["repair_row_types"], "row_type"))
        lines.append("")
        lines.append("Benchmark gates:")
        lines.append(
            f"- focus overlap rows expected: `{family['benchmark_gates']['focus_overlap_rows_expected']}`"
        )
        lines.append("- primary:")
        lines.extend(_bullet_lines(family["benchmark_gates"]["primary"], indent="  - "))
        lines.append("- guardrails:")
        lines.extend(_bullet_lines(family["benchmark_gates"]["guardrails"], indent="  - "))
        lines.append("- global:")
        lines.extend(_bullet_lines(family["benchmark_gates"]["global"], indent="  - "))
        lines.append("")

    lines.append("## Deferred Families")
    lines.append("")
    lines.append("| Family | Reason |")
    lines.append("| --- | --- |")
    for item in plan["deferred_families"]:
        lines.append(f"| `{item['family_id']}` | {item['reason']} |")
    lines.append("")
    lines.append("## Benchmark Manifest")
    lines.append("")
    lines.extend(
        _bullet_lines(
            [
                f"`{run['family_id']}` -> `{run['training_task_id']}` / out-dir `{run['out_dir']}`"
                for run in benchmark_manifest["runs"]
            ]
        )
    )
    lines.append("")
    return "\n".join(lines)


def build_benchmark_manifest(plan: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    for family in sorted(plan["families"], key=lambda item: item["priority"]):
        family_dir = out_dir / family["family_id"]
        runs.append(
            {
                "family_id": family["family_id"],
                "training_task_id": family["training_task_id"],
                "cluster": family["cluster"],
                "basis": family["basis"],
                "focus_metrics": family["focus_metrics"],
                "caps": plan["default_caps"],
                "chunk_strategy": plan["default_run_plan"]["chunk_strategy"],
                "checkpoint_interval": plan["default_run_plan"]["checkpoint_interval"],
                "out_dir": str(family_dir),
                "planned_bundle_dir": str(family_dir / "bundle"),
                "planned_comparison_dir": str(family_dir / "comparison")
            }
        )
    return {
        "plan_id": plan["plan_id"],
        "run_count": len(runs),
        "runs": runs
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    plan = load_json(args.source)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    benchmark_manifest = build_benchmark_manifest(plan, args.out_dir)
    output_json = {
        "plan_id": plan["plan_id"],
        "family_count": len(plan["families"]),
        "deferred_count": len(plan["deferred_families"]),
        "selection_basis": plan["selection_basis"],
        "families": plan["families"],
        "deferred_families": plan["deferred_families"],
        "default_caps": plan["default_caps"],
        "default_run_plan": plan["default_run_plan"]
    }

    write_json(args.out_dir / "primehub_next_three_family_workplan.json", output_json)
    write_json(args.out_dir / "benchmark_manifest.json", benchmark_manifest)
    (args.out_dir / "primehub_next_three_family_workplan.md").write_text(
        render_markdown(plan, benchmark_manifest) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
