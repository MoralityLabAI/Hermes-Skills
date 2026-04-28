from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


STUDY_DIR = Path(__file__).resolve().parent
REPO_ROOT = STUDY_DIR.parents[2]
HARNESS_ROOT = Path(r"C:/projects/trm_observability_harness")
DEFAULT_OUT_DIR = STUDY_DIR / "artifacts" / "primehub_external_abstraction_comparison"
DEFAULT_BASE_CORPUS = REPO_ROOT / "data" / "primehub_trm_autoresearch" / "cycle_12" / "primehub_trm_merged.jsonl"
DEFAULT_EXTERNAL_ABSTRACTION = STUDY_DIR / "artifacts" / "primehub_external_abstraction_bundle" / "primehub_external_abstraction_bundle.jsonl"
DEFAULT_EXTERNAL_CRITIC_SUPPORT = STUDY_DIR / "artifacts" / "primehub_external_critic_support_bundle" / "primehub_external_critic_support_bundle.jsonl"
DEFAULT_IFEVAL_ABSTRACTION = STUDY_DIR / "artifacts" / "primehub_external_ifeval_bundle" / "primehub_external_ifeval_bundle.jsonl"
DEFAULT_IFEVAL_CRITIC_SUPPORT = (
    STUDY_DIR / "artifacts" / "primehub_external_ifeval_critic_support_bundle" / "primehub_external_ifeval_critic_support_bundle.jsonl"
)
DEFAULT_AIME_ABSTRACTION = STUDY_DIR / "artifacts" / "primehub_external_aime2026_bundle" / "primehub_external_aime2026_bundle.jsonl"
DEFAULT_AIME_CRITIC_SUPPORT = (
    STUDY_DIR / "artifacts" / "primehub_external_aime2026_critic_support_bundle" / "primehub_external_aime2026_critic_support_bundle.jsonl"
)
DEFAULT_STRUCTURED_TRANSFER = STUDY_DIR / "artifacts" / "primehub_structured_map_transfer" / "metta_primehub_transfer_bundle.jsonl"
DEFAULT_IF_TRANSFER = STUDY_DIR / "artifacts" / "if_summarize_judge_transfer" / "metta_primehub_transfer_bundle.jsonl"

if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

from harness.trm_critic import TRMCritic  # noqa: E402
from harness.trm_retrieval import TRMRetriever, load_jsonl, normalize_text, stable_split  # noqa: E402


