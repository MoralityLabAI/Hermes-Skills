#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def dump_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            count += 1
    return count


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        if "value" in value and isinstance(value["value"], str):
            return value["value"].strip()
        if "description" in value and isinstance(value["description"], str):
            return value["description"].strip()
    return ""


def _count_ops(encounter: Dict[str, Any]) -> Dict[str, Any]:
    option_rows = list(encounter.get("options", []) or [])
    option_labels: List[str] = []
    reaction_count = 0
    effect_count = 0
    operator_counts: Counter[str] = Counter()
    effect_targets: Counter[str] = Counter()
    formulas: List[str] = []

    for option in option_rows:
        label = _text(option.get("description")) or _text(option.get("label")) or str(option.get("id", "") or "")
        if label:
            option_labels.append(label)
        if option.get("visibility_script") or option.get("performability_script"):
            formulas.append(_text(option.get("text_script")) or label)
        desirability = option.get("desirability_script")
        if desirability:
            formulas.append(str(desirability.get("operator_type", "") or ""))
        reactions = list(option.get("reactions", []) or [])
        reaction_count += len(reactions)
        for reaction in reactions:
            if reaction.get("desirability_script"):
                formulas.append(str(reaction["desirability_script"].get("operator_type", "") or ""))
            effect_rows = list(reaction.get("after_effects", []) or reaction.get("effects", []) or [])
            effect_count += len(effect_rows)
            for effect in effect_rows:
                op = _text(effect.get("operator")) or _text(effect.get("op")) or _text(effect.get("operator_type"))
                if not op:
                    to_node = effect.get("to") if isinstance(effect, dict) else None
                    if isinstance(to_node, dict):
                        op = _text(to_node.get("operator_type")) or _text(to_node.get("script_element_type"))
                if op:
                    operator_counts[op] += 1
                target = _text(effect.get("target"))
                if not target and isinstance(effect, dict):
                    target = _text(effect.get("Set"))
                if target:
                    effect_targets[target] += 1
                formula = effect.get("formula") or effect.get("formulas")
                if isinstance(formula, list):
                    formulas.extend(_text(item) for item in formula if _text(item))
                else:
                    ft = _text(formula)
                    if ft:
                        formulas.append(ft)
                if isinstance(effect, dict) and isinstance(effect.get("to"), dict):
                    to_node = effect["to"]
                    op2 = _text(to_node.get("operator_type")) or _text(to_node.get("script_element_type"))
                    if op2:
                        operator_counts[op2] += 1
                    inner_formula = to_node.get("formula") or to_node.get("value")
                    if inner_formula:
                        ft2 = _text(inner_formula)
                        if ft2:
                            formulas.append(ft2)

    return {
        "option_count": len(option_rows),
        "reaction_count": reaction_count,
        "effect_count": effect_count,
        "option_labels": option_labels[:6],
        "operator_counts": dict(operator_counts),
        "effect_targets": dict(effect_targets),
        "formulas": formulas[:24],
    }


