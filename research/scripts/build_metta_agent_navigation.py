"""Build an agent navigation guide for the MeTTa/TRM project menu.

The project menu answers "what could we do next?"  This guide answers how an
agent should choose among those projects from a paper-writing or experiment
campaign objective, which evidence class it should produce, and what artifacts
it must leave behind.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "research" / "generated"
PROJECT_MENU_JSON = GENERATED / "metta_project_menu.json"

OUT_JSON = GENERATED / "metta_agent_navigation.json"
OUT_MD = GENERATED / "metta_agent_navigation.md"


ROUTES: list[dict[str, Any]] = [
    {
        "route_id": "paper_main_claim_extension",
        "user_intent": "Extend the current MeTTa/TRM paper with the cleanest next positive evidence.",
        "choose_projects": ["mixed_contract_compactification", "real_tool_contract_router"],
        "evidence_class": "live_or_replay_with_exact_validators",
        "why": "These projects keep the claim near the paper's strongest result: explicit symbolic gates expose verifier-visible state and improve small-model control-plane reliability.",
        "first_action": "Create held-out rows and exact validators before adding model runs.",
        "paper_section": "Main results extension or short addendum.",
        "overclaim_risk": "Do not describe format or tool-contract wins as broad reasoning gains.",
    },
    {
        "route_id": "hard_env_boundary",
        "user_intent": "Show whether the method transfers to hard logic and where it fails.",
        "choose_projects": ["logic_signature_camp_gate", "live_symbolic_closure_threshold"],
        "evidence_class": "leakage_audited_hard_env_probe",
        "why": "Logic is the plausible hard positive target, but only if prompt-derived constraints, not answer signatures, drive projection.",
        "first_action": "Write the leakage audit and proposal-tier labels before scoring improvements.",
        "paper_section": "Boundary and generalization appendix.",
        "overclaim_risk": "Post-hoc projection can look strong while leaking target information; require a prompt-derived signature audit.",
    },
    {
        "route_id": "negative_control",
        "user_intent": "Make the paper more credible by showing where MeTTa/TRM does not replace scale.",
        "choose_projects": ["math_teacher_candidate_auditor"],
        "evidence_class": "negative_control_or_teacher_candidate_audit",
        "why": "Hard math separates protocol/candidate-auditing gains from missing base-model solving competence.",
        "first_action": "Build or import a teacher-candidate bank with numeric validators and error archetypes.",
        "paper_section": "Limitations or scale-boundary appendix.",
        "overclaim_risk": "Do not claim small-model math solving unless the model produced the correct candidate unaided.",
    },
    {
        "route_id": "nuanced_metric_extension",
        "user_intent": "Develop the psychometric/nuanced benchmark line rather than chase tiny scalar reward lifts.",
        "choose_projects": ["psycho_item_vector_stability"],
        "evidence_class": "multi_signal_interpretability_probe",
        "why": "PsychoBench needs item-vector, subscale, and stability analysis; scalar reward alone hides the interesting effect.",
        "first_action": "Run repeated probes and emit item vectors, subscale deltas, and stability bands.",
        "paper_section": "Nuanced benchmark appendix.",
        "overclaim_risk": "Variance reduction can be over-regularization if the gate collapses personality signal.",
    },
    {
        "route_id": "tooling_infrastructure",
        "user_intent": "Build reusable infrastructure for future skills and agents.",
        "choose_projects": ["mcp_lookup_efficiency", "real_tool_contract_router"],
        "evidence_class": "infrastructure_efficiency_benchmark",
        "why": "MCP/tool lookup is a broad substrate where TRMs can optimize stable handles, call count, and token load.",
        "first_action": "Define first-useful-hit, token-load, and call-count metrics before collecting traces.",
        "paper_section": "Future work or systems appendix.",
        "overclaim_risk": "If the resource surface is tiny, direct scanning is the right baseline and TRM overhead is not justified.",
    },
    {
        "route_id": "scale_campaign",
        "user_intent": "Prepare for Snacksack or equivalent 9B/27B matched runs.",
        "choose_projects": ["mixed_contract_compactification", "logic_signature_camp_gate", "math_teacher_candidate_auditor"],
        "evidence_class": "matched_scale_matrix",
        "why": "The paper becomes stronger when the same row schema is run at 3B, 9B, and 27B with the same validators.",
        "first_action": "Freeze row IDs, prompt construction, output schema, and validator code before changing models.",
        "paper_section": "Full experiment campaign.",
        "overclaim_risk": "Changing row selection or validators between scales makes the trend uninterpretable.",
    },
]


AGENT_LOOP: list[dict[str, str]] = [
    {
        "step": "1",
        "name": "Classify the requested claim",
        "output": "Select one route_id and one primary project_id.",
        "check": "The selected project must have an evidence class that matches the requested paper claim.",
    },
    {
        "step": "2",
        "name": "Open the source spine",
        "output": "Read the project menu row, scale-transfer row, fork plan, and composition plan for the selected project.",
        "check": "Record source paths in the new study README so later agents can reproduce the reasoning.",
    },
    {
        "step": "3",
        "name": "Create a study folder",
        "output": "Use `research/studies/YYYY-MM-DD-<project_id>/` or a project subfolder under the active MeTTa study if it is clearly an extension.",
        "check": "Do not dump large model artifacts into Git unless they are small, interpretable result files.",
    },
    {
        "step": "4",
        "name": "Freeze rows and validators first",
        "output": "Emit row JSONL, validator code, and a row manifest before running models.",
        "check": "Rows must include split, env_family, expected observable state, and failure labels.",
    },
    {
        "step": "5",
        "name": "Run the smallest meaningful arms",
        "output": "Start with baseline, pure_trm, metta_runtime, and metta_runtime_repair unless the project defines a different matrix.",
        "check": "For local models, keep memory caps explicit and preserve prompt/output schemas for later 9B/27B runs.",
    },
    {
        "step": "6",
        "name": "Separate evidence classes",
        "output": "Mark each result as live model, deterministic replay, post-hoc projection, no-model verifier sweep, or control-plane simulation.",
        "check": "Never mix post-hoc projection with live benchmark columns.",
    },
    {
        "step": "7",
        "name": "Write the paper hook",
        "output": "Add a short findings.md with claim, limitation, metric table, and next run command.",
        "check": "Every positive claim must name the exact verifier-visible state that MeTTa/TRM controlled.",
    },
]


STUDY_ARTIFACTS: list[dict[str, str]] = [
    {
        "path": "README.md",
        "purpose": "One-page study index: route, project, source inputs, active claim, and artifact links.",
    },
    {
        "path": "study_plan.md",
        "purpose": "Hypothesis, arms, validators, splits, stop rules, and paper claim boundary.",
    },
    {
        "path": "rows/*.jsonl",
        "purpose": "Frozen benchmark rows or proposal traces with stable IDs and split labels.",
    },
    {
        "path": "validators/*.py",
        "purpose": "Exact validators or metric extractors used before model results are interpreted.",
    },
    {
        "path": "configs/*.json",
        "purpose": "Prompt, model, memory, and arm configuration with enough detail for 9B/27B reruns.",
    },
    {
        "path": "results/*.json",
        "purpose": "Machine-readable result table with per-row arm scores and evidence_class.",
    },
    {
        "path": "results/*.md",
        "purpose": "Human-readable finding with metric table, failure breakdown, and paper-ready claim.",
    },
    {
        "path": "claim_audit.md",
        "purpose": "Explicit separation of live, deterministic, post-hoc, and control-plane evidence.",
    },
]


def load_project_menu() -> dict[str, Any]:
    with PROJECT_MENU_JSON.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def projects_by_id(menu: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {project["id"]: project for project in menu["projects"]}


def enrich_routes(menu: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = projects_by_id(menu)
    enriched: list[dict[str, Any]] = []
    for route in ROUTES:
        route_copy = dict(route)
        route_copy["projects"] = [
            {
                "id": project_id,
                "priority": by_id[project_id]["priority"],
                "title": by_id[project_id]["title"],
                "first_artifact": by_id[project_id]["first_artifact"],
                "success_metric": by_id[project_id]["success_metric"],
                "paper_claim": by_id[project_id]["paper_claim"],
            }
            for project_id in route["choose_projects"]
            if project_id in by_id
        ]
        enriched.append(route_copy)
    return enriched


def build_navigation() -> dict[str, Any]:
    menu = load_project_menu()
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Agent-facing router for navigating MeTTa/TRM paper extensions and follow-on experiments.",
        "source_inputs": {
            "project_menu": str(PROJECT_MENU_JSON.relative_to(ROOT)),
            "paper_data_campaign_plan": "research\\generated\\paper_latex\\metta_trm_repair_addendum\\data_campaign_plan.md",
            "benchmark_crossref": "research\\generated\\trm_infused_baseline_crossref.md",
        },
        "routes": enrich_routes(menu),
        "agent_loop": AGENT_LOOP,
        "study_artifacts": STUDY_ARTIFACTS,
    }


def md_link(path: str) -> str:
    return f"[{path}](<{ROOT / path}>)"


def render_md(nav: dict[str, Any]) -> str:
    lines: list[str] = [
        "# MeTTa Agent Navigation Guide",
        "",
        f"Generated: `{nav['generated_at_utc']}`",
        "",
        "This guide tells a future agent how to move from the current paper artifacts into the MeTTa project menu without losing claim discipline.",
        "",
        "## Source Spine",
        "",
    ]
    for label, path in nav["source_inputs"].items():
        lines.append(f"- `{label}`: {md_link(path)}")

    lines.extend(
        [
            "",
            "## Claim Router",
            "",
            "| Route | User intent | Primary projects | Evidence class | First action | Overclaim risk |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for route in nav["routes"]:
        projects = ", ".join(f"`{project['id']}`" for project in route["projects"])
        lines.append(
            f"| `{route['route_id']}` | {route['user_intent']} | {projects} | `{route['evidence_class']}` | {route['first_action']} | {route['overclaim_risk']} |"
        )

    lines.extend(
        [
            "",
            "## Recommended Agent Path",
            "",
            "If the user says to continue the paper-adjacent work, choose `paper_main_claim_extension`: start `mixed_contract_compactification` plus `real_tool_contract_router` because both preserve exact validators and small-model compactification claims.",
            "",
            "If the user asks for harder envs or generalization, choose `hard_env_boundary`: start `logic_signature_camp_gate`, but freeze the leakage audit before any score table.",
            "",
            "If the user asks what makes the claim credible, choose `negative_control`: use `math_teacher_candidate_auditor` to show that MeTTa/TRM audits candidates and protocols but does not replace missing math competence.",
            "",
            "If the user asks for new research texture, choose `nuanced_metric_extension`: use `psycho_item_vector_stability` and report item-vector geometry rather than scalar reward.",
            "",
            "## Agent Loop",
            "",
            "| Step | Name | Output | Check |",
            "| ---: | --- | --- | --- |",
        ]
    )
    for step in nav["agent_loop"]:
        lines.append(f"| {step['step']} | {step['name']} | {step['output']} | {step['check']} |")

    lines.extend(
        [
            "",
            "## Required Study Artifacts",
            "",
            "| Path | Purpose |",
            "| --- | --- |",
        ]
    )
    for artifact in nav["study_artifacts"]:
        lines.append(f"| `{artifact['path']}` | {artifact['purpose']} |")

    lines.extend(
        [
            "",
            "## Route Details",
            "",
        ]
    )
    for route in nav["routes"]:
        lines.extend(
            [
                f"### `{route['route_id']}`",
                "",
                f"- User intent: {route['user_intent']}",
                f"- Evidence class: `{route['evidence_class']}`",
                f"- Why this route: {route['why']}",
                f"- First action: {route['first_action']}",
                f"- Paper section: {route['paper_section']}",
                f"- Overclaim risk: {route['overclaim_risk']}",
                "",
                "Projects:",
            ]
        )
        for project in route["projects"]:
            lines.extend(
                [
                    f"- `{project['id']}`: {project['title']}",
                    f"- First artifact for `{project['id']}`: {project['first_artifact']}",
                    f"- Success metric for `{project['id']}`: {project['success_metric']}",
                    f"- Paper claim for `{project['id']}`: {project['paper_claim']}",
                ]
            )
        lines.append("")

    lines.extend(
        [
            "## Execution Rules",
            "",
            "- Prefer exact validators and frozen rows before model calls.",
            "- Keep local 3B, 9B, and 27B comparisons on the same row IDs and output schema.",
            "- Mark every result with one evidence class: `live_model`, `deterministic_replay`, `post_hoc_projection`, `no_model_verifier_sweep`, or `control_plane_simulation`.",
            "- Do not treat deterministic repair as learned TRM lift unless a trained TRM consumed the same features and improved a held split.",
            "- Do not route hard math as a compactification success; route it as candidate auditing unless the model generated the correct solution candidate.",
            "- For safety-like work, separate route/format correctness from advice quality.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    nav = build_navigation()
    GENERATED.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(nav, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(nav), encoding="utf-8")
    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
