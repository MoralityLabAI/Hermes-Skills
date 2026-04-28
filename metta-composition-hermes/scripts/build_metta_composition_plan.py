from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
OUT_DIR = ROOT / "research" / "generated"
OUT_MD = OUT_DIR / "metta_composition_plan.md"
OUT_JSON = OUT_DIR / "metta_composition_plan.json"
SKILL_REGISTRY = OUT_DIR / "skill_registry.json"
ROLE_IMPRINT = ROOT / "data" / "primehub_skill_trm_matrix" / "latest" / "role_based_imprint.md"


COMPOSITIONS: list[dict[str, Any]] = [
    {
        "name": "contract_compactification_circuit",
        "source_skills": [
            "primehub-choice-contract-hermes",
            "primehub-structured-map-hermes",
            "primehub-constraint-summarize-hermes",
        ],
        "trm_roles": ["choice_contract", "structured_map"],
        "composition_class": "compactifiable",
        "metta_gates": ["route_gate", "contract_select_gate", "validate_gate", "repair_gate", "commit_gate", "learning_gate"],
        "pure_trm_exports": ["constraint_error", "repair_success", "format_vs_semantics_split", "commit_error"],
        "primelab_exports": ["hard schema env variants", "literal-count rubric traps", "baseline eval receipts"],
        "benchmark_arms": ["baseline", "pure_trm", "metta_runtime", "metta_runtime_repair"],
        "claim_boundary": "Good compactification target; supports control-plane capability, not latent reasoning gain.",
    },
    {
        "name": "tool_schema_composition_circuit",
        "source_skills": ["trm-mcp", "primehub-structured-map-hermes", "primehub-choice-contract-hermes"],
        "trm_roles": ["structured_map", "choice_contract"],
        "composition_class": "compactifiable",
        "metta_gates": ["tool_route_gate", "schema_memory_gate", "argument_validate_gate", "json_repair_gate", "commit_gate"],
        "pure_trm_exports": ["route_error", "retrieval_miss", "json_repair_success", "tool_commit_error"],
        "primelab_exports": ["tool-use env receipt", "argument rubric failure clusters"],
        "benchmark_arms": ["baseline", "pure_trm", "metta_runtime", "metta_runtime_repair"],
        "claim_boundary": "Tool calls can compactify when schemas and arguments are verifier-visible.",
    },
    {
        "name": "intellect3_logic_signature_circuit",
        "source_skills": ["intellect3-logic-hermes", "primehub-hard-reasoning-logic-hermes", "trm-public-rationale-chain"],
        "trm_roles": ["hard_reasoning_logic", "structured_map"],
        "composition_class": "symbolically_amplifiable",
        "metta_gates": ["proposal_gate", "constraint_parse_gate", "signature_validate_gate", "min_edit_projection_gate", "commit_gate"],
        "pure_trm_exports": ["grid_candidate", "signature_mismatch", "projection_success", "critic_false_positive"],
        "primelab_exports": ["logic rollout trace", "cell-accuracy metric", "signature rubric"],
        "benchmark_arms": ["baseline", "pure_trm", "metta_runtime_repair"],
        "claim_boundary": "Hard positive target; projection must use puzzle constraints rather than leaked target grids.",
    },
    {
        "name": "intellect3_math_teacher_auditor_circuit",
        "source_skills": ["intellect3-math-hermes", "primehub-hard-reasoning-numeric-hermes"],
        "trm_roles": ["hard_reasoning_numeric"],
        "composition_class": "scale_sensitive",
        "metta_gates": ["candidate_parse_gate", "invariant_validate_gate", "numeric_error_gate", "teacher_candidate_commit_gate"],
        "pure_trm_exports": ["numeric_error_archetype", "candidate_selection", "verifier_false_positive", "abstain_correct"],
        "primelab_exports": ["teacher candidate receipt", "math hosted eval receipt", "QLoRA candidate-auditor manifest"],
        "benchmark_arms": ["baseline", "pure_trm", "teacher_candidate_metta"],
        "claim_boundary": "Use as boundary case; MeTTa/TRM audits candidates but does not replace high-scale solving.",
    },
    {
        "name": "safety_abstain_veto_circuit",
        "source_skills": ["primehub-abstain-guard-hermes", "primehub-structured-map-hermes"],
        "trm_roles": ["abstain_guard", "structured_map"],
        "composition_class": "compactifiable_with_domain_boundary",
        "metta_gates": ["risk_route_gate", "policy_validate_gate", "abstain_or_answer_gate", "safe_format_gate", "commit_gate"],
        "pure_trm_exports": ["risk_route_error", "critic_false_positive", "critic_false_negative", "safe_format_repair"],
        "primelab_exports": ["borderline safety env receipt", "advice-quality rubric split"],
        "benchmark_arms": ["baseline", "pure_trm", "metta_runtime"],
        "claim_boundary": "Can test routing and refusal format; not evidence of high-stakes advice quality.",
    },
    {
        "name": "psycho_item_vector_composition_circuit",
        "source_skills": ["primehub-structured-map-hermes"],
        "trm_roles": ["structured_map"],
        "composition_class": "interpretability_only",
        "metta_gates": ["item_vector_validate_gate", "subscale_project_gate", "profile_delta_audit_gate", "stability_commit_gate"],
        "pure_trm_exports": ["item_changed", "subscale_drift", "stability_pass", "profile_regression"],
        "primelab_exports": ["repeated profile eval receipts", "variance report", "item-vector rollout table"],
        "benchmark_arms": ["baseline", "pure_trm", "metta_runtime"],
        "claim_boundary": "Profile stability and interpretability lane; scalar gain alone is not enough.",
    },
]


