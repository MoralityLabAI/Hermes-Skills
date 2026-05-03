from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import os
from pathlib import Path
from typing import Any, Dict, List


SKILL_ROOT = Path(__file__).resolve().parents[1]
HERMES_REPO_ROOT = Path(__file__).resolve().parents[2]


def find_storyworld_repo_root() -> Path:
    candidates = []
    env_root = str(os.environ.get("GPTSTORYWORLD_ROOT", "") or "").strip()
    if env_root:
        candidates.append(Path(env_root))
    candidates.extend([HERMES_REPO_ROOT, Path(r"C:\projects\GPTStoryworld")])
    for root in candidates:
        if (root / "mcp-storyworld-encounter" / "swmd_store.py").exists():
            return root.resolve()
    return HERMES_REPO_ROOT.resolve()


STORYWORLD_REPO_ROOT = find_storyworld_repo_root()
SMALL_BUILDER_SCRIPTS = STORYWORLD_REPO_ROOT / "codex-skills" / "small-storyworld-builder" / "scripts"
CONVEYOR_SCRIPTS = SKILL_ROOT / "scripts"


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_swmd_tools() -> Any:
    module_dir = STORYWORLD_REPO_ROOT / "mcp-storyworld-encounter"
    if str(module_dir) not in sys.path:
        sys.path.insert(0, str(module_dir))
    import swmd_store  # type: ignore

    return swmd_store


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def summarize_trm_advice(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"source_path": str(path), "parse_ok": False}
    summary: Dict[str, Any] = {"source_path": str(path), "parse_ok": True}
    for key in (
        "focus_metrics",
        "target_endings",
        "priority_fixes",
        "notes",
        "recommendations",
        "storyworld",
        "phase_guidance",
        "quality_failures",
        "recommended_overrides",
        "raw_metrics",
    ):
        if key in payload:
            summary[key] = payload[key]
    if "advice" in payload and isinstance(payload["advice"], dict):
        advice = payload["advice"]
        for key in (
            "focus_metrics",
            "target_endings",
            "priority_fixes",
            "notes",
            "recommendations",
            "phase_guidance",
            "quality_failures",
            "recommended_overrides",
            "raw_metrics",
        ):
            if key in advice and key not in summary:
                summary[key] = advice[key]
    if "payload" in payload and isinstance(payload["payload"], dict):
        nested = payload["payload"]
        for key in (
            "focus_metrics",
            "target_endings",
            "priority_fixes",
            "notes",
            "recommendations",
            "storyworld",
            "phase_guidance",
            "quality_failures",
            "recommended_overrides",
            "raw_metrics",
        ):
            if key in nested and key not in summary:
                summary[key] = nested[key]
    return summary


def build_trm_advice_from_reports(run_dir: Path, python_bin: str, config: Dict[str, Any], dry_run: bool) -> Path | None:
    mc_report = str(config.get("monte_carlo_report", "") or "").strip()
    if not mc_report:
        return None
    advice_out = run_dir / "reports" / "trm_advice.generated.json"
    if dry_run:
        return advice_out
    cmd = [
        python_bin,
        str(CONVEYOR_SCRIPTS / "build_storyworld_trm_advice.py"),
        "--mc-report",
        str(Path(mc_report).resolve()),
        "--out-advice",
        str(advice_out),
        "--storyworld-label",
        str(config.get("storyworld_label") or Path(config.get("swmd", "storyworld")).stem),
    ]
    quality_report = str(config.get("quality_report", "") or "").strip()
    if quality_report:
        cmd.extend(["--quality-report", str(Path(quality_report).resolve())])
    rc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if rc.returncode != 0:
        raise RuntimeError((rc.stderr or rc.stdout or "failed to build TRM advice").strip())
    return advice_out


def build_operation_packet_path(run_dir: Path) -> Path:
    return run_dir / "reports" / "operation_packets.jsonl"


def build_stage_manifest(
    run_id: str,
    stage: str,
    status: str,
    input_files: List[str],
    output_files: List[str],
    counters: Dict[str, Any],
    notes: List[str] | None = None,
) -> Dict[str, Any]:
    ts = now_iso()
    return {
        "run_id": run_id,
        "stage": stage,
        "status": status,
        "started_at": ts,
        "completed_at": ts,
        "input_files": input_files,
        "output_files": output_files,
        "counters": counters,
        "notes": notes or [],
    }


