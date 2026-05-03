"""Analyze row-level selectors over Intellect-3-Math patch-bank outputs.

The patch bank often contains isolated row-level fixes even when no whole patch
beats the incumbent.  This script measures whether simple selector policies can
exploit that signal without using labels from the same evaluation row.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "research" / "studies" / "2026-04-22-metta-trm-hermes-pipeline" / "artifacts"
DEFAULT_OUT = ARTIFACTS / "intellect3_math_patch_selector_27b_20260503"
DEFAULT_SHARDS = [
    ARTIFACTS / "intellect3_math_patch_bank_benchmark_27b_20260502",
    ARTIFACTS / "intellect3_math_patch_bank_benchmark_27b_20260502_offset10",
    ARTIFACTS / "intellect3_math_patch_bank_benchmark_27b_20260502_offset20",
    ARTIFACTS / "intellect3_math_patch_bank_benchmark_27b_20260502_offset30",
]
INCUMBENT = "incumbent_current_skill"
RAW = "raw_baseline_no_skill"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze row-level patch selectors.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), type=Path)
    parser.add_argument("shards", nargs="*", type=Path, default=DEFAULT_SHARDS)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def load_rows(shards: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for shard in shards:
        rows.extend(load_jsonl(shard / "patch_bank_benchmark.rows.jsonl"))
    return rows


def group_by_row(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        patch_id = str(row.get("patch_id") or row.get("arm"))
        grouped[str(row["row_id"])][patch_id] = row
    return dict(sorted(grouped.items()))


def answer(row: dict[str, Any] | None) -> str:
    if not row:
        return ""
    return str(row.get("action") or "").strip()


def score_selection(groups: dict[str, dict[str, dict[str, Any]]], selections: dict[str, str]) -> dict[str, Any]:
    hits = 0
    missing = 0
    selected_counts = Counter()
    for row_id, patch_rows in groups.items():
        patch_id = selections.get(row_id, INCUMBENT)
        selected_counts[patch_id] += 1
        row = patch_rows.get(patch_id)
        if not row:
            missing += 1
            row = patch_rows.get(INCUMBENT)
        hits += int(bool(row and row.get("exact")))
    total = len(groups)
    return {
        "rows": total,
        "exact": hits,
        "exact_rate": round(hits / max(1, total), 6),
        "missing_selected_rows": missing,
        "selected_patch_counts": dict(selected_counts),
    }


def incumbent_selector(groups: dict[str, dict[str, dict[str, Any]]]) -> dict[str, str]:
    return {row_id: INCUMBENT for row_id in groups}


def oracle_selector(groups: dict[str, dict[str, dict[str, Any]]]) -> dict[str, str]:
    selections: dict[str, str] = {}
    for row_id, patch_rows in groups.items():
        exact = [patch_id for patch_id, row in patch_rows.items() if row.get("exact")]
        selections[row_id] = exact[0] if exact else INCUMBENT
    return selections


def plurality_answer_selector(groups: dict[str, dict[str, dict[str, Any]]]) -> dict[str, str]:
    selections: dict[str, str] = {}
    for row_id, patch_rows in groups.items():
        counts = Counter(answer(row) for row in patch_rows.values() if answer(row))
        incumbent_answer = answer(patch_rows.get(INCUMBENT))
        if not counts:
            selections[row_id] = INCUMBENT
            continue
        best_answer, best_count = counts.most_common(1)[0]
        if best_count < 2 or best_answer == incumbent_answer:
            selections[row_id] = INCUMBENT
            continue
        candidates = [patch_id for patch_id, row in patch_rows.items() if answer(row) == best_answer and not row.get("error")]
        selections[row_id] = sorted(candidates)[0] if candidates else INCUMBENT
    return selections


def train_priors(groups: dict[str, dict[str, dict[str, Any]]], train_ids: set[str]) -> dict[str, Any]:
    patch_hits = Counter()
    patch_seen = Counter()
    answer_hits = Counter()
    answer_seen = Counter()
    for row_id, patch_rows in groups.items():
        if row_id not in train_ids:
            continue
        for patch_id, row in patch_rows.items():
            patch_seen[patch_id] += 1
            patch_hits[patch_id] += int(bool(row.get("exact")))
            ans = answer(row)
            if ans:
                answer_seen[ans] += 1
                answer_hits[ans] += int(bool(row.get("exact")))
    patch_rate = {
        patch_id: (patch_hits[patch_id] + 1.0) / (patch_seen[patch_id] + 2.0)
        for patch_id in patch_seen
    }
    answer_rate = {
        ans: (answer_hits[ans] + 1.0) / (answer_seen[ans] + 2.0)
        for ans in answer_seen
    }
    return {"patch_rate": patch_rate, "answer_rate": answer_rate}


def prior_selector(
    groups: dict[str, dict[str, dict[str, Any]]],
    priors: dict[str, Any],
    eligible_ids: set[str],
) -> dict[str, str]:
    selections: dict[str, str] = {}
    patch_rate = priors["patch_rate"]
    answer_rate = priors["answer_rate"]
    for row_id, patch_rows in groups.items():
        if row_id not in eligible_ids:
            continue
        incumbent = patch_rows.get(INCUMBENT)
        best_patch = INCUMBENT
        best_score = -1.0
        for patch_id, row in patch_rows.items():
            if patch_id == RAW or row.get("error"):
                continue
            ans = answer(row)
            plurality = sum(1 for candidate in patch_rows.values() if answer(candidate) == ans)
            score = (
                float(patch_rate.get(patch_id, 0.5))
                + float(answer_rate.get(ans, 0.5))
                + min(plurality, 3) * 0.03
            )
            if incumbent and ans == answer(incumbent):
                score += 0.04
            if score > best_score:
                best_score = score
                best_patch = patch_id
        selections[row_id] = best_patch
    return selections


def split_ids(groups: dict[str, dict[str, dict[str, Any]]]) -> tuple[set[str], set[str]]:
    ids = list(groups)
    train = {row_id for idx, row_id in enumerate(ids) if idx % 2 == 0}
    test = set(ids) - train
    return train, test


def subset(groups: dict[str, dict[str, dict[str, Any]]], ids: set[str]) -> dict[str, dict[str, dict[str, Any]]]:
    return {row_id: groups[row_id] for row_id in groups if row_id in ids}


def selector_trm_rows(groups: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row_id, patch_rows in groups.items():
        exact_patches = [patch_id for patch_id, row in patch_rows.items() if row.get("exact")]
        label = exact_patches[0] if exact_patches else INCUMBENT
        for patch_id, row in sorted(patch_rows.items()):
            incumbent = patch_rows.get(INCUMBENT)
            ans = answer(row)
            agreement = sum(1 for candidate in patch_rows.values() if answer(candidate) == ans)
            out.append(
                {
                    "row_id": row_id,
                    "env_family": "intellect3_math_patch_selector",
                    "patch_id": patch_id,
                    "state": {
                        "candidate_action": ans,
                        "incumbent_action": answer(incumbent),
                        "candidate_error": bool(row.get("error")),
                        "answer_agreement_count": agreement,
                        "candidate_patch_source": row.get("patch_source"),
                    },
                    "label": "select_patch" if patch_id == label else "reject_patch",
                    "target": {"selected_patch_id": label},
                }
            )
    return out


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Intellect-3-Math Row-Level Patch Selector",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        f"Rows: `{payload['rows']}`",
        f"Calls: `{payload['calls']}`",
        "",
        "## Selector Scores",
        "",
        "| Selector | Split | Rows | Exact | Exact Rate |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for name, metrics in payload["selectors"].items():
        lines.append(
            f"| `{name}` | `{metrics['split']}` | {metrics['rows']} | {metrics['exact']} | {metrics['exact_rate']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            payload["read"],
            "",
            "## Row-Level Upper Bound",
            "",
            json.dumps(payload["row_level_upper_bound"], indent=2),
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = load_rows(args.shards)
    groups = group_by_row(rows)
    train_ids, test_ids = split_ids(groups)
    train_groups = subset(groups, train_ids)
    test_groups = subset(groups, test_ids)
    priors = train_priors(groups, train_ids)
    train_prior_selections = prior_selector(groups, priors, train_ids)
    test_prior_selections = prior_selector(groups, priors, test_ids)

    selectors = {
        "incumbent_all": {"split": "all", **score_selection(groups, incumbent_selector(groups))},
        "oracle_any_exact_all": {"split": "all", **score_selection(groups, oracle_selector(groups))},
        "plurality_answer_all": {"split": "all", **score_selection(groups, plurality_answer_selector(groups))},
        "prior_selector_train": {"split": "train", **score_selection(train_groups, train_prior_selections)},
        "prior_selector_test": {"split": "test", **score_selection(test_groups, test_prior_selections)},
        "incumbent_test": {"split": "test", **score_selection(test_groups, incumbent_selector(test_groups))},
        "oracle_any_exact_test": {"split": "test", **score_selection(test_groups, oracle_selector(test_groups))},
    }

    upper = score_selection(groups, oracle_selector(groups))
    read = (
        "The current patch bank has a small oracle headroom over the incumbent "
        f"({upper['exact']}/{upper['rows']} vs {selectors['incumbent_all']['exact']}/{selectors['incumbent_all']['rows']}), "
        "but the simple learned prior selector does not yet extract reliable held-out lift. "
        "Next useful work is to train a selector TRM on richer features, not to adopt a global prompt patch."
    )
    payload = {
        "generated_at_utc": utc_now(),
        "shards": [str(path) for path in args.shards],
        "rows": len(groups),
        "calls": len(rows),
        "selectors": selectors,
        "row_level_upper_bound": upper,
        "read": read,
    }
    (args.out_dir / "patch_selector.results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")
    (args.out_dir / "patch_selector.results.md").write_text(render_md(payload), encoding="utf-8", newline="\n")
    with (args.out_dir / "patch_selector_trm_rows.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in selector_trm_rows(groups):
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    print(args.out_dir / "patch_selector.results.md")
    print(json.dumps(selectors, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
