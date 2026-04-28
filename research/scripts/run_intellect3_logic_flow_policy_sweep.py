"""Sweep MeTTa/TRM commit policies for Intellect-3 logic candidate flows.

This deterministic replay uses existing prediction receipts.  It asks which
gate-flow policy should commit among multiple skill arms and repair transforms.
It does not run a model and should be reported as post-hoc policy replay.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
SCRIPTS = ROOT / "research" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from run_intellect3_camp_gate_micro_env import (  # noqa: E402
    c_only_projection,
    cell_accuracy,
    dual_signature_projection,
    exact_match,
    parse_grid,
    signature_pass,
)


DEFAULT_SOURCE = Path(r"C:\projects\trm_observability_harness\data\qwen27b_intellect3_logic_hybrid_200\predictions.jsonl")
DEFAULT_OUT = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "intellect3_logic_flow_policy_sweep"
)
ARM_ORDER = ["logic_skill_trm", "logic_skill", "generic_skill", "vanilla"]
TRANSFORM_ORDER = ["original", "c_repair", "dual_repair"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Intellect-3 logic MeTTa/TRM flow policy sweep.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def hamming(a: list[list[str]] | None, b: list[list[str]] | None) -> int | None:
    if a is None or b is None or len(a) != len(b) or any(len(x) != len(y) for x, y in zip(a, b)):
        return None
    return sum(1 for r in range(len(a)) for c in range(len(a[0])) if a[r][c] != b[r][c])


def grid_text(grid: list[list[str]] | None) -> str:
    if grid is None:
        return ""
    return "\n".join("".join(row) for row in grid)


def build_candidates(record: dict[str, Any]) -> list[dict[str, Any]]:
    expected = parse_grid(record.get("expected_action"))
    final = record.get("final") or {}
    original = parse_grid(final.get("action") or final.get("raw_action") or final.get("raw_text"))
    c_repaired = c_only_projection(original, expected) if original is not None and expected is not None else None
    dual_repaired = dual_signature_projection(original, expected) if original is not None and expected is not None else None
    items = [
        ("original", original),
        ("c_repair", c_repaired),
        ("dual_repair", dual_repaired),
    ]
    candidates: list[dict[str, Any]] = []
    for transform, grid in items:
        if grid is None:
            continue
        candidates.append(
            {
                "row_id": str(record.get("row_id")),
                "source_arm": str(record.get("arm")),
                "transform": transform,
                "grid": grid,
                "grid_text": grid_text(grid),
                "edit_distance": hamming(original, grid),
                "exact": exact_match(grid, expected),
                "cell_accuracy": round(cell_accuracy(grid, expected), 6),
                "t_signature_pass": bool(expected is not None and signature_pass(grid, expected, "T")),
                "c_signature_pass": bool(expected is not None and signature_pass(grid, expected, "C")),
            }
        )
    return candidates


def candidate_rank(candidate: dict[str, Any]) -> tuple[int, int, int, str]:
    edit = candidate.get("edit_distance")
    edit_value = 10**9 if edit is None else int(edit)
    arm_value = ARM_ORDER.index(candidate["source_arm"]) if candidate["source_arm"] in ARM_ORDER else len(ARM_ORDER)
    transform_value = TRANSFORM_ORDER.index(candidate["transform"]) if candidate["transform"] in TRANSFORM_ORDER else len(TRANSFORM_ORDER)
    return (edit_value, transform_value, arm_value, candidate["grid_text"])


def select_policy(policy: str, candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not candidates:
        return None
    by_arm = defaultdict(list)
    for candidate in candidates:
        by_arm[candidate["source_arm"]].append(candidate)

    if policy == "logic_trm_original":
        return first_transform(by_arm.get("logic_skill_trm", []), "original")
    if policy == "logic_trm_c_repair_if_c_fail":
        original = first_transform(by_arm.get("logic_skill_trm", []), "original")
        c_repair = first_transform(by_arm.get("logic_skill_trm", []), "c_repair")
        if original and original["c_signature_pass"]:
            return original
        return c_repair or original
    if policy == "logic_trm_dual_repair_if_any_sig_fail":
        original = first_transform(by_arm.get("logic_skill_trm", []), "original")
        dual = first_transform(by_arm.get("logic_skill_trm", []), "dual_repair")
        if original and original["t_signature_pass"] and original["c_signature_pass"]:
            return original
        return dual or original
    if policy == "multi_arm_original_signature_pass":
        originals = [
            item
            for item in candidates
            if item["transform"] == "original" and item["t_signature_pass"] and item["c_signature_pass"]
        ]
        return sorted(originals, key=candidate_rank)[0] if originals else None
    if policy == "multi_arm_min_edit_c_repair":
        repaired = [item for item in candidates if item["transform"] == "c_repair" and item["c_signature_pass"]]
        return sorted(repaired, key=candidate_rank)[0] if repaired else None
    if policy == "multi_arm_min_edit_dual_repair":
        repaired = [
            item
            for item in candidates
            if item["transform"] == "dual_repair" and item["t_signature_pass"] and item["c_signature_pass"]
        ]
        return sorted(repaired, key=candidate_rank)[0] if repaired else None
    if policy == "signature_first_then_dual":
        signature = select_policy("multi_arm_original_signature_pass", candidates)
        return signature or select_policy("multi_arm_min_edit_dual_repair", candidates)
    raise ValueError(f"unknown policy {policy}")


def first_transform(candidates: list[dict[str, Any]], transform: str) -> dict[str, Any] | None:
    for candidate in candidates:
        if candidate["transform"] == transform:
            return candidate
    return None


def run_policy_sweep(records: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record.get("row_id"))].append(record)
    policies = [
        "logic_trm_original",
        "logic_trm_c_repair_if_c_fail",
        "logic_trm_dual_repair_if_any_sig_fail",
        "multi_arm_original_signature_pass",
        "multi_arm_min_edit_c_repair",
        "multi_arm_min_edit_dual_repair",
        "signature_first_then_dual",
    ]
    rows: list[dict[str, Any]] = []
    training_rows: list[dict[str, Any]] = []
    for row_id, row_records in sorted(grouped.items(), key=lambda item: item[0]):
        candidates: list[dict[str, Any]] = []
        for record in row_records:
            candidates.extend(build_candidates(record))
        for policy in policies:
            selected = select_policy(policy, candidates)
            result = {
                "row_id": row_id,
                "policy": policy,
                "selected": selected is not None,
                "source_arm": selected.get("source_arm") if selected else "",
                "transform": selected.get("transform") if selected else "abstain",
                "edit_distance": selected.get("edit_distance") if selected else None,
                "exact": bool(selected and selected["exact"]),
                "cell_accuracy": float(selected["cell_accuracy"]) if selected else 0.0,
                "t_signature_pass": bool(selected and selected["t_signature_pass"]),
                "c_signature_pass": bool(selected and selected["c_signature_pass"]),
            }
            rows.append(result)
            training_rows.append(make_training_row(result))
    return {
        "generated_at_utc": utc_now(),
        "source_rows": len(records),
        "problem_count": len(grouped),
        "policies": summarize(rows),
        "rows": rows,
        "training_rows": training_rows,
        "read": (
            "This replay tests commit policies over existing candidate arms. "
            "It measures whether MeTTa/TRM flow control should commit original grids, C-only projections, "
            "dual-signature projections, or abstain."
        ),
    }


def make_training_row(result: dict[str, Any]) -> dict[str, Any]:
    if not result["selected"]:
        label = "abstain_no_candidate"
    elif result["exact"]:
        label = "commit_success"
    elif result["t_signature_pass"] and result["c_signature_pass"]:
        label = "signature_pass_cell_fail"
    else:
        label = "signature_fail"
    return {
        "state": {
            "row_id": result["row_id"],
            "policy": result["policy"],
            "source_arm": result["source_arm"],
            "transform": result["transform"],
            "edit_distance": result["edit_distance"],
        },
        "tools": [
            {"name": "route_gate", "result": "hard_reasoning_logic"},
            {"name": "validate_gate", "result": label},
            {"name": "repair_gate", "result": result["transform"]},
            {"name": "commit_gate", "result": "commit" if result["selected"] else "abstain"},
        ],
        "action": "commit" if result["selected"] else "abstain",
        "target_action": "commit" if result["exact"] else "reject_or_repair",
        "bucket": "exact_positive" if result["exact"] else "near_miss",
        "supervision_weight": 2.0 if result["exact"] else 1.0,
        "meta": {
            "source": "intellect3_logic_flow_policy_sweep",
            "learning_row_type": label,
        },
    }


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_policy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_policy[row["policy"]].append(row)
    summary: list[dict[str, Any]] = []
    for policy, policy_rows in by_policy.items():
        transforms = Counter(row["transform"] for row in policy_rows)
        arms = Counter(row["source_arm"] for row in policy_rows if row["source_arm"])
        summary.append(
            {
                "policy": policy,
                "problems": len(policy_rows),
                "selection_rate": round(sum(1 for row in policy_rows if row["selected"]) / max(1, len(policy_rows)), 6),
                "exact_rate": round(sum(1 for row in policy_rows if row["exact"]) / max(1, len(policy_rows)), 6),
                "avg_cell_accuracy": round(
                    sum(float(row["cell_accuracy"]) for row in policy_rows) / max(1, len(policy_rows)), 6
                ),
                "t_signature_pass_rate": round(
                    sum(1 for row in policy_rows if row["t_signature_pass"]) / max(1, len(policy_rows)), 6
                ),
                "c_signature_pass_rate": round(
                    sum(1 for row in policy_rows if row["c_signature_pass"]) / max(1, len(policy_rows)), 6
                ),
                "transform_counts": dict(transforms),
                "source_arm_counts": dict(arms),
            }
        )
    return sorted(summary, key=lambda item: (-item["exact_rate"], -item["avg_cell_accuracy"], item["policy"]))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def render_md(payload: dict[str, Any], source: Path) -> str:
    lines = [
        "# Intellect-3 Logic Flow Policy Sweep",
        "",
        f"Source: `{source}`",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        payload["read"],
        "",
        "Evidence class: `post_hoc_projection`.",
        "",
        "## Policy Summary",
        "",
        "| Policy | Selection | Exact | Cell Acc | T Sig | C Sig | Transforms | Source Arms |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in payload["policies"]:
        lines.append(
            f"| `{row['policy']}` | {row['selection_rate']:.4f} | {row['exact_rate']:.4f} | "
            f"{row['avg_cell_accuracy']:.4f} | {row['t_signature_pass_rate']:.4f} | "
            f"{row['c_signature_pass_rate']:.4f} | {fmt_counts(row['transform_counts'])} | "
            f"{fmt_counts(row['source_arm_counts'])} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- `logic_trm_original` is the current single-arm TRM baseline.",
            "- `logic_trm_c_repair_if_c_fail` tests the narrow camp-placement repair gate.",
            "- `logic_trm_dual_repair_if_any_sig_fail` tests the coupled tent/camp signature gate.",
            "- `multi_arm_*` policies test whether parallel skill candidates can improve commit selection without another model call.",
            "- If multi-arm policies win, the next live benchmark should spend extra calls on candidate diversity and let MeTTa/TRM own the commit gate.",
            "",
        ]
    )
    return "\n".join(lines)


def fmt_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "-"
    return ", ".join(f"`{key}`:{value}" for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def main() -> int:
    args = parse_args()
    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = run_policy_sweep(load_jsonl(source))
    json_path = out_dir / "intellect3_logic_flow_policy_sweep.results.json"
    md_path = out_dir / "intellect3_logic_flow_policy_sweep.results.md"
    rows_path = out_dir / "intellect3_logic_flow_policy_sweep.rows.jsonl"
    trm_path = out_dir / "pure_trm_flow_policy_rows.jsonl"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(render_md(payload, source), encoding="utf-8")
    write_jsonl(rows_path, payload["rows"])
    write_jsonl(trm_path, payload["training_rows"])
    print(md_path)
    print(json_path)
    print(trm_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
