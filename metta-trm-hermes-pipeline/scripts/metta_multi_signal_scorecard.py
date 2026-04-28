from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List

from compile_metta_rows import (
    load_bundle,
    make_profile_repair_observation,
    make_profile_select_observation,
    make_profile_verify_observation,
    make_repair_observation,
    make_select_observation,
    make_verify_observation,
    merge_profile_env,
)
from metta_repair_pass import generate_corrupted_candidate, repair_candidate


SIGNAL_SPECS: Dict[str, Dict[str, Any]] = {
    "task_success": {"channel": "success", "weight": 2.0},
    "contract_validity": {"channel": "success", "weight": 1.75},
    "repair_success": {"channel": "repair", "weight": 1.75},
    "retrieval_selection_correctness": {"channel": "selection", "weight": 1.5},
    "profile_selection_correctness": {"channel": "selection", "weight": 1.5},
    "critic_verdict_agreement": {"channel": "critic", "weight": 1.25},
    "failure_localization": {"channel": "repair", "weight": 1.0},
    "contract_family_match": {"channel": "selection", "weight": 1.0},
    "transport_visible_output": {"channel": "transport", "weight": 0.5},
    "transport_no_fallback": {"channel": "transport", "weight": 0.5},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile a multi-signal TRM scorecard from a MeTTa bundle.")
    parser.add_argument("--bundle-dir", required=True, help="Bundle directory containing runtime_packet.json and retrieval_packet.json.")
    parser.add_argument("--out-dir", required=True, help="Output directory for the multi-signal scorecard bundle.")
    return parser.parse_args()


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def prompt_pressure_band(observation: str) -> str:
    size = len(observation)
    if size <= 325:
        return "low"
    if size <= 700:
        return "medium"
    return "high"


def make_signal(name: str, target: int, note: str) -> Dict[str, Any]:
    spec = SIGNAL_SPECS[name]
    return {
        "name": name,
        "target": int(target),
        "channel": str(spec["channel"]),
        "weight": float(spec["weight"]),
        "note": note,
    }


def base_unit(
    package_id: str,
    env_id: str,
    unit_id: str,
    unit_kind: str,
    support_role: str,
    observation: str,
    candidate_text: str,
    target_text: str,
    profile_id: str = "",
) -> Dict[str, Any]:
    return {
        "source_env_name": package_id,
        "source_env_type": "MeTTaBundle",
        "env_id": env_id,
        "profile_id": profile_id,
        "unit_id": unit_id,
        "unit_kind": unit_kind,
        "support_role": support_role,
        "observation": observation,
        "candidate_text": candidate_text,
        "target_text": target_text,
        "observation_chars": len(observation),
        "observation_lines": len(observation.splitlines()),
        "prompt_pressure_band": prompt_pressure_band(observation),
        "signals": [],
        "meta": {},
    }


def add_transport_signals(unit: Dict[str, Any]) -> None:
    unit["signals"].append(make_signal("transport_visible_output", 1, "Synthesized rows assume visible output is emitted."))
    unit["signals"].append(make_signal("transport_no_fallback", 1, "Synthesized rows assume no model-client fallback is required."))


def add_signal(unit: Dict[str, Any], name: str, target: int, note: str) -> None:
    unit["signals"].append(make_signal(name, target, note))


def build_scorecard_units(bundle_dir: Path) -> List[Dict[str, Any]]:
    bundle = load_bundle(bundle_dir)
    package_id = str(bundle["manifest"].get("package_id") or "metta_bundle").strip()
    runtime_envs: Dict[str, Dict[str, Any]] = bundle["runtime_envs"]
    all_envs = sorted(runtime_envs.keys())
    units: List[Dict[str, Any]] = []

    for env_id in all_envs:
        runtime_env = runtime_envs[env_id]
        minimal_example = str(runtime_env.get("minimal_example") or "").strip()
        corrupted_candidate = generate_corrupted_candidate(env_id, runtime_env)
        repair_report = repair_candidate(env_id, corrupted_candidate, runtime_env)
        repaired_text = str(repair_report.get("repaired_text") or "").strip()
        detected_failures = list(repair_report.get("detected_failures") or [])
        applied_repairs = list(repair_report.get("applied_repairs") or [])

        select_unit = base_unit(
            package_id,
            env_id,
            f"{package_id}:{env_id}:select_scorecard",
            "contract_select",
            "selection_support",
            make_select_observation(env_id, runtime_env, all_envs),
            env_id,
            env_id,
        )
        add_signal(select_unit, "retrieval_selection_correctness", 1, "Correct contract selected from the available env set.")
        add_signal(select_unit, "contract_family_match", 1, "Selected contract matches the env-specific symbolic family.")
        add_transport_signals(select_unit)
        select_unit["meta"] = {
            "answer_shape": runtime_env.get("answer_shape"),
            "summary": runtime_env.get("summary"),
        }
        units.append(select_unit)

        verify_positive = base_unit(
            package_id,
            env_id,
            f"{package_id}:{env_id}:verify_positive_scorecard",
            "contract_verify_positive",
            "critic_verify",
            make_verify_observation(env_id, runtime_env, minimal_example),
            minimal_example,
            "accept",
        )
        add_signal(verify_positive, "task_success", 1, "The minimal example satisfies the contract.")
        add_signal(verify_positive, "contract_validity", 1, "Positive verifier example should be accepted.")
        add_signal(verify_positive, "critic_verdict_agreement", 1, "Verifier should agree with the contract-valid example.")
        add_transport_signals(verify_positive)
        verify_positive["meta"] = {
            "candidate_source": "minimal_example",
        }
        units.append(verify_positive)

        verify_negative = base_unit(
            package_id,
            env_id,
            f"{package_id}:{env_id}:verify_negative_scorecard",
            "contract_verify_negative",
            "critic_verify",
            make_verify_observation(env_id, runtime_env, corrupted_candidate),
            corrupted_candidate,
            "reject",
        )
        add_signal(verify_negative, "task_success", 0, "Deterministic corruption should fail the task contract.")
        add_signal(verify_negative, "contract_validity", 0, "Corrupted candidate should be rejected.")
        add_signal(verify_negative, "critic_verdict_agreement", 1, "Verifier should reject the corrupted candidate.")
        add_signal(
            verify_negative,
            "failure_localization",
            1 if detected_failures else 0,
            "Repair pass should expose concrete failure tags for the corrupted candidate.",
        )
        add_transport_signals(verify_negative)
        verify_negative["meta"] = {
            "candidate_source": "deterministic_corruption",
            "detected_failures": detected_failures,
        }
        units.append(verify_negative)

        repair_unit = base_unit(
            package_id,
            env_id,
            f"{package_id}:{env_id}:repair_scorecard",
            "contract_repair",
            "repair_support",
            make_repair_observation(env_id, runtime_env, corrupted_candidate),
            corrupted_candidate,
            repaired_text,
        )
        add_signal(repair_unit, "repair_success", 1 if repaired_text else 0, "Repair pass should produce a contract-valid corrected output.")
        add_signal(repair_unit, "contract_validity", 1 if repaired_text else 0, "Repaired output should satisfy the contract.")
        add_signal(repair_unit, "task_success", 1 if repaired_text else 0, "Repaired output should recover end-to-end task success.")
        add_signal(
            repair_unit,
            "failure_localization",
            1 if detected_failures else 0,
            "Repair lane should expose why the original candidate was invalid.",
        )
        add_transport_signals(repair_unit)
        repair_unit["meta"] = {
            "candidate_source": "deterministic_corruption",
            "detected_failures": detected_failures,
            "applied_repairs": applied_repairs,
        }
        units.append(repair_unit)

        profile_payloads = runtime_env.get("profiles") or {}
        if not isinstance(profile_payloads, dict) or not profile_payloads:
            continue

        all_profiles = sorted(str(profile_id) for profile_id in profile_payloads.keys())
        for profile_id in all_profiles:
            profile_payload = profile_payloads.get(profile_id)
            if not isinstance(profile_payload, dict):
                continue
            merged_env = merge_profile_env(runtime_env, profile_id, profile_payload)
            profile_example = str(merged_env.get("minimal_example") or "").strip()
            if not profile_example:
                continue
            profile_corrupted = generate_corrupted_candidate(env_id, merged_env)
            profile_repair_report = repair_candidate(env_id, profile_corrupted, merged_env)
            profile_repaired_text = str(profile_repair_report.get("repaired_text") or "").strip()
            profile_failures = list(profile_repair_report.get("detected_failures") or [])
            profile_repairs = list(profile_repair_report.get("applied_repairs") or [])

            profile_select = base_unit(
                package_id,
                env_id,
                f"{package_id}:{env_id}:{profile_id}:profile_select_scorecard",
                "profile_select",
                "selection_support",
                make_profile_select_observation(env_id, profile_id, merged_env, all_profiles),
                profile_id,
                profile_id,
                profile_id=profile_id,
            )
            add_signal(profile_select, "retrieval_selection_correctness", 1, "Correct profile selected within the env-specific contract family.")
            add_signal(profile_select, "profile_selection_correctness", 1, "Selected profile matches the structural family requested by the observation.")
            add_signal(profile_select, "contract_family_match", 1, "Selected profile stays inside the env-specific symbolic family.")
            add_transport_signals(profile_select)
            profile_select["meta"] = {
                "summary": merged_env.get("summary"),
            }
            units.append(profile_select)

            profile_verify_positive = base_unit(
                package_id,
                env_id,
                f"{package_id}:{env_id}:{profile_id}:profile_verify_positive_scorecard",
                "profile_verify_positive",
                "critic_verify",
                make_profile_verify_observation(env_id, profile_id, merged_env, profile_example),
                profile_example,
                "accept",
                profile_id=profile_id,
            )
            add_signal(profile_verify_positive, "task_success", 1, "Profile minimal example satisfies the requested structural family.")
            add_signal(profile_verify_positive, "contract_validity", 1, "Positive profile example should be accepted.")
            add_signal(profile_verify_positive, "critic_verdict_agreement", 1, "Verifier should accept the valid profile example.")
            add_signal(profile_verify_positive, "contract_family_match", 1, "Example stays inside the selected profile family.")
            add_transport_signals(profile_verify_positive)
            profile_verify_positive["meta"] = {
                "candidate_source": "profile_minimal_example",
            }
            units.append(profile_verify_positive)

            profile_verify_negative = base_unit(
                package_id,
                env_id,
                f"{package_id}:{env_id}:{profile_id}:profile_verify_negative_scorecard",
                "profile_verify_negative",
                "critic_verify",
                make_profile_verify_observation(env_id, profile_id, merged_env, profile_corrupted),
                profile_corrupted,
                "reject",
                profile_id=profile_id,
            )
            add_signal(profile_verify_negative, "task_success", 0, "Profile corruption should fail the requested structural family.")
            add_signal(profile_verify_negative, "contract_validity", 0, "Corrupted profile candidate should be rejected.")
            add_signal(profile_verify_negative, "critic_verdict_agreement", 1, "Verifier should reject the corrupted profile candidate.")
            add_signal(
                profile_verify_negative,
                "failure_localization",
                1 if profile_failures else 0,
                "Repair pass should emit concrete failure tags for the broken profile candidate.",
            )
            add_signal(profile_verify_negative, "contract_family_match", 1, "Observation still targets the same profile family even when the candidate is broken.")
            add_transport_signals(profile_verify_negative)
            profile_verify_negative["meta"] = {
                "candidate_source": "deterministic_profile_corruption",
                "detected_failures": profile_failures,
            }
            units.append(profile_verify_negative)

            profile_repair = base_unit(
                package_id,
                env_id,
                f"{package_id}:{env_id}:{profile_id}:profile_repair_scorecard",
                "profile_repair",
                "repair_support",
                make_profile_repair_observation(env_id, profile_id, merged_env, profile_corrupted),
                profile_corrupted,
                profile_repaired_text,
                profile_id=profile_id,
            )
            add_signal(profile_repair, "repair_success", 1 if profile_repaired_text else 0, "Repair pass should restore a valid profile-constrained answer.")
            add_signal(profile_repair, "contract_validity", 1 if profile_repaired_text else 0, "Repaired profile output should satisfy the contract.")
            add_signal(profile_repair, "task_success", 1 if profile_repaired_text else 0, "Repaired profile output should recover task success.")
            add_signal(
                profile_repair,
                "failure_localization",
                1 if profile_failures else 0,
                "Repair lane should expose what broke inside the profile-specific contract.",
            )
            add_signal(profile_repair, "contract_family_match", 1, "Repair should stay inside the selected profile family.")
            add_transport_signals(profile_repair)
            profile_repair["meta"] = {
                "candidate_source": "deterministic_profile_corruption",
                "detected_failures": profile_failures,
                "applied_repairs": profile_repairs,
            }
            units.append(profile_repair)
    return units


def build_summary(bundle_dir: Path, out_dir: Path, units: List[Dict[str, Any]]) -> Dict[str, Any]:
    signal_counts: Counter[str] = Counter()
    signal_positive_counts: Counter[str] = Counter()
    signal_negative_counts: Counter[str] = Counter()
    channel_counts: Counter[str] = Counter()
    env_counts: Counter[str] = Counter()
    profile_counts: Counter[str] = Counter()
    unit_kind_counts: Counter[str] = Counter()
    support_role_counts: Counter[str] = Counter()
    prompt_pressure_counts: Counter[str] = Counter()
    total_observation_chars = 0
    total_signal_targets = 0

    for unit in units:
        env_counts[str(unit.get("env_id") or "")] += 1
        profile_id = str(unit.get("profile_id") or "").strip()
        if profile_id:
            profile_counts[profile_id] += 1
        unit_kind_counts[str(unit.get("unit_kind") or "")] += 1
        support_role_counts[str(unit.get("support_role") or "")] += 1
        prompt_pressure_counts[str(unit.get("prompt_pressure_band") or "")] += 1
        total_observation_chars += int(unit.get("observation_chars") or 0)
        for signal in unit.get("signals") or []:
            signal_name = str(signal.get("name") or "")
            channel_name = str(signal.get("channel") or "")
            target = int(signal.get("target") or 0)
            signal_counts[signal_name] += 1
            channel_counts[channel_name] += 1
            total_signal_targets += 1
            if target > 0:
                signal_positive_counts[signal_name] += 1
            else:
                signal_negative_counts[signal_name] += 1

    unit_count = len(units)
    avg_signals_per_unit = float(total_signal_targets) / float(unit_count) if unit_count else 0.0
    avg_observation_chars = float(total_observation_chars) / float(unit_count) if unit_count else 0.0

    return {
        "bundle_dir": str(bundle_dir),
        "out_dir": str(out_dir),
        "unit_count": unit_count,
        "signal_target_count": total_signal_targets,
        "avg_signals_per_unit": avg_signals_per_unit,
        "label_density_vs_single_reward": avg_signals_per_unit,
        "avg_observation_chars": avg_observation_chars,
        "unique_signal_count": len(signal_counts),
        "signal_counts": dict(signal_counts),
        "signal_positive_counts": dict(signal_positive_counts),
        "signal_negative_counts": dict(signal_negative_counts),
        "channel_counts": dict(channel_counts),
        "env_counts": dict(env_counts),
        "profile_counts": dict(profile_counts),
        "unit_kind_counts": dict(unit_kind_counts),
        "support_role_counts": dict(support_role_counts),
        "prompt_pressure_counts": dict(prompt_pressure_counts),
    }


def render_markdown(summary: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# MeTTa Multi-Signal Scorecard Summary")
    lines.append("")
    lines.append(f"- bundle: `{summary['bundle_dir']}`")
    lines.append(f"- units: `{summary['unit_count']}`")
    lines.append(f"- signal targets: `{summary['signal_target_count']}`")
    lines.append(f"- avg signals per unit: `{summary['avg_signals_per_unit']:.2f}`")
    lines.append(f"- label density vs single reward baseline: `{summary['label_density_vs_single_reward']:.2f}x`")
    lines.append(f"- unique signal names: `{summary['unique_signal_count']}`")
    lines.append(f"- avg observation chars: `{summary['avg_observation_chars']:.1f}`")
    lines.append("")
    lines.append("## Signal Counts")
    lines.append("")
    lines.append("| Signal | Total | Positive | Negative |")
    lines.append("| --- | ---: | ---: | ---: |")
    signal_names = sorted((summary.get("signal_counts") or {}).keys())
    for signal_name in signal_names:
        total = int((summary.get("signal_counts") or {}).get(signal_name, 0))
        positive = int((summary.get("signal_positive_counts") or {}).get(signal_name, 0))
        negative = int((summary.get("signal_negative_counts") or {}).get(signal_name, 0))
        lines.append(f"| {signal_name} | {total} | {positive} | {negative} |")
    lines.append("")
    lines.append("## Channel Counts")
    lines.append("")
    lines.append("| Channel | Count |")
    lines.append("| --- | ---: |")
    for channel_name in sorted((summary.get("channel_counts") or {}).keys()):
        count = int((summary.get("channel_counts") or {}).get(channel_name, 0))
        lines.append(f"| {channel_name} | {count} |")
    lines.append("")
    lines.append("## Support Roles")
    lines.append("")
    lines.append("| Role | Units |")
    lines.append("| --- | ---: |")
    for role_name in sorted((summary.get("support_role_counts") or {}).keys()):
        count = int((summary.get("support_role_counts") or {}).get(role_name, 0))
        lines.append(f"| {role_name} | {count} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    bundle_dir = Path(args.bundle_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    units = build_scorecard_units(bundle_dir)
    summary = build_summary(bundle_dir, out_dir, units)

    scorecard_path = out_dir / "metta_multi_signal_scorecard.jsonl"
    summary_path = out_dir / "metta_multi_signal_scorecard.summary.json"
    markdown_path = out_dir / "metta_multi_signal_scorecard.md"

    write_jsonl(scorecard_path, units)
    write_json(summary_path, summary)
    markdown_path.write_text(render_markdown(summary), encoding="utf-8", newline="\n")

    print(str(scorecard_path))
    print(str(summary_path))
    print(str(markdown_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
