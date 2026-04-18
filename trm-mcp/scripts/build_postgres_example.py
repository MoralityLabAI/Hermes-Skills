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
            "trace_id": "pg_users_schema_exact",
            "mcp_name": "postgres",
            "query": "Open the schema for public.users in the app database.",
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_read",
            "expected_resource_uri": "mcp://postgres/db/app/schema/public.tables/users",
            "chosen_resource_uri": "mcp://postgres/db/app/schema/public.tables/users",
            "candidate_resources": [
                "mcp://postgres/db/app/schema/public.tables/users",
                "mcp://postgres/db/app/schema/public.tables/user_sessions",
            ],
            "answer_shape": "resource_payload",
            "useful_hit": True,
            "success": True,
            "exact_hit": True,
            "resource_match": True,
            "verifier_decision": "accept",
            "result_summary": "Loaded schema for public.users.",
        },
        {
            "trace_id": "pg_orders_view_exact",
            "mcp_name": "postgres",
            "query": "Read the analytics.monthly_orders view definition.",
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_read",
            "expected_resource_uri": "mcp://postgres/db/app/schema/analytics.views/monthly_orders",
            "chosen_resource_uri": "mcp://postgres/db/app/schema/analytics.views/monthly_orders",
            "candidate_resources": [
                "mcp://postgres/db/app/schema/analytics.views/monthly_orders",
                "mcp://postgres/db/app/schema/analytics.views/daily_orders",
            ],
            "answer_shape": "resource_payload",
            "useful_hit": True,
            "success": True,
            "exact_hit": True,
            "resource_match": True,
            "verifier_decision": "accept",
            "result_summary": "Loaded view definition for analytics.monthly_orders.",
        },
        {
            "trace_id": "pg_top_customers_template_exact",
            "mcp_name": "postgres",
            "query": "Find the top customers by revenue in the last 30 days.",
            "expected_route_family": "resource_template_list",
            "chosen_route_family": "resource_template_list",
            "expected_resource_uri": "mcp://postgres/templates/top_customers_last_30d",
            "template_uri": "mcp://postgres/templates/top_customers_last_30d",
            "chosen_resource_uri": "mcp://postgres/templates/top_customers_last_30d",
            "candidate_resources": [
                "mcp://postgres/templates/top_customers_last_30d",
                "mcp://postgres/templates/top_products_last_30d",
            ],
            "answer_shape": "resource_template_list",
            "useful_hit": True,
            "success": True,
            "exact_hit": True,
            "resource_match": True,
            "verifier_decision": "accept",
            "result_summary": "Matched reusable revenue-ranking query template.",
        },
        {
            "trace_id": "pg_users_near_miss",
            "mcp_name": "postgres",
            "query": "Open the schema for public.users in the app database.",
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_read",
            "expected_resource_uri": "mcp://postgres/db/app/schema/public.tables/users",
            "chosen_resource_uri": "mcp://postgres/db/app/schema/public.tables/user_sessions",
            "candidate_resources": [
                "mcp://postgres/db/app/schema/public.tables/user_sessions",
                "mcp://postgres/db/app/schema/public.tables/users",
            ],
            "answer_shape": "resource_payload",
            "useful_hit": False,
            "success": False,
            "exact_hit": False,
            "resource_match": False,
            "verifier_decision": "reject",
            "result_summary": "Picked public.user_sessions instead of public.users.",
        },
        {
            "trace_id": "pg_wrong_route_schema",
            "mcp_name": "postgres",
            "query": "Open the schema for analytics.monthly_orders.",
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_list",
            "candidate_resources": [
                "mcp://postgres/db/app/schema/analytics.views",
                "mcp://postgres/db/app/schema/public.tables",
            ],
            "answer_shape": "resource_payload",
            "useful_hit": False,
            "success": False,
            "exact_hit": False,
            "resource_match": False,
            "verifier_decision": "reject",
            "result_summary": "Listed schema groups broadly instead of reading the exact analytics.monthly_orders handle.",
        },
    ]


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Build a popular postgres MCP example pack.")
    parser.add_argument(
        "--out-dir",
        default=str(repo_root / "data" / "trm_mcp_postgres_example"),
        help="Output directory for example traces, rows, and summaries.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    traces = build_example_traces()

    traces_path = out_dir / "postgres_mcp_traces.jsonl"
    traces_summary_path = out_dir / "postgres_mcp_traces.summary.json"
    write_jsonl(traces_path, traces)
    write_json(
        traces_summary_path,
        {
            "trace_count": len(traces),
            "mcp_name": "postgres",
            "scenario_ids": [str(trace["trace_id"]) for trace in traces],
            "notes": "Popular worked example for TRM-MCP around postgres schema reads, view reads, query-template retrieval, near-miss retrieval, and wrong-route failure.",
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
            "postgres",
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
