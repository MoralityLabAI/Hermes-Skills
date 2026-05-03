"""Aggregate Intellect-3-Math patch-bank benchmark shards."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "research" / "scripts"
RUNNER = SCRIPTS / "run_intellect3_math_patch_bank_benchmark.py"
ARTIFACTS = ROOT / "research" / "studies" / "2026-04-22-metta-trm-hermes-pipeline" / "artifacts"
DEFAULT_OUT = ARTIFACTS / "intellect3_math_patch_bank_benchmark_27b_20260502_combined20"


def load_runner():
    spec = importlib.util.spec_from_file_location("patch_bank_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUN = load_runner()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate patch-bank benchmark shards.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), type=Path)
    parser.add_argument("shards", nargs="+", type=Path)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def patch_order(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ids = []
    for row in rows:
        patch_id = str(row.get("patch_id") or row.get("arm"))
        if patch_id not in ids:
            ids.append(patch_id)
    return [{"patch_id": patch_id} for patch_id in ids]


def aggregate_rows(shards: list[Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    shard_summaries: list[dict[str, Any]] = []
    for shard in shards:
        rows_path = shard / "patch_bank_benchmark.rows.jsonl"
        results_path = shard / "patch_bank_benchmark.results.json"
        shard_rows = load_jsonl(rows_path)
        rows.extend(shard_rows)
        summary = load_json(results_path) if results_path.exists() else {}
        shard_summaries.append(
            {
                "path": str(shard),
                "rows": len({row.get("row_id") for row in shard_rows}),
                "calls": len(shard_rows),
                "summary": summary.get("summary", {}),
            }
        )
    return rows, shard_summaries


def per_patch_rows(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        out[str(row.get("patch_id") or row.get("arm"))].append(row)
    return out


def row_level_winners(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_row: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_row[str(row.get("row_id"))].append(row)
    wins = Counter()
    exact_rows = Counter()
    for row_id, row_group in by_row.items():
        exact_patches = [str(row.get("patch_id") or row.get("arm")) for row in row_group if row.get("exact")]
        if exact_patches:
            for patch_id in exact_patches:
                exact_rows[patch_id] += 1
            if len(exact_patches) == 1:
                wins[exact_patches[0]] += 1
            else:
                wins["multi_patch_exact"] += 1
        else:
            wins["no_patch_exact"] += 1
    return {
        "row_count": len(by_row),
        "exclusive_wins": dict(wins),
        "exact_rows_by_patch": dict(exact_rows),
    }


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Combined Intellect-3-Math Patch-Bank Benchmark",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        f"Unique rows: `{payload['unique_rows']}`",
        f"Calls: `{payload['calls']}`",
        "",
        "## Aggregate Patch Scores",
        "",
        "| Patch | Rows | Exact | Exact Rate | Errors | Gate |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    gates = payload["summary"].get("adoption_gates") or {}
    for patch_id, metrics in payload["summary"]["arms"].items():
        gate = gates.get(patch_id, {}).get("decision", "incumbent")
        lines.append(
            f"| `{patch_id}` | {metrics['rows']} | {metrics['exact']} | {metrics['exact_rate']:.4f} | "
            f"{metrics['errors']} | `{gate}` |"
        )
    lines.extend(
        [
            "",
            "## Row-Level Winners",
            "",
            json.dumps(payload["row_level_winners"], indent=2),
            "",
            "## Read",
            "",
            payload["summary"]["read"],
            "",
            f"Best raw exact patch: `{payload['summary']['best_patch_by_exact']}`.",
            "No candidate patch clears the adoption gate on the combined 20-row smoke.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows, shard_summaries = aggregate_rows(args.shards)
    patches = patch_order(rows)
    summary = RUN.summarize(rows, patches)
    payload = {
        "generated_at_utc": utc_now(),
        "shards": shard_summaries,
        "unique_rows": len({row.get("row_id") for row in rows}),
        "calls": len(rows),
        "summary": summary,
        "row_level_winners": row_level_winners(rows),
    }
    (args.out_dir / "combined_patch_bank_benchmark.results.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8", newline="\n"
    )
    (args.out_dir / "combined_patch_bank_benchmark.results.md").write_text(
        render_md(payload), encoding="utf-8", newline="\n"
    )
    (args.out_dir / "combined_patch_bank_benchmark_contract.metta").write_text(
        RUN.render_metta({"summary": summary}), encoding="utf-8", newline="\n"
    )
    with (args.out_dir / "combined_patch_bank_commit_trm_rows.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in RUN.trm_rows(rows, summary):
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    print(args.out_dir / "combined_patch_bank_benchmark.results.md")
    print(json.dumps(summary["arms"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
