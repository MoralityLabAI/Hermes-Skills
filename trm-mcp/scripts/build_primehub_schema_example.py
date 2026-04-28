from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


DEFAULT_SAMPLE_ROOTS = [
    Path(r"C:/projects/Hermes-Skills/Hermes Skills/data/primehub_eligible_benchmark_v2_47env"),
    Path(r"C:/projects/Hermes-Skills/Hermes Skills/data/primehub_eligible_benchmark_v1_retry_27b_tail"),
    Path(r"C:/projects/Hermes-Skills/Hermes Skills/data/primehub_eligible_benchmark_v1"),
]

ENV_SPECS: Dict[str, Dict[str, object]] = {
    "psycho_bench": {
        "task_alias": "instrument:BFI",
        "answer_shape": "indexed_mapping_lines",
        "resource_uri": "mcp://primehub_schema/env/psycho_bench",
        "template_uri": "mcp://primehub_schema/templates/minimal_example?env=psycho_bench",
        "summary": "Exact plain-text lines in the form `index: score`, integer scores only, and no wrapper prose.",
        "example_status": "validated_minimal_example",
        "query_cues": [
            "reply numbers from 1 to 5",
            "index: score",
            "BFI subscale",
            "plain text lines only",
        ],
        "minimal_example": "31: 2\n39: 3",
        "failure_modes": [
            "refusal text instead of numbered lines",
            "extra commentary around scores",
            "non-integer values or out-of-range scores",
        ],
    },
    "ascii_tree": {
        "task_alias": "ascii-tree",
        "answer_shape": "ascii_formatted_tree",
        "resource_uri": "mcp://primehub_schema/env/ascii_tree",
        "template_uri": "mcp://primehub_schema/templates/minimal_example?env=ascii_tree",
        "summary": "Exact ASCII tree structure wrapped in <ascii_formatted> tags with no surrounding prose.",
        "example_status": "validated_minimal_example",
        "query_cues": [
            "ASCII tree",
            "<ascii_formatted>",
            "directory hierarchy",
            "plain ASCII structure",
        ],
        "minimal_example": "<ascii_formatted>\nmain\n `--child\n</ascii_formatted>",
        "failure_modes": [
            "missing wrapper tags",
            "extra prose before or after the tree",
            "wrong branch glyphs or unstable indentation",
        ],
    },
    "pydantic_adherence": {
        "task_alias": "pydantic-adherence",
        "answer_shape": "strict_json_object",
        "resource_uri": "mcp://primehub_schema/env/pydantic_adherence",
        "template_uri": "mcp://primehub_schema/templates/minimal_example?env=pydantic_adherence",
        "summary": "Return one JSON object compatible with the provided pydantic model and nothing else. The live community verifier extracts the last JSON object and validates it with JSON-native semantics via `model_validate_json(..., strict=False)`.",
        "example_status": "validated_minimal_example",
        "validation_path": "extract_last_json -> json.dumps(parsed_dict) -> model.model_validate_json(serialized_payload, strict=False)",
        "query_cues": [
            "Return the json and nothing else",
            "pydantic model",
            "compatible with the model",
            "strict JSON only",
        ],
        "validator_notes": [
            "period genres must be unique",
            "reference genre cannot exceed 7 days",
            "fine_policy.max_total must be >= fine_policy.per_day",
            "renewal_policy.cooldown accepts integer day counts or numeric strings before timedelta coercion",
            "the live scorer now validates JSON-native payloads with model_validate_json(..., strict=False)",
        ],
        "minimal_example": '{"policy_id":"11111111-1111-1111-1111-111111111111","name":"Main","max_books":3,"periods":[],"fine_policy":{"per_day":1.0,"max_total":5.0},"renewal_policy":{"max_renewals":1,"cooldown":"1"},"exceptions":{},"created_at":"2026-01-01T00:00:00"}',
        "failure_modes": [
            "empty output or fallback action",
            "markdown fences around JSON",
            "schema-violating field types or missing required keys",
            "natural-language cooldown values such as `14 days` instead of integer day counts",
        ],
        "known_verifier_gaps": [
            "historical note: before 2026-04-22, the live scorer validated the parsed Python dict directly and made UUID/datetime fields unsatisfiable from plain JSON",
        ],
    },
}


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def first_jsonl_row(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                return json.loads(line)
    raise ValueError(f"No JSONL rows found in {path}")


def find_sample_replay(env_name: str, sample_roots: List[Path]) -> Path | None:
    pattern = f"*{env_name}*.jsonl"
    for root in sample_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob(pattern)):
            if not path.parent.name.startswith("qwen35_"):
                continue
            return path.resolve()
    return None


def observation_excerpt(text: str, *, max_lines: int = 10, max_chars: int = 600) -> str:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    excerpt = "\n".join(lines[:max_lines]).strip()
    if len(excerpt) > max_chars:
        excerpt = excerpt[: max_chars - 3].rstrip() + "..."
    return excerpt


