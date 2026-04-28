from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ROOTS = [
    ROOT / "data" / "primehub_eligible_benchmark_v1",
    ROOT / "data" / "primehub_eligible_benchmark_v1_retry_27b_tail",
    ROOT / "data" / "primehub_eligible_benchmark_v2_47env",
]
DEFAULT_AUDIT_SUMMARY = ROOT / "data" / "primehub_bridge_audit_full_v4" / "audit_prime_env_bridge.summary.json"
DEFAULT_BENCHMARK_RUN_ROOT = ROOT / "data" / "primehub_eligible_benchmark_v2_47env"
DEFAULT_SKILL_SIDE_CAR_ROOTS = [
    ROOT / "intellect3-logic-hermes" / "references",
    ROOT / "intellect3-math-hermes" / "references",
]


@dataclass
class Proposal:
    priority: int
    title: str
    rationale: str
    expected_gain: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "priority": self.priority,
            "title": self.title,
            "rationale": self.rationale,
            "expected_gain": self.expected_gain,
        }


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def publish_skill_sidecars(json_source: Path, md_source: Path, cycle_index: int) -> Dict[str, Any]:
    published: List[Dict[str, str]] = []
    for refs_root in DEFAULT_SKILL_SIDE_CAR_ROOTS:
        refs_root.mkdir(parents=True, exist_ok=True)
        imprints_root = refs_root / "imprints"
        imprints_root.mkdir(parents=True, exist_ok=True)

        latest_json = refs_root / "primehub_skill_imprint.latest.json"
        latest_md = refs_root / "primehub_skill_imprint.latest.md"
        version_json = imprints_root / f"primehub_skill_imprint.cycle_{cycle_index:02d}.json"
        version_md = imprints_root / f"primehub_skill_imprint.cycle_{cycle_index:02d}.md"

        shutil.copyfile(json_source, latest_json)
        shutil.copyfile(md_source, latest_md)
        shutil.copyfile(json_source, version_json)
        shutil.copyfile(md_source, version_md)
        published.append(
            {
                "refs_root": str(refs_root),
                "latest_json": str(latest_json),
                "latest_md": str(latest_md),
                "version_json": str(version_json),
                "version_md": str(version_md),
            }
        )
    return {"published": published}


def discover_replay_files(run_roots: List[Path]) -> List[Path]:
    files: List[Path] = []
    seen = set()
    for run_root in run_roots:
        if not run_root.exists():
            continue
        for path in sorted(run_root.rglob("*.jsonl")):
            if "qwen35_" not in str(path.parent).lower():
                continue
            key = str(path.resolve()).lower()
            if key not in seen:
                seen.add(key)
                files.append(path.resolve())
    return files


def replay_snapshot(run_roots: List[Path]) -> Dict[str, Any]:
    files = discover_replay_files(run_roots)
    reward_ge_1 = 0
    reward_gt_0 = 0
    model_counts: Counter[str] = Counter()
    for path in files:
        try:
            with path.open("r", encoding="utf-8") as handle:
                first = None
                for line in handle:
                    line = line.strip()
                    if line:
                        first = json.loads(line)
                        break
            if first is None:
                continue
            model_counts[str(first.get("model_name") or "")] += 1
            reward = float(first.get("reward") or 0.0)
            if reward >= 1.0:
                reward_ge_1 += 1
            if reward > 0:
                reward_gt_0 += 1
        except Exception:
            continue
    return {
        "replay_files": len(files),
        "reward_ge_1_files": reward_ge_1,
        "reward_gt_0_files": reward_gt_0,
        "model_file_counts": dict(model_counts),
    }


