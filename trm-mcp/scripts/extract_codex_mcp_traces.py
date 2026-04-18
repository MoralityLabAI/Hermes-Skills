from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


MCP_TOOLS = {
    "list_mcp_resources",
    "list_mcp_resource_templates",
    "read_mcp_resource",
}


def load_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def parse_json_maybe(text: str) -> Any:
    text = normalize_text(text)
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def extract_message_text(payload: Dict[str, Any]) -> str:
    pieces: List[str] = []
    for part in payload.get("content", []):
        part_type = part.get("type")
        if part_type in {"input_text", "output_text", "text"}:
            text = normalize_text(part.get("text"))
            if text:
                pieces.append(text)
    return "\n".join(pieces).strip()


def extract_user_message(event: Dict[str, Any]) -> str:
    payload = event.get("payload", {})
    if event.get("type") == "event_msg" and payload.get("type") == "user_message":
        return normalize_text(payload.get("message"))
    if event.get("type") == "response_item" and payload.get("type") == "message" and payload.get("role") == "user":
        return extract_message_text(payload)
    return ""


def parse_call_arguments(arguments: Any) -> Dict[str, Any]:
    if isinstance(arguments, dict):
        return arguments
    parsed = parse_json_maybe(normalize_text(arguments))
    if isinstance(parsed, dict):
        return parsed
    return {}


def tool_route_family(tool_name: str) -> str:
    if tool_name == "list_mcp_resources":
        return "resource_list"
    if tool_name == "list_mcp_resource_templates":
        return "resource_template_list"
    if tool_name == "read_mcp_resource":
        return "resource_read"
    return "unknown"


def answer_shape_for_tool(tool_name: str) -> str:
    if tool_name == "list_mcp_resources":
        return "resource_list"
    if tool_name == "list_mcp_resource_templates":
        return "resource_template_list"
    if tool_name == "read_mcp_resource":
        return "resource_payload"
    return ""


def parse_mcp_result(result: Dict[str, Any]) -> Tuple[bool, Any, str]:
    if "Err" in result:
        error = normalize_text(result.get("Err"))
        return False, None, error
    ok = result.get("Ok")
    if not isinstance(ok, dict):
        return False, None, "missing_ok_payload"
    for content_item in ok.get("content", []):
        if content_item.get("type") != "text":
            continue
        text = normalize_text(content_item.get("text"))
        parsed = parse_json_maybe(text)
        if parsed is not None:
            return True, parsed, ""
        return True, text, ""
    return True, ok, ""


def compact_candidates(parsed_payload: Any) -> List[str]:
    candidates: List[str] = []
    if isinstance(parsed_payload, dict):
        for key in ("resources", "resourceTemplates"):
            items = parsed_payload.get(key)
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict):
                    label = (
                        normalize_text(item.get("uri"))
                        or normalize_text(item.get("name"))
                        or normalize_text(item.get("title"))
                        or normalize_text(item.get("description"))
                    )
                    if label:
                        candidates.append(label)
                else:
                    text = normalize_text(item)
                    if text:
                        candidates.append(text)
    elif isinstance(parsed_payload, list):
        for item in parsed_payload:
            text = normalize_text(item)
            if text:
                candidates.append(text)
    return candidates[:24]


def build_result_summary(tool_name: str, ok: bool, parsed_payload: Any, error_text: str) -> str:
    if not ok:
        return error_text or f"{tool_name} failed"
    if isinstance(parsed_payload, dict):
        if "resources" in parsed_payload and isinstance(parsed_payload["resources"], list):
            return f"resources={len(parsed_payload['resources'])}"
        if "resourceTemplates" in parsed_payload and isinstance(parsed_payload["resourceTemplates"], list):
            return f"resource_templates={len(parsed_payload['resourceTemplates'])}"
    if isinstance(parsed_payload, str):
        text = parsed_payload.strip()
        if len(text) > 180:
            return text[:177] + "..."
        return text
    return f"{tool_name} ok"


def useful_hit(tool_name: str, ok: bool, parsed_payload: Any) -> bool:
    if not ok:
        return False
    if tool_name == "read_mcp_resource":
        return True
    if isinstance(parsed_payload, dict):
        if "resources" in parsed_payload and isinstance(parsed_payload["resources"], list):
            return len(parsed_payload["resources"]) > 0
        if "resourceTemplates" in parsed_payload and isinstance(parsed_payload["resourceTemplates"], list):
            return len(parsed_payload["resourceTemplates"]) > 0
    return False


def resource_descriptor(uri: str) -> List[str]:
    if not uri:
        return []
    path_tail = uri.rstrip("/").split("/")[-1]
    if path_tail and path_tail != uri:
        return [uri, path_tail]
    return [uri]


