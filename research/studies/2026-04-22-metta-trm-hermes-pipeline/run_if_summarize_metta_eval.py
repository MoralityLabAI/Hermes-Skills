from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


STUDY_ROOT = Path(__file__).resolve().parent
REPO_ROOT = STUDY_ROOT.parents[2]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
PIPELINE_SCRIPTS_ROOT = REPO_ROOT / "metta-trm-hermes-pipeline" / "scripts"
TRM_ROOT = Path(r"C:/projects/trm_observability_harness")
PROMPT_BUILDER = REPO_ROOT / "primehub-constraint-summarize-hermes" / "scripts" / "build_skill_prompt.py"
RUNTIME_PACKET_PATH = STUDY_ROOT / "artifacts" / "if_summarize_judge_bundle" / "runtime_packet.json"
METTA_BUNDLE_ROOT = STUDY_ROOT / "artifacts" / "if_summarize_judge_bundle"
SLICE_MANIFEST_PATH = STUDY_ROOT / "artifacts" / "nuanced_env_slice" / "nuanced_env_slice.json"
REMOTE_BRIDGE = REPO_ROOT / "scripts" / "remote_prime_env_bridge.py"
ENV_ID = "if_summarize_judge"
JUDGE_BASE_URL = "http://snacksack-ms-7d32.tail3156cd.ts.net:8082/v1"
JUDGE_MODEL = "Qwen_Qwen3.5-9B-Q4_K_M.gguf"

if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))
if str(PIPELINE_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(PIPELINE_SCRIPTS_ROOT))

from metta_repair_pass import load_bundle_env, repair_candidate, selected_profile_id  # noqa: E402
from overnight_primehub_benchmark import ModelProfile, build_config, run_one_task  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run baseline vs MeTTa runtime eval for if_summarize_judge.")
    parser.add_argument("--seed", action="append", dest="seeds", type=int, default=[])
    parser.add_argument("--model-id", default="qwen35_9b")
    parser.add_argument("--base-url", default="http://snacksack-ms-7d32.tail3156cd.ts.net:8082/v1")
    parser.add_argument("--model-name", default="Qwen_Qwen3.5-9B-Q4_K_M.gguf")
    parser.add_argument("--max-new-tokens", type=int, default=240)
    parser.add_argument("--request-timeout", type=int, default=240)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument(
        "--output-dir",
        default=str(STUDY_ROOT / "artifacts" / "live_eval_qwen35_9b_if_summarize_with_metta_repair"),
    )
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not decode to an object")
    return payload


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            text = raw.strip()
            if not text:
                continue
            payload = json.loads(text)
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


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


def join_items(values: Iterable[str] | None) -> str:
    items = [str(value).strip() for value in (values or []) if str(value).strip()]
    return "; ".join(items)


def action_excerpt(text: str, limit: int = 220) -> str:
    clean = " ".join(str(text or "").split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3].rstrip() + "..."


def load_runtime_env() -> Dict[str, Any]:
    payload = read_json(RUNTIME_PACKET_PATH)
    envs = payload.get("envs") or {}
    runtime_env = envs.get(ENV_ID)
    if not isinstance(runtime_env, dict):
        raise RuntimeError(f"missing env {ENV_ID!r} in {RUNTIME_PACKET_PATH}")
    return runtime_env


def load_manifest_profile() -> Dict[str, Any]:
    payload = read_json(SLICE_MANIFEST_PATH)
    envs = payload.get("envs") or []
    for entry in envs:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("env_id") or "").strip() != ENV_ID:
            continue
        manifest_profile = entry.get("manifest_profile") or {}
        if isinstance(manifest_profile, dict):
            return manifest_profile
    raise RuntimeError(f"missing manifest profile for {ENV_ID}")


def build_base_prompt() -> str:
    return run_builder(
        [
            sys.executable,
            str(PROMPT_BUILDER),
            "--env-name",
            ENV_ID,
            "--role-mode",
            "critic_only",
        ]
    )


def render_profile_catalog(runtime_env: Dict[str, Any]) -> str:
    profiles = runtime_env.get("profiles") or {}
    if not isinstance(profiles, dict) or not profiles:
        return ""
    lines = ["Profile lookup table:"]
    for profile_id in sorted(str(key) for key in profiles.keys()):
        profile_payload = profiles.get(profile_id) or {}
        summary = str(profile_payload.get("summary") or "").strip()
        cues = join_items(profile_payload.get("query_cues") or [])
        rule = f"- {profile_id}: {summary}"
        if cues:
            rule += f" | cues: {cues}"
        lines.append(rule)
    return "\n".join(lines)


