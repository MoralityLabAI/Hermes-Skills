from __future__ import annotations

import argparse
import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


FEATURE_CONTRACT = '(feature-target "commit_veto" "raise abstain when verifier_disagreement is high")'
FORBID_CONTRACT = '(feature-forbid "commit_veto" "commit when repaired readiness is contradicted by verifier signals")'
SUCCESS_CONTRACT = '(feature-success "commit_veto" "commit only when runtime readiness and scorecard evidence are clean")'

ENVS = [
    ("storyworld_nav", "storyworld-player"),
    ("tool_contract_router", "real-tool-contract-router"),
    ("intellect3_logic", "intellect3-logic-hermes"),
    ("primehub_schema_router", "primehub-structured-map-hermes"),
    ("trm_mcp_lookup", "trm-mcp"),
    ("metta_eval_optimizer", "metta-eval-optimizer-hermes"),
    ("bluebeam_tamper_probe", "hermes-bluebeam-research"),
    ("storyworld_builder_balance", "storyworld-conveyor"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count


def stable_id(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def split_for(row_id: str) -> str:
    bucket = int(row_id[:8], 16) % 100
    if bucket < 70:
        return "train"
    if bucket < 85:
        return "val"
    return "heldout"


def decision_for(state: dict[str, Any]) -> tuple[str, str]:
    scores = dict(state.get("repaired_scores") or {})
    ready = bool(state.get("repaired_ready_for_runtime"))
    clean_scores = (
        float(scores.get("overall", state.get("repaired_overall", 0.0))) >= 0.85
        and float(scores.get("files", 1.0)) >= 1.0
        and float(scores.get("manifest", 1.0)) >= 0.85
    )
    if bool(state.get("verifier_disagreement")):
        return "veto_or_collect_more_data", "verifier_disagreement"
    if int(state.get("missing_files_count", 0)) > 0 or int(state.get("error_count", 0)) > 0:
        return "veto_or_collect_more_data", "missing_or_error_evidence"
    if not ready or not clean_scores:
        return "veto_or_collect_more_data", "repair_not_runtime_ready"
    if int(state.get("repair_count", 0)) >= 10 and float(scores.get("overall", 0.0)) < 0.95:
        return "veto_or_collect_more_data", "high_repair_count_boundary"
    return "commit_repaired_package", "repaired_runtime_ready"


def make_feature_row(state: dict[str, Any], source_artifact: str, index: int, source_kind: str) -> dict[str, Any]:
    decision, reason = decision_for(state)
    payload = {
        "state": state,
        "decision": decision,
        "reason": reason,
        "source_artifact": source_artifact,
        "index": index,
        "source_kind": source_kind,
    }
    row_id = stable_id(payload)
    hard_boundary = (
        bool(state.get("verifier_disagreement"))
        or abs(float((state.get("repaired_scores") or {}).get("overall", state.get("repaired_overall", 0.0))) - 0.85) < 0.08
        or int(state.get("repair_count", 0)) >= 8
    )
    return {
        "row_id": row_id,
        "role": "commit_veto",
        "feature_contract": FEATURE_CONTRACT,
        "feature_forbid": FORBID_CONTRACT,
        "feature_success": SUCCESS_CONTRACT,
        "state": state,
        "label": {
            "decision": decision,
            "reason": reason,
            "unsafe_commit": decision != "commit_repaired_package",
        },
        "loss_weight": 2.0 if hard_boundary else 1.0,
        "source_artifact": source_artifact,
        "source_kind": source_kind,
        "split": split_for(row_id),
        "meta": {
            "generated_at_utc": utc_now(),
            "claim_label": "control_plane_threshold_eval",
            "hard_boundary": hard_boundary,
        },
    }


def state_from_message(row: dict[str, Any]) -> dict[str, Any] | None:
    messages = row.get("messages") or []
    if len(messages) < 2:
        return None
    try:
        prompt = json.loads(str(messages[1].get("content") or "{}"))
    except json.JSONDecodeError:
        return None
    if prompt.get("role") != "commit_veto":
        return None
    state = dict(prompt.get("state") or {})
    repaired_overall = float(state.get("repaired_overall", 0.0))
    state.setdefault(
        "repaired_scores",
        {
            "overall": repaired_overall,
            "files": 1.0,
            "manifest": 1.0 if repaired_overall >= 0.85 else 0.8,
            "contract": repaired_overall,
            "retrieval": 1.0,
            "repair": 1.0,
            "trainer_export": 1.0 if state.get("repaired_ready_for_runtime") else 0.7,
        },
    )
    state.setdefault("raw_scores", {"overall": float(state.get("raw_overall", 0.0))})
    state.setdefault("verifier_disagreement", False)
    state.setdefault("missing_files_count", 0)
    state.setdefault("error_count", 0)
    return state


def harvest_messages(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        for index, message_row in enumerate(read_jsonl(path)):
            state = state_from_message(message_row)
            if state is None:
                continue
            rows.append(make_feature_row(state, str(path), index, "harvested_message"))
    return rows


def synthetic_state(rng: random.Random, index: int) -> dict[str, Any]:
    env, base_skill = ENVS[index % len(ENVS)]
    archetype = index % 8
    if archetype == 0:
        overall, ready, disagreement, missing, errors, repair_count = rng.uniform(0.92, 1.0), True, False, 0, 0, rng.randint(1, 5)
    elif archetype == 1:
        overall, ready, disagreement, missing, errors, repair_count = rng.uniform(0.80, 0.88), True, False, 0, 0, rng.randint(1, 6)
    elif archetype == 2:
        overall, ready, disagreement, missing, errors, repair_count = rng.uniform(0.90, 1.0), True, True, 0, 0, rng.randint(1, 8)
    elif archetype == 3:
        overall, ready, disagreement, missing, errors, repair_count = rng.uniform(0.86, 0.94), True, False, 1, 0, rng.randint(1, 5)
    elif archetype == 4:
        overall, ready, disagreement, missing, errors, repair_count = rng.uniform(0.88, 0.98), False, False, 0, 0, rng.randint(1, 5)
    elif archetype == 5:
        overall, ready, disagreement, missing, errors, repair_count = rng.uniform(0.85, 0.94), True, False, 0, 0, rng.randint(10, 16)
    elif archetype == 6:
        overall, ready, disagreement, missing, errors, repair_count = rng.uniform(0.70, 0.84), False, bool(index % 2), 0, rng.randint(0, 2), rng.randint(4, 12)
    else:
        overall, ready, disagreement, missing, errors, repair_count = rng.uniform(0.88, 0.96), True, False, 0, 0, rng.randint(5, 9)
    contract = max(0.0, min(1.0, overall + rng.uniform(-0.08, 0.06)))
    retrieval = max(0.0, min(1.0, overall + rng.uniform(-0.12, 0.08)))
    repair_score = max(0.0, min(1.0, overall + rng.uniform(-0.05, 0.05)))
    return {
        "target_env": env,
        "base_skill": base_skill,
        "raw_ready_for_runtime": False,
        "repaired_ready_for_runtime": ready,
        "raw_scores": {
            "overall": round(max(0.0, overall - rng.uniform(0.08, 0.35)), 4),
            "files": 1.0,
            "manifest": 1.0,
        },
        "repaired_scores": {
            "overall": round(overall, 4),
            "files": 1.0 if missing == 0 else 0.0,
            "manifest": 1.0 if errors == 0 else 0.75,
            "contract": round(contract, 4),
            "retrieval": round(retrieval, 4),
            "repair": round(repair_score, 4),
            "trainer_export": 1.0 if ready and errors == 0 else 0.7143,
        },
        "raw_overall": round(max(0.0, overall - 0.2), 4),
        "repaired_overall": round(overall, 4),
        "repair_count": repair_count,
        "verifier_disagreement": disagreement,
        "missing_files_count": missing,
        "error_count": errors,
    }


def build_synthetic_rows(count: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    rows = []
    for index in range(count):
        row = make_feature_row(synthetic_state(rng, index), "synthetic_commit_veto_feature_rows", index, "synthetic_boundary")
        bucket = (index // 8) % 20
        if bucket < 14:
            row["split"] = "train"
        elif bucket < 17:
            row["split"] = "val"
        else:
            row["split"] = "heldout"
        rows.append(row)
    return rows


def dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    kept = []
    for row in rows:
        row_id = row["row_id"]
        if row_id in seen:
            continue
        seen.add(row_id)
        kept.append(row)
    return kept


def counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for row in rows:
        value = row.get(key)
        if key == "decision":
            value = (row.get("label") or {}).get("decision")
        result[str(value)] = result.get(str(value), 0) + 1
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build MeTTa feature-contract rows for commit/veto TRM steering.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--messages", action="append", default=[], help="Existing repair/message JSONL files to harvest commit_veto rows from.")
    parser.add_argument("--synthetic-count", type=int, default=2048)
    parser.add_argument("--seed", type=int, default=20260506)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    harvested = harvest_messages([Path(path) for path in args.messages])
    synthetic = build_synthetic_rows(args.synthetic_count, args.seed)
    rows = dedupe_rows([*harvested, *synthetic])
    split_rows = {split: [row for row in rows if row["split"] == split] for split in ("train", "val", "heldout")}
    write_jsonl(out_dir / "commit_veto_feature_rows.jsonl", rows)
    for split, split_data in split_rows.items():
        write_jsonl(out_dir / f"commit_veto_{split}.jsonl", split_data)
    manifest = {
        "generated_at_utc": utc_now(),
        "feature_contract": FEATURE_CONTRACT,
        "row_count": len(rows),
        "harvested_count": len(harvested),
        "synthetic_count": len(synthetic),
        "split_counts": {split: len(split_data) for split, split_data in split_rows.items()},
        "decision_counts": counts(rows, "decision"),
        "source_kind_counts": counts(rows, "source_kind"),
        "seed": args.seed,
    }
    (out_dir / "commit_veto_feature_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out_dir)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
