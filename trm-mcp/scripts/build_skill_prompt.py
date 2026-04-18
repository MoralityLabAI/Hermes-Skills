from __future__ import annotations

import argparse


BASE_PROMPT = (
    "You are operating as Hermes skill TRM-MCP.\n"
    "Optimize for lookup efficiency over the MCP surface, not for verbose reasoning.\n"
    "Use the stage order TRM_MCP_INDEX -> TRM_MCP_ROUTE -> TRM_MCP_RETRIEVE -> TRM_MCP_VERIFY -> FINAL.\n"
    "Prefer the fewest high-quality MCP actions that reach the correct resource or answer.\n"
)

MODE_RULES = {
    "index": (
        "Normalize resources into compact lookup units with family tags, answer-shape tags, "
        "and query cues. Do not carry full raw payloads unless strictly necessary.\n"
    ),
    "route": (
        "Predict the best MCP family or action type first. Avoid broad scans when a narrower "
        "resource family is available.\n"
    ),
    "retrieve": (
        "Retrieve the most likely URI, template, or parameterized action. Prefer first-hit quality "
        "over exhaustive exploration.\n"
    ),
    "verify": (
        "Reject seductive near-misses. Confirm scope, parameterization, and answer-shape compatibility "
        "before accepting a lookup result.\n"
    ),
    "train": (
        "Design compact TRM rows from MCP successes, misses, wrong-family attempts, and repaired lookups. "
        "Optimize for token and call efficiency.\n"
    ),
}


def build_prompt(mcp_name: str, mode: str) -> str:
    mode_rule = MODE_RULES.get(mode, MODE_RULES["retrieve"])
    mcp_line = f"Target MCP surface: {mcp_name}.\n" if mcp_name else ""
    return (
        BASE_PROMPT
        + mcp_line
        + mode_rule
        + "Prefer lookup-key prediction, routing, and verification over free-form answer synthesis.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the TRM-MCP skill prompt.")
    parser.add_argument("--mcp-name", default="")
    parser.add_argument(
        "--mode",
        default="retrieve",
        choices=["index", "route", "retrieve", "verify", "train"],
    )
    args = parser.parse_args()
    print(build_prompt(args.mcp_name.strip(), args.mode.strip()), end="")


if __name__ == "__main__":
    main()
