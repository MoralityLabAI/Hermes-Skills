from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List


def write_jsonl(path: Path, rows: Iterable[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def build_example_traces() -> List[Dict[str, object]]:
    return [
        {
            "trace_id": "gh_issue_exact",
            "mcp_name": "github",
            "query": "Open issue #142 about the benchmark freeze in acme/engine.",
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_read",
            "expected_resource_uri": "mcp://github/repos/acme/engine/issues/142",
            "chosen_resource_uri": "mcp://github/repos/acme/engine/issues/142",
            "candidate_resources": [
                "mcp://github/repos/acme/engine/issues/142",
                "mcp://github/repos/acme/engine/issues/124",
            ],
            "answer_shape": "resource_payload",
            "useful_hit": True,
            "success": True,
            "exact_hit": True,
            "resource_match": True,
            "verifier_decision": "accept",
            "result_summary": "Loaded issue #142 in acme/engine.",
        },
        {
            "trace_id": "gh_pr_exact",
            "mcp_name": "github",
            "query": "Read pull request #88 in acme/engine and summarize the benchmark note.",
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_read",
            "expected_resource_uri": "mcp://github/repos/acme/engine/pulls/88",
            "chosen_resource_uri": "mcp://github/repos/acme/engine/pulls/88",
            "candidate_resources": [
                "mcp://github/repos/acme/engine/pulls/88",
                "mcp://github/repos/acme/engine/pulls/89",
            ],
            "answer_shape": "resource_payload",
            "useful_hit": True,
            "success": True,
            "exact_hit": True,
            "resource_match": True,
            "verifier_decision": "accept",
            "result_summary": "Loaded pull request #88.",
        },
        {
            "trace_id": "gh_pr_search_template_exact",
            "mcp_name": "github",
            "query": "Find PRs in acme/engine mentioning benchmark regressions.",
            "expected_route_family": "resource_template_list",
            "chosen_route_family": "resource_template_list",
            "expected_resource_uri": "mcp://github/templates/search_pull_requests?q=repo:acme/engine+benchmark+regression",
            "template_uri": "mcp://github/templates/search_pull_requests?q=repo:acme/engine+benchmark+regression",
            "chosen_resource_uri": "mcp://github/templates/search_pull_requests?q=repo:acme/engine+benchmark+regression",
            "candidate_resources": [
                "mcp://github/templates/search_pull_requests?q=repo:acme/engine+benchmark+regression",
                "mcp://github/templates/search_issues?q=repo:acme/engine+benchmark+regression",
            ],
            "answer_shape": "resource_template_list",
            "useful_hit": True,
            "success": True,
            "exact_hit": True,
            "resource_match": True,
            "verifier_decision": "accept",
            "result_summary": "Matched 6 pull requests mentioning benchmark regressions.",
        },
        {
            "trace_id": "gh_issue_near_miss",
            "mcp_name": "github",
            "query": "Open issue #142 about the benchmark freeze in acme/engine.",
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_read",
            "expected_resource_uri": "mcp://github/repos/acme/engine/issues/142",
            "chosen_resource_uri": "mcp://github/repos/acme/engine/issues/124",
            "candidate_resources": [
                "mcp://github/repos/acme/engine/issues/124",
                "mcp://github/repos/acme/engine/issues/142",
            ],
            "answer_shape": "resource_payload",
            "useful_hit": False,
            "success": False,
            "exact_hit": False,
            "resource_match": False,
            "verifier_decision": "reject",
            "result_summary": "Picked issue #124 instead of issue #142.",
        },
        {
            "trace_id": "gh_wrong_route_exact_pr",
            "mcp_name": "github",
            "query": "Open pull request #88 in acme/engine.",
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_template_list",
            "candidate_resources": [
                "mcp://github/templates/search_pull_requests?q=repo:acme/engine+88",
                "mcp://github/repos/acme/engine/pulls/89",
            ],
            "answer_shape": "resource_payload",
            "useful_hit": False,
            "success": False,
            "exact_hit": False,
            "resource_match": False,
            "verifier_decision": "reject",
            "result_summary": "Used broad PR search instead of direct PR handle and did not resolve PR #88.",
        },
    ]


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Build a popular github MCP example pack.")
    parser.add_argument(
        "--out-dir",
        default=str(repo_root / "data" / "trm_mcp_github_example"),
        help="Output directory for example traces, rows, and summaries.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    traces = build_example_traces()

    traces_path = out_dir / "github_mcp_traces.jsonl"
    traces_summary_path = out_dir / "github_mcp_traces.summary.json"
    write_jsonl(traces_path, traces)
    write_json(
        traces_summary_path,
        {
            "trace_count": len(traces),
            "mcp_name": "github",
            "scenario_ids": [str(trace["trace_id"]) for trace in traces],
            "notes": "Popular worked example for TRM-MCP around github issue reads, PR reads, search templates, near-miss retrieval, and wrong-route failure.",
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
            "github",
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
