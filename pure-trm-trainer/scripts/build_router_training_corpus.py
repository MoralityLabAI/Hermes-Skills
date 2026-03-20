#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


DEFAULT_SOURCE_CANDIDATES = [
    Path("D:/Research_Engine/tesseract_persistent/data/router/tesseract-router-dataset-v1.jsonl"),
    Path("/mnt/d/Research_Engine/tesseract_persistent/data/router/tesseract-router-dataset-v1.jsonl"),
]


def resolve_existing(path_like: str | Path | List[str | Path], fallback: Path | List[Path]) -> Path:
    if isinstance(path_like, list):
        for item in path_like:
            try:
                return resolve_existing(item, fallback)
            except FileNotFoundError:
                continue
        raise FileNotFoundError(f"Could not resolve any candidate in {path_like}")
    raw = str(path_like or "").strip()
    if raw:
        candidate = Path(raw).expanduser()
        if candidate.exists():
            return candidate.resolve()
        if raw.startswith("D:/"):
            alt = Path(raw.replace("D:/", "/mnt/d/"))
            if alt.exists():
                return alt.resolve()
        if raw.startswith("D:\\"):
            alt = Path(raw.replace("D:\\", "/mnt/d/").replace("\\", "/"))
            if alt.exists():
                return alt.resolve()
    if isinstance(fallback, list):
        for candidate in fallback:
            if candidate.exists():
                return candidate.resolve()
        raise FileNotFoundError(f"Could not resolve {raw or fallback[0]}")
    if fallback.exists():
        return fallback.resolve()
    raise FileNotFoundError(f"Could not resolve {raw or fallback}")


def read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def dump_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            count += 1
    return count


def short_rationale(row: Dict[str, Any]) -> str:
    output = dict(row.get("output") or {})
    rationale = dict(output.get("rationale") or {})
    parts: List[str] = []
    for key in ("data_source", "driver", "response_changed"):
        value = rationale.get(key)
        if value not in (None, "", [], {}):
            parts.append(f"{key}={value}")
    if not parts:
        route = output.get("route")
        if route:
            parts.append(f"route={route}")
    return "; ".join(parts)[:220]


def build_messages(row: Dict[str, Any], system_prompt: str) -> Dict[str, Any]:
    input_block = dict(row.get("input") or {})
    output_block = dict(row.get("output") or {})
    prompt_text = str(input_block.get("prompt_text") or input_block.get("prompt") or row.get("prompt_text") or "").strip()
    intent = str(output_block.get("intent") or input_block.get("intent") or "router").strip()
    route = str(output_block.get("route") or "SLM_PLUS_ADAPTER").strip()
    assistant_payload = {
        "route": route,
        "intent": intent,
        "adapter_id": output_block.get("adapter_id") or "",
        "expert_id": output_block.get("expert_id") or "",
        "prompt_family": output_block.get("prompt_family") or "",
        "tool_caps": output_block.get("tool_caps") or {},
        "rationale_summary": short_rationale(row),
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt_text},
        {"role": "assistant", "content": json.dumps(assistant_payload, ensure_ascii=True)},
    ]
    meta = {
        "source_name": "tesseract-router-dataset-v1",
        "source_run_dir": input_block.get("source_run_dir") or "",
        "source_bench_rows": input_block.get("source_bench_rows") or "",
        "encounter_id": input_block.get("encounter_id") or "",
        "intent": intent,
        "route": route,
    }
    return {"messages": messages, "meta": meta}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert the persistent-tesseract router dataset into messages JSONL for QLoRA training.")
    parser.add_argument("--source", default="", help="Source router JSONL.")
    parser.add_argument("--out", required=True, help="Output messages JSONL.")
    parser.add_argument(
        "--system-prompt",
        default="You are a TRM router. Emit compact JSON only. Do not output hidden reasoning.",
        help="System prompt to prepend to each training row.",
    )
    parser.add_argument("--max-records", type=int, default=0, help="Optional record cap for smoke runs.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve paths and report counts without writing output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_path = resolve_existing(args.source, DEFAULT_SOURCE_CANDIDATES)
    out_path = Path(args.out).expanduser().resolve()
    rows = list(read_jsonl(source_path))
    if args.max_records and args.max_records > 0:
        rows = rows[: args.max_records]

    converted = [build_messages(row, args.system_prompt) for row in rows]
    manifest = {
        "source": str(source_path),
        "out": str(out_path),
        "count": len(converted),
        "system_prompt": args.system_prompt,
    }
    manifest_path = out_path.parent / "router_corpus_manifest.json"
    if args.dry_run:
        print(json.dumps(manifest, indent=2, ensure_ascii=True))
        return 0

    count = dump_jsonl(out_path, converted)
    manifest["count"] = count
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
