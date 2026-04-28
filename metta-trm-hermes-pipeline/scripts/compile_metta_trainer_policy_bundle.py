from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PIPELINE_ROOT.parents[0]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from primehub_role_imprint import DEFAULT_MANIFEST, build_trainer_policy, load_cluster_profiles  # noqa: E402


PRIMARY_POSITIVE_BUCKET = {
    "retrieval_selection_correctness": "exact_positive",
    "profile_selection_correctness": "exact_positive",
    "task_success": "exact_positive",
    "contract_validity": "exact_positive",
    "repair_success": "exact_positive",
    "critic_verdict_agreement": "weak_positive",
    "failure_localization": "near_miss",
    "contract_family_match": "weak_positive",
    "transport_visible_output": "weak_positive",
    "transport_no_fallback": "weak_positive",
}

BUCKET_REWARD = {
    "exact_positive": 1.0,
    "near_miss": 0.7,
    "weak_positive": 0.45,
    "negative": 0.0,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile a MeTTa multi-signal scorecard into a trainer-policy TRM bundle.")
    parser.add_argument("--bundle-dir", required=True, help="Bundle directory containing bundle.manifest.json and runtime_packet.json.")
    parser.add_argument("--scorecard-dir", required=True, help="Directory containing metta_multi_signal_scorecard.jsonl and summary.")
    parser.add_argument("--out-dir", required=True, help="Output directory for the trainer-policy bundle.")
    parser.add_argument("--cluster-id", default="", help="Optional explicit cluster id. If omitted, infer from env ids and package id.")
    parser.add_argument("--manifest-path", default=str(DEFAULT_MANIFEST), help="Skill batch manifest path for cluster profiles.")
    return parser.parse_args()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def infer_cluster_id(explicit_cluster: str, bundle_dir: Path, manifest_path: Path) -> str:
    if explicit_cluster.strip():
        return explicit_cluster.strip()

    bundle_manifest = load_json(bundle_dir / "bundle.manifest.json")
    runtime_packet = load_json(bundle_dir / "runtime_packet.json")
    package_id = str(bundle_manifest.get("package_id") or "").strip().lower()
    env_ids = {str(item).strip() for item in (runtime_packet.get("envs") or {}).keys() if str(item).strip()}

    manifest = load_json(manifest_path)
    env_clusters = manifest.get("env_clusters") or {}
    best_cluster = ""
    best_overlap = -1
    for cluster_id, cluster_envs in env_clusters.items():
        if not isinstance(cluster_envs, list):
            continue
        overlap = len(env_ids & {str(item).strip() for item in cluster_envs if str(item).strip()})
        if overlap > best_overlap:
            best_overlap = overlap
            best_cluster = str(cluster_id)
    if best_cluster and best_overlap > 0:
        return best_cluster
    if "summarize" in package_id:
        return "constraint_summarize"
    if "structured_map" in package_id:
        return "structured_map"
    raise RuntimeError("Could not infer cluster id for the MeTTa bundle. Pass --cluster-id explicitly.")


def make_target_action(signal_name: str, signal_target: int, unit: Dict[str, Any]) -> str:
    env_id = str(unit.get("env_id") or "").strip()
    profile_id = str(unit.get("profile_id") or "").strip()
    target_text = str(unit.get("target_text") or "").strip()
    meta = unit.get("meta") or {}
    detected_failures = [str(item).strip() for item in (meta.get("detected_failures") or []) if str(item).strip()]

    if signal_name in {"retrieval_selection_correctness", "profile_selection_correctness"}:
        return target_text or profile_id or env_id
    if signal_name in {"contract_validity", "critic_verdict_agreement"}:
        return "accept" if signal_target else "reject"
    if signal_name == "task_success":
        return "succeed" if signal_target else "fail"
    if signal_name == "repair_success":
        return target_text if signal_target and target_text else "repair_failed"
    if signal_name == "failure_localization":
        if signal_target and detected_failures:
            return "|".join(detected_failures)
        return "unlocalized_failure"
    if signal_name == "contract_family_match":
        return profile_id or env_id or target_text
    if signal_name == "transport_visible_output":
        return f"visible_output:{'true' if signal_target else 'false'}"
    if signal_name == "transport_no_fallback":
        return f"no_fallback:{'true' if signal_target else 'false'}"
    return target_text or ("positive" if signal_target else "negative")


def signal_bucket(signal_name: str, signal_target: int) -> str:
    if signal_target <= 0:
        return "negative"
    return PRIMARY_POSITIVE_BUCKET.get(signal_name, "weak_positive")


def signal_observation(unit: Dict[str, Any], signal: Dict[str, Any]) -> str:
    parts = [
        f"SIGNAL_NAME:\n{signal.get('name')}",
        f"SIGNAL_CHANNEL:\n{signal.get('channel')}",
        f"SUPPORT_ROLE:\n{unit.get('support_role')}",
        f"ENV_ID:\n{unit.get('env_id')}",
    ]
    profile_id = str(unit.get("profile_id") or "").strip()
    if profile_id:
        parts.append(f"PROFILE_ID:\n{profile_id}")
    note = str(signal.get("note") or "").strip()
    if note:
        parts.append(f"SIGNAL_NOTE:\n{note}")
    parts.append(f"BASE_OBSERVATION:\n{unit.get('observation')}")
    return "\n\n".join(parts)


def build_metrics(scorecard_summary: Dict[str, Any]) -> Dict[str, Any]:
    positive_counts = scorecard_summary.get("signal_positive_counts") or {}
    return {
        "rows": int(scorecard_summary.get("unit_count") or 0),
        "exact_positive_rows": max(
            int(positive_counts.get("contract_validity", 0) or 0),
            int(positive_counts.get("task_success", 0) or 0),
            int(positive_counts.get("repair_success", 0) or 0),
        ),
        "weak_positive_rows": int(positive_counts.get("critic_verdict_agreement", 0) or 0),
        "target_action_coverage": 0.0,
        "critic_bucket_accuracy": 0.0,
        "retriever_exact_match_rate": 0.0,
        "route_abstain_rate": 0.0,
    }


def compile_rows(
    scorecard_units: List[Dict[str, Any]],
    *,
    cluster_id: str,
    trainer_policy: Dict[str, Any],
    profile: Dict[str, Any],
) -> List[Dict[str, Any]]:
    task_family_label = str(profile.get("task_family_label") or f"metta_{cluster_id}")
    signal_weights = trainer_policy.get("signal_weights") or {}
    enabled_signals = set(str(item) for item in (trainer_policy.get("enabled_signals") or []))
    positive_weight_map = {
        "exact_positive": float(trainer_policy.get("exact_positive_weight") or 1.0),
        "near_miss": float(trainer_policy.get("near_miss_weight") or 1.0),
        "weak_positive": float(trainer_policy.get("weak_positive_weight") or 1.0),
        "negative": float(trainer_policy.get("negative_weight") or 0.2),
    }

    rows: List[Dict[str, Any]] = []
    for unit in scorecard_units:
        env_id = str(unit.get("env_id") or "").strip()
        profile_id = str(unit.get("profile_id") or "").strip()
        task_name = env_id if not profile_id else f"{env_id}:{profile_id}"
        prompt_pressure = str(unit.get("prompt_pressure_band") or "").strip()
        pressure_multiplier = 1.0
        if prompt_pressure == "high":
            pressure_multiplier = 0.95
        elif prompt_pressure == "low":
            pressure_multiplier = 1.05

        for signal in unit.get("signals") or []:
            signal_name = str(signal.get("name") or "").strip()
            if enabled_signals and signal_name not in enabled_signals:
                continue
            signal_target = int(signal.get("target") or 0)
            bucket = signal_bucket(signal_name, signal_target)
            bucket_weight = positive_weight_map[bucket]
            signal_weight = float(signal_weights.get(signal_name, 1.0) or 1.0)
            supervision_weight = round(bucket_weight * signal_weight * pressure_multiplier, 4)
            target_action = make_target_action(signal_name, signal_target, unit)
            reward = BUCKET_REWARD[bucket] if signal_target > 0 else 0.0

            row = {
                "source_env_name": env_id,
                "source_env_type": "MeTTaTrainerPolicyBundle",
                "task_family": f"{task_family_label}__{signal_name}",
                "task": task_name,
                "row_id": f"{unit.get('unit_id')}::{signal_name}",
                "observation": signal_observation(unit, signal),
                "model_action": target_action,
                "target_action": target_action,
                "bucket": bucket,
                "supervision_weight": supervision_weight,
                "reward": reward,
                "score": reward,
                "valid_action": True,
                "visible_output_emitted": signal_name != "transport_visible_output" or signal_target > 0,
                "reasoning_mode": "off",
                "reasoning_trace": [],
                "reasoning_summary": f"Multi-signal trainer-policy row synthesized for {signal_name}.",
                "meta": {
                    "cluster_id": cluster_id,
                    "profile_id": profile_id,
                    "support_role": unit.get("support_role"),
                    "unit_kind": unit.get("unit_kind"),
                    "signal_name": signal_name,
                    "signal_channel": signal.get("channel"),
                    "signal_target": signal_target,
                    "signal_weight": signal_weight,
                    "prompt_pressure_band": prompt_pressure,
                    "trainer_policy_name": trainer_policy.get("policy_name"),
                    "trainer_policy_support_tier": trainer_policy.get("support_tier"),
                    "trainer_policy_bucket": bucket,
                    "trainer_policy_weight_floor": trainer_policy.get("min_supervision_weight"),
                    "supervision_weight_source": "metta_signal_policy",
                    "candidate_text": unit.get("candidate_text"),
                    "target_text": unit.get("target_text"),
                },
            }
            unit_meta = unit.get("meta") or {}
            if isinstance(unit_meta, dict):
                row["meta"]["unit_meta"] = unit_meta
            rows.append(row)
    return rows


def build_summary(
    rows: List[Dict[str, Any]],
    *,
    bundle_dir: Path,
    scorecard_dir: Path,
    cluster_id: str,
    trainer_policy: Dict[str, Any],
) -> Dict[str, Any]:
    bucket_counts: Counter[str] = Counter()
    task_family_counts: Counter[str] = Counter()
    signal_counts: Counter[str] = Counter()
    channel_counts: Counter[str] = Counter()
    support_role_counts: Counter[str] = Counter()
    signal_positive_counts: Counter[str] = Counter()
    signal_negative_counts: Counter[str] = Counter()
    supervision_weights: List[float] = []

    for row in rows:
        bucket_counts[str(row.get("bucket") or "")] += 1
        task_family_counts[str(row.get("task_family") or "")] += 1
        supervision_weights.append(float(row.get("supervision_weight") or 0.0))
        meta = row.get("meta") or {}
        signal_name = str(meta.get("signal_name") or "")
        signal_channel = str(meta.get("signal_channel") or "")
        support_role = str(meta.get("support_role") or "")
        signal_counts[signal_name] += 1
        channel_counts[signal_channel] += 1
        support_role_counts[support_role] += 1
        if str(row.get("bucket") or "") == "negative":
            signal_negative_counts[signal_name] += 1
        else:
            signal_positive_counts[signal_name] += 1

    avg_supervision_weight = sum(supervision_weights) / len(supervision_weights) if supervision_weights else 0.0
    return {
        "bundle_dir": str(bundle_dir),
        "scorecard_dir": str(scorecard_dir),
        "cluster_id": cluster_id,
        "trainer_policy": trainer_policy,
        "row_count": len(rows),
        "avg_supervision_weight": round(avg_supervision_weight, 4),
        "bucket_counts": dict(bucket_counts),
        "task_family_counts": dict(task_family_counts),
        "signal_counts": dict(signal_counts),
        "signal_positive_counts": dict(signal_positive_counts),
        "signal_negative_counts": dict(signal_negative_counts),
        "channel_counts": dict(channel_counts),
        "support_role_counts": dict(support_role_counts),
    }


def render_markdown(summary: Dict[str, Any]) -> str:
    trainer_policy = summary.get("trainer_policy") or {}
    lines = [
        "# MeTTa Trainer-Policy Bundle",
        "",
        f"- cluster_id: `{summary.get('cluster_id', '')}`",
        f"- row_count: `{summary.get('row_count', 0)}`",
        f"- avg_supervision_weight: `{summary.get('avg_supervision_weight', 0.0)}`",
        "",
        "## Trainer Policy",
        "",
        f"- policy_name: `{trainer_policy.get('policy_name', '')}`",
        f"- support_tier: `{trainer_policy.get('support_tier', '')}`",
        f"- routing_strength: `{trainer_policy.get('routing_strength', '')}`",
        f"- min_supervision_weight: `{trainer_policy.get('min_supervision_weight', 0.0)}`",
        "",
        "## Signal Counts",
        "",
        "| Signal | Total | Positive | Negative |",
        "| --- | ---: | ---: | ---: |",
    ]
    for signal_name in sorted((summary.get("signal_counts") or {}).keys()):
        total = int((summary.get("signal_counts") or {}).get(signal_name, 0))
        positive = int((summary.get("signal_positive_counts") or {}).get(signal_name, 0))
        negative = int((summary.get("signal_negative_counts") or {}).get(signal_name, 0))
        lines.append(f"| {signal_name} | {total} | {positive} | {negative} |")
    lines.extend(
        [
            "",
            "## Bucket Counts",
            "",
            "| Bucket | Count |",
            "| --- | ---: |",
        ]
    )
    for bucket_name in sorted((summary.get("bucket_counts") or {}).keys()):
        count = int((summary.get("bucket_counts") or {}).get(bucket_name, 0))
        lines.append(f"| {bucket_name} | {count} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    bundle_dir = Path(args.bundle_dir).resolve()
    scorecard_dir = Path(args.scorecard_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    manifest_path = Path(args.manifest_path).resolve()

    cluster_id = infer_cluster_id(args.cluster_id, bundle_dir, manifest_path)
    profiles = load_cluster_profiles(manifest_path)
    profile = profiles.get(cluster_id, {})
    trainer_policy = build_trainer_policy(cluster_id, build_metrics(load_json(scorecard_dir / "metta_multi_signal_scorecard.summary.json")), profile)
    scorecard_units = load_jsonl(scorecard_dir / "metta_multi_signal_scorecard.jsonl")
    rows = compile_rows(scorecard_units, cluster_id=cluster_id, trainer_policy=trainer_policy, profile=profile)
    summary = build_summary(rows, bundle_dir=bundle_dir, scorecard_dir=scorecard_dir, cluster_id=cluster_id, trainer_policy=trainer_policy)

    rows_path = out_dir / "metta_trainer_policy_bundle.jsonl"
    summary_path = out_dir / "metta_trainer_policy_bundle.summary.json"
    md_path = out_dir / "metta_trainer_policy_bundle.md"
    write_jsonl(rows_path, rows)
    write_json(summary_path, summary)
    md_path.write_text(render_markdown(summary), encoding="utf-8", newline="\n")

    print(str(rows_path))
    print(str(summary_path))
    print(str(md_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