def benchmark_progress(run_root: Path, audit_summary: Path, models: List[str]) -> Dict[str, Any]:
    ledger_path = run_root / "ledger.jsonl"
    if not ledger_path.exists():
        return {"success_count": 0, "missing_count": None, "missing_keys_head": []}

    success = set()
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if row.get("status") == "success":
            key = str(row.get("task_key") or "")
            if key:
                success.add(key)

    if not audit_summary.exists():
        return {"success_count": len(success), "missing_count": None, "missing_keys_head": []}

    summary = load_json(audit_summary)
    env_ids = [str(item) for item in summary.get("eligible_env_ids", []) if str(item).strip()]
    expected = [f"{model}:{env_id}" for model in models for env_id in env_ids]
    missing = [key for key in expected if key not in success]
    return {
        "success_count": len(success),
        "missing_count": len(missing),
        "missing_keys_head": missing[:20],
    }


def wrapper_active(event_log: Path, stale_after_seconds: int) -> Dict[str, Any]:
    if not event_log.exists():
        return {"active": False, "reason": "missing_event_log"}
    lines = [line for line in event_log.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return {"active": False, "reason": "empty_event_log"}
    try:
        last = json.loads(lines[-1])
    except json.JSONDecodeError:
        return {"active": False, "reason": "invalid_event_log_tail"}
    if last.get("event") == "finish":
        return {"active": False, "reason": "finish_event_present"}

    mtime_age = time.time() - event_log.stat().st_mtime
    return {
        "active": mtime_age <= stale_after_seconds,
        "reason": "fresh_heartbeat" if mtime_age <= stale_after_seconds else "stale_event_log",
        "last_event": last.get("event"),
        "mtime_age_seconds": round(mtime_age, 1),
    }


def run_rollup(work_dir: Path, run_roots: List[Path]) -> Dict[str, Any]:
    cmd = [sys.executable, str(ROOT / "scripts" / "run_primehub_trm_rollup.py")]
    for run_root in run_roots:
        cmd.extend(["--run-root", str(run_root)])
    cmd.extend(["--work-dir", str(work_dir)])
    subprocess.run(cmd, cwd=str(ROOT), check=True)
    manifest = load_json(work_dir / "primehub_trm_rollup.manifest.json")
    critic = load_json(work_dir / "bench" / "trm_critic_bench.summary.json")
    retriever = load_json(work_dir / "bench" / "trm_retriever_bench.summary.json")
    router = load_json(work_dir / "bench" / "trm_router_bench.summary.json")
    imprint_dir = work_dir / "imprint"
    imprint_json = imprint_dir / "primehub_skill_imprint.json"
    imprint_md = imprint_dir / "primehub_skill_imprint.md"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_primehub_skill_imprint.py"),
            "--merged-jsonl",
            str(work_dir / "primehub_trm_merged.jsonl"),
            "--critic-summary",
            str(work_dir / "bench" / "trm_critic_bench.summary.json"),
            "--retriever-summary",
            str(work_dir / "bench" / "trm_retriever_bench.summary.json"),
            "--router-summary",
            str(work_dir / "bench" / "trm_router_bench.summary.json"),
            "--output-json",
            str(imprint_json),
            "--output-md",
            str(imprint_md),
        ],
        cwd=str(ROOT),
        check=True,
    )
    imprint = load_json(imprint_json)
    return {
        "manifest": manifest,
        "critic_bench": critic,
        "retriever_bench": retriever,
        "router_bench": router,
        "skill_imprint": imprint,
        "skill_imprint_json": str(imprint_json),
        "skill_imprint_md": str(imprint_md),
    }


