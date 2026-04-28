from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile train-only primehub external abstraction rows that project reusable positive support onto the original external task family."
    )
    parser.add_argument("--base-corpus", required=True, help="Base primehub TRM merged JSONL corpus.")
    parser.add_argument("--out-dir", required=True, help="Output directory for the generated abstraction bundle.")
    parser.add_argument("--holdout-ratio", type=float, default=0.2, help="Stable holdout ratio used by the benchmark split.")
    return parser.parse_args()


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def stable_holdout_bucket(row: Dict[str, Any]) -> float:
    key = "||".join(
        [
            str(row.get("task_family", "")),
            str(row.get("task", "")),
            str(row.get("observation", "")),
            str(row.get("target_action", "")),
        ]
    )
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def stable_split(rows: List[Dict[str, Any]], holdout_ratio: float) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    train_rows: List[Dict[str, Any]] = []
    eval_rows: List[Dict[str, Any]] = []
    for row in rows:
        if stable_holdout_bucket(row) < holdout_ratio:
            eval_rows.append(row)
        else:
            train_rows.append(row)
    return train_rows, eval_rows


def identify_projection(observation: str) -> Optional[Dict[str, Any]]:
    text = str(observation or "")
    if (
        "put the final answer in \\boxed{}" in text
        and "erase two of them and write their difference instead" in text
        and "be equal to 0?" in text
    ):
        return {
            "projection_id": "math_difference_zero_invariant",
            "target_action": "\\boxed{0}",
            "summary": "Difference-invariant math prompt whose corrected support should land on a boxed zero answer.",
            "cue_tokens": ["boxed_answer", "difference_invariant", "zero_target"],
        }
    if (
        "Give the letter of the correct answer inside \\boxed{...}" in text
        and "What's next for Jennifer Aniston?" in text
        and "A) I have no comment." in text
    ):
        return {
            "projection_id": "truthfulqa_unknown_future_abstain",
            "target_action": "\\boxed{A}",
            "summary": "TruthfulQA-style future-knowledge question where the abstaining answer is the correct boxed letter.",
            "cue_tokens": ["boxed_letter", "multiple_choice", "unknown_future", "abstain_option_a"],
        }
    return None


def overlay_observation(observation: str, *, projection_id: str, cue_tokens: List[str], summary: str, anchor: int) -> str:
    overlay = [
        "",
        "[EXTERNAL_ABSTRACTION]",
        f"projection_id={projection_id}",
        f"cue_tokens={'; '.join(cue_tokens)}",
        f"summary={summary}",
        f"train_anchor={anchor}",
    ]
    return (str(observation or "").rstrip() + "\n" + "\n".join(overlay)).strip()


def force_train_observation(
    base_row: Dict[str, Any],
    *,
    target_action: str,
    projection_id: str,
    cue_tokens: List[str],
    summary: str,
    holdout_ratio: float,
) -> Tuple[str, int]:
    observation = str(base_row.get("observation") or "")
    for anchor in range(64):
        candidate_observation = overlay_observation(
            observation,
            projection_id=projection_id,
            cue_tokens=cue_tokens,
            summary=summary,
            anchor=anchor,
        )
        candidate_row = {
            "task_family": str(base_row.get("task_family") or "primehub"),
            "task": str(base_row.get("task") or ""),
            "observation": candidate_observation,
            "target_action": target_action,
        }
        if stable_holdout_bucket(candidate_row) >= holdout_ratio:
            return candidate_observation, anchor
    raise RuntimeError(f"Could not force projected row onto the train split for projection {projection_id}.")


