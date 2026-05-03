from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class TRMContext:
    task: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    working_memory: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TRMResult:
    name: str
    action: str
    payload: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    notes: List[str] = field(default_factory=list)
    continue_pipeline: bool = True
