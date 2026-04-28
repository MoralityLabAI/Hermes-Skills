from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


STUDY_ROOT = Path(__file__).resolve().parent
REPO_ROOT = STUDY_ROOT.parents[2]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
PIPELINE_SCRIPTS_ROOT = REPO_ROOT / "metta-trm-hermes-pipeline" / "scripts"
TRM_ROOT = Path(r"C:/projects/trm_observability_harness")
STRUCTURED_MAP_PROMPT_BUILDER = REPO_ROOT / "primehub-structured-map-hermes" / "scripts" / "build_skill_prompt.py"
REMOTE_BRIDGE = REPO_ROOT / "scripts" / "remote_prime_env_bridge.py"

CONTROL_SURFACE_PATH = (
    REPO_ROOT
    / "research"
    / "studies"
    / "2026-04-22-primehub-structured-map-retrieval"
    / "artifacts"
    / "primehub_schema_pack"
    / "primehub_schema_surface.json"
)
METTA_BUNDLE_ROOT = STUDY_ROOT / "artifacts" / "primehub_structured_map_bundle"
RUNTIME_PACKET_PATH = METTA_BUNDLE_ROOT / "runtime_packet.json"

if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))
if str(PIPELINE_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(PIPELINE_SCRIPTS_ROOT))

from metta_repair_pass import load_bundle_env, repair_candidate  # noqa: E402
from overnight_primehub_benchmark import ModelProfile, build_config, run_one_task  # noqa: E402


ENV_IDS = ["psycho_bench", "ascii_tree", "pydantic_adherence"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run control vs compact MeTTa runtime packet vs repair-assisted live eval.")
    parser.add_argument("--env-id", action="append", dest="env_ids", default=[], help="Optional env id to run. Repeat to include multiple envs.")
    parser.add_argument("--model-id", default="qwen35_9b")
    parser.add_argument("--base-url", default="http://snacksack-ms-7d32.tail3156cd.ts.net:8082/v1")
    parser.add_argument("--model-name", default="Qwen_Qwen3.5-9B-Q4_K_M.gguf")
    parser.add_argument("--max-new-tokens", type=int, default=320)
    parser.add_argument("--request-timeout", type=int, default=180)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument(
        "--output-dir",
        default=str(STUDY_ROOT / "artifacts" / "live_eval_qwen35_9b_runtime_packet_repair"),
    )
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not decode to an object")
    return payload


def run_builder(command: List[str]) -> str:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "builder failed").strip())
    output = (result.stdout or "").strip()
    if not output:
        raise RuntimeError("builder returned empty output")
    return output


def resolve_env_ids(args: argparse.Namespace) -> List[str]:
    requested = [str(env_id).strip() for env_id in (args.env_ids or []) if str(env_id).strip()]
    if not requested:
        return list(ENV_IDS)
    unknown = [env_id for env_id in requested if env_id not in ENV_IDS]
    if unknown:
        raise SystemExit(f"unknown env ids: {', '.join(sorted(set(unknown)))}")
    ordered: List[str] = []
    for env_id in requested:
        if env_id not in ordered:
            ordered.append(env_id)
    return ordered


def build_base_prompt(env_id: str) -> str:
    return run_builder(
        [
            sys.executable,
            str(STRUCTURED_MAP_PROMPT_BUILDER),
            "--env-name",
            env_id,
            "--role-mode",
            "critic_only",
        ]
    )


def load_control_surface() -> Dict[str, Dict[str, Any]]:
    payload = read_json(CONTROL_SURFACE_PATH)
    resources = payload.get("resources") or []
    env_resources: Dict[str, Dict[str, Any]] = {}
    template_resources: Dict[str, Dict[str, Any]] = {}
    for resource in resources:
        if not isinstance(resource, dict):
            continue
        label = str(resource.get("label") or "").strip()
        if label in ENV_IDS:
            env_resources[label] = resource
        elif label.endswith("_minimal_example"):
            template_resources[label.replace("_minimal_example", "")] = resource
    return {"env": env_resources, "template": template_resources}


