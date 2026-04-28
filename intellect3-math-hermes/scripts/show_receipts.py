from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "references" / "math_hybrid_200.summary.json",
    ROOT / "references" / "math_router_100.summary.json",
]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    hybrid = _load(FILES[0])
    router = _load(FILES[1])
    print(f"rows={hybrid['rows']}")
    print(f"vanilla_exact={hybrid['arms']['vanilla']['exact_match_rate']}")
    print(f"math_skill_trm_exact={hybrid['arms']['math_skill_trm']['exact_match_rate']}")
    print(f"support_gate_exact={router['support_gate']['exact_match_rate']}")
    print(f"support_gate_route_choice={router['support_gate']['route_choice_accuracy']}")


if __name__ == "__main__":
    main()
