from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


STUDY_ROOT = Path(__file__).resolve().parent
REPO_ROOT = STUDY_ROOT.parents[2]
DATA_ROOT = REPO_ROOT / "data"
BENCHMARK_ROOT = DATA_ROOT / "primehub_eligible_benchmark_v2_47env"
ENV_MANIFEST_PATH = DATA_ROOT / "primehub_env_manifest.json"
OUTPUT_ROOT = STUDY_ROOT / "artifacts" / "nuanced_env_slice"
OUTPUT_JSON = OUTPUT_ROOT / "nuanced_env_slice.json"
OUTPUT_MD = OUTPUT_ROOT / "nuanced_env_slice.md"


CURATED_ENVS: List[Dict[str, str]] = [
    {
        "env_id": "psycho_bench",
        "selection_status": "core_ready",
        "nuance_family": "psychometric_self_model",
        "why_now": "Closest current benchmark to symbolic self-modeling under a strict flat output contract and partial-credit scoring.",
        "use_case": "Primary nuanced benchmark for format-sensitive self-model and consistency work.",
        "notes": "Keep as the anchor env for any MeTTa/TRM self-model slice.",
        "blocker": "",
    },
    {
        "env_id": "if_summarize_judge",
        "selection_status": "core_ready",
        "nuance_family": "constraint_summarization_judged",
        "why_now": "Long-context summarization with held-out structural constraints and an LLM judge gives richer failure modes than short QA or plain IF tasks.",
        "use_case": "Best immediate second env for psycho-like nuance without depending on a missing scorer fix.",
        "notes": "More semantically open than `psycho_bench`, but still structurally legible and judge-backed.",
        "blocker": "",
    },
    {
        "env_id": "allenai_ifeval",
        "selection_status": "supporting_ready",
        "nuance_family": "instruction_compliance",
        "why_now": "Useful supporting contract benchmark for strict instruction execution, though less semantically nuanced than `psycho_bench`.",
        "use_case": "Supporting slice member to check whether gains generalize beyond schema formatting.",
        "notes": "Good as a boundary env, not the centerpiece of the nuanced slice.",
        "blocker": "",
    },
    {
        "env_id": "clbench",
        "selection_status": "blocked_high_value",
        "nuance_family": "rubric_judged_long_context",
        "why_now": "Potentially the highest-value psycho-adjacent benchmark because it scores long-context task completion against explicit rubrics.",
        "use_case": "Promote into the expanded nuanced slice once the transport/scorer issue is fixed.",
        "notes": "The local benchmark evidence shows a 400 failure and zero token usage, so it is not ready for live slice inclusion.",
        "blocker": "Current local replay path failed with `HTTP Error 400: Bad Request` and `run_token_total = 0`.",
    },
    {
        "env_id": "ifbench",
        "selection_status": "research_candidate",
        "nuance_family": "instruction_compliance",
        "why_now": "Research-env IF task with strict/loose scoring that can widen the slice later.",
        "use_case": "Secondary expansion target after the core nuanced slice is stable.",
        "notes": "Not as rich as `psycho_bench` or `if_summarize_judge`; useful mainly for structural generalization checks.",
        "blocker": "No local Primehub replay evidence in this study yet.",
    },
    {
        "env_id": "ifeval",
        "selection_status": "research_candidate",
        "nuance_family": "instruction_compliance",
        "why_now": "Canonical IF benchmark that can act as a contract-compliance check in the research env stack.",
        "use_case": "Expansion env after the core nuanced slice is benchmarked.",
        "notes": "Treat as a supporting control-plane benchmark, not a psycho substitute.",
        "blocker": "No local Primehub replay evidence in this study yet.",
    },
    {
        "env_id": "simpleqa",
        "selection_status": "exclude_simple",
        "nuance_family": "short_fact_qa",
        "why_now": "Very short factual QA surface with little structural or judgment nuance.",
        "use_case": "Keep out of the psycho-like slice.",
        "notes": "Still useful elsewhere as a cheap factual baseline, but not for this study question.",
        "blocker": "",
    },
    {
        "env_id": "simpleqa_verified",
        "selection_status": "exclude_simple",
        "nuance_family": "short_fact_qa",
        "why_now": "Same basic issue as `simpleqa`: answerability and correctness matter, but the task is too short and discrete to test nuanced symbolic infusion.",
        "use_case": "Keep out of the psycho-like slice.",
        "notes": "Use for factual precision checks, not for nuanced-benchmark widening.",
        "blocker": "",
    },
    {
        "env_id": "simpleqa_verified_2",
        "selection_status": "exclude_simple",
        "nuance_family": "short_fact_qa",
        "why_now": "Verified factual QA remains too low-context and too binary for the current goal.",
        "use_case": "Keep out of the psycho-like slice.",
        "notes": "Only revisit if the study shifts toward factual micro-accuracy.",
        "blocker": "",
    },
    {
        "env_id": "truthfulqa",
        "selection_status": "exclude_simple",
        "nuance_family": "multiple_choice_truthfulness",
        "why_now": "Important benchmark, but the current multiple-choice wrapper is too discrete to play the `psycho_bench` role.",
        "use_case": "Leave outside the nuanced slice and track separately.",
        "notes": "Useful as a truthfulness spot-check, not as a nuanced symbolic benchmark.",
        "blocker": "",
    },
]