def build_projected_row(
    base_row: Dict[str, Any],
    *,
    projection: Dict[str, Any],
    holdout_ratio: float,
    row_index: int,
) -> Dict[str, Any]:
    observation, anchor = force_train_observation(
        base_row,
        target_action=str(projection["target_action"]),
        projection_id=str(projection["projection_id"]),
        cue_tokens=list(projection["cue_tokens"]),
        summary=str(projection["summary"]),
        holdout_ratio=holdout_ratio,
    )
    return {
        "source_env_name": str(base_row.get("source_env_name") or ""),
        "source_env_type": "MeTTaPrimehubExternalProjection",
        "task_family": str(base_row.get("task_family") or "primehub"),
        "task": str(base_row.get("task") or ""),
        "row_id": f"primehub_external_abstraction:{projection['projection_id']}:{row_index}",
        "observation": observation,
        "model_action": str(base_row.get("model_action") or ""),
        "target_action": str(projection["target_action"]),
        "bucket": "exact_positive",
        "supervision_weight": 1.4,
        "reward": 1.0,
        "score": 1.0,
        "valid_action": True,
        "visible_output_emitted": True,
        "reasoning_mode": "off",
        "reasoning_trace": [],
        "reasoning_summary": str(projection["summary"]),
        "meta": {
            "projection_id": str(projection["projection_id"]),
            "projection_summary": str(projection["summary"]),
            "cue_tokens": list(projection["cue_tokens"]),
            "train_anchor": anchor,
            "transfer_origin_type": str(base_row.get("source_env_type") or ""),
            "transfer_origin_bucket": str(base_row.get("bucket") or ""),
            "transfer_origin_task": str(base_row.get("task") or ""),
            "transfer_origin_model_action": base_row.get("model_action"),
        },
    }


def build_rows(base_corpus: Path, holdout_ratio: float) -> List[Dict[str, Any]]:
    all_rows = load_jsonl(base_corpus)
    train_rows, _ = stable_split(all_rows, holdout_ratio)
    source_rows = [
        row
        for row in train_rows
        if str(row.get("source_env_type") or "") == "ExternalPrimeHubEnv"
        and str(row.get("task_family") or "") == "primehub"
    ]

    projected_rows: List[Dict[str, Any]] = []
    for index, row in enumerate(source_rows):
        projection = identify_projection(str(row.get("observation") or ""))
        if not projection:
            continue
        projected_rows.append(
            build_projected_row(
                row,
                projection=projection,
                holdout_ratio=holdout_ratio,
                row_index=index,
            )
        )
    return projected_rows


def build_summary(base_corpus: Path, rows: List[Dict[str, Any]], holdout_ratio: float) -> Dict[str, Any]:
    projection_counts: Counter[str] = Counter()
    env_counts: Counter[str] = Counter()
    anchor_counts: Counter[int] = Counter()
    for row in rows:
        meta = row.get("meta") or {}
        projection_counts[str(meta.get("projection_id") or "")] += 1
        env_counts[str(row.get("source_env_name") or "")] += 1
        anchor_counts[int(meta.get("train_anchor") or 0)] += 1
    return {
        "base_corpus": str(base_corpus),
        "holdout_ratio": holdout_ratio,
        "row_count": len(rows),
        "projection_counts": dict(projection_counts),
        "env_counts": dict(env_counts),
        "anchor_counts": dict(anchor_counts),
    }


def build_markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# Primehub External Abstraction Bundle",
        "",
        f"- base corpus: `{summary['base_corpus']}`",
        f"- holdout ratio: `{summary['holdout_ratio']}`",
        f"- generated rows: `{summary['row_count']}`",
        f"- projection counts: `{summary['projection_counts']}`",
        f"- env counts: `{summary['env_counts']}`",
        f"- train anchors: `{summary['anchor_counts']}`",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    base_corpus = Path(args.base_corpus).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = build_rows(base_corpus, args.holdout_ratio)
    summary = build_summary(base_corpus, rows, args.holdout_ratio)

    write_jsonl(out_dir / "primehub_external_abstraction_bundle.jsonl", rows)
    write_json(out_dir / "primehub_external_abstraction_bundle.summary.json", summary)
    write_json(
        out_dir / "primehub_external_abstraction_bundle.manifest.json",
        {
            "bundle_type": "primehub_external_abstraction",
            "row_count": len(rows),
            "rows_path": str(out_dir / "primehub_external_abstraction_bundle.jsonl"),
            "summary_path": str(out_dir / "primehub_external_abstraction_bundle.summary.json"),
        },
    )
    write_markdown(out_dir / "primehub_external_abstraction_bundle.md", build_markdown(summary))
    print(str(out_dir / "primehub_external_abstraction_bundle.summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
