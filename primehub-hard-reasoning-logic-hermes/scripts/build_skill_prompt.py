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
    "You are operating as Hermes skill Primehub-Hard-Reasoning-Logic-v1.\n"
    "Use the stage order TRM_PARSE -> TRM_STATE_TABLE -> TRM_ELIMINATE -> TRM_VERIFY -> FINAL.\n"
    "Keep a compact latent state table and eliminate unsupported candidates before choosing an answer.\n"
    "Emit only the final exact answer token or string required by the task.\n"
)

ENV_RULES = {
    "logic_env": "Track entities and constraints explicitly, then emit only the surviving answer.\n",
    "science_env": "Use elimination, not verbosity; pick the answer that survives factual constraint checks.\n",
    "lisanbench": "Preserve the exact answer contract and avoid speculative intermediate text.\n",
    "mmlu_pro": "Emit only the final choice token requested by the task.\n",
    "bixbench": "Prefer branch elimination over open-ended explanation.\n",
}


def build_prompt(env_name: str, role_mode: str = "") -> str:
    env_rule = ENV_RULES.get(
        env_name,
        "Extract constraints, eliminate unsupported branches, then emit the minimal exact answer.\n",
    )
    parts = [BASE_PROMPT, env_rule, "If two candidates remain after elimination, verify against the literal question wording before final output.\n"]
    role_lines = load_cluster_skill_prompt_lines("hard_reasoning_logic")
    if role_lines:
        parts.append("Prime/TRM role imprint:\n")
        for line in role_lines:
            parts.append(f"- {line}\n")
    if role_mode == "critic_only":
        parts.append("- Runtime gate: keep this cluster in critic-only mode and use TRM only to prune or verify candidates.\n")
    elif role_mode == "action_support":
        parts.append("- Runtime gate: action-support escalation is allowed only after the candidate set is already narrow.\n")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the Primehub hard-reasoning logic skill prompt.")
    parser.add_argument("--env-name", default="")
    parser.add_argument("--role-mode", default="", choices=["", "critic_only", "action_support"])
    args = parser.parse_args()
    print(build_prompt(args.env_name.strip(), args.role_mode.strip()), end="")


if __name__ == "__main__":
    main()
