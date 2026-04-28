from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


STUDY_ROOT = Path(__file__).resolve().parent
REPO_ROOT = STUDY_ROOT.parents[2]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
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
METTA_PACKET_PATH = METTA_BUNDLE_ROOT / "retrieval_packet.json"
METTA_CRITIC_HINTS_PATH = METTA_BUNDLE_ROOT / "critic_hints.json"
METTA_TRACE_LABELS_PATH = METTA_BUNDLE_ROOT / "trace_labels.json"

if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from overnight_primehub_benchmark import ModelProfile, build_config, run_one_task  # noqa: E402


ENV_IDS = ["psycho_bench", "ascii_tree", "pydantic_adherence"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a with-MeTTa vs without-MeTTa live eval on Primehub structured-map envs.")
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
        default=str(STUDY_ROOT / "artifacts" / "live_eval_qwen35_9b_with_vs_without_metta"),
    )
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not decode to an object")
    return payload


def run_builder(command: List[str]) -> str:
    import subprocess

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
    return {
        "env": env_resources,
        "template": template_resources,
    }


def load_metta_bundle() -> Dict[str, Dict[str, Any]]:
    packet = read_json(METTA_PACKET_PATH)
    critic_hints = read_json(METTA_CRITIC_HINTS_PATH)
    trace_labels = read_json(METTA_TRACE_LABELS_PATH)
    return {
        "packet": packet.get("envs") or {},
        "critic_hints": critic_hints.get("envs") or {},
        "trace_labels": trace_labels.get("envs") or {},
    }


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
    failure_modes: List[str] | None,
    validation_path: str,
    validator_notes: List[str] | None,
    known_verifier_gaps: List[str] | None,
    minimal_example: str,
    example_status: str,
    extra_lines: List[str] | None = None,
) -> str:
    lines = [
        "Retrieved contract memory for the current env:",
        f"- source: {source_label}",
        f"- answer_shape: {answer_shape}",
        f"- summary: {summary}",
        f"- query_cues: {join_items(query_cues or [])}",
        f"- failure_modes: {join_items(failure_modes or [])}",
    ]
    if validation_path:
        lines.append(f"- validation_path: {validation_path}")
    validator_notes_text = join_items(validator_notes or [])
    if validator_notes_text:
        lines.append(f"- validator_notes: {validator_notes_text}")
    verifier_gaps_text = join_items(known_verifier_gaps or [])
    if verifier_gaps_text:
        lines.append(f"- known_verifier_gaps: {verifier_gaps_text}")
    for line in extra_lines or []:
        text = str(line).strip()
        if text:
            lines.append(text)
    heading = "Minimal valid example:" if example_status == "validated_minimal_example" else "Best-effort shape example:"
    lines.extend(
        [
            heading,
            minimal_example,
            "Use this contract memory privately to choose the closest contract-shaped final answer.",
            "Do not mention the retrieval step or contract memory in the final answer.",
        ]
    )
    return "\n".join(lines)


def build_without_metta_prompt(env_id: str, surface: Dict[str, Dict[str, Any]]) -> str:
    base_prompt = build_base_prompt(env_id)
    env_resource = surface["env"][env_id]
    template_resource = surface["template"][env_id]
    minimal_example = str(template_resource.get("minimal_example") or "").strip()
    example_status = str(template_resource.get("example_status") or env_resource.get("example_status") or "validated_minimal_example").strip()
    memory_block = render_contract_memory_block(
        source_label="primehub_schema_pack (non-MeTTa control)",
        answer_shape=str(env_resource.get("answer_shape") or "").strip(),
        summary=str(env_resource.get("summary") or "").strip(),
        query_cues=env_resource.get("query_cues") or [],
        failure_modes=env_resource.get("failure_modes") or [],
        validation_path=str(env_resource.get("validation_path") or "").strip(),
        validator_notes=env_resource.get("validator_notes") or [],
        known_verifier_gaps=env_resource.get("known_verifier_gaps") or [],
        minimal_example=minimal_example,
        example_status=example_status,
    )
    return f"{base_prompt}\n\n{memory_block}"


