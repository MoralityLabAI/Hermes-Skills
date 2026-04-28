from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
OUT_DIR = ROOT / "research" / "generated"
OUT_MD = OUT_DIR / "metta_eval_meta_skill_fork_plan.md"
OUT_JSON = OUT_DIR / "metta_eval_meta_skill_fork_plan.json"

PURE_TRM_ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills\pure-trm-trainer")
PRIMELAB_ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills\primelab\primelab-hermes")


FORKS: list[dict[str, Any]] = [
    {
        "fork": "metta-flow-trm-circuit-controller",
        "source_skills": ["metta-eval-optimizer-hermes", "trm-observability-workflow"],
        "env_families": ["all gate-circuit forks"],
        "bottleneck": "skill-flow routing and typed failure logging",
        "metta_gates": ["route_gate", "validate_gate", "repair_gate", "commit_gate", "learning_gate"],
        "pure_trm_exports": ["route_error", "repair_success", "repair_failure", "commit_error"],
        "primelab_exports": ["baseline rollout receipts", "rubric brittleness notes"],
        "benchmark_arms": ["baseline", "pure_trm", "metta_runtime", "metta_runtime_repair"],
        "claim_boundary": "Meta-controller infrastructure; proves eval discipline only after live env arms are run.",
        "next_experiment": "Use this controller plan to fork structured-map and Intellect-3 logic first.",
    },
    {
        "fork": "metta-intellect3-logic-signature-gate",
        "source_skills": ["intellect3-logic-hermes", "primehub-hard-reasoning-logic-hermes"],
        "env_families": ["intellect3_logic", "logic_env"],
        "bottleneck": "grid candidate plausibility plus row/column/object signature repair",
        "metta_gates": ["proposal_gate", "signature_validate_gate", "min_edit_projection_gate", "commit_gate"],
        "pure_trm_exports": ["grid_candidate", "signature_mismatch", "projection_success", "critic_false_positive"],
        "primelab_exports": ["logic env baseline", "rollout grid traces", "rubric exactness and cell-accuracy metrics"],
        "benchmark_arms": ["baseline", "pure_trm", "metta_runtime_repair"],
        "claim_boundary": "Hard-env positive target; valid only when puzzle-provided constraints, not leaked answers, drive projection.",
        "next_experiment": "Run a small live local 3B grid-candidate probe and classify proposal tiers before projection.",
    },
    {
        "fork": "metta-intellect3-math-teacher-auditor",
        "source_skills": ["intellect3-math-hermes", "primehub-hard-reasoning-numeric-hermes"],
        "env_families": ["intellect3_math", "math500", "aime2024", "aime2025", "aime2026"],
        "bottleneck": "raw solve quality and candidate selection under 100B-class reasoning pressure",
        "metta_gates": ["candidate_parse_gate", "invariant_validate_gate", "numeric_error_gate", "teacher_candidate_commit_gate"],
        "pure_trm_exports": ["numeric_error_archetype", "candidate_selection", "verifier_false_positive", "abstain_correct"],
        "primelab_exports": ["teacher candidate eval", "hosted INTELLECT-3 or supported-model receipts", "QLoRA candidate-auditor lane"],
        "benchmark_arms": ["baseline", "pure_trm", "teacher_candidate_metta"],
        "claim_boundary": "Negative/control boundary for small-model solving; gains must come from candidate auditing, not invented math.",
        "next_experiment": "Generate or import teacher candidate sets, then test whether MeTTa/TRM selects better than keyword routing.",
    },
    {
        "fork": "metta-structured-contract-repair-lane",
        "source_skills": ["primehub-structured-map-hermes", "primehub-choice-contract-hermes", "primehub-constraint-summarize-hermes"],
        "env_families": ["pydantic_adherence", "ascii_tree", "ifeval_contract_family", "boolq_choice_contract"],
        "bottleneck": "observable contract validity and deterministic repair",
        "metta_gates": ["contract_select_gate", "field_validate_gate", "canonical_repair_gate", "commit_gate"],
        "pure_trm_exports": ["constraint_error", "repair_success", "repair_failure", "format_vs_semantics_split"],
        "primelab_exports": ["harder schema env variants", "rubric traps", "baseline eval receipts"],
        "benchmark_arms": ["baseline", "pure_trm", "metta_runtime", "metta_runtime_repair"],
        "claim_boundary": "Best compactification lane; does not imply latent reasoning gain.",
        "next_experiment": "Expand local 3B suite from six cases to a held-out 20-50 row mixed contract suite.",
    },
    {
        "fork": "metta-psycho-item-vector-stability",
        "source_skills": ["primehub-structured-map-hermes"],
        "env_families": ["psycho_bench"],
        "bottleneck": "aggregate reward hides item-level profile geometry",
        "metta_gates": ["item_vector_validate_gate", "subscale_project_gate", "profile_delta_audit_gate", "stability_commit_gate"],
        "pure_trm_exports": ["item_changed", "subscale_drift", "stability_pass", "profile_regression"],
        "primelab_exports": ["repeated profile evals", "rubric variance report", "rollout item vectors"],
        "benchmark_arms": ["baseline", "pure_trm", "metta_runtime"],
        "claim_boundary": "Interpretability and stability lane, not conventional exact-answer correctness.",
        "next_experiment": "Run repeated local/profile probes and report variance before claiming scalar improvement.",
    },
]


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# MeTTa Eval Meta-Skill Fork Plan",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "This plan composes MeTTa gate circuits with Pure-TRM-Trainer and PrimeLab. MeTTa owns the gate grammar, Pure-TRM-Trainer owns controller/corpus training, and PrimeLab owns env/rubric/eval or QLoRA workflows.",
        "",
        "## Source Infrastructure",
        "",
        f"- Pure-TRM-Trainer: [{PURE_TRM_ROOT.name}](<{PURE_TRM_ROOT}>)",
        f"- PrimeLab Hermes: [{PRIMELAB_ROOT.name}](<{PRIMELAB_ROOT}>)",
        "",
        "## Forks",
        "",
        "| Fork | Env families | Bottleneck | Pure-TRM export | PrimeLab export | Claim boundary |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for fork in payload["forks"]:
        lines.append(
            f"| `{fork['fork']}` | {', '.join(f'`{env}`' for env in fork['env_families'])} | "
            f"{fork['bottleneck']} | {', '.join(f'`{row}`' for row in fork['pure_trm_exports'])} | "
            f"{', '.join(f'`{row}`' for row in fork['primelab_exports'])} | {fork['claim_boundary']} |"
        )
    lines.extend(["", "## Gate Plans", ""])
    for fork in payload["forks"]:
        lines.extend(
            [
                f"### `{fork['fork']}`",
                "",
                f"- Source skills: {', '.join(f'`{skill}`' for skill in fork['source_skills'])}",
                f"- MeTTa gates: {', '.join(f'`{gate}`' for gate in fork['metta_gates'])}",
                f"- Benchmark arms: {', '.join(f'`{arm}`' for arm in fork['benchmark_arms'])}",
                f"- Next experiment: {fork['next_experiment']}",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "pure_trm_root": str(PURE_TRM_ROOT),
        "primelab_root": str(PRIMELAB_ROOT),
        "forks": FORKS,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(OUT_MD)
    print(OUT_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