def build_proposals(
    replay: Dict[str, Any],
    progress: Dict[str, Any],
    wrapper: Dict[str, Any],
    rollup: Dict[str, Any],
) -> List[Proposal]:
    proposals: List[Proposal] = []
    merged = (rollup.get("manifest") or {}).get("merged") or {}
    critic = rollup.get("critic_bench") or {}
    retriever = rollup.get("retriever_bench") or {}
    router = rollup.get("router_bench") or {}

    exact_positive = int((merged.get("bucket_counts") or {}).get("exact_positive") or 0)
    weak_positive = int((merged.get("bucket_counts") or {}).get("weak_positive") or 0)
    target_cov = float(merged.get("target_action_coverage") or 0.0)
    critic_acc = float(critic.get("bucket_accuracy") or 0.0)
    retrieval_exact = float(retriever.get("exact_match_rate") or 0.0)
    abstain_rate = float(((router.get("critic_gated") or {}).get("route_abstain_rate")) or 0.0)

    if progress.get("missing_count") not in (None, 0):
        if wrapper.get("active"):
            proposals.append(
                Proposal(
                    priority=1,
                    title="Keep the Prime collector running",
                    rationale=(
                        f"There are still {progress['missing_count']} missing Prime tasks and the capped collector is active. "
                        "More replay coverage is the fastest way to improve the TRM corpus."
                    ),
                    expected_gain="More exact positives and weak positives for the next TRM rollup.",
                )
            )
        else:
            proposals.append(
                Proposal(
                    priority=1,
                    title="Resume the missing Prime tasks",
                    rationale=(
                        f"There are still {progress['missing_count']} missing Prime tasks and no active collector heartbeat."
                    ),
                    expected_gain="Complete the current 47-env benchmark slice before changing the trainer stack.",
                )
            )

    if exact_positive < 20:
        proposals.append(
            Proposal(
                priority=2,
                title="Grow exact-positive Prime rows before expecting router gains",
                rationale=(
                    f"The merged Prime corpus has only {exact_positive} exact positives and {weak_positive} weak positives."
                ),
                expected_gain="Increase target-bearing supervision so retrieval and routing stop being exemplar-starved.",
            )
        )

    if target_cov < 0.25:
        proposals.append(
            Proposal(
                priority=3,
                title="Treat the Prime corpus as control-plane supervision first",
                rationale=(
                    f"Target-action coverage is only {target_cov:.4f}, so retrieval-style action supervision is still sparse."
                ),
                expected_gain="Use the corpus for critic, abstention, and failure-shape learning while collection continues.",
            )
        )

    if critic_acc >= 0.7 and retrieval_exact <= 0.05:
        proposals.append(
            Proposal(
                priority=4,
                title="Use the critic as the current self-improvement spine",
                rationale=(
                    f"Critic bucket accuracy is {critic_acc:.4f} while retrieval exact match is {retrieval_exact:.4f}."
                ),
                expected_gain="Focus recursive improvement on grading, abstention, and route selection rather than direct action imitation.",
            )
        )

    if abstain_rate >= 0.8:
        proposals.append(
            Proposal(
                priority=5,
                title="Lower abstention by expanding positive support, not by weakening the critic",
                rationale=(
                    f"The critic-gated router abstains on {abstain_rate:.4f} of eval rows because the positive action bank is still too small."
                ),
                expected_gain="Preserve critic conservatism while making retrieval candidates actually useful.",
            )
        )

    return sorted(proposals, key=lambda item: item.priority)


