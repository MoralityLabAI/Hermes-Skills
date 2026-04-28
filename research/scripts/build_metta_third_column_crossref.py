"""Build a 9B baseline/TRM/MeTTa cross-reference table.

The source benchmark pack is the PrimeHub 9B skill reasoning batch.  The third
column is intentionally provenance-aware: some MeTTa rows are live 9B reward
evaluations, while the newer family-router rows are local TRM benchmark metrics.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
SOURCE_PACK = ROOT / "data" / "primehub_skill_reasoning_batch_20260416_2100mdt" / "qwen35_9b"
GENERATED = ROOT / "research" / "generated"
STUDY = ROOT / "research" / "studies" / "2026-04-22-metta-trm-hermes-pipeline"
STRUCTURED_STUDY = ROOT / "research" / "studies" / "2026-04-22-primehub-structured-map-retrieval"

RUNTIME_PACKET_RESULTS = (
    STUDY
    / "artifacts"
    / "live_eval_qwen35_9b_runtime_packet_repair"
    / "runtime_packet_repair.results.json"
)
IF_SUMMARIZE_RESULTS = (
    STUDY
    / "artifacts"
    / "live_eval_qwen35_9b_if_summarize_with_metta_repair"
    / "if_summarize_with_metta.results.json"
)
FAMILY_ROUTER_RESULTS = (
    STUDY
    / "artifacts"
    / "primehub_family_router_comparison"
    / "family_router.summary.json"
)
STRUCTURED_POSTFIX_FINDINGS = (
    STRUCTURED_STUDY / "artifacts" / "live_eval_qwen35_9b_post_fix_3env.findings.md"
)
LOCAL_IF_SUMMARIZE_FINDINGS = (
    STUDY
    / "artifacts"
    / "local_eval_qwen35_0p8b_if_summarize_metta"
    / "local_if_summarize_metta.results.md"
)
LOCAL_IF_SUMMARIZE_3B_FINDINGS = (
    STUDY
    / "artifacts"
    / "local_eval_smollm3_3b_if_summarize_metta"
    / "local_if_summarize_metta.results.md"
)
LOCAL_IF_SUMMARIZE_QWEN25_3B_Q4_TOK16_FINDINGS = (
    STUDY
    / "artifacts"
    / "local_eval_qwen25_3b_q4km_llamacli_probe_ctx2048_tok16"
    / "local_if_summarize_metta.results.md"
)
LOCAL_IF_SUMMARIZE_QWEN25_3B_Q4_TOK32_FINDINGS = (
    STUDY
    / "artifacts"
    / "local_eval_qwen25_3b_q4km_llamacli_3seed_tok64_repairfix_v2"
    / "local_if_summarize_metta.results.md"
)
SYNTHETIC_TOOL_ROUTER_FINDINGS = (
    STUDY
    / "artifacts"
    / "synthetic_tool_router_qwen25_3b_q4km"
    / "synthetic_tool_router.results.md"
)

OUT_JSON = GENERATED / "metta_third_column_crossref.json"
OUT_MD = GENERATED / "metta_third_column_crossref.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_summary_name(path: Path) -> tuple[str, str] | None:
    match = re.match(r"qwen35_9b_(?P<variant>.+?)_(?P<env>.+)_q\d+\.summary\.json$", path.name)
    if not match:
        return None
    return match.group("variant"), match.group("env")


def status_from_summary(summary: dict[str, Any]) -> str:
    failures = summary.get("failure_types") or {}
    if failures:
        return "failure:" + ",".join(sorted(failures))
    output_statuses = summary.get("output_statuses") or {}
    if output_statuses:
        return ",".join(sorted(output_statuses))
    return "ok"


def load_9b_pack() -> dict[str, dict[str, Any]]:
    by_env: dict[str, dict[str, Any]] = defaultdict(dict)
    for path in sorted(SOURCE_PACK.glob("*.summary.json")):
        parsed = parse_summary_name(path)
        if not parsed:
            continue
        variant, env = parsed
        summary = load_json(path)
        reward = round(sum((summary.get("reward_totals") or {}).values()), 6)
        by_env[env][variant] = {
            "variant": variant,
            "reward": reward,
            "status": status_from_summary(summary),
            "path": str(path),
        }
    return dict(by_env)


def best_trm_variant(variants: dict[str, Any]) -> dict[str, Any] | None:
    trm_rows = [row for name, row in variants.items() if name != "single-model-baseline"]
    if not trm_rows:
        return None
    return sorted(trm_rows, key=lambda row: (row["reward"], row["status"] == "ok"), reverse=True)[0]


def add_live_metta(metta: dict[str, dict[str, Any]], path: Path, arm: str, score_key: str) -> None:
    data = load_json(path)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in data.get("results", []):
        grouped[row["env_id"]].append(row)
    for env, rows in grouped.items():
        target = next((row for row in rows if row.get("arm_id") == arm), None)
        if not target:
            continue
        control = next((row for row in rows if row.get("arm_id") == "without_metta"), None)
        score = target.get(score_key)
        control_score = control.get(score_key) if control else None
        metta[env] = {
            "score": round(float(score), 6),
            "metric": score_key,
            "arm": arm,
            "control_score": round(float(control_score), 6) if control_score is not None else None,
            "delta_vs_metta_control": (
                round(float(score) - float(control_score), 6) if control_score is not None else None
            ),
            "evidence_type": "live_9b_reward",
            "path": str(path),
        }


def add_if_summarize(metta: dict[str, dict[str, Any]]) -> None:
    data = load_json(IF_SUMMARIZE_RESULTS)
    target = next(
        row for row in data["results"] if row.get("arm_id") == "with_metta_runtime_repair"
    )
    control = next(row for row in data["results"] if row.get("arm_id") == "without_metta")
    metta[target["env_id"]] = {
        "score": round(float(target["avg_reward"]), 6),
        "metric": "avg_reward",
        "arm": "with_metta_runtime_repair",
        "control_score": round(float(control["avg_reward"]), 6),
        "delta_vs_metta_control": round(float(target["avg_reward"]) - float(control["avg_reward"]), 6),
        "evidence_type": "live_9b_reward",
        "path": str(IF_SUMMARIZE_RESULTS),
    }


def add_family_router(metta: dict[str, dict[str, Any]]) -> None:
    data = load_json(FAMILY_ROUTER_RESULTS)
    variant = data.get("best_target_lift_variant") or "global_all_abstractions"
    row = data["variants"][variant]
    metta["allenai_ifeval"] = {
        "score": round(float(row["ifeval_contract_eval"]["gated_contract_success_rate"]), 6),
        "metric": "gated_contract_success_rate",
        "arm": variant,
        "control_score": round(
            float(data["variants"]["control"]["ifeval_contract_eval"]["gated_contract_success_rate"]), 6
        ),
        "delta_vs_metta_control": round(
            float(row["ifeval_contract_eval"]["gated_contract_success_rate"])
            - float(data["variants"]["control"]["ifeval_contract_eval"]["gated_contract_success_rate"]),
            6,
        ),
        "evidence_type": "local_trm_router_benchmark",
        "path": str(FAMILY_ROUTER_RESULTS),
    }
    metta["aime2026"] = {
        "score": round(float(row["aime_numeric_eval"]["gated_boxed_exact_rate"]), 6),
        "metric": "gated_boxed_exact_rate",
        "arm": variant,
        "control_score": round(
            float(data["variants"]["control"]["aime_numeric_eval"]["gated_boxed_exact_rate"]), 6
        ),
        "delta_vs_metta_control": round(
            float(row["aime_numeric_eval"]["gated_boxed_exact_rate"])
            - float(data["variants"]["control"]["aime_numeric_eval"]["gated_boxed_exact_rate"]),
            6,
        ),
        "evidence_type": "local_trm_router_benchmark",
        "path": str(FAMILY_ROUTER_RESULTS),
    }


def load_metta_rows() -> dict[str, dict[str, Any]]:
    metta: dict[str, dict[str, Any]] = {}
    add_live_metta(metta, RUNTIME_PACKET_RESULTS, "with_metta_runtime_repair", "reward")
    add_if_summarize(metta)
    add_family_router(metta)
    return metta


def build_rows() -> list[dict[str, Any]]:
    pack = load_9b_pack()
    metta = load_metta_rows()
    all_envs = sorted(set(pack) | set(metta))
    rows: list[dict[str, Any]] = []
    for env in all_envs:
        variants = pack.get(env, {})
        baseline = variants.get("single-model-baseline")
        best_trm = best_trm_variant(variants)
        metta_row = metta.get(env)
        rows.append(
            {
                "env": env,
                "without_trm_reward": baseline["reward"] if baseline else None,
                "without_trm_status": baseline["status"] if baseline else "not_in_pack",
                "without_trm_path": baseline["path"] if baseline else None,
                "with_trm_best_reward": best_trm["reward"] if best_trm else None,
                "with_trm_best_variant": best_trm["variant"] if best_trm else None,
                "with_trm_status": best_trm["status"] if best_trm else "not_in_pack",
                "with_trm_path": best_trm["path"] if best_trm else None,
                "with_metta_score": metta_row["score"] if metta_row else None,
                "with_metta_metric": metta_row["metric"] if metta_row else None,
                "with_metta_arm": metta_row["arm"] if metta_row else None,
                "with_metta_evidence_type": metta_row["evidence_type"] if metta_row else None,
                "with_metta_control_score": metta_row["control_score"] if metta_row else None,
                "with_metta_delta_vs_control": metta_row["delta_vs_metta_control"] if metta_row else None,
                "with_metta_path": metta_row["path"] if metta_row else None,
                "variants_seen": sorted(variants),
            }
        )
    return rows


def fmt_score(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def markdown_link(path: str | None, label: str) -> str:
    if not path:
        return label
    return f"[{label}](<{path}>)"


def write_outputs(rows: list[dict[str, Any]]) -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_pack": str(SOURCE_PACK.parent),
        "model_id": "qwen35_9b",
        "notes": [
            "without_trm is single-model-baseline from the local 9B skill reasoning pack.",
            "with_trm_best is the highest reward non-baseline variant in the same pack.",
            "with_metta_score is provenance-aware and can be live 9B reward or local TRM-router benchmark score.",
            "Do not average reward metrics with local router metrics without a normalization layer.",
        ],
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    highlights = [
        row
        for row in rows
        if row["with_metta_score"] is not None
        or row["env"] in {"psycho_bench", "ascii_tree", "pydantic_adherence"}
    ]
    lines = [
        "# MeTTa Third-Column Cross-Ref",
        "",
        "This joins the local 9B skill benchmark pack against the current MeTTa/TRM evidence.",
        "",
        f"- Source pack: `{SOURCE_PACK.parent}`",
        f"- Machine-readable output: {markdown_link(str(OUT_JSON), 'metta_third_column_crossref.json')}",
        f"- Structured-map promoted snapshot: {markdown_link(str(STRUCTURED_POSTFIX_FINDINGS), 'post-fix 3-env findings')}",
        "",
        "## Three-Column View",
        "",
        "| Env | 9B without TRM | 9B with TRM best | MeTTa/TRM third column | Evidence type | Read |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in highlights:
        without = fmt_score(row["without_trm_reward"])
        if row["without_trm_status"] != "ok":
            without += f" ({row['without_trm_status']})"
        with_trm = fmt_score(row["with_trm_best_reward"])
        if row["with_trm_best_variant"]:
            with_trm += f" `{row['with_trm_best_variant']}`"
        if row["with_trm_status"] not in {"ok", "not_in_pack"}:
            with_trm += f" ({row['with_trm_status']})"
        metta_score = fmt_score(row["with_metta_score"])
        if row["with_metta_metric"]:
            metta_score += f" `{row['with_metta_metric']}`"
        evidence = row["with_metta_evidence_type"] or "-"
        read = "-"
        if row["with_metta_delta_vs_control"] is not None:
            read = f"MeTTa delta vs its matched control: {row['with_metta_delta_vs_control']:+.4f}"
        elif row["with_metta_score"] is None:
            read = "No MeTTa row yet"
        lines.append(
            f"| `{row['env']}` | {without} | {with_trm} | {metta_score} | {evidence} | {read} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "- The `9B without TRM` and `9B with TRM best` columns come from the same local skill benchmark pack and are directly comparable within an environment.",
            "- The MeTTa column is a cross-reference column, not a single pooled metric. `live_9b_reward` rows are closest to direct comparison; `local_trm_router_benchmark` rows are evidence for training/control-plane effectiveness.",
            "- The strongest publishable claim is currently scoped: MeTTa improves structured constraint framing and router-specialized training signals, with the cleanest live reward gains on `psycho_bench` and `if_summarize_judge` and strongest exact-structure evidence on `ascii_tree`/`pydantic_adherence`.",
            "",
            "## Local Fallback Run",
            "",
            f"After Snacksack access was lost, local-only survivability runs were executed for `if_summarize_judge`: {markdown_link(str(LOCAL_IF_SUMMARIZE_FINDINGS), '0.8B HF local results')}, {markdown_link(str(LOCAL_IF_SUMMARIZE_3B_FINDINGS), '3B HF local results')}, {markdown_link(str(LOCAL_IF_SUMMARIZE_QWEN25_3B_Q4_TOK16_FINDINGS), '3B Q4 GGUF tok16 results')}, and {markdown_link(str(LOCAL_IF_SUMMARIZE_QWEN25_3B_Q4_TOK32_FINDINGS), '3B Q4 GGUF tok64 v2 results')}.",
            "",
            "| Local model | Env | Setting | without_metta | with_metta_runtime | with_metta_runtime_repair | Read |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
            "| `qwen35_0p8b_local` | `if_summarize_judge` | HF, 3 seeds | 0.3333 | 0.3333 | 1.0000 | Repair layer reproduces the same constraint-framing pattern locally, but this is not a 9B-equivalent run. |",
            "| `smollm3_3b_local` | `if_summarize_judge` | HF CPU, 3 seeds | 0.0000 | 0.0000 | 1.0000 | Larger local model also fails raw structure but reaches exact compliance through MeTTa-framed repair across the same three seeds. |",
            "| `qwen25_3b_q4km_llamacli` | `if_summarize_judge` | GGUF CUDA, seed 7, max_tokens 16 | 0.0000 | 0.0000 | 1.0000 | VRAM-first GGUF path works operationally; repair succeeds when the candidate is detected as wrong sentence count. |",
            "| `qwen25_3b_q4km_llamacli` | `if_summarize_judge` | GGUF CUDA, 3 seeds, max_tokens 64, post-repair-fix-v2 | 0.0000 | 0.0000 | 1.0000 | VRAM-first local 3B slice: metric-aware MeTTa repair restores exact compliance on all three longer-output cases. |",
            "",
            "Resource caveat: the run used the capped launcher configured for `2048 MB RAM`, `50% CPU`, `50 MB/s IO`, but the monitor reported `3114.4375 MB` peak working set. Treat the result as local evidence, not a resource-clean benchmark receipt, until rerun with an approved higher cap or a smaller working backend.",
            "The 3B run required an `8192 MB RAM` cap because the only complete local 3B asset is a CPU-side `bfloat16` HF model; the capped receipt reported `7665.3984 MB` peak working set.",
            "The Qwen2.5-3B Q4_K_M GGUF runs used llama.cpp CUDA full offload. llama.cpp reported about `1834 MiB` model buffer on CUDA and `166-170 MiB` host mapped model memory in single-seed probes; the promoted three-seed tok64 v2 Windows job wrapper reported `2053.1406 MB` peak working set.",
            "",
            "## Synthetic Tool Router",
            "",
            f"A controlled tool-calling surrogate was added for the small-model claim: {markdown_link(str(SYNTHETIC_TOOL_ROUTER_FINDINGS), 'synthetic tool-router results')}.",
            "",
            "| Local model | Task | without_metta | with_metta_runtime | with_metta_runtime_repair | Read |",
            "| --- | --- | ---: | ---: | ---: | --- |",
            "| `qwen25_3b_q4km_llamacli` | `synthetic_tool_router` | 0.0000 | 1.0000 | 1.0000 | MeTTa contract memory turns wrong raw tool names/slots into exact JSON tool calls; repair is unchanged because runtime already satisfies all three schemas. |",
            "",
            "Resource caveat: the outer job receipt records the parent process only for this subprocess-heavy runner, but per-child telemetry captured by the runner shows `2139-2343 MB` peak child RSS and llama.cpp reports about `1834 MiB` CUDA model buffer plus `166-170 MiB` host mapped model memory.",
            "",
            "## Full Pack Coverage",
            "",
            "| Env | Baseline status | TRM variants seen | MeTTa evidence |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        variants = ", ".join(f"`{variant}`" for variant in row["variants_seen"]) or "-"
        metta = row["with_metta_evidence_type"] or "-"
        lines.append(f"| `{row['env']}` | {row['without_trm_status']} | {variants} | {metta} |")
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_outputs(rows)
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"Rows: {len(rows)}")


if __name__ == "__main__":
    main()
