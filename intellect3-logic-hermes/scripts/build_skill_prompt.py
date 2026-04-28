from __future__ import annotations

import argparse
import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMPRINT_CANDIDATES = [
    SKILL_ROOT / "references" / "primehub_skill_imprint.latest.json",
    REPO_ROOT / "data" / "primehub_trm_autoresearch" / "latest.skill_imprint.json",
]

BASE_PROMPT = (
    "You are operating as Hermes skill Intellect-3-Logic-v1.\n"
    "Solve Campsite-style logic grids with a parse -> candidate -> verify -> commit flow.\n"
    "Treat TRM hints as contractual internal helpers, not as visible output.\n"
    "Route to the TRM-augmented workspace only on an exact supported row/column signature.\n"
    "Do not guess from puzzle shape, size, or vague similarity.\n"
    "Otherwise stay on the plain skill path.\n"
    "Return only the completed Python-style 2D list using T, X, and C.\n"
)


def resolve_imprint_path(explicit_path: str) -> Path | None:
    if explicit_path:
        path = Path(explicit_path).resolve()
        return path if path.exists() else None
    for path in DEFAULT_IMPRINT_CANDIDATES:
        if path.exists():
            return path
    return None


def load_imprint_lines(path: Path | None) -> list[str]:
    if path is None:
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    lines = []
    for item in payload.get("skill_prompt_lines", []):
        text = str(item).strip()
        if text:
            lines.append(text)
    return lines


def build_prompt(imprint_lines: list[str]) -> str:
    parts = [BASE_PROMPT]
    if imprint_lines:
        parts.append("Prime/TRM imprint:\n")
        for line in imprint_lines:
            parts.append(f"- {line}\n")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the Intellect-3 Logic Hermes skill prompt.")
    parser.add_argument("--imprint-json", default="", help="Optional Prime/TRM skill imprint JSON path.")
    args = parser.parse_args()
    print(build_prompt(load_imprint_lines(resolve_imprint_path(args.imprint_json))), end="")


if __name__ == "__main__":
    main()