def run_command(stage_dir: Path, command: List[str]) -> int:
    stdout_path = stage_dir / "stdout.log"
    stderr_path = stage_dir / "stderr.log"
    with stdout_path.open("w", encoding="utf-8", newline="\n") as out_handle, stderr_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as err_handle:
        proc = subprocess.run(command, stdout=out_handle, stderr=err_handle, text=True, check=False)
    return int(proc.returncode)


def line_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def run_mcp_budget_preflight(run_dir: Path, run_id: str, config: Dict[str, Any], swmd_path: Path) -> bool:
    stage_dir = ensure_dir(run_dir / "mcp_budget_preflight")
    report_path = stage_dir / "budget_report.json"
    rows_path = stage_dir / "budget_rows.jsonl"
    events_path = stage_dir / "events.jsonl"

    context_budget = int(config.get("context_budget_tokens", 8192))
    reserve_output = int(config.get("reserve_output_tokens", 1024))
    planning_card = int(config.get("planning_card_tokens", 900))
    neighbor_hops = int(config.get("neighbor_hops", 1))
    start_index = int(config.get("start_index", 0))
    max_encounters = int(config.get("max_encounters", 12))
    max_prompt_tokens = int(config.get("max_prompt_tokens", context_budget - reserve_output))
    if max_prompt_tokens <= 0:
        max_prompt_tokens = max(1, context_budget - reserve_output)
    ratio_cap = float(config.get("max_input_output_ratio", 24.0))
    max_new_tokens = max(1, int(config.get("max_new_tokens", 160)))
    allow_overflow = bool(config.get("allow_mcp_budget_overflow", False))

    swmd_tools = load_swmd_tools()
    doc = swmd_tools.parse_swmd_min(swmd_path)
    selected = doc.encounter_order[start_index : start_index + max_encounters]
    worst_prompt = 0
    worst_ratio = 0.0
    overflow_rows: List[Dict[str, Any]] = []

    with rows_path.open("w", encoding="utf-8", newline="\n") as handle:
        for encounter_id in selected:
            packet = swmd_tools.iteration_packet(
                path=swmd_path,
                encounter_id=encounter_id,
                neighbor_hops=neighbor_hops,
                context_budget_tokens=context_budget,
                reserve_output_tokens=reserve_output,
                planning_card_tokens=planning_card,
                include_poetics=True,
            )
            used = int(packet.get("budget", {}).get("estimated_tokens_used", 0))
            ratio = round(used / max_new_tokens, 3)
            row = {
                "encounter_id": encounter_id,
                "estimated_prompt_tokens": used,
                "max_prompt_tokens": max_prompt_tokens,
                "estimated_input_output_ratio": ratio,
                "max_input_output_ratio": ratio_cap,
                "neighbor_hops": neighbor_hops,
                "within_prompt_budget": used <= max_prompt_tokens,
                "within_ratio_budget": ratio <= ratio_cap,
            }
            if not row["within_prompt_budget"] or not row["within_ratio_budget"]:
                overflow_rows.append(row)
            worst_prompt = max(worst_prompt, used)
            worst_ratio = max(worst_ratio, ratio)
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")

    status = "completed"
    if overflow_rows and not allow_overflow:
        status = "failed"
    report = {
        "run_id": run_id,
        "status": status,
        "swmd": str(swmd_path),
        "selected_encounters": len(selected),
        "context_budget_tokens": context_budget,
        "reserve_output_tokens": reserve_output,
        "max_prompt_tokens": max_prompt_tokens,
        "planning_card_tokens": planning_card,
        "max_new_tokens": max_new_tokens,
        "max_input_output_ratio": ratio_cap,
        "worst_prompt_tokens": worst_prompt,
        "worst_input_output_ratio": worst_ratio,
        "overflow_count": len(overflow_rows),
        "overflow_preview": overflow_rows[:10],
        "allow_mcp_budget_overflow": allow_overflow,
    }
    dump_json(report_path, report)
    dump_json(
        stage_dir / "manifest.json",
        build_stage_manifest(
            run_id,
            "mcp_budget_preflight",
            status,
            [str(swmd_path)],
            [str(report_path), str(rows_path)],
            {
                "selected_encounters": len(selected),
                "worst_prompt_tokens": worst_prompt,
                "worst_input_output_ratio": worst_ratio,
                "overflow_count": len(overflow_rows),
            },
            notes=["hard MCP budget guard before any model load"],
        ),
    )
    dump_json(stage_dir / "progress.json", {"stage": "mcp_budget_preflight", "status": status, "updated_at": now_iso()})
    append_jsonl(events_path, {"event": "stage_finished", "status": status, "at": now_iso()})
    return status == "completed"


