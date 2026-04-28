from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile a compact runtime packet from a rich MeTTa bundle.")
    parser.add_argument("--bundle-dir", required=True, help="Directory containing bundle.manifest.json and retrieval artifacts.")
    parser.add_argument("--out-dir", default="", help="Optional output directory. Defaults to the bundle directory.")
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not decode to an object")
    return payload


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def unique(values: Iterable[Any], limit: int) -> List[str]:
    seen: set[str] = set()
    items: List[str] = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        items.append(text)
        if len(items) >= limit:
            break
    return items


def load_bundle(bundle_dir: Path) -> Dict[str, Any]:
    bundle_manifest = read_json(bundle_dir / "bundle.manifest.json")
    retrieval_packet = read_json(bundle_dir / "retrieval_packet.json")
    critic_hints = read_json(bundle_dir / "critic_hints.json")
    trace_labels = read_json(bundle_dir / "trace_labels.json")
    return {
        "manifest": bundle_manifest,
        "retrieval_packet": retrieval_packet.get("envs") or {},
        "critic_hints": critic_hints.get("envs") or {},
        "trace_labels": trace_labels.get("envs") or {},
    }


def build_runtime_packet(bundle: Dict[str, Any]) -> Dict[str, Any]:
    envs: Dict[str, Any] = {}
    retrieval_envs: Dict[str, Dict[str, Any]] = bundle["retrieval_packet"]
    critic_envs: Dict[str, Dict[str, Any]] = bundle["critic_hints"]
    trace_envs: Dict[str, Dict[str, Any]] = bundle["trace_labels"]
    for env_id, retrieval_env in retrieval_envs.items():
        critic_env = critic_envs.get(env_id) or {}
        trace_env = trace_envs.get(env_id) or {}
        must_do = unique(
            list(retrieval_env.get("constraints") or []) + list(retrieval_env.get("validator_notes") or []),
            limit=5,
        )
        avoid = unique(
            list(retrieval_env.get("forbids") or []) + list(trace_env.get("failure_modes") or []) + list(retrieval_env.get("failure_modes") or []),
            limit=5,
        )
        repair_focus = unique(
            list(trace_env.get("repair_hints") or []) + list(retrieval_env.get("repair_hints") or []) + list(critic_env.get("repair_hints") or []),
            limit=2,
        )
        query_cues = unique(retrieval_env.get("query_cues") or [], limit=3)
        env_packet = {
            "answer_shape": str(retrieval_env.get("answer_shape") or critic_env.get("required_shape") or "").strip(),
            "summary": str(retrieval_env.get("summary") or "").strip(),
            "query_cues": query_cues,
            "must_do": must_do,
            "avoid": avoid,
            "minimal_example": str(retrieval_env.get("minimal_example") or "").strip(),
            "repair_focus": repair_focus,
            "contract_priority": str((retrieval_env.get("retrieval_priorities") or [""])[0]).strip(),
            "validation_path": str(retrieval_env.get("validation_path") or "").strip(),
        }
        retrieval_profiles = retrieval_env.get("profiles") or {}
        critic_profiles = critic_env.get("profiles") or {}
        if isinstance(retrieval_profiles, dict) and retrieval_profiles:
            compact_profiles: Dict[str, Any] = {}
            for profile_id, profile_payload in retrieval_profiles.items():
                if not isinstance(profile_payload, dict):
                    continue
                critic_profile = critic_profiles.get(profile_id) if isinstance(critic_profiles, dict) else {}
                compact_profiles[str(profile_id)] = {
                    "summary": str(profile_payload.get("summary") or "").strip(),
                    "query_cues": unique(profile_payload.get("query_cues") or [], limit=3),
                    "must_do": unique(
                        list(profile_payload.get("constraints") or []) + list((critic_profile or {}).get("checks") or []),
                        limit=5,
                    ),
                    "avoid": unique(profile_payload.get("forbids") or [], limit=4),
                    "minimal_example": str(profile_payload.get("minimal_example") or "").strip(),
                    "repair_focus": unique(
                        list(profile_payload.get("repair_hints") or []) + list((critic_profile or {}).get("repair_hints") or []),
                        limit=2,
                    ),
                }
            if compact_profiles:
                env_packet["profiles"] = compact_profiles
        envs[env_id] = env_packet
    return {
        "packet_type": "metta_runtime_packet_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "package_id": str(bundle["manifest"].get("package_id") or "").strip(),
        "base_skill": str(bundle["manifest"].get("base_skill") or "").strip(),
        "trm_overlay": str(bundle["manifest"].get("trm_overlay") or "").strip(),
        "envs": envs,
    }


def build_summary(runtime_packet: Dict[str, Any], bundle_dir: Path, out_dir: Path) -> Dict[str, Any]:
    env_summaries: Dict[str, Any] = {}
    for env_id, env_payload in (runtime_packet.get("envs") or {}).items():
        env_summaries[str(env_id)] = {
            "query_cue_count": len(env_payload.get("query_cues") or []),
            "must_do_count": len(env_payload.get("must_do") or []),
            "avoid_count": len(env_payload.get("avoid") or []),
            "repair_focus_count": len(env_payload.get("repair_focus") or []),
            "profile_count": len(env_payload.get("profiles") or {}),
            "summary_chars": len(str(env_payload.get("summary") or "")),
            "minimal_example_chars": len(str(env_payload.get("minimal_example") or "")),
        }
    return {
        "bundle_dir": str(bundle_dir),
        "out_dir": str(out_dir),
        "packet_type": str(runtime_packet.get("packet_type") or ""),
        "package_id": str(runtime_packet.get("package_id") or ""),
        "env_count": len(runtime_packet.get("envs") or {}),
        "env_summaries": env_summaries,
    }


def main() -> int:
    args = parse_args()
    bundle_dir = Path(args.bundle_dir).resolve()
    out_dir = Path(args.out_dir).resolve() if str(args.out_dir).strip() else bundle_dir
    bundle = load_bundle(bundle_dir)
    runtime_packet = build_runtime_packet(bundle)
    summary = build_summary(runtime_packet, bundle_dir, out_dir)
    runtime_packet_path = out_dir / "runtime_packet.json"
    summary_path = out_dir / "runtime_packet.summary.json"
    write_json(runtime_packet_path, runtime_packet)
    write_json(summary_path, summary)
    print(str(runtime_packet_path))
    print(str(summary_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
