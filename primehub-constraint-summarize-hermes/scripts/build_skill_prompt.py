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
    "You are operating as Hermes skill Primehub-Constraint-Summarize-v1.\n"
    "Use the stage order TRM_PARSE -> TRM_CLASSIFY_CONSTRAINT -> TRM_STRUCTURE_PLAN -> TRM_VERIFY_COUNTS -> FINAL.\n"
    "Infer the active structural family from the user's instruction before writing any summary text.\n"
    "Emit only the final constrained summary text with no explanations or wrapper prose.\n"
)

ENV_RULES = {
    "if_summarize_judge": (
        "The instruction defines the required family.\n"
        "Common families include exact word counts, exact sentence counts, one-comma sentences, ALL-CAPS headlines, hashtags, XML word tags, and question-shaped summaries.\n"
        "Treat structural compliance as the primary objective and keep the answer as short as possible while satisfying the family.\n"
    ),
}

FAMILY_REMINDERS = (
    "Family reminders:\n"
    "- exact words: count words, not ideas\n"
    "- exact sentences: count sentence endings explicitly\n"
    "- bullets or hashtags: emit only the requested list shape\n"
    "- one comma / exclamation / headline casing: verify punctuation and case literally\n"
    "- XML tags: wrap every word, not just the sentence\n"
)


def build_prompt(env_name: str, role_mode: str = "") -> str:
    env_rule = ENV_RULES.get(env_name, "Infer the structural family and satisfy it exactly.\n")
    parts = [
        BASE_PROMPT,
        env_rule,
        FAMILY_REMINDERS,
        "If the draft satisfies the topic but violates the structure, repair the structure before final output.\n",
    ]
    role_lines = load_cluster_skill_prompt_lines("constraint_summarize")
    if role_lines:
        parts.append("Prime/TRM role imprint:\n")
        for line in role_lines:
            parts.append(f"- {line}\n")
    if role_mode == "critic_only":
        parts.append("- Runtime gate: stay critic-only and use support to classify and verify the structural family before emitting the final answer.\n")
    elif role_mode == "action_support":
        parts.append("- Runtime gate: action-support escalation is allowed only for structural repair after the family is already classified.\n")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the Primehub constraint-summarize skill prompt.")
    parser.add_argument("--env-name", default="")
    parser.add_argument("--role-mode", default="", choices=["", "critic_only", "action_support"])
    args = parser.parse_args()
    print(build_prompt(args.env_name.strip(), args.role_mode.strip()), end="")


if __name__ == "__main__":
    main()
