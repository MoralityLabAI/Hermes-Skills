"""Build figures and CSV tables for the MeTTa/TRM repair addendum."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
OUT_DIR = ROOT / "research" / "generated" / "paper_latex" / "metta_trm_repair_addendum"
FIG_DIR = OUT_DIR / "figures"

RUDDER_JSON = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "local_3b_repair_training_rudder_benchmark"
    / "local_3b_repair_training_rudder.results.json"
)
RUDDER_ROWS = RUDDER_JSON.with_name("local_3b_repair_training_rudder.rows.jsonl")
ACTION_SPACE_JSON = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "local_3b_metta_action_space_rudder_benchmark"
    / "local_3b_repair_training_rudder.results.json"
)
SPLIT_MANIFEST = ROOT / "research" / "generated" / "near_miss_repair_curriculum" / "splits" / "split_manifest.json"
THRESHOLD_JSON = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "symbolic_closure_threshold_suite"
    / "symbolic_closure_threshold.results.json"
)
POSTREPAIR_VERIFIER_JSON = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "c_signature_postrepair_verifier_sweep"
    / "c_signature_postrepair_verifier.results.json"
)
METHODOLOGY_LIFT_JSON = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "metta_trm_methodology_lift_matrix"
    / "methodology_lift.results.json"
)
CAMP_GATE_NOISY_JSON = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-29-logic-signature-camp-gate-leakage-safe"
    / "results"
    / "local_qwen25_3b_noisy_graph_constraint_extract"
    / "local_qwen25_3b_constraint_extract.results.json"
)
CAMP_GATE_GRAPH_ROUTER_JSON = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-29-logic-signature-camp-gate-leakage-safe"
    / "results"
    / "noisy_graph_router_script"
    / "noisy_graph_router.results.json"
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def build_rudder_summary() -> None:
    summary: dict[str, Any] = {}
    for path in [RUDDER_JSON, ACTION_SPACE_JSON]:
        if path.exists():
            summary.update(load_json(path)["summary_by_arm"])
    rows = [
        {
            "arm": arm,
            "target_action_accuracy": values["target_action_accuracy"],
            "repair_action_accuracy": values["repair_action_accuracy"],
            "joint_accuracy": values["joint_accuracy"],
        }
        for arm, values in summary.items()
    ]
    order = [
        "raw_3b_rudder",
        "repair_training_rudder",
        "metta_action_space_rudder",
        "metta_action_space_training_rudder",
        "metta_static_gate_rudder",
        "metta_validator_gate",
    ]
    rows.sort(key=lambda row: order.index(row["arm"]) if row["arm"] in order else len(order))
    write_csv(
        OUT_DIR / "tables" / "rudder_summary.csv",
        rows,
        ["arm", "target_action_accuracy", "repair_action_accuracy", "joint_accuracy"],
    )

    arms = [row["arm"].replace("_", "\\n") for row in rows]
    metrics = ["target_action_accuracy", "repair_action_accuracy", "joint_accuracy"]
    colors = ["#2d6cdf", "#c35a2e", "#4a8f43"]
    x = range(len(arms))
    width = 0.22

    plt.figure(figsize=(10.4, 4.8))
    for index, metric in enumerate(metrics):
        offsets = [pos + (index - 1) * width for pos in x]
        plt.bar(offsets, [row[metric] for row in rows], width=width, label=metric.replace("_", " "), color=colors[index])
    plt.xticks(list(x), arms, fontsize=8)
    plt.ylim(0, 1.05)
    plt.ylabel("accuracy")
    plt.title("Local 3B repair-training rudder benchmark")
    plt.legend(loc="upper right", fontsize=8)
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig_rudder_summary.pdf")
    plt.savefig(FIG_DIR / "fig_rudder_summary.png", dpi=180)
    plt.close()


def build_split_summary() -> None:
    manifest = load_json(SPLIT_MANIFEST)
    split_counts = manifest["split_counts"]
    rows = [{"split": split, "rows": count} for split, count in split_counts.items()]
    write_csv(OUT_DIR / "tables" / "near_miss_split_counts.csv", rows, ["split", "rows"])

    labels = [row["split"].replace("_", "\\n") for row in rows]
    counts = [row["rows"] for row in rows]
    plt.figure(figsize=(7.2, 4.1))
    plt.bar(labels, counts, color=["#3f5f7f", "#6d8f3a", "#b8742b", "#8f4a59"])
    plt.ylabel("rows")
    plt.title("Leakage-aware near-miss repair split")
    for idx, count in enumerate(counts):
        plt.text(idx, count + 2, str(count), ha="center", fontsize=9)
    plt.ylim(0, max(counts) + 30)
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig_split_counts.pdf")
    plt.savefig(FIG_DIR / "fig_split_counts.png", dpi=180)
    plt.close()


def build_rudder_breakdown() -> None:
    rows = load_jsonl(RUDDER_ROWS)
    records: list[dict[str, Any]] = []
    for arm in sorted({row["arm"] for row in rows}):
        arm_rows = [row for row in rows if row["arm"] == arm]
        for split in sorted({row["eval_split"] for row in arm_rows}):
            split_rows = [row for row in arm_rows if row["eval_split"] == split]
            records.append(
                {
                    "arm": arm,
                    "split": split,
                    "n": len(split_rows),
                    "target_action_accuracy": round(
                        sum(row["target_action_correct"] for row in split_rows) / max(1, len(split_rows)), 4
                    ),
                    "repair_action_accuracy": round(
                        sum(row["repair_action_correct"] for row in split_rows) / max(1, len(split_rows)), 4
                    ),
                    "joint_accuracy": round(sum(row["joint_correct"] for row in split_rows) / max(1, len(split_rows)), 4),
                }
            )
    write_csv(
        OUT_DIR / "tables" / "rudder_by_split.csv",
        records,
        ["arm", "split", "n", "target_action_accuracy", "repair_action_accuracy", "joint_accuracy"],
    )


def build_c_signature_verifier_summary() -> None:
    if not POSTREPAIR_VERIFIER_JSON.exists():
        return
    payload = load_json(POSTREPAIR_VERIFIER_JSON)
    rows: list[dict[str, Any]] = []
    for item in payload["ranked_policies"]:
        val = item["summaries"]["val_seen"]
        hold = item["summaries"]["holdout_seen"]
        rows.append(
            {
                "policy": item["policy_id"],
                "signal_class": item["signal_class"],
                "val_accuracy": val["accuracy"],
                "val_false_commit_rate": val["false_commit_rate"],
                "val_false_reject_rate": val["false_reject_rate"],
                "holdout_accuracy": hold["accuracy"],
                "holdout_false_commit_rate": hold["false_commit_rate"],
                "holdout_false_reject_rate": hold["false_reject_rate"],
            }
        )
    write_csv(
        OUT_DIR / "tables" / "c_signature_postrepair_verifier_summary.csv",
        rows,
        [
            "policy",
            "signal_class",
            "val_accuracy",
            "val_false_commit_rate",
            "val_false_reject_rate",
            "holdout_accuracy",
            "holdout_false_commit_rate",
            "holdout_false_reject_rate",
        ],
    )


def build_methodology_lift_summary() -> None:
    if not METHODOLOGY_LIFT_JSON.exists():
        return
    payload = load_json(METHODOLOGY_LIFT_JSON)
    policy_rows: list[dict[str, Any]] = []
    for policy, values in payload["policy_summary"].items():
        policy_rows.append(
            {
                "policy": policy,
                "rows": values["n"],
                "accuracy": values["accuracy"],
                "false_commit_rate": values["false_commit_rate"],
                "false_reject_rate": values["false_reject_rate"],
                "expected_delta_if_committed": values["expected_delta_if_committed"],
            }
        )
    write_csv(
        OUT_DIR / "tables" / "methodology_lift_policy_summary.csv",
        policy_rows,
        ["policy", "rows", "accuracy", "false_commit_rate", "false_reject_rate", "expected_delta_if_committed"],
    )

    env_rows: list[dict[str, Any]] = []
    for env, values in payload["env_summary"].items():
        env_rows.append(
            {
                "env": env,
                "rows": values["n"],
                "avg_reward_lift": values["avg_reward_lift"],
                "exact_count_lift": values["exact_count_lift"],
                "pre_scalar_accuracy": values["policies"]["pre_reward_ge_0p8"]["accuracy"],
                "symbolic_accuracy": values["policies"]["post_symbolic_adapter"]["accuracy"],
                "multi_signal_accuracy": values["policies"]["post_multi_signal"]["accuracy"],
                "false_commit_reduction_vs_pre_scalar": values["false_commit_reduction_vs_pre_scalar"],
                "symbolic_gap_to_multi_signal": values["symbolic_gap_to_multi_signal"],
            }
        )
    write_csv(
        OUT_DIR / "tables" / "methodology_lift_env_summary.csv",
        env_rows,
        [
            "env",
            "rows",
            "avg_reward_lift",
            "exact_count_lift",
            "pre_scalar_accuracy",
            "symbolic_accuracy",
            "multi_signal_accuracy",
            "false_commit_reduction_vs_pre_scalar",
            "symbolic_gap_to_multi_signal",
        ],
    )


def build_camp_gate_noisy_summary() -> None:
    if not CAMP_GATE_NOISY_JSON.exists() or not CAMP_GATE_GRAPH_ROUTER_JSON.exists():
        return
    noisy = load_json(CAMP_GATE_NOISY_JSON)
    router = load_json(CAMP_GATE_GRAPH_ROUTER_JSON)
    noisy_arms = noisy["summary"]["arms"]
    router_arm = router["summary"]["arms"]["metta_graph_router_script"]
    rows = [
        {
            "arm": "baseline_extract",
            "executor": "3B extraction",
            "strict_solve_exact": noisy_arms["baseline_extract"]["solve_exact"],
            "repair_solve_exact": noisy_arms["baseline_extract"]["repair_solve_exact"],
            "rows": noisy_arms["baseline_extract"]["rows"],
            "repair_solve_rate": noisy_arms["baseline_extract"]["repair_solve_exact_rate"],
        },
        {
            "arm": "metta_schema_extract",
            "executor": "3B plus schema",
            "strict_solve_exact": noisy_arms["metta_schema_extract"]["solve_exact"],
            "repair_solve_exact": noisy_arms["metta_schema_extract"]["repair_solve_exact"],
            "rows": noisy_arms["metta_schema_extract"]["rows"],
            "repair_solve_rate": noisy_arms["metta_schema_extract"]["repair_solve_exact_rate"],
        },
        {
            "arm": "metta_graph_extract",
            "executor": "3B plus graph gates",
            "strict_solve_exact": noisy_arms["metta_graph_extract"]["solve_exact"],
            "repair_solve_exact": noisy_arms["metta_graph_extract"]["repair_solve_exact"],
            "rows": noisy_arms["metta_graph_extract"]["rows"],
            "repair_solve_rate": noisy_arms["metta_graph_extract"]["repair_solve_exact_rate"],
        },
        {
            "arm": "metta_graph_router_script",
            "executor": "script gates plus solver",
            "strict_solve_exact": router_arm["solve_exact"],
            "repair_solve_exact": router_arm["solve_exact"],
            "rows": router_arm["rows"],
            "repair_solve_rate": router_arm["solve_exact_rate"],
        },
    ]
    write_csv(
        OUT_DIR / "tables" / "camp_gate_noisy_task_allocation.csv",
        rows,
        ["arm", "executor", "strict_solve_exact", "repair_solve_exact", "rows", "repair_solve_rate"],
    )

    labels = ["baseline\nextract", "schema\nextract", "graph\nextract", "script graph\nrouter"]
    values = [row["repair_solve_exact"] for row in rows]
    totals = [row["rows"] for row in rows]
    colors = ["#8b8b8b", "#5577aa", "#2f8a5b", "#bf7f2f"]

    plt.figure(figsize=(8.6, 4.4))
    bars = plt.bar(labels, values, color=colors)
    plt.ylim(0, max(totals) + 1.2)
    plt.ylabel("exact solves after repair / routing")
    plt.title("Noisy camp-gate task allocation ladder")
    plt.grid(axis="y", alpha=0.25)
    for bar, value, total in zip(bars, values, totals):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.25,
            f"{value}/{total}",
            ha="center",
            fontsize=10,
        )
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig_camp_gate_task_allocation.pdf")
    plt.savefig(FIG_DIR / "fig_camp_gate_task_allocation.png", dpi=180)
    plt.close()


def build_task_graph_diagram() -> None:
    fig, ax = plt.subplots(figsize=(10.2, 5.2))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)

    def box(x: float, y: float, w: float, h: float, text: str, color: str) -> None:
        rect = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor="#222222", linewidth=1.3)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9, wrap=True)

    def arrow(x1: float, y1: float, x2: float, y2: float) -> None:
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops={"arrowstyle": "->", "lw": 1.4, "color": "#222222"},
        )

    box(0.35, 4.25, 1.8, 0.85, "LLM\nproposal / ambiguity", "#d7e6f5")
    box(3.0, 4.25, 2.0, 0.85, "MeTTa task graph\nfield contracts", "#e7dfef")
    box(6.0, 4.25, 1.8, 0.85, "Script gates\nstable parsing", "#dcebd5")
    box(6.0, 2.65, 1.8, 0.85, "TRM gates\nlearned uncertain gates", "#f3e0c5")
    box(6.0, 1.05, 1.8, 0.85, "Symbolic solver /\nvalidator", "#ead7d4")
    box(8.55, 2.65, 1.1, 0.85, "commit /\nveto", "#eeeeee")

    arrow(2.15, 4.68, 3.0, 4.68)
    arrow(5.0, 4.68, 6.0, 4.68)
    arrow(5.0, 4.45, 6.0, 3.08)
    arrow(5.0, 4.35, 6.0, 1.48)
    arrow(7.8, 4.68, 8.55, 3.08)
    arrow(7.8, 3.08, 8.55, 3.08)
    arrow(7.8, 1.48, 8.55, 3.08)

    ax.text(0.35, 0.35, "Principle: route each subtask to the cheapest reliable executor; train TRMs on gates that are neither stable scripts nor safe LLM-only decisions.", fontsize=10)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig_task_graph_allocation_schema.pdf")
    plt.savefig(FIG_DIR / "fig_task_graph_allocation_schema.png", dpi=180)
    plt.close()


def main() -> int:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "tables").mkdir(parents=True, exist_ok=True)
    build_rudder_summary()
    build_split_summary()
    build_rudder_breakdown()
    build_c_signature_verifier_summary()
    build_methodology_lift_summary()
    build_camp_gate_noisy_summary()
    build_task_graph_diagram()
    print(FIG_DIR / "fig_rudder_summary.pdf")
    print(FIG_DIR / "fig_split_counts.pdf")
    print(FIG_DIR / "fig_camp_gate_task_allocation.pdf")
    print(FIG_DIR / "fig_task_graph_allocation_schema.pdf")
    print(OUT_DIR / "tables" / "rudder_summary.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
