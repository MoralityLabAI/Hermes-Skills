#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from storyworld_mcp_server import StoryworldIndex  # type: ignore


SYSTEM_PROMPT = (
    "You are a Hermes TRM router for a small-storyworld assembly line. "
    "Route each turn to the smallest lookup that unlocks the next stage. "
    "Return compact JSON only and do not solve the task in prose."
)


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def dump_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> int:
    count = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            count += 1
    return count


def build_row(
    *,
    family: str,
    phase: str,
    user_prompt: str,
    tool: str,
    args: Dict[str, Any],
    namespace: str,
    source_files: List[str],
) -> Dict[str, Any]:
    assistant_payload = {
        "tool": tool,
        "args": args,
        "prompt_family": family,
        "phase": phase,
        "namespace": namespace,
        "compression": "excerpt",
    }
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": json.dumps(assistant_payload, ensure_ascii=True)},
        ],
        "meta": {
            "prompt_family": family,
            "phase": phase,
            "tool": tool,
            "namespace": namespace,
            "source_files": source_files,
        },
    }


def resolved_samples(index: StoryworldIndex) -> Dict[str, str]:
    summary = index.describe()
    sample_ids = [str(item) for item in summary.get("sample_encounter_ids", []) if str(item).strip()]
    scene_ids = [item for item in sample_ids if item.startswith("page_scene_")]
    terminal_ids = [item for item in sample_ids if item.startswith("page_end_")]
    if not scene_ids and sample_ids:
        scene_ids = [sample_ids[0]]
    if not terminal_ids and sample_ids:
        terminal_ids = [sample_ids[-1]]
    return {
        "scene_id": scene_ids[0] if scene_ids else "page_scene_01",
        "terminal_id": terminal_ids[0] if terminal_ids else "page_end_200",
        "sample_lore_query": "core story rules and structural constraints",
    }


def build_examples(index: StoryworldIndex) -> List[Dict[str, Any]]:
    samples = resolved_samples(index)
    scene_id = samples["scene_id"]
    terminal_id = samples["terminal_id"]
    examples: List[Dict[str, Any]] = []

    families = [
        (
            "encounter_build",
            "encounter_build",
            "Build out the encounter packet for {scene_id}; I need the local reactions, option labels, and the exact card.",
            "get_encounter_card",
            lambda: {"encounter_id": scene_id},
            "encounters",
        ),
        (
            "scene_followup",
            "characterize",
            "I need the encounter card for {terminal_id} and the adjacent route context.",
            "get_encounter_card",
            lambda: {"encounter_id": terminal_id},
            "encounters",
        ),
        (
            "world_rules",
            "plan",
            "What are the world's core story rules and structural constraints?",
            "query_lore_index",
            lambda: {"namespace": "world_card", "query": samples["sample_lore_query"]},
            "world_card",
        ),
        (
            "monte_carlo_rebalance",
            "characterize",
            "Review the Monte Carlo distribution to target a rebalance.",
            "query_lore_index",
            lambda: {"namespace": "monte_carlo", "query": "distribution target a rebalance"},
            "monte_carlo",
        ),
        (
            "quality_gate_pathing",
            "act_complete",
            "Review the quality gate failures that affect pathing, options, reactions, and effects.",
            "query_lore_index",
            lambda: {"namespace": "quality_gate", "query": "pathing options reactions effects"},
            "quality_gate",
        ),
        (
            "formula_rebalance",
            "recharacterize",
            "Revise the formulas to modify pathing and ending rebalance.",
            "query_lore_index",
            lambda: {"namespace": "rebalance_advice", "query": "pathing ending rebalance formulas"},
            "rebalance_advice",
        ),
    ]

    prompt_variants = {
        "encounter_build": [
            "Build out the encounter packet for {scene_id}; I need the local reactions, option labels, and the exact card.",
            "Pull the smallest local card for {scene_id} so I can author the next turn.",
        ],
        "scene_followup": [
            "I need the encounter card for {terminal_id} and the adjacent route context.",
            "Fetch the terminal encounter packet for {terminal_id}; keep the context tight.",
        ],
        "world_rules": [
            "What are the world's core story rules and structural constraints?",
            "Give me the smallest world-card excerpt that explains the core rules.",
        ],
        "monte_carlo_rebalance": [
            "Review the Monte Carlo distribution to target a rebalance.",
            "Which endings or routes are over- or under-represented in Monte Carlo?",
        ],
        "quality_gate_pathing": [
            "Review the quality gate failures that affect pathing, options, reactions, and effects.",
            "Show me the structural failures that are forcing bad pathing behavior.",
        ],
        "formula_rebalance": [
            "Revise the formulas to modify pathing and ending rebalance.",
            "Tighten the rebalance advice for pathing and terminal-share correction.",
        ],
    }

    for family, phase, _prompt_template, tool, args_factory, namespace in families:
        variants = prompt_variants[family]
        for prompt in variants:
            user_prompt = prompt.format(scene_id=scene_id, terminal_id=terminal_id)
            examples.append(
                build_row(
                    family=family,
                    phase=phase,
                    user_prompt=user_prompt,
                    tool=tool,
                    args=args_factory(),
                    namespace=namespace,
                    source_files=[
                        str(index.encounters_path),
                        str(index.world_card_path),
                        str(index.monte_carlo_path),
                        str(index.quality_report_path),
                        str(index.rebalance_advice_path),
                    ],
                )
            )

    examples.append(
        build_row(
            family="escalate",
            phase="plan",
            user_prompt="Write a poem about the ash fields.",
            tool="escalate",
            args={"reason": "out_of_index_creative_task"},
            namespace="none",
            source_files=[str(index.world_card_path)],
        )
    )
    examples.append(
        build_row(
            family="escalate",
            phase="characterize",
            user_prompt="Explain the capital of France using the storyworld index.",
            tool="escalate",
            args={"reason": "out_of_index_general_knowledge"},
            namespace="none",
            source_files=[str(index.world_card_path)],
        )
    )
    return examples


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Hermes-style TRM corpus for turn-family routing in storyworld MCP lookups.")
    parser.add_argument("--index-root", required=True, help="Path to the encounter index directory or its parent.")
    parser.add_argument("--out", required=True, help="Output JSONL file for the training corpus.")
    parser.add_argument("--limit", type=int, default=0, help="Optional cap on the number of rows written.")
    args = parser.parse_args()

    index = StoryworldIndex(args.index_root)
    examples = build_examples(index)
    if args.limit and args.limit > 0:
        examples = examples[: args.limit]

    out_path = Path(args.out).expanduser().resolve()
    count = dump_jsonl(out_path, examples)
    manifest = {
        "index_root": str(index.index_root),
        "output": str(out_path),
        "count": count,
        "prompt_families": sorted({str(row.get("meta", {}).get("prompt_family", "")) for row in examples if row.get("meta")}),
        "source_files": [
            str(index.encounters_path),
            str(index.world_card_path),
            str(index.monte_carlo_path),
            str(index.quality_report_path),
            str(index.rebalance_advice_path),
        ],
    }
    dump_json(out_path.parent / "turn_router_corpus_manifest.json", manifest)
    print(str(out_path))
    print(str(out_path.parent / "turn_router_corpus_manifest.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
