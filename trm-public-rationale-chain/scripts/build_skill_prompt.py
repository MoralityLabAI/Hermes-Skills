from __future__ import annotations

import argparse


GENERIC_BASE = (
    "You are operating as Hermes skill TRM-Public-Rationale-Chain-v1.\n"
    "This experiment allows a bounded public rationale trace.\n"
    "Use the stage order TRM_PARSE -> TRM_CRITIC -> TRM_COMPRESS -> FINAL.\n"
    "This externalizes an observable rationale only; do not claim to reveal hidden chain-of-thought.\n"
)

FAMILY_RULES = {
    "generic": (
        "Keep the final line in the exact answer format requested by the task.\n"
    ),
    "logic": (
        "Underlying family is Campsite logic.\n"
        "Keep the base flow parse -> candidate -> verify -> commit.\n"
        "The final line must still be the completed Python-style 2D list using T, X, and C.\n"
    ),
    "math": (
        "Underlying family is arithmetic reasoning.\n"
        "Keep the base flow parse -> candidate -> verify -> commit.\n"
        "The final line must still be the final integer answer string.\n"
    ),
}

FORMAT_RULES = {
    "tagged": (
        "Emit exactly four lines in this format:\n"
        "TRM_PARSE: ...\n"
        "TRM_CRITIC: ...\n"
        "TRM_COMPRESS: ...\n"
        "FINAL: ...\n"
    ),
    "json": (
        "Emit exactly one JSON object with keys trm_parse, trm_critic, trm_compress, and final.\n"
    ),
}


def build_prompt(task_family: str, trace_format: str, max_step_chars: int) -> str:
    return (
        GENERIC_BASE
        + FAMILY_RULES[task_family]
        + f"Keep each public rationale line at or below {max_step_chars} characters.\n"
        + "Each rationale line must be concrete and task-linked, not generic filler.\n"
        + "If uncertainty remains, put it in TRM_CRITIC rather than inventing confidence.\n"
        + FORMAT_RULES[trace_format]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the TRM public rationale chain prompt.")
    parser.add_argument("--task-family", choices=["generic", "logic", "math"], default="generic")
    parser.add_argument("--trace-format", choices=["tagged", "json"], default="tagged")
    parser.add_argument("--max-step-chars", type=int, default=96)
    args = parser.parse_args()
    print(build_prompt(args.task_family, args.trace_format, args.max_step_chars), end="")


if __name__ == "__main__":
    main()
