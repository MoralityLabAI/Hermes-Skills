from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
HARNESS_ROOT = Path(r"C:/projects/trm_observability_harness")
DEFAULT_MANIFEST = ROOT / "data" / "primehub_skill_batch_evolution" / "latest.manifest.json"
DEFAULT_OUT = ROOT / "data" / "primehub_skill_trm_matrix" / "latest"
DEFAULT_RUN_ROOTS = [
    ROOT / "data" / "primehub_eligible_benchmark_v1",
    ROOT / "data" / "primehub_eligible_benchmark_v1_retry_27b_tail",
    ROOT / "data" / "primehub_eligible_benchmark_v2_47env",
    ROOT / "data" / "primehub_eligible_benchmark_v3_tuned_44env_v2",
]

CHOICE_CONTRACT_PRESSURE_ENVS = {
    "allenai_ifeval",
    "arc",
    "hellaswag",
    "mmlu_pro",
    "simpleqa",
    "simpleqa_verified",
    "simpleqa_verified_2",
    "truthfulqa",
}

CHOICE_CONTRACT_FACTOID_ENVS = {
    "simpleqa",
    "simpleqa_verified",
    "simpleqa_verified_2",
}

CHOICE_CONTRACT_ANCHOR_ENVS = {
    "boolq",
    "winogrande",
}

CHOICE_CONTRACT_MC_REASONING_ENVS = {
    "mmlu_pro",
}


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def run(cmd: List[str], *, cwd: Path) -> None:
    subprocess.run(cmd, cwd=str(cwd), check=True)


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from harness.trm_retrieval import stable_holdout_bucket  # noqa: E402
from primehub_role_imprint import build_payload as build_role_imprint_payload  # noqa: E402
from primehub_role_imprint import build_trainer_policy  # noqa: E402
from primehub_role_imprint import render_markdown as render_role_imprint_markdown  # noqa: E402


def first_row(path: Path) -> Dict[str, Any] | None:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            return json.loads(line)
    return None


def discover_replays(run_roots: List[Path]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    seen = set()
    for run_root in run_roots:
        if not run_root.exists():
            continue
        for path in sorted(run_root.rglob("*.jsonl")):
            if not path.parent.name.startswith("qwen35_"):
                continue
            key = str(path.resolve()).lower()
            if key in seen:
                continue
            seen.add(key)
            first = first_row(path)
            if not first:
                continue
            rows.append(
                {
                    "path": str(path.resolve()),
                    "env_name": str(first.get("env_name") or ""),
                    "task": str(first.get("task") or ""),
                    "model_name": str(first.get("model_name") or ""),
                    "reward": float(first.get("reward") or 0.0),
                }
            )
    return rows


def stage_replay(replay_path: Path, stage_dir: Path, *, task_family: str) -> Dict[str, Any]:
    trm_path = stage_dir / f"{replay_path.stem}.trm.jsonl"
    summary_path = stage_dir / f"{replay_path.stem}.trm.summary.json"
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "build_trm_train_rows.py"),
            "--input",
            str(replay_path),
            "--output",
            str(trm_path),
            "--summary",
            str(summary_path),
            "--task-family",
            task_family,
        ],
        cwd=ROOT,
    )
    summary = load_json(summary_path)
    return {
        "input": str(replay_path),
        "staged": str(trm_path),
        "summary": str(summary_path),
        "total_rows": int(summary.get("total_rows") or 0),
        "bucket_counts": summary.get("bucket_counts") or {},
    }


