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
TRM_ROOT = Path(r"C:/projects/trm_observability_harness")
SCHEMA_PACK_ROOT = STUDY_ROOT / "artifacts" / "primehub_schema_pack"
STRUCTURED_MAP_PROMPT_BUILDER = REPO_ROOT / "primehub-structured-map-hermes" / "scripts" / "build_skill_prompt.py"
TRM_MCP_PROMPT_BUILDER = REPO_ROOT / "trm-mcp" / "scripts" / "build_skill_prompt.py"
REMOTE_BRIDGE = REPO_ROOT / "scripts" / "remote_prime_env_bridge.py"
SURFACE_PATH = SCHEMA_PACK_ROOT / "primehub_schema_surface.json"

if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from overnight_primehub_benchmark import ModelProfile, build_config, run_one_task  # noqa: E402


ENV_IDS = ["psycho_bench", "ascii_tree", "pydantic_adherence"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run live held eval for Primehub structured-map retrieval study.")
    parser.add_argument("--env-id", action="append", dest="env_ids", default=[], help="Optional env id to run. Repeat to include multiple envs.")
    parser.add_argument("--model-id", default="qwen35_9b")
    parser.add_argument("--base-url", default="http://snacksack-ms-7d32.tail3156cd.ts.net:8082/v1")
    parser.add_argument("--model-name", default="Qwen_Qwen3.5-9B-Q4_K_M.gguf")
    parser.add_argument("--max-new-tokens", type=int, default=320)
    parser.add_argument("--request-timeout", type=int, default=180)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--output-dir", default=str(STUDY_ROOT / "artifacts" / "live_eval_qwen35_9b"))
    return parser.parse_args()


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


def load_surface() -> Dict[str, Dict[str, Any]]:
    payload = json.loads(SURFACE_PATH.read_text(encoding="utf-8"))
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


def resolve_env_ids(args: argparse.Namespace) -> List[str]:
    requested = [str(env_id).strip() for env_id in (args.env_ids or []) if str(env_id).strip()]
    if not requested:
        return list(ENV_IDS)
    unknown = [env_id for env_id in requested if env_id not in ENV_IDS]
    if unknown:
        raise SystemExit(f"unknown env ids: {', '.join(sorted(set(unknown)))}")
    ordered = []
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


def build_retrieval_assisted_prompt(env_id: str, surface: Dict[str, Dict[str, Any]]) -> str:
    base_prompt = build_base_prompt(env_id)
    trm_prompt = run_builder(
        [
            sys.executable,
            str(TRM_MCP_PROMPT_BUILDER),
            "--mcp-name",
            "primehub_schema",
            "--mode",
            "retrieve",
        ]
    )
    env_resource = surface["env"][env_id]
    template_resource = surface["template"][env_id]
    query_cues = ", ".join(str(item) for item in env_resource.get("query_cues") or [])
    failure_modes = "; ".join(str(item) for item in env_resource.get("failure_modes") or [])
    validator_notes = "; ".join(str(item) for item in env_resource.get("validator_notes") or [])
    verifier_gaps = "; ".join(str(item) for item in env_resource.get("known_verifier_gaps") or [])
    validation_path = str(env_resource.get("validation_path") or "").strip()
    minimal_example = str(template_resource.get("minimal_example") or "").strip()
    example_status = str(template_resource.get("example_status") or env_resource.get("example_status") or "validated_minimal_example").strip()
    example_heading = "Minimal valid example:" if example_status == "validated_minimal_example" else "Best-effort shape example:"
    lines = [
        "Retrieved schema memory for the current env:",
        f"- resource_uri: {env_resource.get('uri', '')}",
        f"- answer_shape: {env_resource.get('answer_shape', '')}",
        f"- summary: {env_resource.get('summary', '')}",
        f"- query_cues: {query_cues}",
        f"- failure_modes: {failure_modes}",
    ]
    if validation_path:
        lines.append(f"- validation_path: {validation_path}")
    if validator_notes:
        lines.append(f"- validator_notes: {validator_notes}")
    if verifier_gaps:
        lines.append(f"- known_verifier_gaps: {verifier_gaps}")
    lines.extend(
        [
            example_heading,
            minimal_example,
            "Use this retrieved schema memory privately to choose the closest contract-shaped final answer.",
            "Do not mention the retrieval step, schema memory, or resource URIs in the final answer.",
        ]
    )
    retrieval_memory = "\n".join(lines)
    return f"{base_prompt}\n{trm_prompt}\n{retrieval_memory}".strip()


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


def summarize_result(
    arm_id: str,
    env_id: str,
    export_path: Path,
    task_result: Dict[str, Any],
) -> Dict[str, Any]:
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


def render_markdown(results: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    lines.append("# Structured-Map Live Eval")
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
    lines.append("- `baseline`: no Hermes structured-map prompt.")
    lines.append("- `plain_structured_map`: base `primehub-structured-map-hermes` prompt only.")
    lines.append("- `retrieval_assisted`: base structured-map prompt plus Primehub schema memory from `primehub_schema_pack`.")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    env_ids = resolve_env_ids(args)
    artifacts_root = Path(args.output_dir).resolve()
    results_json = artifacts_root / "structured_map_live_eval.results.json"
    results_md = artifacts_root / "structured_map_live_eval.results.md"
    artifacts_root.mkdir(parents=True, exist_ok=True)
    if not SURFACE_PATH.exists():
        raise SystemExit(f"missing schema surface: {SURFACE_PATH}")
    model = ModelProfile(
        model_id=args.model_id,
        base_url=args.base_url,
        model_name=args.model_name,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        request_timeout=args.request_timeout,
    )

    surface = load_surface()
    arms = [
        {
            "arm_id": "baseline",
            "variant_id": "structured-map-baseline",
            "skill_name": "",
            "skill_cluster": "",
            "skill_prompt_by_env": {},
        },
        {
            "arm_id": "plain_structured_map",
            "variant_id": "structured-map-plain",
            "skill_name": "primehub-structured-map-hermes",
            "skill_cluster": "structured_map",
            "skill_prompt_by_env": {env_id: build_base_prompt(env_id) for env_id in env_ids},
        },
        {
            "arm_id": "retrieval_assisted",
            "variant_id": "structured-map-retrieval-assisted",
            "skill_name": "primehub-structured-map-hermes+trm-mcp",
            "skill_cluster": "structured_map",
            "skill_prompt_by_env": {env_id: build_retrieval_assisted_prompt(env_id, surface) for env_id in env_ids},
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
                role_mode="critic_only" if arm_id != "baseline" else "",
                role_support_tier="format_support" if arm_id != "baseline" else "",
                role_gate_applied=arm_id != "baseline",
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
    results_md.write_text(render_markdown(results), encoding="utf-8")
    print(str(results_json))
    print(str(results_md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