def emit_trace(
    session_path: Path,
    call: Dict[str, Any],
    tool_end_payload: Dict[str, Any],
) -> Dict[str, Any]:
    invocation = tool_end_payload.get("invocation", {})
    result = tool_end_payload.get("result", {})
    server = normalize_text(invocation.get("server")) or normalize_text(call["arguments"].get("server")) or "unknown"
    tool_name = normalize_text(invocation.get("tool")) or call["tool_name"]
    ok, parsed_payload, error_text = parse_mcp_result(result if isinstance(result, dict) else {})
    candidates = compact_candidates(parsed_payload)
    uri = normalize_text(call["arguments"].get("uri"))
    hit = useful_hit(tool_name, ok, parsed_payload)
    summary = build_result_summary(tool_name, ok, parsed_payload, error_text)
    query = call["query"]
    return {
        "trace_id": f"{session_path.stem}:{call['call_id']}",
        "session_path": str(session_path),
        "mcp_name": server,
        "query": query,
        "tool_name": tool_name,
        "chosen_route_family": tool_route_family(tool_name),
        "route_family": tool_route_family(tool_name),
        "resource_family": server,
        "resource_uri": uri or "",
        "chosen_resource_uri": uri or "",
        "candidate_resources": candidates if candidates else resource_descriptor(uri),
        "resource_descriptors": candidates if candidates else resource_descriptor(uri),
        "available_families": ["resource_list", "resource_template_list", "resource_read"],
        "answer_shape": answer_shape_for_tool(tool_name),
        "useful_hit": hit,
        "success": ok,
        "exact_hit": hit and tool_name == "read_mcp_resource",
        "resource_match": hit and bool(uri),
        "verifier_decision": "accept" if hit else "reject",
        "result_summary": summary,
        "error": error_text,
        "call_id": call["call_id"],
        "timestamp_call": call["timestamp_call"],
        "timestamp_result": normalize_text(tool_end_payload.get("timestamp")),
        "meta": {
            "source": "codex_session_mcp_adapter",
            "session_name": session_path.name,
            "session_dir": str(session_path.parent),
        },
    }


def collect_input_files(inputs: List[str], max_files: int) -> List[Path]:
    files: List[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_file():
            files.append(path)
            continue
        if path.is_dir():
            for child in path.rglob("*.jsonl"):
                files.append(child)
    files = sorted(set(files))
    if max_files > 0:
        files = files[:max_files]
    return files


def process_session(path: Path) -> List[Dict[str, Any]]:
    traces: List[Dict[str, Any]] = []
    pending_calls: Dict[str, Dict[str, Any]] = {}
    latest_user_query = ""
    for event in load_jsonl(path):
        user_message = extract_user_message(event)
        if user_message:
            latest_user_query = user_message
        event_type = normalize_text(event.get("type"))
        payload = event.get("payload", {})
        payload_type = normalize_text(payload.get("type"))
        if event_type == "response_item" and payload_type == "function_call":
            tool_name = normalize_text(payload.get("name"))
            if tool_name not in MCP_TOOLS:
                continue
            call_id = normalize_text(payload.get("call_id"))
            if not call_id:
                continue
            pending_calls[call_id] = {
                "call_id": call_id,
                "tool_name": tool_name,
                "arguments": parse_call_arguments(payload.get("arguments")),
                "timestamp_call": normalize_text(event.get("timestamp")),
                "query": latest_user_query,
            }
            continue
        if event_type == "event_msg" and payload_type == "mcp_tool_call_end":
            call_id = normalize_text(payload.get("call_id"))
            call = pending_calls.pop(call_id, None)
            if not call:
                continue
            traces.append(emit_trace(path, call, {"timestamp": event.get("timestamp"), **payload}))
    return traces


def build_summary(traces: List[Dict[str, Any]], files: List[Path]) -> Dict[str, Any]:
    tool_counts: Counter[str] = Counter()
    server_counts: Counter[str] = Counter()
    useful_counts: Counter[str] = Counter()
    for trace in traces:
        tool_counts[normalize_text(trace.get("tool_name"))] += 1
        server_counts[normalize_text(trace.get("mcp_name"))] += 1
        useful_counts["useful_hit" if trace.get("useful_hit") else "not_useful"] += 1
    return {
        "input_count": len(files),
        "trace_count": len(traces),
        "tool_counts": dict(tool_counts),
        "server_counts": dict(server_counts),
        "usefulness_counts": dict(useful_counts),
        "input_files": [str(path) for path in files],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract MCP lookup traces from Codex session JSONL.")
    parser.add_argument("--input", nargs="+", required=True, help="Session JSONL file(s) or directories.")
    parser.add_argument("--out-dir", required=True, help="Directory for normalized trace artifacts.")
    parser.add_argument("--max-files", type=int, default=0, help="Optional limit on discovered input files.")
    args = parser.parse_args()

    files = collect_input_files(args.input, args.max_files)
    traces: List[Dict[str, Any]] = []
    for path in files:
        traces.extend(process_session(path))

    out_dir = Path(args.out_dir)
    traces_path = out_dir / "codex_mcp_traces.jsonl"
    summary_path = out_dir / "codex_mcp_traces.summary.json"
    write_jsonl(traces_path, traces)
    write_json(summary_path, build_summary(traces, files))
    print(str(traces_path))
    print(str(summary_path))


if __name__ == "__main__":
    main()
