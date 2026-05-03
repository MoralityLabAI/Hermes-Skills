#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


PICK_PREFIX = "PICK "


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        raw = line.strip()
        if not raw:
            continue
        yield json.loads(raw)


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> int:
    count = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            count += 1
    return count


def compact_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def normalize_tools(value: Any, default: List[str] | None = None) -> List[str]:
    if isinstance(value, list):
        tools = [str(item).strip() for item in value if str(item).strip()]
        return tools or list(default or ["WAIT"])
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return list(default or ["WAIT"])


def extract_pick_index(label: str) -> int:
    if not label.startswith(PICK_PREFIX):
        return 0
    tail = label[len(PICK_PREFIX) :].strip()
    try:
        return max(0, int(tail))
    except ValueError:
        return 0


def extract_tools_and_action_from_trm_row(row: Dict[str, Any]) -> Tuple[List[str], str]:
    reason = row.get("reasoning_interpret_log", {})
    candidates = reason.get("candidate_scores", []) if isinstance(reason, dict) else []
    if not isinstance(candidates, list):
        candidates = []
    tools: List[str] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        opt_id = str(candidate.get("opt_id", "") or "").strip()
        action = str(candidate.get("action", "") or "").strip()
        if opt_id:
            tools.append(opt_id)
        elif action:
            tools.append(action)
    tools = tools or ["WAIT"]

    pick_index = extract_pick_index(str(row.get("label", "") or ""))
    chosen = ""
    if pick_index < len(candidates) and isinstance(candidates[pick_index], dict):
        candidate = candidates[pick_index]
        chosen = str(candidate.get("opt_id", "") or "").strip() or str(candidate.get("action", "") or "").strip()
    if not chosen:
        chosen = tools[min(pick_index, len(tools) - 1)]
    return tools, chosen


def build_state_from_trm_row(row: Dict[str, Any], world_id: str) -> str:
    event = row.get("event", {})
    latent = row.get("latent", {})
    metrics = event.get("metrics", {}) if isinstance(event, dict) else {}
    state = {
        "world_id": world_id,
        "episode": int(row.get("episode", 0) or 0),
        "turn": int(row.get("turn", 0) or 0),
        "encounter_id": str(event.get("encounter_id", "") if isinstance(event, dict) else ""),
        "next_encounter": str(event.get("next_encounter", "") if isinstance(event, dict) else ""),
        "outcome": str(event.get("outcome", "") if isinstance(event, dict) else ""),
        "latent_norm": float(latent.get("latent_norm", 0.0) or 0.0) if isinstance(latent, dict) else 0.0,
        "desirability": float(metrics.get("desirability", 0.0) or 0.0) if isinstance(metrics, dict) else 0.0,
    }
    return compact_json(state)


def collect_trm_play_root(source: Dict[str, Any]) -> List[Dict[str, Any]]:
    run_root = Path(source["path"]).resolve()
    trace_files = sorted(run_root.glob("worlds/*/trm_traces.jsonl"))
    rows: List[Dict[str, Any]] = []
    for trace_file in trace_files:
        world_id = trace_file.parent.name
        for row in iter_jsonl(trace_file):
            tools, action = extract_tools_and_action_from_trm_row(row)
            rows.append(
                {
                    "state": build_state_from_trm_row(row, world_id),
                    "tools": tools,
                    "action": action,
                    "meta": {
                        "source_name": source.get("name", "trm-play"),
                        "source_type": "trm_play_root",
                        "world_id": world_id,
                        "source_trace": str(trace_file),
                        "episode": row.get("episode"),
                        "turn": row.get("turn"),
                    },
                }
            )
    return rows


