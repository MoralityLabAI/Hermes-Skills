from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StepResult:
    prompt: str
    output: str
    reward: float


class ToyEnv:
    """Minimal single-turn environment.

    Replace this with a richer tool-using or multi-turn environment later.
    """

    def build_prompt(self, example: dict) -> str:
        return str(example["input"])