def build_with_metta_prompt(env_id: str, bundle: Dict[str, Dict[str, Any]]) -> str:
    base_prompt = build_base_prompt(env_id)
    packet_env = bundle["packet"][env_id]
    critic_env = bundle["critic_hints"].get(env_id) or {}
    trace_env = bundle["trace_labels"].get(env_id) or {}
    extra_lines = []
    retrieval_priorities = join_items(packet_env.get("retrieval_priorities") or [])
    if retrieval_priorities:
        extra_lines.append(f"- retrieval_priorities: {retrieval_priorities}")
    checks = critic_env.get("checks") or []
    if checks:
        extra_lines.append(f"- compiled_checks: {join_items(checks)}")
    repair_hints = packet_env.get("repair_hints") or trace_env.get("repair_hints") or critic_env.get("repair_hints") or []
    if repair_hints:
        extra_lines.append(f"- repair_hints: {join_items(repair_hints)}")
    trace_labels = packet_env.get("trace_labels") or trace_env.get("trace_labels") or []
    if trace_labels:
        extra_lines.append(f"- trace_labels: {join_items(trace_labels)}")
    memory_block = render_contract_memory_block(
        source_label="metta_compiled_bundle (treatment)",
        answer_shape=str(packet_env.get("answer_shape") or critic_env.get("required_shape") or "").strip(),
        summary=str(packet_env.get("summary") or "").strip(),
        query_cues=packet_env.get("query_cues") or [],
        failure_modes=packet_env.get("failure_modes") or trace_env.get("failure_modes") or [],
        validation_path=str(packet_env.get("validation_path") or "").strip(),
        validator_notes=packet_env.get("validator_notes") or [],
        known_verifier_gaps=packet_env.get("known_verifier_gaps") or [],
        minimal_example=str(packet_env.get("minimal_example") or "").strip(),
        example_status=str(packet_env.get("example_status") or "validated_minimal_example").strip(),
        extra_lines=extra_lines,
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


def summarize_result(arm_id: str, env_id: str, export_path: Path, task_result: Dict[str, Any]) -> Dict[str, Any]:
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
        "action_excerpt": action_excerpt(str(row.get("action") or "")),
        "short_justification": action_excerpt(str(row.get("short_justification") or ""), 180),
        "episode_metrics": episode_summary.get("metrics") or {},
        "export_path": str(export_path),
        "summary_path": str(export_path.with_suffix(".summary.json")),
    }


