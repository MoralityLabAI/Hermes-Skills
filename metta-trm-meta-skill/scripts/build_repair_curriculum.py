from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ENV_SPECS = [
    ("storyworld_nav", "storyworld-player"),
    ("tool_contract_router", "real-tool-contract-router"),
    ("intellect3_logic", "intellect3-logic-hermes"),
    ("primehub_schema_router", "primehub-structured-map-hermes"),
    ("trm_mcp_lookup", "trm-mcp"),
    ("metta_eval_optimizer", "metta-eval-optimizer-hermes"),
]

ENV_VALUE_HEADS = [
    "goal",
    "answer-shape",
    "constraint",
    "forbid",
    "minimal-example",
    "summary",
    "query-cue",
    "retrieval-priority",
    "validation-path",
    "failure-mode",
    "repair-hint",
    "trace-label",
]

UNSUPPORTED_HEADS = [
    "validator-update",
    "commit_veto_update",
    "route-policy",
    "repair-policy",
    "score-delta",
    "runtime-ready",
]

VALUE_FRAGMENTS = [
    "exact legal action gate",
    "env aligned contract packet",
    "near miss repair cue",
    "fixed anchor scorecard",
    "commit veto ready",
    "retrieval priority signal",
    "schema validation path",
    "candidate contradiction check",
    "min edit projection",
    "MCP first useful hit",
]

SYSTEM_PROMPT = "You are a MeTTa/TRM control-plane model. Emit the direct JSON action object only. Do not wrap it in action/params. Do not output hidden reasoning."


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def quote(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def atom(head: str, *args: Any) -> str:
    return "(" + " ".join([head, *[quote(arg) for arg in args]]) + ")"


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def row_to_messages(row: dict[str, Any]) -> dict[str, Any]:
    action = dict(row["action"])
    prompt_payload = {
        "role": row["role"],
        "state": row["state"],
        "tools": row.get("tools", []),
        "output_contract": {
            "format": "direct_json_action_object",
            "required_keys": sorted(action),
            "forbid": ["tool_call_wrapper", "action_params_wrapper", "hidden_reasoning"],
        },
    }
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(prompt_payload, ensure_ascii=False, sort_keys=True)},
            {"role": "assistant", "content": json.dumps(action, ensure_ascii=False, sort_keys=True)},
        ],
        "meta": {**row["meta"], "source_format": "metta_trm_meta_synthetic_curriculum", "role": row["role"]},
    }


def make_repair_row(env: str, base_skill: str, repair_type: str, head: str, values: list[str], index: int) -> dict[str, Any]:
    if repair_type == "env_arg_inserted":
        raw_atom = atom(head, *values)
        repaired_atom = atom(head, env, " ".join(values))
    elif repair_type == "env_arg_reordered":
        raw_atom = atom(head, values[0], env, *values[1:])
        repaired_atom = atom(head, env, " ".join(values))
    elif repair_type == "env_wrapper_projected":
        raw_atom = atom("env", env, head, *values)
        repaired_atom = atom(head, env, " ".join(values))
    elif repair_type == "unsupported_head_projected":
        unsupported = UNSUPPORTED_HEADS[index % len(UNSUPPORTED_HEADS)]
        raw_atom = atom(unsupported, env, *values)
        projected_head = "repair-hint" if "repair" in unsupported else "trace-label"
        if "validator" in unsupported:
            projected_head = "validator-note"
        repaired_atom = atom(projected_head, env, f"{unsupported}: {' '.join(values)}")
    elif repair_type == "wrapped_single_atom":
        raw_atom = f'{head} {quote(env)} {quote(" ".join(values))}'
        repaired_atom = atom(head, env, " ".join(values))
    else:
        raise ValueError(f"unknown repair_type: {repair_type}")
    scores_before = {
        "files": 1.0,
        "syntax": 0.85 if repair_type in {"unsupported_head_projected", "wrapped_single_atom"} else 1.0,
        "manifest": 1.0,
        "contract": 0.5 if head in {"goal", "answer-shape", "summary", "constraint", "forbid", "minimal-example", "validation-path"} else 1.0,
        "retrieval": 0.5 if head in {"query-cue", "retrieval-priority"} else 1.0,
        "repair": 0.5 if head in {"failure-mode", "repair-hint", "trace-label"} else 1.0,
        "trainer_export": 0.7143,
        "overall": 0.78,
    }
    return {
        "role": "metta_syntax_repair",
        "state": {
            "raw_atom": raw_atom,
            "source_file": "contracts.metta" if head in {"goal", "answer-shape", "summary", "constraint", "forbid", "minimal-example", "validation-path"} else "failure_modes.metta",
            "line_no": (index % 9) + 1,
            "repair_type": repair_type,
            "target_envs": [env],
            "pre_scores": scores_before,
            "failing_components": ["syntax"] if repair_type in {"unsupported_head_projected", "wrapped_single_atom"} else ["contract"],
        },
        "tools": ["repair-packet", "verify-packet"],
        "action": {
            "accept_repair": True,
            "repair": repair_type,
            "repaired_atom": repaired_atom,
        },
        "meta": {
            "source": "synthetic_repair_curriculum",
            "package_id": f"{env}_synthetic_repair",
            "task_id": f"{env}_repair_curriculum",
            "base_skill": base_skill,
            "repair_index": index,
            "score_delta": {"overall": 0.22, "trainer_export": 0.2857},
            "generated_at_utc": utc_now(),
        },
    }