ALLOWED_BUCKETS = {
    "exact_positive": {"exact_positive", "near_miss", "weak_positive"},
    "near_miss": {"near_miss", "exact_positive", "weak_positive"},
    "weak_positive": {"weak_positive", "near_miss", "exact_positive"},
    "negative": set(),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare primehub external abstractions against the untouched external primehub holdout.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--base-corpus", default=str(DEFAULT_BASE_CORPUS))
    parser.add_argument("--external-abstraction", default=str(DEFAULT_EXTERNAL_ABSTRACTION))
    parser.add_argument("--external-critic-support", default=str(DEFAULT_EXTERNAL_CRITIC_SUPPORT))
    parser.add_argument("--ifeval-abstraction", default=str(DEFAULT_IFEVAL_ABSTRACTION))
    parser.add_argument("--ifeval-critic-support", default=str(DEFAULT_IFEVAL_CRITIC_SUPPORT))
    parser.add_argument("--aime-abstraction", default=str(DEFAULT_AIME_ABSTRACTION))
    parser.add_argument("--aime-critic-support", default=str(DEFAULT_AIME_CRITIC_SUPPORT))
    parser.add_argument("--structured-transfer", default=str(DEFAULT_STRUCTURED_TRANSFER))
    parser.add_argument("--if-transfer", default=str(DEFAULT_IF_TRANSFER))
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--holdout-ratio", type=float, default=0.2)
    parser.add_argument("--min-supervision-weight", type=float, default=0.4)
    parser.add_argument("--events-path", help="Optional JSONL event log path.")
    parser.add_argument("--summary-path", help="Optional summary JSON path.")
    parser.add_argument("--training-task-id", default="metta-primehub-external-abstraction-comparison-20260423")
    parser.add_argument("--checkpoint-interval", default="variant_complete")
    parser.add_argument("--chunk-strategy", default="variant_per_run")
    return parser.parse_args()


def run(cmd: List[str], *, cwd: Path) -> None:
    subprocess.run(cmd, cwd=str(cwd), check=True)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def emit_event(event_path: Path, event: str, **payload: Any) -> None:
    event_path.parent.mkdir(parents=True, exist_ok=True)
    row = {"ts": utc_now(), "event": event}
    row.update(payload)
    with event_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def merge_inputs(inputs: List[Path], out_jsonl: Path, out_summary: Path) -> None:
    cmd = [sys.executable, str(HARNESS_ROOT / "scripts" / "merge_trm_train_rows.py")]
    for input_path in inputs:
        cmd.extend(["--input", str(input_path)])
    cmd.extend(
        [
            "--output",
            str(out_jsonl),
            "--summary",
            str(out_summary),
            "--min-exact-positives-per-family",
            "2",
        ]
    )
    run(cmd, cwd=REPO_ROOT)


def run_rollup(
    *,
    input_path: Path,
    out_dir: Path,
    top_k: int,
    holdout_ratio: float,
    min_supervision_weight: float,
) -> Dict[str, Any]:
    model_dir = out_dir / "models"
    bench_dir = out_dir / "bench"
    model_dir.mkdir(parents=True, exist_ok=True)
    bench_dir.mkdir(parents=True, exist_ok=True)

    critic_model = model_dir / "trm_critic.json"
    critic_summary = model_dir / "trm_critic.summary.json"
    critic_bench_summary = bench_dir / "trm_critic_bench.summary.json"

    retriever_model = model_dir / "trm_retriever.json"
    retriever_summary = model_dir / "trm_retriever.summary.json"
    retriever_bench_summary = bench_dir / "trm_retriever_bench.summary.json"

    router_bench_summary = bench_dir / "trm_router_bench.summary.json"

    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "train_trm_critic.py"),
            "--input",
            str(input_path),
            "--output",
            str(critic_model),
            "--summary",
            str(critic_summary),
            "--k",
            str(top_k),
        ],
        cwd=REPO_ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "bench_trm_critic.py"),
            "--input",
            str(input_path),
            "--summary",
            str(critic_bench_summary),
            "--holdout-ratio",
            str(holdout_ratio),
            "--k",
            str(top_k),
        ],
        cwd=REPO_ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "train_trm_retriever.py"),
            "--input",
            str(input_path),
            "--output",
            str(retriever_model),
            "--summary",
            str(retriever_summary),
            "--min-supervision-weight",
            str(min_supervision_weight),
        ],
        cwd=REPO_ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "bench_trm_retriever.py"),
            "--input",
            str(input_path),
            "--summary",
            str(retriever_bench_summary),
            "--holdout-ratio",
            str(holdout_ratio),
            "--min-supervision-weight",
            str(min_supervision_weight),
        ],
        cwd=REPO_ROOT,
    )
    run(
        [
            sys.executable,
            str(HARNESS_ROOT / "scripts" / "bench_trm_router.py"),
            "--input",
            str(input_path),
            "--summary",
            str(router_bench_summary),
            "--holdout-ratio",
            str(holdout_ratio),
            "--top-k",
            str(top_k),
            "--min-supervision-weight",
            str(min_supervision_weight),
        ],
        cwd=REPO_ROOT,
    )

    return {
        "critic_model": str(critic_model),
        "critic_summary": json.loads(critic_summary.read_text(encoding="utf-8")),
        "critic_bench_summary": json.loads(critic_bench_summary.read_text(encoding="utf-8")),
        "retriever_model": str(retriever_model),
        "retriever_summary": json.loads(retriever_summary.read_text(encoding="utf-8")),
        "retriever_bench_summary": json.loads(retriever_bench_summary.read_text(encoding="utf-8")),
        "router_bench_summary": json.loads(router_bench_summary.read_text(encoding="utf-8")),
    }


def choose_gated_action(
    row: Dict[str, Any],
    *,
    retriever: TRMRetriever,
    critic: TRMCritic,
    top_k: int,
) -> Optional[str]:
    critic_pred = critic.predict(row)
    predicted_bucket = str(critic_pred["predicted_bucket"])
    allowed = ALLOWED_BUCKETS.get(predicted_bucket, set())
    if predicted_bucket == "negative" or not allowed:
        return None
    ranked = retriever.ranked_candidates(row, limit=top_k)
    for _, example in ranked:
        if example.bucket in allowed:
            return example.target_action
    if ranked:
        return ranked[0][1].target_action
    return None


def parse_ifeval_contract(action: Optional[str]) -> Dict[str, bool]:
    text = str(action or "").strip()
    if not text:
        return {
            "action_nonempty": False,
            "postscript_present": False,
            "postscript_last_line": False,
            "semantic_match": False,
            "contract_success": False,
        }

    normalized_lines = [line.strip() for line in text.splitlines() if line.strip()]
    last_line = normalized_lines[-1].lower() if normalized_lines else ""
    lowered = text.lower()
    postscript_prefix = "before i forget:"
    postscript_present = postscript_prefix in lowered
    postscript_last_line = last_line.startswith(postscript_prefix)
    semantic_region = lowered.split(postscript_prefix, 1)[0] if postscript_present else lowered
    semantic_match = bool(re.search(r"\bnegative\b", semantic_region)) and not bool(
        re.search(r"\bpositive\b", semantic_region)
    )
    contract_success = postscript_last_line and semantic_match
    return {
        "action_nonempty": True,
        "postscript_present": postscript_present,
        "postscript_last_line": postscript_last_line,
        "semantic_match": semantic_match,
        "contract_success": contract_success,
    }


