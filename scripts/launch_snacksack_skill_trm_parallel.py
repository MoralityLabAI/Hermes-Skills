from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STAGE_ROOT = ROOT / "data" / "primehub_skill_trm_matrix" / "latest"
DEFAULT_MANIFEST = ROOT / "data" / "primehub_skill_batch_evolution" / "latest.manifest.json"
HARNESS_ROOT = Path(r"C:/projects/trm_observability_harness")


def run(cmd: List[str]) -> str:
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ssh_cmd(host: str, user: str, remote_cmd: str) -> List[str]:
    return ["ssh", "-o", "BatchMode=yes", f"{user}@{host}", remote_cmd]


def scp_cmd(local_path: Path, remote_target: str) -> List[str]:
    return ["scp", "-q", "-r", str(local_path), remote_target]


def ensure_remote_dir(host: str, user: str, remote_dir: str) -> None:
    run(ssh_cmd(host, user, f"mkdir -p '{remote_dir}'"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy staged specialist TRM bundles to snacksack and launch capped parallel jobs.")
    parser.add_argument("--stage-root", default=str(DEFAULT_STAGE_ROOT))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--cluster", action="append", default=[])
    parser.add_argument("--host", default="snacksack-ms-7d32.tail3156cd.ts.net")
    parser.add_argument("--user", default="snacksack")
    parser.add_argument("--remote-base", default="/home/snacksack/outputs/hermes_skill_trm_parallel")
    parser.add_argument("--ram-mb", type=int, default=5120)
    parser.add_argument("--cpu-quota", type=int, default=200)
    args = parser.parse_args()

    stage_root = Path(args.stage_root).resolve()
    manifest = load_json(Path(args.manifest).resolve())
    selected_clusters = args.cluster or list(manifest.get("recommended_parallel_training_clusters") or [])
    stage_manifest = load_json(stage_root / "manifest.json")

    stamp = now_stamp()
    remote_root = f"{args.remote_base.rstrip('/')}/{stamp}"
    for suffix in ["", "/scripts", "/harness", "/clusters"]:
        ensure_remote_dir(args.host, args.user, remote_root + suffix)

    for script_name in [
        "train_trm_critic.py",
        "bench_trm_critic.py",
        "train_trm_retriever.py",
        "bench_trm_retriever.py",
        "bench_trm_router.py",
    ]:
        run(scp_cmd(HARNESS_ROOT / "scripts" / script_name, f"{args.user}@{args.host}:{remote_root}/scripts/"))
    run(scp_cmd(HARNESS_ROOT / "harness", f"{args.user}@{args.host}:{remote_root}/"))
    run(scp_cmd(ROOT / "scripts" / "run_remote_skill_trm_cluster.py", f"{args.user}@{args.host}:{remote_root}/"))

    launch_records: List[Dict[str, Any]] = []
    for cluster_id in selected_clusters:
        cluster_info = (stage_manifest.get("clusters") or {}).get(cluster_id)
        if not cluster_info:
            continue
        local_cluster_dir = stage_root / cluster_id
        run(scp_cmd(local_cluster_dir, f"{args.user}@{args.host}:{remote_root}/clusters/"))
        profile = (manifest.get("cluster_profiles") or {}).get(cluster_id) or {}
        remote_cluster_dir = f"{remote_root}/clusters/{cluster_id}"
        unit = f"hermes-skill-trm-{cluster_id.replace('_', '-')}-{stamp[-6:].lower()}"
        log_path = f"{remote_cluster_dir}/run.log"
        remote_cmd = (
            "systemd-run --user --unit "
            + unit
            + " --collect -p MemoryMax="
            + str(args.ram_mb)
            + "M -p CPUQuota="
            + str(args.cpu_quota)
            + "% /bin/bash -lc 'cd "
            + remote_root
            + " && /usr/bin/python3 run_remote_skill_trm_cluster.py"
            + " --cluster-id "
            + cluster_id
            + " --input "
            + remote_cluster_dir
            + "/cluster_merged.jsonl"
            + " --out-dir "
            + remote_cluster_dir
            + " --top-k "
            + str(int(profile.get("top_k") or 5))
            + " --holdout-ratio "
            + str(float(profile.get("holdout_ratio") or 0.2))
            + " --min-supervision-weight "
            + str(float(profile.get("min_supervision_weight") or 0.4))
            + " > "
            + log_path
            + " 2>&1'"
        )
        stdout = run(ssh_cmd(args.host, args.user, remote_cmd))
        launch_records.append(
            {
                "cluster_id": cluster_id,
                "unit": unit,
                "remote_cluster_dir": remote_cluster_dir,
                "log_path": log_path,
                "systemd_stdout": stdout,
            }
        )

    summary = {
        "remote_root": remote_root,
        "clusters": launch_records,
        "host": args.host,
        "user": args.user,
        "ram_mb": args.ram_mb,
        "cpu_quota": args.cpu_quota,
    }
    summary_path = stage_root / "snacksack_launch.summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(str(summary_path.resolve()))


if __name__ == "__main__":
    main()
