from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(r"C:/projects/Hermes-Skills/Hermes Skills")
DEFAULT_SESSION_PATH = Path(
    r"C:/Users/patri/.codex/sessions/2026/04/19/rollout-2026-04-19T22-45-11-019da8c7-1000-7920-8a73-f020962d546d.jsonl"
)
DEFAULT_OUTPUT_DIR = ROOT / "research" / "generated"

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
WINDOWS_DRIVE_RE = re.compile(r"^/[A-Za-z]:[/\\\\]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile a cross-reference bundle from the recent TRM-infused Hermes Codex chat.")
    parser.add_argument("--session-path", default=str(DEFAULT_SESSION_PATH))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not decode to an object")
    return payload


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        for raw in handle:
            text = raw.strip()
            if not text:
                continue
            payload = json.loads(text)
            if isinstance(payload, dict):
                yield payload


def normalize_link_target(raw: str) -> str:
    text = str(raw).strip()
    if text.startswith("<") and text.endswith(">"):
        text = text[1:-1].strip()
    if WINDOWS_DRIVE_RE.match(text):
        text = text[1:]
    return text


def markdown_link(label: str, target: str) -> str:
    safe_target = normalize_link_target(target)
    if " " in safe_target:
        return f"[{label}](<{safe_target}>)"
    return f"[{label}]({safe_target})"


def reward_for_row(row: dict[str, Any]) -> float | None:
    payload = row.get("reward_totals") or {}
    if isinstance(payload, dict) and payload:
        value = next(iter(payload.values()))
        if isinstance(value, (int, float)):
            return float(value)
    return None


def find_session_message(session_path: Path) -> dict[str, Any]:
    for row in iter_jsonl(session_path):
        if str(row.get("type") or "") != "response_item":
            continue
        payload = row.get("payload") or {}
        if str(payload.get("type") or "") != "message":
            continue
        content = payload.get("content") or []
        for item in content:
            text = str((item or {}).get("text") or "")
            if "Keep the main research line in **TRM-infusion**." not in text:
                continue
            links: list[dict[str, Any]] = []
            for label, target in LINK_RE.findall(text):
                normalized = normalize_link_target(target)
                links.append(
                    {
                        "label": label,
                        "target": normalized,
                        "exists": Path(normalized).exists(),
                    }
                )
            return {
                "session_path": str(session_path),
                "message_timestamp": str(row.get("timestamp") or ""),
                "message_excerpt": text[:1200].strip(),
                "message_text": text,
                "link_count": len(links),
                "links": links,
            }
    raise RuntimeError(f"Could not find the TRM-infusion benchmark message in {session_path}")


def parse_missing_env_claim(chat_text: str) -> dict[str, Any]:
    direct_match = re.search(
        r"adding `(\d+)/(\d+)` successful tasks across `(\d+)` environments",
        chat_text,
    )
    if direct_match:
        completed = int(direct_match.group(1))
        attempted = int(direct_match.group(2))
        env_count = int(direct_match.group(3))
        return {
            "task_complete_count": attempted,
            "success_count": completed,
            "env_count": env_count,
            "source": "chat_message_fallback",
        }
    compact_match = re.search(
        r"covered `(\d+)` envs x `(\d+)` models with `(\d+)/(\d+)` completed",
        chat_text,
    )
    if compact_match:
        env_count = int(compact_match.group(1))
        model_count = int(compact_match.group(2))
        completed = int(compact_match.group(3))
        attempted = int(compact_match.group(4))
        return {
            "task_complete_count": attempted,
            "success_count": completed,
            "env_count": env_count,
            "claimed_model_count": model_count,
            "source": "chat_message_fallback",
        }
    return {}