def evaluate_ifeval_contract_subset(
    rows: List[Dict[str, Any]],
    *,
    retriever: TRMRetriever,
    critic: TRMCritic,
    top_k: int,
) -> Dict[str, Any]:
    if not rows:
        return {
            "rows": 0,
            "retrieval_contract_success_rate": None,
            "gated_contract_success_rate": None,
            "gated_postscript_present_rate": None,
            "gated_semantic_match_rate": None,
            "gated_action_nonempty_rate": None,
        }

    retrieval_contract_hits = 0
    gated_contract_hits = 0
    gated_postscript_hits = 0
    gated_semantic_hits = 0
    gated_nonempty_hits = 0

    for row in rows:
        retrieval_action, _, _ = retriever.predict(row)
        retrieval_eval = parse_ifeval_contract(retrieval_action)
        retrieval_contract_hits += int(retrieval_eval["contract_success"])

        gated_action = choose_gated_action(row, retriever=retriever, critic=critic, top_k=top_k)
        gated_eval = parse_ifeval_contract(gated_action)
        gated_contract_hits += int(gated_eval["contract_success"])
        gated_postscript_hits += int(gated_eval["postscript_present"])
        gated_semantic_hits += int(gated_eval["semantic_match"])
        gated_nonempty_hits += int(gated_eval["action_nonempty"])

    total = len(rows)
    return {
        "rows": total,
        "retrieval_contract_success_rate": round(retrieval_contract_hits / total, 4),
        "gated_contract_success_rate": round(gated_contract_hits / total, 4),
        "gated_postscript_present_rate": round(gated_postscript_hits / total, 4),
        "gated_semantic_match_rate": round(gated_semantic_hits / total, 4),
        "gated_action_nonempty_rate": round(gated_nonempty_hits / total, 4),
    }


def parse_aime_action(action: Optional[str], expected_integer: str = "39") -> Dict[str, bool]:
    text = str(action or "").strip()
    if not text:
        return {
            "action_nonempty": False,
            "box_present": False,
            "boxed_exact": False,
        }
    match = re.search(r"\\boxed\s*\{\s*([^{}]+?)\s*\}", text)
    if not match:
        return {
            "action_nonempty": True,
            "box_present": False,
            "boxed_exact": False,
        }
    boxed_value = match.group(1).strip()
    boxed_exact = boxed_value == expected_integer
    return {
        "action_nonempty": True,
        "box_present": True,
        "boxed_exact": boxed_exact,
    }


def evaluate_aime_subset(
    rows: List[Dict[str, Any]],
    *,
    retriever: TRMRetriever,
    critic: TRMCritic,
    top_k: int,
    expected_integer: str = "39",
) -> Dict[str, Any]:
    if not rows:
        return {
            "rows": 0,
            "retrieval_action_nonempty_rate": None,
            "retrieval_box_present_rate": None,
            "retrieval_boxed_exact_rate": None,
            "gated_action_nonempty_rate": None,
            "gated_box_present_rate": None,
            "gated_boxed_exact_rate": None,
        }

    retrieval_nonempty_hits = 0
    retrieval_box_hits = 0
    retrieval_exact_hits = 0
    gated_nonempty_hits = 0
    gated_box_hits = 0
    gated_exact_hits = 0

    for row in rows:
        retrieval_action, _, _ = retriever.predict(row)
        retrieval_eval = parse_aime_action(retrieval_action, expected_integer=expected_integer)
        retrieval_nonempty_hits += int(retrieval_eval["action_nonempty"])
        retrieval_box_hits += int(retrieval_eval["box_present"])
        retrieval_exact_hits += int(retrieval_eval["boxed_exact"])

        gated_action = choose_gated_action(row, retriever=retriever, critic=critic, top_k=top_k)
        gated_eval = parse_aime_action(gated_action, expected_integer=expected_integer)
        gated_nonempty_hits += int(gated_eval["action_nonempty"])
        gated_box_hits += int(gated_eval["box_present"])
        gated_exact_hits += int(gated_eval["boxed_exact"])

    total = len(rows)
    return {
        "rows": total,
        "retrieval_action_nonempty_rate": round(retrieval_nonempty_hits / total, 4),
        "retrieval_box_present_rate": round(retrieval_box_hits / total, 4),
        "retrieval_boxed_exact_rate": round(retrieval_exact_hits / total, 4),
        "gated_action_nonempty_rate": round(gated_nonempty_hits / total, 4),
        "gated_box_present_rate": round(gated_box_hits / total, 4),
        "gated_boxed_exact_rate": round(gated_exact_hits / total, 4),
    }


