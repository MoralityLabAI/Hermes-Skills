from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List

from metta_repair_pass import generate_corrupted_candidate, repair_candidate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile deterministic TRM supervision rows from a MeTTa bundle.")
    parser.add_argument("--bundle-dir", required=True, help="Bundle directory containing retrieval_packet.json and runtime_packet.json.")
    parser.add_argument("--out-dir", required=True, help="Output directory for synthesized TRM rows.")
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not decode to an object")
    return payload


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def join_items(values: List[str] | None) -> str:
    return "; ".join(str(value).strip() for value in (values or []) if str(value).strip())


def supervision_weight(bucket: str) -> float:
    if bucket == "exact_positive":
        return 2.5
    if bucket == "weak_positive":
        return 1.25
    return 0.2


def load_bundle(bundle_dir: Path) -> Dict[str, Any]:
    bundle_manifest = read_json(bundle_dir / "bundle.manifest.json")
    runtime_packet = read_json(bundle_dir / "runtime_packet.json")
    retrieval_packet = read_json(bundle_dir / "retrieval_packet.json")
    trace_labels = read_json(bundle_dir / "trace_labels.json")
    return {
        "manifest": bundle_manifest,
        "runtime_envs": runtime_packet.get("envs") or {},
        "retrieval_envs": retrieval_packet.get("envs") or {},
        "trace_envs": trace_labels.get("envs") or {},
    }


def make_select_observation(env_id: str, runtime_env: Dict[str, Any], all_envs: List[str]) -> str:
    parts = [
        f"QUERY_HINTS:\n{join_items(runtime_env.get('query_cues') or [])}",
        f"AVAILABLE_CONTRACTS:\n{', '.join(all_envs)}",
        f"EXPECTED_SHAPE:\n{runtime_env.get('answer_shape', '')}",
        f"CONTRACT_SUMMARY:\n{runtime_env.get('summary', '')}",
    ]
    return "\n\n".join(parts)


def make_verify_observation(env_id: str, runtime_env: Dict[str, Any], candidate_output: str) -> str:
    parts = [
        f"ENV_ID:\n{env_id}",
        f"CONTRACT_SUMMARY:\n{runtime_env.get('summary', '')}",
        f"MUST_DO:\n{join_items(runtime_env.get('must_do') or [])}",
        f"AVOID:\n{join_items(runtime_env.get('avoid') or [])}",
        f"CANDIDATE_OUTPUT:\n{candidate_output}",
    ]
    validation_path = str(runtime_env.get("validation_path") or "").strip()
    if validation_path:
        parts.append(f"VALIDATION_PATH:\n{validation_path}")
    return "\n\n".join(parts)


def make_repair_observation(env_id: str, runtime_env: Dict[str, Any], candidate_output: str) -> str:
    parts = [
        f"ENV_ID:\n{env_id}",
        f"ANSWER_SHAPE:\n{runtime_env.get('answer_shape', '')}",
        f"REPAIR_FOCUS:\n{join_items(runtime_env.get('repair_focus') or [])}",
        f"AVOID:\n{join_items(runtime_env.get('avoid') or [])}",
        f"BROKEN_OUTPUT:\n{candidate_output}",
    ]
    return "\n\n".join(parts)


