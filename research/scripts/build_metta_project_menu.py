"""Build a concise project menu from the MeTTa/TRM planning artifacts.

This is a synthesis artifact, not a benchmark run. It turns the scale-transfer
map, meta-skill fork plan, and composition plan into an actionable menu of
research projects with first artifacts, success metrics, and claim boundaries.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "research" / "generated"

SCALE_JSON = GENERATED / "metta_trm_scale_transfer_map.json"
FORK_JSON = GENERATED / "metta_eval_meta_skill_fork_plan.json"
COMPOSITION_JSON = GENERATED / "metta_composition_plan.json"

OUT_JSON = GENERATED / "metta_project_menu.json"
OUT_MD = GENERATED / "metta_project_menu.md"


PROJECTS: list[dict[str, Any]] = [
    {
        "id": "real_tool_contract_router",
        "title": "Real Tool-Contract Router",
        "priority": 1,
        "thesis": "Move the synthetic tool-router win onto real Hermes-style tool calls where MeTTa owns schema memory, argument validation, and commit gating.",
        "why_now": "The synthetic 3B result is already clean, but the claim is too narrow until it survives real tool diversity.",
        "env_families": ["synthetic_tool_router", "pydantic_adherence"],
        "forks": ["metta-structured-contract-repair-lane"],
        "circuits": ["tool_schema_composition_circuit"],
        "first_artifact": "A 30-60 row real-tool trace suite covering repo search, file lookup, shell-safe commands, calendar-like scheduling, weather-like queries, and JSON argument traps.",
        "first_experiment": "Run baseline vs pure_trm vs metta_runtime vs metta_runtime_repair on a small local model and score valid tool choice, valid JSON, argument exactness, and first-useful-hit rate.",
        "success_metric": "At least +0.20 absolute exact tool-call validity over baseline with zero schema-invalid commits on held-out tools.",
        "stop_rule": "If MeTTa only fixes JSON syntax while selecting the wrong tool family, split router and argument-repair TRMs before expanding.",
        "paper_claim": "MeTTa/TRM improves control-plane tool-use reliability when tool schemas and arguments are verifier-visible.",
    },
    {
        "id": "mixed_contract_compactification",
        "title": "Mixed Contract Compactification Suite",
        "priority": 2,
        "thesis": "Unify instruction constraints, pydantic objects, ASCII trees, choice labels, and IFEval-style literal contracts into one small-model compactification benchmark.",
        "why_now": "The strongest positive evidence is scattered across format and schema envs; a mixed suite makes the methodology harder to dismiss as one-off repair.",
        "env_families": [
            "if_summarize_judge",
            "pydantic_adherence",
            "ascii_tree",
            "ifeval_contract_family",
            "boolq_choice_contract",
        ],
        "forks": ["metta-structured-contract-repair-lane"],
        "circuits": ["contract_compactification_circuit"],
        "first_artifact": "A 50-row held-out mixed-contract dataset with explicit failure labels, exact validators, and near-miss cases.",
        "first_experiment": "Evaluate no-MeTTa, prompt-only MeTTa, repair-only MeTTa, and runtime+repair MeTTa against the same validators.",
        "success_metric": "Runtime+repair wins on exact contract validity without reducing semantic correctness on choice or summary rows.",
        "stop_rule": "If gains come only from deterministic postprocessing, label the result as verifier-owned repair rather than TRM training lift.",
        "paper_claim": "Small LLMs can act as proposal engines when explicit symbolic gates own observable output contracts.",
    },
    {
        "id": "logic_signature_camp_gate",
        "title": "Leakage-Safe Logic Signature Gate",
        "priority": 3,
        "thesis": "Test whether MeTTa signature checks can amplify weak Intellect-3 logic proposals without using target-grid leakage.",
        "why_now": "The C-signature projection result is large, but the next claim needs puzzle-provided constraints only.",
        "env_families": ["intellect3_logic_camp_gate"],
        "forks": ["metta-intellect3-logic-signature-gate"],
        "circuits": ["intellect3_logic_signature_circuit"],
        "first_artifact": "A tiny Campsite-style micro-suite with puzzle constraints, row/column signatures derivable from the prompt, and proposal-tier labels.",
        "first_experiment": "Run local 3B proposals, classify partial-semantic vs full-candidate tiers, then apply MeTTa min-edit projection only from prompt-derived constraints.",
        "success_metric": "Improved cell accuracy and exactness over raw proposals, with an audit column proving no target answer signatures were imported.",
        "stop_rule": "If 3B proposals lack enough grid atoms for projection, switch this lane to 9B/27B or teacher-proposal mode.",
        "paper_claim": "Symbolic amplification can help hard logic only after the model emits enough verifier-visible state.",
    },
    {
        "id": "psycho_item_vector_stability",
        "title": "PsychoBench Item-Vector Stability",
        "priority": 4,
        "thesis": "Replace scalar PsychoBench reward chasing with item-vector, subscale, and profile-stability instrumentation.",
        "why_now": "The scalar lift is tiny, but the existing evidence shows MeTTa changes item geometry; that is a better research object.",
        "env_families": ["psycho_bench"],
        "forks": ["metta-psycho-item-vector-stability"],
        "circuits": ["psycho_item_vector_composition_circuit"],
        "first_artifact": "Repeated profile probes with item vectors, BFI subscale deltas, stability bands, and repair provenance.",
        "first_experiment": "Run repeated local 3B and later 9B/27B probes, then compare variance and subscale drift across with/without MeTTa.",
        "success_metric": "Lower profile variance or clearer target-profile adherence without merely clipping every response to a safe midpoint.",
        "stop_rule": "If MeTTa reduces variance by collapsing personality signal, treat as over-regularization and redesign gates.",
        "paper_claim": "MeTTa/TRM can expose and control psychometric response geometry even when scalar reward barely moves.",
    },
    {
        "id": "math_teacher_candidate_auditor",
        "title": "Math Teacher-Candidate Auditor",
        "priority": 5,
        "thesis": "Use MeTTa/TRM as a candidate auditor for hard math rather than pretending small models solve 100B-class problems.",
        "why_now": "Math is the clearest negative boundary; turning it into a teacher-candidate audit lane strengthens the paper.",
        "env_families": ["aime_boxed_answer", "intellect3_math_router"],
        "forks": ["metta-intellect3-math-teacher-auditor"],
        "circuits": ["intellect3_math_teacher_auditor_circuit"],
        "first_artifact": "A teacher-candidate bank with multiple proposed answers per item, numeric error archetypes, boxed-answer validators, and abstain labels.",
        "first_experiment": "Compare keyword routing, pure TRM candidate routing, and MeTTa invariant/boxed-answer auditing on candidate selection accuracy.",
        "success_metric": "Better candidate selection than keyword or always-first baselines while preserving a clear no-small-model-solve claim boundary.",
        "stop_rule": "If teacher candidates are mostly wrong or indistinguishable, collect better candidate diversity before training auditors.",
        "paper_claim": "For hard math, MeTTa/TRM is useful as an auditor and protocol gate, not as a substitute solver.",
    },
    {
        "id": "safety_abstain_router",
        "title": "Safety Abstain Router",
        "priority": 6,
        "thesis": "Evaluate routing and refusal-format reliability separately from high-stakes advice quality.",
        "why_now": "The route-only signal may transfer to small models, but the domain boundary must be explicit.",
        "env_families": ["safety_abstain_family"],
        "forks": [],
        "circuits": ["safety_abstain_veto_circuit"],
        "first_artifact": "A transparent route-only abstain-vs-answer dataset with borderline cases and separate advice-quality labels.",
        "first_experiment": "Score route accuracy, refusal format validity, false abstains, false answers, and advice-quality abstentions separately.",
        "success_metric": "Improved route/format reliability without claiming medical, security, or legal answer quality.",
        "stop_rule": "If the model gives unsafe substantive content after correct routing, add a separate safe-completion verifier before expanding.",
        "paper_claim": "MeTTa/TRM can enforce safety routing contracts, but high-stakes answer quality remains scale- and domain-sensitive.",
    },
    {
        "id": "mcp_lookup_efficiency",
        "title": "TRM-MCP Lookup Efficiency",
        "priority": 7,
        "thesis": "Turn MCP resource surfaces into short TRM rows for route, retrieve, verify, and first-useful-hit optimization.",
        "why_now": "This is the most general infrastructure project and pairs naturally with tool-schema work.",
        "env_families": ["mcp_lookup_surface"],
        "forks": ["metta-flow-trm-circuit-controller"],
        "circuits": ["tool_schema_composition_circuit"],
        "first_artifact": "A benchmark over filesystem, GitHub, Postgres, and PrimeHub-schema MCP examples with call-count and token-load metrics.",
        "first_experiment": "Compare plain resource scan, cached index lookup, TRM route/retrieve, and MeTTa verifier-gated retrieve.",
        "success_metric": "Fewer calls and fewer loaded tokens before first useful answer at equal or better answer correctness.",
        "stop_rule": "If the resource surface is tiny, skip TRM and use direct scan; the project only matters on large or heterogeneous MCPs.",
        "paper_claim": "TRM rows can compactify tool/resource lookup when the target is stable handles rather than raw memorized answers.",
    },
    {
        "id": "live_symbolic_closure_threshold",
        "title": "Live Symbolic Closure Threshold",
        "priority": 8,
        "thesis": "Replace deterministic proposal-tier simulations with observed local-model proposal tiers across env families.",
        "why_now": "The control-plane result is conceptually important, but it needs live proposal distributions to become empirical.",
        "env_families": ["symbolic_closure_threshold_suite"],
        "forks": ["metta-flow-trm-circuit-controller"],
        "circuits": ["contract_compactification_circuit", "intellect3_logic_signature_circuit"],
        "first_artifact": "A proposal-tier classifier applied to local 3B logs across tool routing, contracts, ASCII tree, camp-gate, and math.",
        "first_experiment": "Measure how often the model emits none, weak_surface, partial_semantic, or full_candidate state, then map which gates can close each case.",
        "success_metric": "A clear threshold curve showing where the LLM becomes mostly a proposal generator and where it still needs scale.",
        "stop_rule": "If tier labels are unstable across annotators or validators, formalize the label grammar before adding more envs.",
        "paper_claim": "The compactification threshold is measurable as the amount of verifier-visible state emitted before symbolic execution takes over.",
    },
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def by_key(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {str(row[key]): row for row in rows if key in row}


def attach_source_context(project: dict[str, Any], sources: dict[str, Any]) -> dict[str, Any]:
    scale_by_env = sources["scale_by_env"]
    fork_by_name = sources["fork_by_name"]
    circuit_by_name = sources["circuit_by_name"]

    scale_rows = [scale_by_env[env] for env in project["env_families"] if env in scale_by_env]
    forks = [fork_by_name[name] for name in project["forks"] if name in fork_by_name]
    circuits = [circuit_by_name[name] for name in project["circuits"] if name in circuit_by_name]

    gates: list[str] = []
    benchmark_arms: list[str] = []
    for row in scale_rows:
        gates.extend(row.get("recommended_gates", []))
    for item in forks + circuits:
        gates.extend(item.get("metta_gates", []))
        benchmark_arms.extend(item.get("benchmark_arms", []))

    enriched = dict(project)
    enriched["source_evidence"] = [
        {
            "env_family": row["env_family"],
            "scale_class": row.get("scale_class"),
            "evidence": row.get("evidence"),
            "next_eval": row.get("next_eval"),
            "claim_boundary": row.get("claim_boundary"),
        }
        for row in scale_rows
    ]
    enriched["metta_gates"] = sorted(set(gates))
    enriched["benchmark_arms"] = sorted(set(benchmark_arms))
    enriched["source_files"] = {
        "scale_transfer_map": str(SCALE_JSON.relative_to(ROOT)),
        "fork_plan": str(FORK_JSON.relative_to(ROOT)),
        "composition_plan": str(COMPOSITION_JSON.relative_to(ROOT)),
    }
    return enriched


def build_menu() -> dict[str, Any]:
    scale = load_json(SCALE_JSON)
    fork = load_json(FORK_JSON)
    composition = load_json(COMPOSITION_JSON)
    sources = {
        "scale_by_env": by_key(scale.get("rows", []), "env_family"),
        "fork_by_name": by_key(fork.get("forks", []), "fork"),
        "circuit_by_name": by_key(composition.get("compositions", []), "name"),
    }

    projects = [attach_source_context(project, sources) for project in PROJECTS]
    projects.sort(key=lambda item: int(item["priority"]))
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Actionable MeTTa project menu synthesized from local TRM/Hermes planning artifacts.",
        "source_inputs": {
            "scale_transfer_map": str(SCALE_JSON.relative_to(ROOT)),
            "fork_plan": str(FORK_JSON.relative_to(ROOT)),
            "composition_plan": str(COMPOSITION_JSON.relative_to(ROOT)),
        },
        "projects": projects,
    }


def md_link(path: str) -> str:
    return f"[{path}](<{ROOT / path}>)"


def render_md(menu: dict[str, Any]) -> str:
    lines: list[str] = [
        "# MeTTa Project Menu",
        "",
        f"Generated: `{menu['generated_at_utc']}`",
        "",
        "This is the working menu for MeTTa-based follow-on projects. It is a synthesis artifact, not a new benchmark run.",
        "",
        "## Source Inputs",
        "",
    ]
    for label, path in menu["source_inputs"].items():
        lines.append(f"- `{label}`: {md_link(path)}")

    lines.extend(
        [
            "",
            "## Priority Menu",
            "",
            "| Priority | Project | Best first artifact | Success metric | Claim boundary |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for project in menu["projects"]:
        lines.append(
            "| {priority} | `{id}` | {first_artifact} | {success_metric} | {paper_claim} |".format(
                **project
            )
        )

    lines.extend(
        [
            "",
            "## Recommended Start",
            "",
            "Start with `real_tool_contract_router` and `mixed_contract_compactification` as the first pair. They are the cleanest compactification lanes: the failure state is observable, validators can be exact, and local 3B runs can produce meaningful with/without-MeTTa deltas without making a broad reasoning claim.",
            "",
            "Keep `logic_signature_camp_gate` as the first hard-env follow-up. It is potentially higher-impact, but only if the micro-suite is leakage-safe and the proposal-tier labels prove the model emitted enough verifier-visible state.",
            "",
            "Use `math_teacher_candidate_auditor` as the negative/control lane. It should strengthen the paper by showing where the method stops replacing scale and starts requiring teacher candidates.",
            "",
            "## Project Details",
            "",
        ]
    )

    for project in menu["projects"]:
        lines.extend(
            [
                f"### {project['priority']}. `{project['id']}`",
                "",
                f"- Title: {project['title']}",
                f"- Thesis: {project['thesis']}",
                f"- Why now: {project['why_now']}",
                f"- Env families: {', '.join(f'`{env}`' for env in project['env_families'])}",
                f"- Source forks: {', '.join(f'`{name}`' for name in project['forks']) if project['forks'] else 'none'}",
                f"- Source circuits: {', '.join(f'`{name}`' for name in project['circuits']) if project['circuits'] else 'none'}",
                f"- First artifact: {project['first_artifact']}",
                f"- First experiment: {project['first_experiment']}",
                f"- Success metric: {project['success_metric']}",
                f"- Stop rule: {project['stop_rule']}",
                f"- Paper claim: {project['paper_claim']}",
                f"- Benchmark arms: {', '.join(f'`{arm}`' for arm in project['benchmark_arms']) if project['benchmark_arms'] else 'define in project harness'}",
                f"- MeTTa gates: {', '.join(f'`{gate}`' for gate in project['metta_gates']) if project['metta_gates'] else 'define in project harness'}",
                "",
            ]
        )
        if project["source_evidence"]:
            lines.append("Evidence anchors:")
            for evidence in project["source_evidence"]:
                lines.append(
                    "- `{env_family}`: {scale_class}; {evidence} Next: {next_eval}".format(
                        **evidence
                    )
                )
            lines.append("")

    lines.extend(
        [
            "## First Sprint Cut",
            "",
            "| Step | Output | Why |",
            "| ---: | --- | --- |",
            "| 1 | `research/studies/.../real_tool_contract_router/` trace suite | Converts the synthetic result into a real tool-use claim. |",
            "| 2 | `research/studies/.../mixed_contract_compactification/` validators | Gives the paper a unified compactification benchmark. |",
            "| 3 | `research/studies/.../logic_signature_camp_gate/` leakage audit | Tests the hard-env amplification claim without target leakage. |",
            "| 4 | Update paper appendix tables from the new runs | Keeps methodology claims aligned with evidence class. |",
            "",
            "## Claim Discipline",
            "",
            "- Positive compactification claims require exact validators, held-out rows, and separate semantic-vs-format scoring.",
            "- Hard-logic claims require an explicit leakage audit and prompt-derived constraints only.",
            "- Math claims should be framed as candidate auditing or protocol validation unless a larger solver supplies the candidate set.",
            "- PsychoBench claims should report item vectors, subscale drift, and stability instead of scalar reward alone.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    menu = build_menu()
    GENERATED.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(menu, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(menu), encoding="utf-8")
    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
