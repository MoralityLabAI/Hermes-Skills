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
    "You are operating as Hermes skill Primehub-Structured-Map-v1.\n"
    "Use the stage order TRM_PARSE -> TRM_INDEX_PLAN -> TRM_FORMATTER -> TRM_VERIFY -> FINAL.\n"
    "Return only the required structure, with no explanations or wrapper prose.\n"
)

ENV_RULES = {
    "psycho_bench": (
        "Emit only plain text lines in the exact form `index: score`.\n"
        "Use integer scores only.\n"
    ),
    "ascii_tree": (
        "Emit only the requested ASCII structure.\n"
        "Do not add any surrounding prose.\n"
    ),
    "pydantic_adherence": (
        "Emit only the exact schema-conforming payload requested by the task.\n"
    ),
}


def build_prompt(env_name: str, role_mode: str = "") -> str:
    env_rule = ENV_RULES.get(env_name, "Emit only the exact required structure.\n")
    parts = [BASE_PROMPT, env_rule, "Reject malformed lines before final output.\n"]
    role_lines = load_cluster_skill_prompt_lines("structured_map")
    if role_lines:
        parts.append("Prime/TRM role imprint:\n")
        for line in role_lines:
            parts.append(f"- {line}\n")
    if role_mode == "action_support":
        parts.append("- Runtime gate: action-support escalation is allowed for schema-preserving repair on this cluster.\n")
    elif role_mode == "critic_only":
        parts.append("- Runtime gate: stay critic-only and do not force structural imitation from weak support.\n")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the Primehub structured-map skill prompt.")
    parser.add_argument("--env-name", default="")
    parser.add_argument("--role-mode", default="", choices=["", "critic_only", "action_support"])
    args = parser.parse_args()
    print(build_prompt(args.env_name.strip(), args.role_mode.strip()), end="")


if __name__ == "__main__":
    main()