def _quality_map(quality: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for row in quality.get("checks", []) or []:
        if isinstance(row, dict) and row.get("name"):
            out[str(row["name"])] = row
    return out


def _suggest_ops(stats: Dict[str, Any], quality: Dict[str, Any]) -> List[Dict[str, Any]]:
    suggestions: List[Dict[str, Any]] = []
    qmap = _quality_map(quality)
    failures = {str(x) for x in quality.get("failures", []) or []}
    option_count = int(stats.get("option_count", 0) or 0)
    reaction_count = int(stats.get("reaction_count", 0) or 0)
    effect_count = int(stats.get("effect_count", 0) or 0)
    operator_counts = Counter(stats.get("operator_counts", {}))
    formulas = list(stats.get("formulas", []))

    if "options_per_encounter" in failures or option_count < 3:
        suggestions.append(
            {
                "kind": "option",
                "action": "add_option",
                "reason": "Increase local branching while keeping the story thematically simple.",
                "target_count": max(3, option_count + 1),
            }
        )
    if "reactions_per_option" in failures or reaction_count < 2:
        suggestions.append(
            {
                "kind": "reaction",
                "action": "add_reaction",
                "reason": "Split a coarse reaction into smaller consequences and clearer contrast.",
                "target_count": max(2, reaction_count + 1),
            }
        )
    if "effects_per_reaction" in failures or effect_count < 4:
        suggestions.append(
            {
                "kind": "effect",
                "action": "add_effect",
                "reason": "Add more granular state changes so each reaction carries a clearer machine-readable payload.",
                "target_count": max(4, effect_count + 1),
            }
        )
    if len(operator_counts) <= 1:
        suggestions.append(
            {
                "kind": "formula",
                "action": "diversify_operator",
                "reason": "The model should express multiple formula shapes instead of one operator monoculture.",
                "operator_diversity_target": 3,
            }
        )
    if not formulas or len(set(formulas)) <= 1:
        suggestions.append(
            {
                "kind": "formula",
                "action": "rewrite_formula",
                "reason": "Rewrite the formula payloads into distinct, locally checkable expressions.",
                "formula_diversity_target": 2,
            }
        )
    if "option_visibility_complexity" in failures or qmap.get("option_visibility_complexity", {}).get("pass") is False:
        suggestions.append(
            {
                "kind": "option",
                "action": "rebalance_visibility",
                "reason": "Spread gating across options instead of collapsing to a single visible choice.",
            }
        )
    if "desirability_operator_dominance" in failures or "effect_operator_dominance" in failures:
        suggestions.append(
            {
                "kind": "effect",
                "action": "diversify_effect_operator",
                "reason": "Break operator monoculture by swapping in alternate effect shapes.",
            }
        )
    return suggestions


def _repair_contract() -> Dict[str, Any]:
    return {
        "response_schema": {
            "encounter_id": "string",
            "status": "ok|needs_repair",
            "selected_op": {
                "kind": "option|reaction|effect|formula",
                "action": "string",
                "target": "string",
                "details": "string",
            },
            "repair_notes": ["string"],
        },
        "allowed_kinds": ["option", "reaction", "effect", "formula"],
        "allowed_actions": [
            "add_option",
            "rebalance_visibility",
            "add_reaction",
            "add_effect",
            "diversify_effect_operator",
            "diversify_operator",
            "rewrite_formula",
        ],
        "format_rule": "return JSON only; no markdown fences; no prose wrapper",
        "repair_scope": "local and deterministic",
    }


def build_packets(world: Dict[str, Any], quality: Dict[str, Any]) -> List[Dict[str, Any]]:
    encounters = list(world.get("encounters", []) or [])
    quality_map = _quality_map(quality)
    packets: List[Dict[str, Any]] = []
    for encounter in encounters:
        encounter_id = str(encounter.get("id", "") or "")
        stats = _count_ops(encounter)
        packet = {
            "encounter_id": encounter_id,
            "title": str(encounter.get("title", "") or ""),
            "turn_span": str(encounter.get("turn_span", "") or "0..0"),
            "stats": stats,
            "quality_notes": [name for name, row in quality_map.items() if row.get("pass") is False],
            "suggested_ops": _suggest_ops(stats, quality),
            "repair_contract": _repair_contract(),
            "operation_scope": {
                "formula": "rewrite local numeric/script expressions",
                "option": "adjust branching labels and visibility",
                "effect": "split or merge effect payloads",
                "repair_mode": "local and deterministic",
            },
        }
        packets.append(packet)
    return packets


def main() -> int:
    parser = argparse.ArgumentParser(description="Build discrete operation packets from a world JSON and quality report.")
    parser.add_argument("--world-json", required=True)
    parser.add_argument("--quality-report", default="")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    world_path = Path(args.world_json).expanduser().resolve()
    world = read_json(world_path)
    quality = read_json(Path(args.quality_report).expanduser().resolve()) if args.quality_report else {}
    packets = build_packets(world, quality)

    out_path = Path(args.out).expanduser().resolve()
    count = dump_jsonl(out_path, packets)
    manifest = {
        "world_json": str(world_path),
        "quality_report": str(Path(args.quality_report).expanduser().resolve()) if args.quality_report else "",
        "output": str(out_path),
        "count": count,
        "encounter_count": len(packets),
        "quality_failures": [str(x) for x in quality.get("failures", []) or []],
    }
    dump_json(out_path.parent / "operation_packet_manifest.json", manifest)
    print(str(out_path))
    print(str(out_path.parent / "operation_packet_manifest.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