def run_operation_stage(run_dir: Path, python_bin: str, config: Dict[str, Any], trm_packet_path: Path, dry_run: bool) -> Dict[str, Any]:
    op_stage = ensure_dir(run_dir / "operation_pipeline")
    op_run_root = ensure_dir(op_stage / "runs")
    op_run_id = str(config.get("operation_run_id") or f"{config.get('run_id', 'small_port')}_op")
    world_json_value = str(config.get("world_json", "") or config.get("operation_world_json", "") or "").strip()
    if world_json_value:
        world_json_path = Path(world_json_value).resolve()
    else:
        swmd_path = Path(config["swmd"]).resolve()
        candidate = swmd_path.with_name("artistry_world.json")
        world_json_path = candidate if candidate.exists() else swmd_path
    op_cmd = [
        python_bin,
        str(CONVEYOR_SCRIPTS / "run_storyworld_operation_smoke.py"),
        "--world-json",
        str(world_json_path),
        "--model-path",
        str(Path(config["model_path"]).resolve()),
        "--output-root",
        str(op_run_root),
        "--run-id",
        op_run_id,
        "--max-packets",
        str(int(config.get("operation_max_packets", config.get("max_encounters", 12)))),
        "--max-new-tokens",
        str(int(config.get("operation_max_new_tokens", 160))),
        "--temperature",
        str(float(config.get("operation_temperature", config.get("temperature", 0.0)))),
    ]
    quality_report = str(config.get("quality_report", "") or "").strip()
    if quality_report:
        op_cmd.extend(["--quality-report", str(Path(quality_report).resolve())])
    if bool(config.get("operation_no_adapter", False)) or not str(config.get("adapter_path", "") or "").strip():
        op_cmd.append("--no-adapter")
    else:
        op_cmd.extend(["--adapter-path", str(config.get("adapter_path"))])
    packet_jsonl = str(config.get("operation_packet_jsonl", "") or "").strip()
    if packet_jsonl:
        op_cmd.extend(["--packet-jsonl", str(Path(packet_jsonl).resolve())])

    dump_json(op_stage / "command.json", {"command": op_cmd})
    if dry_run:
        op_status = "planned"
    else:
        rc = run_command(op_stage, op_cmd)
        op_status = "completed" if rc == 0 else "failed"

    op_run_dir = op_run_root / op_run_id
    op_summary = op_run_dir / "summary.json"
    op_gens = op_run_dir / "generations.jsonl"
    op_manifest = build_stage_manifest(
        str(config.get("run_id") or run_dir.name),
        "operation_pipeline",
        op_status,
        [x for x in [str(world_json_path), str(Path(quality_report).resolve()) if quality_report else ""] if x],
        [str(op_summary), str(op_gens)],
        {
            "packet_count": line_count(op_gens),
            "parse_accuracy": read_json(op_summary).get("parse_accuracy", 0.0) if op_summary.exists() else 0.0,
        },
        notes=["operation-level repair packet smoke"],
    )
    dump_json(op_stage / "manifest.json", op_manifest)
    dump_json(op_stage / "progress.json", {"stage": "operation_pipeline", "status": op_status, "updated_at": now_iso()})
    append_jsonl(op_stage / "events.jsonl", {"event": "stage_finished", "status": op_status, "at": now_iso()})
    return {
        "stage_dir": str(op_stage),
        "run_dir": str(op_run_dir),
        "summary": str(op_summary),
        "generations": str(op_gens),
        "status": op_status,
        "manifest": str(op_stage / "manifest.json"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes context-managed port of the small storyworld builder for 4GB VRAM setups.")
    parser.add_argument("--config", required=True, help="JSON config path.")
    parser.add_argument("--run-id", default="", help="Optional run id override.")
    parser.add_argument("--dry-run", action="store_true", help="Write manifests and commands but do not run the model stages.")
    parser.add_argument("--preflight-only", action="store_true", help="Build index and MCP budget report, then stop before model load.")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))

    run_id = str(args.run_id or config.get("run_id") or f"small_port_{int(time.time())}")
    artifact_root = ensure_dir(Path(config["artifact_root"]).resolve())
    run_dir = ensure_dir(artifact_root / run_id)
    dump_json(run_dir / "run_config.snapshot.json", config)

    python_bin = str(config.get("python_bin") or sys.executable)
    swmd_path = Path(config["swmd"]).resolve()
    model_path = str(Path(config["model_path"]).resolve())
    adapter_path = str(config.get("adapter_path", "") or "")
    trm_advice_path = Path(config.get("trm_advice_json", "")).resolve() if config.get("trm_advice_json") else None
    qlora_examples = str(Path(config["qlora_examples_jsonl"]).resolve()) if config.get("qlora_examples_jsonl") else ""
    repair_mode = str(config.get("repair_mode", "phase_then_operation_fallback") or "phase_then_operation_fallback").strip()
    if repair_mode not in {"swmd_only", "operation_only", "both", "phase_then_operation_fallback"}:
        repair_mode = "phase_then_operation_fallback"
    force_phase_failure = bool(config.get("force_phase_failure", False))

    index_stage = ensure_dir(run_dir / "build_encounter_index")
    index_dir = ensure_dir(run_dir / "indices" / "encounter_index")
    index_cmd = [
        python_bin,
        str(SMALL_BUILDER_SCRIPTS / "swmd_encounter_index.py"),
        "--swmd",
        str(swmd_path),
        "--out-dir",
        str(index_dir),
    ]
    dump_json(index_stage / "command.json", {"command": index_cmd})

    if args.dry_run:
        status = "planned"
    else:
        rc = run_command(index_stage, index_cmd)
        status = "completed" if rc == 0 else "failed"
    dump_json(
        index_stage / "manifest.json",
        build_stage_manifest(
            run_id,
            "build_encounter_index",
            status,
            [str(swmd_path)],
            [str(index_dir / "encounters.jsonl"), str(index_dir / "world_card.txt")],
            {"encounters_indexed": line_count(index_dir / "encounters.jsonl")},
        ),
    )
    dump_json(index_stage / "progress.json", {"stage": "build_encounter_index", "status": status, "updated_at": now_iso()})
    append_jsonl(index_stage / "events.jsonl", {"event": "stage_finished", "status": status, "at": now_iso()})
    if status == "failed":
        return 1

    if not args.dry_run and bool(config.get("mcp_budget_preflight", True)):
        preflight_ok = run_mcp_budget_preflight(run_dir, run_id, config, swmd_path)
        if not preflight_ok:
            return 1
        if args.preflight_only:
            summary = {
                "run_id": run_id,
                "run_dir": str(run_dir),
                "swmd": str(swmd_path),
                "status": "preflight_completed",
                "mcp_budget_report": str(run_dir / "mcp_budget_preflight" / "budget_report.json"),
            }
            dump_json(run_dir / "summary.json", summary)
            print(str(run_dir))
            print(str(run_dir / "summary.json"))
            return 0
    elif args.preflight_only:
        raise RuntimeError("preflight-only requires mcp_budget_preflight=true and must not be combined with --dry-run")

    trm_stage = ensure_dir(run_dir / "prepare_trm_packet")
    trm_packet_path = run_dir / "reports" / "trm_constraints.json"
    generated_trm_advice = build_trm_advice_from_reports(run_dir, python_bin, config, args.dry_run)
    effective_trm_advice = trm_advice_path or generated_trm_advice
    trm_payload = summarize_trm_advice(effective_trm_advice) if effective_trm_advice and effective_trm_advice.exists() else {}
    trm_payload.setdefault("profile", {})
    trm_payload["profile"].update(
        {
            "goal": "bounded_context_storyworld_revision",
            "hardware": "4GB_VRAM",
            "model_family": "Qwen_2B_class",
            "memory_mode": "encounter_packet_only",
            "cross_play_memory_mode": "summary",
        }
    )
    dump_json(trm_packet_path, trm_payload)
    dump_json(
        trm_stage / "manifest.json",
        build_stage_manifest(
            run_id,
            "prepare_trm_packet",
            "completed",
            [str(p) for p in (trm_advice_path, generated_trm_advice) if p],
            [str(trm_packet_path)],
            {"keys": len(trm_payload.keys())},
            notes=["TRM constraints summarized for MCP packet injection"],
        ),
    )
    dump_json(trm_stage / "progress.json", {"stage": "prepare_trm_packet", "status": "completed", "updated_at": now_iso()})
    append_jsonl(trm_stage / "events.jsonl", {"event": "stage_finished", "status": "completed", "at": now_iso()})

    operation_result: Dict[str, Any] = {
        "stage_dir": "",
        "run_dir": "",
        "summary": "",
        "generations": "",
        "status": "skipped",
        "manifest": "",
    }
    phase_status = "skipped"
    if repair_mode != "operation_only":
        phase_stage = ensure_dir(run_dir / "phase_pipeline")
        phase_events = run_dir / "reports" / "phase_events.jsonl"
        phase_state = run_dir / "reports" / "phase_state.json"
        phase_cmd = [
            python_bin,
            str(SMALL_BUILDER_SCRIPTS / "swmd_mcp_phase_pipeline.py"),
            "--swmd",
            str(swmd_path),
            "--backend",
            str(config.get("inference_backend", "auto")),
            "--model-path",
            model_path,
            "--max-encounters",
            str(int(config.get("max_encounters", 12))),
            "--start-index",
            str(int(config.get("start_index", 0))),
            "--neighbor-hops",
            str(int(config.get("neighbor_hops", 1))),
            "--context-budget-tokens",
            str(int(config.get("context_budget_tokens", 8192))),
            "--reserve-output-tokens",
            str(int(config.get("reserve_output_tokens", 1024))),
            "--planning-card-tokens",
            str(int(config.get("planning_card_tokens", 900))),
            "--max-new-tokens",
            str(int(config.get("max_new_tokens", 160))),
            "--temperature",
            str(float(config.get("temperature", 0.0))),
            "--out-jsonl",
            str(phase_events),
            "--state-json",
            str(phase_state),
            "--fewshot-count",
            str(int(config.get("fewshot_count", 0))),
            "--external-constraints-json",
            str(trm_packet_path),
        ]
        phases = str(config.get("phases", "")).strip()
        if phases:
            phase_cmd.extend(["--phases", phases])
        if adapter_path:
            phase_cmd.extend(["--adapter-path", adapter_path])
        if qlora_examples:
            phase_cmd.extend(["--qlora-examples-jsonl", qlora_examples])
        if bool(config.get("repair_build_output", False)):
            phase_cmd.append("--repair-build-output")
        if bool(config.get("apply", False)):
            phase_cmd.append("--apply")
        dump_json(phase_stage / "command.json", {"command": phase_cmd})

        if args.dry_run:
            phase_status = "planned"
        else:
            rc = run_command(phase_stage, phase_cmd)
            phase_status = "completed" if rc == 0 else "failed"
        if force_phase_failure and phase_status != "planned":
            phase_status = "failed"
        dump_json(
            phase_stage / "manifest.json",
            build_stage_manifest(
                run_id,
                "phase_pipeline",
                phase_status,
                [str(swmd_path), str(trm_packet_path)],
                [str(phase_events), str(phase_state)],
                {"rows": line_count(phase_events)},
                notes=["4GB-friendly bounded-context phase loop"],
            ),
        )
        dump_json(phase_stage / "progress.json", {"stage": "phase_pipeline", "status": phase_status, "updated_at": now_iso()})
        append_jsonl(phase_stage / "events.jsonl", {"event": "stage_finished", "status": phase_status, "at": now_iso()})
        if repair_mode == "swmd_only" and phase_status == "failed":
            return 1
    elif repair_mode == "operation_only":
        phase_events = run_dir / "reports" / "phase_events.jsonl"
        phase_state = run_dir / "reports" / "phase_state.json"

    if repair_mode in {"operation_only", "both"} or (repair_mode == "phase_then_operation_fallback" and phase_status == "failed"):
        operation_result = run_operation_stage(run_dir, python_bin, config, trm_packet_path, args.dry_run)
        if operation_result.get("status") == "failed":
            if repair_mode in {"operation_only", "phase_then_operation_fallback"}:
                return 1
            if repair_mode == "both" and phase_status == "failed":
                return 1

    summary = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "swmd": str(swmd_path),
        "phase_events": str(phase_events),
        "phase_state": str(phase_state),
        "trm_constraints": str(trm_packet_path),
        "operation_pipeline": operation_result,
        "repair_mode": repair_mode,
        "status": "planned" if args.dry_run else "completed",
    }
    dump_json(run_dir / "summary.json", summary)
    print(str(run_dir))
    print(str(run_dir / "summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
