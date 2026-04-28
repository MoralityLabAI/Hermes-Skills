from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "primehub_skill_batch_evolution" / "latest.manifest.json"


ENV_CLUSTERS = {
    "hard_reasoning_numeric": [
        "math_env",
        "math500",
        "gauss",
        "aime2024",
        "aime2025",
        "aime2026",
    ],
    "hard_reasoning_logic": [
        "logic_env",
        "science_env",
        "lisanbench",
        "mmlu_pro",
        "bixbench",
    ],
    "choice_contract": [
        "truthfulqa",
        "boolq",
        "simple_bench",
        "arc",
        "hellaswag",
        "winogrande",
        "mmlu_pro",
        "allenai_ifeval",
        "simpleqa",
        "simpleqa_verified",
        "simpleqa_verified_2",
    ],
    "structured_map": [
        "psycho_bench",
        "ascii_tree",
        "pydantic_adherence",
    ],
    "constraint_summarize": [
        "if_summarize_judge",
    ],
    "internal_action": [
        "antislop",
    ],
    "abstain_guard": [
        "truthfulqa",
        "wmdp",
        "agency_bench",
        "jailbreak_bench",
        "medsafetybench",
    ],
    "core_reasoning": [
        "logic_env",
        "math_env",
        "science_env",
        "math500",
        "aime2024",
        "aime2025",
        "aime2026",
        "mmlu_pro",
        "gauss",
        "lisanbench",
    ],
}


CLUSTER_PROFILES = {
    "hard_reasoning_numeric": {
        "task_family_label": "primehub_hard_reasoning_numeric",
        "top_k": 3,
        "holdout_ratio": 0.25,
        "min_supervision_weight": 0.4,
        "goal": "improve exact numeric recovery and verification on hard reasoning envs",
    },
    "hard_reasoning_logic": {
        "task_family_label": "primehub_hard_reasoning_logic",
        "top_k": 3,
        "holdout_ratio": 0.25,
        "min_supervision_weight": 0.4,
        "goal": "improve branch elimination and exact answer emission on logic-heavy envs",
    },
    "choice_contract": {
        "task_family_label": "primehub_choice_contract",
        "top_k": 5,
        "holdout_ratio": 0.2,
        "min_supervision_weight": 0.4,
        "goal": "repair exact small-answer wrappers without changing semantics",
    },
    "structured_map": {
        "task_family_label": "primehub_structured_map",
        "top_k": 3,
        "holdout_ratio": 0.2,
        "min_supervision_weight": 0.2,
        "goal": "preserve strict line schemas and structured answer maps",
        "support_tier_override": "format_support",
        "signal_weights": {
            "retrieval_selection_correctness": 1.35,
            "contract_validity": 1.5,
            "repair_success": 1.55,
            "failure_localization": 1.1,
            "contract_family_match": 1.25,
            "transport_visible_output": 0.8,
            "transport_no_fallback": 0.8
        }
    },
    "constraint_summarize": {
        "task_family_label": "primehub_constraint_summarize",
        "top_k": 3,
        "holdout_ratio": 0.2,
        "min_supervision_weight": 0.35,
        "goal": "enforce profile-conditioned structural summary contracts and deterministic repair on nuanced constraint tasks",
        "support_tier_override": "format_support",
        "signal_weights": {
            "profile_selection_correctness": 1.6,
            "contract_validity": 1.6,
            "repair_success": 1.7,
            "failure_localization": 1.2,
            "contract_family_match": 1.4,
            "task_success": 1.3,
            "critic_verdict_agreement": 1.1,
            "transport_visible_output": 0.85,
            "transport_no_fallback": 0.85
        }
    },
    "internal_action": {
        "task_family_label": "primehub_internal_action",
        "top_k": 1,
        "holdout_ratio": 0.25,
        "min_supervision_weight": 0.4,
        "goal": "recover exact hidden-action tokens such as inspect_and_continue",
    },
    "abstain_guard": {
        "task_family_label": "primehub_abstain_guard",
        "top_k": 5,
        "holdout_ratio": 0.2,
        "min_supervision_weight": 0.2,
        "goal": "separate true negatives from high-confidence guarded overrides",
    },
}


