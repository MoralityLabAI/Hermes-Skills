from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List


EXAMPLE_BUILDERS = {
    "filesystem": "build_filesystem_example.py",
    "github": "build_github_example.py",
    "postgres": "build_postgres_example.py",
}


def load_jsonl(path: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Build the bundled TRM-MCP example matrix and merged corpus.")
    parser.add_argument(
        "--out-dir",
        default=str(repo_root / "data" / "trm_mcp_example_matrix"),
        help="Output directory for per-pack outputs and merged corpus.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    script_dir = Path(__file__).resolve().parent

    merged_rows: List[Dict[str, object]] = []
    merged_traces: List[Dict[str, object]] = []
    pack_summaries: Dict[str, object] = {}
    bucket_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    mcp_counts: Counter[str] = Counter()

    for pack_name, script_name in EXAMPLE_BUILDERS.items():
        pack_out_dir = out_dir / pack_name
        subprocess.run(
            [sys.executable, str(script_dir / script_name), "--out-dir", str(pack_out_dir)],
            check=True,
        )

        if pack_name == "filesystem":
            traces_path = pack_out_dir / "filesystem_mcp_traces.jsonl"
        elif pack_name == "github":
            traces_path = pack_out_dir / "github_mcp_traces.jsonl"
        else:
            traces_path = pack_out_dir / "postgres_mcp_traces.jsonl"
        rows_path = pack_out_dir / "rows" / "mcp_trm_rows.jsonl"
        summary_path = pack_out_dir / "rows" / "mcp_trm_rows.summary.json"

        traces = load_jsonl(traces_path)
        rows = load_jsonl(rows_path)
        summary = json.loads(summary_path.read_text(encoding="utf-8"))

        merged_traces.extend(traces)
        merged_rows.extend(rows)
        pack_summaries[pack_name] = summary

        for row in rows:
            bucket_counts[str(row.get("bucket", ""))] += 1
            family_counts[str(row.get("task_family", ""))] += 1
            mcp_counts[str(row.get("source_env_name", ""))] += 1

    merged_traces_path = out_dir / "merged" / "trm_mcp_example_traces.jsonl"
    merged_rows_path = out_dir / "merged" / "trm_mcp_example_rows.jsonl"
    manifest_path = out_dir / "merged" / "trm_mcp_example_matrix.manifest.json"

    write_jsonl(merged_traces_path, merged_traces)
    write_jsonl(merged_rows_path, merged_rows)
    write_json(
        manifest_path,
        {
            "packs": list(EXAMPLE_BUILDERS.keys()),
            "pack_summaries": pack_summaries,
            "trace_count": len(merged_traces),
            "row_count": len(merged_rows),
            "bucket_counts": dict(bucket_counts),
            "task_family_counts": dict(family_counts),
            "mcp_counts": dict(mcp_counts),
            "merged_traces_path": str(merged_traces_path),
            "merged_rows_path": str(merged_rows_path),
        },
    )

    print(str(merged_traces_path))
    print(str(merged_rows_path))
    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
