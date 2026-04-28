from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUPPORT_PATTERNS = ROOT / "references" / "trm_support_patterns.json"
ROUTER_SUMMARY = ROOT / "references" / "math_router_100.summary.json"


def _load_phrases() -> list[str]:
    if SUPPORT_PATTERNS.exists():
        payload = json.loads(SUPPORT_PATTERNS.read_text(encoding="utf-8"))
        return [str(item) for item in payload.get("selected_phrases", [])]
    router = json.loads(ROUTER_SUMMARY.read_text(encoding="utf-8"))
    return [str(item) for item in router.get("support_gate", {}).get("selected_phrases", [])]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check whether a math prompt matches the current TRM support-pattern shortlist."
    )
    parser.add_argument("--text", required=True, help="Math prompt text to inspect")
    args = parser.parse_args()

    text = args.text.strip().lower()
    phrases = _load_phrases()
    matched = [phrase for phrase in phrases if phrase and phrase.lower() in text]
    route = "math_skill_trm" if matched else "math_skill"

    print(f"matched_phrases={json.dumps(matched)}")
    print(f"route={route}")


if __name__ == "__main__":
    main()
