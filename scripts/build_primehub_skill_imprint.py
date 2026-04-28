from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def classify_action_shape(row: Dict[str, Any]) -> str:
    if not row.get("visible_output_emitted"):
        return "internal_only"
    text = str(row.get("model_action") or "").strip()
    if not text:
        return "empty"
    if "\n" in text and ":" in text:
        return "multiline_structured"
    if len(text) <= 24 and "\n" not in text:
        return "short_exact"
    if len(text) <= 120 and "\n" not in text:
        return "short_single_line"
    return "longform"


def model_label(row: Dict[str, Any]) -> str:
    meta = row.get("meta") or {}
    if isinstance(meta, dict):
        name = str(meta.get("model_name") or "").strip()
        if name:
            return name
    return "unknown"


def build_payload(
    rows: List[Dict[str, Any]],
    *,
    critic_summary: Dict[str, Any],
    retriever_summary: Dict[str, Any],
    router_summary: Dict[str, Any],
    max_envs: int,
    max_failures: int,
) -> Dict[str, Any]:
    bucket_counts = Counter(str(row.get("bucket") or "unknown") for row in rows)
    target_action_rows = sum(1 for row in rows if row.get("target_action"))
    target_cov = round(target_action_rows / len(rows), 4) if rows else 0.0

    positive_rows = [row for row in rows if str(row.get("bucket") or "") == "exact_positive"]
    weak_rows = [row for row in rows if str(row.get("bucket") or "") == "weak_positive"]
    negative_rows = [row for row in rows if str(row.get("bucket") or "") == "negative"]

    by_env: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "rows": 0,
            "exact_positive": 0,
            "weak_positive": 0,
            "negative": 0,
            "positive_rewards": [],
            "models": Counter(),
        }
    )
    by_model: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "rows": 0,
            "exact_positive": 0,
            "weak_positive": 0,
            "negative": 0,
            "positive_rewards": [],
        }
    )

    for row in rows:
        env_name = str(row.get("source_env_name") or "unknown")
        bucket = str(row.get("bucket") or "unknown")
        model = model_label(row)
        reward = safe_float(row.get("reward"))

        env_stats = by_env[env_name]
        env_stats["rows"] += 1
        env_stats["models"][model] += 1
        if bucket in env_stats:
            env_stats[bucket] += 1
        if bucket == "exact_positive":
            env_stats["positive_rewards"].append(reward)

        model_stats = by_model[model]
        model_stats["rows"] += 1
        if bucket in model_stats:
            model_stats[bucket] += 1
        if bucket == "exact_positive":
            model_stats["positive_rewards"].append(reward)

    top_positive_envs = []
    for env_name, stats in by_env.items():
        if stats["exact_positive"] <= 0:
            continue
        top_positive_envs.append(
            {
                "env_name": env_name,
                "exact_positive": stats["exact_positive"],
                "weak_positive": stats["weak_positive"],
                "negative": stats["negative"],
                "avg_positive_reward": round(mean(stats["positive_rewards"]), 4) if stats["positive_rewards"] else 0.0,
                "models": dict(stats["models"]),
            }
        )
    top_positive_envs.sort(
        key=lambda item: (
            -int(item["exact_positive"]),
            -float(item["avg_positive_reward"]),
            str(item["env_name"]),
        )
    )

    negative_status_counts = Counter(str(row.get("output_status") or "unknown") for row in negative_rows)
    positive_shape_counts = Counter(classify_action_shape(row) for row in positive_rows)
    positive_visible_rate = round(
        sum(1 for row in positive_rows if row.get("visible_output_emitted")) / len(positive_rows),
        4,
    ) if positive_rows else 0.0

    critic_acc = safe_float(critic_summary.get("bucket_accuracy"))
    retrieval_exact = safe_float(retriever_summary.get("exact_match_rate"))
    route_abstain = safe_float(((router_summary.get("critic_gated") or {}).get("route_abstain_rate")))

    top_env_names = [item["env_name"] for item in top_positive_envs[:max_envs]]
    prompt_lines: List[str] = []
    trainer_lines: List[str] = []

    if critic_acc >= 0.7 and retrieval_exact <= 0.1:
        prompt_lines.append(
            f"Use TRM mainly as a critic and verification layer first; held-out critic accuracy is {critic_acc:.2f} while retrieval exact match is only {retrieval_exact:.2f}."
        )
        trainer_lines.append(
            "Promote critic and abstention gains first; do not treat the current corpus as strong action-imitation supervision."
        )

    if target_cov < 0.25 or route_abstain >= 0.7:
        prompt_lines.append(
            f"When support is weak, stay on the plain skill path instead of forcing TRM escalation; target-action coverage is {target_cov:.2f} and critic-gated abstention is {route_abstain:.2f}."
        )
        trainer_lines.append(
            "Grow the exact-positive bank before relaxing the router gate or widening TRM default routing."
        )

    timeout_like = sum(
        count
        for status, count in negative_status_counts.items()
        if "timed out" in status.lower() or "bad request" in status.lower()
    )
    if negative_rows and timeout_like / len(negative_rows) >= 0.35:
        prompt_lines.append(
            "Keep outputs contract-tight and low-overhead; many Prime failures were timeouts or malformed requests rather than near-miss reasoning errors."
        )
        trainer_lines.append(
            "Prefer short exact outputs and explicit format compliance in candidate prompts before adding more reasoning text."
        )

    short_like = positive_shape_counts.get("short_exact", 0) + positive_shape_counts.get("short_single_line", 0)
    if positive_rows and short_like / len(positive_rows) >= 0.35:
        prompt_lines.append(
            "When the task specifies a tight answer format, prefer the minimal exact answer over explanatory prose."
        )

    if top_env_names:
        prompt_lines.append(
            "Current positive support is concentrated in "
            + ", ".join(top_env_names[:max_envs])
            + "; use this imprint as a control-plane prior, not a general reasoning substitute."
        )
        trainer_lines.append(
            "Keep collection focused on envs that can add completed exact-positive rows, especially outside the current narrow positive cluster."
        )

    if not prompt_lines:
        prompt_lines.append("Use TRM conservatively until the Prime corpus contains more completed exact-positive rows.")
    if not trainer_lines:
        trainer_lines.append("Continue collection before changing routing defaults.")

    model_summary = []
    for name, stats in sorted(by_model.items(), key=lambda item: (-item[1]["exact_positive"], -item[1]["rows"], item[0])):
        model_summary.append(
            {
                "model_name": name,
                "rows": stats["rows"],
                "exact_positive": stats["exact_positive"],
                "weak_positive": stats["weak_positive"],
                "negative": stats["negative"],
                "avg_positive_reward": round(mean(stats["positive_rewards"]), 4) if stats["positive_rewards"] else 0.0,
            }
        )

    return {
        "rows": len(rows),
        "bucket_counts": dict(bucket_counts),
        "target_action_rows": target_action_rows,
        "target_action_coverage": target_cov,
        "critic_bucket_accuracy": critic_acc,
        "retriever_exact_match_rate": retrieval_exact,
        "critic_gated_route_abstain_rate": route_abstain,
        "positive_visible_output_rate": positive_visible_rate,
        "positive_shape_counts": dict(positive_shape_counts),
        "top_positive_envs": top_positive_envs[:max_envs],
        "negative_output_status_counts": dict(negative_status_counts.most_common(max_failures)),
        "model_summary": model_summary,
        "skill_prompt_lines": prompt_lines,
        "trainer_lines": trainer_lines,
    }


