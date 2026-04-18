from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def build_example_traces() -> List[Dict[str, Any]]:
    return [
        {
            "trace_id": "fs_readme_exact",
            "mcp_name": "filesystem",
            "query": "Open the root README and show the setup steps.",
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_read",
            "expected_resource_uri": "file:///workspace/README.md",
            "chosen_resource_uri": "file:///workspace/README.md",
            "candidate_resources": [
                "file:///workspace/README.md",
                "file:///workspace/README.old.md",
                "file:///workspace/docs/setup.md",
            ],
            "answer_shape": "resource_payload",
            "useful_hit": True,
            "success": True,
            "exact_hit": True,
            "resource_match": True,
            "verifier_decision": "accept",
            "result_summary": "Loaded README.md with setup section.",
        },
        {
            "trace_id": "fs_package_json_exact",
            "mcp_name": "filesystem",
            "query": "Read the app package.json in the workspace root.",
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_read",
            "expected_resource_uri": "file:///workspace/package.json",
            "chosen_resource_uri": "file:///workspace/package.json",
            "candidate_resources": [
                "file:///workspace/package.json",
                "file:///workspace/packages/ui/package.json",
            ],
            "answer_shape": "resource_payload",
            "useful_hit": True,
            "success": True,
            "exact_hit": True,
            "resource_match": True,
            "verifier_decision": "accept",
            "result_summary": "Loaded root package.json.",
        },
        {
            "trace_id": "fs_glob_template_exact",
            "mcp_name": "filesystem",
            "query": "Find all test files matching *.spec.ts under the repo.",
            "expected_route_family": "resource_template_list",
            "chosen_route_family": "resource_template_list",
            "expected_resource_uri": "mcp://filesystem/templates/glob?pattern=**/*.spec.ts",
            "template_uri": "mcp://filesystem/templates/glob?pattern=**/*.spec.ts",
            "chosen_resource_uri": "mcp://filesystem/templates/glob?pattern=**/*.spec.ts",
            "candidate_resources": [
                "mcp://filesystem/templates/glob?pattern=**/*.spec.ts",
                "mcp://filesystem/templates/glob?pattern=**/*.test.ts",
            ],
            "answer_shape": "resource_template_list",
            "useful_hit": True,
            "success": True,
            "exact_hit": True,
            "resource_match": True,
            "verifier_decision": "accept",
            "result_summary": "Matched 14 spec files.",
        },
        {
            "trace_id": "fs_readme_near_miss",
            "mcp_name": "filesystem",
            "query": "Open README.md for current setup instructions.",
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_read",
            "expected_resource_uri": "file:///workspace/README.md",
            "chosen_resource_uri": "file:///workspace/README.old.md",
            "candidate_resources": [
                "file:///workspace/README.old.md",
                "file:///workspace/README.md",
            ],
            "answer_shape": "resource_payload",
            "useful_hit": False,
            "success": False,
            "exact_hit": False,
            "resource_match": False,
            "verifier_decision": "reject",
            "result_summary": "Picked stale README.old.md instead of current README.md.",
        },
        {
            "trace_id": "fs_wrong_route_missing",
            "mcp_name": "filesystem",
            "query": "Open CONTRIBUTING.md in the repo root.",
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_list",
            "candidate_resources": [
                "file:///workspace/README.md",
                "file:///workspace/docs/contributing-notes.md",
            ],
            "answer_shape": "resource_payload",
            "useful_hit": False,
            "success": False,
            "exact_hit": False,
            "resource_match": False,
            "verifier_decision": "reject",
            "result_summary": "Listed broad repo files but never opened CONTRIBUTING.md.",
        },
    ]


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Build a popular filesystem MCP example pack.")
    parser.add_argument(
        "--out-dir",
        default=str(repo_root / "data" / "trm_mcp_filesystem_example"),
        help="Output directory for example traces, rows, and summaries.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    traces = build_example_traces()

    traces_path = out_dir / "filesystem_mcp_traces.jsonl"
    traces_summary_path = out_dir / "filesystem_mcp_traces.summary.json"
    write_jsonl(traces_path, traces)
    write_json(
        traces_summary_path,
        {
            "trace_count": len(traces),
            "mcp_name": "filesystem",
            "scenario_ids": [trace["trace_id"] for trace in traces],
            "notes": "Popular worked example for TRM-MCP around direct reads, template search, near-miss retrieval, and wrong-route failure.",
        },
    )

    row_builder = Path(__file__).resolve().with_name("build_mcp_trm_rows.py")
    subprocess.run(
        [
            sys.executable,
            str(row_builder),
            "--input",
            str(traces_path),
            "--out-dir",
            str(out_dir / "rows"),
            "--mcp-name",
            "filesystem",
        ],
        check=True,
    )

    print(str(traces_path))
    print(str(traces_summary_path))
    print(str(out_dir / "rows" / "mcp_trm_rows.jsonl"))
    print(str(out_dir / "rows" / "mcp_trm_rows.summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
