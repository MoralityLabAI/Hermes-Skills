from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from .schemas import TRMContext, TRMResult


class BaseTRM(ABC):
    name: str = "base_trm"
    description: str = "Base TRM"

    @abstractmethod
    def run(self, context: TRMContext, **kwargs: Any) -> TRMResult:
        raise NotImplementedError

    def as_tool_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string"},
                        "metadata": {"type": "object"},
                    },
                    "required": ["task"],
                },
            },
        }