def render_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# Prime/TRM Skill Imprint",
        "",
        "## Corpus",
        f"- rows: {payload.get('rows', 0)}",
        f"- bucket_counts: {json.dumps(payload.get('bucket_counts', {}), ensure_ascii=True)}",
        f"- target_action_coverage: {payload.get('target_action_coverage', 0.0):.4f}",
        "",
        "## Bench",
        f"- critic_bucket_accuracy: {payload.get('critic_bucket_accuracy', 0.0):.4f}",
        f"- retriever_exact_match_rate: {payload.get('retriever_exact_match_rate', 0.0):.4f}",
        f"- critic_gated_route_abstain_rate: {payload.get('critic_gated_route_abstain_rate', 0.0):.4f}",
        "",
        "## Skill Prompt Lines",
    ]
    for line in payload.get("skill_prompt_lines", []):
        lines.append(f"- {line}")
    lines.extend(["", "## Trainer Lines"])
    for line in payload.get("trainer_lines", []):
        lines.append(f"- {line}")
    lines.extend(["", "## Top Positive Envs"])
    for item in payload.get("top_positive_envs", []):
        lines.append(
            "- "
            + f"{item['env_name']}: exact_positive={item['exact_positive']}, "
            + f"avg_positive_reward={item['avg_positive_reward']}, models={json.dumps(item['models'], ensure_ascii=True)}"
        )
    lines.extend(["", "## Negative Output Statuses"])
    for status, count in (payload.get("negative_output_status_counts") or {}).items():
        lines.append(f"- {status}: {count}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a compact Prime/TRM skill imprint from a merged corpus.")
    parser.add_argument("--merged-jsonl", required=True)
    parser.add_argument("--critic-summary", default="")
    parser.add_argument("--retriever-summary", default="")
    parser.add_argument("--router-summary", default="")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--max-envs", type=int, default=8)
    parser.add_argument("--max-failures", type=int, default=8)
    args = parser.parse_args()

    merged_jsonl = Path(args.merged_jsonl).resolve()
    rows = load_jsonl(merged_jsonl)
    critic_summary = load_json(Path(args.critic_summary).resolve()) if args.critic_summary else {}
    retriever_summary = load_json(Path(args.retriever_summary).resolve()) if args.retriever_summary else {}
    router_summary = load_json(Path(args.router_summary).resolve()) if args.router_summary else {}

    payload = build_payload(
        rows,
        critic_summary=critic_summary,
        retriever_summary=retriever_summary,
        router_summary=router_summary,
        max_envs=max(1, args.max_envs),
        max_failures=max(1, args.max_failures),
    )

    output_json = Path(args.output_json).resolve()
    output_md = Path(args.output_md).resolve()
    write_json(output_json, payload)
    write_text(output_md, render_markdown(payload))
    print(json.dumps({"output_json": str(output_json), "output_md": str(output_md), "rows": payload["rows"]}, indent=2))


if __name__ == "__main__":
    main()