SKILLS = {
    "primehub-hard-reasoning-numeric-hermes": {
        "path": str((ROOT / "primehub-hard-reasoning-numeric-hermes" / "SKILL.md").resolve()),
        "prompt_builder": str((ROOT / "primehub-hard-reasoning-numeric-hermes" / "scripts" / "build_skill_prompt.py").resolve()),
        "env_cluster": "hard_reasoning_numeric",
        "stages": ["TRM_PARSE", "TRM_DECOMPOSE", "TRM_SOLVE", "TRM_VERIFY", "FINAL"],
    },
    "primehub-hard-reasoning-logic-hermes": {
        "path": str((ROOT / "primehub-hard-reasoning-logic-hermes" / "SKILL.md").resolve()),
        "prompt_builder": str((ROOT / "primehub-hard-reasoning-logic-hermes" / "scripts" / "build_skill_prompt.py").resolve()),
        "env_cluster": "hard_reasoning_logic",
        "stages": ["TRM_PARSE", "TRM_STATE_TABLE", "TRM_ELIMINATE", "TRM_VERIFY", "FINAL"],
    },
    "primehub-choice-contract-hermes": {
        "path": str((ROOT / "primehub-choice-contract-hermes" / "SKILL.md").resolve()),
        "prompt_builder": str((ROOT / "primehub-choice-contract-hermes" / "scripts" / "build_skill_prompt.py").resolve()),
        "env_cluster": "choice_contract",
        "stages": ["TRM_PARSE", "TRM_CRITIC", "TRM_FORMATTER", "TRM_VERIFY", "FINAL"],
    },
    "primehub-structured-map-hermes": {
        "path": str((ROOT / "primehub-structured-map-hermes" / "SKILL.md").resolve()),
        "prompt_builder": str((ROOT / "primehub-structured-map-hermes" / "scripts" / "build_skill_prompt.py").resolve()),
        "env_cluster": "structured_map",
        "stages": ["TRM_PARSE", "TRM_INDEX_PLAN", "TRM_FORMATTER", "TRM_VERIFY", "FINAL"],
    },
    "primehub-constraint-summarize-hermes": {
        "path": str((ROOT / "primehub-constraint-summarize-hermes" / "SKILL.md").resolve()),
        "prompt_builder": str((ROOT / "primehub-constraint-summarize-hermes" / "scripts" / "build_skill_prompt.py").resolve()),
        "env_cluster": "constraint_summarize",
        "stages": ["TRM_PARSE", "TRM_PROFILE_SELECT", "TRM_FORMATTER", "TRM_VERIFY", "FINAL"],
    },
    "primehub-internal-action-hermes": {
        "path": str((ROOT / "primehub-internal-action-hermes" / "SKILL.md").resolve()),
        "prompt_builder": str((ROOT / "primehub-internal-action-hermes" / "scripts" / "build_skill_prompt.py").resolve()),
        "env_cluster": "internal_action",
        "stages": ["TRM_PARSE", "TRM_CRITIC", "TRM_INTERNAL_ACT", "TRM_VERIFY", "FINAL"],
    },
    "primehub-abstain-guard-hermes": {
        "path": str((ROOT / "primehub-abstain-guard-hermes" / "SKILL.md").resolve()),
        "prompt_builder": str((ROOT / "primehub-abstain-guard-hermes" / "scripts" / "build_skill_prompt.py").resolve()),
        "env_cluster": "abstain_guard",
        "stages": ["TRM_PARSE", "TRM_CRITIC", "TRM_OVERRIDE_CHECK", "TRM_VERIFY", "FINAL"],
    },
}


