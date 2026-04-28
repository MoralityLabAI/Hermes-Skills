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
REMOTE_BRIDGE = REPO_ROOT / "scripts" / "remote_prime_env_bridge.py"
SLICE_MANIFEST_PATH = STUDY_ROOT / "artifacts" / "nuanced_env_slice" / "nuanced_env_slice.json"

if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from overnight_primehub_benchmark import ModelProfile, build_config, run_one_task  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the curated nuanced benchmark slice with a baseline no-skill arm.")
    parser.add_argument("--bundle", default="core_ready", choices=["core_ready", "expanded_ready", "blocked_high_value", "research_candidates"])
    parser.add_argument("--env-id", action="append", dest="env_ids", default=[], help="Optional env ids to override the bundle.")
    parser.add_argument("--manifest-json", default=str(SLICE_MANIFEST_PATH))
    parser.add_argument("--model-id", default="qwen35_9b")
    parser.add_argument("--base-url", default="http://snacksack-ms-7d32.tail3156cd.ts.net:8082/v1")
    parser.add_argument("--model-name", default="Qwen_Qwen3.5-9B-Q4_K_M.gguf")
    parser.add_argument("--max-new-tokens", type=int, default=480)
    parser.add_argument("--request-timeout", type=int, default=240)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--output-dir",
        default=str(STUDY_ROOT / "artifacts" / "live_eval_qwen35_9b_nuanced_slice"),
    )
    return parser.parse_args()


def load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not decode to an object")
    return payload


def first_row(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                payload = json.loads(text)
                return payload if isinstance(payload, dict) else {}
    return {}


def action_excerpt(text: str, limit: int = 220) -> str:
    clean = " ".join(str(text or "").split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3].rstrip() + "..."


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


def command_template() -> str:
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
        '--remote-site-packages "/tmp/prime_env_bridge_site_nuanced_{env_id}" '
        '--remote-cache-root "/tmp/prime_env_bridge_cache_nuanced_{env_id}" '
        "{env_id}"
    )