def load_runtime_packet() -> Dict[str, Dict[str, Any]]:
    payload = read_json(RUNTIME_PACKET_PATH)
    return payload.get("envs") or {}


def join_items(values: List[str] | None, fallback: str = "") -> str:
    items = [str(value).strip() for value in (values or []) if str(value).strip()]
    if not items:
        return fallback
    return "; ".join(items)


def render_contract_memory_block(
    *,
    source_label: str,
    answer_shape: str,
    summary: str,
    query_cues: List[str] | None,
    must_do: List[str] | None,
    avoid: List[str] | None,
    validation_path: str,
    minimal_example: str,
    extra_lines: List[str] | None = None,
) -> str:
    lines = [
        "Retrieved contract memory for the current env:",
        f"- source: {source_label}",
        f"- answer_shape: {answer_shape}",
        f"- summary: {summary}",
        f"- query_cues: {join_items(query_cues or [])}",
    ]
    must_do_text = join_items(must_do or [])
    if must_do_text:
        lines.append(f"- must_do: {must_do_text}")
    avoid_text = join_items(avoid or [])
    if avoid_text:
        lines.append(f"- avoid: {avoid_text}")
    if validation_path:
        lines.append(f"- validation_path: {validation_path}")
    for line in extra_lines or []:
        text = str(line).strip()
        if text:
            lines.append(text)
    lines.extend(
        [
            "Minimal valid example:",
            minimal_example,
            "Use this contract memory privately to choose the closest contract-shaped final answer.",
            "Do not mention the retrieval step or contract memory in the final answer.",
        ]
    )
    return "\n".join(lines)


def build_control_prompt(env_id: str, surface: Dict[str, Dict[str, Any]]) -> str:
    base_prompt = build_base_prompt(env_id)
    env_resource = surface["env"][env_id]
    template_resource = surface["template"][env_id]
    memory_block = render_contract_memory_block(
        source_label="primehub_schema_pack (control)",
        answer_shape=str(env_resource.get("answer_shape") or "").strip(),
        summary=str(env_resource.get("summary") or "").strip(),
        query_cues=env_resource.get("query_cues") or [],
        must_do=[],
        avoid=(env_resource.get("failure_modes") or []) + (env_resource.get("known_verifier_gaps") or []),
        validation_path=str(env_resource.get("validation_path") or "").strip(),
        minimal_example=str(template_resource.get("minimal_example") or "").strip(),
        extra_lines=[
            f"- validator_notes: {join_items(env_resource.get('validator_notes') or [])}"
            if env_resource.get("validator_notes")
            else "",
        ],
    )
    return f"{base_prompt}\n\n{memory_block}"


def build_runtime_prompt(env_id: str, runtime_packet: Dict[str, Dict[str, Any]]) -> str:
    base_prompt = build_base_prompt(env_id)
    env_packet = runtime_packet[env_id]
    memory_block = render_contract_memory_block(
        source_label="metta_runtime_packet (compact treatment)",
        answer_shape=str(env_packet.get("answer_shape") or "").strip(),
        summary=str(env_packet.get("summary") or "").strip(),
        query_cues=env_packet.get("query_cues") or [],
        must_do=env_packet.get("must_do") or [],
        avoid=env_packet.get("avoid") or [],
        validation_path=str(env_packet.get("validation_path") or "").strip(),
        minimal_example=str(env_packet.get("minimal_example") or "").strip(),
        extra_lines=[
            f"- repair_focus: {join_items(env_packet.get('repair_focus') or [])}",
            f"- contract_priority: {str(env_packet.get('contract_priority') or '').strip()}",
        ],
    )
    return f"{base_prompt}\n\n{memory_block}"


