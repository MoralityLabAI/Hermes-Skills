from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTE_POLICY = ROOT / "references" / "trm_route_policy.json"
ROUTER_SUMMARY = ROOT / "references" / "logic_router_200.summary.json"


def _parse_vector(text: str) -> list[int]:
    text = text.strip()
    if not text:
        raise ValueError("expected a non-empty integer list")
    if text.startswith("["):
        value = ast.literal_eval(text)
        if not isinstance(value, list):
            raise ValueError("expected a Python-style list")
        items = value
    else:
        items = [part.strip() for part in text.split(",")]
    result: list[int] = []
    for item in items:
        if isinstance(item, int):
            result.append(item)
            continue
        if not item:
            raise ValueError("empty integer entry")
        result.append(int(item))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check whether a Campsite row/column signature should route to the TRM logic path."
    )
    parser.add_argument("--rows", required=True, help='Row constraints, e.g. "[2,0,2,0,1]" or "2,0,2,0,1"')
    parser.add_argument("--cols", required=True, help='Column constraints, e.g. "[1,1,0,2,1]" or "1,1,0,2,1"')
    args = parser.parse_args()

    rows = _parse_vector(args.rows)
    cols = _parse_vector(args.cols)

    if ROUTE_POLICY.exists():
        route_policy = json.loads(ROUTE_POLICY.read_text(encoding="utf-8"))
        selected = set(route_policy.get("selected_signatures", []))
    else:
        router = json.loads(ROUTER_SUMMARY.read_text(encoding="utf-8"))
        selected = set(router["signature_gate"]["selected_signatures"])
    signature = json.dumps(
        {"row_constraints": rows, "col_constraints": cols},
        separators=(",", ":"),
    )

    matched = signature in selected
    route = "logic_skill_trm" if matched else "logic_skill"

    print(f"signature={signature}")
    print(f"matched={str(matched).lower()}")
    print(f"route={route}")


if __name__ == "__main__":
    main()