def specialize_rows(cluster_id: str, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if cluster_id == "internal_action":
        filtered: List[Dict[str, Any]] = []
        for row in rows:
            bucket = str(row.get("bucket") or "")
            model_action = str(row.get("model_action") or "").strip()
            visible = bool(row.get("visible_output_emitted"))
            if bucket == "exact_positive" and visible and model_action != "inspect_and_continue":
                continue
            filtered.append(row)
        return filtered
    if cluster_id == "choice_contract":
        filtered = []
        for row in rows:
            # Transport/harness failures are not useful supervision for answer-contract training.
            if has_failure_signal(row):
                continue
            if not bool(row.get("valid_action")) and not bool(row.get("visible_output_emitted")):
                continue
            if should_drop_choice_contract_row(row):
                continue
            filtered.append(row)
        return filtered
    return rows


def normalize_text(value: Any) -> str:
    return str(value or "").strip()


def looks_refusal_or_reasoning_leak(text: str) -> bool:
    lowered = text.strip().lower()
    if not lowered:
        return False
    refusal_markers = [
        "i'm not going to",
        "i am not going to",
        "i cannot",
        "i can't",
        "i will not",
        "as an ai",
        "i'm an ai",
        "i am an ai",
        "i have no comment",
        "<analysis>",
        "```",
    ]
    return any(marker in lowered for marker in refusal_markers)


def has_failure_signal(row: Dict[str, Any]) -> bool:
    output_status = normalize_text(row.get("output_status")).lower()
    meta = row.get("meta") or {}
    failure_type = normalize_text(meta.get("failure_type"))
    return bool(
        failure_type
        or "error" in output_status
        or "timed out" in output_status
        or "timeout" in output_status
        or "failed" in output_status
    )


def looks_concise_answer(text: str) -> bool:
    compact = " ".join(text.strip().split())
    if not compact or len(compact) > 96:
        return False
    if looks_refusal_or_reasoning_leak(compact):
        return False
    if compact.count(".") + compact.count("!") + compact.count("?") > 1:
        return False
    word_count = len(re.findall(r"[A-Za-z0-9]+", compact))
    return word_count <= 16


def looks_choice_contract_attempt(text: str, env_name: str) -> bool:
    compact = text.strip()
    if not compact or looks_refusal_or_reasoning_leak(compact):
        return False
    if looks_concise_answer(compact):
        return True

    lines = [line.strip() for line in compact.splitlines() if line.strip()]
    last_line = lines[-1] if lines else compact
    if re.fullmatch(r"(?:answer\s*[:\-]?\s*)?[A-J]", last_line, re.IGNORECASE):
        return True
    if re.search(r"\\boxed\{\s*[A-J]\s*\}", compact, re.IGNORECASE):
        return True
    if re.search(r"(?:correct answer|answer is)\s*[:\-]?\s*[A-J]\b", compact, re.IGNORECASE):
        return True

    normalized_env = normalize_text(env_name)
    if normalized_env in CHOICE_CONTRACT_FACTOID_ENVS:
        factoid = " ".join(compact.split())
        if len(factoid) <= 120 and len(re.findall(r"[A-Za-z0-9]+", factoid)) <= 18:
            return True
    return False


def looks_mmlu_repair_attempt(text: str) -> bool:
    compact = text.strip()
    if not compact or looks_refusal_or_reasoning_leak(compact):
        return False
    lowered = compact.lower()
    if len(compact) < 180:
        return False
    if not any(marker in lowered for marker in ["the core issue", "hearsay", "admissible", "inadmissible", "federal rules"]):
        return False
    option_hits = len(re.findall(r"\b[A-J]\.", compact))
    numbered_hits = len(re.findall(r"\b\d+\.", compact))
    return option_hits >= 2 or numbered_hits >= 2


def should_drop_choice_contract_row(row: Dict[str, Any]) -> bool:
    env_name = normalize_text(row.get("source_env_name"))
    model_action = normalize_text(row.get("model_action"))
    visible = bool(row.get("visible_output_emitted"))
    output_status = normalize_text(row.get("output_status")).lower()

    if env_name in CHOICE_CONTRACT_FACTOID_ENVS:
        if model_action == "inspect_and_continue":
            return True
        if "<analysis>" in model_action.lower():
            return True
    if env_name == "truthfulqa" and model_action == "inspect_and_continue" and not visible:
        return True
    if env_name in CHOICE_CONTRACT_MC_REASONING_ENVS and model_action == "inspect_and_continue" and not visible and "completed" in output_status:
        return True
    return False


def looks_boxed_or_numeric_answer(text: str) -> bool:
    compact = text.strip()
    if not compact or looks_refusal_or_reasoning_leak(compact):
        return False
    if "\\boxed{" in compact:
        return True
    return bool(re.fullmatch(r"[-+]?[\d][\d,./ ]*", compact))


def looks_structured_map_attempt(text: str) -> bool:
    compact = text.strip()
    if not compact or looks_refusal_or_reasoning_leak(compact):
        return False
    lines = [line.strip() for line in compact.splitlines() if line.strip()]
    if len(lines) < 2:
        return False
    score_like_lines = sum(1 for line in lines[:12] if ":" in line)
    if score_like_lines >= 2:
        return True
    if "<ascii_formatted>" in compact.lower():
        return True
    return False


def looks_guarded_abstention(text: str) -> bool:
    lowered = text.strip().lower()
    if not lowered:
        return False
    return any(
        marker in lowered
        for marker in [
            "i have no comment",
            "cannot help",
            "can't help",
            "cannot provide",
            "can't provide",
            "cannot comply",
            "can't comply",
            "not assist",
        ]
    )


def deterministic_row_key(row: Dict[str, Any]) -> tuple[str, ...]:
    meta = row.get("meta") or {}
    return (
        normalize_text(row.get("source_env_name")),
        normalize_text(row.get("task")),
        normalize_text(meta.get("model_name")),
        normalize_text(meta.get("episode_id")),
        normalize_text(row.get("model_action"))[:64],
    )


def mine_bucket_override(cluster_id: str, row: Dict[str, Any]) -> tuple[str, str] | None:
    bucket = normalize_text(row.get("bucket")) or "negative"
    if bucket != "negative":
        return None
    model_action = normalize_text(row.get("model_action"))
    if not model_action:
        return None
    if has_failure_signal(row):
        return None
    if not bool(row.get("valid_action")):
        return None
    if cluster_id == "structured_map" and bool(row.get("visible_output_emitted")) and looks_structured_map_attempt(model_action):
        return ("near_miss", "structured_output_attempt")
    if cluster_id == "choice_contract" and bool(row.get("visible_output_emitted")):
        env_name = normalize_text(row.get("source_env_name"))
        if looks_choice_contract_attempt(model_action, env_name):
            reason = "contract_answer_attempt"
            if env_name in CHOICE_CONTRACT_FACTOID_ENVS:
                reason = "factoid_answer_attempt"
            return ("weak_positive", reason)
        if env_name in CHOICE_CONTRACT_MC_REASONING_ENVS and looks_mmlu_repair_attempt(model_action):
            return ("near_miss", "mc_reasoning_attempt")
    if cluster_id in {"hard_reasoning_numeric", "hard_reasoning_logic"} and bool(row.get("visible_output_emitted")):
        if looks_boxed_or_numeric_answer(model_action):
            return ("weak_positive", "final_answer_attempt")
    if cluster_id == "abstain_guard" and bool(row.get("visible_output_emitted")) and looks_guarded_abstention(model_action):
        return ("weak_positive", "guarded_abstention_attempt")
    return None


def apply_bucket_mining(cluster_id: str, rows: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    mined_rows: List[Dict[str, Any]] = []
    transition_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    changed_rows = 0
    for row in rows:
        enriched = dict(row)
        override = mine_bucket_override(cluster_id, enriched)
        if override is None:
            mined_rows.append(enriched)
            continue
        next_bucket, reason = override
        prior_bucket = normalize_text(enriched.get("bucket")) or "negative"
        if next_bucket == prior_bucket:
            mined_rows.append(enriched)
            continue
        enriched["bucket"] = next_bucket
        meta = dict(enriched.get("meta") or {})
        meta["bucket_mined_from"] = prior_bucket
        meta["bucket_mined_to"] = next_bucket
        meta["bucket_mining_reason"] = reason
        enriched["meta"] = meta
        mined_rows.append(enriched)
        transition_counts[f"{prior_bucket}->{next_bucket}"] += 1
        reason_counts[reason] += 1
        changed_rows += 1
    return mined_rows, {
        "changed_rows": changed_rows,
        "transitions": dict(transition_counts),
        "reasons": dict(reason_counts),
    }


def is_easy_negative(row: Dict[str, Any]) -> bool:
    bucket = normalize_text(row.get("bucket")) or "negative"
    if bucket != "negative":
        return False
    if has_failure_signal(row):
        return False
    if not bool(row.get("valid_action")):
        return False
    if not bool(row.get("visible_output_emitted")):
        return False
    model_action = normalize_text(row.get("model_action"))
    if not model_action or looks_refusal_or_reasoning_leak(model_action):
        return False
    return True


def priority_replica_count(cluster_id: str, row: Dict[str, Any]) -> int:
    if cluster_id != "choice_contract":
        return 0
    env_name = normalize_text(row.get("source_env_name"))
    bucket = normalize_text(row.get("bucket"))
    if env_name in CHOICE_CONTRACT_ANCHOR_ENVS and bucket == "exact_positive":
        return 2
    if env_name == "truthfulqa" and bucket == "exact_positive":
        return 1
    if env_name in CHOICE_CONTRACT_MC_REASONING_ENVS and bucket == "near_miss":
        return 2
    if env_name not in CHOICE_CONTRACT_PRESSURE_ENVS:
        return 0
    if bucket == "exact_positive":
        return 1
    if bucket in {"near_miss", "weak_positive"}:
        return 2
    return 0


def amplify_priority_rows(cluster_id: str, rows: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    amplified_rows: List[Dict[str, Any]] = []
    replicated_rows = 0
    added_rows = 0
    bucket_counts: Counter[str] = Counter()
    env_counts: Counter[str] = Counter()
    for row in rows:
        amplified_rows.append(row)
        copies = priority_replica_count(cluster_id, row)
        if copies <= 0:
            continue
        bucket = normalize_text(row.get("bucket")) or "unknown"
        env_name = normalize_text(row.get("source_env_name")) or "unknown"
        for copy_index in range(copies):
            replica = dict(row)
            meta = dict(replica.get("meta") or {})
            meta["env_priority_oversample"] = True
            meta["env_priority_oversample_env"] = env_name
            meta["env_priority_oversample_bucket"] = bucket
            meta["env_priority_oversample_copy_index"] = copy_index + 1
            replica["meta"] = meta
            amplified_rows.append(replica)
            added_rows += 1
        replicated_rows += 1
        bucket_counts[bucket] += copies
        env_counts[env_name] += copies
    return amplified_rows, {
        "replicated_source_rows": replicated_rows,
        "added_rows": added_rows,
        "bucket_replica_counts": dict(bucket_counts),
        "env_replica_counts": dict(env_counts),
    }


def downsample_negative_rows(rows: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    positives = [row for row in rows if normalize_text(row.get("bucket")) not in {"", "negative"}]
    negatives = [row for row in rows if normalize_text(row.get("bucket")) == "negative"]
    if not negatives:
        return rows, {
            "original_negative_rows": 0,
            "kept_negative_rows": 0,
            "dropped_negative_rows": 0,
            "hard_negative_rows_kept": 0,
            "easy_negative_rows_kept": 0,
            "easy_negative_rows_dropped": 0,
        }

    hard_negatives = [row for row in negatives if not is_easy_negative(row)]
    easy_negatives = [row for row in negatives if is_easy_negative(row)]
    unique_envs = {normalize_text(row.get("source_env_name")) or "unknown" for row in rows}
    positive_support = len(positives)
    if positive_support > 0:
        target_negative_budget = max(len(hard_negatives), min(len(negatives), max(len(unique_envs), positive_support * 3)))
    else:
        target_negative_budget = min(len(negatives), max(len(unique_envs) * 2, 8))
    easy_budget = max(0, target_negative_budget - len(hard_negatives))

    kept_easy: List[Dict[str, Any]] = []
    easy_by_env: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in sorted(easy_negatives, key=deterministic_row_key):
        env_name = normalize_text(row.get("source_env_name")) or "unknown"
        easy_by_env[env_name].append(row)

    for env_name in sorted(easy_by_env):
        if len(kept_easy) >= easy_budget:
            break
        kept_easy.append(easy_by_env[env_name][0])

    already_kept = {deterministic_row_key(row) for row in kept_easy}
    for row in sorted(easy_negatives, key=deterministic_row_key):
        if len(kept_easy) >= easy_budget:
            break
        row_key = deterministic_row_key(row)
        if row_key in already_kept:
            continue
        kept_easy.append(row)
        already_kept.add(row_key)

    kept_negative_keys = {deterministic_row_key(row) for row in hard_negatives + kept_easy}
    kept_rows = [row for row in rows if normalize_text(row.get("bucket")) != "negative" or deterministic_row_key(row) in kept_negative_keys]
    dropped_easy = max(0, len(easy_negatives) - len(kept_easy))
    return kept_rows, {
        "original_negative_rows": len(negatives),
        "kept_negative_rows": len(hard_negatives) + len(kept_easy),
        "dropped_negative_rows": dropped_easy,
        "hard_negative_rows_kept": len(hard_negatives),
        "easy_negative_rows_kept": len(kept_easy),
        "easy_negative_rows_dropped": dropped_easy,
        "target_negative_budget": target_negative_budget,
    }


def summarize_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    bucket_counts: Counter[str] = Counter()
    env_counts: Counter[str] = Counter()
    target_action_rows = 0
    exact_positive_rows = 0
    near_miss_rows = 0
    weak_positive_rows = 0
    target_action_imputed_rows = 0
    for row in rows:
        bucket = str(row.get("bucket") or "unknown")
        if not row.get("target_action") and bucket == "exact_positive":
            model_action = str(row.get("model_action") or "").strip()
            if model_action:
                row["target_action"] = model_action
                meta = row.setdefault("meta", {})
                if isinstance(meta, dict):
                    meta["target_action_source"] = "model_action_exact_positive_imputation"
                target_action_imputed_rows += 1
        bucket_counts[bucket] += 1
        env_counts[str(row.get("source_env_name") or "unknown")] += 1
        if row.get("target_action"):
            target_action_rows += 1
        if bucket == "exact_positive":
            exact_positive_rows += 1
        if bucket == "near_miss":
            near_miss_rows += 1
        if bucket == "weak_positive":
            weak_positive_rows += 1
    return {
        "total_rows": len(rows),
        "bucket_counts": dict(bucket_counts),
        "source_env_counts": dict(env_counts),
        "target_action_rows": target_action_rows,
        "target_action_imputed_rows": target_action_imputed_rows,
        "target_action_coverage": round(target_action_rows / len(rows), 4) if rows else 0.0,
        "exact_positive_rows": exact_positive_rows,
        "near_miss_rows": near_miss_rows,
        "weak_positive_rows": weak_positive_rows,
    }


def apply_trainer_policy(rows: List[Dict[str, Any]], trainer_policy: Dict[str, Any]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    adjusted_rows: List[Dict[str, Any]] = []
    bucket_weight_totals: Dict[str, float] = defaultdict(float)
    bucket_weight_counts: Counter[str] = Counter()
    changed_rows = 0
    for row in rows:
        enriched = dict(row)
        prior_weight = safe_float(enriched.get("supervision_weight"), 0.0)
        bucket = str(enriched.get("bucket") or "unknown")
        if bucket == "exact_positive":
            floor_weight = safe_float(trainer_policy.get("exact_positive_weight"), prior_weight)
        elif bucket == "near_miss":
            floor_weight = safe_float(trainer_policy.get("near_miss_weight"), prior_weight)
        elif bucket == "weak_positive":
            floor_weight = safe_float(trainer_policy.get("weak_positive_weight"), prior_weight)
        else:
            floor_weight = safe_float(trainer_policy.get("negative_weight"), prior_weight)
        next_weight = max(prior_weight, floor_weight)
        if abs(next_weight - prior_weight) > 1e-9:
            changed_rows += 1
        enriched["supervision_weight"] = round(next_weight, 4)
        meta = dict(enriched.get("meta") or {})
        meta["trainer_policy_name"] = str(trainer_policy.get("policy_name") or "")
        meta["trainer_policy_bucket"] = bucket
        meta["trainer_policy_weight_floor"] = round(floor_weight, 4)
        meta["supervision_weight_source"] = "role_trainer_policy_floor"
        enriched["meta"] = meta
        adjusted_rows.append(enriched)
        bucket_weight_totals[bucket] += next_weight
        bucket_weight_counts[bucket] += 1
    return adjusted_rows, {
        "policy_name": str(trainer_policy.get("policy_name") or ""),
        "adjusted_rows": changed_rows,
        "bucket_weight_totals": {key: round(value, 4) for key, value in bucket_weight_totals.items()},
        "bucket_weight_averages": {
            key: round(bucket_weight_totals[key] / bucket_weight_counts[key], 4)
            for key in sorted(bucket_weight_counts)
            if bucket_weight_counts[key]
        },
    }


def merge_rows(
    cluster_id: str,
    stage_paths: List[Path],
    merged_path: Path,
    summary_path: Path,
    profile: Dict[str, Any],
) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for path in stage_paths:
        staged_rows = load_jsonl(path)
        rows.extend(staged_rows)
    rows = specialize_rows(cluster_id, rows)
    mined_rows, bucket_mining_summary = apply_bucket_mining(cluster_id, rows)
    amplified_rows, env_priority_summary = amplify_priority_rows(cluster_id, mined_rows)
    sampled_rows, negative_downsampling_summary = downsample_negative_rows(amplified_rows)
    pre_weight_summary = summarize_rows(sampled_rows)
    trainer_policy = build_trainer_policy(cluster_id, pre_weight_summary, profile)
    weighted_rows, training_weight_summary = apply_trainer_policy(sampled_rows, trainer_policy)
    write_jsonl(merged_path, weighted_rows)
    summary = {
        "output": str(merged_path),
        **summarize_rows(weighted_rows),
        "bucket_mining_summary": bucket_mining_summary,
        "env_priority_summary": env_priority_summary,
        "negative_downsampling_summary": negative_downsampling_summary,
        "trainer_policy": trainer_policy,
        "training_weight_summary": training_weight_summary,
    }
    write_json(summary_path, summary)
    return summary


def effective_holdout_ratio(merged_jsonl: Path, requested_ratio: float) -> float:
    rows = load_jsonl(merged_jsonl)
    if len(rows) <= 1:
        return 0.0
    target_eval = max(1, min(len(rows) - 1, round(len(rows) * requested_ratio)))
    values = sorted(stable_holdout_bucket(row) for row in rows)
    chosen = values[target_eval - 1]
    return min(chosen + 1e-9, 0.999999999)


def train_and_bench(
    work_dir: Path,
    merged_jsonl: Path,
    *,
    top_k: int,
    holdout_ratio: float,
    min_supervision_weight: float,
) -> Dict[str, Any]:
    model_dir = work_dir / "models"
    bench_dir = work_dir / "bench"
    model_dir.mkdir(parents=True, exist_ok=True)
    bench_dir.mkdir(parents=True, exist_ok=True)
    bench_holdout_ratio = effective_holdout_ratio(merged_jsonl, holdout_ratio)

    critic_summary = model_dir / "trm_critic.summary.json"
    critic_bench_summary = bench_dir / "trm_critic_bench.summary.json"
    retriever_summary = model_dir / "trm_retriever.summary.json"
    retriever_bench_summary = bench_dir / "trm_retriever_bench.summary.json"
    router_bench_summary = bench_dir / "trm_router_bench.summary.json"

    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "train_trm_critic.py"),
            "--input",
            str(merged_jsonl),
            "--output",
            str(model_dir / "trm_critic.json"),
            "--summary",
            str(critic_summary),
            "--k",
            str(top_k),
        ],
        cwd=ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "bench_trm_critic.py"),
            "--input",
            str(merged_jsonl),
            "--summary",
            str(critic_bench_summary),
            "--predictions",
            str(bench_dir / "trm_critic_bench.jsonl"),
            "--holdout-ratio",
            str(bench_holdout_ratio),
            "--k",
            str(top_k),
        ],
        cwd=ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "train_trm_retriever.py"),
            "--input",
            str(merged_jsonl),
            "--output",
            str(model_dir / "trm_retriever.json"),
            "--summary",
            str(retriever_summary),
            "--min-supervision-weight",
            str(min_supervision_weight),
        ],
        cwd=ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "bench_trm_retriever.py"),
            "--input",
            str(merged_jsonl),
            "--summary",
            str(retriever_bench_summary),
            "--predictions",
            str(bench_dir / "trm_retriever_bench.jsonl"),
            "--holdout-ratio",
            str(bench_holdout_ratio),
            "--min-supervision-weight",
            str(min_supervision_weight),
        ],
        cwd=ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "bench_trm_router.py"),
            "--input",
            str(merged_jsonl),
            "--summary",
            str(router_bench_summary),
            "--predictions",
            str(bench_dir / "trm_router_bench.jsonl"),
            "--holdout-ratio",
            str(bench_holdout_ratio),
            "--top-k",
            str(top_k),
            "--min-supervision-weight",
            str(min_supervision_weight),
        ],
        cwd=ROOT,
    )
    return {
        "bench_holdout_ratio": bench_holdout_ratio,
        "critic_train": load_json(critic_summary),
        "critic_bench": load_json(critic_bench_summary),
        "retriever_train": load_json(retriever_summary),
        "retriever_bench": load_json(retriever_bench_summary),
        "router_bench": load_json(router_bench_summary),
    }


