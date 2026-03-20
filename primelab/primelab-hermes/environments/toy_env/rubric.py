from __future__ import annotations


def score(example: dict, output: str) -> float:
    target = str(example.get("target", "")).strip()
    got = str(output).strip()
    return 1.0 if got == target else 0.0