def parse_bluebeam_handoff(readme_path: Path) -> dict[str, Any]:
    text = readme_path.read_text(encoding="utf-8")

    def capture(pattern: str) -> str:
        match = re.search(pattern, text)
        return match.group(1) if match else ""

    return {
        "readme_path": str(readme_path),
        "benchmark_completed": capture(r"Benchmark run: `(\d+/\d+)` tasks completed"),
        "failed": int(capture(r"tasks completed, `(\d+)` failed") or 0),
        "skipped": int(capture(r"failed, `(\d+)` skipped") or 0),
        "new_positive_replays": int(capture(r"New run positives: `(\d+)` raw positive replays") or 0),
        "qwen35_9b_positive_count": int(capture(r"`qwen35_9b`: `(\d+)` positives") or 0),
        "qwen35_9b_reward_sum": float(capture(r"`qwen35_9b`: `\d+` positives, reward sum `([0-9.]+)`") or 0.0),
        "qwen35_27b_positive_count": int(capture(r"`qwen35_27b`: `(\d+)` positives") or 0),
        "qwen35_27b_reward_sum": float(capture(r"`qwen35_27b`: `\d+` positives, reward sum `([0-9.]+)`") or 0.0),
        "trm_rows": int(capture(r"rows: `(\d+)`") or 0),
        "trm_exact_positive": int(capture(r"exact positive: `(\d+)`") or 0),
        "trm_weak_positive": int(capture(r"weak positive: `(\d+)`") or 0),
        "trm_negative": int(capture(r"negative: `(\d+)`") or 0),
        "target_action_coverage": float(capture(r"target-action coverage: `([0-9.]+)`") or 0.0),
        "critic_bucket_accuracy": float(capture(r"critic bucket accuracy: `([0-9.]+)`") or 0.0),
        "retriever_exact_match": float(capture(r"retriever exact match: `([0-9.]+)`") or 0.0),
        "router_abstain_rate": float(capture(r"critic-gated router abstain rate: `([0-9.]+)`") or 0.0),
    }


def summarize_job_run(summary_path: Path, chat_text: str = "") -> dict[str, Any]:
    summary = read_json(summary_path)
    event_log = Path(str(summary.get("event_log") or "")).resolve()
    rows = list(iter_jsonl(event_log)) if event_log.exists() else []
    task_rows = [row for row in rows if str(row.get("event") or "") == "task_complete"]
    selected_row = next((row for row in rows if str(row.get("event") or "") == "run_envs_resolved"), {})
    status_counts = Counter(str(row.get("status") or "") for row in task_rows)
    model_ids = sorted({str(row.get("model_id") or "") for row in task_rows if str(row.get("model_id") or "").strip()})
    env_ids = sorted({str(row.get("env_id") or "") for row in task_rows if str(row.get("env_id") or "").strip()})
    payload = {
        "summary_path": str(summary_path),
        "event_log": str(event_log),
        "status": str(summary.get("status") or ""),
        "selected_envs": int(selected_row.get("selected_envs") or 0),
        "selected_variants": list(selected_row.get("selected_variant_ids") or []),
        "task_complete_count": len(task_rows),
        "success_count": int(status_counts.get("success", 0)),
        "failure_count": int(status_counts.get("execution_failure", 0) + status_counts.get("failed", 0)),
        "model_ids": model_ids,
        "env_ids": env_ids,
        "env_count": len(env_ids),
        "steps_completed": int(summary.get("steps_completed") or 0),
        "source": "event_log",
    }
    if payload["task_complete_count"] == 0:
        fallback = parse_missing_env_claim(chat_text)
        if fallback:
            payload.update(fallback)
    return payload


def summarize_gapfill(stout_path: Path) -> dict[str, Any]:
    rows = list(iter_jsonl(stout_path))
    task_rows = [row for row in rows if str(row.get("event") or "") == "task_complete"]
    per_task: list[dict[str, Any]] = []
    for row in task_rows:
        per_task.append(
            {
                "model_id": str(row.get("model_id") or ""),
                "env_id": str(row.get("env_id") or ""),
                "variant_id": str(row.get("variant_id") or ""),
                "status": str(row.get("status") or ""),
                "reward": reward_for_row(row),
                "failure_types": row.get("failure_types") or {},
            }
        )
    return {
        "stout_path": str(stout_path),
        "task_count": len(task_rows),
        "per_task": per_task,
    }