def main() -> None:
    parser = argparse.ArgumentParser(description="Receipts-first Prime/TRM autoresearch loop.")
    parser.add_argument("--run-root", action="append", dest="run_roots", default=[])
    parser.add_argument("--benchmark-run-root", default=str(DEFAULT_BENCHMARK_RUN_ROOT))
    parser.add_argument("--audit-summary", default=str(DEFAULT_AUDIT_SUMMARY))
    parser.add_argument("--watch-event-log", default=str(ROOT / "data" / "job_limited_runs" / "primehub-47env-9b27b-resume5.events.jsonl"))
    parser.add_argument("--models", nargs="+", default=["qwen35_9b", "qwen35_27b"])
    parser.add_argument("--work-base", default=str(ROOT / "data" / "primehub_trm_autoresearch"))
    parser.add_argument("--summary", default=str(ROOT / "data" / "primehub_trm_autoresearch" / "latest.summary.json"))
    parser.add_argument("--ledger", default=str(ROOT / "data" / "primehub_trm_autoresearch" / "ledger.jsonl"))
    parser.add_argument("--latest-skill-imprint-json", default=str(ROOT / "data" / "primehub_trm_autoresearch" / "latest.skill_imprint.json"))
    parser.add_argument("--latest-skill-imprint-md", default=str(ROOT / "data" / "primehub_trm_autoresearch" / "latest.skill_imprint.md"))
    parser.add_argument("--publish-skill-sidecars", action="store_true")
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--sleep-seconds", type=int, default=300)
    parser.add_argument("--reroll-on-any-growth", action="store_true")
    parser.add_argument("--stale-after-seconds", type=int, default=600)
    args = parser.parse_args()

    run_roots = [Path(item).resolve() for item in (args.run_roots or [str(path) for path in DEFAULT_RUN_ROOTS])]
    summary_path = Path(args.summary).resolve()
    ledger_path = Path(args.ledger).resolve()
    work_base = Path(args.work_base).resolve()
    audit_summary = Path(args.audit_summary).resolve()
    benchmark_run_root = Path(args.benchmark_run_root).resolve()
    watch_event_log = Path(args.watch_event_log).resolve()
    latest_skill_imprint_json = Path(args.latest_skill_imprint_json).resolve()
    latest_skill_imprint_md = Path(args.latest_skill_imprint_md).resolve()

    last_replay_count = -1
    latest_payload: Dict[str, Any] = {}

    for cycle_index in range(1, max(1, args.cycles) + 1):
        replay = replay_snapshot(run_roots)
        progress = benchmark_progress(benchmark_run_root, audit_summary, args.models)
        wrapper = wrapper_active(watch_event_log, args.stale_after_seconds)
        should_reroll = cycle_index == 1 or args.reroll_on_any_growth or replay["replay_files"] != last_replay_count

        rollup_data: Dict[str, Any] | None = None
        rollup_dir: Optional[Path] = None
        if should_reroll:
            rollup_dir = work_base / f"cycle_{cycle_index:02d}"
            rollup_data = run_rollup(rollup_dir, run_roots)
            last_replay_count = replay["replay_files"]
        else:
            previous_summary = latest_payload.get("rollup") or {}
            rollup_data = previous_summary if isinstance(previous_summary, dict) else {}

        proposals = build_proposals(replay, progress, wrapper, rollup_data or {})
        latest_payload = {
            "timestamp_utc": now_iso(),
            "cycle_index": cycle_index,
            "run_roots": [str(path) for path in run_roots],
            "replay": replay,
            "benchmark_progress": progress,
            "collector_wrapper": wrapper,
            "rollup_dir": str(rollup_dir) if rollup_dir else None,
            "rollup": rollup_data,
            "proposals": [proposal.to_dict() for proposal in proposals],
        }
        rollup_imprint = (rollup_data or {}).get("skill_imprint") or {}
        if rollup_imprint:
            write_json(latest_skill_imprint_json, rollup_imprint)
            md_source = Path(str((rollup_data or {}).get("skill_imprint_md") or ""))
            if md_source.exists():
                latest_skill_imprint_md.parent.mkdir(parents=True, exist_ok=True)
                latest_skill_imprint_md.write_text(md_source.read_text(encoding="utf-8"), encoding="utf-8")
            latest_payload["latest_skill_imprint_json"] = str(latest_skill_imprint_json)
            latest_payload["latest_skill_imprint_md"] = str(latest_skill_imprint_md)
            if args.publish_skill_sidecars and latest_skill_imprint_md.exists():
                latest_payload["skill_sidecars"] = publish_skill_sidecars(
                    latest_skill_imprint_json,
                    latest_skill_imprint_md,
                    cycle_index,
                )
        write_json(summary_path, latest_payload)
        append_jsonl(ledger_path, latest_payload)

        if cycle_index < args.cycles:
            time.sleep(max(1, args.sleep_seconds))

    print(json.dumps({"summary": str(summary_path), "proposal_count": len(latest_payload.get("proposals", []))}, indent=2))


if __name__ == "__main__":
    main()