def merge_profile_env(runtime_env: Dict[str, Any], profile_id: str, profile_payload: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(runtime_env)
    merged["summary"] = str(profile_payload.get("summary") or runtime_env.get("summary") or "").strip()
    merged["query_cues"] = list(profile_payload.get("query_cues") or runtime_env.get("query_cues") or [])
    merged["must_do"] = list(profile_payload.get("must_do") or runtime_env.get("must_do") or [])
    merged["avoid"] = list(profile_payload.get("avoid") or runtime_env.get("avoid") or [])
    merged["minimal_example"] = str(profile_payload.get("minimal_example") or runtime_env.get("minimal_example") or "").strip()
    merged["repair_focus"] = list(profile_payload.get("repair_focus") or runtime_env.get("repair_focus") or [])
    merged["selected_profile_id"] = profile_id
    return merged


def make_profile_select_observation(env_id: str, profile_id: str, runtime_env: Dict[str, Any], all_profiles: List[str]) -> str:
    parts = [
        f"ENV_ID:\n{env_id}",
        f"PROFILE_HINTS:\n{join_items(runtime_env.get('query_cues') or [])}",
        f"AVAILABLE_PROFILES:\n{', '.join(all_profiles)}",
        f"PROFILE_SUMMARY:\n{runtime_env.get('summary', '')}",
        f"EXPECTED_SHAPE:\n{runtime_env.get('answer_shape', '')}",
    ]
    return "\n\n".join(parts)


def make_profile_verify_observation(env_id: str, profile_id: str, runtime_env: Dict[str, Any], candidate_output: str) -> str:
    parts = [
        f"ENV_ID:\n{env_id}",
        f"PROFILE_ID:\n{profile_id}",
        f"PROFILE_SUMMARY:\n{runtime_env.get('summary', '')}",
        f"MUST_DO:\n{join_items(runtime_env.get('must_do') or [])}",
        f"AVOID:\n{join_items(runtime_env.get('avoid') or [])}",
        f"CANDIDATE_OUTPUT:\n{candidate_output}",
    ]
    return "\n\n".join(parts)


def make_profile_repair_observation(env_id: str, profile_id: str, runtime_env: Dict[str, Any], candidate_output: str) -> str:
    parts = [
        f"ENV_ID:\n{env_id}",
        f"PROFILE_ID:\n{profile_id}",
        f"PROFILE_SUMMARY:\n{runtime_env.get('summary', '')}",
        f"REPAIR_FOCUS:\n{join_items(runtime_env.get('repair_focus') or [])}",
        f"AVOID:\n{join_items(runtime_env.get('avoid') or [])}",
        f"BROKEN_OUTPUT:\n{candidate_output}",
    ]
    return "\n\n".join(parts)


def base_row(package_id: str, env_id: str, task_family: str, row_id: str, observation: str) -> Dict[str, Any]:
    return {
        "source_env_name": package_id,
        "source_env_type": "MeTTaBundle",
        "task_family": task_family,
        "task": env_id,
        "row_id": row_id,
        "observation": observation,
        "valid_action": True,
        "visible_output_emitted": True,
        "reasoning_mode": "off",
        "reasoning_trace": [],
    }


def build_rows(bundle_dir: Path) -> List[Dict[str, Any]]:
    bundle = load_bundle(bundle_dir)
    package_id = str(bundle["manifest"].get("package_id") or "metta_bundle").strip()
    runtime_envs: Dict[str, Dict[str, Any]] = bundle["runtime_envs"]
    all_envs = sorted(runtime_envs.keys())
    rows: List[Dict[str, Any]] = []
    for env_id in all_envs:
        runtime_env = runtime_envs[env_id]
        minimal_example = str(runtime_env.get("minimal_example") or "").strip()
        corrupted_candidate = generate_corrupted_candidate(env_id, runtime_env)
        repair_report = repair_candidate(env_id, corrupted_candidate, runtime_env)

        select_row = base_row(
            package_id,
            env_id,
            "metta_contract_select",
            f"{package_id}:{env_id}:select",
            make_select_observation(env_id, runtime_env, all_envs),
        )
        select_row.update(
            {
                "model_action": env_id,
                "target_action": env_id,
                "bucket": "exact_positive",
                "supervision_weight": supervision_weight("exact_positive"),
                "reward": 1.0,
                "score": 1.0,
                "reasoning_summary": "Contract selection row synthesized from the MeTTa runtime packet.",
                "meta": {
                    "env_id": env_id,
                    "row_kind": "select",
                    "answer_shape": runtime_env.get("answer_shape"),
                },
            }
        )
        rows.append(select_row)

        verify_positive = base_row(
            package_id,
            env_id,
            "metta_contract_verify",
            f"{package_id}:{env_id}:verify_positive",
            make_verify_observation(env_id, runtime_env, minimal_example),
        )
        verify_positive.update(
            {
                "model_action": "accept",
                "target_action": "accept",
                "bucket": "exact_positive",
                "supervision_weight": supervision_weight("exact_positive"),
                "reward": 1.0,
                "score": 1.0,
                "reasoning_summary": "Positive verifier row using the MeTTa minimal valid example.",
                "meta": {
                    "env_id": env_id,
                    "row_kind": "verify_positive",
                    "candidate_source": "minimal_example",
                },
            }
        )
        rows.append(verify_positive)

        verify_negative = base_row(
            package_id,
            env_id,
            "metta_contract_verify",
            f"{package_id}:{env_id}:verify_negative",
            make_verify_observation(env_id, runtime_env, corrupted_candidate),
        )
        verify_negative.update(
            {
                "model_action": "accept",
                "target_action": "reject",
                "bucket": "negative",
                "supervision_weight": supervision_weight("negative"),
                "reward": 0.0,
                "score": 0.0,
                "reasoning_summary": "Negative verifier row synthesized from a deterministic corrupted candidate.",
                "meta": {
                    "env_id": env_id,
                    "row_kind": "verify_negative",
                    "candidate_source": "deterministic_corruption",
                    "detected_failures": repair_report.get("detected_failures") or [],
                },
            }
        )
        rows.append(verify_negative)

        repaired_text = str(repair_report.get("repaired_text") or "").strip()
        repair_row = base_row(
            package_id,
            env_id,
            "metta_contract_repair",
            f"{package_id}:{env_id}:repair",
            make_repair_observation(env_id, runtime_env, corrupted_candidate),
        )
        repair_row.update(
            {
                "model_action": repaired_text,
                "target_action": repaired_text,
                "bucket": "exact_positive",
                "supervision_weight": supervision_weight("exact_positive"),
                "reward": 1.0 if repaired_text else 0.0,
                "score": 1.0 if repaired_text else 0.0,
                "reasoning_summary": "Repair row synthesized from the deterministic MeTTa repair pass.",
                "meta": {
                    "env_id": env_id,
                    "row_kind": "repair",
                    "candidate_source": "deterministic_corruption",
                    "applied_repairs": repair_report.get("applied_repairs") or [],
                    "detected_failures": repair_report.get("detected_failures") or [],
                },
            }
        )
        rows.append(repair_row)

        profile_payloads = runtime_env.get("profiles") or {}
        if isinstance(profile_payloads, dict) and profile_payloads:
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

                profile_select_row = base_row(
                    package_id,
                    env_id,
                    "metta_profile_select",
                    f"{package_id}:{env_id}:{profile_id}:profile_select",
                    make_profile_select_observation(env_id, profile_id, merged_env, all_profiles),
                )
                profile_select_row.update(
                    {
                        "model_action": profile_id,
                        "target_action": profile_id,
                        "bucket": "exact_positive",
                        "supervision_weight": supervision_weight("exact_positive"),
                        "reward": 1.0,
                        "score": 1.0,
                        "reasoning_summary": "Profile-selection row synthesized from the MeTTa runtime packet.",
                        "meta": {
                            "env_id": env_id,
                            "profile_id": profile_id,
                            "row_kind": "profile_select",
                        },
                    }
                )
                rows.append(profile_select_row)

                profile_verify_positive = base_row(
                    package_id,
                    env_id,
                    "metta_profile_verify",
                    f"{package_id}:{env_id}:{profile_id}:profile_verify_positive",
                    make_profile_verify_observation(env_id, profile_id, merged_env, profile_example),
                )
                profile_verify_positive.update(
                    {
                        "model_action": "accept",
                        "target_action": "accept",
                        "bucket": "exact_positive",
                        "supervision_weight": supervision_weight("exact_positive"),
                        "reward": 1.0,
                        "score": 1.0,
                        "reasoning_summary": "Positive verifier row using the MeTTa profile minimal example.",
                        "meta": {
                            "env_id": env_id,
                            "profile_id": profile_id,
                            "row_kind": "profile_verify_positive",
                            "candidate_source": "profile_minimal_example",
                        },
                    }
                )
                rows.append(profile_verify_positive)

                profile_verify_negative = base_row(
                    package_id,
                    env_id,
                    "metta_profile_verify",
                    f"{package_id}:{env_id}:{profile_id}:profile_verify_negative",
                    make_profile_verify_observation(env_id, profile_id, merged_env, profile_corrupted),
                )
                profile_verify_negative.update(
                    {
                        "model_action": "accept",
                        "target_action": "reject",
                        "bucket": "negative",
                        "supervision_weight": supervision_weight("negative"),
                        "reward": 0.0,
                        "score": 0.0,
                        "reasoning_summary": "Negative verifier row synthesized from a deterministic profile corruption.",
                        "meta": {
                            "env_id": env_id,
                            "profile_id": profile_id,
                            "row_kind": "profile_verify_negative",
                            "candidate_source": "deterministic_profile_corruption",
                            "detected_failures": profile_repair_report.get("detected_failures") or [],
                        },
                    }
                )
                rows.append(profile_verify_negative)

                profile_repaired_text = str(profile_repair_report.get("repaired_text") or "").strip()
                profile_repair_row = base_row(
                    package_id,
                    env_id,
                    "metta_profile_repair",
                    f"{package_id}:{env_id}:{profile_id}:profile_repair",
                    make_profile_repair_observation(env_id, profile_id, merged_env, profile_corrupted),
                )
                profile_repair_row.update(
                    {
                        "model_action": profile_repaired_text,
                        "target_action": profile_repaired_text,
                        "bucket": "exact_positive",
                        "supervision_weight": supervision_weight("exact_positive"),
                        "reward": 1.0 if profile_repaired_text else 0.0,
                        "score": 1.0 if profile_repaired_text else 0.0,
                        "reasoning_summary": "Repair row synthesized from the deterministic MeTTa profile repair pass.",
                        "meta": {
                            "env_id": env_id,
                            "profile_id": profile_id,
                            "row_kind": "profile_repair",
                            "candidate_source": "deterministic_profile_corruption",
                            "applied_repairs": profile_repair_report.get("applied_repairs") or [],
                            "detected_failures": profile_repair_report.get("detected_failures") or [],
                        },
                    }
                )
                rows.append(profile_repair_row)
    return rows


def build_summary(bundle_dir: Path, out_dir: Path, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    family_counts: Counter[str] = Counter()
    bucket_counts: Counter[str] = Counter()
    env_counts: Counter[str] = Counter()
    for row in rows:
        family_counts[str(row.get("task_family") or "")] += 1
        bucket_counts[str(row.get("bucket") or "")] += 1
        env_counts[str(row.get("task") or "")] += 1
    return {
        "bundle_dir": str(bundle_dir),
        "out_dir": str(out_dir),
        "row_count": len(rows),
        "task_family_counts": dict(family_counts),
        "bucket_counts": dict(bucket_counts),
        "env_counts": dict(env_counts),
    }


def main() -> int:
    args = parse_args()
    bundle_dir = Path(args.bundle_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    rows = build_rows(bundle_dir)
    rows_path = out_dir / "metta_trm_rows.jsonl"
    summary_path = out_dir / "metta_trm_rows.summary.json"
    write_jsonl(rows_path, rows)
    write_json(summary_path, build_summary(bundle_dir, out_dir, rows))
    print(str(rows_path))
    print(str(summary_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
