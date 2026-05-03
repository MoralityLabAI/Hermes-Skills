#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def iter_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        raw = line.strip()
        if not raw:
            continue
        rows.append(json.loads(raw))
    return rows


def local_fix_hints(global_advice: Dict[str, Any], encounter: Dict[str, Any]) -> List[str]:
    hints: List[str] = []
    failures = set(global_advice.get("quality_failures", []))
    consequences = list(encounter.get("consequences", []))
    option_labels = list(encounter.get("option_labels", []))
    reaction_count = int(encounter.get("reaction_count", 0) or 0)
    encounter_id = str(encounter.get("encounter_id", ""))

    if "avg_encounter_words" in failures or "avg_reaction_words" in failures:
        hints.append("Increase local specificity with slightly richer option and reaction phrasing.")
    if "effects_per_reaction" in failures:
        hints.append("Prefer denser effect payloads rather than flat single-axis updates.")
    if "effect_operator_variety" in failures or "effect_operator_dominance" in failures:
        hints.append("Reduce pure NUDGE monoculture when possible by varying local effect structure.")
    if "pvalue_refs" in failures:
        hints.append("If natural, add at least one desirability reference using P(...).")
    if "p2value_refs" in failures:
        hints.append("If natural, add at least one second-order desirability reference using P2(...).")
    if global_advice.get("raw_metrics", {}).get("dead_end_rate_pct", 0.0) >= 100.0:
        if consequences:
            hints.append("Avoid making all local consequences feel terminal or convergent; preserve continuation pressure.")
    if reaction_count <= 2:
        hints.append("Use the available reactions to maximize contrast instead of repeating the same emotional move.")
    if len(set(option_labels)) <= 1 and option_labels:
        hints.append("Differentiate reactions under the same option with clearer tradeoffs and consequences.")
    if len(set(consequences)) <= 1 and consequences:
        hints.append(f"Do not let every reaction in {encounter_id} collapse into the same narrative consequence tone.")
    return hints


def build_packet(global_advice: Dict[str, Any], encounters: List[Dict[str, Any]]) -> Dict[str, Any]:
    local_targets: List[Dict[str, Any]] = []
    all_hints: List[str] = []
    for encounter in encounters:
        hints = local_fix_hints(global_advice, encounter)
        local_targets.append(
            {
                "encounter_id": encounter.get("encounter_id"),
                "turn_span": encounter.get("turn_span"),
                "reaction_count": encounter.get("reaction_count"),
                "option_labels": encounter.get("option_labels", []),
                "consequences": encounter.get("consequences", []),
                "local_fix_hints": hints,
            }
        )
        all_hints.extend(hints)

    deduped_hints: List[str] = []
    seen: set[str] = set()
    for hint in all_hints:
        if hint in seen:
            continue
        seen.add(hint)
        deduped_hints.append(hint)

    return {
        "storyworld": global_advice.get("storyworld", {}),
        "focus_metrics": global_advice.get("focus_metrics", []),
        "quality_failures": global_advice.get("quality_failures", []),
        "priority_fixes": deduped_hints[:8] or global_advice.get("priority_fixes", [])[:8],
        "phase_guidance": {
            "plan": [
                "Translate global failures into encounter-local edits only.",
                "Prefer the smallest revision that improves continuity, consequence clarity, or operator variety.",
            ],
            "encounter_build": [
                "Emit only a valid ENC block with stable ids.",
                "Change text and scripts only where the local fix hints justify it.",
                "Do not apply broad whole-world rebalance ideas directly inside one encounter.",
            ],
            "local_fix_hints": deduped_hints[:8],
        },
        "local_targets": local_targets,
        "recommended_overrides": {
            "style": {
                "scene_scope": "local",
                "novelty": "low",
                "format_discipline": "strict",
            },
            "repair_build_output": True,
        },
        "notes": [
            "Derived from global Monte Carlo and quality failures, narrowed to the requested encounters.",
            "Use this packet for local authoring guidance, not whole-world rebalance planning.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local authoring TRM packet from global advice and encounter index rows.")
    parser.add_argument("--global-advice", required=True)
    parser.add_argument("--encounter-index-jsonl", required=True)
    parser.add_argument("--encounter-ids", nargs="+", required=True)
    parser.add_argument("--out-json", required=True)
    args = parser.parse_args()

    global_advice = read_json(Path(args.global_advice).resolve())
    encounter_rows = iter_jsonl(Path(args.encounter_index_jsonl).resolve())
    wanted = set(args.encounter_ids)
    picked = [row for row in encounter_rows if str(row.get("encounter_id")) in wanted]
    payload = build_packet(global_advice, picked)
    out_path = Path(args.out_json).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