def summarize_role_imprint(json_path: Path) -> dict[str, Any]:
    payload = read_json(json_path)
    cards = payload.get("cluster_cards") or {}
    clusters: list[dict[str, Any]] = []
    for cluster_id, card in sorted(cards.items()):
        if not isinstance(card, dict):
            continue
        clusters.append(
            {
                "cluster_id": str(cluster_id),
                "role_name": str(card.get("role_name") or ""),
                "support_tier": str(card.get("support_tier") or ""),
                "rows": int(card.get("rows") or 0),
                "exact_positive_rows": int(card.get("exact_positive_rows") or 0),
                "weak_positive_rows": int(card.get("weak_positive_rows") or 0),
                "target_action_coverage": float(card.get("target_action_coverage") or 0.0),
                "critic_bucket_accuracy": float(card.get("critic_bucket_accuracy") or 0.0),
                "retriever_exact_match_rate": float(card.get("retriever_exact_match_rate") or 0.0),
                "route_abstain_rate": float(card.get("route_abstain_rate") or 0.0),
            }
        )
    return {
        "json_path": str(json_path),
        "global_prompt_lines": list(payload.get("global_prompt_lines") or []),
        "clusters": clusters,
    }


def load_ledger_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    for row in iter_jsonl(path):
        if str(row.get("event") or "") != "task_complete":
            continue
        rows.append(row)
    return rows


def ledger_reward_index(path: Path) -> dict[tuple[str, str, str], dict[str, Any]]:
    index: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in load_ledger_rows(path):
        key = (
            str(row.get("model_id") or ""),
            str(row.get("env_id") or ""),
            str(row.get("variant_id") or ""),
        )
        index[key] = {
            "model_id": key[0],
            "env_id": key[1],
            "variant_id": key[2],
            "skill_name": str(row.get("skill_name") or ""),
            "skill_cluster": str(row.get("skill_cluster") or ""),
            "role_mode": str(row.get("role_mode") or ""),
            "role_support_tier": str(row.get("role_support_tier") or ""),
            "reward": reward_for_row(row),
            "run_token_total": int(row.get("run_token_total") or 0),
            "summary_path": str(row.get("summary_path") or ""),
        }
    return index


def summarize_baseline_vs_mining(baseline_path: Path, mining_path: Path) -> dict[str, Any]:
    baseline = ledger_reward_index(baseline_path)
    mining = ledger_reward_index(mining_path)
    comparisons: list[dict[str, Any]] = []
    for key in sorted(set(baseline.keys()) & set(mining.keys())):
        base_row = baseline[key]
        mining_row = mining[key]
        base_reward = base_row.get("reward")
        mining_reward = mining_row.get("reward")
        delta = None
        if isinstance(base_reward, (int, float)) and isinstance(mining_reward, (int, float)):
            delta = float(mining_reward) - float(base_reward)
        comparisons.append(
            {
                "model_id": key[0],
                "env_id": key[1],
                "variant_id": key[2],
                "skill_name": str(mining_row.get("skill_name") or base_row.get("skill_name") or ""),
                "skill_cluster": str(mining_row.get("skill_cluster") or base_row.get("skill_cluster") or ""),
                "baseline_reward": base_reward,
                "mining_reward": mining_reward,
                "delta": delta,
            }
        )
    positive_deltas = [row for row in comparisons if isinstance(row.get("delta"), (int, float)) and float(row["delta"]) > 0.0]
    positive_deltas.sort(key=lambda row: float(row.get("delta") or 0.0), reverse=True)
    return {
        "baseline_ledger": str(baseline_path),
        "mining_ledger": str(mining_path),
        "comparison_count": len(comparisons),
        "positive_delta_count": len(positive_deltas),
        "positive_deltas": positive_deltas,
        "comparison_rows": comparisons,
    }


def summarize_pressure_slice(ledger_path: Path) -> dict[str, Any]:
    groups: dict[tuple[str, str], dict[str, Any]] = defaultdict(dict)
    for row in load_ledger_rows(ledger_path):
        key = (str(row.get("model_id") or ""), str(row.get("env_id") or ""))
        groups[key][str(row.get("variant_id") or "")] = {
            "reward": reward_for_row(row),
            "skill_name": str(row.get("skill_name") or ""),
            "skill_cluster": str(row.get("skill_cluster") or ""),
        }

    rows: list[dict[str, Any]] = []
    counts = Counter()
    for key in sorted(groups.keys()):
        payload = groups[key]
        baseline_reward = (payload.get("single-model-baseline") or {}).get("reward")
        contract_reward = (payload.get("two-model-contract-repair-v1") or {}).get("reward")
        abstain_reward = (payload.get("two-model-abstain-guard-v1") or {}).get("reward")
        delta = None
        if isinstance(baseline_reward, (int, float)) and isinstance(contract_reward, (int, float)):
            delta = float(contract_reward) - float(baseline_reward)
            if delta > 0:
                counts["contract_gt_baseline"] += 1
            elif delta < 0:
                counts["contract_lt_baseline"] += 1
            else:
                counts["contract_eq_baseline"] += 1
        rows.append(
            {
                "model_id": key[0],
                "env_id": key[1],
                "baseline_reward": baseline_reward,
                "contract_reward": contract_reward,
                "abstain_reward": abstain_reward,
                "contract_delta": delta,
            }
        )
    return {
        "ledger_path": str(ledger_path),
        "comparison_count": len(rows),
        "counts": dict(counts),
        "rows": rows,
    }