def build_without_metta_prompt() -> str:
    return build_base_prompt()


def build_with_metta_prompt(runtime_env: Dict[str, Any]) -> str:
    base_prompt = build_base_prompt()
    lines = [
        "Retrieved MeTTa contract memory for the current env:",
        f"- answer_shape: {str(runtime_env.get('answer_shape') or '').strip()}",
        f"- summary: {str(runtime_env.get('summary') or '').strip()}",
        f"- query_cues: {join_items(runtime_env.get('query_cues') or [])}",
        f"- must_do: {join_items(runtime_env.get('must_do') or [])}",
        f"- avoid: {join_items(runtime_env.get('avoid') or [])}",
        f"- validation_path: {str(runtime_env.get('validation_path') or '').strip()}",
        f"- repair_focus: {join_items(runtime_env.get('repair_focus') or [])}",
        f"- contract_priority: {str(runtime_env.get('contract_priority') or '').strip()}",
        render_profile_catalog(runtime_env),
        "Use this contract memory privately to classify the active structural family from the user's instruction.",
        "Then satisfy that family exactly and emit only the final constrained summary text.",
        "Do not mention the contract memory or profile catalog in the final answer.",
    ]
    return f"{base_prompt}\n\n" + "\n".join(line for line in lines if str(line).strip())


def command_template_for_arm(arm_id: str, seed: int) -> str:
    return (
        '"{python_exec}" '
        f'"{REMOTE_BRIDGE.as_posix()}" '
        "--source {env_source} "
        '--host "snacksack-ms-7d32.tail3156cd.ts.net" '
        '--user "snacksack" '
        '--identity-file "C:/Users/patri/.ssh/id_ed25519" '
        '--ssh-timeout-seconds 300 '
        f"--seed {seed} "
        f'--judge-base-url "{JUDGE_BASE_URL}" '
        f'--judge-model "{JUDGE_MODEL}" '
        '--research-root "/home/snacksack/prime_repos_tmp/research-environments/environments" '
        '--community-root "/home/snacksack/prime_repos_tmp/community-environments/environments" '
        f'--remote-site-packages "/tmp/prime_env_bridge_site_{arm_id}_{seed}_{{env_id}}" '
        f'--remote-cache-root "/tmp/prime_env_bridge_cache_{arm_id}_{seed}_{{env_id}}" '
        "{env_id}"
    )


def bridge_args(
    *,
    seed: int,
    arm_id: str,
    mode: str,
    env_source: str,
    judge_base_url: str,
    judge_model: str,
) -> List[str]:
    mode_flag = "--reset" if mode == "reset" else "--step"
    return [
        sys.executable,
        str(REMOTE_BRIDGE),
        ENV_ID,
        "--source",
        env_source,
        mode_flag,
        "--host",
        "snacksack-ms-7d32.tail3156cd.ts.net",
        "--user",
        "snacksack",
        "--identity-file",
        "C:/Users/patri/.ssh/id_ed25519",
        "--ssh-timeout-seconds",
        "300",
        "--seed",
        str(seed),
        "--judge-base-url",
        judge_base_url,
        "--judge-model",
        judge_model,
        "--research-root",
        "/home/snacksack/prime_repos_tmp/research-environments/environments",
        "--community-root",
        "/home/snacksack/prime_repos_tmp/community-environments/environments",
        "--remote-site-packages",
        f"/tmp/prime_env_bridge_site_{arm_id}_{seed}_{ENV_ID}",
        "--remote-cache-root",
        f"/tmp/prime_env_bridge_cache_{arm_id}_{seed}_{ENV_ID}",
    ]