def build_surface_resources(sample_replays: Dict[str, Path | None]) -> List[Dict[str, Any]]:
    resources: List[Dict[str, Any]] = []
    for env_name, spec in ENV_SPECS.items():
        sample_path = sample_replays.get(env_name)
        sample_row: Dict[str, Any] = {}
        if sample_path is not None:
            sample_row = first_jsonl_row(sample_path)
        example_status = str(spec.get("example_status") or "validated_minimal_example")
        template_summary = f"Minimal valid example for {env_name}."
        template_failure_modes = ["example uses the wrong env schema"]
        if example_status != "validated_minimal_example":
            template_summary = f"Best-effort shape example for {env_name}; use it for field-shape cues only."
            template_failure_modes.append("example is shape-only and is not guaranteed to satisfy the live validator")

        resources.append(
            {
                "uri": spec["resource_uri"],
                "family": "resource_read",
                "label": env_name,
                "answer_shape": spec["answer_shape"],
                "summary": spec["summary"],
                "example_status": example_status,
                "query_cues": spec["query_cues"],
                "minimal_example": spec["minimal_example"],
                "failure_modes": spec["failure_modes"],
                "validator_notes": spec.get("validator_notes") or [],
                "known_verifier_gaps": spec.get("known_verifier_gaps") or [],
                "validation_path": spec.get("validation_path") or "",
                "source_task": sample_row.get("task") or spec["task_alias"],
                "source_replay_path": str(sample_path) if sample_path else "",
                "observation_excerpt": observation_excerpt(str(sample_row.get("observation") or "")),
            }
        )
        resources.append(
            {
                "uri": spec["template_uri"],
                "family": "resource_template_list",
                "label": f"{env_name}_minimal_example",
                "answer_shape": "resource_template_list",
                "summary": template_summary,
                "example_status": example_status,
                "query_cues": [f"minimal example for {env_name}", f"valid sample output for {env_name}"],
                "minimal_example": spec["minimal_example"],
                "failure_modes": template_failure_modes,
                "validator_notes": spec.get("validator_notes") or [],
                "known_verifier_gaps": spec.get("known_verifier_gaps") or [],
                "validation_path": spec.get("validation_path") or "",
                "source_task": sample_row.get("task") or spec["task_alias"],
                "source_replay_path": str(sample_path) if sample_path else "",
                "observation_excerpt": observation_excerpt(str(sample_row.get("observation") or "")),
            }
        )
    return resources


