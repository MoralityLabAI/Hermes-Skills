"""Optimize the Intellect-3 math_skill_trm router from existing receipts.

This is an offline receipt replay. It does not call a model; it evaluates which
already-recorded candidate the router should have committed:

- current_final: the published math_skill_trm final action
- math_skill: the plain math skill candidate inside the TRM arm
- trm_skill: the TRM-conditioned candidate inside the TRM arm
- retrieval_threshold: choose trm_skill when retrieval similarity is above a threshold
- generic_retrieval_guard: use a generic-skill agreement guard; costs a third call live

The purpose is to tune the control-plane policy before rerunning the expensive
benchmark.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
DEFAULT_SOURCE = Path(r"C:\projects\trm_observability_harness\data\qwen27b_intellect3_math_hybrid_200\predictions.jsonl")
DEFAULT_OUT = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "intellect3_math_optimized_trm_router"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Optimize math_skill_trm routing from existing receipts.")
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


def parse_int(value: Any) -> int | None:
    match = re.search(r"[-+]?\d+", str(value or ""))
    if not match:
        return None
    return int(match.group(0))


def rel_distance(predicted: int | None, expected: int | None) -> float | None:
    if predicted is None or expected is None:
        return None
    return abs(predicted - expected) / max(1, abs(expected))


def candidate_table(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_row_arm = {(str(record.get("row_id")), str(record.get("arm"))): record for record in records}
    rows: list[dict[str, Any]] = []
    for record in records:
        if record.get("arm") != "math_skill_trm":
            continue
        row_id = str(record.get("row_id"))
        generic_record = by_row_arm.get((row_id, "generic_skill")) or {}
        trm = record.get("trm") or {}
        expected = parse_int(record.get("expected_action"))
        row = {
            "row_id": row_id,
            "expected": expected,
            "current_final": parse_int((record.get("final") or {}).get("action")),
            "math_skill": parse_int(trm.get("math_skill_action")),
            "trm_skill": parse_int(trm.get("trm_skill_action")),
            "retrieved": parse_int(trm.get("retrieved_action")),
            "generic_skill": parse_int((generic_record.get("final") or {}).get("action")),
            "retrieval_similarity": float(trm.get("retrieval_similarity") or 0.0),
            "current_route_source": trm.get("route_source"),
        }
        for name in ("current_final", "math_skill", "trm_skill", "retrieved", "generic_skill"):
            row[f"{name}_exact"] = row[name] == expected
            row[f"{name}_relative_distance"] = rel_distance(row[name], expected)
        rows.append(row)
    return rows


def exact_rate(rows: list[dict[str, Any]], key: str) -> float:
    return round(sum(1 for row in rows if row.get(f"{key}_exact")) / max(1, len(rows)), 6)


def avg_rel_distance(rows: list[dict[str, Any]], key: str) -> float:
    values = [float(row[f"{key}_relative_distance"]) for row in rows if row.get(f"{key}_relative_distance") is not None]
    return round(sum(values) / max(1, len(values)), 6)


def choose_threshold(rows: list[dict[str, Any]], train_ids: set[str]) -> dict[str, Any]:
    train = [row for row in rows if row["row_id"] in train_ids]
    candidates: list[dict[str, Any]] = []
    for threshold_int in range(0, 101):
        threshold = threshold_int / 100.0
        hits = 0
        avg_dist_total = 0.0
        for row in train:
            pred = row["trm_skill"] if row["retrieval_similarity"] >= threshold else row["math_skill"]
            hits += pred == row["expected"]
            avg_dist_total += rel_distance(pred, row["expected"]) or 0.0
        candidates.append(
            {
                "threshold": threshold,
                "train_exact": hits,
                "train_exact_rate": round(hits / max(1, len(train)), 6),
                "train_avg_relative_distance": round(avg_dist_total / max(1, len(train)), 6),
            }
        )
    return max(candidates, key=lambda item: (item["train_exact"], -item["train_avg_relative_distance"], -item["threshold"]))


def policy_eval(rows: list[dict[str, Any]], policy: str, *, threshold: float | None = None) -> dict[str, Any]:
    hits = 0
    distances: list[float] = []
    route_sources: Counter[str] = Counter()
    per_row: list[dict[str, Any]] = []
    for row in rows:
        if policy == "current_final":
            source = "current_final"
        elif policy == "math_skill":
            source = "math_skill"
        elif policy == "trm_skill":
            source = "trm_skill"
        elif policy == "retrieved":
            source = "retrieved"
        elif policy == "generic_retrieval_guard":
            source = "math_skill" if row["retrieved"] is not None and row["retrieved"] == row["generic_skill"] else "trm_skill"
        elif policy == "retrieval_threshold":
            source = "trm_skill" if row["retrieval_similarity"] >= float(threshold or 0.0) else "math_skill"
        else:
            raise ValueError(f"unknown policy: {policy}")
        predicted = row[source]
        exact = predicted == row["expected"]
        distance = rel_distance(predicted, row["expected"])
        hits += int(exact)
        if distance is not None:
            distances.append(distance)
        route_sources[source] += 1
        per_row.append(
            {
                "row_id": row["row_id"],
                "expected": row["expected"],
                "source": source,
                "predicted": predicted,
                "exact": exact,
                "relative_distance": round(distance, 6) if distance is not None else None,
                "retrieval_similarity": row["retrieval_similarity"],
                "current_final": row["current_final"],
                "math_skill": row["math_skill"],
                "trm_skill": row["trm_skill"],
                "retrieved": row["retrieved"],
                "generic_skill": row["generic_skill"],
            }
        )
    return {
        "policy": policy,
        "threshold": threshold,
        "rows": len(rows),
        "exact_count": hits,
        "exact_rate": round(hits / max(1, len(rows)), 6),
        "avg_relative_distance": round(sum(distances) / max(1, len(distances)), 6),
        "route_sources": dict(route_sources),
        "rows_detail": per_row,
    }


def split_ids(rows: list[dict[str, Any]]) -> tuple[set[str], set[str]]:
    ordered = sorted(row["row_id"] for row in rows)
    train = {row_id for idx, row_id in enumerate(ordered) if idx % 2 == 0}
    test = set(ordered) - train
    return train, test


def summarize(rows: list[dict[str, Any]], source: Path) -> dict[str, Any]:
    train_ids, test_ids = split_ids(rows)
    threshold = choose_threshold(rows, train_ids)
    policies = {
        "current_final": policy_eval(rows, "current_final"),
        "math_skill": policy_eval(rows, "math_skill"),
        "trm_skill": policy_eval(rows, "trm_skill"),
        "retrieved": policy_eval(rows, "retrieved"),
        "generic_retrieval_guard": policy_eval(rows, "generic_retrieval_guard"),
        "retrieval_threshold": policy_eval(rows, "retrieval_threshold", threshold=float(threshold["threshold"])),
    }
    train_policies = {
        name: policy_eval([row for row in rows if row["row_id"] in train_ids], name, threshold=policies[name].get("threshold"))
        for name in policies
    }
    test_policies = {
        name: policy_eval([row for row in rows if row["row_id"] in test_ids], name, threshold=policies[name].get("threshold"))
        for name in policies
    }
    deltas = {
        name: round(data["exact_rate"] - policies["current_final"]["exact_rate"], 6)
        for name, data in policies.items()
    }
    return {
        "env_id": "intellect3_math_optimized_trm_router",
        "source_path": str(source),
        "generated_at_utc": utc_now(),
        "rows": len(rows),
        "candidate_exact_rates": {
            "current_final": exact_rate(rows, "current_final"),
            "math_skill": exact_rate(rows, "math_skill"),
            "trm_skill": exact_rate(rows, "trm_skill"),
            "retrieved": exact_rate(rows, "retrieved"),
            "generic_skill": exact_rate(rows, "generic_skill"),
        },
        "candidate_avg_relative_distance": {
            "current_final": avg_rel_distance(rows, "current_final"),
            "math_skill": avg_rel_distance(rows, "math_skill"),
            "trm_skill": avg_rel_distance(rows, "trm_skill"),
            "retrieved": avg_rel_distance(rows, "retrieved"),
            "generic_skill": avg_rel_distance(rows, "generic_skill"),
        },
        "selected_threshold_from_train": threshold,
        "policies": policies,
        "train_policies": train_policies,
        "test_policies": test_policies,
        "deltas_vs_current_final": deltas,
        "recommendation": (
            "Use `math_trm_route_policy: always_trm` for the next live rerun. The recorded TRM-conditioned "
            "candidate is exact on more rows than the current keyword-routed final action. The optional "
            "`generic_retrieval_guard` policy has a slightly higher offline exact rate but costs a third model call."
        ),
    }


def fmt(value: Any) -> str:
    return f"{float(value):.4f}"


def render_md(summary: dict[str, Any]) -> str:
    lines = [
        "# Intellect-3 Math Optimized TRM Router",
        "",
        f"Source: `{summary['source_path']}`",
        f"Generated: `{summary['generated_at_utc']}`",
        "",
        "MeTTa contract: [`intellect3_math_optimized_router_contract.metta`](<intellect3_math_optimized_router_contract.metta>)",
        "",
        summary["recommendation"],
        "",
        "## Candidate Scores",
        "",
        "| Candidate | Exact | Avg Relative Distance | Delta Vs Current |",
        "| --- | ---: | ---: | ---: |",
    ]
    current = summary["candidate_exact_rates"]["current_final"]
    for name in ("current_final", "math_skill", "trm_skill", "retrieved", "generic_skill"):
        lines.append(
            f"| `{name}` | {fmt(summary['candidate_exact_rates'][name])} | "
            f"{fmt(summary['candidate_avg_relative_distance'][name])} | "
            f"{summary['candidate_exact_rates'][name] - current:+.4f} |"
        )
    lines.extend(
        [
            "",
            "## Policy Replay",
            "",
            "| Policy | Threshold | Exact Count | Exact Rate | Avg Relative Distance | Route Sources | Delta Vs Current |",
            "| --- | ---: | ---: | ---: | ---: | --- | ---: |",
        ]
    )
    for name, data in summary["policies"].items():
        route_sources = ", ".join(f"{key}:{value}" for key, value in data["route_sources"].items())
        threshold = "-" if data.get("threshold") is None else fmt(data["threshold"])
        lines.append(
            f"| `{name}` | {threshold} | {data['exact_count']} | {fmt(data['exact_rate'])} | "
            f"{fmt(data['avg_relative_distance'])} | {route_sources} | {summary['deltas_vs_current_final'][name]:+.4f} |"
        )
    lines.extend(
        [
            "",
            "## Train/Test Check",
            "",
            f"Threshold selected on alternating train rows: `{summary['selected_threshold_from_train']['threshold']:.2f}`.",
            "",
            "| Policy | Train Exact | Test Exact |",
            "| --- | ---: | ---: |",
        ]
    )
    for name in summary["policies"]:
        lines.append(
            f"| `{name}` | {fmt(summary['train_policies'][name]['exact_rate'])} | {fmt(summary['test_policies'][name]['exact_rate'])} |"
        )
    lines.extend(
        [
            "",
            "## Rows Changed By Recommended Policy",
            "",
            "| Row | Expected | Current | TRM Skill | Retrieved | Generic | TRM Exact | Similarity |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
        ]
    )
    for row in summary["policies"]["trm_skill"]["rows_detail"]:
        if row["trm_skill"] == row["current_final"]:
            continue
        lines.append(
            f"| `{row['row_id']}` | {row['expected']} | {row['current_final']} | {row['trm_skill']} | "
            f"{row['retrieved']} | {row['generic_skill']} | {row['exact']} | {fmt(row['retrieval_similarity'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_metta_contract() -> str:
    return "\n".join(
        [
            ";; Intellect-3 math optimized TRM router contract.",
            "(= env_id intellect3_math_optimized_trm_router)",
            "(= stage_order (parse_candidates compare_trm_candidate route_commit audit_regret))",
            "(= metric_exact_rate answer_exact_match_rate)",
            "(= metric_relative_distance abs_error_div_max_abs_expected)",
            "(= gate_candidate_parse TRM_PARSE_INTEGER_CANDIDATES)",
            "(= gate_route_policy TRM_ROUTE_TRM_CANDIDATE)",
            "(= recommended_policy always_trm)",
            "(= optional_policy generic_retrieval_guard)",
            "(= fallback_policy retrieval_similarity_threshold)",
            "(= failure_taxonomy (bad_math_candidate bad_trm_candidate route_regret retrieval_overfit numeric_scale_error))",
            "",
        ]
    )


def main() -> int:
    args = parse_args()
    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = candidate_table(load_jsonl(source))
    summary = summarize(rows, source)
    (out_dir / "math_skill_trm_optimized_router.results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out_dir / "math_skill_trm_optimized_router.results.md").write_text(render_md(summary), encoding="utf-8")
    (out_dir / "intellect3_math_optimized_router_contract.metta").write_text(render_metta_contract(), encoding="utf-8")
    print(out_dir / "math_skill_trm_optimized_router.results.md")
    print(
        json.dumps(
            {
                "current_final": summary["policies"]["current_final"]["exact_rate"],
                "recommended_trm_skill": summary["policies"]["trm_skill"]["exact_rate"],
                "generic_retrieval_guard": summary["policies"]["generic_retrieval_guard"]["exact_rate"],
                "delta": summary["deltas_vs_current_final"]["trm_skill"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
