"""Benchmark the Intellect-3-Math skill-patch bank on a live endpoint.

This runner evaluates every patch in the gym patch bank against held-out rows,
checkpointing each row-arm result to JSONL.  It is intentionally resumable:
rerunning the same output directory skips completed row/patch pairs unless
`--force` is supplied.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "research" / "scripts"
SELF_IMPROVE_SCRIPT = SCRIPTS / "run_intellect3_math_metta_self_improve.py"
ARTIFACTS = ROOT / "research" / "studies" / "2026-04-22-metta-trm-hermes-pipeline" / "artifacts"
DEFAULT_PATCH_BANK = ARTIFACTS / "intellect3_math_skill_patch_gym_20260502" / "patch_bank.json"
DEFAULT_OUT = ARTIFACTS / "intellect3_math_patch_bank_benchmark_27b_20260502"
DEFAULT_SOURCE = Path(r"C:\projects\Tesseract\Tesseract\data\normalized_trajectories\intellect_3_math.jsonl")
DEFAULT_BASE_URL = "http://snacksack-ms-7d32.tail3156cd.ts.net:8081/v1"


def load_self_improve_module():
    spec = importlib.util.spec_from_file_location("math_self_improve", SELF_IMPROVE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SELF_IMPROVE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SI = load_self_improve_module()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Intellect-3-Math patch-bank benchmark.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), type=Path)
    parser.add_argument("--patch-bank", default=str(DEFAULT_PATCH_BANK), type=Path)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), type=Path)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--holdout-rows", default=10, type=int)
    parser.add_argument("--start-offset", default=0, type=int)
    parser.add_argument("--patch-id", action="append", default=None, help="Optional patch id filter; repeatable.")
    parser.add_argument("--request-timeout", default=180, type=int)
    parser.add_argument("--max-tokens", default=32, type=int)
    parser.add_argument("--sleep-sec", default=0.25, type=float)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def heldout_rows(source: Path, *, limit: int, start_offset: int) -> list[dict[str, Any]]:
    all_rows = SI.load_math_rows(source)
    heldout = [row for idx, row in enumerate(all_rows) if idx % 2 == 1]
    return heldout[start_offset : start_offset + limit]


def run_patch(args: argparse.Namespace, row: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        result = SI.run_arm(
            args,
            row,
            arm=str(patch["patch_id"]),
            task_prefix=str(patch.get("task_prefix") or ""),
        )
        result["error"] = ""
    except Exception as exc:
        result = SI.error_row(row, arm=str(patch["patch_id"]), error=repr(exc))
    result.update(
        {
            "ts": utc_now(),
            "patch_id": patch["patch_id"],
            "patch_source": patch.get("source"),
            "patch_status": patch.get("status"),
            "elapsed_wall_seconds": round(time.perf_counter() - started, 4),
        }
    )
    return result


def summarize(rows: list[dict[str, Any]], patches: list[dict[str, Any]]) -> dict[str, Any]:
    by_patch: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_patch[str(row.get("patch_id") or row.get("arm"))].append(row)
    arms: dict[str, Any] = {}
    for patch in patches:
        patch_id = str(patch["patch_id"])
        patch_rows = by_patch.get(patch_id, [])
        arms[patch_id] = {
            "rows": len(patch_rows),
            "exact": sum(1 for row in patch_rows if row.get("exact")),
            "exact_rate": round(sum(1 for row in patch_rows if row.get("exact")) / max(1, len(patch_rows)), 6),
            "errors": sum(1 for row in patch_rows if row.get("error")),
            "avg_latency_seconds": round(
                sum(float(row.get("latency_seconds") or 0.0) for row in patch_rows) / max(1, len(patch_rows)), 4
            ),
            "common_actions": dict(Counter(str(row.get("action")) for row in patch_rows).most_common(8)),
        }

    incumbent_id = "incumbent_current_skill"
    incumbent_rows = {row["row_id"]: row for row in by_patch.get(incumbent_id, [])}
    gates: dict[str, Any] = {}
    for patch in patches:
        patch_id = str(patch["patch_id"])
        if patch_id == incumbent_id:
            continue
        fixes = 0
        regressions = 0
        changed_wrong = 0
        for row in by_patch.get(patch_id, []):
            incumbent = incumbent_rows.get(row["row_id"])
            if not incumbent:
                continue
            if not incumbent.get("exact") and row.get("exact"):
                fixes += 1
            elif incumbent.get("exact") and not row.get("exact"):
                regressions += 1
            elif incumbent.get("action") != row.get("action") and not row.get("exact"):
                changed_wrong += 1
        decision = "adopt_patch" if arms[patch_id]["exact"] > arms.get(incumbent_id, {}).get("exact", 0) and fixes >= regressions else "reject_patch"
        if patch_id == "raw_baseline_no_skill":
            decision = "comparison_only"
        gates[patch_id] = {
            "decision": decision,
            "fixes_vs_incumbent": fixes,
            "regressions_vs_incumbent": regressions,
            "changed_wrong_vs_incumbent": changed_wrong,
            "candidate_exact": arms[patch_id]["exact"],
            "incumbent_exact": arms.get(incumbent_id, {}).get("exact", 0),
        }

    best_patch = max(arms.items(), key=lambda item: (item[1]["exact"], -item[1]["errors"], item[0]))[0] if arms else ""
    return {
        "arms": arms,
        "adoption_gates": gates,
        "best_patch_by_exact": best_patch,
        "read": "Patch-bank benchmark over held-out rows; adoption is gated against the incumbent, not raw exact alone.",
    }


def trm_rows(rows: list[dict[str, Any]], summary: dict[str, Any]) -> list[dict[str, Any]]:
    by_row: dict[str, dict[str, Any]] = defaultdict(dict)
    for row in rows:
        by_row[str(row.get("row_id"))][str(row.get("patch_id"))] = row
    out: list[dict[str, Any]] = []
    for row_id, group in sorted(by_row.items()):
        incumbent = group.get("incumbent_current_skill")
        for patch_id, row in sorted(group.items()):
            if patch_id == "incumbent_current_skill":
                label = "incumbent"
                reason = "current_skill_baseline"
            elif patch_id == "raw_baseline_no_skill":
                label = "reject_patch"
                reason = "raw_baseline_control"
            elif not incumbent:
                label = "reject_patch"
                reason = "missing_incumbent_comparator"
            elif not incumbent.get("exact") and row.get("exact"):
                label = "commit_patch"
                reason = "fixes_incumbent_miss"
            elif incumbent.get("exact") and not row.get("exact"):
                label = "reject_patch"
                reason = "regresses_incumbent_hit"
            else:
                label = "reject_patch"
                reason = "no_exact_gain"
            out.append(
                {
                    "row_id": row_id,
                    "env_family": "intellect3_math_patch_bank_benchmark",
                    "patch_id": patch_id,
                    "state": {
                        "candidate_action": row.get("action"),
                        "incumbent_action": (incumbent or {}).get("action"),
                        "candidate_exact": bool(row.get("exact")),
                        "incumbent_exact": bool((incumbent or {}).get("exact")),
                        "patch_gate_decision": (summary.get("adoption_gates") or {}).get(patch_id, {}).get("decision"),
                    },
                    "label": label,
                    "reason": reason,
                    "target": {"adoption_action": "commit" if label == "commit_patch" else "reject_or_keep_incumbent"},
                }
            )
    return out


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Intellect-3-Math Patch-Bank Benchmark",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        f"Base URL: `{payload['base_url']}`",
        f"Rows requested: `{payload['holdout_rows']}`",
        f"Completed calls: `{payload['completed_calls']}`",
        "",
        "## Patch Scores",
        "",
        "| Patch | Rows | Exact | Exact Rate | Errors | Avg Latency | Gate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    summary = payload["summary"]
    gates = summary.get("adoption_gates") or {}
    for patch_id, metrics in summary["arms"].items():
        gate = gates.get(patch_id, {}).get("decision", "incumbent")
        lines.append(
            f"| `{patch_id}` | {metrics['rows']} | {metrics['exact']} | {metrics['exact_rate']:.4f} | "
            f"{metrics['errors']} | {metrics['avg_latency_seconds']:.2f}s | `{gate}` |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            summary["read"],
            "",
            f"Best raw exact patch: `{summary['best_patch_by_exact']}`.",
            "",
            "Adoption gates compare each patch against `incumbent_current_skill`; a patch with equal or lower exact is rejected even if it looks plausible.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_metta(payload: dict[str, Any]) -> str:
    lines = [
        ";; Live Intellect-3-Math patch-bank benchmark.",
        "(= env_id intellect3_math_patch_bank_benchmark)",
        "(= incumbent_patch incumbent_current_skill)",
    ]
    for patch_id, gate in (payload["summary"].get("adoption_gates") or {}).items():
        lines.append(f"(= (patch_gate {patch_id}) {gate['decision']})")
    for patch_id, metrics in payload["summary"]["arms"].items():
        lines.append(f"(= (patch_exact {patch_id}) {metrics['exact']}/{metrics['rows']})")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    patch_bank = load_json(args.patch_bank)
    if args.patch_id:
        wanted = set(args.patch_id)
        patch_bank = [patch for patch in patch_bank if patch["patch_id"] in wanted]
    rows = heldout_rows(args.source, limit=args.holdout_rows, start_offset=args.start_offset)
    results_path = args.out_dir / "patch_bank_benchmark.rows.jsonl"
    existing = [] if args.force else load_jsonl(results_path)
    completed = {(row.get("row_id"), row.get("patch_id") or row.get("arm")) for row in existing}
    evaluated = list(existing)

    for row in rows:
        for patch in patch_bank:
            key = (row["row_id"], patch["patch_id"])
            if key in completed:
                continue
            result = run_patch(args, row, patch)
            evaluated.append(result)
            append_jsonl(results_path, result)
            completed.add(key)
            if args.sleep_sec > 0:
                time.sleep(args.sleep_sec)

    summary = summarize(evaluated, patch_bank)
    payload = {
        "generated_at_utc": utc_now(),
        "source": str(args.source),
        "patch_bank": str(args.patch_bank),
        "base_url": args.base_url,
        "holdout_rows": len(rows),
        "start_offset": args.start_offset,
        "completed_calls": len(evaluated),
        "patch_count": len(patch_bank),
        "summary": summary,
    }
    (args.out_dir / "patch_bank_benchmark.results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")
    (args.out_dir / "patch_bank_benchmark.results.md").write_text(render_md(payload), encoding="utf-8", newline="\n")
    (args.out_dir / "patch_bank_benchmark_contract.metta").write_text(render_metta(payload), encoding="utf-8", newline="\n")
    with (args.out_dir / "patch_bank_commit_trm_rows.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in trm_rows(evaluated, summary):
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    print(args.out_dir / "patch_bank_benchmark.results.md")
    print(json.dumps(summary["arms"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