def make_verifier_row(env: str, base_skill: str, index: int) -> dict[str, Any]:
    return {
        "role": "semantic_contract_verifier",
        "state": {
            "raw_scores": {"overall": 0.78, "contract": 0.5, "trainer_export": 0.7143},
            "repaired_scores": {"overall": 1.0, "contract": 1.0, "trainer_export": 1.0},
            "raw_missing_files": [],
            "raw_manifest_missing": [],
            "raw_error_count": 0,
            "repair_count": 2 + (index % 4),
        },
        "tools": ["verify-packet", "repair-packet"],
        "action": {
            "verdict": "runtime_ready",
            "score_delta": {"overall": 0.22, "contract": 0.5, "trainer_export": 0.2857},
            "failing_components_after_repair": [],
        },
        "meta": {
            "source": "synthetic_repair_curriculum",
            "package_id": f"{env}_synthetic_repair",
            "task_id": f"{env}_verifier_curriculum",
            "base_skill": base_skill,
            "generated_at_utc": utc_now(),
        },
    }


def make_commit_row(env: str, base_skill: str, index: int) -> dict[str, Any]:
    ready = index % 5 != 0
    return {
        "role": "commit_veto",
        "state": {
            "raw_ready_for_runtime": False,
            "repaired_ready_for_runtime": ready,
            "raw_overall": 0.78,
            "repaired_overall": 1.0 if ready else 0.82,
            "repair_count": 2 + (index % 4),
        },
        "tools": ["verify-packet", "export-trm-rows"],
        "action": {
            "decision": "commit_repaired_package" if ready else "veto_or_collect_more_data",
            "reason": "repaired_runtime_ready" if ready else "repair_not_runtime_ready",
        },
        "meta": {
            "source": "synthetic_repair_curriculum",
            "package_id": f"{env}_synthetic_repair",
            "task_id": f"{env}_commit_curriculum",
            "base_skill": base_skill,
            "generated_at_utc": utc_now(),
        },
    }


def build_rows(examples_per_env: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    repair_types = ["env_arg_inserted", "env_arg_reordered", "env_wrapper_projected", "unsupported_head_projected", "wrapped_single_atom"]
    rows: list[dict[str, Any]] = []
    index = 0
    for env, base_skill in ENV_SPECS:
        for _ in range(examples_per_env):
            head = rng.choice(ENV_VALUE_HEADS)
            repair_type = rng.choice(repair_types)
            values = rng.sample(VALUE_FRAGMENTS, k=2)
            rows.append(make_repair_row(env, base_skill, repair_type, head, values, index))
            index += 1
        for extra in range(max(2, examples_per_env // 10)):
            rows.append(make_verifier_row(env, base_skill, extra))
            rows.append(make_commit_row(env, base_skill, extra))
    rng.shuffle(rows)
    return rows


def split_rows(rows: list[dict[str, Any]], train_ratio: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cut = max(1, min(len(rows) - 1, int(len(rows) * train_ratio)))
    return rows[:cut], rows[cut:]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a synthetic MeTTa repair/control-plane curriculum.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--examples-per-env", type=int, default=60)
    parser.add_argument("--train-ratio", type=float, default=0.85)
    parser.add_argument("--seed", type=int, default=20260505)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    rows = build_rows(args.examples_per_env, args.seed)
    messages = [row_to_messages(row) for row in rows]
    train_messages, val_messages = split_rows(messages, args.train_ratio)
    write_jsonl(out_dir / "repair_curriculum_rows.jsonl", rows)
    write_jsonl(out_dir / "repair_curriculum_messages.jsonl", messages)
    write_jsonl(out_dir / "repair_curriculum_train_messages.jsonl", train_messages)
    write_jsonl(out_dir / "repair_curriculum_val_messages.jsonl", val_messages)
    role_counts: dict[str, int] = {}
    repair_counts: dict[str, int] = {}
    for row in rows:
        role_counts[row["role"]] = role_counts.get(row["role"], 0) + 1
        if row["role"] == "metta_syntax_repair":
            repair = str(row["action"].get("repair", ""))
            repair_counts[repair] = repair_counts.get(repair, 0) + 1
    manifest = {
        "generated_at_utc": utc_now(),
        "row_count": len(rows),
        "message_count": len(messages),
        "train_count": len(train_messages),
        "val_count": len(val_messages),
        "examples_per_env": args.examples_per_env,
        "seed": args.seed,
        "role_counts": role_counts,
        "repair_counts": repair_counts,
    }
    (out_dir / "repair_curriculum_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out_dir)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

