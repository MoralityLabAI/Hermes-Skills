from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List

from compile_metta_rows import load_bundle, merge_profile_env
from metta_repair_pass import repair_candidate, selected_profile_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile MeTTa-informed transfer rows onto the original primehub task family.")
    parser.add_argument("--bundle-dir", required=True, help="Bundle directory containing runtime_packet.json and bundle.manifest.json.")
    parser.add_argument("--base-corpus", required=True, help="Base primehub TRM merged JSONL corpus.")
    parser.add_argument("--out-dir", required=True, help="Output directory for transfer rows.")
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


def join_items(values: List[str] | None, *, limit: int = 3) -> str:
    items = [str(value).strip() for value in (values or []) if str(value).strip()]
    return "; ".join(items[:limit])


def overlay_observation(
    original_observation: str,
    *,
    env_id: str,
    runtime_env: Dict[str, Any],
    overlay_kind: str,
) -> str:
    lines = [original_observation.strip()]
    summary = str(runtime_env.get("summary") or "").strip()
    must_do = join_items(runtime_env.get("must_do") or [])
    avoid = join_items(runtime_env.get("avoid") or [])
    repair_focus = join_items(runtime_env.get("repair_focus") or [], limit=2)
    validation_path = str(runtime_env.get("validation_path") or "").strip()
    answer_shape = str(runtime_env.get("answer_shape") or "").strip()
    profile_id = str(runtime_env.get("selected_profile_id") or "").strip()

    lines.extend(
        [
            "",
            "[TRM_TRANSFER]",
            f"env_id={env_id}",
            f"overlay_kind={overlay_kind}",
        ]
    )
    if profile_id:
        lines.append(f"profile_id={profile_id}")
    if answer_shape:
        lines.append(f"answer_shape={answer_shape}")
    if summary:
        lines.append(f"summary={summary}")
    if must_do:
        lines.append(f"must_do={must_do}")
    if avoid:
        lines.append(f"avoid={avoid}")
    if repair_focus and overlay_kind == "repair":
        lines.append(f"repair_focus={repair_focus}")
    if validation_path:
        lines.append(f"validation_path={validation_path}")
    return "\n".join(lines).strip()


def maybe_profile_env(env_id: str, runtime_env: Dict[str, Any], observation_text: str) -> Dict[str, Any]:
    profile = selected_profile_payload(runtime_env, observation_text)
    if not profile:
        return runtime_env
    profile_id = str(profile.get("profile_id") or "").strip()
    return merge_profile_env(runtime_env, profile_id, profile)


def base_transfer_row(
    base_row: Dict[str, Any],
    *,
    package_id: str,
    observation: str,
    overlay_kind: str,
    row_suffix: str,
    source_env_name: str,
) -> Dict[str, Any]:
    row = {
        "source_env_name": source_env_name,
        "source_env_type": "MeTTaPrimehubTransfer",
        "task_family": str(base_row.get("task_family") or "primehub"),
        "task": str(base_row.get("task") or ""),
        "row_id": f"{package_id}:{source_env_name}:{row_suffix}",
        "observation": observation,
        "model_action": base_row.get("model_action"),
        "target_action": base_row.get("target_action"),
        "bucket": str(base_row.get("bucket") or "negative"),
        "supervision_weight": float(base_row.get("supervision_weight") or 0.2),
        "reward": float(base_row.get("reward") or 0.0),
        "score": float(base_row.get("score") or base_row.get("reward") or 0.0),
        "valid_action": bool(base_row.get("valid_action", True)),
        "visible_output_emitted": bool(base_row.get("visible_output_emitted")),
        "reasoning_mode": str(base_row.get("reasoning_mode") or "off"),
        "reasoning_trace": list(base_row.get("reasoning_trace") or []),
        "reasoning_summary": f"Primehub transfer row synthesized from {overlay_kind}.",
        "meta": {
            "overlay_kind": overlay_kind,
            "transfer_origin_env": source_env_name,
            "transfer_origin_type": str(base_row.get("source_env_type") or ""),
            "transfer_origin_bucket": str(base_row.get("bucket") or ""),
            "transfer_origin_task": str(base_row.get("task") or ""),
            "transfer_origin_target_action": base_row.get("target_action"),
        },
    }
    if isinstance(base_row.get("meta"), dict):
        row["meta"]["transfer_origin_meta"] = base_row["meta"]
    return row


def clone_weight(base_row: Dict[str, Any]) -> float:
    bucket = str(base_row.get("bucket") or "negative")
    base_weight = float(base_row.get("supervision_weight") or 0.2)
    if bucket == "exact_positive":
        return round(max(base_weight * 1.15, 1.0), 4)
    if bucket == "weak_positive":
        return round(max(base_weight * 1.1, 0.4), 4)
    if bucket == "near_miss":
        return round(max(base_weight * 1.05, 0.5), 4)
    return round(base_weight, 4)


def repair_weight(base_row: Dict[str, Any]) -> float:
    base_weight = float(base_row.get("supervision_weight") or 0.2)
    return round(max(base_weight * 2.0, 0.7), 4)


def should_attempt_repair(model_action: str) -> bool:
    text = str(model_action or "").strip()
    if not text:
        return False
    lowered = text.lower()
    if lowered == "inspect_and_continue":
        return False
    if "i'm not going to" in lowered or "i am not going to" in lowered:
        return False
    return True


