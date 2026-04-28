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
    "You are operating as Hermes skill Primehub-Hard-Reasoning-Numeric-v1.\n"
    "Use the stage order TRM_PARSE -> TRM_DECOMPOSE -> TRM_SOLVE -> TRM_VERIFY -> FINAL.\n"
    "Keep the derivation compact and explicit enough to catch arithmetic drift.\n"
    "Emit only the final exact answer string.\n"
)

ENV_RULES = {
    "math_env": "Compute the final value exactly and prefer the minimal legal numeric form.\n",
    "math500": "Solve exactly; do not leave the answer as an unresolved expression when a final value is available.\n",
    "gauss": "Preserve sign, parity, and integer constraints before final output.\n",
    "aime2024": "Verify the final numeric result with a second quick check before emitting it.\n",
    "aime2025": "Verify the final numeric result with a second quick check before emitting it.\n",
    "aime2026": "Verify the final numeric result with a second quick check before emitting it.\n",
}


def build_prompt(env_name: str, role_mode: str = "") -> str:
    env_rule = ENV_RULES.get(
        env_name,
        "Decompose the problem, solve the minimum necessary subgoals, then verify the result before emitting it.\n",
    )
    parts = [BASE_PROMPT, env_rule, "If the verification stage disagrees with the solve stage, repair before final output.\n"]
    role_lines = load_cluster_skill_prompt_lines("hard_reasoning_numeric")
    if role_lines:
        parts.append("Prime/TRM role imprint:\n")
        for line in role_lines:
            parts.append(f"- {line}\n")
    if role_mode == "critic_only":
        parts.append("- Runtime gate: keep this cluster in critic-only mode and do not escalate to retrieval-led action support.\n")
    elif role_mode == "action_support":
        parts.append("- Runtime gate: action-support escalation is allowed, but only after a locally solved candidate exists.\n")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the Primehub hard-reasoning numeric skill prompt.")
    parser.add_argument("--env-name", default="")
    parser.add_argument("--role-mode", default="", choices=["", "critic_only", "action_support"])
    args = parser.parse_args()
    print(build_prompt(args.env_name.strip(), args.role_mode.strip()), end="")


if __name__ == "__main__":
    main()