def evaluate_subset(
    rows: List[Dict[str, Any]],
    *,
    retriever: TRMRetriever,
    critic: TRMCritic,
    top_k: int,
) -> Dict[str, Any]:
    if not rows:
        return {
            "rows": 0,
            "critic_bucket_accuracy": None,
            "retriever_exact_match_rate": None,
            "router_retrieval_only_exact_match_rate": None,
            "router_critic_gated_exact_match_rate": None,
            "router_critic_gated_route_abstain_rate": None,
        }

    critic_hits = 0
    retrieval_hits = 0
    router_retrieval_hits = 0
    router_gated_hits = 0
    router_abstains = 0

    for row in rows:
        critic_pred = critic.predict(row)
        critic_hits += int(str(critic_pred["predicted_bucket"]) == str(row.get("bucket") or ""))

        base_action, _, _ = retriever.predict(row)
        gold_action = row.get("target_action")
        base_exact = bool(base_action) and normalize_text(base_action) == normalize_text(gold_action)
        retrieval_hits += int(base_exact)
        router_retrieval_hits += int(base_exact)

        gated_action = choose_gated_action(row, retriever=retriever, critic=critic, top_k=top_k)
        gated_exact = bool(gated_action) and normalize_text(gated_action) == normalize_text(gold_action)
        router_gated_hits += int(gated_exact)
        router_abstains += int(not gated_action)

    total = len(rows)
    return {
        "rows": total,
        "critic_bucket_accuracy": round(critic_hits / total, 4),
        "retriever_exact_match_rate": round(retrieval_hits / total, 4),
        "router_retrieval_only_exact_match_rate": round(router_retrieval_hits / total, 4),
        "router_critic_gated_exact_match_rate": round(router_gated_hits / total, 4),
        "router_critic_gated_route_abstain_rate": round(router_abstains / total, 4),
    }


def evaluate_original_subsets(
    *,
    merged_rows: List[Dict[str, Any]],
    holdout_ratio: float,
    top_k: int,
    min_supervision_weight: float,
    focus_envs: List[str],
) -> Dict[str, Any]:
    train_rows, eval_rows = stable_split(merged_rows, holdout_ratio)
    critic = TRMCritic.from_rows(train_rows, k=top_k)
    retriever = TRMRetriever.from_rows(
        train_rows,
        include_buckets=["exact_positive", "near_miss", "weak_positive"],
        min_supervision_weight=min_supervision_weight,
    )

    original_external = [
        row
        for row in eval_rows
        if str(row.get("source_env_type") or "") == "ExternalPrimeHubEnv"
        and str(row.get("task_family") or "") == "primehub"
    ]
    focus_external = [row for row in original_external if str(row.get("source_env_name") or "") in focus_envs]
    ifeval_external = [row for row in original_external if str(row.get("source_env_name") or "") == "allenai_ifeval"]
    aime_external = [row for row in original_external if str(row.get("source_env_name") or "") == "aime2026"]

    env_counts: Dict[str, int] = {}
    for row in original_external:
        env_id = str(row.get("source_env_name") or "")
        env_counts[env_id] = env_counts.get(env_id, 0) + 1

    focus_env_counts: Dict[str, int] = {}
    for row in focus_external:
        env_id = str(row.get("source_env_name") or "")
        focus_env_counts[env_id] = focus_env_counts.get(env_id, 0) + 1

    return {
        "original_external_primehub_eval": evaluate_subset(original_external, retriever=retriever, critic=critic, top_k=top_k),
        "original_external_focus_eval": evaluate_subset(focus_external, retriever=retriever, critic=critic, top_k=top_k),
        "original_external_ifeval_eval": evaluate_ifeval_contract_subset(
            ifeval_external,
            retriever=retriever,
            critic=critic,
            top_k=top_k,
        ),
        "original_external_aime_eval": evaluate_aime_subset(
            aime_external,
            retriever=retriever,
            critic=critic,
            top_k=top_k,
        ),
        "original_external_env_counts": env_counts,
        "original_external_focus_env_counts": focus_env_counts,
        "focus_envs": focus_envs,
    }


def metric_delta(current: Dict[str, Any], control: Dict[str, Any], keys: Iterable[str]) -> Dict[str, Any]:
    delta: Dict[str, Any] = {}
    for key in keys:
        cur = current.get(key)
        base = control.get(key)
        if isinstance(cur, (int, float)) and isinstance(base, (int, float)):
            delta[key] = round(cur - base, 4)
        else:
            delta[key] = None
    return delta


