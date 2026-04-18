from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def first_present(row: Dict[str, Any], keys: List[str]) -> Any:
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return None


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    return None


def compact_list(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        parts: List[str] = []
        for item in value[:12]:
            if isinstance(item, dict):
                label = normalize_text(
                    first_present(
                        item,
                        [
                            "uri",
                            "resource_uri",
                            "template_uri",
                            "name",
                            "id",
                            "label",
                        ],
                    )
                )
                if label:
                    parts.append(label)
            else:
                text = normalize_text(item)
                if text:
                    parts.append(text)
        return ", ".join(parts)
    return normalize_text(value)


def trace_identity(trace: Dict[str, Any], index: int) -> str:
    for key in ["trace_id", "id", "episode_id", "request_id", "row_id"]:
        value = normalize_text(trace.get(key))
        if value:
            return value
    return f"trace_{index:06d}"


def inferred_lookup_success(trace: Dict[str, Any]) -> bool:
    for key in [
        "exact_hit",
        "useful_hit",
        "solved",
        "success",
        "verified_relevant",
        "resource_match",
    ]:
        normalized = normalize_bool(trace.get(key))
        if normalized is not None:
            return normalized
    reward = trace.get("reward")
    if isinstance(reward, (int, float)) and reward > 0:
        return True
    return False


def supervision_weight(bucket: str) -> float:
    if bucket == "exact_positive":
        return 2.5
    if bucket == "weak_positive":
        return 1.25
    return 0.2


def build_route_observation(trace: Dict[str, Any], query: str) -> str:
    available_families = compact_list(
        first_present(trace, ["available_families", "resource_families", "candidate_families"])
    )
    parts = [
        f"QUERY:\n{query}",
    ]
    if available_families:
        parts.append(f"AVAILABLE_FAMILIES:\n{available_families}")
    hint = normalize_text(first_present(trace, ["answer_shape", "expected_answer_shape", "output_contract"]))
    if hint:
        parts.append(f"EXPECTED_ANSWER_SHAPE:\n{hint}")
    return "\n\n".join(parts)


def build_retrieve_observation(trace: Dict[str, Any], query: str) -> str:
    route_family = normalize_text(
        first_present(trace, ["expected_route_family", "route_family", "chosen_route_family", "resource_family"])
    )
    candidate_resources = compact_list(
        first_present(trace, ["candidate_resources", "resource_candidates", "resource_descriptors"])
    )
    parts = [f"QUERY:\n{query}"]
    if route_family:
        parts.append(f"ROUTE_FAMILY:\n{route_family}")
    if candidate_resources:
        parts.append(f"CANDIDATE_RESOURCES:\n{candidate_resources}")
    answer_shape = normalize_text(first_present(trace, ["answer_shape", "expected_answer_shape"]))
    if answer_shape:
        parts.append(f"EXPECTED_ANSWER_SHAPE:\n{answer_shape}")
    return "\n\n".join(parts)


def build_verify_observation(trace: Dict[str, Any], query: str, candidate_action: str) -> str:
    result_summary = normalize_text(first_present(trace, ["result_summary", "resource_summary", "response_summary"]))
    parts = [
        f"QUERY:\n{query}",
        f"CANDIDATE_LOOKUP:\n{candidate_action or '<EMPTY>'}",
    ]
    if result_summary:
        parts.append(f"LOOKUP_RESULT_SUMMARY:\n{result_summary}")
    answer_shape = normalize_text(first_present(trace, ["answer_shape", "expected_answer_shape", "output_contract"]))
    if answer_shape:
        parts.append(f"EXPECTED_ANSWER_SHAPE:\n{answer_shape}")
    return "\n\n".join(parts)


def maybe_emit_route_row(
    trace: Dict[str, Any],
    query: str,
    mcp_name: str,
    trace_id: str,
) -> Optional[Dict[str, Any]]:
    success = inferred_lookup_success(trace)
    model_route = normalize_text(first_present(trace, ["chosen_route_family", "route_family", "resource_family"]))
    target_route = normalize_text(first_present(trace, ["expected_route_family"]))
    if not target_route and success:
        target_route = model_route
    if not model_route and not target_route:
        return None
    route_match = normalize_bool(trace.get("route_match"))
    if target_route and (route_match is True or (model_route and model_route == target_route)):
        bucket = "exact_positive"
    elif target_route and success:
        bucket = "weak_positive"
    else:
        bucket = "negative"
    return {
        "source_env_name": mcp_name,
        "source_env_type": "MCPTrace",
        "task_family": "mcp_route",
        "task": mcp_name,
        "row_id": f"{trace_id}:route",
        "observation": build_route_observation(trace, query),
        "model_action": model_route,
        "target_action": target_route if bucket != "negative" else None,
        "bucket": bucket,
        "supervision_weight": supervision_weight(bucket),
        "reward": 1.0 if bucket == "exact_positive" else (0.5 if bucket == "weak_positive" else 0.0),
        "score": 1.0 if bucket == "exact_positive" else (0.5 if bucket == "weak_positive" else 0.0),
        "valid_action": bool(model_route or target_route),
        "visible_output_emitted": True,
        "reasoning_mode": "off",
        "reasoning_trace": [],
        "reasoning_summary": "Route family supervision row derived from MCP trace.",
        "meta": {
            "trace_id": trace_id,
            "mcp_name": mcp_name,
            "stage_kind": "route",
            "lookup_success": success,
        },
    }


def maybe_emit_retrieve_row(
    trace: Dict[str, Any],
    query: str,
    mcp_name: str,
    trace_id: str,
) -> Optional[Dict[str, Any]]:
    expected_resource = normalize_text(
        first_present(
            trace,
            [
                "expected_resource_uri",
                "expected_uri",
                "resource_uri",
                "chosen_resource_uri",
                "template_uri",
                "template_name",
            ],
        )
    )
    if not expected_resource:
        return None
    success = inferred_lookup_success(trace)
    exact_hit = normalize_bool(first_present(trace, ["exact_hit", "resource_match"]))
    if exact_hit is True:
        bucket = "exact_positive"
    elif success:
        bucket = "weak_positive"
    else:
        bucket = "negative"
    return {
        "source_env_name": mcp_name,
        "source_env_type": "MCPTrace",
        "task_family": "mcp_retrieve",
        "task": mcp_name,
        "row_id": f"{trace_id}:retrieve",
        "observation": build_retrieve_observation(trace, query),
        "model_action": normalize_text(
            first_present(trace, ["chosen_resource_uri", "resource_uri", "template_uri", "template_name"])
        ),
        "target_action": expected_resource if bucket != "negative" else None,
        "bucket": bucket,
        "supervision_weight": supervision_weight(bucket),
        "reward": 1.0 if bucket == "exact_positive" else (0.5 if bucket == "weak_positive" else 0.0),
        "score": 1.0 if bucket == "exact_positive" else (0.5 if bucket == "weak_positive" else 0.0),
        "valid_action": bool(expected_resource),
        "visible_output_emitted": True,
        "reasoning_mode": "off",
        "reasoning_trace": [],
        "reasoning_summary": "Resource retrieval supervision row derived from MCP trace.",
        "meta": {
            "trace_id": trace_id,
            "mcp_name": mcp_name,
            "stage_kind": "retrieve",
            "lookup_success": success,
        },
    }


def maybe_emit_verify_row(
    trace: Dict[str, Any],
    query: str,
    mcp_name: str,
    trace_id: str,
) -> Optional[Dict[str, Any]]:
    candidate_action = normalize_text(
        first_present(
            trace,
            [
                "chosen_resource_uri",
                "resource_uri",
                "template_uri",
                "template_name",
                "chosen_route_family",
            ],
        )
    )
    if not candidate_action:
        return None
    success = inferred_lookup_success(trace)
    verifier_decision = normalize_text(first_present(trace, ["verifier_decision", "verify_decision"]))
    target_action = "accept" if success else "reject"
    bucket = "exact_positive" if (not verifier_decision or verifier_decision == target_action) else "negative"
    return {
        "source_env_name": mcp_name,
        "source_env_type": "MCPTrace",
        "task_family": "mcp_verify",
        "task": mcp_name,
        "row_id": f"{trace_id}:verify",
        "observation": build_verify_observation(trace, query, candidate_action),
        "model_action": verifier_decision or "",
        "target_action": target_action,
        "bucket": bucket,
        "supervision_weight": supervision_weight(bucket),
        "reward": 1.0 if bucket == "exact_positive" else 0.0,
        "score": 1.0 if bucket == "exact_positive" else 0.0,
        "valid_action": True,
        "visible_output_emitted": True,
        "reasoning_mode": "off",
        "reasoning_trace": [],
        "reasoning_summary": "Verifier supervision row derived from MCP trace.",
        "meta": {
            "trace_id": trace_id,
            "mcp_name": mcp_name,
            "stage_kind": "verify",
            "lookup_success": success,
        },
    }


def parse_args() -> argparse.Namespace:
    skill_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build TRM training rows from MCP trace JSONL.")
    parser.add_argument("--input", required=True, help="Input MCP trace JSONL.")
    parser.add_argument(
        "--out-dir",
        default=str(skill_root / "artifacts" / "mcp_trm_rows" / "latest"),
        help="Output directory for rows and summary.",
    )
    parser.add_argument(
        "--mcp-name",
        default="",
        help="Override MCP name. Defaults to per-row `mcp_name` when present.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    out_dir = Path(args.out_dir).resolve()
    traces = load_jsonl(input_path)

    emitted_rows: List[Dict[str, Any]] = []
    family_counts: Counter[str] = Counter()
    bucket_counts: Counter[str] = Counter()
    mcp_counts: Counter[str] = Counter()

    for index, trace in enumerate(traces):
        query = normalize_text(first_present(trace, ["query", "task", "observation", "prompt", "question"]))
        if not query:
            continue
        mcp_name = args.mcp_name.strip() or normalize_text(first_present(trace, ["mcp_name", "server_name", "server"])) or "mcp"
        trace_id = trace_identity(trace, index)

        for builder in [maybe_emit_route_row, maybe_emit_retrieve_row, maybe_emit_verify_row]:
            row = builder(trace, query, mcp_name, trace_id)
            if row is None:
                continue
            emitted_rows.append(row)
            family_counts[str(row["task_family"])] += 1
            bucket_counts[str(row["bucket"])] += 1
            mcp_counts[mcp_name] += 1

    rows_path = out_dir / "mcp_trm_rows.jsonl"
    summary_path = out_dir / "mcp_trm_rows.summary.json"
    write_jsonl(rows_path, emitted_rows)
    write_json(
        summary_path,
        {
            "input": str(input_path),
            "rows_path": str(rows_path),
            "trace_count": len(traces),
            "row_count": len(emitted_rows),
            "task_family_counts": dict(family_counts),
            "bucket_counts": dict(bucket_counts),
            "mcp_counts": dict(mcp_counts),
        },
    )
    print(str(rows_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