BUNDLES: Dict[str, List[str]] = {
    "core_ready": ["psycho_bench", "if_summarize_judge"],
    "expanded_ready": ["psycho_bench", "if_summarize_judge", "allenai_ifeval"],
    "blocked_high_value": ["clbench"],
    "research_candidates": ["ifbench", "ifeval"],
}


def load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not decode to an object")
    return payload


def load_env_profiles() -> Dict[str, Dict[str, Any]]:
    payload = load_json(ENV_MANIFEST_PATH)
    profiles = payload.get("profiles") or []
    lookup: Dict[str, Dict[str, Any]] = {}
    for item in profiles:
        if not isinstance(item, dict):
            continue
        env_id = str(item.get("env_id") or "").strip()
        if env_id:
            lookup[env_id] = item
    return lookup


def first_row(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                payload = json.loads(text)
                return payload if isinstance(payload, dict) else {}
    return {}


def compact_text(value: str, limit: int = 180) -> str:
    clean = " ".join(str(value or "").split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3].rstrip() + "..."


def evidence_records(env_id: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for summary_path in sorted(BENCHMARK_ROOT.glob("*/*.summary.json")):
        if f"_{env_id}_" not in summary_path.name:
            continue
        summary = load_json(summary_path)
        export_path = Path(str(summary.get("export_path") or summary_path.with_suffix(".jsonl")))
        row = first_row(export_path)
        reward_totals = summary.get("reward_totals") or {}
        episodes = int(summary.get("episodes") or 0)
        raw_reward = reward_totals.get(env_id)
        avg_reward = None
        if raw_reward is not None:
            avg_reward = float(raw_reward) / float(episodes or 1)
        output_statuses = summary.get("output_statuses") or {}
        output_status = str(row.get("output_status") or next(iter(output_statuses.keys()), "")).strip()
        records.append(
            {
                "model_dir": summary_path.parent.name,
                "summary_path": str(summary_path),
                "export_path": str(export_path),
                "reward_total": raw_reward,
                "avg_reward": avg_reward,
                "episodes": episodes,
                "run_token_total": summary.get("run_token_total"),
                "output_status": output_status,
                "visible_output_emitted": row.get("visible_output_emitted"),
                "action_excerpt": compact_text(str(row.get("action") or "")),
                "observation_excerpt": compact_text(str(row.get("observation") or ""), 220),
            }
        )
    return records


def best_evidence(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {}
    return max(
        records,
        key=lambda record: (
            float(record.get("avg_reward") or 0.0),
            float(record.get("run_token_total") or 0.0),
            str(record.get("model_dir") or ""),
        ),
    )


def latest_evidence(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {}
    return records[-1]


def trajectory_payload(env_ids: List[str]) -> Dict[str, Any]:
    return {"envs": env_ids}


def env_entry(spec: Dict[str, str], profiles: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    env_id = spec["env_id"]
    profile = profiles.get(env_id) or {}
    records = evidence_records(env_id)
    best = best_evidence(records)
    latest = latest_evidence(records)
    return {
        "env_id": env_id,
        "selection_status": spec["selection_status"],
        "nuance_family": spec["nuance_family"],
        "why_now": spec["why_now"],
        "use_case": spec["use_case"],
        "notes": spec["notes"],
        "blocker": spec["blocker"],
        "manifest_profile": {
            "source": profile.get("source"),
            "owner": profile.get("owner"),
            "folder": profile.get("folder"),
            "available": profile.get("available"),
        },
        "evidence": {
            "count": len(records),
            "models": sorted({str(record.get("model_dir") or "") for record in records if str(record.get("model_dir") or "").strip()}),
            "best_avg_reward": best.get("avg_reward"),
            "best_reward_total": best.get("reward_total"),
            "best_model_dir": best.get("model_dir"),
            "best_output_status": best.get("output_status"),
            "best_run_token_total": best.get("run_token_total"),
            "best_action_excerpt": best.get("action_excerpt"),
            "latest_avg_reward": latest.get("avg_reward"),
            "latest_reward_total": latest.get("reward_total"),
            "latest_model_dir": latest.get("model_dir"),
            "latest_output_status": latest.get("output_status"),
            "latest_run_token_total": latest.get("run_token_total"),
            "latest_observation_excerpt": latest.get("observation_excerpt"),
            "records": records,
        },
    }


def render_markdown(payload: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Nuanced Env Slice")
    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append("- `core_ready`: `psycho_bench`, `if_summarize_judge`")
    lines.append("- `expanded_ready`: add `allenai_ifeval` as a supporting contract-compliance member")
    lines.append("- `blocked_high_value`: `clbench` once the 400-path is fixed")
    lines.append("- keep `simpleqa`, `simpleqa_verified`, and `truthfulqa` out of this psycho-like slice")
    lines.append("")
    lines.append("## Bundle Summary")
    lines.append("")
    lines.append("| Bundle | Envs | Purpose |")
    lines.append("| --- | --- | --- |")
    lines.append("| `core_ready` | `psycho_bench`, `if_summarize_judge` | Highest-signal nuanced slice that is already benchmarkable. |")
    lines.append("| `expanded_ready` | `psycho_bench`, `if_summarize_judge`, `allenai_ifeval` | Add a supporting IF boundary env without diluting the core. |")
    lines.append("| `blocked_high_value` | `clbench` | Promote after the current 400-path is repaired. |")
    lines.append("| `research_candidates` | `ifbench`, `ifeval` | Research-env follow-ons after the live nuanced slice is stable. |")
    lines.append("")
    lines.append("## Env Review")
    lines.append("")
    lines.append("| Env | Status | Source | Nuance Family | Best Reward | Tokens | Notes |")
    lines.append("| --- | --- | --- | --- | ---: | ---: | --- |")
    for entry in payload.get("envs") or []:
        manifest_profile = entry.get("manifest_profile") or {}
        evidence = entry.get("evidence") or {}
        lines.append(
            "| {env} | {status} | {source} | {family} | {reward} | {tokens} | {notes} |".format(
                env=entry.get("env_id"),
                status=entry.get("selection_status"),
                source=str(manifest_profile.get("source") or "-"),
                family=entry.get("nuance_family"),
                reward=evidence.get("best_avg_reward") if evidence.get("best_avg_reward") is not None else "-",
                tokens=evidence.get("best_run_token_total") if evidence.get("best_run_token_total") is not None else "-",
                notes=str(entry.get("why_now") or "").replace("|", "\\|"),
            )
        )
    lines.append("")
    lines.append("## Exclusion Rule")
    lines.append("")
    lines.append("- Favor long-context, judged, or partial-credit tasks with visible structural failure modes.")
    lines.append("- Deprioritize short single-answer factual or multiple-choice tasks, even when they are important benchmarks elsewhere.")
    lines.append("")
    lines.append("## Commands")
    lines.append("")
    lines.append("```powershell")
    lines.append(
        f'python "{(STUDY_ROOT / "build_nuanced_env_slice.py")}"'
    )
    lines.append(
        f'python "{(STUDY_ROOT / "run_nuanced_slice_baseline.py")}" --bundle core_ready --dry-run'
    )
    lines.append(
        f'python "{(STUDY_ROOT / "run_nuanced_slice_baseline.py")}" --bundle expanded_ready'
    )
    lines.append("```")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    profiles = load_env_profiles()
    envs = [env_entry(spec, profiles) for spec in CURATED_ENVS]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "study": "2026-04-22-metta-trm-hermes-pipeline",
        "selection_policy": {
            "goal": "Find more nuanced benchmark surfaces like psycho_bench without diluting the slice with short or overly discrete tasks.",
            "include_bias": "Long-context, judged, structurally constrained, or partial-credit tasks.",
            "exclude_bias": "Short factual QA and discrete multiple-choice tasks.",
        },
        "bundles": BUNDLES,
        "envs": envs,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    for bundle_name, env_ids in BUNDLES.items():
        bundle_path = OUTPUT_ROOT / f"trajectory_manifest.{bundle_name}.json"
        bundle_path.write_text(json.dumps(trajectory_payload(env_ids), indent=2) + "\n", encoding="utf-8")
    print(str(OUTPUT_JSON))
    print(str(OUTPUT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