def filter_clusters(manifest: Dict[str, Any], cluster_ids: List[str]) -> List[str]:
    available = set((manifest.get("env_clusters") or {}).keys())
    wanted = cluster_ids or list(manifest.get("recommended_parallel_training_clusters") or [])
    if not wanted:
        wanted = list(available)
    return [cluster_id for cluster_id in wanted if cluster_id in available]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and optionally train Primehub specialist TRM bundles by env cluster.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--cluster", action="append", default=[])
    parser.add_argument("--run-root", action="append", default=[])
    parser.add_argument("--stage-only", action="store_true")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    out_root = Path(args.out).resolve()
    manifest = load_json(manifest_path)
    run_roots = [Path(item).resolve() for item in (args.run_root or [])] or DEFAULT_RUN_ROOTS
    replays = discover_replays(run_roots)
    replay_index: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for replay in replays:
        replay_index[replay["env_name"]].append(replay)

    selected_clusters = filter_clusters(manifest, args.cluster)
    summary: Dict[str, Any] = {
        "manifest": str(manifest_path),
        "run_roots": [str(path) for path in run_roots],
        "replay_count": len(replays),
        "clusters": {},
    }

    cluster_profiles = manifest.get("cluster_profiles") or {}
    for cluster_id in selected_clusters:
        envs = list((manifest.get("env_clusters") or {}).get(cluster_id) or [])
        profile = dict(cluster_profiles.get(cluster_id) or {})
        cluster_dir = out_root / cluster_id
        stage_dir = cluster_dir / "stage"
        stage_dir.mkdir(parents=True, exist_ok=True)

        selected_replays: List[Dict[str, Any]] = []
        for env_name in envs:
            selected_replays.extend(replay_index.get(env_name, []))

        stage_records: List[Dict[str, Any]] = []
        stage_paths: List[Path] = []
        for replay in selected_replays:
            staged = stage_replay(
                Path(replay["path"]),
                stage_dir,
                task_family=str(profile.get("task_family_label") or f"primehub_{cluster_id}"),
            )
            stage_records.append({**replay, **staged})
            stage_paths.append(Path(staged["staged"]))

        merged_jsonl = cluster_dir / "cluster_merged.jsonl"
        merged_summary = cluster_dir / "cluster_merged.summary.json"
        merged = merge_rows(cluster_id, stage_paths, merged_jsonl, merged_summary, profile)

        cluster_payload: Dict[str, Any] = {
            "envs": envs,
            "profile": profile,
            "replays": len(selected_replays),
            "stage_manifest": stage_records,
            "merged": merged,
        }
        if not args.stage_only and merged["total_rows"] > 0:
            trainer_policy = dict(merged.get("trainer_policy") or {})
            cluster_payload["bench"] = train_and_bench(
                cluster_dir,
                merged_jsonl,
                top_k=int(trainer_policy.get("top_k") or profile.get("top_k") or 5),
                holdout_ratio=float(profile.get("holdout_ratio") or 0.2),
                min_supervision_weight=float(
                    trainer_policy.get("min_supervision_weight") or profile.get("min_supervision_weight") or 0.4
                ),
            )
        summary["clusters"][cluster_id] = cluster_payload

    role_imprint_json = out_root / "role_based_imprint.json"
    role_imprint_md = out_root / "role_based_imprint.md"
    role_imprint = build_role_imprint_payload(
        matrix_root=out_root,
        cluster_ids=selected_clusters,
        manifest_path=manifest_path,
    )
    write_json(role_imprint_json, role_imprint)
    role_imprint_md.write_text(render_role_imprint_markdown(role_imprint), encoding="utf-8")
    summary["role_based_imprint"] = {
        "json": str(role_imprint_json),
        "md": str(role_imprint_md),
        "clusters": sorted((role_imprint.get("cluster_cards") or {}).keys()),
    }

    write_json(out_root / "manifest.json", summary)
    print(str((out_root / "manifest.json").resolve()))


if __name__ == "__main__":
    main()
