from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
BOOTSTRAP = SCRIPT_DIR / "run_small_model_bootstrap_bench.py"
META_CLI = SCRIPT_DIR / "metta_trm_meta_skill.py"
CONTROLLER = SCRIPT_DIR / "train_repair_controller.py"

HELDOUT_TASKS = [
    {
        "task_id": "alife_complexity_sculptor_bootstrap",
        "base_skill": "alife-complexity-sculptor",
        "target_env": "alife_complexity",
        "task": (
            "Bootstrap a MeTTa package for ALife simulation steering. The package should encode complexity-level "
            "targets, morphology and ecology retrieval cues, novelty collapse failure modes, repair hints, and "
            "commit/veto gates for preserving open-ended dynamics."
        ),
    },
    {
        "task_id": "diplomacy_coalition_forecast_bootstrap",
        "base_skill": "diplomacy-negotiation-storyworld",
        "target_env": "diplomacy_coalition",
        "task": (
            "Bootstrap a MeTTa package for diplomacy coalition forecasting. The package should encode alliance "
            "signals, betrayal-risk retrieval cues, negotiation diary failures, repair hints, and commit/veto gates "
            "for bounded forecast updates."
        ),
    },
    {
        "task_id": "bluebeam_tamper_probe_bootstrap",
        "base_skill": "bluebeam-tamper-probe",
        "target_env": "bluebeam_tamper",
        "task": (
            "Bootstrap a MeTTa package for latent tamper sensing. The package should encode probe calibration, "
            "drift/tamper failure modes, weak localization retrieval cues, repair hints, and commit/veto gates for "
            "safe escalation."
        ),
    },
    {
        "task_id": "storyworld_builder_balance_bootstrap",
        "base_skill": "storyworld-conveyor",
        "target_env": "storyworld_builder_balance",
        "task": (
            "Bootstrap a MeTTa package for storyworld building balance. The package should encode encounter DAG "
            "balance constraints, secret-ending pathing cues, Monte Carlo calibration failures, repair hints, and "
            "commit/veto gates for playable SWMD output."
        ),
    },
    {
        "task_id": "prime_math_candidate_auditor_bootstrap",
        "base_skill": "primehub-hard-reasoning-numeric-hermes",
        "target_env": "prime_math_candidate_auditor",
        "task": (
            "Bootstrap a MeTTa package for math candidate auditing. The package should encode candidate-set "
            "invariants, numeric verifier failures, teacher-candidate retrieval cues, repair hints, and commit/veto "
            "gates without claiming direct solve ability."
        ),
    },
]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_cmd(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=str(cwd), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def find_latest_run(out_root: Path, before: set[str]) -> Path:
    candidates = [
        path for path in out_root.glob("small_model_bootstrap_*")
        if path.is_dir() and path.name not in before
    ]
    if not candidates:
        candidates = [path for path in out_root.glob("small_model_bootstrap_*") if path.is_dir()]
    if not candidates:
        raise SystemExit(f"no bootstrap run directories found under {out_root}")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def summarize_controller(controller_summary: dict[str, Any], bootstrap_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "raw_bootstrap_overall": bootstrap_summary.get("averages", {}).get("raw_overall", 0.0),
        "script_repaired_overall": bootstrap_summary.get("averages", {}).get("repaired_overall", 0.0),
        "script_runtime_ready_rate": bootstrap_summary.get("averages", {}).get("ready_for_runtime_rate", 0.0),
        "controller_exact_action_rate": controller_summary.get("exact_action_rate", 0.0),
        "controller_mean_key_accuracy": controller_summary.get("mean_key_accuracy", 0.0),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a held-out Qwen bootstrap plus compact repair-controller generalization study.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--controller-train-messages", required=True)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8084")
    parser.add_argument("--model", default="Qwen3.5-4B.Q4_K_M.gguf")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--stage-max-tokens", type=int, default=520)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.out_dir) / f"repair_generalization_{utc_stamp()}"
    root.mkdir(parents=True, exist_ok=True)
    tasks = HELDOUT_TASKS[: args.limit] if args.limit else HELDOUT_TASKS
    tasks_path = root / "heldout_tasks.json"
    tasks_path.write_text(json.dumps(tasks, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    bootstrap_root = root / "bootstrap_runs"
    bootstrap_root.mkdir(parents=True, exist_ok=True)
    before = {path.name for path in bootstrap_root.glob("small_model_bootstrap_*") if path.is_dir()}
    bootstrap_proc = run_cmd(
        [
            sys.executable,
            str(BOOTSTRAP),
            "--tasks-json",
            str(tasks_path),
            "--out-dir",
            str(bootstrap_root),
            "--prompt-mode",
            "compact",
            "--generation-mode",
            "staged",
            "--max-tokens",
            "1200",
            "--stage-max-tokens",
            str(args.stage_max_tokens),
            "--timeout",
            str(args.timeout),
            "--endpoint",
            args.endpoint,
            "--model",
            args.model,
        ],
        cwd=SCRIPT_DIR.parent,
    )
    (root / "bootstrap_process.json").write_text(
        json.dumps({"returncode": bootstrap_proc.returncode, "stdout": bootstrap_proc.stdout, "stderr": bootstrap_proc.stderr}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if bootstrap_proc.returncode != 0:
        raise SystemExit(bootstrap_proc.returncode)
    run_dir = find_latest_run(bootstrap_root, before)

    repair_rows = run_dir / "repair_training_rows.jsonl"
    repair_messages = run_dir / "repair_training_messages.jsonl"
    repair_manifest = run_dir / "repair_training_manifest.json"
    export_proc = run_cmd(
        [
            sys.executable,
            str(META_CLI),
            "export-repair-training-rows",
            "--input",
            str(run_dir),
            "--out",
            str(repair_rows),
            "--messages-out",
            str(repair_messages),
            "--manifest",
            str(repair_manifest),
        ],
        cwd=SCRIPT_DIR.parent,
    )
    (root / "repair_export_process.json").write_text(
        json.dumps({"returncode": export_proc.returncode, "stdout": export_proc.stdout, "stderr": export_proc.stderr}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if export_proc.returncode != 0:
        raise SystemExit(export_proc.returncode)

    controller_dir = root / "controller_eval_on_heldout_repairs"
    controller_proc = run_cmd(
        [
            sys.executable,
            str(CONTROLLER),
            "--train-messages",
            str(Path(args.controller_train_messages)),
            "--val-messages",
            str(repair_messages),
            "--out-dir",
            str(controller_dir),
        ],
        cwd=SCRIPT_DIR.parent,
    )
    (root / "controller_process.json").write_text(
        json.dumps({"returncode": controller_proc.returncode, "stdout": controller_proc.stdout, "stderr": controller_proc.stderr}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if controller_proc.returncode != 0:
        raise SystemExit(controller_proc.returncode)

    bootstrap_summary = load_json(run_dir / "summary.json")
    repair_summary = load_json(repair_manifest)
    controller_summary = load_json(controller_dir / "summary.json")
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "task_count": len(tasks),
        "tasks_path": str(tasks_path),
        "bootstrap_run": str(run_dir),
        "repair_manifest": str(repair_manifest),
        "controller_eval": str(controller_dir),
        "bootstrap_summary": bootstrap_summary,
        "repair_summary": repair_summary,
        "controller_summary": controller_summary,
        "comparison": summarize_controller(controller_summary, bootstrap_summary),
    }
    (root / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(root)
    print(json.dumps(summary["comparison"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

