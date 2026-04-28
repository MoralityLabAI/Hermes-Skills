from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


DEFAULT_MANIFEST = Path(r"C:/projects/Hermes-Skills/Hermes Skills/data/primehub_env_manifest.json")
DEFAULT_BRIDGE_SCRIPT = Path(__file__).resolve().parent / "remote_prime_env_bridge.py"
DEFAULT_OUT_DIR = Path(r"C:/projects/Hermes-Skills/Hermes Skills/data/primehub_bridge_audit")
DEFAULT_HOST = "snacksack-ms-7d32.tail3156cd.ts.net"
DEFAULT_USER = "snacksack"
DEFAULT_IDENTITY_FILE = Path(r"C:/Users/patri/.ssh/id_ed25519")
DEFAULT_RESEARCH_ROOT = "/home/snacksack/prime_repos_tmp/research-environments/environments"
DEFAULT_COMMUNITY_ROOT = "/home/snacksack/prime_repos_tmp/community-environments/environments"
DEFAULT_JUDGE_BASE_URL = f"http://{DEFAULT_HOST}:8081/v1"
DEFAULT_JUDGE_MODEL = "Qwen3.5-27B.Q4_K_M.gguf"


def split_values(values: Iterable[str]) -> List[str]:
    items: List[str] = []
    for value in values:
        for piece in str(value).split(","):
            text = piece.strip()
            if text:
                items.append(text)
    return items


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def load_profiles(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    profiles = payload.get("profiles", [])
    if not isinstance(profiles, list):
        raise ValueError(f"manifest {path} has invalid profiles")
    return [profile for profile in profiles if isinstance(profile, dict)]


def filter_profiles(
    profiles: List[Dict[str, Any]],
    sources: List[str],
    owners: List[str],
    include: List[str],
    exclude: List[str],
    max_envs: int,
) -> List[Dict[str, Any]]:
    source_set = set(sources)
    owner_set = set(owners)
    include_set = set(include)
    exclude_set = set(exclude)
    selected: List[Dict[str, Any]] = []
    for profile in profiles:
        if not profile.get("available", True):
            continue
        env_id = str(profile.get("env_id", "")).strip()
        source = str(profile.get("source", "")).strip()
        owner = str(profile.get("owner", "")).strip()
        if not env_id or source not in source_set:
            continue
        if owner_set and owner not in owner_set:
            continue
        if include_set and env_id not in include_set:
            continue
        if env_id in exclude_set:
            continue
        selected.append(profile)
        if max_envs and len(selected) >= max_envs:
            break
    return selected


def build_command(args: argparse.Namespace, profile: Dict[str, Any]) -> List[str]:
    return [
        args.python,
        str(Path(args.bridge_script).resolve()),
        "--source",
        str(profile["source"]),
        "--probe",
        "--host",
        args.host,
        "--user",
        args.user,
        "--identity-file",
        args.identity_file,
        "--research-root",
        args.research_root,
        "--community-root",
        args.community_root,
        "--ssh-timeout-seconds",
        str(args.ssh_timeout_seconds),
        "--judge-base-url",
        args.judge_base_url,
        "--judge-model",
        args.judge_model,
        str(profile["env_id"]),
    ]


def parse_probe_output(result: subprocess.CompletedProcess[str]) -> Dict[str, Any]:
    text = (result.stdout or "").strip()
    if result.returncode != 0:
        return {
            "status": "process_error",
            "reason": (result.stderr or text or f"bridge exited with {result.returncode}").strip(),
            "env_type": "",
            "task": "",
            "observation_preview": "",
            "bridge_debug": "",
        }
    if not text:
        return {
            "status": "process_error",
            "reason": "bridge returned empty stdout",
            "env_type": "",
            "task": "",
            "observation_preview": "",
            "bridge_debug": "",
        }
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return {
            "status": "invalid_json",
            "reason": f"{exc}: {text[-400:]}",
            "env_type": "",
            "task": "",
            "observation_preview": "",
            "bridge_debug": "",
        }
    if not isinstance(payload, dict):
        return {
            "status": "invalid_json",
            "reason": "bridge payload was not an object",
            "env_type": "",
            "task": "",
            "observation_preview": "",
            "bridge_debug": "",
        }
    if not payload.get("reason") and payload.get("failure_message"):
        payload["reason"] = str(payload.get("failure_message", ""))
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Prime Intellect env compatibility through the snacksack SSH bridge.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--bridge-script", default=str(DEFAULT_BRIDGE_SCRIPT))
    parser.add_argument("--python", dest="python", default=sys.executable)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--stout", default="")
    parser.add_argument("--summary", default="")
    parser.add_argument("--sources", nargs="+", default=["research", "community"], choices=["research", "community"])
    parser.add_argument("--owner", nargs="*", default=[])
    parser.add_argument("--include", nargs="*", default=[])
    parser.add_argument("--exclude", nargs="*", default=[])
    parser.add_argument("--max-envs", type=int, default=0)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--identity-file", default=str(DEFAULT_IDENTITY_FILE))
    parser.add_argument("--research-root", default=DEFAULT_RESEARCH_ROOT)
    parser.add_argument("--community-root", default=DEFAULT_COMMUNITY_ROOT)
    parser.add_argument("--ssh-timeout-seconds", type=int, default=45)
    parser.add_argument("--judge-base-url", default=DEFAULT_JUDGE_BASE_URL)
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    stout_path = Path(args.stout).resolve() if args.stout else out_dir / "audit_prime_env_bridge.stout.jsonl"
    summary_path = Path(args.summary).resolve() if args.summary else out_dir / "audit_prime_env_bridge.summary.json"
    if stout_path.exists():
        stout_path.unlink()
    if summary_path.exists():
        summary_path.unlink()

    profiles = load_profiles(manifest_path)
    selected = filter_profiles(
        profiles,
        sources=list(args.sources),
        owners=split_values(args.owner),
        include=split_values(args.include),
        exclude=split_values(args.exclude),
        max_envs=args.max_envs,
    )

    append_jsonl(
        stout_path,
        {
            "ts": time.time(),
            "event": "audit_start",
            "manifest": str(manifest_path),
            "selected_envs": len(selected),
            "sources": list(args.sources),
            "owners": split_values(args.owner),
            "include": split_values(args.include),
            "exclude": split_values(args.exclude),
            "max_envs": args.max_envs,
            "bridge_script": str(Path(args.bridge_script).resolve()),
            "python": args.python,
            "host": args.host,
            "user": args.user,
        },
    )

    status_counts: Counter[str] = Counter()
    env_type_counts: Counter[str] = Counter()
    eligible_envs: List[str] = []
    results: List[Dict[str, Any]] = []

    for index, profile in enumerate(selected, start=1):
        env_id = str(profile["env_id"])
        start = time.time()
        command = build_command(args, profile)
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=max(30, args.ssh_timeout_seconds + 30),
                check=False,
            )
        except subprocess.TimeoutExpired:
            payload = {
                "status": "timeout",
                "reason": f"probe timed out after {max(30, args.ssh_timeout_seconds + 30)}s",
                "env_type": "",
                "task": "",
                "observation_preview": "",
                "bridge_debug": "",
            }
            returncode = -1
        else:
            payload = parse_probe_output(result)
            returncode = int(result.returncode)

        elapsed = time.time() - start
        status = str(payload.get("status", "failure"))
        env_type = str(payload.get("env_type", ""))
        record = {
            "ts": time.time(),
            "event": "env_result",
            "index": index,
            "total": len(selected),
            "env_id": env_id,
            "source": str(profile.get("source", "")),
            "owner": str(profile.get("owner", "")),
            "folder": str(profile.get("folder", "")),
            "status": status,
            "env_type": env_type,
            "reason": str(payload.get("reason", "")),
            "task": str(payload.get("task", "")),
            "observation_preview": str(payload.get("observation_preview", "")),
            "bridge_debug": str(payload.get("bridge_debug", "")),
            "returncode": returncode,
            "elapsed_seconds": round(elapsed, 3),
        }
        append_jsonl(stout_path, record)
        results.append(record)
        status_counts[status] += 1
        if env_type:
            env_type_counts[env_type] += 1
        if status == "ok":
            eligible_envs.append(env_id)

    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "manifest": str(manifest_path),
        "selected_envs": len(selected),
        "eligible_envs": len(eligible_envs),
        "status_counts": dict(status_counts),
        "env_type_counts": dict(env_type_counts),
        "eligible_env_ids": eligible_envs,
        "artifacts": {
            "stout": str(stout_path),
            "summary": str(summary_path),
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    append_jsonl(
        stout_path,
        {
            "ts": time.time(),
            "event": "audit_complete",
            "selected_envs": len(selected),
            "eligible_envs": len(eligible_envs),
            "status_counts": dict(status_counts),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
