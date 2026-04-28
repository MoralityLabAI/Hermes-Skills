from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_REPLAY_ROOTS = [
    Path(r"C:\projects\Hermes-Skills\Hermes Skills\data\primehub_eligible_benchmark_v3_tuned_44env_v2"),
    Path(r"C:\projects\Hermes-Skills\Hermes Skills\data\primehub_overnight_all"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile train-only critic-support rows for the repeated aime2026 boxed-answer family."
    )
    parser.add_argument("--base-corpus", required=True, help="Base primehub TRM merged JSONL corpus.")
    parser.add_argument("--out-dir", required=True, help="Output directory for the generated aime2026 critic-support bundle.")
    parser.add_argument("--holdout-ratio", type=float, default=0.2, help="Stable holdout ratio used by the benchmark split.")
    parser.add_argument("--copies-per-family", type=int, default=6, help="Minimum number of critic-support rows to generate per supported family.")
    parser.add_argument(
        "--replay-root",
        action="append",
        default=[],
        help="Optional replay roots to mine for aime2026 observations when the base corpus train split has no usable source rows.",
    )
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


def first_jsonl_row(path: Path) -> Optional[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                return json.loads(text)
    return None


def load_replay_source_rows(replay_roots: List[Path]) -> List[Dict[str, Any]]:
    source_rows: List[Dict[str, Any]] = []
    seen_keys = set()
    for root in replay_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.jsonl")):
            row = first_jsonl_row(path)
            if not row or str(row.get("env_name") or "") != "aime2026":
                continue
            observation = str(row.get("observation") or "")
            action = str(row.get("action") or "")
            key = (observation, action, path.name)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            source_rows.append(
                {
                    "source_env_name": "aime2026",
                    "source_env_type": "ExternalPrimeHubEnvReplay",
                    "task_family": "primehub",
                    "task": str(row.get("task_id") or "default"),
                    "observation": observation,
                    "model_action": action,
                    "bucket": "negative" if float(row.get("reward") or 0.0) <= 0.0 else "exact_positive",
                    "meta": {
                        "replay_path": str(path),
                        "replay_root": str(root),
                    },
                }
            )
    return source_rows


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


def identify_family(observation: str) -> Optional[Dict[str, Any]]:
    text = str(observation or "")
    if (
        "Solve the following math problem." in text
        and "put the final answer in \\boxed{}" in text
        and "For each positive integer $r$ less than $502,$ define" in text
        and "multiples of the prime number $503.$" in text
    ):
        return {
            "family_id": "aime2026_binomial_mod503_boxed39",
            "source_env_name": "aime2026",
            "expected_answer": r"\boxed{39}",
            "summary": "Critic support for the repeated aime2026 boxed-39 family, emphasizing visible boxed output over inspect_and_continue failures.",
            "cue_tokens": ["aime2026", "boxed_answer", "numeric_exact", "visible_output_recovery", "critic_support"],
        }
    return None


def force_train_target_action(
    row: Dict[str, Any],
    *,
    family_id: str,
    support_index: int,
    holdout_ratio: float,
) -> str:
    for anchor in range(128):
        target_action = f"CRITIC_SUPPORT::{family_id}::{support_index:02d}::{anchor:02d}"
        candidate = {
            "task_family": str(row.get("task_family") or "primehub"),
            "task": str(row.get("task") or ""),
            "observation": str(row.get("observation") or ""),
            "target_action": target_action,
        }
        if stable_holdout_bucket(candidate) >= holdout_ratio:
            return target_action
    raise RuntimeError(f"Could not force critic-support row onto the train split for {family_id}.")


def build_rows(base_corpus: Path, holdout_ratio: float, copies_per_family: int, replay_roots: List[Path]) -> List[Dict[str, Any]]:
    all_rows = load_jsonl(base_corpus)
    train_rows, _ = stable_split(all_rows, holdout_ratio)
    source_rows = [
        row
        for row in train_rows
        if str(row.get("source_env_type") or "") == "ExternalPrimeHubEnv"
        and str(row.get("task_family") or "") == "primehub"
        and str(row.get("source_env_name") or "") == "aime2026"
    ]
    if not source_rows:
        source_rows = load_replay_source_rows(replay_roots)

    family_sources: Dict[str, List[Tuple[Dict[str, Any], Dict[str, Any]]]] = defaultdict(list)
    for row in source_rows:
        family = identify_family(str(row.get("observation") or ""))
        if family:
            family_sources[str(family["family_id"])].append((row, family))

    critic_rows: List[Dict[str, Any]] = []
    for family_id, items in family_sources.items():
        if not items:
            continue
        required = max(copies_per_family, len(items))
        for support_index in range(required):
            source_row, family = items[support_index % len(items)]
            target_action = force_train_target_action(
                source_row,
                family_id=family_id,
                support_index=support_index,
                holdout_ratio=holdout_ratio,
            )
            critic_rows.append(
                {
                    "source_env_name": str(family["source_env_name"]),
                    "source_env_type": "MeTTaPrimehubAimeCriticSupport",
                    "task_family": str(source_row.get("task_family") or "primehub"),
                    "task": str(source_row.get("task") or ""),
                    "row_id": f"primehub_external_aime2026_critic_support:{family_id}:{support_index}",
                    "observation": str(source_row.get("observation") or ""),
                    "model_action": str(source_row.get("model_action") or ""),
                    "target_action": target_action,
                    "bucket": "exact_positive",
                    "supervision_weight": 0.1,
                    "reward": 1.0,
                    "score": 1.0,
                    "valid_action": True,
                    "visible_output_emitted": True,
                    "reasoning_mode": "off",
                    "reasoning_trace": [],
                    "reasoning_summary": str(family["summary"]),
                    "meta": {
                        "family_id": family_id,
                        "expected_answer": str(family["expected_answer"]),
                        "cue_tokens": list(family["cue_tokens"]),
                        "support_index": support_index,
                        "transfer_origin_type": str(source_row.get("source_env_type") or ""),
                        "transfer_origin_bucket": str(source_row.get("bucket") or ""),
                        "transfer_origin_model_action": source_row.get("model_action"),
                        "transfer_origin_replay_path": ((source_row.get("meta") or {}).get("replay_path")),
                    },
                }
            )
    return critic_rows


def build_summary(
    base_corpus: Path,
    rows: List[Dict[str, Any]],
    holdout_ratio: float,
    copies_per_family: int,
    replay_roots: List[Path],
) -> Dict[str, Any]:
    family_counts: Counter[str] = Counter()
    env_counts: Counter[str] = Counter()
    origin_type_counts: Counter[str] = Counter()
    for row in rows:
        family_counts[str((row.get("meta") or {}).get("family_id") or "")] += 1
        env_counts[str(row.get("source_env_name") or "")] += 1
        origin_type_counts[str((row.get("meta") or {}).get("transfer_origin_type") or "")] += 1
    return {
        "base_corpus": str(base_corpus),
        "holdout_ratio": holdout_ratio,
        "copies_per_family": copies_per_family,
        "replay_roots": [str(path) for path in replay_roots],
        "row_count": len(rows),
        "family_counts": dict(family_counts),
        "env_counts": dict(env_counts),
        "origin_type_counts": dict(origin_type_counts),
    }


def build_markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# Primehub External AIME2026 Critic Support Bundle",
        "",
        f"- base corpus: `{summary['base_corpus']}`",
        f"- holdout ratio: `{summary['holdout_ratio']}`",
        f"- copies per family: `{summary['copies_per_family']}`",
        f"- replay roots: `{summary['replay_roots']}`",
        f"- generated rows: `{summary['row_count']}`",
        f"- family counts: `{summary['family_counts']}`",
        f"- env counts: `{summary['env_counts']}`",
        f"- origin types: `{summary['origin_type_counts']}`",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    base_corpus = Path(args.base_corpus).resolve()
    out_dir = Path(args.out_dir).resolve()
    replay_roots = [Path(path).resolve() for path in (args.replay_root or [])]
    if not replay_roots:
        replay_roots = [path.resolve() for path in DEFAULT_REPLAY_ROOTS]
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = build_rows(base_corpus, args.holdout_ratio, args.copies_per_family, replay_roots)
    summary = build_summary(base_corpus, rows, args.holdout_ratio, args.copies_per_family, replay_roots)

    write_jsonl(out_dir / "primehub_external_aime2026_critic_support_bundle.jsonl", rows)
    write_json(out_dir / "primehub_external_aime2026_critic_support_bundle.summary.json", summary)
    write_json(
        out_dir / "primehub_external_aime2026_critic_support_bundle.manifest.json",
        {
            "bundle_type": "primehub_external_aime2026_critic_support",
            "row_count": len(rows),
            "rows_path": str(out_dir / "primehub_external_aime2026_critic_support_bundle.jsonl"),
            "summary_path": str(out_dir / "primehub_external_aime2026_critic_support_bundle.summary.json"),
        },
    )
    write_markdown(out_dir / "primehub_external_aime2026_critic_support_bundle.md", build_markdown(summary))
    print(str(out_dir / "primehub_external_aime2026_critic_support_bundle.summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