def _extract_field(row: Dict[str, Any], field: str, default: Any = "") -> Any:
    current: Any = row
    for key in field.split("."):
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def collect_jsonl_source(source: Dict[str, Any]) -> List[Dict[str, Any]]:
    path = Path(source["path"]).resolve()
    rows: List[Dict[str, Any]] = []
    mode = str(source.get("mode", "normalized") or "normalized")
    state_fields = list(source.get("state_fields", []))
    meta_fields = list(source.get("meta_fields", []))
    for row in iter_jsonl(path):
        if mode == "normalized":
            state = str(row.get("state", "") or "")
            tools = normalize_tools(row.get("tools"))
            action = str(row.get("action", "") or "").strip()
            meta = dict(row.get("meta", {})) if isinstance(row.get("meta"), dict) else {}
        else:
            payload = {field: _extract_field(row, field, "") for field in state_fields}
            state = compact_json(payload)
            tools = normalize_tools(_extract_field(row, str(source.get("tools_field", "")), []), source.get("tools_default"))
            action = str(_extract_field(row, str(source.get("action_field", "")), source.get("action_default", "")) or "").strip()
            meta = {field: _extract_field(row, field, "") for field in meta_fields}
        if not state or not action:
            continue
        meta.update(
            {
                "source_name": source.get("name", path.stem),
                "source_type": mode if mode != "normalized" else "jsonl_normalized",
                "source_path": str(path),
            }
        )
        rows.append({"state": state, "tools": tools, "action": action, "meta": meta})
    return rows


def normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    meta = dict(row.get("meta", {})) if isinstance(row.get("meta"), dict) else {}
    return {
        "state": str(row.get("state", "") or "").strip(),
        "tools": normalize_tools(row.get("tools")),
        "action": str(row.get("action", "") or "").strip(),
        "meta": meta,
    }


def row_key(row: Dict[str, Any]) -> str:
    payload = {"state": row["state"], "tools": row["tools"], "action": row["action"]}
    return hashlib.sha1(compact_json(payload).encode("utf-8")).hexdigest()


def split_rows(rows: List[Dict[str, Any]], train_ratio: float, seed: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    working = list(rows)
    rng = random.Random(seed)
    rng.shuffle(working)
    if not working:
        return [], []
    split_index = int(len(working) * train_ratio)
    split_index = min(max(split_index, 1), len(working))
    if split_index == len(working) and len(working) > 1:
        split_index -= 1
    return working[:split_index], working[split_index:]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a normalized TRM training corpus from mixed sources.")
    parser.add_argument("--config", required=True, help="JSON corpus spec path.")
    parser.add_argument("--out-dir", default="", help="Optional output directory override.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config = read_json(config_path)
    out_dir = Path(args.out_dir).resolve() if args.out_dir else Path(config.get("output_dir") or (config_path.parent / "trm_corpus")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    all_rows: List[Dict[str, Any]] = []
    source_counts: List[Dict[str, Any]] = []
    for source in config.get("sources", []):
        source_type = str(source.get("type", "") or "")
        if source_type == "trm_play_root":
            rows = collect_trm_play_root(source)
        elif source_type == "jsonl":
            rows = collect_jsonl_source(source)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
        normalized = [normalize_row(row) for row in rows if row.get("state") and row.get("action")]
        all_rows.extend(normalized)
        source_counts.append({"name": source.get("name", source_type), "type": source_type, "rows": len(normalized)})

    dedupe = bool(config.get("dedupe", True))
    if dedupe:
        deduped: List[Dict[str, Any]] = []
        seen: set[str] = set()
        for row in all_rows:
            key = row_key(row)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(row)
        all_rows = deduped

    train_ratio = float(config.get("train_ratio", 0.9) or 0.9)
    seed = int(config.get("shuffle_seed", 7) or 7)
    train_rows, val_rows = split_rows(all_rows, train_ratio, seed)

    train_path = out_dir / "train.jsonl"
    val_path = out_dir / "val.jsonl"
    manifest_path = out_dir / "manifest.json"
    splits_path = out_dir / "splits.json"

    train_count = write_jsonl(train_path, train_rows)
    val_count = write_jsonl(val_path, val_rows)
    dump_json(splits_path, {"train": str(train_path), "val": str(val_path), "train_count": train_count, "val_count": val_count})
    dump_json(
        manifest_path,
        {
            "config_path": str(config_path),
            "output_dir": str(out_dir),
            "source_counts": source_counts,
            "dedupe": dedupe,
            "train_ratio": train_ratio,
            "shuffle_seed": seed,
            "total_rows": len(all_rows),
            "train_rows": train_count,
            "val_rows": val_count,
            "outputs": {"train": str(train_path), "val": str(val_path), "splits": str(splits_path)},
        },
    )
    print(str(out_dir))
    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