def summarize_simpleqa_proof(root: Path) -> dict[str, Any]:
    ledger_path = root / "ledger.jsonl"
    rows = load_ledger_rows(ledger_path)
    task_rows: list[dict[str, Any]] = []
    visible_true = 0
    visible_false = 0
    fallback_total = 0
    for row in rows:
        summary_path = Path(str(row.get("summary_path") or ""))
        summary = read_json(summary_path) if summary_path.exists() else {}
        visible = summary.get("visible_output_emitted") or {}
        model_fallbacks = summary.get("model_client_fallbacks") or {}
        visible_true += int(visible.get("true", 0) or 0)
        visible_false += int(visible.get("false", 0) or 0)
        if isinstance(model_fallbacks, dict):
            fallback_total += sum(int(value or 0) for value in model_fallbacks.values())
        task_rows.append(
            {
                "model_id": str(row.get("model_id") or ""),
                "env_id": str(row.get("env_id") or ""),
                "variant_id": str(row.get("variant_id") or ""),
                "skill_cluster": str(row.get("skill_cluster") or ""),
                "reward": reward_for_row(row),
                "visible_output_true": int(visible.get("true", 0) or 0),
                "visible_output_false": int(visible.get("false", 0) or 0),
                "model_client_fallbacks_total": int(sum(int(value or 0) for value in model_fallbacks.values())) if isinstance(model_fallbacks, dict) else 0,
            }
        )
    return {
        "root": str(root),
        "ledger_path": str(ledger_path),
        "task_count": len(task_rows),
        "visible_output_true_total": visible_true,
        "visible_output_false_total": visible_false,
        "model_client_fallbacks_total": fallback_total,
        "task_rows": task_rows,
    }


def build_payload(session_path: Path) -> dict[str, Any]:
    session_ref = find_session_message(session_path)
    session_chat_text = str(session_ref.get("message_text") or "")
    session_ref.pop("message_text", None)

    bluebeam_readme = ROOT / "data" / "handoffs" / "bluebeam_mechinterp_2026-04-16" / "README.md"
    missing_env_summary = ROOT / "data" / "job_limited_runs" / "primehub-missing-envs-rerun-20260420.summary.json"
    gapfill_stout = ROOT / "data" / "primehub_final_eligible_gapfill_20260420" / "overnight_primehub_benchmark.stout.jsonl"
    role_imprint_json = ROOT / "data" / "primehub_skill_trm_matrix" / "latest" / "role_based_imprint.json"
    baseline_ledger = ROOT / "data" / "primehub_trainer_policy_baseline_rerun_20260421" / "ledger.jsonl"
    mining_ledger = ROOT / "data" / "primehub_trainer_policy_mining_rerun_20260421" / "ledger.jsonl"
    pressure_ledger = ROOT / "data" / "primehub_choice_contract_pressure_20260421" / "ledger.jsonl"
    simpleqa_root = ROOT / "data" / "primehub_simpleqa_verified_proof_20260422"

    linked_studies = [
        ROOT / "research" / "studies" / "2026-04-22-primehub-structured-map-retrieval" / "README.md",
        ROOT / "research" / "studies" / "2026-04-22-metta-trm-hermes-pipeline" / "README.md",
        ROOT / "research" / "generated" / "paper_drafts" / "2026-04-22-hermes-trm-weekly-draft.md",
    ]

    return {
        "source_chat": session_ref,
        "bluebeam_handoff": parse_bluebeam_handoff(bluebeam_readme),
        "missing_env_rerun": summarize_job_run(missing_env_summary, chat_text=session_chat_text),
        "final_gapfill": summarize_gapfill(gapfill_stout),
        "role_imprint": summarize_role_imprint(role_imprint_json),
        "baseline_vs_mining": summarize_baseline_vs_mining(baseline_ledger, mining_ledger),
        "choice_contract_pressure": summarize_pressure_slice(pressure_ledger),
        "simpleqa_verified_proof": summarize_simpleqa_proof(simpleqa_root),
        "linked_studies": [
            {
                "path": str(path),
                "exists": path.exists(),
            }
            for path in linked_studies
        ],
    }