def command_template_for_arm(arm_id: str) -> str:
    return (
        '"{python_exec}" '
        f'"{REMOTE_BRIDGE.as_posix()}" '
        "--source {env_source} "
        '--host "snacksack-ms-7d32.tail3156cd.ts.net" '
        '--user "snacksack" '
        '--identity-file "C:/Users/patri/.ssh/id_ed25519" '
        '--ssh-timeout-seconds 120 '
        '--research-root "/home/snacksack/prime_repos_tmp/research-environments/environments" '
        '--community-root "/home/snacksack/prime_repos_tmp/community-environments/environments" '
        f'--remote-site-packages "/tmp/prime_env_bridge_site_{arm_id}_{{env_id}}" '
        f'--remote-cache-root "/tmp/prime_env_bridge_cache_{arm_id}_{{env_id}}" '
        "{env_id}"
    )


def bridge_args(env_id: str, arm_id: str, mode: str) -> List[str]:
    mode_flag = "--reset" if mode == "reset" else "--step"
    return [
        sys.executable,
        str(REMOTE_BRIDGE),
        env_id,
        "--source",
        "community",
        mode_flag,
        "--host",
        "snacksack-ms-7d32.tail3156cd.ts.net",
        "--user",
        "snacksack",
        "--identity-file",
        "C:/Users/patri/.ssh/id_ed25519",
        "--ssh-timeout-seconds",
        "120",
        "--research-root",
        "/home/snacksack/prime_repos_tmp/research-environments/environments",
        "--community-root",
        "/home/snacksack/prime_repos_tmp/community-environments/environments",
        "--remote-site-packages",
        f"/tmp/prime_env_bridge_site_{arm_id}_{env_id}",
        "--remote-cache-root",
        f"/tmp/prime_env_bridge_cache_{arm_id}_{env_id}",
    ]


def run_remote_bridge(env_id: str, arm_id: str, mode: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    command = bridge_args(env_id, arm_id, mode)
    result = subprocess.run(
        command,
        input=(json.dumps(payload) if payload is not None else ""),
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
        timeout=240,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or f"remote bridge {mode} failed").strip())
    raw = (result.stdout or "").strip()
    if not raw:
        raise RuntimeError(f"remote bridge {mode} returned empty output")
    response = json.loads(raw)
    if not isinstance(response, dict):
        raise RuntimeError(f"remote bridge {mode} returned non-object payload")
    return response