def build_markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# Primehub External Abstraction Comparison",
        "",
        "## Trainer Plan",
        "",
        f"- `training_task_id`: `{summary['trainer_plan']['training_task_id']}`",
        f"- `chunk_strategy`: `{summary['trainer_plan']['chunk_strategy']}`",
        f"- `checkpoint_interval`: `{summary['trainer_plan']['checkpoint_interval']}`",
        f"- `holdout_ratio`: `{summary['trainer_plan']['holdout_ratio']}`",
        f"- `top_k`: `{summary['trainer_plan']['top_k']}`",
        f"- `min_supervision_weight`: `{summary['trainer_plan']['min_supervision_weight']}`",
        "",
        "## Original External Primehub Holdout",
        "",
        "| Variant | Rows | Critic bucket acc | Retriever exact | Gated router exact | Gated abstain |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variant_name, variant in summary["variants"].items():
        subset = variant["subsets"]["original_external_primehub_eval"]
        lines.append(
            "| "
            + " | ".join(
                [
                    variant_name,
                    str(subset["rows"]),
                    f"{subset['critic_bucket_accuracy']:.4f}" if subset["critic_bucket_accuracy"] is not None else "n/a",
                    f"{subset['retriever_exact_match_rate']:.4f}" if subset["retriever_exact_match_rate"] is not None else "n/a",
                    f"{subset['router_critic_gated_exact_match_rate']:.4f}" if subset["router_critic_gated_exact_match_rate"] is not None else "n/a",
                    f"{subset['router_critic_gated_route_abstain_rate']:.4f}" if subset["router_critic_gated_route_abstain_rate"] is not None else "n/a",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Focus Env Holdout",
            "",
            f"Focus envs: {', '.join('`' + env + '`' for env in summary['focus_envs'])}",
            "",
            "| Variant | Rows | Critic bucket acc | Retriever exact | Gated router exact | Gated abstain |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for variant_name, variant in summary["variants"].items():
        subset = variant["subsets"]["original_external_focus_eval"]
        lines.append(
            "| "
            + " | ".join(
                [
                    variant_name,
                    str(subset["rows"]),
                    f"{subset['critic_bucket_accuracy']:.4f}" if subset["critic_bucket_accuracy"] is not None else "n/a",
                    f"{subset['retriever_exact_match_rate']:.4f}" if subset["retriever_exact_match_rate"] is not None else "n/a",
                    f"{subset['router_critic_gated_exact_match_rate']:.4f}" if subset["router_critic_gated_exact_match_rate"] is not None else "n/a",
                    f"{subset['router_critic_gated_route_abstain_rate']:.4f}" if subset["router_critic_gated_route_abstain_rate"] is not None else "n/a",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## AllenAI IFEval Contract Holdout",
            "",
            "| Variant | Rows | Retrieval contract | Gated contract | Gated postscript | Gated semantic | Gated nonempty |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for variant_name, variant in summary["variants"].items():
        subset = variant["subsets"]["original_external_ifeval_eval"]
        lines.append(
            "| "
            + " | ".join(
                [
                    variant_name,
                    str(subset["rows"]),
                    f"{subset['retrieval_contract_success_rate']:.4f}" if subset["retrieval_contract_success_rate"] is not None else "n/a",
                    f"{subset['gated_contract_success_rate']:.4f}" if subset["gated_contract_success_rate"] is not None else "n/a",
                    f"{subset['gated_postscript_present_rate']:.4f}" if subset["gated_postscript_present_rate"] is not None else "n/a",
                    f"{subset['gated_semantic_match_rate']:.4f}" if subset["gated_semantic_match_rate"] is not None else "n/a",
                    f"{subset['gated_action_nonempty_rate']:.4f}" if subset["gated_action_nonempty_rate"] is not None else "n/a",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## AIME2026 Numeric Holdout",
            "",
            "| Variant | Rows | Retrieval nonempty | Retrieval boxed | Retrieval exact | Gated nonempty | Gated boxed | Gated exact |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for variant_name, variant in summary["variants"].items():
        subset = variant["subsets"]["original_external_aime_eval"]
        lines.append(
            "| "
            + " | ".join(
                [
                    variant_name,
                    str(subset["rows"]),
                    f"{subset['retrieval_action_nonempty_rate']:.4f}" if subset["retrieval_action_nonempty_rate"] is not None else "n/a",
                    f"{subset['retrieval_box_present_rate']:.4f}" if subset["retrieval_box_present_rate"] is not None else "n/a",
                    f"{subset['retrieval_boxed_exact_rate']:.4f}" if subset["retrieval_boxed_exact_rate"] is not None else "n/a",
                    f"{subset['gated_action_nonempty_rate']:.4f}" if subset["gated_action_nonempty_rate"] is not None else "n/a",
                    f"{subset['gated_box_present_rate']:.4f}" if subset["gated_box_present_rate"] is not None else "n/a",
                    f"{subset['gated_boxed_exact_rate']:.4f}" if subset["gated_boxed_exact_rate"] is not None else "n/a",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Delta Vs Control On Original External Holdout",
            "",
            "| Variant | Critic bucket acc | Retriever exact | Gated router exact | Gated abstain |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for variant_name, delta in summary["control_deltas"].items():
        subset = delta["original_external_primehub_eval"]
        lines.append(
            "| "
            + " | ".join(
                [
                    variant_name,
                    f"{subset['critic_bucket_accuracy']:+.4f}" if subset["critic_bucket_accuracy"] is not None else "n/a",
                    f"{subset['retriever_exact_match_rate']:+.4f}" if subset["retriever_exact_match_rate"] is not None else "n/a",
                    f"{subset['router_critic_gated_exact_match_rate']:+.4f}" if subset["router_critic_gated_exact_match_rate"] is not None else "n/a",
                    f"{subset['router_critic_gated_route_abstain_rate']:+.4f}" if subset["router_critic_gated_route_abstain_rate"] is not None else "n/a",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Delta Vs Control On AllenAI IFEval Contract Holdout",
            "",
            "| Variant | Retrieval contract | Gated contract | Gated postscript | Gated semantic | Gated nonempty |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for variant_name, delta in summary["control_deltas"].items():
        subset = delta["original_external_ifeval_eval"]
        lines.append(
            "| "
            + " | ".join(
                [
                    variant_name,
                    f"{subset['retrieval_contract_success_rate']:+.4f}" if subset["retrieval_contract_success_rate"] is not None else "n/a",
                    f"{subset['gated_contract_success_rate']:+.4f}" if subset["gated_contract_success_rate"] is not None else "n/a",
                    f"{subset['gated_postscript_present_rate']:+.4f}" if subset["gated_postscript_present_rate"] is not None else "n/a",
                    f"{subset['gated_semantic_match_rate']:+.4f}" if subset["gated_semantic_match_rate"] is not None else "n/a",
                    f"{subset['gated_action_nonempty_rate']:+.4f}" if subset["gated_action_nonempty_rate"] is not None else "n/a",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Delta Vs Control On AIME2026 Numeric Holdout",
            "",
            "| Variant | Retrieval nonempty | Retrieval boxed | Retrieval exact | Gated nonempty | Gated boxed | Gated exact |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for variant_name, delta in summary["control_deltas"].items():
        subset = delta["original_external_aime_eval"]
        lines.append(
            "| "
            + " | ".join(
                [
                    variant_name,
                    f"{subset['retrieval_action_nonempty_rate']:+.4f}" if subset["retrieval_action_nonempty_rate"] is not None else "n/a",
                    f"{subset['retrieval_box_present_rate']:+.4f}" if subset["retrieval_box_present_rate"] is not None else "n/a",
                    f"{subset['retrieval_boxed_exact_rate']:+.4f}" if subset["retrieval_boxed_exact_rate"] is not None else "n/a",
                    f"{subset['gated_action_nonempty_rate']:+.4f}" if subset["gated_action_nonempty_rate"] is not None else "n/a",
                    f"{subset['gated_box_present_rate']:+.4f}" if subset["gated_box_present_rate"] is not None else "n/a",
                    f"{subset['gated_boxed_exact_rate']:+.4f}" if subset["gated_boxed_exact_rate"] is not None else "n/a",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Readout",
            "",
            f"- Original external primehub holdout rows: `{summary['variants']['control']['subsets']['original_external_primehub_eval']['rows']}`.",
            f"- Best original external lift variant: `{summary['best_original_variant']}`.",
            f"- Best allenai_ifeval contract variant: `{summary['best_ifeval_variant']}`.",
            f"- Best aime2026 numeric variant: `{summary['best_aime_variant']}`.",
            f"- Original external env counts: `{summary['variants']['control']['subsets']['original_external_env_counts']}`.",
            f"- Focus-env overlap in the original holdout: `{summary['variants']['control']['subsets']['original_external_focus_env_counts']}`.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    events_path = Path(args.events_path).resolve() if args.events_path else out_dir / "comparison.events.jsonl"
    summary_path = Path(args.summary_path).resolve() if args.summary_path else out_dir / "comparison.summary.json"
    if events_path.exists():
        events_path.unlink()

    base_corpus = Path(args.base_corpus).resolve()
    external_abstraction = Path(args.external_abstraction).resolve()
    external_critic_support = Path(args.external_critic_support).resolve()
    ifeval_abstraction = Path(args.ifeval_abstraction).resolve()
    ifeval_critic_support = Path(args.ifeval_critic_support).resolve()
    aime_abstraction = Path(args.aime_abstraction).resolve()
    aime_critic_support = Path(args.aime_critic_support).resolve()
    structured_transfer = Path(args.structured_transfer).resolve()
    if_transfer = Path(args.if_transfer).resolve()

    trainer_plan = {
        "training_task_id": args.training_task_id,
        "checkpoint_interval": args.checkpoint_interval,
        "chunk_strategy": args.chunk_strategy,
        "holdout_ratio": args.holdout_ratio,
        "top_k": args.top_k,
        "min_supervision_weight": args.min_supervision_weight,
        "base_corpus": str(base_corpus),
        "external_abstraction": str(external_abstraction),
        "external_critic_support": str(external_critic_support),
        "ifeval_abstraction": str(ifeval_abstraction),
        "ifeval_critic_support": str(ifeval_critic_support),
        "aime_abstraction": str(aime_abstraction),
        "aime_critic_support": str(aime_critic_support),
        "structured_transfer": str(structured_transfer),
        "if_transfer": str(if_transfer),
    }
    emit_event(events_path, "trainer_plan", trainer_plan=trainer_plan)

    variants = [
        ("control", [base_corpus]),
        ("control_plus_external_abstraction", [base_corpus, external_abstraction]),
    ]
    if external_critic_support.exists():
        variants.append(
            (
                "control_plus_external_abstraction_and_critic_support",
                [base_corpus, external_abstraction, external_critic_support],
            )
        )
    variants.append(
        (
            "control_plus_external_and_all_transfer",
            [base_corpus, external_abstraction, structured_transfer, if_transfer],
        )
    )
    if external_critic_support.exists():
        variants.append(
            (
                "control_plus_external_critic_and_all_transfer",
                [base_corpus, external_abstraction, external_critic_support, structured_transfer, if_transfer],
            )
        )
    if ifeval_abstraction.exists() and external_critic_support.exists():
        variants.append(
            (
                "control_plus_external_abstraction_and_critic_support_and_ifeval_abstraction",
                [base_corpus, external_abstraction, external_critic_support, ifeval_abstraction],
            )
        )
    if ifeval_abstraction.exists() and ifeval_critic_support.exists() and external_critic_support.exists():
        variants.append(
            (
                "control_plus_external_abstraction_and_critic_support_and_ifeval_stack",
                [base_corpus, external_abstraction, external_critic_support, ifeval_abstraction, ifeval_critic_support],
            )
        )
    if aime_abstraction.exists() and external_critic_support.exists():
        variants.append(
            (
                "control_plus_external_abstraction_and_critic_support_and_aime_abstraction",
                [base_corpus, external_abstraction, external_critic_support, aime_abstraction],
            )
        )
    if aime_abstraction.exists() and aime_critic_support.exists() and external_critic_support.exists():
        variants.append(
            (
                "control_plus_external_abstraction_and_critic_support_and_aime_stack",
                [base_corpus, external_abstraction, external_critic_support, aime_abstraction, aime_critic_support],
            )
        )

    focus_envs = sorted(
        {
            str(row.get("source_env_name") or "")
            for path in [
                external_abstraction,
                external_critic_support,
                ifeval_abstraction,
                ifeval_critic_support,
                aime_abstraction,
                aime_critic_support,
                structured_transfer,
                if_transfer,
            ]
            if path.exists()
            for row in load_jsonl(path)
            if str(row.get("source_env_name") or "").strip()
        }
    )

    variant_results: Dict[str, Any] = {}
    for variant_name, inputs in variants:
        variant_dir = out_dir / "variants" / variant_name
        merged_path = variant_dir / "merged.jsonl"
        merged_summary_path = variant_dir / "merged.summary.json"
        emit_event(events_path, "variant_start", variant=variant_name, inputs=[str(path) for path in inputs])
        merge_inputs(inputs, merged_path, merged_summary_path)
        emit_event(events_path, "checkpoint", variant=variant_name, checkpoint="merged", output=str(merged_path))
        rollup = run_rollup(
            input_path=merged_path,
            out_dir=variant_dir,
            top_k=args.top_k,
            holdout_ratio=args.holdout_ratio,
            min_supervision_weight=args.min_supervision_weight,
        )
        merged_rows = load_jsonl(merged_path)
        subsets = evaluate_original_subsets(
            merged_rows=merged_rows,
            holdout_ratio=args.holdout_ratio,
            top_k=args.top_k,
            min_supervision_weight=args.min_supervision_weight,
            focus_envs=focus_envs,
        )
        variant_results[variant_name] = {
            "merged_summary": json.loads(merged_summary_path.read_text(encoding="utf-8")),
            "global": {
                "critic_bucket_accuracy": rollup["critic_bench_summary"]["bucket_accuracy"],
                "retriever_exact_match_rate": rollup["retriever_bench_summary"]["exact_match_rate"],
                "router_critic_gated_exact_match_rate": rollup["router_bench_summary"]["critic_gated"]["exact_match_rate"],
                "router_critic_gated_route_abstain_rate": rollup["router_bench_summary"]["critic_gated"]["route_abstain_rate"],
            },
            "subsets": subsets,
            "artifacts": rollup,
        }
        emit_event(
            events_path,
            "variant_complete",
            variant=variant_name,
            total_rows=variant_results[variant_name]["merged_summary"]["total_rows"],
            original_external_critic_bucket_accuracy=subsets["original_external_primehub_eval"]["critic_bucket_accuracy"],
            original_external_router_exact=subsets["original_external_primehub_eval"]["router_critic_gated_exact_match_rate"],
        )

    control = variant_results["control"]
    delta_keys = [
        "critic_bucket_accuracy",
        "retriever_exact_match_rate",
        "router_retrieval_only_exact_match_rate",
        "router_critic_gated_exact_match_rate",
        "router_critic_gated_route_abstain_rate",
    ]
    control_deltas: Dict[str, Any] = {}
    for variant_name, variant in variant_results.items():
        if variant_name == "control":
            continue
        control_deltas[variant_name] = {
            "original_external_primehub_eval": metric_delta(
                variant["subsets"]["original_external_primehub_eval"],
                control["subsets"]["original_external_primehub_eval"],
                delta_keys,
            ),
            "original_external_focus_eval": metric_delta(
                variant["subsets"]["original_external_focus_eval"],
                control["subsets"]["original_external_focus_eval"],
                delta_keys,
            ),
            "original_external_ifeval_eval": metric_delta(
                variant["subsets"]["original_external_ifeval_eval"],
                control["subsets"]["original_external_ifeval_eval"],
                [
                    "retrieval_contract_success_rate",
                    "gated_contract_success_rate",
                    "gated_postscript_present_rate",
                    "gated_semantic_match_rate",
                    "gated_action_nonempty_rate",
                ],
            ),
            "original_external_aime_eval": metric_delta(
                variant["subsets"]["original_external_aime_eval"],
                control["subsets"]["original_external_aime_eval"],
                [
                    "retrieval_action_nonempty_rate",
                    "retrieval_box_present_rate",
                    "retrieval_boxed_exact_rate",
                    "gated_action_nonempty_rate",
                    "gated_box_present_rate",
                    "gated_boxed_exact_rate",
                ],
            ),
        }

    best_original_variant = max(
        control_deltas,
        key=lambda item: (
            control_deltas[item]["original_external_primehub_eval"]["router_critic_gated_exact_match_rate"] or -999.0,
            control_deltas[item]["original_external_primehub_eval"]["critic_bucket_accuracy"] or -999.0,
            control_deltas[item]["original_external_primehub_eval"]["retriever_exact_match_rate"] or -999.0,
        ),
    )
    best_ifeval_variant = max(
        control_deltas,
        key=lambda item: (
            control_deltas[item]["original_external_ifeval_eval"]["gated_contract_success_rate"] or -999.0,
            control_deltas[item]["original_external_ifeval_eval"]["gated_postscript_present_rate"] or -999.0,
            control_deltas[item]["original_external_ifeval_eval"]["gated_action_nonempty_rate"] or -999.0,
        ),
    )
    best_aime_variant = max(
        control_deltas,
        key=lambda item: (
            control_deltas[item]["original_external_aime_eval"]["gated_boxed_exact_rate"] or -999.0,
            control_deltas[item]["original_external_aime_eval"]["gated_box_present_rate"] or -999.0,
            control_deltas[item]["original_external_aime_eval"]["gated_action_nonempty_rate"] or -999.0,
        ),
    )

    summary = {
        "generated_at_utc": utc_now(),
        "trainer_plan": trainer_plan,
        "focus_envs": focus_envs,
        "variants": variant_results,
        "control_deltas": control_deltas,
        "best_original_variant": best_original_variant,
        "best_ifeval_variant": best_ifeval_variant,
        "best_aime_variant": best_aime_variant,
    }
    write_json(summary_path, summary)
    write_markdown(out_dir / "comparison.findings.md", build_markdown(summary))
    emit_event(events_path, "done", summary_path=str(summary_path))
    print(str(summary_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
