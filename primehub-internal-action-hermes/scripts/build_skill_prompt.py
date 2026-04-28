from __future__ import annotations

import argparse
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from primehub_role_imprint import load_cluster_skill_prompt_lines


def build_prompt(env_name: str, role_mode: str = "") -> str:
    _ = env_name
    parts = [
        "You are operating as Hermes skill Primehub-Internal-Action-v1.\n"
        "Use the stage order TRM_PARSE -> TRM_CRITIC -> TRM_INTERNAL_ACT -> TRM_VERIFY -> FINAL.\n"
        "When the valid move is hidden or deferred, emit only `inspect_and_continue`.\n"
        "Do not emit visible draft content when the contract requires internal continuation.\n"
    ]
    role_lines = load_cluster_skill_prompt_lines("internal_action")
    if role_lines:
        parts.append("Prime/TRM role imprint:\n")
        for line in role_lines:
            parts.append(f"- {line}\n")
    if role_mode == "action_support":
        parts.append("- Runtime gate: action-support escalation is allowed only for the narrow hidden-action token behavior.\n")
    elif role_mode == "critic_only":
        parts.append("- Runtime gate: stay critic-only and do not emit hidden-action tokens from weak support.\n")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the Primehub internal-action skill prompt.")
    parser.add_argument("--env-name", default="")
    parser.add_argument("--role-mode", default="", choices=["", "critic_only", "action_support"])
    args = parser.parse_args()
    print(build_prompt(args.env_name.strip(), args.role_mode.strip()), end="")


if __name__ == "__main__":
    main()
