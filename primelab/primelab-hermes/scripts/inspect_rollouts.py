from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("rollouts.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    rewards = []
    for row in data:
        rewards.append(float(row.get("reward", 0.0)))
        print("INPUT :", row.get("input"))
        print("TARGET:", row.get("target"))
        print("OUTPUT:", row.get("output"))
        print("REWARD:", row.get("reward"))
        print("-" * 60)
    if rewards:
        print(f"AVERAGE REWARD: {sum(rewards)/len(rewards):.3f}")


if __name__ == "__main__":
    main()