def build_example_traces() -> List[Dict[str, Any]]:
    psycho = ENV_SPECS["psycho_bench"]
    ascii_tree = ENV_SPECS["ascii_tree"]
    pydantic = ENV_SPECS["pydantic_adherence"]
    return [
        {
            "trace_id": "primehub_psycho_schema_exact",
            "mcp_name": "primehub_schema",
            "query": "Open the schema rules for psycho_bench so I only emit valid `index: score` lines.",
            "available_families": ["resource_read", "resource_template_list"],
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_read",
            "expected_resource_uri": psycho["resource_uri"],
            "chosen_resource_uri": psycho["resource_uri"],
            "candidate_resources": [
                psycho["resource_uri"],
                ascii_tree["resource_uri"],
                pydantic["resource_uri"],
            ],
            "answer_shape": psycho["answer_shape"],
            "useful_hit": True,
            "success": True,
            "exact_hit": True,
            "resource_match": True,
            "verifier_decision": "accept",
            "result_summary": "Loaded psycho_bench schema with exact `index: score` format and integer range [1, 5].",
        },
        {
            "trace_id": "primehub_ascii_schema_exact",
            "mcp_name": "primehub_schema",
            "query": "Open the schema rules for ascii_tree including wrapper tags and indentation.",
            "available_families": ["resource_read", "resource_template_list"],
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_read",
            "expected_resource_uri": ascii_tree["resource_uri"],
            "chosen_resource_uri": ascii_tree["resource_uri"],
            "candidate_resources": [
                ascii_tree["resource_uri"],
                psycho["resource_uri"],
                pydantic["resource_uri"],
            ],
            "answer_shape": ascii_tree["answer_shape"],
            "useful_hit": True,
            "success": True,
            "exact_hit": True,
            "resource_match": True,
            "verifier_decision": "accept",
            "result_summary": "Loaded ascii_tree schema with <ascii_formatted> wrapper and ASCII branch rules.",
        },
        {
            "trace_id": "primehub_pydantic_schema_exact",
            "mcp_name": "primehub_schema",
            "query": "Open the schema notes for pydantic_adherence so I return one valid JSON object and nothing else.",
            "available_families": ["resource_read", "resource_template_list"],
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_read",
            "expected_resource_uri": pydantic["resource_uri"],
            "chosen_resource_uri": pydantic["resource_uri"],
            "candidate_resources": [
                pydantic["resource_uri"],
                ascii_tree["resource_uri"],
                psycho["resource_uri"],
            ],
            "answer_shape": pydantic["answer_shape"],
            "useful_hit": True,
            "success": True,
            "exact_hit": True,
            "resource_match": True,
            "verifier_decision": "accept",
            "result_summary": "Loaded strict JSON-only schema notes plus the live JSON-native `model_validate_json(..., strict=False)` verifier path for pydantic_adherence.",
        },
        {
            "trace_id": "primehub_psycho_template_exact",
            "mcp_name": "primehub_schema",
            "query": "Fetch a minimal valid example for psycho_bench output formatting.",
            "available_families": ["resource_read", "resource_template_list"],
            "expected_route_family": "resource_template_list",
            "chosen_route_family": "resource_template_list",
            "expected_resource_uri": psycho["template_uri"],
            "template_uri": psycho["template_uri"],
            "chosen_resource_uri": psycho["template_uri"],
            "candidate_resources": [
                psycho["template_uri"],
                ascii_tree["template_uri"],
                pydantic["template_uri"],
            ],
            "answer_shape": "resource_template_list",
            "useful_hit": True,
            "success": True,
            "exact_hit": True,
            "resource_match": True,
            "verifier_decision": "accept",
            "result_summary": "Loaded minimal psycho_bench example with numbered score lines.",
        },
        {
            "trace_id": "primehub_ascii_near_miss",
            "mcp_name": "primehub_schema",
            "query": "Open the output schema for ascii_tree directory rendering.",
            "available_families": ["resource_read", "resource_template_list"],
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_read",
            "expected_resource_uri": ascii_tree["resource_uri"],
            "chosen_resource_uri": psycho["resource_uri"],
            "candidate_resources": [
                psycho["resource_uri"],
                ascii_tree["resource_uri"],
                pydantic["resource_uri"],
            ],
            "answer_shape": ascii_tree["answer_shape"],
            "useful_hit": False,
            "success": False,
            "exact_hit": False,
            "resource_match": False,
            "verifier_decision": "reject",
            "result_summary": "Picked psycho_bench score-line schema instead of the ASCII tree wrapper rules.",
        },
        {
            "trace_id": "primehub_pydantic_wrong_route",
            "mcp_name": "primehub_schema",
            "query": "Open the strict JSON schema notes for pydantic_adherence.",
            "available_families": ["resource_read", "resource_template_list"],
            "expected_route_family": "resource_read",
            "chosen_route_family": "resource_template_list",
            "expected_resource_uri": pydantic["resource_uri"],
            "template_uri": ascii_tree["template_uri"],
            "chosen_resource_uri": ascii_tree["template_uri"],
            "candidate_resources": [
                ascii_tree["template_uri"],
                pydantic["resource_uri"],
                pydantic["template_uri"],
            ],
            "answer_shape": pydantic["answer_shape"],
            "useful_hit": False,
            "success": False,
            "exact_hit": False,
            "resource_match": False,
            "verifier_decision": "reject",
            "result_summary": "Used an example-template path instead of opening the strict JSON schema resource.",
        },
    ]


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Build a Primehub schema MCP example pack.")
    parser.add_argument(
        "--out-dir",
        default=str(repo_root / "data" / "trm_mcp_primehub_schema_example"),
        help="Output directory for schema surface, traces, rows, and summaries.",
    )
    parser.add_argument(
        "--sample-root",
        action="append",
        dest="sample_roots",
        default=[],
        help="Optional replay root to search for env samples. Repeat to include multiple roots.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    sample_roots = [Path(item).resolve() for item in (args.sample_roots or [str(path) for path in DEFAULT_SAMPLE_ROOTS])]

    sample_replays = {env_name: find_sample_replay(env_name, sample_roots) for env_name in ENV_SPECS}
    resources = build_surface_resources(sample_replays)
    traces = build_example_traces()

    surface_path = out_dir / "primehub_schema_surface.json"
    resources_path = out_dir / "primehub_schema_resources.jsonl"
    traces_path = out_dir / "primehub_schema_mcp_traces.jsonl"
    traces_summary_path = out_dir / "primehub_schema_mcp_traces.summary.json"

    write_json(
        surface_path,
        {
            "mcp_name": "primehub_schema",
            "resource_count": len(resources),
            "envs": list(ENV_SPECS.keys()),
            "resources": resources,
        },
    )
    write_jsonl(resources_path, resources)
    write_jsonl(traces_path, traces)
    write_json(
        traces_summary_path,
        {
            "trace_count": len(traces),
            "mcp_name": "primehub_schema",
            "scenario_ids": [trace["trace_id"] for trace in traces],
            "sample_replays": {env_name: str(path) if path else "" for env_name, path in sample_replays.items()},
            "notes": "Primehub-specific schema lookup example for structured-map retrieval over psycho_bench, ascii_tree, and pydantic_adherence.",
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
            "primehub_schema",
        ],
        check=True,
    )

    print(str(surface_path))
    print(str(resources_path))
    print(str(traces_path))
    print(str(traces_summary_path))
    print(str(out_dir / "rows" / "mcp_trm_rows.jsonl"))
    print(str(out_dir / "rows" / "mcp_trm_rows.summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
