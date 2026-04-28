"""Build an appendix-ready MeTTa/TRM scale-transfer map.

The map is a curated synthesis of existing local artifacts.  It is not a new
model run.  It classifies candidate environments by the bottleneck that a
MeTTa-scaffolded, TRM-infused skill would address and marks whether the current
evidence suggests scale-independent transfer, scale-sensitive transfer, or a
negative/control boundary.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
OUT_DIR = ROOT / "research" / "generated"
OUT_MD = OUT_DIR / "metta_trm_scale_transfer_map.md"
OUT_JSON = OUT_DIR / "metta_trm_scale_transfer_map.json"


ROWS: list[dict[str, Any]] = [
    {
        "env_family": "if_summarize_judge",
        "candidate_skill": "Hermes/Instruction-Constraint-Repair-v1",
        "bottleneck": "exact structural constraint enforcement",
        "scale_class": "scale_independent_positive",
        "evidence": "0.8B HF 0.3333/0.3333/1.0000; SmolLM3-3B 0.0000/0.0000/1.0000; Qwen2.5-3B Q4 tok64 v2 0.0000/0.0000/1.0000 for no-MeTTa/runtime/runtime+repair.",
        "line": "Small models fail raw formatting but deterministic MeTTa repair can own the observable contract.",
        "recommended_gates": [
            "TRM_CONSTRAINT_CLASSIFY",
            "TRM_OUTPUT_METRIC_EXTRACT",
            "METTA_REPAIR_EXACT_COUNT",
            "TRM_COMMIT_FASTPATH",
        ],
        "next_eval": "Expand from three local seeds to a 20-50 row mixed constraint suite with held-out constraint families.",
        "claim_boundary": "Strong for exact output-form constraints; not evidence of deeper reasoning improvement.",
    },
    {
        "env_family": "synthetic_tool_router",
        "candidate_skill": "Hermes/Tool-Contract-Router-v1",
        "bottleneck": "tool schema selection and JSON argument contract",
        "scale_class": "scale_independent_positive",
        "evidence": "Local Qwen2.5-3B Q4: 0.0000/1.0000/1.0000 for no-MeTTa/runtime/runtime+repair.",
        "line": "The LLM can be a weak proposal engine when MeTTa owns schema memory and exact validation.",
        "recommended_gates": [
            "TRM_TOOL_INTENT_CLASSIFY",
            "METTA_SCHEMA_MEMORY",
            "TRM_ARGUMENT_NORMALIZE",
            "TRM_JSON_COMMIT_GATE",
        ],
        "next_eval": "Replace synthetic cases with real Hermes tool calls from repo, calendar, shell-safe search, and weather-like APIs.",
        "claim_boundary": "Current evidence is controlled/synthetic; needs real tool diversity before broad tool-calling claims.",
    },
    {
        "env_family": "symbolic_closure_threshold_suite",
        "candidate_skill": "Hermes/MeTTa-TRM-Circuit-Executor-v1",
        "bottleneck": "minimum proposal information required before symbolic gates can own execution",
        "scale_class": "control_plane_threshold_eval",
        "evidence": "Deterministic threshold suite: MeTTa/TRM circuit exact at `partial_semantic` tier for tool routing, choice contracts, ASCII tree, and camp-gate projection; math exactness remains `full_candidate` only.",
        "line": "The LLM becomes an idea spinner when it emits enough verifier-visible atoms; the circuit executes, repairs, and commits the final action.",
        "recommended_gates": [
            "TRM_ROUTE_GATE",
            "METTA_VALIDATE_GATE",
            "TRM_REPAIR_GATE",
            "TRM_COMMIT_GATE",
            "TRM_LEARNING_GATE",
        ],
        "next_eval": "Replace synthetic proposal tiers with live local 3B proposal logs and measure the observed tier distribution per env family.",
        "claim_boundary": "This is a deterministic control-plane threshold eval with zero model calls, not a live benchmark improvement.",
    },
    {
        "env_family": "intellect3_logic_camp_gate",
        "candidate_skill": "Hermes/Intellect-3-Logic-CampGate-v1",
        "bottleneck": "symbolic grid state verification and camp placement signatures",
        "scale_class": "scale_sensitive_but_symbolically_amplifiable",
        "evidence": "27B/109 logic_skill_trm original exact 0.3028; C-only projection exact 0.6789; avg cell accuracy 0.8787 -> 0.9340.",
        "line": "TRM must supply a plausible grid, but MeTTa can strongly amplify it when failures are row/column signature errors.",
        "recommended_gates": [
            "TRM_PARSE_GRID",
            "TRM_CAMP_ROW_COL_SIGNATURE",
            "METTA_MIN_EDIT_C_PROJECTION",
            "TRM_COMMIT_GRID",
        ],
        "next_eval": "Run local 3B on a tiny Campsite micro-suite to test whether weak proposals still contain enough T/C structure for projection.",
        "claim_boundary": "Post-hoc projection uses known signatures; fresh runs must avoid answer leakage and include puzzle-provided constraints only.",
    },
    {
        "env_family": "intellect3_math_router",
        "candidate_skill": "Hermes/Intellect-3-Math-Router-v1",
        "bottleneck": "raw arithmetic/problem-solving competence plus candidate routing",
        "scale_class": "scale_sensitive_negative_boundary",
        "evidence": "27B offline replay: current final 0.0700, hidden TRM candidate 0.1050, generic guard 0.1100. Local 3B first-5 smoke: vanilla 0.4000, always_trm 0.2000, generic guard 0.2000.",
        "line": "Routing can recover hidden good candidates at 27B scale, but the 3B TRM candidate quality is too weak on the tested slice.",
        "recommended_gates": [
            "TRM_PARSE_INTEGER_CANDIDATES",
            "TRM_NUMERIC_ERROR_ARCHETYPE",
            "TRM_ROUTE_TRM_CANDIDATE",
            "METTA_REGRET_AUDIT",
        ],
        "next_eval": "Use math as a negative-control lane and collect teacher candidates rather than relying on small-model TRM generations.",
        "claim_boundary": "Do not claim small-model math improvement; current evidence maps the limit line.",
    },
    {
        "env_family": "psycho_bench",
        "candidate_skill": "Hermes/PsychoBench-ItemVector-v1",
        "bottleneck": "latent profile stability and item-level response contract",
        "scale_class": "nuanced_scalar_not_enough",
        "evidence": "Richer-packet run reward 3.3283 -> 3.3311; both arms pass 44/44 item contract; MeTTa changes 4 items and shifts neuroticism +0.2500.",
        "line": "Tiny scalar gains need item/subscale decomposition; MeTTa may change profile geometry rather than obvious correctness.",
        "recommended_gates": [
            "TRM_LIKERT_ITEM_VECTOR_CONTRACT",
            "TRM_BFI_SUBSCALE_PROJECTOR",
            "METTA_PROFILE_DELTA_AUDIT",
            "TRM_STABILITY_GATE",
        ],
        "next_eval": "Run repeated local 3B and 9B profile probes, score variance, and compare subscale drift instead of only aggregate reward.",
        "claim_boundary": "Psychometric envs are interpretability/consistency probes, not conventional correctness benchmarks.",
    },
    {
        "env_family": "pydantic_adherence",
        "candidate_skill": "Hermes/Pydantic-Schema-Repair-v1",
        "bottleneck": "typed object emission and field-level validation",
        "scale_class": "likely_scale_independent_positive",
        "evidence": "Structured-map study reaches 1.0 reward; richer packet stayed 1.0 with and without MeTTa. Fresh local Qwen2.5-3B Q4 hard-schema probe: without_metta 0.0000, with_metta_runtime 1.0000, repair 1.0000.",
        "line": "Once the schema and canonical target shape are explicit, a 3B model can satisfy hard typed validation; the ceiling hides gains on easy cases.",
        "recommended_gates": [
            "TRM_SCHEMA_PARSE",
            "METTA_FIELD_TYPE_VALIDATE",
            "TRM_DEFAULT_POLICY_REPAIR",
            "TRM_JSON_COMMIT_GATE",
        ],
        "next_eval": "Create harder schema variants with missing optional fields, enum traps, nested arrays, and adversarial dates.",
        "claim_boundary": "Current row is ceilinged; needs harder cases to detect improvement.",
    },
    {
        "env_family": "ascii_tree",
        "candidate_skill": "Hermes/Ascii-Tree-Structure-v1",
        "bottleneck": "hierarchical formatting and node coverage",
        "scale_class": "likely_scale_independent_positive_with_ceiling",
        "evidence": "Structured-map study: ascii_tree 0.0 -> 0.8; richer packet with/without MeTTa both 0.8. Fresh local Qwen2.5-3B Q4 deep-tree probe: without_metta 0.6000, with_metta_runtime 0.0500, repair 1.0000.",
        "line": "MeTTa prompts can regress formatting if the model emits flattened trees, but a canonical tree repair gate gives exact structure.",
        "recommended_gates": [
            "TRM_NODE_LIST_PARSE",
            "METTA_PARENT_CHILD_VALIDATE",
            "TRM_ASCII_INDENT_REPAIR",
            "TRM_COVERAGE_COMMIT",
        ],
        "next_eval": "Add deeper trees, sibling ordering traps, missing-node penalties, and exact wrapper validation.",
        "claim_boundary": "Evidence supports structure-sensitive usefulness, not broad reasoning.",
    },
    {
        "env_family": "ifeval_contract_family",
        "candidate_skill": "Hermes/IFEval-Contract-Router-v1",
        "bottleneck": "instruction-family classification and output contract choice",
        "scale_class": "scale_independent_candidate",
        "evidence": "Local TRM-router benchmark reports gated contract success 1.0000 for allenai_ifeval, while pack columns were mostly zero/bridge-limited. Fresh local Qwen2.5-3B Q4 literal-count probe: without_metta 0.0000, runtime 0.0000, repair 1.0000.",
        "line": "This transfers when MeTTa owns literal repair; prompt-only runtime is insufficient because the model appends or miscounts tokens.",
        "recommended_gates": [
            "TRM_INSTRUCTION_FAMILY_CLASSIFY",
            "METTA_CONTRACT_SELECT",
            "TRM_LITERAL_CONSTRAINT_VERIFY",
            "TRM_REPAIR_OR_ABSTAIN",
        ],
        "next_eval": "Run a local 3B deterministic IFEval subset with per-constraint failure labels.",
        "claim_boundary": "Existing evidence is router-benchmark, not direct live environment reward.",
    },
    {
        "env_family": "aime_boxed_answer",
        "candidate_skill": "Hermes/AIME-Boxed-Answer-Gate-v1",
        "bottleneck": "answer extraction and boxed-format validation around hard math",
        "scale_class": "format_transfers_reasoning_does_not",
        "evidence": "Local TRM-router benchmark reports gated boxed exact rate 1.0000, but hard-math live columns were bridge-limited or zero.",
        "line": "MeTTa can enforce boxed answer protocol, but cannot create the missing mathematical solution at small scale.",
        "recommended_gates": [
            "TRM_BOXED_PARSE",
            "METTA_MOD_1000_VALIDATE",
            "TRM_NUMERIC_COMMIT",
            "TRM_TEACHER_CANDIDATE_ROUTE",
        ],
        "next_eval": "Separate answer-format extraction from actual AIME solve quality; use teacher candidates for the latter.",
        "claim_boundary": "Good for protocol/answer extraction; not evidence of hard-math competence transfer.",
    },
    {
        "env_family": "boolq_choice_contract",
        "candidate_skill": "Hermes/Choice-Contract-Repair-v1",
        "bottleneck": "binary/multiple-choice answer contract",
        "scale_class": "narrow_scale_independent_candidate",
        "evidence": "Trainer-policy mining rerun: boolq/qwen35_27b/two-model-contract-repair-v1 moved 0.0 -> 1.0; wider family only 1 contract win across 22 comparisons.",
        "line": "Choice-contract repair is real but narrow; it should be treated as a contract win, not comprehension gain.",
        "recommended_gates": [
            "TRM_CHOICE_SET_PARSE",
            "METTA_ALLOWED_LABEL_VALIDATE",
            "TRM_ABSTAIN_OR_COMMIT",
            "TRM_CONSISTENCY_CHECK",
        ],
        "next_eval": "Use as a small-model contract-control lane with semantic correctness separated from label validity.",
        "claim_boundary": "Narrow `choice_contract` claim only.",
    },
    {
        "env_family": "safety_abstain_family",
        "candidate_skill": "Hermes/Safety-Abstain-Router-v1",
        "bottleneck": "risk classification and abstain/answer routing",
        "scale_class": "candidate_unknown",
        "evidence": "Pack includes medsafetybench, jailbreak_bench, wmdp with abstain-guard variants. Fresh local Qwen2.5-3B Q4 obvious-route probe: without_metta 0.0000, with_metta_runtime 1.0000, repair 1.0000.",
        "line": "Obvious policy routing transfers to 3B when reduced to a JSON route contract, but factual medical/security advice remains scale- and domain-sensitive.",
        "recommended_gates": [
            "TRM_RISK_CLASSIFY",
            "METTA_POLICY_ROUTE",
            "TRM_REFUSAL_FORMAT_VALIDATE",
            "TRM_SAFE_COMPLETION_COMMIT",
        ],
        "next_eval": "Expand the local abstain-vs-answer suite with transparent labels, borderline cases, and separate advice-quality scoring.",
        "claim_boundary": "High-stakes domain; current evidence is routing/format safety only, not advice quality.",
    },
]


ORDER = {
    "scale_independent_positive": 0,
    "likely_scale_independent_positive": 1,
    "likely_scale_independent_positive_with_ceiling": 2,
    "control_plane_threshold_eval": 3,
    "scale_independent_candidate": 4,
    "narrow_scale_independent_candidate": 5,
    "scale_sensitive_but_symbolically_amplifiable": 6,
    "nuanced_scalar_not_enough": 7,
    "format_transfers_reasoning_does_not": 8,
    "scale_sensitive_negative_boundary": 9,
    "candidate_unknown": 10,
}


def markdown_link(path: Path, label: str) -> str:
    return f"[{label}](<{path}>)"


def render_md(payload: dict[str, Any]) -> str:
    rows = payload["rows"]
    lines = [
        "# MeTTa/TRM Scale-Transfer Map",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "This appendix map classifies where MeTTa-scaffolded, TRM-infused skills are likely to transfer across model scale and where they depend on base-model competence.",
        "",
        "## Core Boundary",
        "",
        "- Scale-independent pattern: observable contract, schema, routing, repair, or verifier state is the bottleneck.",
        "- Scale-sensitive pattern: the bottleneck is raw latent problem solving, missing arithmetic, or missing domain knowledge.",
        "- Nuanced pattern: scalar reward is too coarse, so the env needs item/vector/subcomponent decomposition before claiming improvement.",
        "",
        "## Ranked Env Families",
        "",
        "| Rank | Env family | Scale class | Bottleneck | Candidate skill | Current line | Next eval |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for idx, row in enumerate(rows, 1):
        lines.append(
            f"| {idx} | `{row['env_family']}` | `{row['scale_class']}` | {row['bottleneck']} | "
            f"`{row['candidate_skill']}` | {row['line']} | {row['next_eval']} |"
        )
    lines.extend(
        [
            "",
            "## Evidence And Gates",
            "",
        ]
    )
    for row in rows:
        lines.extend(
            [
                f"### `{row['env_family']}`",
                "",
                f"- Candidate skill: `{row['candidate_skill']}`",
                f"- Scale class: `{row['scale_class']}`",
                f"- Evidence: {row['evidence']}",
                f"- Claim boundary: {row['claim_boundary']}",
                f"- Recommended gates: {', '.join(f'`{gate}`' for gate in row['recommended_gates'])}",
                "",
            ]
        )
    lines.extend(
        [
            "## Paper Use",
            "",
            "Use this as an appendix table rather than a main-result table. The central paper claim should stay narrow: MeTTa/TRM scaffolding improves the training pipe and runtime behavior when the skill can decompose the task into explicit contracts, gates, and verifier-visible state transitions. The appendix then documents the boundary cases where that does not transfer.",
            "",
            "Suggested subsection title: `Appendix: Scale-Dependence Map for Symbolic TRM Scaffolding`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = sorted(ROWS, key=lambda row: (ORDER.get(row["scale_class"], 99), row["env_family"]))
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
        "source_summary": str((OUT_DIR / "trm_infused_baseline_summary_table.md").resolve()),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(OUT_MD)
    print(OUT_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