def render_results_markdown(results: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    lines.append("# With-MeTTa Vs Without-MeTTa Live Eval")
    lines.append("")
    lines.append("| Env | Arm | Status | Reward | Visible Output | Action Type | Action Excerpt |")
    lines.append("| --- | --- | --- | ---: | --- | --- | --- |")
    for result in results:
        lines.append(
            "| {env} | {arm} | {status} | {reward} | {visible} | {atype} | {action} |".format(
                env=result["env_id"],
                arm=result["arm_id"],
                status=result["status"],
                reward=result["reward"] if result["reward"] is not None else "-",
                visible=result["visible_output_emitted"],
                atype=result["action_type"] or "-",
                action=str(result["action_excerpt"] or "-").replace("|", "\\|"),
            )
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- `without_metta`: base `primehub-structured-map-hermes` prompt plus the existing non-MeTTa Primehub schema pack.")
    lines.append("- `with_metta`: base `primehub-structured-map-hermes` prompt plus the compiled MeTTa retrieval packet and critic hints.")
    lines.append("")
    return "\n".join(lines) + "\n"


def render_findings(results: List[Dict[str, Any]]) -> str:
    by_env: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for result in results:
        by_env.setdefault(str(result["env_id"]), {})[str(result["arm_id"])] = result
    lines: List[str] = []
    lines.append("# With-MeTTa Vs Without-MeTTa Findings")
    lines.append("")
    lines.append("This slice isolates the retrieval memory source while keeping the base structured-map prompt fixed.")
    lines.append("")
    lines.append("## Reward Snapshot")
    lines.append("")
    for env_id in ENV_IDS:
        env_rows = by_env.get(env_id, {})
        without_row = env_rows.get("without_metta", {})
        with_row = env_rows.get("with_metta", {})
        lines.append(f"- `{env_id}`")
        lines.append(f"  - without_metta: `{without_row.get('reward')}`")
        lines.append(f"  - with_metta: `{with_row.get('reward')}`")
    lines.append("")
    lines.append("## Read")
    lines.append("")
    for env_id in ENV_IDS:
        env_rows = by_env.get(env_id, {})
        without_reward = env_rows.get("without_metta", {}).get("reward")
        with_reward = env_rows.get("with_metta", {}).get("reward")
        if isinstance(without_reward, (int, float)) and isinstance(with_reward, (int, float)):
            delta = with_reward - without_reward
            if delta > 0:
                read = f"`with_metta` improved over `without_metta` by `{delta:.4f}`."
            elif delta < 0:
                read = f"`with_metta` underperformed `without_metta` by `{abs(delta):.4f}`."
            else:
                read = "`with_metta` matched `without_metta`."
        else:
            read = "One or both arms did not return a numeric reward."
        lines.append(f"- `{env_id}`: {read}")
    lines.append("")
    lines.append("## Takeaway")
    lines.append("")
    wins = 0
    losses = 0
    for env_id in ENV_IDS:
        env_rows = by_env.get(env_id, {})
        without_reward = env_rows.get("without_metta", {}).get("reward")
        with_reward = env_rows.get("with_metta", {}).get("reward")
        if isinstance(without_reward, (int, float)) and isinstance(with_reward, (int, float)):
            if with_reward > without_reward:
                wins += 1
            elif with_reward < without_reward:
                losses += 1
    if wins and not losses:
        takeaway = "The MeTTa treatment outperformed the non-MeTTa control on every scored env in this slice."
    elif wins > losses:
        takeaway = "The MeTTa treatment showed a net positive effect, but it is not a clean sweep."
    elif losses > wins:
        takeaway = "The non-MeTTa control remains stronger on this slice."
    else:
        takeaway = "The slice is mixed or flat; the MeTTa treatment is not yet clearly superior."
    lines.append(takeaway)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    env_ids = resolve_env_ids(args)
    artifacts_root = Path(args.output_dir).resolve()
    results_json = artifacts_root / "with_vs_without_metta.results.json"
    results_md = artifacts_root / "with_vs_without_metta.results.md"
    findings_md = artifacts_root / "with_vs_without_metta.findings.md"
    artifacts_root.mkdir(parents=True, exist_ok=True)

    for required_path in [CONTROL_SURFACE_PATH, METTA_PACKET_PATH, METTA_CRITIC_HINTS_PATH, METTA_TRACE_LABELS_PATH]:
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
    metta_bundle = load_metta_bundle()
    arms = [
        {
            "arm_id": "without_metta",
            "variant_id": "structured-map-without-metta",
            "skill_name": "primehub-structured-map-hermes+trm-mcp",
            "skill_cluster": "structured_map",
            "skill_prompt_by_env": {env_id: build_without_metta_prompt(env_id, control_surface) for env_id in env_ids},
        },
        {
            "arm_id": "with_metta",
            "variant_id": "structured-map-with-metta",
            "skill_name": "primehub-structured-map-hermes+metta-trm",
            "skill_cluster": "structured_map",
            "skill_prompt_by_env": {env_id: build_with_metta_prompt(env_id, metta_bundle) for env_id in env_ids},
        },
    ]

    results: List[Dict[str, Any]] = []
    for arm in arms:
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
            result_row = summarize_result(arm_id, env_id, export_path, task_result)
            result_row["success"] = success
            results.append(result_row)

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