def build_transfer_rows(bundle_dir: Path, base_corpus: Path) -> List[Dict[str, Any]]:
    bundle = load_bundle(bundle_dir)
    package_id = str(bundle["manifest"].get("package_id") or bundle_dir.name).strip()
    runtime_envs = bundle["runtime_envs"]
    env_ids = set(runtime_envs.keys())
    base_rows = load_jsonl(base_corpus)
    transfer_rows: List[Dict[str, Any]] = []

    for index, base_row in enumerate(base_rows):
        if str(base_row.get("task_family") or "") != "primehub":
            continue
        env_id = str(base_row.get("source_env_name") or "").strip()
        if env_id not in env_ids:
            continue

        original_observation = str(base_row.get("observation") or "").strip()
        runtime_env = maybe_profile_env(env_id, runtime_envs[env_id], original_observation)

        clone_row = base_transfer_row(
            base_row,
            package_id=package_id,
            observation=overlay_observation(
                original_observation,
                env_id=env_id,
                runtime_env=runtime_env,
                overlay_kind="contract_clone",
            ),
            overlay_kind="contract_clone",
            row_suffix=f"clone:{index}",
            source_env_name=env_id,
        )
        clone_row["supervision_weight"] = clone_weight(base_row)
        transfer_rows.append(clone_row)

        model_action = str(base_row.get("model_action") or "").strip()
        if not should_attempt_repair(model_action):
            continue
        repair_report = repair_candidate(env_id, model_action, runtime_env, original_observation)
        repaired_text = str(repair_report.get("repaired_text") or "").strip()
        if not repaired_text:
            continue
        original_target = str(base_row.get("target_action") or "").strip()
        if repaired_text == original_target:
            continue

        repair_row = base_transfer_row(
            base_row,
            package_id=package_id,
            observation=overlay_observation(
                original_observation,
                env_id=env_id,
                runtime_env=runtime_env,
                overlay_kind="repair_projection",
            ),
            overlay_kind="repair_projection",
            row_suffix=f"repair:{index}",
            source_env_name=env_id,
        )
        repair_row["target_action"] = repaired_text
        repair_row["bucket"] = "near_miss" if str(base_row.get("bucket") or "") != "exact_positive" else "exact_positive"
        repair_row["reward"] = 0.7 if repair_row["bucket"] == "near_miss" else 1.0
        repair_row["score"] = repair_row["reward"]
        repair_row["supervision_weight"] = repair_weight(base_row)
        repair_row["meta"]["detected_failures"] = repair_report.get("detected_failures") or []
        repair_row["meta"]["applied_repairs"] = repair_report.get("applied_repairs") or []
        repair_row["meta"]["repaired_text"] = repaired_text
        transfer_rows.append(repair_row)

    return transfer_rows


def build_summary(bundle_dir: Path, base_corpus: Path, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    env_counts: Counter[str] = Counter()
    bucket_counts: Counter[str] = Counter()
    overlay_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    target_action_rows = 0
    for row in rows:
        env_counts[str(row.get("source_env_name") or "")] += 1
        bucket_counts[str(row.get("bucket") or "")] += 1
        family_counts[str(row.get("task_family") or "")] += 1
        overlay_counts[str((row.get("meta") or {}).get("overlay_kind") or "")] += 1
        if row.get("target_action"):
            target_action_rows += 1
    return {
        "bundle_dir": str(bundle_dir),
        "base_corpus": str(base_corpus),
        "row_count": len(rows),
        "target_action_rows": target_action_rows,
        "bucket_counts": dict(bucket_counts),
        "env_counts": dict(env_counts),
        "task_family_counts": dict(family_counts),
        "overlay_kind_counts": dict(overlay_counts),
    }


def render_markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# MeTTa Primehub Transfer Bundle",
        "",
        f"- row_count: `{summary.get('row_count', 0)}`",
        f"- target_action_rows: `{summary.get('target_action_rows', 0)}`",
        "",
        "## Env Counts",
        "",
        "| Env | Rows |",
        "| --- | ---: |",
    ]
    for env_id, count in sorted((summary.get("env_counts") or {}).items()):
        lines.append(f"| {env_id} | {count} |")
    lines.extend(
        [
            "",
            "## Bucket Counts",
            "",
            "| Bucket | Count |",
            "| --- | ---: |",
        ]
    )
    for bucket, count in sorted((summary.get("bucket_counts") or {}).items()):
        lines.append(f"| {bucket} | {count} |")
    lines.extend(
        [
            "",
            "## Overlay Kinds",
            "",
            "| Overlay | Count |",
            "| --- | ---: |",
        ]
    )
    for overlay_kind, count in sorted((summary.get("overlay_kind_counts") or {}).items()):
        lines.append(f"| {overlay_kind} | {count} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    bundle_dir = Path(args.bundle_dir).resolve()
    base_corpus = Path(args.base_corpus).resolve()
    out_dir = Path(args.out_dir).resolve()

    rows = build_transfer_rows(bundle_dir, base_corpus)
    summary = build_summary(bundle_dir, base_corpus, rows)

    write_jsonl(out_dir / "metta_primehub_transfer_bundle.jsonl", rows)
    write_json(out_dir / "metta_primehub_transfer_bundle.summary.json", summary)
    write_json(out_dir / "metta_primehub_transfer_bundle.manifest.json", summary)
    (out_dir / "metta_primehub_transfer_bundle.md").write_text(render_markdown(summary), encoding="utf-8", newline="\n")

    print(str(out_dir / "metta_primehub_transfer_bundle.summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
