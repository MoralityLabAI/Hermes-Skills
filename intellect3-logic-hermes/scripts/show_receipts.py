from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "references" / "logic_hybrid_200.summary.json",
    ROOT / "references" / "logic_router_200.summary.json",
]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    hybrid = _load(FILES[0])
    router = _load(FILES[1])
    print(f"rows={hybrid['rows']}")
    print(f"vanilla_exact={hybrid['arms']['vanilla']['exact_match_rate']}")
    print(f"logic_skill_trm_exact={hybrid['arms']['logic_skill_trm']['exact_match_rate']}")
    print(f"signature_gate_exact={router['signature_gate']['exact_match_rate']}")
    print(f"signature_gate_route_choice={router['signature_gate']['route_choice_accuracy']}")


if __name__ == "__main__":
    main()
