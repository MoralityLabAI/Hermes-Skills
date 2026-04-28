from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "primehub_trm_autoresearch" / "cycle_12" / "primehub_trm_merged.jsonl"
DEFAULT_OUTPUT = ROOT / "data" / "hrm_gym" / "primehub_trm_cycle12_public_trace_enriched.jsonl"
DEFAULT_SUMMARY = ROOT / "data" / "hrm_gym" / "primehub_trm_cycle12_public_trace_enriched.summary.json"


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def short_status(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return "unknown"
    lowered = text.lower()
    if "timed out" in lowered:
        return "timeout"
    if "completed" in lowered:
        return "completed"
    if "error" in lowered:
        return "error"
    if len(text) > 48:
        return text[:48]
    return text


def action_shape(model_action: Any, visible_output_emitted: Any) -> str:
    text = str(model_action or "").strip()
    if not visible_output_emitted:
        return "internal_only"
    if not text:
        return "empty"
    if "\n" in text and ":" in text:
        return "multiline_structured"
    if len(text) <= 24:
        return "short_exact"
    if len(text) <= 120 and "\n" not in text:
        return "short_single_line"
    return "longform"


def normalize_env_name(env_name: str) -> str:
    env = "".join(char.lower() if char.isalnum() else "_" for char in env_name).strip("_") or "unknown"
    while "__" in env:
        env = env.replace("__", "_")
    return env


def infer_action_family(env_name: str, text: str, visible_output_emitted: bool, namespace: str = "env_shape") -> str:
    env = normalize_env_name(env_name)
    stripped = str(text or "").strip()
    upper = stripped.upper()

    prefix = f"{env}::" if namespace == "env_shape" else ""

    if not stripped:
        return f"{prefix}no_output"
    if not visible_output_emitted and stripped == "inspect_and_continue":
        return f"{prefix}internal_inspect_continue"
    if stripped.startswith("<ascii_formatted>") or "+--" in stripped:
        return f"{prefix}ascii_tree"
    if stripped.startswith("[[") and stripped.endswith("]]") and len(stripped) <= 8:
        return f"{prefix}double_bracket_choice"
    if stripped.startswith("\\boxed{") and stripped.endswith("}"):
        inner = stripped[len("\\boxed{") : -1].strip()
        if len(inner) == 1 and inner.isalpha():
            return f"{prefix}boxed_choice"
        if inner.replace(".", "", 1).replace("-", "", 1).isdigit():
            return f"{prefix}boxed_number"
        return f"{prefix}boxed_exact"
    if len(stripped) == 1 and upper in {"A", "B", "C", "D", "E"}:
        return f"{prefix}single_choice_letter"
    if stripped in {"True", "False"}:
        return f"{prefix}boolean_word"
    if stripped.startswith("Final Answer:"):
        return f"{prefix}final_answer_prefixed"

    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    if lines and all(":" in line and line.split(":", 1)[0].strip().isdigit() for line in lines[: min(len(lines), 8)]):
        return f"{prefix}indexed_mapping"
    if "," in stripped:
        parts = [part.strip() for part in stripped.split(",") if part.strip()]
        if len(parts) == 4 and all(len(part.split()) <= 3 for part in parts):
            return f"{prefix}comma_list_4"
        return f"{prefix}comma_list"
    if "\n\n" in stripped or len(stripped) >= 400:
        return f"{prefix}longform_narrative"
    if len(stripped.split()) <= 8:
        return f"{prefix}short_exact"
    return f"{prefix}short_response"


def top_symbolic_channel(row: Dict[str, Any]) -> str:
    channels = row.get("symbolic_channels") or {}
    best_name = ""
    best_value = 0.0
    for name, raw_value in channels.items():
        try:
            value = abs(float(raw_value))
        except (TypeError, ValueError):
            continue
        if value > best_value:
            best_value = value
            best_name = str(name)
    return best_name or "none"


def build_public_trace(row: Dict[str, Any]) -> List[Dict[str, str]]:
    trace: List[Dict[str, str]] = []
    env_name = str(row.get("source_env_name") or "unknown")
    task_family = str(row.get("task_family") or "unknown")
    status = short_status(row.get("output_status"))
    channel = top_symbolic_channel(row)
    shape = action_shape(row.get("model_action"), row.get("visible_output_emitted"))

    trace.append(
        {
            "stage": "TRM_PARSE",
            "note": f"parse {task_family} task from {env_name}",
        }
    )

    if channel != "none" or row.get("constitutional_score") is not None:
        critic_note = f"critic on constitutional signal {channel}"
        if row.get("constitutional_score") is not None:
            critic_note += f" score={float(row.get('constitutional_score') or 0.0):.3f}"
        trace.append({"stage": "TRM_CRITIC", "note": critic_note})

    trace.append(
        {
            "stage": "TRM_ROUTE",
            "note": f"route action shape={shape}",
        }
    )

    if row.get("visible_output_emitted"):
        trace.append(
            {
                "stage": "TRM_COMPRESS",
                "note": f"compress public output status={status}",
            }
        )
    else:
        trace.append(
            {
                "stage": "TRM_MONITOR",
                "note": f"monitor internal-only path status={status}",
            }
        )

    trace.append(
        {
            "stage": "FINAL",
            "note": f"final status={status}",
        }
    )
    return trace


def render_public_summary(trace: List[Dict[str, str]], original_summary: Any) -> str:
    stage_path = " -> ".join(str(item.get("stage") or "").strip() for item in trace if item.get("stage"))
    note_tail = "; ".join(str(item.get("note") or "").strip() for item in trace[:4] if item.get("note"))
    original = str(original_summary or "").strip()
    parts = [
        f"Public trace: {stage_path}.",
        note_tail + "." if note_tail else "",
        original,
    ]
    return " ".join(part for part in parts if part).strip()


def enrich_row(
    row: Dict[str, Any],
    *,
    exact_positive_weight: float,
    weak_positive_family_weight: float,
    family_namespace: str,
    include_weak_positive_families: bool,
) -> Dict[str, Any]:
    enriched = dict(row)
    existing_trace = row.get("reasoning_trace")
    synthesized = not bool(existing_trace)
    public_trace = existing_trace if existing_trace else build_public_trace(row)

    enriched["reasoning_trace"] = public_trace
    enriched["reasoning_summary"] = render_public_summary(public_trace, row.get("reasoning_summary"))
    if synthesized:
        enriched["reasoning_mode"] = "public_trace_synth"

    if str(row.get("bucket") or "") == "exact_positive" and row.get("target_action"):
        prior_weight = float(row.get("supervision_weight") or 1.0)
        enriched["supervision_weight"] = max(prior_weight, exact_positive_weight)
        enriched["target_action_family"] = infer_action_family(
            str(row.get("source_env_name") or "unknown"),
            str(row.get("target_action") or row.get("model_action") or ""),
            bool(row.get("visible_output_emitted")),
            namespace=family_namespace,
        )
    elif include_weak_positive_families and str(row.get("bucket") or "") == "weak_positive":
        family_text = str(row.get("model_action") or row.get("target_action") or "")
        enriched["target_action_family"] = infer_action_family(
            str(row.get("source_env_name") or "unknown"),
            family_text,
            bool(row.get("visible_output_emitted")),
            namespace=family_namespace,
        )
        prior_weight = float(row.get("supervision_weight") or 0.2)
        enriched["supervision_weight"] = max(prior_weight, weak_positive_family_weight)

    meta = dict(row.get("meta") or {})
    meta["hrm_gym_enrichment"] = {
        "version": "public_trace_v1",
        "trace_synthesized": synthesized,
        "target_action_family": enriched.get("target_action_family"),
    }
    enriched["meta"] = meta
    return enriched


def build_summary(rows: List[Dict[str, Any]], enriched_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    bucket_counts = Counter(str(row.get("bucket") or "unknown") for row in enriched_rows)
    trace_lengths = Counter(len(row.get("reasoning_trace") or []) for row in enriched_rows)
    reasoning_modes = Counter(str(row.get("reasoning_mode") or "unknown") for row in enriched_rows)
    synthesized_rows = sum(
        1
        for row in enriched_rows
        if bool(((row.get("meta") or {}).get("hrm_gym_enrichment") or {}).get("trace_synthesized"))
    )
    exact_positive_weights = sorted(
        {
            float(row.get("supervision_weight") or 0.0)
            for row in enriched_rows
            if str(row.get("bucket") or "") == "exact_positive"
        }
    )
    weak_positive_weights = sorted(
        {
            float(row.get("supervision_weight") or 0.0)
            for row in enriched_rows
            if str(row.get("bucket") or "") == "weak_positive"
        }
    )
    action_family_rows = sum(1 for row in enriched_rows if row.get("target_action_family"))
    distinct_action_families = len({str(row.get("target_action_family") or "") for row in enriched_rows if row.get("target_action_family")})

    return {
        "input_rows": len(rows),
        "output_rows": len(enriched_rows),
        "bucket_counts": dict(bucket_counts),
        "synthesized_trace_rows": synthesized_rows,
        "reasoning_mode_counts": dict(reasoning_modes),
        "trace_length_counts": dict(trace_lengths),
        "exact_positive_supervision_weights": exact_positive_weights,
        "weak_positive_supervision_weights": weak_positive_weights,
        "action_family_rows": action_family_rows,
        "distinct_action_families": distinct_action_families,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an HRM gym source with public-trace synthesis.")
    parser.add_argument("--input-jsonl", default=str(DEFAULT_INPUT))
    parser.add_argument("--output-jsonl", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--summary-json", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--exact-positive-weight", type=float, default=2.5)
    parser.add_argument("--weak-positive-family-weight", type=float, default=0.75)
    parser.add_argument("--family-namespace", choices=["env_shape", "shape"], default="env_shape")
    parser.add_argument("--include-weak-positive-families", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input_jsonl).resolve()
    output_path = Path(args.output_jsonl).resolve()
    summary_path = Path(args.summary_json).resolve()

    rows = load_jsonl(input_path)
    enriched_rows = [
        enrich_row(
            row,
            exact_positive_weight=float(args.exact_positive_weight),
            weak_positive_family_weight=float(args.weak_positive_family_weight),
            family_namespace=str(args.family_namespace),
            include_weak_positive_families=bool(args.include_weak_positive_families),
        )
        for row in rows
    ]
    write_jsonl(output_path, enriched_rows)
    write_json(summary_path, build_summary(rows, enriched_rows))
    print(
        json.dumps(
            {
                "output_jsonl": str(output_path),
                "summary_json": str(summary_path),
                "rows": len(enriched_rows),
            },
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