def run_remote_bridge(
    *,
    seed: int,
    arm_id: str,
    mode: str,
    env_source: str,
    judge_base_url: str,
    judge_model: str,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    result = subprocess.run(
        bridge_args(
            seed=seed,
            arm_id=arm_id,
            mode=mode,
            env_source=env_source,
            judge_base_url=judge_base_url,
            judge_model=judge_model,
        ),
        input=(json.dumps(payload) if payload is not None else ""),
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
        timeout=360,
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


def count_values(rows: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        value = row.get(key)
        counts[str(value).lower()] += 1
    return dict(sorted(counts.items()))


def infer_profile_counts(rows: List[Dict[str, Any]], runtime_env: Dict[str, Any]) -> Dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        observation = str(row.get("observation") or "")
        profile_id = selected_profile_id(runtime_env, observation)
        counts[profile_id or "unknown"] += 1
    return dict(sorted(counts.items()))


def sample_actions(rows: List[Dict[str, Any]], limit: int = 3) -> List[str]:
    excerpts: List[str] = []
    for row in rows[:limit]:
        action = str(row.get("action") or "")
        if action:
            excerpts.append(action_excerpt(action))
    return excerpts


def average_reward(total: Any, episodes: int) -> float | None:
    if not isinstance(total, (int, float)) or episodes <= 0:
        return None
    return float(total) / float(episodes)


def summarize_result(
    arm_id: str,
    export_path: Path,
    task_result: Dict[str, Any],
    runtime_env: Dict[str, Any],
    seed: int,
) -> Dict[str, Any]:
    rows = read_jsonl(export_path)
    summary = task_result.get("summary") if isinstance(task_result.get("summary"), dict) else {}
    reward_total = (summary.get("reward_totals") or {}).get(ENV_ID)
    token_usage = summary.get("token_usage") or {}
    episodes = int(summary.get("episodes") or len(rows) or 0)
    avg = average_reward(reward_total, episodes)
    last_row = rows[-1] if rows else {}
    episode_metrics = parse_episode_summary(last_row).get("metrics") or {}
    return {
        "arm_id": arm_id,
        "env_id": ENV_ID,
        "seed": seed,
        "status": str(task_result.get("status") or ""),
        "returncode": task_result.get("returncode"),
        "episodes": episodes,
        "reward_total": reward_total,
        "avg_reward": avg,
        "token_usage": token_usage,
        "output_statuses": summary.get("output_statuses") or {},
        "visible_output_emitted": summary.get("visible_output_emitted") or {},
        "action_types": count_values(rows, "action_type"),
        "profile_counts": infer_profile_counts(rows, runtime_env),
        "sample_actions": sample_actions(rows),
        "last_action_excerpt": action_excerpt(str(last_row.get("action") or "")),
        "episode_metrics": episode_metrics if isinstance(episode_metrics, dict) else {},
        "export_path": str(export_path),
        "summary_path": str(export_path.with_suffix(".summary.json")),
        "success": bool(task_result.get("status") == "success"),
    }


def sum_token_usage(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    totals: Dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    for row in rows:
        usage = row.get("token_usage") or {}
        for key in list(totals.keys()):
            value = usage.get(key)
            if isinstance(value, (int, float)):
                totals[key] += int(value)
    return totals


def merge_count_maps(rows: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        payload = row.get(key) or {}
        if not isinstance(payload, dict):
            continue
        for item_key, value in payload.items():
            if isinstance(value, (int, float)):
                counts[str(item_key)] += int(value)
    return dict(sorted(counts.items()))


def aggregate_arm_results(arm_id: str, seed_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    reward_total = 0.0
    reward_count = 0
    sample_actions_list: List[str] = []
    env_info_samples: List[Dict[str, Any]] = []
    repair_reports: List[Dict[str, Any]] = []
    for row in seed_rows:
        value = row.get("reward_total")
        if isinstance(value, (int, float)):
            reward_total += float(value)
            reward_count += int(row.get("episodes") or 0)
        for excerpt in row.get("sample_actions") or []:
            if excerpt not in sample_actions_list and len(sample_actions_list) < 4:
                sample_actions_list.append(excerpt)
        env_info = row.get("env_info") or {}
        if isinstance(env_info, dict) and env_info and len(env_info_samples) < 3:
            env_info_samples.append(env_info)
        repair_report = row.get("repair_report") or {}
        if isinstance(repair_report, dict) and repair_report:
            repair_reports.append(repair_report)
        replay_rows = read_jsonl(Path(str(row.get("export_path") or "")))
        if replay_rows and len(env_info_samples) < 3:
            env_info = replay_rows[-1].get("env_info") or {}
            if isinstance(env_info, dict) and env_info and len(env_info_samples) < 3:
                env_info_samples.append(env_info)
    avg = average_reward(reward_total, reward_count)
    aggregate = {
        "arm_id": arm_id,
        "env_id": ENV_ID,
        "seeds": [row.get("seed") for row in seed_rows],
        "status": "success" if all(bool(row.get("success")) for row in seed_rows) else "partial_failure",
        "episodes": reward_count,
        "reward_total": reward_total,
        "avg_reward": avg,
        "token_usage": sum_token_usage(seed_rows),
        "output_statuses": merge_count_maps(seed_rows, "output_statuses"),
        "visible_output_emitted": merge_count_maps(seed_rows, "visible_output_emitted"),
        "action_types": merge_count_maps(seed_rows, "action_types"),
        "profile_counts": merge_count_maps(seed_rows, "profile_counts"),
        "sample_actions": sample_actions_list,
        "per_seed": seed_rows,
        "env_info_samples": env_info_samples,
        "success": all(bool(row.get("success")) for row in seed_rows),
    }
    if repair_reports:
        aggregate["repair_reports"] = repair_reports
    return aggregate


def summarize_repair_result(
    *,
    seed: int,
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
        "env_id": ENV_ID,
        "seed": seed,
        "status": "success" if bool(scored_payload.get("valid_action", True)) else "failure",
        "returncode": 0,
        "episodes": 1,
        "reward_total": reward,
        "avg_reward": reward,
        "token_usage": dict(source_row.get("token_usage") or {}),
        "output_statuses": {"completed": 1},
        "visible_output_emitted": {"true": 1},
        "action_types": {"direct_answer_repaired": 1},
        "profile_counts": dict(source_row.get("profile_counts") or {}),
        "sample_actions": [repaired_text] if repaired_text else [],
        "last_action_excerpt": action_excerpt(repaired_text),
        "episode_metrics": metrics if isinstance(metrics, dict) else {},
        "export_path": str(source_row.get("export_path") or ""),
        "summary_path": str(source_row.get("summary_path") or ""),
        "repair_applied": repaired_text != original_text,
        "repair_report": {
            "status": repair_report.get("status"),
            "applied_repairs": repair_report.get("applied_repairs") or [],
            "detected_failures": repair_report.get("detected_failures") or [],
        },
        "env_info": scored_payload.get("env_info") or {},
        "success": bool(scored_payload.get("valid_action", True)),
    }


def build_repair_seed_result(
    *,
    seed: int,
    source_row: Dict[str, Any],
    runtime_env: Dict[str, Any],
    env_source: str,
    judge_base_url: str,
    judge_model: str,
) -> Dict[str, Any]:
    replay_rows = read_jsonl(Path(str(source_row.get("export_path") or "")))
    trace_row = replay_rows[-1] if replay_rows else {}
    original_action = str(trace_row.get("action") or source_row.get("last_action_excerpt") or "").strip()
    observation = str(trace_row.get("observation") or "").strip()
    repair_report = repair_candidate(ENV_ID, original_action, runtime_env, observation)
    reset_payload = run_remote_bridge(
        seed=seed,
        arm_id="with_metta_runtime_repair",
        mode="reset",
        env_source=env_source,
        judge_base_url=judge_base_url,
        judge_model=judge_model,
    )
    session_state = reset_payload.get("session")
    if not isinstance(session_state, dict):
        raise RuntimeError(f"missing session state for repair scoring on seed {seed}")
    scored_payload = run_remote_bridge(
        seed=seed,
        arm_id="with_metta_runtime_repair",
        mode="step",
        env_source=env_source,
        judge_base_url=judge_base_url,
        judge_model=judge_model,
        payload={
            "state": session_state,
            "action": str(repair_report.get("repaired_text") or ""),
        },
    )
    return summarize_repair_result(
        seed=seed,
        source_row=source_row,
        repair_report=repair_report,
        scored_payload=scored_payload,
    )


def render_results_markdown(results: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    lines.append("# if_summarize_judge With-MeTTa Eval")
    lines.append("")
    lines.append("| Arm | Seeds | Episodes | Total Reward | Avg Reward | Prompt Tokens | Completion Tokens | Profiles Seen |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |")
    for result in results:
        token_usage = result.get("token_usage") or {}
        profiles = ", ".join(f"{key}:{value}" for key, value in (result.get("profile_counts") or {}).items()) or "-"
        seeds = ", ".join(str(seed) for seed in (result.get("seeds") or [])) or "-"
        lines.append(
            "| {arm} | {seeds} | {episodes} | {total} | {avg} | {prompt_tokens} | {completion_tokens} | {profiles} |".format(
                arm=result.get("arm_id"),
                seeds=seeds,
                episodes=result.get("episodes", "-"),
                total=result.get("reward_total") if result.get("reward_total") is not None else "-",
                avg=f"{result.get('avg_reward'):.4f}" if isinstance(result.get("avg_reward"), (int, float)) else "-",
                prompt_tokens=token_usage.get("prompt_tokens", "-"),
                completion_tokens=token_usage.get("completion_tokens", "-"),
                profiles=profiles.replace("|", "\\|"),
            )
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- `without_metta`: base `primehub-constraint-summarize-hermes` prompt only.")
    lines.append("- `with_metta_runtime`: same base prompt plus the compact profile-aware MeTTa runtime packet.")
    lines.append("- `with_metta_runtime_repair`: same runtime arm, then deterministic MeTTa repair before remote verifier scoring.")
    lines.append("")
    return "\n".join(lines) + "\n"


def render_findings(results: List[Dict[str, Any]]) -> str:
    by_arm = {str(result.get("arm_id")): result for result in results}
    control = by_arm.get("without_metta", {})
    treatment = by_arm.get("with_metta_runtime", {})
    repair = by_arm.get("with_metta_runtime_repair", {})
    control_avg = control.get("avg_reward")
    treatment_avg = treatment.get("avg_reward")
    repair_avg = repair.get("avg_reward")
    delta_text = "n/a"
    repair_delta_text = "n/a"
    if isinstance(control_avg, (int, float)) and isinstance(treatment_avg, (int, float)):
        delta = float(treatment_avg) - float(control_avg)
        delta_text = f"{delta:.4f}"
    if isinstance(treatment_avg, (int, float)) and isinstance(repair_avg, (int, float)):
        repair_delta = float(repair_avg) - float(treatment_avg)
        repair_delta_text = f"{repair_delta:.4f}"

    lines: List[str] = []
    lines.append("# if_summarize_judge With-MeTTa Findings")
    lines.append("")
    lines.append("This run keeps the new summarization skill fixed and changes only whether the model gets the compact MeTTa profile catalog.")
    lines.append("")
    lines.append("## Reward Snapshot")
    lines.append("")
    for arm_id in ["without_metta", "with_metta_runtime", "with_metta_runtime_repair"]:
        row = by_arm.get(arm_id, {})
        lines.append(f"- `{arm_id}`")
        lines.append(f"  - seeds: `{row.get('seeds')}`")
        lines.append(f"  - episodes: `{row.get('episodes')}`")
        lines.append(f"  - reward_total: `{row.get('reward_total')}`")
        lines.append(f"  - avg_reward: `{row.get('avg_reward')}`")
        lines.append(f"  - profiles_seen: `{row.get('profile_counts')}`")
        env_info_samples = row.get("env_info_samples") or []
        if env_info_samples:
            lines.append(f"  - env_info_samples: `{env_info_samples}`")
    lines.append("")
    lines.append("## Read")
    lines.append("")
    if delta_text == "n/a":
        lines.append("- One or both arms failed to produce a numeric average reward.")
    else:
        lines.append(f"- `with_metta_runtime` minus `without_metta` avg reward: `{delta_text}`.")
    if repair_delta_text != "n/a":
        lines.append(f"- `with_metta_runtime_repair` minus `with_metta_runtime` avg reward: `{repair_delta_text}`.")
    control_actions = "; ".join(control.get("sample_actions") or []) or "-"
    treatment_actions = "; ".join(treatment.get("sample_actions") or []) or "-"
    repair_actions = "; ".join(repair.get("sample_actions") or []) or "-"
    lines.append(f"- control sample actions: {control_actions}")
    lines.append(f"- treatment sample actions: {treatment_actions}")
    lines.append(f"- repair sample actions: {repair_actions}")
    repair_rows = repair.get("per_seed") or []
    if repair_rows:
        repaired_seed_ids = [str(row.get("seed")) for row in repair_rows if bool(row.get("repair_applied"))]
        if repaired_seed_ids:
            lines.append(f"- repair-applied seeds: {', '.join(repaired_seed_ids)}")
    lines.append("")
    lines.append("## Takeaway")
    lines.append("")
    if isinstance(control_avg, (int, float)) and isinstance(treatment_avg, (int, float)) and isinstance(repair_avg, (int, float)):
        if repair_avg > treatment_avg and treatment_avg == control_avg:
            takeaway = "The compact MeTTa runtime packet matched control on this rerun, and deterministic repair cleared the remaining structural misses."
        elif repair_avg > treatment_avg >= control_avg:
            takeaway = "The compact MeTTa profile catalog improved the seeded slice, and deterministic repair closed the remaining exact-count miss."
        elif treatment_avg > control_avg:
            takeaway = "The compact MeTTa profile catalog improved average judged reward on this multi-episode slice."
        elif treatment_avg < control_avg:
            takeaway = "The base summarization skill remained stronger than the MeTTa treatment on this slice."
        else:
            takeaway = "The MeTTa catalog matched the base summarization skill on this slice."
    else:
        takeaway = "The slice did not yield a clean numeric comparison."
    lines.append(takeaway)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    seeds = [int(seed) for seed in (args.seeds or [])]
    if not seeds:
        seeds = [7, 11, 19]
    artifacts_root = Path(args.output_dir).resolve()
    artifacts_root.mkdir(parents=True, exist_ok=True)
    results_json = artifacts_root / "if_summarize_with_metta.results.json"
    results_md = artifacts_root / "if_summarize_with_metta.results.md"
    findings_md = artifacts_root / "if_summarize_with_metta.findings.md"

    for required_path in [PROMPT_BUILDER, RUNTIME_PACKET_PATH, SLICE_MANIFEST_PATH]:
        if not required_path.exists():
            raise SystemExit(f"missing required path: {required_path}")

    runtime_env = load_runtime_env()
    manifest_profile = load_manifest_profile()
    env_source = str(manifest_profile.get("source") or "research")
    env_owner = str(manifest_profile.get("owner") or "primeintellect")
    env_folder = str(manifest_profile.get("folder") or ENV_ID)

    model = ModelProfile(
        model_id=args.model_id,
        base_url=args.base_url,
        model_name=args.model_name,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        request_timeout=args.request_timeout,
    )

    arms = {
        "without_metta": build_without_metta_prompt(),
        "with_metta_runtime": build_with_metta_prompt(runtime_env),
    }

    results: List[Dict[str, Any]] = []
    for arm_id, prompt in arms.items():
        seed_rows: List[Dict[str, Any]] = []
        for seed in seeds:
            export_path = artifacts_root / "replays" / arm_id / f"{ENV_ID}.seed_{seed}.jsonl"
            config_path = artifacts_root / "configs" / f"{arm_id}.{ENV_ID}.seed_{seed}.json"
            config_obj = build_config(
                model=model,
                env_id=ENV_ID,
                env_name=ENV_ID,
                env_source=env_source,
                env_owner=env_owner,
                env_folder=env_folder,
                export_path=export_path,
                python_exec=sys.executable,
                command_template=command_template_for_arm(arm_id, seed),
                env_mode="primehub",
                variant_id=f"{ENV_ID}-{arm_id}-seed-{seed}",
                reasoning_mode="off",
                skill_name="primehub-constraint-summarize-hermes",
                skill_prompt=prompt,
                skill_cluster="constraint_summarize",
                role_mode="critic_only",
                role_support_tier="",
                role_gate_applied=False,
                role_gate_downgraded=False,
                role_gate_reason="",
            )
            config_obj["max_steps_per_episode"] = 1
            config_obj["max_episodes"] = 1
            success, task_result, _, _ = run_one_task(
                trm_root=TRM_ROOT,
                python_exec=sys.executable,
                config_path=config_path,
                config_obj=config_obj,
                export_path=export_path,
                episodes=1,
                token_budget=None,
                task_key=f"{model.model_id}:{ENV_ID}:{arm_id}:seed:{seed}",
                task_timeout=1800,
            )
            row = summarize_result(arm_id, export_path, task_result, runtime_env, seed)
            row["success"] = success
            seed_rows.append(row)
        results.append(aggregate_arm_results(arm_id, seed_rows))

    runtime_row = next((row for row in results if str(row.get("arm_id")) == "with_metta_runtime"), {})
    runtime_seed_rows = runtime_row.get("per_seed") or []
    if runtime_seed_rows:
        repair_seed_rows: List[Dict[str, Any]] = []
        bundle_env = load_bundle_env(METTA_BUNDLE_ROOT, ENV_ID)
        for seed_row in runtime_seed_rows:
            repair_seed_rows.append(
                build_repair_seed_result(
                    seed=int(seed_row.get("seed") or 0),
                    source_row=seed_row,
                    runtime_env=bundle_env,
                    env_source=env_source,
                    judge_base_url=args.base_url,
                    judge_model=args.model_name,
                )
            )
        results.append(aggregate_arm_results("with_metta_runtime_repair", repair_seed_rows))

    payload = {
        "model": {
            "model_id": model.model_id,
            "base_url": model.base_url,
            "model_name": model.model_name,
        },
        "env_id": ENV_ID,
        "seeds": seeds,
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