EVOLUTION_VARIANTS = [
    {
        "variant_id": "single-model-baseline",
        "description": "One model handles all stages without env-targeted skills.",
        "models": {"monolith": "qwen35_9b_reasoning"},
        "routing": "none",
    },
    {
        "variant_id": "two-model-hard-reasoning-v1",
        "description": "Use 9B for parse/solve and 27B only for hard-reasoning verify on numeric and logic clusters.",
        "models": {
            "reasoner": "qwen35_9b_reasoning",
            "verify": "qwen35_27b_reasoning",
        },
        "routing": {
            "hard_reasoning_numeric": "primehub-hard-reasoning-numeric-hermes",
            "hard_reasoning_logic": "primehub-hard-reasoning-logic-hermes",
        },
    },
    {
        "variant_id": "two-model-contract-repair-v1",
        "description": "Use 9B critic, then 27B formatter/verify only on contract-heavy env clusters.",
        "models": {
            "critic": "qwen35_9b_reasoning",
            "formatter_verify": "qwen35_27b_reasoning",
        },
        "routing": {
            "choice_contract": "primehub-choice-contract-hermes",
            "structured_map": "primehub-structured-map-hermes",
            "internal_action": "primehub-internal-action-hermes",
        },
    },
    {
        "variant_id": "two-model-abstain-guard-v1",
        "description": "Use 9B critic with one 27B guarded override pass on honesty and safety envs.",
        "models": {
            "critic": "qwen35_9b_reasoning",
            "override_verify": "qwen35_27b_reasoning",
        },
        "routing": {
            "abstain_guard": "primehub-abstain-guard-hermes",
            "choice_contract": "primehub-choice-contract-hermes",
        },
    },
    {
        "variant_id": "three-model-basket-v1",
        "description": "Use 9B critic, 9B router, and 27B formatter/verify across the env-targeted skill basket.",
        "models": {
            "critic": "qwen35_9b_reasoning",
            "router": "qwen35_9b_reasoning",
            "formatter_verify": "qwen35_27b_reasoning",
        },
        "routing": {
            "hard_reasoning_numeric": "primehub-hard-reasoning-numeric-hermes",
            "hard_reasoning_logic": "primehub-hard-reasoning-logic-hermes",
            "choice_contract": "primehub-choice-contract-hermes",
            "structured_map": "primehub-structured-map-hermes",
            "internal_action": "primehub-internal-action-hermes",
            "abstain_guard": "primehub-abstain-guard-hermes",
        },
    },
    {
        "variant_id": "three-model-basket-v2-strong-guard",
        "description": "Use 9B critic, 27B router on abstention-heavy envs, and 27B formatter/verify for exact repair.",
        "models": {
            "critic": "qwen35_9b_reasoning",
            "router": "qwen35_27b_reasoning",
            "formatter_verify": "qwen35_27b_reasoning",
        },
        "routing": {
            "hard_reasoning_numeric": "primehub-hard-reasoning-numeric-hermes",
            "hard_reasoning_logic": "primehub-hard-reasoning-logic-hermes",
            "choice_contract": "primehub-choice-contract-hermes",
            "structured_map": "primehub-structured-map-hermes",
            "internal_action": "primehub-internal-action-hermes",
            "abstain_guard": "primehub-abstain-guard-hermes",
        },
    },
    {
        "variant_id": "three-model-basket-v3-reasoning-heavy",
        "description": "Use 9B critic, 9B hard-reasoner, and 27B verification/repair across the six specialist clusters.",
        "models": {
            "critic": "qwen35_9b_reasoning",
            "reasoner": "qwen35_9b_reasoning",
            "verify": "qwen35_27b_reasoning",
        },
        "routing": {
            "hard_reasoning_numeric": "primehub-hard-reasoning-numeric-hermes",
            "hard_reasoning_logic": "primehub-hard-reasoning-logic-hermes",
            "choice_contract": "primehub-choice-contract-hermes",
            "structured_map": "primehub-structured-map-hermes",
            "internal_action": "primehub-internal-action-hermes",
            "abstain_guard": "primehub-abstain-guard-hermes",
        },
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def build_manifest() -> dict[str, object]:
    return {
        "generated_at": utc_now(),
        "env_clusters": ENV_CLUSTERS,
        "cluster_profiles": CLUSTER_PROFILES,
        "skills": SKILLS,
        "recommended_batches": [
            {
                "batch_id": "hard-reasoning-numeric",
                "envs": ENV_CLUSTERS["hard_reasoning_numeric"],
                "goal": CLUSTER_PROFILES["hard_reasoning_numeric"]["goal"],
            },
            {
                "batch_id": "hard-reasoning-logic",
                "envs": ENV_CLUSTERS["hard_reasoning_logic"],
                "goal": CLUSTER_PROFILES["hard_reasoning_logic"]["goal"],
            },
            {
                "batch_id": "contract-heavy",
                "envs": ENV_CLUSTERS["choice_contract"],
                "goal": "measure exact contract repair gains",
            },
            {
                "batch_id": "structured-output",
                "envs": ENV_CLUSTERS["structured_map"],
                "goal": "measure strict schema compliance",
            },
            {
                "batch_id": "constraint-summarize",
                "envs": ENV_CLUSTERS["constraint_summarize"],
                "goal": "measure profile-conditioned constraint compliance and repair",
            },
            {
                "batch_id": "internal-action",
                "envs": ENV_CLUSTERS["internal_action"],
                "goal": "measure hidden-action recovery",
            },
            {
                "batch_id": "abstain-guard",
                "envs": ENV_CLUSTERS["abstain_guard"],
                "goal": "measure guarded negative overrides",
            },
            {
                "batch_id": "core-reasoning",
                "envs": ENV_CLUSTERS["core_reasoning"],
                "goal": "measure whether env-targeted skill routing hurts or helps hard reasoning",
            },
        ],
        "evolution_variants": EVOLUTION_VARIANTS,
        "recommended_parallel_training_clusters": [
            "hard_reasoning_numeric",
            "hard_reasoning_logic",
            "choice_contract",
            "structured_map",
            "constraint_summarize",
            "internal_action",
            "abstain_guard",
        ],
        "recommended_cron_order": [
            "two-model-hard-reasoning-v1",
            "two-model-contract-repair-v1",
            "two-model-abstain-guard-v1",
            "three-model-basket-v1",
            "three-model-basket-v2-strong-guard",
            "three-model-basket-v3-reasoning-heavy",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Primehub skill batch-evolution manifest.")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_manifest()
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(str(out_path))


if __name__ == "__main__":
    main()