def resolve_entries(args: argparse.Namespace, manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    entries = {str(entry.get("env_id") or "").strip(): entry for entry in (manifest.get("envs") or []) if isinstance(entry, dict)}
    requested = [str(env_id).strip() for env_id in (args.env_ids or []) if str(env_id).strip()]
    if requested:
        missing = [env_id for env_id in requested if env_id not in entries]
        if missing:
            raise SystemExit(f"unknown env ids: {', '.join(sorted(set(missing)))}")
        return [entries[env_id] for env_id in requested]
    bundle_envs = list((manifest.get("bundles") or {}).get(args.bundle) or [])
    return [entries[env_id] for env_id in bundle_envs if env_id in entries]


def summarize_result(entry: Dict[str, Any], export_path: Path, task_result: Dict[str, Any]) -> Dict[str, Any]:
    row = first_row(export_path)
    summary = task_result.get("summary") if isinstance(task_result.get("summary"), dict) else {}
    reward_totals = summary.get("reward_totals") or {}
    env_id = str(entry.get("env_id") or "")
    episode_summary = parse_episode_summary(row)
    manifest_profile = entry.get("manifest_profile") or {}
    return {
        "env_id": env_id,
        "selection_status": entry.get("selection_status"),
        "env_source": manifest_profile.get("source"),
        "status": str(task_result.get("status") or ""),
        "returncode": task_result.get("returncode"),
        "reward": reward_totals.get(env_id),
        "token_usage": summary.get("token_usage") or {},
        "visible_output_emitted": row.get("visible_output_emitted"),
        "output_status": row.get("output_status"),
        "valid_action": row.get("valid_action"),
        "action_type": row.get("action_type"),
        "action_excerpt": action_excerpt(str(row.get("action") or "")),
        "observation_excerpt": action_excerpt(str(row.get("observation") or ""), 200),
        "episode_metrics": episode_summary.get("metrics") or {},
        "export_path": str(export_path),
    }


def render_markdown(results: List[Dict[str, Any]], bundle: str, dry_run: bool) -> str:
    lines: List[str] = []
    lines.append("# Nuanced Slice Baseline Eval")
    lines.append("")
    lines.append(f"- bundle: `{bundle}`")
    lines.append(f"- dry_run: `{str(dry_run).lower()}`")
    lines.append("")
    lines.append("| Env | Status | Source | Reward | Output Status | Action Type | Action Excerpt |")
    lines.append("| --- | --- | --- | ---: | --- | --- | --- |")
    for result in results:
        lines.append(
            "| {env} | {status} | {source} | {reward} | {output_status} | {action_type} | {action} |".format(
                env=result.get("env_id"),
                status=result.get("selection_status"),
                source=result.get("env_source") or "-",
                reward=result.get("reward") if result.get("reward") is not None else "-",
                output_status=result.get("output_status") or "-",
                action_type=result.get("action_type") or "-",
                action=str(result.get("action_excerpt") or "-").replace("|", "\\|"),
            )
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    manifest = load_json(Path(args.manifest_json).resolve())
    entries = resolve_entries(args, manifest)
    if not entries:
        raise SystemExit("no envs selected")

    artifacts_root = Path(args.output_dir).resolve() / args.bundle
    artifacts_root.mkdir(parents=True, exist_ok=True)
    results_json = artifacts_root / "nuanced_slice_baseline.results.json"
    results_md = artifacts_root / "nuanced_slice_baseline.results.md"

    if args.dry_run:
        results = []
        for entry in entries:
            manifest_profile = entry.get("manifest_profile") or {}
            results.append(
                {
                    "env_id": entry.get("env_id"),
                    "selection_status": entry.get("selection_status"),
                    "env_source": manifest_profile.get("source"),
                    "status": "dry_run",
                    "reward": None,
                    "output_status": "",
                    "action_type": "",
                    "action_excerpt": str(entry.get("why_now") or ""),
                }
            )
        payload = {"bundle": args.bundle, "dry_run": True, "results": results}
        results_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        results_md.write_text(render_markdown(results, args.bundle, True), encoding="utf-8")
        print(str(results_json))
        print(str(results_md))
        return 0

    model = ModelProfile(
        model_id=args.model_id,
        base_url=args.base_url,
        model_name=args.model_name,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        request_timeout=args.request_timeout,
    )

    results: List[Dict[str, Any]] = []
    for entry in entries:
        env_id = str(entry.get("env_id") or "")
        manifest_profile = entry.get("manifest_profile") or {}
        env_source = str(manifest_profile.get("source") or "community")
        env_owner = str(manifest_profile.get("owner") or env_source)
        env_folder = str(manifest_profile.get("folder") or env_id)
        export_path = artifacts_root / "replays" / f"{env_id}.jsonl"
        config_path = artifacts_root / "configs" / f"{env_id}.json"
        config_obj = build_config(
            model=model,
            env_id=env_id,
            env_name=env_id,
            env_source=env_source,
            env_owner=env_owner,
            env_folder=env_folder,
            export_path=export_path,
            python_exec=sys.executable,
            command_template=command_template(),
            env_mode="primehub",
            variant_id=f"nuanced-slice-baseline-{args.bundle}",
            reasoning_mode="off",
            skill_name="",
            skill_prompt="",
            skill_cluster="",
            role_mode="",
            role_support_tier="",
            role_gate_applied=False,
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
            task_key=f"{model.model_id}:nuanced:{args.bundle}:{env_id}",
            task_timeout=1200,
        )
        row = summarize_result(entry, export_path, task_result)
        row["success"] = success
        results.append(row)

    payload = {
        "bundle": args.bundle,
        "dry_run": False,
        "model": {
            "model_id": model.model_id,
            "base_url": model.base_url,
            "model_name": model.model_name,
        },
        "results": results,
    }
    results_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    results_md.write_text(render_markdown(results, args.bundle, False), encoding="utf-8")
    print(str(results_json))
    print(str(results_md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