def load_registry() -> dict[str, Any]:
    if not SKILL_REGISTRY.exists():
        return {"entries": []}
    data = json.loads(SKILL_REGISTRY.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {"entries": data}
    return data


def registry_names(registry: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    entries = registry.get("entries") or registry.get("skills") or []
    for entry in entries:
        if isinstance(entry, dict):
            names.add(str(entry.get("slug") or entry.get("name") or ""))
    return names


def validate_compositions(skill_names: set[str]) -> list[dict[str, Any]]:
    validated: list[dict[str, Any]] = []
    for comp in COMPOSITIONS:
        missing = [skill for skill in comp["source_skills"] if skill not in skill_names]
        row = dict(comp)
        row["missing_source_skills"] = missing
        row["status"] = "ready" if not missing else "blocked_missing_skill"
        validated.append(row)
    return validated


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# MeTTa Composition Plan For TRM-Infused Hermes Skills",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "This plan composes Hermes skills into TRM-aware MeTTa circuits. It separates skill composition from eval execution and training.",
        "",
        "## Sources",
        "",
        f"- Skill registry: [{SKILL_REGISTRY.name}](<{SKILL_REGISTRY}>)",
        f"- TRM role imprint: [{ROLE_IMPRINT.name}](<{ROLE_IMPRINT}>)",
        "",
        "## Composition Summary",
        "",
        "| Circuit | Class | Status | Source skills | TRM roles | Claim boundary |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for comp in payload["compositions"]:
        lines.append(
            f"| `{comp['name']}` | `{comp['composition_class']}` | `{comp['status']}` | "
            f"{', '.join(f'`{skill}`' for skill in comp['source_skills'])} | "
            f"{', '.join(f'`{role}`' for role in comp['trm_roles'])} | {comp['claim_boundary']} |"
        )
    lines.extend(["", "## Gate Details", ""])
    for comp in payload["compositions"]:
        lines.extend(
            [
                f"### `{comp['name']}`",
                "",
                f"- MeTTa gates: {', '.join(f'`{gate}`' for gate in comp['metta_gates'])}",
                f"- Pure-TRM exports: {', '.join(f'`{row}`' for row in comp['pure_trm_exports'])}",
                f"- PrimeLab exports: {', '.join(f'`{artifact}`' for artifact in comp['primelab_exports'])}",
                f"- Benchmark arms: {', '.join(f'`{arm}`' for arm in comp['benchmark_arms'])}",
            ]
        )
        if comp["missing_source_skills"]:
            lines.append(f"- Missing source skills: {', '.join(f'`{skill}`' for skill in comp['missing_source_skills'])}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    registry = load_registry()
    compositions = validate_compositions(registry_names(registry))
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "skill_registry": str(SKILL_REGISTRY),
        "role_imprint": str(ROLE_IMPRINT),
        "compositions": compositions,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(OUT_MD)
    print(OUT_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
