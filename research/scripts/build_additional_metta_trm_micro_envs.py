"""Build additional deterministic MeTTa/TRM micro-env artifacts.

The generated envs are receipt replays, not model runs:

- Intellect-3 math answer-manifold: numeric answer parsing, error taxonomy,
  and baseline-vs-TRM row status.
- PsychoBench item-vector: BFI response contract checks, item deltas, and
  subscale-level movement between without/with MeTTa runs.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
STUDY = ROOT / "research" / "studies" / "2026-04-22-metta-trm-hermes-pipeline"
ARTIFACTS = STUDY / "artifacts"
DEFAULT_MATH_SOURCE = Path(r"C:\projects\trm_observability_harness\data\qwen27b_intellect3_math_hybrid_200\predictions.jsonl")
DEFAULT_PSYCHO_WITHOUT = (
    ARTIFACTS
    / "live_eval_qwen35_9b_with_vs_without_metta_richer_packet"
    / "replays"
    / "without_metta"
    / "psycho_bench.jsonl"
)
DEFAULT_PSYCHO_WITH = (
    ARTIFACTS
    / "live_eval_qwen35_9b_with_vs_without_metta_richer_packet"
    / "replays"
    / "with_metta"
    / "psycho_bench.jsonl"
)


BFI_SUBSCALES = {
    "extraversion": {1: 1, 6: -1, 11: 1, 16: 1, 21: -1, 26: 1, 31: -1, 36: 1},
    "agreeableness": {2: -1, 7: 1, 12: -1, 17: 1, 22: 1, 27: -1, 32: 1, 37: -1, 42: 1},
    "conscientiousness": {3: 1, 8: -1, 13: 1, 18: -1, 23: -1, 28: 1, 33: 1, 38: 1, 43: -1},
    "neuroticism": {4: 1, 9: -1, 14: 1, 19: 1, 24: -1, 29: 1, 34: -1, 39: 1},
    "openness": {5: 1, 10: 1, 15: 1, 20: 1, 25: 1, 30: 1, 35: -1, 40: 1, 41: -1, 44: 1},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build additional MeTTa/TRM micro-env artifacts.")
    parser.add_argument("--math-source", default=str(DEFAULT_MATH_SOURCE))
    parser.add_argument("--psycho-without", default=str(DEFAULT_PSYCHO_WITHOUT))
    parser.add_argument("--psycho-with", default=str(DEFAULT_PSYCHO_WITH))
    parser.add_argument("--out-root", default=str(ARTIFACTS))
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def parse_first_int(text: Any) -> int | None:
    match = re.search(r"[-+]?\d+", str(text or ""))
    if not match:
        return None
    try:
        return int(match.group(0))
    except ValueError:
        return None


def classify_numeric_error(expected: int | None, predicted: int | None, raw: str) -> list[str]:
    if expected is None:
        return ["expected_parse_failure"]
    if predicted is None:
        return ["prediction_parse_failure"]
    if predicted == expected:
        return ["exact"]
    tags: list[str] = []
    diff = predicted - expected
    abs_diff = abs(diff)
    if abs_diff == 1:
        tags.append("off_by_one")
    elif abs_diff <= 5:
        tags.append("off_by_small")
    if predicted == expected * 2:
        tags.append("double")
    if expected % 2 == 0 and predicted == expected // 2:
        tags.append("half")
    if predicted == -expected:
        tags.append("negation")
    if abs(predicted) == abs(expected) and predicted != expected:
        tags.append("sign_error_abs_match")
    if str(abs(predicted))[-1:] == str(abs(expected))[-1:]:
        tags.append("same_last_digit")
    if sorted(str(abs(predicted))) == sorted(str(abs(expected))):
        tags.append("same_digit_multiset")
    if expected != 0 and predicted != 0:
        log_gap = abs(math.log10(abs(predicted)) - math.log10(abs(expected)))
        if log_gap >= 1:
            tags.append("order_of_magnitude")
    if not re.fullmatch(r"\s*[-+]?\d+\s*", raw or ""):
        tags.append("non_integer_wrapper")
    if not tags:
        tags.append("wrong_integer")
    return sorted(set(tags))


def build_math_env(source: Path, out_root: Path) -> dict[str, Any]:
    records = load_jsonl(source)
    rows: list[dict[str, Any]] = []
    for record in records:
        final = record.get("final") or {}
        raw_action = str(final.get("action") or final.get("raw_action") or final.get("raw_text") or "")
        expected = parse_first_int(record.get("expected_action"))
        predicted = parse_first_int(raw_action)
        distance = None if expected is None or predicted is None else abs(predicted - expected)
        rel_distance = None
        if distance is not None and expected is not None:
            rel_distance = distance / max(1, abs(expected))
        rows.append(
            {
                "row_id": str(record.get("row_id")),
                "arm": str(record.get("arm")),
                "expected": expected,
                "predicted": predicted,
                "exact": bool(final.get("exact_match")) or expected == predicted,
                "numeric_distance": distance,
                "relative_distance": round(rel_distance, 6) if rel_distance is not None else None,
                "tags": classify_numeric_error(expected, predicted, raw_action),
                "route_source": (record.get("trm") or {}).get("route_source"),
                "retrieval_bucket": (record.get("trm") or {}).get("retrieval_bucket"),
                "model_calls": record.get("model_calls"),
            }
        )
    arms = sorted({row["arm"] for row in rows})
    arm_summaries: dict[str, Any] = {}
    for arm in arms:
        arm_rows = [row for row in rows if row["arm"] == arm]
        failures = [row for row in arm_rows if not row["exact"]]
        tag_counts = Counter(tag for row in failures for tag in row["tags"] if tag != "exact")
        distances = [float(row["relative_distance"]) for row in arm_rows if row["relative_distance"] is not None]
        arm_summaries[arm] = {
            "rows": len(arm_rows),
            "exact_rate": round(sum(1 for row in arm_rows if row["exact"]) / max(1, len(arm_rows)), 6),
            "avg_relative_distance": round(sum(distances) / max(1, len(distances)), 6),
            "median_relative_distance": round(sorted(distances)[len(distances) // 2], 6) if distances else None,
            "failure_tag_counts": dict(tag_counts),
            "route_sources": dict(Counter(str(row["route_source"]) for row in arm_rows if row["route_source"])),
        }
    problem_rows = compare_arms(rows, baseline_arm="vanilla", compare_arm="math_skill_trm")
    summary = {
        "env_id": "intellect3_math_answer_manifold_micro_env",
        "source_path": str(source),
        "generated_at_utc": utc_now(),
        "arms": arm_summaries,
        "problem_status_counts": dict(Counter(row["status"] for row in problem_rows)),
        "problem_rows": problem_rows,
        "read": (
            "The current math TRM route is weak as a solver, but this env exposes whether future "
            "MeTTa gates should target answer parsing, small arithmetic slips, scaling errors, or route selection."
        ),
    }
    out_dir = out_root / "intellect3_math_answer_manifold_micro_env"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "intellect3_math_answer_manifold.results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out_dir / "intellect3_math_answer_manifold.results.md").write_text(render_math_md(summary), encoding="utf-8")
    (out_dir / "intellect3_math_answer_manifold_contract.metta").write_text(render_math_contract(), encoding="utf-8")
    return summary


def compare_arms(rows: list[dict[str, Any]], *, baseline_arm: str, compare_arm: str) -> list[dict[str, Any]]:
    by_key = {(row["row_id"], row["arm"]): row for row in rows}
    row_ids = sorted({row["row_id"] for row in rows})
    result: list[dict[str, Any]] = []
    for row_id in row_ids:
        baseline = by_key.get((row_id, baseline_arm))
        compare = by_key.get((row_id, compare_arm))
        if not baseline or not compare:
            continue
        status = "same"
        if not baseline["exact"] and compare["exact"]:
            status = "fixed_by_compare"
        elif baseline["exact"] and not compare["exact"]:
            status = "regressed_by_compare"
        elif not baseline["exact"] and not compare["exact"]:
            b_dist = baseline["relative_distance"]
            c_dist = compare["relative_distance"]
            if b_dist is not None and c_dist is not None and c_dist < b_dist:
                status = "partial_improvement"
            elif b_dist is not None and c_dist is not None and c_dist > b_dist:
                status = "partial_regression"
            else:
                status = "unfixed"
        result.append(
            {
                "row_id": row_id,
                "status": status,
                "baseline_expected": baseline["expected"],
                "baseline_predicted": baseline["predicted"],
                "compare_predicted": compare["predicted"],
                "baseline_exact": baseline["exact"],
                "compare_exact": compare["exact"],
                "baseline_relative_distance": baseline["relative_distance"],
                "compare_relative_distance": compare["relative_distance"],
                "compare_tags": compare["tags"],
                "compare_route_source": compare.get("route_source"),
            }
        )
    return result


def parse_psycho_action(text: str) -> dict[int, int]:
    scores: dict[int, int] = {}
    for match in re.finditer(r"(?m)^\s*(\d+)\s*:\s*([1-5])\s*$", text or ""):
        scores[int(match.group(1))] = int(match.group(2))
    return scores


def parse_observation_indexes(text: str) -> list[int]:
    indexes: list[int] = []
    for match in re.finditer(r"(?m)^(\d+):\s+.+$", text or ""):
        idx = int(match.group(1))
        if idx not in indexes:
            indexes.append(idx)
    return indexes


def subscale_scores(scores: dict[int, int]) -> dict[str, float]:
    out: dict[str, float] = {}
    for name, mapping in BFI_SUBSCALES.items():
        values: list[int] = []
        for idx, direction in mapping.items():
            if idx not in scores:
                continue
            value = scores[idx]
            values.append(value if direction == 1 else 6 - value)
        out[name] = round(sum(values) / max(1, len(values)), 6)
    return out


def build_psycho_env(without_path: Path, with_path: Path, out_root: Path) -> dict[str, Any]:
    without = load_jsonl(without_path)[0]
    with_metta = load_jsonl(with_path)[0]
    expected_indexes = parse_observation_indexes(str(without.get("observation") or ""))
    without_scores = parse_psycho_action(str(without.get("action") or ""))
    with_scores = parse_psycho_action(str(with_metta.get("action") or ""))
    expected_set = set(expected_indexes)
    changed_items = []
    for idx in expected_indexes:
        left = without_scores.get(idx)
        right = with_scores.get(idx)
        if left != right:
            changed_items.append({"index": idx, "without_metta": left, "with_metta": right, "delta": None if left is None or right is None else right - left})
    without_subscales = subscale_scores(without_scores)
    with_subscales = subscale_scores(with_scores)
    subscale_deltas = {
        name: round(with_subscales[name] - without_subscales[name], 6)
        for name in sorted(set(without_subscales) | set(with_subscales))
    }
    summary = {
        "env_id": "psycho_bench_item_vector_micro_env",
        "source_paths": {"without_metta": str(without_path), "with_metta": str(with_path)},
        "generated_at_utc": utc_now(),
        "expected_items": len(expected_indexes),
        "without_metta": psycho_arm_summary(without, without_scores, expected_set),
        "with_metta": psycho_arm_summary(with_metta, with_scores, expected_set),
        "reward_delta": round(float(with_metta.get("reward") or 0.0) - float(without.get("reward") or 0.0), 6),
        "changed_item_count": len(changed_items),
        "changed_items": changed_items,
        "without_subscales": without_subscales,
        "with_subscales": with_subscales,
        "subscale_deltas": subscale_deltas,
        "read": (
            "This env turns a tiny aggregate PsychoBench reward shift into contract checks plus item/subscale deltas. "
            "It is useful for studying whether MeTTa changes stable latent-profile structure or just nudges individual answers."
        ),
    }
    out_dir = out_root / "psycho_bench_item_vector_micro_env"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "psycho_bench_item_vector.results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out_dir / "psycho_bench_item_vector.results.md").write_text(render_psycho_md(summary), encoding="utf-8")
    (out_dir / "psycho_bench_item_vector_contract.metta").write_text(render_psycho_contract(), encoding="utf-8")
    return summary


def psycho_arm_summary(record: dict[str, Any], scores: dict[int, int], expected_set: set[int]) -> dict[str, Any]:
    missing = sorted(expected_set - set(scores))
    extra = sorted(set(scores) - expected_set)
    return {
        "reward": record.get("reward"),
        "valid_action": record.get("valid_action"),
        "item_count": len(scores),
        "missing_items": missing,
        "extra_items": extra,
        "format_pass": not missing and not extra and len(scores) == len(expected_set),
        "mean_score": round(sum(scores.values()) / max(1, len(scores)), 6),
        "score_histogram": dict(Counter(str(value) for value in scores.values())),
    }


def render_math_md(summary: dict[str, Any]) -> str:
    lines = [
        "# Intellect-3 Math Answer-Manifold Micro-Env",
        "",
        f"Source: `{summary['source_path']}`",
        f"Generated: `{summary['generated_at_utc']}`",
        "",
        "MeTTa contract: [`intellect3_math_answer_manifold_contract.metta`](<intellect3_math_answer_manifold_contract.metta>)",
        "",
        summary["read"],
        "",
        "## Arm Summary",
        "",
        "| Arm | Rows | Exact | Avg Rel Distance | Median Rel Distance | Route Sources | Top Failure Tags |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for arm, data in summary["arms"].items():
        lines.append(
            f"| `{arm}` | {data['rows']} | {fmt(data['exact_rate'])} | {fmt(data['avg_relative_distance'])} | "
            f"{fmt(data['median_relative_distance']) if data['median_relative_distance'] is not None else '-'} | "
            f"{top_counts(data['route_sources'])} | {top_counts(data['failure_tag_counts'])} |"
        )
    lines.extend(["", "## Vanilla Vs Math-TRM", "", "| Status | Count |", "| --- | ---: |"])
    for status, count in sorted(summary["problem_status_counts"].items()):
        lines.append(f"| `{status}` | {count} |")
    lines.extend(
        [
            "",
            "## Problem Rows",
            "",
            "| Row | Status | Expected | Vanilla | Math-TRM | Vanilla Rel Dist | TRM Rel Dist | TRM Tags | Route |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in summary["problem_rows"][:220]:
        lines.append(
            f"| `{row['row_id']}` | `{row['status']}` | {row['baseline_expected']} | {row['baseline_predicted']} | "
            f"{row['compare_predicted']} | {fmt(row['baseline_relative_distance'])} | {fmt(row['compare_relative_distance'])} | "
            f"{', '.join(row['compare_tags'])} | `{row['compare_route_source']}` |"
        )
    lines.append("")
    return "\n".join(lines)


def render_psycho_md(summary: dict[str, Any]) -> str:
    lines = [
        "# PsychoBench Item-Vector Micro-Env",
        "",
        f"Generated: `{summary['generated_at_utc']}`",
        "",
        "MeTTa contract: [`psycho_bench_item_vector_contract.metta`](<psycho_bench_item_vector_contract.metta>)",
        "",
        summary["read"],
        "",
        "## Arm Summary",
        "",
        "| Arm | Reward | Format Pass | Item Count | Mean Score | Histogram |",
        "| --- | ---: | --- | ---: | ---: | --- |",
        f"| `without_metta` | {fmt(summary['without_metta']['reward'])} | {summary['without_metta']['format_pass']} | {summary['without_metta']['item_count']} | {fmt(summary['without_metta']['mean_score'])} | {top_counts(summary['without_metta']['score_histogram'])} |",
        f"| `with_metta` | {fmt(summary['with_metta']['reward'])} | {summary['with_metta']['format_pass']} | {summary['with_metta']['item_count']} | {fmt(summary['with_metta']['mean_score'])} | {top_counts(summary['with_metta']['score_histogram'])} |",
        "",
        f"Reward delta: `{summary['reward_delta']:+.6f}`. Changed items: `{summary['changed_item_count']}`.",
        "",
        "## Subscale Deltas",
        "",
        "| Subscale | Without | With MeTTa | Delta |",
        "| --- | ---: | ---: | ---: |",
    ]
    for name in sorted(summary["subscale_deltas"]):
        lines.append(
            f"| `{name}` | {fmt(summary['without_subscales'][name])} | {fmt(summary['with_subscales'][name])} | {summary['subscale_deltas'][name]:+.4f} |"
        )
    lines.extend(["", "## Changed Items", "", "| Item | Without | With MeTTa | Delta |", "| ---: | ---: | ---: | ---: |"])
    for row in summary["changed_items"]:
        lines.append(f"| {row['index']} | {row['without_metta']} | {row['with_metta']} | {row['delta']:+d} |")
    lines.append("")
    return "\n".join(lines)


def render_math_contract() -> str:
    return "\n".join(
        [
            ";; Intellect-3 math answer-manifold micro-env contract.",
            "(= env_id intellect3_math_answer_manifold_micro_env)",
            "(= stage_order (parse_answer classify_numeric_error route_select repair_or_commit))",
            "(= metric_exact_match answer_exact_match)",
            "(= metric_relative_distance abs_error_div_max_abs_expected)",
            "(= gate_parse TRM_PARSE_INTEGER_ANSWER)",
            "(= gate_error_taxonomy TRM_NUMERIC_ERROR_ARCHETYPE)",
            "(= gate_route TRM_ROUTE_MATH_REPAIR)",
            "(= failure_taxonomy (prediction_parse_failure off_by_one off_by_small double half negation sign_error_abs_match same_last_digit same_digit_multiset order_of_magnitude wrong_integer non_integer_wrapper))",
            "",
        ]
    )


def render_psycho_contract() -> str:
    return "\n".join(
        [
            ";; PsychoBench item-vector micro-env contract.",
            "(= env_id psycho_bench_item_vector_micro_env)",
            "(= stage_order (parse_items validate_contract score_vector project_subscales compare_delta))",
            "(= metric_reward_delta psycho_reward_delta)",
            "(= metric_format_pass all_expected_items_once_scores_1_to_5)",
            "(= gate_item_contract TRM_LIKERT_ITEM_VECTOR_CONTRACT)",
            "(= gate_subscale_projection TRM_BFI_SUBSCALE_PROJECTOR)",
            "(= failure_taxonomy (missing_item extra_item duplicate_item out_of_range_score format_wrapper_failure latent_profile_shift))",
            "",
        ]
    )


def fmt(value: Any) -> str:
    if value is None:
        return "-"
    return f"{float(value):.4f}"


def top_counts(counts: dict[str, Any], limit: int = 6) -> str:
    if not counts:
        return "-"
    return ", ".join(f"{key}:{value}" for key, value in sorted(counts.items(), key=lambda item: (-int(item[1]), str(item[0])))[:limit])


def main() -> int:
    args = parse_args()
    out_root = Path(args.out_root).resolve()
    math_summary = build_math_env(Path(args.math_source).resolve(), out_root)
    psycho_summary = build_psycho_env(Path(args.psycho_without).resolve(), Path(args.psycho_with).resolve(), out_root)
    print(out_root / "intellect3_math_answer_manifold_micro_env" / "intellect3_math_answer_manifold.results.md")
    print(out_root / "psycho_bench_item_vector_micro_env" / "psycho_bench_item_vector.results.md")
    print(
        json.dumps(
            {
                "math_exact": {
                    arm: data["exact_rate"] for arm, data in math_summary["arms"].items()
                },
                "psycho_reward_delta": psycho_summary["reward_delta"],
                "psycho_changed_items": psycho_summary["changed_item_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