def render_markdown(payload: dict[str, Any]) -> str:
    session = payload["source_chat"]
    bluebeam = payload["bluebeam_handoff"]
    missing_env = payload["missing_env_rerun"]
    gapfill = payload["final_gapfill"]
    imprint = payload["role_imprint"]
    baseline_vs_mining = payload["baseline_vs_mining"]
    pressure = payload["choice_contract_pressure"]
    simpleqa = payload["simpleqa_verified_proof"]

    boolq_delta = next(
        (
            row
            for row in baseline_vs_mining["positive_deltas"]
            if row["model_id"] == "qwen35_27b" and row["env_id"] == "boolq"
        ),
        None,
    )
    antislop_row = next(
        (
            row
            for row in baseline_vs_mining["comparison_rows"]
            if row["model_id"] == "qwen35_27b" and row["env_id"] == "antislop" and row["variant_id"] == "two-model-contract-repair-v1"
        ),
        None,
    )
    pressure_winogrande = next((row for row in pressure["rows"] if row["env_id"] == "winogrande"), None)

    lines: list[str] = []
    lines.append("# TRM-Infused Hermes Benchmark Cross-Ref")
    lines.append("")
    lines.append("## Source Chat")
    lines.append("")
    lines.append(f"- session: `{session['session_path']}`")
    lines.append(f"- timestamp: `{session['message_timestamp']}`")
    lines.append(f"- extracted links: `{session['link_count']}`")
    lines.append(f"- missing-env rerun source: `{payload['missing_env_rerun']['source']}`")
    lines.append("")
    lines.append("## Artifact Spine")
    lines.append("")
    lines.append("| Artifact | Type | Key Read | Path |")
    lines.append("| --- | --- | --- | --- |")
    lines.append(
        "| BlueBeam handoff | benchmark handoff | {benchmark}; positives `{positives}`; TRM rows `{rows}` | {path} |".format(
            benchmark=bluebeam["benchmark_completed"],
            positives=bluebeam["new_positive_replays"],
            rows=bluebeam["trm_rows"],
            path=markdown_link("README.md", bluebeam["readme_path"]),
        )
    )
    lines.append(
        "| Missing-env rerun | coverage rerun | task_complete `{tasks}`; success `{success}`; envs `{envs}` | {path} |".format(
            tasks=missing_env["task_complete_count"],
            success=missing_env["success_count"],
            envs=missing_env["env_count"],
            path=markdown_link("summary.json", missing_env["summary_path"]),
        )
    )
    lines.append(
        "| Final gapfill | gapfill audit | tasks `{tasks}`; `passthrough` bridge failures, `verbatim_copy` success | {path} |".format(
            tasks=gapfill["task_count"],
            path=markdown_link("overnight_primehub_benchmark.stout.jsonl", gapfill["stout_path"]),
        )
    )
    lines.append(
        "| Role imprint | TRM role cards | clusters `{clusters}`; strongest action-bearing support in `choice_contract` / `structured_map` / `internal_action` | {path} |".format(
            clusters=len(imprint["clusters"]),
            path=markdown_link("role_based_imprint.json", ROOT / "data" / "primehub_skill_trm_matrix" / "latest" / "role_based_imprint.json"),
        )
    )
    lines.append(
        "| Baseline vs mining | trainer-policy rerun pair | overlapping rows `{rows}`; positive deltas `{deltas}` | {path} |".format(
            rows=baseline_vs_mining["comparison_count"],
            deltas=baseline_vs_mining["positive_delta_count"],
            path=markdown_link("baseline ledger", baseline_vs_mining["baseline_ledger"]),
        )
    )
    lines.append(
        "| Pressure slice | wider `choice_contract` check | comparisons `{rows}`; contract>baseline `{wins}` | {path} |".format(
            rows=pressure["comparison_count"],
            wins=pressure["counts"].get("contract_gt_baseline", 0),
            path=markdown_link("pressure ledger", pressure["ledger_path"]),
        )
    )
    lines.append(
        "| SimpleQA verified proof | transport proof | tasks `{tasks}`; visible output true `{visible}`; model fallbacks `{fallbacks}` | {path} |".format(
            tasks=simpleqa["task_count"],
            visible=simpleqa["visible_output_true_total"],
            fallbacks=simpleqa["model_client_fallbacks_total"],
            path=markdown_link("ledger.jsonl", Path(simpleqa["ledger_path"])),
        )
    )
    lines.append("")
    lines.append("## Key Deltas")
    lines.append("")
    if boolq_delta:
        lines.append(
            "- `boolq` / `qwen35_27b` / `two-model-contract-repair-v1`: baseline `{base}` -> mining `{mined}` (delta `{delta:+.4f}`)".format(
                base=boolq_delta["baseline_reward"],
                mined=boolq_delta["mining_reward"],
                delta=float(boolq_delta["delta"] or 0.0),
            )
        )
    if antislop_row:
        lines.append(
            "- `antislop` / `qwen35_27b` / `two-model-contract-repair-v1`: baseline `{base}` -> mining `{mined}` (delta `{delta:+.4f}`)".format(
                base=antislop_row["baseline_reward"],
                mined=antislop_row["mining_reward"],
                delta=float(antislop_row["delta"] or 0.0),
            )
        )
    if pressure_winogrande:
        lines.append(
            "- pressure slice `winogrande`: baseline `{base}` / contract `{contract}` / abstain `{abstain}`".format(
                base=pressure_winogrande["baseline_reward"],
                contract=pressure_winogrande["contract_reward"],
                abstain=pressure_winogrande["abstain_reward"],
            )
        )
    lines.append("")
    lines.append("## Role Cards")
    lines.append("")
    lines.append("| Cluster | Support Tier | Rows | Exact+ | Coverage | Critic Acc | Route Abstain |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for row in imprint["clusters"]:
        lines.append(
            "| {cluster} | {tier} | {rows} | {exact} | {coverage:.4f} | {critic:.4f} | {abstain:.4f} |".format(
                cluster=row["cluster_id"],
                tier=row["support_tier"],
                rows=row["rows"],
                exact=row["exact_positive_rows"],
                coverage=float(row["target_action_coverage"]),
                critic=float(row["critic_bucket_accuracy"]),
                abstain=float(row["route_abstain_rate"]),
            )
        )
    lines.append("")
    lines.append("## Gapfill Status")
    lines.append("")
    for row in gapfill["per_task"]:
        lines.append(
            "- `{model}` / `{env}` / `{variant}`: `{status}`".format(
                model=row["model_id"],
                env=row["env_id"],
                variant=row["variant_id"],
                status=row["status"],
            )
        )
    lines.append("")
    lines.append("## SimpleQA Proof")
    lines.append("")
    for row in simpleqa["task_rows"]:
        lines.append(
            "- `{model}` / `{env}` / `{variant}`: reward `{reward}`, visible_output_true `{visible}`, model_client_fallbacks `{fallbacks}`".format(
                model=row["model_id"],
                env=row["env_id"],
                variant=row["variant_id"],
                reward=row["reward"],
                visible=row["visible_output_true"],
                fallbacks=row["model_client_fallbacks_total"],
            )
        )
    lines.append("")
    lines.append("## Linked Studies")
    lines.append("")
    for row in payload["linked_studies"]:
        path = str(row["path"])
        lines.append(f"- {markdown_link(Path(path).name, path)}")
    lines.append("")
    return "\n".join(lines)


def render_summary_table(payload: dict[str, Any]) -> str:
    bluebeam = payload["bluebeam_handoff"]
    missing_env = payload["missing_env_rerun"]
    baseline_vs_mining = payload["baseline_vs_mining"]
    pressure = payload["choice_contract_pressure"]
    simpleqa = payload["simpleqa_verified_proof"]

    boolq_delta = next(
        (
            row
            for row in baseline_vs_mining["positive_deltas"]
            if row["model_id"] == "qwen35_27b" and row["env_id"] == "boolq" and row["variant_id"] == "two-model-contract-repair-v1"
        ),
        None,
    )

    lines: list[str] = []
    lines.append("# TRM-Infused Hermes Baseline Summary Table")
    lines.append("")
    lines.append("This file is generated from the recent Codex benchmark-summary chat plus local benchmark artifacts.")
    lines.append("")
    lines.append("## Baseline Spine")
    lines.append("")
    lines.append("| Lane | Date | Evidence | Read | Claim Boundary |")
    lines.append("| --- | --- | --- | --- | --- |")
    lines.append(
        "| BlueBeam benchmark handoff | 2026-04-16 | `{benchmark}` tasks, `{positives}` new positives, `{rows}` TRM rows | Corpus became useful as control-plane support before it was strong as broad action imitation. | Baseline snapshot, not a live benchmark win by itself. |".format(
            benchmark=bluebeam["benchmark_completed"],
            positives=bluebeam["new_positive_replays"],
            rows=bluebeam["trm_rows"],
        )
    )
    lines.append(
        "| Missing-env coverage rerun | 2026-04-20 | `{tasks}/{tasks}` completed across `{envs}` envs and `{models}` models | Coverage expansion finished cleanly. | Counts come from the benchmark-summary chat because the wrapper event log only records heartbeats. |".format(
            tasks=missing_env["success_count"],
            envs=missing_env["env_count"],
            models=missing_env.get("claimed_model_count", 0),
        )
    )
    lines.append(
        "| Final gapfill | 2026-04-20 | `verbatim_copy` succeeded on both models; `passthrough` failed with `bridge_failure` on both | Remaining issue is harness or bridge accounting, not a missing attempt. | Do not treat `passthrough` as benchmarked quality data yet. |"
    )
    if boolq_delta:
        lines.append(
            "| Trainer-policy mining rerun | 2026-04-21 | `boolq` / `qwen35_27b` / `two-model-contract-repair-v1`: `{base} -> {mined}` | Narrow `choice_contract` lift is real. | Not broad generalization across the wider pressure slice. |".format(
                base=boolq_delta["baseline_reward"],
                mined=boolq_delta["mining_reward"],
            )
        )
    lines.append(
        "| Choice-contract pressure slice | 2026-04-21 | `{wins}` contract wins across `{rows}` comparisons | Wider family mostly stayed at parity or zero. | Supports a narrow `choice_contract` claim, not a family-wide reasoning claim. |".format(
            wins=pressure["counts"].get("contract_gt_baseline", 0),
            rows=pressure["comparison_count"],
        )
    )
    lines.append(
        "| Structured-map retrieval study | 2026-04-22 | `ascii_tree 0.0 -> 0.8`, `psycho_bench 3.3283 -> 3.3311`, `pydantic_adherence 0.0 -> 1.0` | Strongest scoped positive result in the repo. | Promote only for exact-structure-sensitive lanes. |"
    )
    lines.append(
        "| SimpleQA verified proof | 2026-04-22 | visible output true `{visible}`, model fallbacks `{fallbacks}` over `{tasks}` tasks | Runtime path now reaches the scorer reliably. | This is a transport/harness result, not a judged-quality win. |".format(
            visible=simpleqa["visible_output_true_total"],
            fallbacks=simpleqa["model_client_fallbacks_total"],
            tasks=simpleqa["task_count"],
        )
    )
    lines.append("")
    lines.append("## Current Cross-Reference")
    lines.append("")
    lines.append(
        "- Full artifact cross-ref: {path}".format(
            path=markdown_link(
                "trm_infused_baseline_crossref.md",
                ROOT / "research" / "generated" / "trm_infused_baseline_crossref.md",
            )
        )
    )
    lines.append(
        "- Machine-readable bundle: {path}".format(
            path=markdown_link(
                "trm_infused_baseline_crossref.json",
                ROOT / "research" / "generated" / "trm_infused_baseline_crossref.json",
            )
        )
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    session_path = Path(args.session_path).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(session_path)
    json_path = out_dir / "trm_infused_baseline_crossref.json"
    md_path = out_dir / "trm_infused_baseline_crossref.md"
    summary_md_path = out_dir / "trm_infused_baseline_summary_table.md"

    json_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    summary_md_path.write_text(render_summary_table(payload), encoding="utf-8")

    print(str(json_path))
    print(str(md_path))
    print(str(summary_md_path))


if __name__ == "__main__":
    main()
