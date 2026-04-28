from __future__ import annotations

import argparse
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from primehub_role_imprint import load_cluster_skill_prompt_lines


BASE_PROMPT = (
    "You are operating as Hermes skill Primehub-Choice-Contract-v1.\n"
    "Use the stage order TRM_PARSE -> TRM_CRITIC -> TRM_FORMATTER -> TRM_VERIFY -> FINAL.\n"
    "Recover the semantic answer first, then repair only the output wrapper.\n"
    "Do not add explanations, rationale, or extra lines.\n"
)

ENV_RULES = {
    "truthfulqa": "Emit only a short truthful answer phrase or sentence. Do not use boxes unless the task explicitly asks for them.\n",
    "boolq": 'Emit only "True" or "False".\n',
    "simple_bench": "Emit exactly `Final Answer: X`.\n",
    "arc": "Emit only the final choice token requested by the task.\n",
    "hellaswag": "Emit only the final choice token requested by the task.\n",
    "winogrande": "Emit only the final choice token requested by the task.\n",
    "mmlu_pro": "Emit only the final answer letter inside \\boxed{...}.\n",
    "simpleqa": "Emit only a short factual answer phrase. No preamble, no explanation, no extra punctuation beyond the answer itself.\n",
    "simpleqa_verified": "Emit only a short factual answer phrase. No preamble, no explanation, no extra punctuation beyond the answer itself.\n",
    "simpleqa_verified_2": "Emit only a short factual answer phrase. No preamble, no explanation, no extra punctuation beyond the answer itself.\n",
    "allenai_ifeval": "Emit only the exact format required by the instruction.\n",
}


def build_prompt(env_name: str, role_mode: str = "") -> str:
    env_rule = ENV_RULES.get(env_name, "Emit only the exact final answer string required by the task.\n")
    parts = [
        BASE_PROMPT,
        env_rule,
        "If the answer is already semantically correct but wrapped incorrectly, repair the wrapper before final output.\n",
    ]
    role_lines = load_cluster_skill_prompt_lines("choice_contract")
    if role_lines:
        parts.append("Prime/TRM role imprint:\n")
        for line in role_lines:
            parts.append(f"- {line}\n")
    if role_mode == "action_support":
        parts.append("- Runtime gate: action-support escalation is allowed for this cluster after semantics are fixed.\n")
    elif role_mode == "critic_only":
        parts.append("- Runtime gate: stay critic-only here and do not let support override the solved semantics.\n")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the Primehub choice-contract skill prompt.")
    parser.add_argument("--env-name", default="")
    parser.add_argument("--role-mode", default="", choices=["", "critic_only", "action_support"])
    args = parser.parse_args()
    print(build_prompt(args.env_name.strip(), args.role_mode.strip()), end="")


if __name__ == "__main__":
    main()