def first_row(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                return json.loads(line)
    return {}


def parse_episode_summary(row: Dict[str, Any]) -> Dict[str, Any]:
    raw = row.get("episode_summary")
    if not raw:
        raw_env = row.get("raw_env") or {}
        raw = raw_env.get("episode_summary")
    if not raw or not isinstance(raw, str):
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def action_excerpt(text: str, limit: int = 220) -> str:
    clean = " ".join(str(text or "").split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3].rstrip() + "..."


def summarize_generation_result(arm_id: str, env_id: str, export_path: Path, task_result: Dict[str, Any]) -> Dict[str, Any]:
    row = first_row(export_path) if export_path.exists() else {}
    summary = task_result.get("summary") if isinstance(task_result, dict) and isinstance(task_result.get("summary"), dict) else {}
    reward_totals = summary.get("reward_totals") or {}
    episode_summary = parse_episode_summary(row)
    return {
        "arm_id": arm_id,
        "env_id": env_id,
        "status": str(task_result.get("status") or ""),
        "returncode": task_result.get("returncode"),
        "reward": reward_totals.get(env_id),
        "token_usage": summary.get("token_usage") or {},
        "failure_types": summary.get("failure_types") or {},
        "visible_output_emitted": row.get("visible_output_emitted"),
        "output_status": row.get("output_status"),
        "valid_action": row.get("valid_action"),
        "action_type": row.get("action_type"),
        "action_text": str(row.get("action") or ""),
        "action_excerpt": action_excerpt(str(row.get("action") or "")),
        "short_justification": action_excerpt(str(row.get("short_justification") or ""), 180),
        "episode_metrics": episode_summary.get("metrics") or {},
        "export_path": str(export_path),
        "summary_path": str(export_path.with_suffix(".summary.json")),
    }


def summarize_repair_result(
    *,
    env_id: str,
    source_row: Dict[str, Any],
    repair_report: Dict[str, Any],
    scored_payload: Dict[str, Any],
) -> Dict[str, Any]:
    reward = float(scored_payload.get("reward", 0.0) or 0.0)
    metrics = scored_payload.get("metrics") or {}
    repaired_text = str(repair_report.get("repaired_text") or "").strip()
    original_text = str(repair_report.get("original_text") or "").strip()
    return {
        "arm_id": "with_metta_runtime_repair",
        "env_id": env_id,
        "status": "success" if bool(scored_payload.get("valid_action", True)) else "failure",
        "returncode": 0,
        "reward": reward,
        "token_usage": dict(source_row.get("token_usage") or {}),
        "failure_types": {},
        "visible_output_emitted": True,
        "output_status": "completed",
        "valid_action": bool(scored_payload.get("valid_action", True)),
        "action_type": "direct_answer_repaired",
        "action_text": repaired_text,
        "action_excerpt": action_excerpt(repaired_text),
        "short_justification": action_excerpt("Deterministic MeTTa repair pass applied before verifier scoring.", 180),
        "episode_metrics": metrics if isinstance(metrics, dict) else {},
        "export_path": str(source_row.get("export_path") or ""),
        "summary_path": str(source_row.get("summary_path") or ""),
        "repair_applied": repaired_text != original_text,
        "repair_report": {
            "status": repair_report.get("status"),
            "applied_repairs": repair_report.get("applied_repairs") or [],
            "detected_failures": repair_report.get("detected_failures") or [],
        },
    }


def build_repair_result(env_id: str, source_row: Dict[str, Any]) -> Dict[str, Any]:
    original_action = str(source_row.get("action_text") or "").strip()
    env_payload = load_bundle_env(METTA_BUNDLE_ROOT, env_id)
    repair_report = repair_candidate(env_id, original_action, env_payload)
    reset_payload = run_remote_bridge(env_id, "with_metta_runtime_repair", "reset")
    session_state = reset_payload.get("session")
    if not isinstance(session_state, dict):
        raise RuntimeError(f"missing session state for repair scoring on {env_id}")
    scored_payload = run_remote_bridge(
        env_id,
        "with_metta_runtime_repair",
        "step",
        {
            "state": session_state,
            "action": str(repair_report.get("repaired_text") or ""),
        },
    )
    return summarize_repair_result(env_id=env_id, source_row=source_row, repair_report=repair_report, scored_payload=scored_payload)


def render_results_markdown(results: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    lines.append("# Runtime-Packet And Repair Live Eval")
    lines.append("")
    lines.append("| Env | Arm | Reward | Prompt Tokens | Completion Tokens | Repair Applied | Action Excerpt |")
    lines.append("| --- | --- | ---: | ---: | ---: | --- | --- |")
    for result in results:
        token_usage = result.get("token_usage") or {}
        lines.append(
            "| {env} | {arm} | {reward} | {prompt_tokens} | {completion_tokens} | {repair} | {action} |".format(
                env=result["env_id"],
                arm=result["arm_id"],
                reward=result["reward"] if result["reward"] is not None else "-",
                prompt_tokens=token_usage.get("prompt_tokens", "-"),
                completion_tokens=token_usage.get("completion_tokens", "-"),
                repair=result.get("repair_applied", False),
                action=str(result.get("action_excerpt") or "-").replace("|", "\\|"),
            )
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- `without_metta`: control prompt using the non-MeTTa Primehub schema pack.")
    lines.append("- `with_metta_runtime`: compact prompt using `runtime_packet.json`.")
    lines.append("- `with_metta_runtime_repair`: same runtime-packet generation, then deterministic MeTTa repair before remote verifier scoring.")
    lines.append("")
    return "\n".join(lines) + "\n"


def render_findings(results: List[Dict[str, Any]]) -> str:
    by_env: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for result in results:
        by_env.setdefault(str(result["env_id"]), {})[str(result["arm_id"])] = result
    lines: List[str] = []
    lines.append("# Runtime-Packet And Repair Findings")
    lines.append("")
    lines.append("This slice tests whether the compact MeTTa runtime packet and deterministic repair pass beat the control more cleanly than the richer prompt-only MeTTa packet.")
    lines.append("")
    lines.append("## Reward Snapshot")
    lines.append("")
    for env_id in ENV_IDS:
        env_rows = by_env.get(env_id, {})
        lines.append(f"- `{env_id}`")
        lines.append(f"  - without_metta: `{env_rows.get('without_metta', {}).get('reward')}`")
        lines.append(f"  - with_metta_runtime: `{env_rows.get('with_metta_runtime', {}).get('reward')}`")
        lines.append(f"  - with_metta_runtime_repair: `{env_rows.get('with_metta_runtime_repair', {}).get('reward')}`")
    lines.append("")
    lines.append("## Token Snapshot")
    lines.append("")
    for env_id in ENV_IDS:
        env_rows = by_env.get(env_id, {})
        control_tokens = (env_rows.get("without_metta", {}).get("token_usage") or {}).get("prompt_tokens")
        runtime_tokens = (env_rows.get("with_metta_runtime", {}).get("token_usage") or {}).get("prompt_tokens")
        lines.append(f"- `{env_id}`: control prompt tokens `{control_tokens}`, runtime packet prompt tokens `{runtime_tokens}`")
    lines.append("")
    lines.append("## Read")
    lines.append("")
    for env_id in ENV_IDS:
        env_rows = by_env.get(env_id, {})
        control_reward = env_rows.get("without_metta", {}).get("reward")
        runtime_reward = env_rows.get("with_metta_runtime", {}).get("reward")
        repair_reward = env_rows.get("with_metta_runtime_repair", {}).get("reward")
        notes: List[str] = []
        if isinstance(control_reward, (int, float)) and isinstance(runtime_reward, (int, float)):
            delta = runtime_reward - control_reward
            if delta > 0:
                notes.append(f"runtime packet beat control by `{delta:.4f}`")
            elif delta < 0:
                notes.append(f"runtime packet trailed control by `{abs(delta):.4f}`")
            else:
                notes.append("runtime packet matched control")
        if isinstance(runtime_reward, (int, float)) and isinstance(repair_reward, (int, float)):
            delta = repair_reward - runtime_reward
            if delta > 0:
                notes.append(f"repair improved runtime scoring by `{delta:.4f}`")
            elif delta < 0:
                notes.append(f"repair hurt runtime scoring by `{abs(delta):.4f}`")
            else:
                notes.append("repair did not change the verifier score")
        repair_meta = env_rows.get("with_metta_runtime_repair", {}).get("repair_report") or {}
        applied_repairs = repair_meta.get("applied_repairs") or []
        if applied_repairs:
            notes.append(f"repairs applied: {join_items(applied_repairs)}")
        lines.append(f"- `{env_id}`: " + "; ".join(notes))
    lines.append("")
    lines.append("## Takeaway")
    lines.append("")
    runtime_wins = 0
    repair_wins = 0
    for env_id in ENV_IDS:
        env_rows = by_env.get(env_id, {})
        control_reward = env_rows.get("without_metta", {}).get("reward")
        runtime_reward = env_rows.get("with_metta_runtime", {}).get("reward")
        repair_reward = env_rows.get("with_metta_runtime_repair", {}).get("reward")
        if isinstance(control_reward, (int, float)) and isinstance(runtime_reward, (int, float)) and runtime_reward >= control_reward:
            runtime_wins += 1
        if isinstance(control_reward, (int, float)) and isinstance(repair_reward, (int, float)) and repair_reward >= control_reward:
            repair_wins += 1
    if repair_wins == len(ENV_IDS):
        takeaway = "The compact runtime packet plus repair path now clears the control on every held env, with repair providing the safer scoring surface."
    elif runtime_wins == len(ENV_IDS):
        takeaway = "The compact runtime packet already clears the control on every held env; repair is useful but not yet decisive on this slice."
    else:
        takeaway = "The compact packet and repair path are implemented, but the slice is still mixed and needs a broader or harder benchmark."
    lines.append(takeaway)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    env_ids = resolve_env_ids(args)
    artifacts_root = Path(args.output_dir).resolve()
    results_json = artifacts_root / "runtime_packet_repair.results.json"
    results_md = artifacts_root / "runtime_packet_repair.results.md"
    findings_md = artifacts_root / "runtime_packet_repair.findings.md"
    artifacts_root.mkdir(parents=True, exist_ok=True)

    for required_path in [CONTROL_SURFACE_PATH, RUNTIME_PACKET_PATH]:
        if not required_path.exists():
            raise SystemExit(f"missing required artifact: {required_path}")

    model = ModelProfile(
        model_id=args.model_id,
        base_url=args.base_url,
        model_name=args.model_name,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        request_timeout=args.request_timeout,
    )

    control_surface = load_control_surface()
    runtime_packet = load_runtime_packet()
    generation_arms = [
        {
            "arm_id": "without_metta",
            "variant_id": "structured-map-without-metta",
            "skill_name": "primehub-structured-map-hermes+trm-mcp",
            "skill_cluster": "structured_map",
            "skill_prompt_by_env": {env_id: build_control_prompt(env_id, control_surface) for env_id in env_ids},
        },
        {
            "arm_id": "with_metta_runtime",
            "variant_id": "structured-map-with-metta-runtime",
            "skill_name": "primehub-structured-map-hermes+metta-runtime",
            "skill_cluster": "structured_map",
            "skill_prompt_by_env": {env_id: build_runtime_prompt(env_id, runtime_packet) for env_id in env_ids},
        },
    ]

    results: List[Dict[str, Any]] = []
    runtime_rows: Dict[str, Dict[str, Any]] = {}
    for arm in generation_arms:
        arm_id = str(arm["arm_id"])
        command_template = command_template_for_arm(arm_id)
        for env_id in env_ids:
            export_path = artifacts_root / "replays" / arm_id / f"{env_id}.jsonl"
            config_path = artifacts_root / "configs" / arm_id / f"{env_id}.json"
            config_obj = build_config(
                model=model,
                env_id=env_id,
                env_name=env_id,
                env_source="community",
                env_owner="community",
                env_folder=env_id,
                export_path=export_path,
                python_exec=sys.executable,
                command_template=command_template,
                env_mode="primehub",
                variant_id=str(arm["variant_id"]),
                reasoning_mode="off",
                skill_name=str(arm["skill_name"]),
                skill_prompt=str((arm["skill_prompt_by_env"] or {}).get(env_id, "")),
                skill_cluster=str(arm["skill_cluster"]),
                role_mode="critic_only",
                role_support_tier="format_support",
                role_gate_applied=True,
                role_gate_downgraded=False,
                role_gate_reason="",
            )
            config_obj["max_steps_per_episode"] = 1
            success, task_result, _, _ = run_one_task(
                trm_root=TRM_ROOT,
                python_exec=sys.executable,
                config_path=config_path,
                config_obj=config_obj,
                export_path=export_path,
                episodes=1,
                token_budget=None,
                task_key=f"{model.model_id}:{arm_id}:{env_id}",
                task_timeout=900,
            )
            row = summarize_generation_result(arm_id, env_id, export_path, task_result)
            row["success"] = success
            results.append(row)
            if arm_id == "with_metta_runtime":
                runtime_rows[env_id] = row

    for env_id in env_ids:
        source_row = runtime_rows.get(env_id)
        if not source_row:
            continue
        repair_row = build_repair_result(env_id, source_row)
        results.append(repair_row)

    payload = {
        "model": {
            "model_id": model.model_id,
            "base_url": model.base_url,
            "model_name": model.model_name,
        },
        "envs": env_ids,
        "results": results,
    }
    results_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    results_md.write_text(render_results_markdown(results), encoding="utf-8")
    findings_md.write_text(render_findings(results), encoding="utf-8")
    print(str(results_json))
    print(str(results_md))
    print(str(findings_md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
